import os
import urllib
import json
import copy
import time
from datetime import datetime, date, timedelta
from collections import defaultdict, namedtuple
import requests
import logging
from elasticsearch import Elasticsearch
from flags.state import flag_enabled
from complaint_search.es_builders import (
    SearchBuilder,
    PostFilterBuilder,
    AggregationBuilder,
)
from complaint_search.defaults import (
    CHUNK_SIZE,
    CSV_ORDERED_HEADERS,
    EXPORT_FORMATS,
    PARAMS,
)
from stream_content import (
    StreamCSVContent,
    StreamJSONContent,
)

_ES_URL = "{}://{}:{}".format("http", os.environ.get('ES_HOST', 'localhost'),
                              os.environ.get('ES_PORT', '9200'))
_ES_USER = os.environ.get('ES_USER', '')
_ES_PASSWORD = os.environ.get('ES_PASSWORD', '')

_ES_INSTANCE = None

_COMPLAINT_ES_INDEX = os.environ.get('COMPLAINT_ES_INDEX', 'complaint-index')
_COMPLAINT_DOC_TYPE = os.environ.get('COMPLAINT_DOC_TYPE', 'complaint-doctype')


def _get_es():
    global _ES_INSTANCE
    if _ES_INSTANCE is None:
        _ES_INSTANCE = Elasticsearch([_ES_URL], http_auth=(_ES_USER, _ES_PASSWORD),
                                     timeout=100)
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
    if (last_updated_time < _min_valid_time()):
        return True

    return False


def from_timestamp(seconds):
    # Socrata fields (:field_name) are indexed in seconds, not the usual milliseconds
    fromtimestamp = datetime.fromtimestamp(seconds)
    return fromtimestamp.strftime('%Y-%m-%d')


def _get_meta():
    # Hard code noon Eastern Time zone since that is where it is built
    body = {
        # size: 0 here to prevent taking too long since we only needed max_date
        "size": 0,
        "aggs": {
            "max_date": {
                "max": {
                    "field": "date_received",
                    "format": "yyyy-MM-dd'T'12:00:00-05:00"
                }
            },
            "max_indexed_date": {
                "max": {
                    "field": "date_indexed",
                    "format": "yyyy-MM-dd'T'12:00:00-05:00"
                }
            },
            "max_narratives": {
                "filter": {"term": {"has_narrative": "true"}},
                "aggs": {
                    "max_date": {
                        "max": {
                            "field": ":updated_at",
                        }
                    }
                }
            }
        }
    }
    max_date_res = _get_es().search(index=_COMPLAINT_ES_INDEX, body=body)
    count_res = _get_es().count(index=_COMPLAINT_ES_INDEX, 
        doc_type=_COMPLAINT_DOC_TYPE)

    result = {
        "license": "CC0",
        "last_updated": max_date_res["aggregations"]["max_date"]["value_as_string"],
        "last_indexed": max_date_res["aggregations"]["max_indexed_date"]["value_as_string"],
        "total_record_count": count_res["count"],
        "is_data_stale": _is_data_stale(max_date_res["aggregations"]["max_date"]["value_as_string"]),
        "is_narrative_stale": _is_data_stale(from_timestamp(max_date_res["aggregations"]["max_narratives"]["max_date"]["value"])),
        "has_data_issue": flag_enabled('CCDB_TECHNICAL_ISSUES')
    }

    return result

# List of possible arguments:
# - format: format to be returned: "json", "csv"
# - field: field you want to search in: "complaint_what_happened", "company_public_response", "_all"
# - size: number of complaints to return
# - frm: from which index to start returning
# - sort: sort by: "relevance_desc", "relevance_asc", "created_date_desc", "created_date_asc"
# - search_term: the term to be searched
# - date_received_min: return only date received including and later than this date i.e. 2017-03-02
# - date_received_max: return only date received before this date, i.e. 2017-04-12
# - company_received_min: return only date company received including and later than this date i.e. 2017-03-02
# - company_received_max: return only date company received before this date, i.e. 2017-04-12
# - company: filters a list of companies you want ["Bank 1", "Bank 2"]
# - product: filters a list of product you want if a subproduct is needed to filter, separated by a bullet (u'\u2022), i.e. [u"Mortgage\u2022FHA Mortgage", "Payday Loan"]
# - issue: filters a list of issue you want if a subissue is needed to filter, separated by a bullet (u'\u2022), i.e. See Product above
# - state: filters a list of states you want
# - zip_code: filters a list of zipcodes you want
# - timely: filters a list of whether the company responds in a timely matter or not
# - consumer_disputed: filters a list of dispute resolution
# - company_response: filters a list of response from the company to consumer
# - company_public_response: filters a list of public response from the company
# - consumer_consent_provided: filters a list of whether consumer consent was provided in the complaint
# - has_narrative: filters a list of whether complaint has narratives or not
# - submitted_via: filters a list of ways the complaint was submitted
# - tags - filters a list of tags


