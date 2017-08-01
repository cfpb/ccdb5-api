import os
import urllib
import json
from collections import defaultdict, namedtuple
import requests
from elasticsearch import Elasticsearch
from complaint_search.es_builders import SearchBuilder, PostFilterBuilder, AggregationBuilder

_ES_URL = "{}://{}:{}".format("http", os.environ.get('ES_HOST', 'localhost'), 
    os.environ.get('ES_PORT', '9200'))
_ES_USER = os.environ.get('ES_USER', '')
_ES_PASSWORD = os.environ.get('ES_PASSWORD', '')

_ES_INSTANCE = None

_COMPLAINT_ES_INDEX = os.environ.get('COMPLAINT_ES_INDEX', 'complaint-index')
_COMPLAINT_DOC_TYPE = os.environ.get('COMPLAINT_DOC_TYPE', 'complaint-doctype')

def get_es():
    global _ES_INSTANCE
    if _ES_INSTANCE is None:
        _ES_INSTANCE = Elasticsearch([_ES_URL], http_auth=(_ES_USER, _ES_PASSWORD), 
            timeout=100)
    return _ES_INSTANCE

def get_meta():
    body = {
        # size: 0 here to prevent taking too long since we only needed max_date
        "size": 0,
        "aggs": { "max_date" : { "max" : { "field" : "date_received" }}}
    }
    max_date_res = get_es().search(index=_COMPLAINT_ES_INDEX, body=body)
    count_res = get_es().count(index=_COMPLAINT_ES_INDEX, doc_type=_COMPLAINT_DOC_TYPE)
    return {
        "license": "CC0",
        "last_updated": max_date_res["aggregations"]["max_date"]["value_as_string"],
        "total_record_count": count_res["count"]
    }
# List of possible arguments:
# - format: format to be returned: "json", "csv", "xls", or "xlsx"
# - field: field you want to search in: "complaint_what_happened", "company_public_response", "_all"
# - size: number of complaints to return
# - frm: from which index to start returning
# - sort: sort by: "relevance_desc", "relevance_asc", "created_date_desc", "created_date_asc"
# - search_term: the term to be searched
# - min_date: return only date including and later than this date i.e. 2017-03-02
# - max_date: return only date before this date, i.e. 2017-04-12 
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
# - has_narratives: filters a list of whether complaint has narratives or not
# - submitted_via: filters a list of ways the complaint was submitted
# - tag - filters a list of tags
def search(**kwargs):

    search_builder = SearchBuilder()
    search_builder.add(**kwargs)
    body = search_builder.build()

    post_filter_builder = PostFilterBuilder()
    post_filter_builder.add(**kwargs)
    body["post_filter"] = post_filter_builder.build()

    # format
    res = None
    format = kwargs.get("format", "json")
    if format == "json":
        if not kwargs.get("no_aggs", False):
            aggregation_builder = AggregationBuilder()
            aggregation_builder.add(**kwargs)
            body["aggs"] = aggregation_builder.build()

        res = get_es().search(index=_COMPLAINT_ES_INDEX, doc_type=_COMPLAINT_DOC_TYPE, body=body, scroll="10m")

        res["_meta"] = get_meta()

    elif format in ("csv", "xls", "xlsx"):
        p = {"format": format, "source": json.dumps(body)}
        p = urllib.urlencode(p)
        url = "{}/{}/{}/_data?{}".format(_ES_URL, _COMPLAINT_ES_INDEX, 
            _COMPLAINT_DOC_TYPE, p)
        response = requests.get(url, auth=(_ES_USER, _ES_PASSWORD), timeout=30)
        if response.ok:
            res = response.content
    return res

def suggest(text=None, size=6):
    if text is None:
        return []
    body = {"sgg": {"text": text, "completion": {"field": "suggest", "size": size}}}
    res = get_es().suggest(index=_COMPLAINT_ES_INDEX, body=body)
    candidates = [ e['text'] for e in res['sgg'][0]['options'] ]
    return candidates

def document(complaint_id):
    doc_query = {"query": {"term": {"_id": complaint_id}}}
    res = get_es().search(index=_COMPLAINT_ES_INDEX, 
        doc_type=_COMPLAINT_DOC_TYPE, body=doc_query)
    return res
