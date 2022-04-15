import copy
import logging
import os
from datetime import datetime, timedelta
from math import ceil

from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers
from flags.state import flag_enabled
from requests_aws4auth import AWS4Auth

from complaint_search.defaults import (
    CSV_ORDERED_HEADERS,
    EXPORT_FORMATS,
    MAX_PAGINATION_DEPTH,
    PAGINATION_BATCH,
    PARAMS,
)
from complaint_search.es_builders import (
    AggregationBuilder,
    DateRangeBucketsBuilder,
    PostFilterBuilder,
    SearchBuilder,
    StateAggregationBuilder,
    TrendsAggregationBuilder,
)
from complaint_search.export import ElasticSearchExporter


log = logging.getLogger(__name__)

_ES_URL = "{}://{}:{}".format(
    "http",
    os.environ.get("ES_HOST", "localhost"),
    os.environ.get("ES_PORT", "9200"),
)
_ES_USER = os.environ.get("ES_USER", "")
_ES_PASSWORD = os.environ.get("ES_PASSWORD", "")
_ES_INSTANCE = None

USE_AWS_ES = os.environ.get("USE_AWS_ES", False)
AWS_ES_ACCESS_KEY = os.environ.get("AWS_ES_ACCESS_KEY")
AWS_ES_SECRET_KEY = os.environ.get("AWS_ES_SECRET_KEY")
AWS_ES_HOST = os.environ.get("ES_HOST")

_COMPLAINT_ES_INDEX = os.environ.get("COMPLAINT_ES_INDEX", "complaint-index")


# -----------------------------------------------------------------------------
# Trends Operations
# -----------------------------------------------------------------------------


def extract_date(agg_term, default_value):
    return agg_term.get("value_as_string", default_value)


def build_trend_meta(response):
    meta = {}

    if "max_date" in response["aggregations"]:
        date_max = extract_date(response["aggregations"]["max_date"], None)
        date_min = extract_date(response["aggregations"]["min_date"], None)
        meta["date_min"] = date_min
        meta["date_max"] = date_max

    return meta


# PAGINATION_BATCH = 100
# MAX_PAGINATION_DEPTH = 10000
def get_pagination_query_size(page, user_batch_size):
    batch_ahead = PAGINATION_BATCH * 2
    batch_point = page * user_batch_size
    if batch_point < PAGINATION_BATCH:
        return batch_ahead
    multiplier = ceil(batch_point / PAGINATION_BATCH)
    query_size = batch_ahead + (PAGINATION_BATCH * multiplier)
    if query_size <= MAX_PAGINATION_DEPTH:
        return query_size
    else:
        return MAX_PAGINATION_DEPTH


def get_break_points(hits, size):
    """Return a dict of upcoming 'search-after' values for pagination."""
    end_page = int(MAX_PAGINATION_DEPTH / size)
    break_points = {}
    if size >= len(hits):
        return break_points
    page = 2
    break_points[page] = hits[size - 1].get("sort")
    next_batch = hits[size:]
    while page < end_page and len(next_batch) > size:
        page += 1
        break_points[page] = next_batch[size - 1].get("sort")
        next_batch = next_batch[size:]
    return break_points


# Find sub_agg name if it exists in order to filter percent change
def get_sug_agg_key_if_exists(agg):
    agg_keys_exclude = ("trend_period", "key", "doc_count")
    for key in agg.keys():
        if key not in agg_keys_exclude:
            return key
    return None