def search(agg_exclude=None, **kwargs):
    params = copy.deepcopy(PARAMS)
    params.update(**kwargs)
    search_builder = SearchBuilder()
    search_builder.add(**params)
    body = search_builder.build()
    post_filter_builder = PostFilterBuilder()
    post_filter_builder.add(**params)
    body["post_filter"] = post_filter_builder.build()

    log = logging.getLogger(__name__)
    log.info(
        'Calling %s/%s/%s/_search with %s',
        _ES_URL, _COMPLAINT_ES_INDEX, _COMPLAINT_DOC_TYPE, body
    )

    # format
    res = {}
    format = params.get("format")
    if format == "default":
        if not params.get("no_aggs"):
            aggregation_builder = AggregationBuilder()
            aggregation_builder.add(**params)
            if agg_exclude:
                aggregation_builder.add_exclude(agg_exclude)
            body["aggs"] = aggregation_builder.build()

        res = _get_es().search(index=_COMPLAINT_ES_INDEX,
                               doc_type=_COMPLAINT_DOC_TYPE,
                               body=body,
                               scroll="10m")

        num_of_scroll = params.get("frm") / params.get("size")
        scroll_id = res['_scroll_id']
        if num_of_scroll > 0:
            while num_of_scroll > 0:
                res['hits']['hits'] = _get_es().scroll(scroll_id=scroll_id,
                                                       scroll="10m")['hits']['hits']
                num_of_scroll -= 1
        res["_meta"] = _get_meta()

    elif format in EXPORT_FORMATS:
        # Deleting from field and this will force data format plugin to use
        # scan/scroll query to create the content,
        # Size also doesn't seem to be relevant anymore
        del(body["from"])

        p = {
            "format": format,
            "source": json.dumps(body),
            "fl": ",".join(field for field in CSV_ORDERED_HEADERS.keys()),
            "append.header": "false"
        }
        p = urllib.urlencode(p)

        url = "{}/{}/{}/_data?{}".format(_ES_URL, _COMPLAINT_ES_INDEX,
                                         _COMPLAINT_DOC_TYPE, p)

        # requests.get does not seem to respect an IP address in NO_PROXY.
        # This is a workaround based on:
        # https://stackoverflow.com/questions/28521535/requests-how-to-disable-bypass-proxy/28521696#28521696  # noqa
        session = requests.Session()
        session.trust_env = False
        response = session.get(url, auth=(
            _ES_USER, _ES_PASSWORD), stream=True)
        if response.ok:
            res = response.iter_content(chunk_size=CHUNK_SIZE)
            if format == "json":
                res = StreamJSONContent(res)
            elif format == "csv":
                readable_header = ",".join('"' + rfield + '"'
                                           for rfield in CSV_ORDERED_HEADERS.values()) + "\n"
                res = StreamCSVContent(readable_header, res)
    return res


def suggest(text=None, size=6):
    if text is None:
        return []
    body = {"sgg": {"text": text, "completion": {
        "field": "suggest", "size": size}}}
    res = _get_es().suggest(index=_COMPLAINT_ES_INDEX, body=body)
    candidates = [e['text'] for e in res['sgg'][0]['options']]
    return candidates


def filter_suggest(filterField, display_field=None, **kwargs):
    params = dict(**kwargs)
    params.update({
        'size': 0,
        'no_highlight': True
    })

    search_builder = SearchBuilder()
    search_builder.add(**params)
    body = search_builder.build()

    aggregation_builder = AggregationBuilder()
    aggregation_builder.add(**params)
    aggs = {
        filterField: aggregation_builder.build_one(filterField)
    }
    # add the input value as a must match
    aggs[filterField]['filter']['bool']['must'].append(
        {
            'prefix': {filterField: params['text']}
        }
    )
    # choose which field to actually display
    aggs[filterField]['aggs'][filterField]['terms'][
        'field'] = filterField if display_field is None else display_field
    # add to the body
    body['aggs'] = aggs

    # format
    res = _get_es().search(
        index=_COMPLAINT_ES_INDEX,
        doc_type=_COMPLAINT_DOC_TYPE,
        body=body
    )
    # reformat the return
    candidates = [
        x['key']
        for x in res['aggregations'][filterField][filterField]['buckets'][:10]
    ]

    return candidates


def document(complaint_id):
    doc_query = {"query": {"term": {"_id": complaint_id}}}
    res = _get_es().search(index=_COMPLAINT_ES_INDEX,
                           doc_type=_COMPLAINT_DOC_TYPE, body=doc_query)
    return res
