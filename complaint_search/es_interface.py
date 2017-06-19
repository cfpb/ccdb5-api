import os
import urllib
import json
from collections import defaultdict
import requests
from elasticsearch import Elasticsearch

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

def _create_and_append_bool_should_clauses(es_field_name, value_list, 
    filter_list, with_subitems=False, es_subitem_field_name=None):
    if value_list:
        if not with_subitems:
            term_list = [ {"terms": {es_field_name: [value]}} 
                for value in value_list ]
            filter_list.append({"bool": {"should": term_list}})
        else:
            item_dict = defaultdict(list)
            for v in value_list:
                # -*- coding: utf-8 -*-
                v_pair = v.split(u'\u2022')
                # No subitem
                if len(v_pair) == 1:
                    # This will initialize empty list for item if not in item_dict yet
                    item_dict[v_pair[0]]
                elif len(v_pair) == 2:
                    # put subproduct into list
                    item_dict[v_pair[0]].append(v_pair[1])

            # Go through item_dict to create filters
            f_list = []
            for item, subitems in item_dict.iteritems():
                item_term = {"terms": {es_field_name: [item]}}
                # Item without any subitems
                if not subitems:
                    f_list.append(item_term)
                else:
                    subitem_term = {"terms": {es_subitem_field_name: subitems}}
                    f_list.append({"and": {"filters": [item_term, subitem_term]}})

            filter_list.append({"bool": {"should": f_list}})

# List of possible arguments:
# - fmt: format to be returned: "json", "csv", "xls", or "xlsx"
# - field: field you want to search in: "complaint_what_happened", "company_public_response", "_all"
# - size: number of complaints to return
# - frm: from which index to start returning
# - sort: sort by: "relevance_desc", "relevance_asc", "created_date_desc", "created_date_asc"
# - search_term: the term to be searched
# - min_date: return only date including and later than this date i.e. 2017-03-02
# - max_date: return only date before this date, i.e. 2017-04-12 
# - company: a list of companies you want ["Bank 1", "Bank 2"]
# - product: 
# - issue:
# - state:
# - zip_code:
# - timely:
# - consumer_disputed:
# - company_response:
# - company_public_response:
# - consumer_consent_provided
# - has_narratives
# - submitted_via
# - tag
def search(**kwargs):

    # base default parameters
    params = {
        "fmt": "json", 
        "field": "complaint_what_happened", 
        "size": 10, 
        "frm": 0,
        "sort": "relevance_desc"
    }

    OPTIONAL_FILTERS = ("product", "issue", "company", "state", "zip_code", "timely", 
        "company_response", "company_public_response", 
        "consumer_consent_provided", "submitted_via", "tag")

    OPTIONAL_FILTERS_CHILD_MAP = {
        "product": "subproduct", 
        "issue": "subissue"
    }

    OPTIONAL_FILTERS_STRING_TO_BOOL = ("consumer_disputed", "has_narratives")

    params.update(**kwargs)

    res = None
    body = {
        "from": params.get("frm"), 
        "size": params.get("size"), 
        "query": {"match_all": {}},
        "highlight": {
            "fields": {
                params.get("field"): {}
            },
            "number_of_fragments": 1,
            "fragment_size": 500
        }
    }

    # sort
    sort_field, sort_order = params.get("sort").rsplit("_", 1)
    sort_field = "_score" if sort_field == "relevance" else sort_field
    body["sort"] = [{sort_field: {"order": sort_order}}]

    # query
    if params.get("search_term"):
        body["query"] = {"match": {params.get("field"): {"query": params.get("search_term"), "operator": "and"}}}
    else:
        body["query"] = {
            "query_string": {
                "query": "*",
                "fields": [
                    params.get("field")
                ],
                "default_operator": "AND"
            }
        }

    # post-filter
    body["post_filter"] = {"and": {"filters": []}}

    ## date
    if params.get("min_date") or params.get("max_date"):
        date_clause = {"range": {"date_received": {}}}
        if params.get("min_date"):
            date_clause["range"]["date_received"]["from"] = params.get("min_date")
        if params.get("max_date"):
            date_clause["range"]["date_received"]["to"] = params.get("max_date")

        body["post_filter"]["and"]["filters"].append(date_clause)

    ## Create bool should clauses for fields in OPTIONAL_FILTERS
    for field in OPTIONAL_FILTERS:
        if field in OPTIONAL_FILTERS_CHILD_MAP: 
            _create_and_append_bool_should_clauses(field, params.get(field),
                body["post_filter"]["and"]["filters"], with_subitems=True, 
                es_subitem_field_name=OPTIONAL_FILTERS_CHILD_MAP.get(field))
        else:
            _create_and_append_bool_should_clauses(field, params.get(field),
                body["post_filter"]["and"]["filters"])

    for field in OPTIONAL_FILTERS_STRING_TO_BOOL:
        if params.get(field):
            _create_and_append_bool_should_clauses(field, 
                [ 0 if cd.lower() == "no" else 1 for cd in params.get(field) ],
                body["post_filter"]["and"]["filters"])

    # format
    if params.get("fmt") == "json":
        res = get_es().search(index=_COMPLAINT_ES_INDEX, body=body)
    elif params.get("fmt") in ["csv", "xls", "xlsx"]:
        p = {"format": params.get("fmt"),
                  "source": json.dumps(body)}
        p = urllib.urlencode(p)
        url = "{}/{}/{}/_data?{}".format(_ES_URL, _COMPLAINT_ES_INDEX, 
            _COMPLAINT_DOC_TYPE, p)
        response = requests.get(url, auth=(_ES_USER, _ES_PASSWORD), verify=False, 
            timeout=30)
        if response.ok:
            res = response.content
    return res

def suggest(text=None, size=6):
    if text is None:
        return {}
    body = {"sgg": {"text": text, "completion": {"field": "suggest", "size": size}}}
    res = get_es().suggest(index=_COMPLAINT_ES_INDEX, body=body)
    return res

def document(complaint_id):
    doc_query = {"query": {"term": {"_id": complaint_id}}}
    res = get_es().search(index=_COMPLAINT_ES_INDEX, 
        doc_type=_COMPLAINT_DOC_TYPE, body=doc_query)
    return res