# Filter out all but the most recent buckets in sub agg
#  for the Percent Change on chart
def process_trend_aggregations(aggregations):
    trend_charts = ("product", "sub-product", "issue", "sub-issue", "tags")

    for agg_name in trend_charts:
        if agg_name in aggregations:
            agg_buckets = aggregations[agg_name][agg_name]["buckets"]
            for sub_agg in agg_buckets:
                sub_agg["trend_period"]["buckets"] = sorted(
                    sub_agg["trend_period"]["buckets"],
                    key=lambda k: k["key_as_string"],
                    reverse=True,
                )
                sub_agg_name = get_sug_agg_key_if_exists(sub_agg)
                if sub_agg_name:
                    for sub_sub_agg in sub_agg[sub_agg_name]["buckets"]:
                        sub_sub_agg["trend_period"]["buckets"] = sorted(
                            sub_sub_agg["trend_period"]["buckets"],
                            key=lambda k: k["key_as_string"],
                            reverse=True,
                        )[1:2]
    return aggregations


# Process the response from a trends query
def process_trends_response(response):
    response["aggregations"] = process_trend_aggregations(
        response["aggregations"]
    )

    response["_meta"] = build_trend_meta(response)

    return response


def _get_es():
    global _ES_INSTANCE
    if _ES_INSTANCE is None:
        if USE_AWS_ES:  # pragma: no cover
            awsauth = AWS4Auth(
                AWS_ES_ACCESS_KEY, AWS_ES_SECRET_KEY, "us-east-1", "es"
            )
            _ES_INSTANCE = Elasticsearch(
                hosts=[{"host": AWS_ES_HOST, "port": 443}],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
                timeout=100,
            )
        else:
            _ES_INSTANCE = Elasticsearch(
                [_ES_URL], http_auth=(_ES_USER, _ES_PASSWORD), timeout=100
            )
    return _ES_INSTANCE


def _get_now():
    return datetime.now()


def _min_valid_time():
    # show notification starting fifth business day data has not been updated
    # M-Th, data needs to have been updated 6 days ago; F-S, preceding Monday
    now = _get_now()
    weekday = datetime.weekday(now)
    # When bigger than 3, it means it is a Friday/Saturday/Sunday,
    # we can use the weekday integer to get 4 days ago without the need to
    # worry about hitting the weekend.  Else we need to include the weekend
    delta = weekday if weekday > 3 else 6
    return (now - timedelta(delta)).strftime("%Y-%m-%d")


def _is_data_stale(last_updated_time):
    if last_updated_time < _min_valid_time():
        return True

    return False


def _get_meta():
    # Hard code noon Eastern Time zone since that is where it is built
    body = {
        # size: 0 here to prevent taking too long since we only needed max_date
        "size": 0,
        "aggs": {
            "max_date": {
                "max": {
                    "field": "date_received",
                    "format": "yyyy-MM-dd'T'12:00:00-05:00",
                }
            },
            "max_indexed_date": {
                "max": {
                    "field": "date_indexed",
                    "format": "yyyy-MM-dd'T'12:00:00-05:00",
                }
            },
        },
    }
    max_date_res = _get_es().search(index=_COMPLAINT_ES_INDEX, body=body)
    count_res = _get_es().count(index=_COMPLAINT_ES_INDEX)

    result = {
        "license": "CC0",
        "last_updated": max_date_res["aggregations"]["max_date"][
            "value_as_string"
        ],
        "last_indexed": max_date_res["aggregations"]["max_indexed_date"][
            "value_as_string"
        ],
        "total_record_count": count_res["count"],
        "is_data_stale": _is_data_stale(
            max_date_res["aggregations"]["max_date"]["value_as_string"]
        ),
        "has_data_issue": bool(flag_enabled("CCDB_TECHNICAL_ISSUES")),
    }

    return result


def test_float(value):
    try:
        _float = float(value)
    except Exception:
        return
    return _float


def parse_search_after(params):
    """Validate search_after and return it as a list of [score, ID]."""
    search_pair = params.get("search_after")
    sort = params.get("sort")
    if not search_pair or not sort:
        return
    if "_" not in search_pair or len(search_pair.split("_")) != 2:
        return
    _score, _id = search_pair.split("_")
    _sort = sort.split("_")[0]
    if _sort not in ["relevance", "created"]:
        log.error("{} is not a supported sort value.".format(_sort))
        return
    if _sort == "relevance":
        score = test_float(_score)
        if score is None:
            log.error("Search_after relevance score is not a float.")
            return
    elif _sort == "created":
        if not str(_score).isdigit():
            log.error("Search_after date score is not an integer.")
            return
        score = int(_score)
    return [score, _id]


def search(agg_exclude=None, **kwargs):
    """
    Prepare a search, get results from Elasticsearch, and return the hits.

    Starting from a copy of default PARAMS, these are the steps:
    - Update params with request details.
    - Add a formatted 'search_after' param if pagination is requested.
    - Build a search body based on params
    - Add param-based post_filter and aggregation sections to the search body.
    - Add a track_total_hits directive to get accurate hit counts (new in 2021)
    - Assemble pagination break points if needed.

    The response is finalized based on whether the results are to be viewed
    in a browser or exported as CSV or JSON.
    Exportable results are produced with "scroll" Elasticsearch searches,
    and are never paginated.
    """
    params = copy.deepcopy(PARAMS)
    params.update(**kwargs)
    search_after = parse_search_after(params)
    if search_after:
        params["search_after"] = search_after
    search_builder = SearchBuilder()
    search_builder.add(**params)
    body = search_builder.build()
    post_filter_builder = PostFilterBuilder()
    post_filter_builder.add(**params)
    body["post_filter"] = post_filter_builder.build()
    body["track_total_hits"] = True
    # format
    res = {}
    _format = params.get("format")
    if _format == "default":
        aggregation_builder = AggregationBuilder()
        aggregation_builder.add(**params)
        if agg_exclude:
            aggregation_builder.add_exclude(agg_exclude)
        body["aggs"] = aggregation_builder.build()
        log.info(
            "Requesting %s/%s/_search with %s",
            _ES_URL,
            _COMPLAINT_ES_INDEX,
            body,
        )
        res = _get_es().search(index=_COMPLAINT_ES_INDEX, body=body)
        hit_total = res["hits"]["total"]["value"]
        break_points = {}
        if res["hits"]["hits"]:
            user_batch_size = body["size"]
            if hit_total and hit_total > user_batch_size:
                # We have more than one page of results and need pagination
                pagination_body = copy.deepcopy(body)
                # cleaner to get page from frontend, but 'frm' works for now
                page = params.get("frm", user_batch_size) / user_batch_size
                pagination_body["size"] = get_pagination_query_size(
                    page, user_batch_size
                )
                if "search_after" in pagination_body:
                    del pagination_body["search_after"]
                log.info(
                    "Harvesting break points using %s/%s/_search with %s",
                    _ES_URL,
                    _COMPLAINT_ES_INDEX,
                    pagination_body,
                )
                pagination_res = _get_es().search(
                    index=_COMPLAINT_ES_INDEX, body=pagination_body
                )
                break_points = get_break_points(
                    pagination_res["hits"]["hits"], user_batch_size
                )
        res["_meta"] = _get_meta()
        res["_meta"]["break_points"] = break_points

    elif _format in EXPORT_FORMATS:
        scan_response = helpers.scan(
            client=_get_es(),
            query=body,
            scroll="10m",
            index=_COMPLAINT_ES_INDEX,
            size=7000,  # batch size for scroll request
            request_timeout=3000,
        )

        exporter = ElasticSearchExporter()

        if params.get("format") == "csv":
            res = exporter.export_csv(scan_response, CSV_ORDERED_HEADERS)
        elif params.get("format") == "json":
            if "highlight" in body:
                del body["highlight"]
            body.update({"size": 0, "track_total_hits": True})
            count_res = _get_es().search(index=_COMPLAINT_ES_INDEX, body=body)
            hit_total = count_res["hits"]["total"]["value"]
            res = exporter.export_json(scan_response, hit_total)

    return res


def suggest(text=None, size=6):
    if text is None:
        return []
    body = {
        "_source": False,
        "suggest": {
            "sgg": {
                "text": text,
                "completion": {
                    "field": "typeahead_dropdown",
                    "skip_duplicates": True,
                    "size": size,
                },
            }
        },
    }

    res = _get_es().search(index=_COMPLAINT_ES_INDEX, body=body)
    candidates = [e["text"] for e in res["suggest"]["sgg"][0]["options"]]
    return candidates


def filter_suggest(filter_field, display_field=None, **kwargs):
    params = dict(**kwargs)
    params.update({"size": 0, "no_highlight": True})

    search_builder = SearchBuilder()
    search_builder.add(**params)
    body = search_builder.build()

    aggregation_builder = AggregationBuilder()
    aggregation_builder.add(**params)
    aggs = {filter_field: aggregation_builder.build_one(filter_field)}
    # add the input value as a must match
    if filter_field != "zip_code":
        aggs[filter_field]["filter"]["bool"]["must"].append(
            {"wildcard": {filter_field: "*{}*".format(params["text"])}}
        )
    else:
        aggs[filter_field]["filter"]["bool"]["must"].append(
            {"prefix": {filter_field: params["text"]}}
        )

    # choose which field to actually display
    aggs[filter_field]["aggs"][filter_field]["terms"]["field"] = (
        filter_field if display_field is None else display_field
    )
    # add to the body
    body["aggs"] = aggs
    body["track_total_hits"] = True

    # format
    res = _get_es().search(index=_COMPLAINT_ES_INDEX, body=body)
    # reformat the return
    candidates = [
        x["key"]
        for x in res["aggregations"][filter_field][filter_field]["buckets"][
            :10
        ]
    ]

    return candidates


def document(complaint_id):
    doc_query = {"query": {"term": {"_id": complaint_id}}}
    res = _get_es().search(index=_COMPLAINT_ES_INDEX, body=doc_query)
    return res


def states_agg(agg_exclude=None, **kwargs):
    params = copy.deepcopy(PARAMS)
    params.update(**kwargs)
    params.update({"size": 0})
    search_builder = SearchBuilder()
    search_builder.add(**params)
    body = search_builder.build()
    aggregation_builder = StateAggregationBuilder()
    aggregation_builder.add(**params)
    if agg_exclude:
        aggregation_builder.add_exclude(agg_exclude)
    body["aggs"] = aggregation_builder.build()
    body["track_total_hits"] = True
    log.info(
        "Calling %s/%s/_search with %s",
        _ES_URL,
        _COMPLAINT_ES_INDEX,
        body,
    )
    log.info("API params were %s", params)
    res = _get_es().search(index=_COMPLAINT_ES_INDEX, body=body)
    return res


def trends(agg_exclude=None, **kwargs):
    params = copy.deepcopy(PARAMS)
    params.update(**kwargs)
    params.update(size=0)
    search_builder = SearchBuilder()
    search_builder.add(**params)
    body = search_builder.build()

    res_trends = None

    aggregation_builder = TrendsAggregationBuilder()
    aggregation_builder.add(**params)
    if agg_exclude:
        aggregation_builder.add_exclude(agg_exclude)
    body["aggs"] = aggregation_builder.build()
    body["track_total_hits"] = True

    res_trends = _get_es().search(index=_COMPLAINT_ES_INDEX, body=body)

    res_date_buckets = None

    date_bucket_body = copy.deepcopy(body)
    date_bucket_body["query"] = {"match_all": {}}

    date_range_buckets_builder = DateRangeBucketsBuilder()
    date_range_buckets_builder.add(**params)
    date_bucket_body["aggs"] = date_range_buckets_builder.build()

    res_date_buckets = _get_es().search(
        index=_COMPLAINT_ES_INDEX, body=date_bucket_body
    )

    res_trends = process_trends_response(res_trends)
    res_trends["aggregations"]["dateRangeBuckets"] = res_date_buckets[
        "aggregations"
    ]["dateRangeBuckets"]

    res_trends["aggregations"]["dateRangeBuckets"]["body"] = date_bucket_body

    return res_trends
