import os
import sys
import urllib
import json
from collections import defaultdict, namedtuple
import requests
from elasticsearch import Elasticsearch, TransportError


_ES_URL = "{}://{}:{}".format("http", os.environ.get('ES_HOST', 'localhost'), 
    os.environ.get('ES_PORT', '9200'))
_ES_USER = os.environ.get('ES_USER', '')
_ES_PASSWORD = os.environ.get('ES_PASSWORD', '')

_ES_INSTANCE = None

_COMPLAINT_ES_INDEX = os.environ.get('COMPLAINT_ES_INDEX', 'complaint-index')
_COMPLAINT_DOC_TYPE = os.environ.get('COMPLAINT_DOC_TYPE', 'complaint-doctype')

# Filters for those with string type
_OPTIONAL_FILTERS = ("product", "issue", "company", "state", "zip_code", "timely", 
    "company_response", "company_public_response", 
    "consumer_consent_provided", "submitted_via", "tag", "consumer_disputed")

# Filters for those that need conversion from string to boolean
_OPTIONAL_FILTERS_STRING_TO_BOOL = ("has_narratives",)

_OPTIONAL_FILTERS_PARAM_TO_ES_MAP = {
    "product": "product.raw",
    "sub_product": "sub_product.raw",
    "issue": "issue.raw",
    "sub_issue": "sub_issue.raw",
    "company_public_response": "company_public_response.raw",
    "consumer_consent_provided": "consumer_consent_provided.raw",
    "consumer_disputed": "consumer_disputed.raw"
}

_OPTIONAL_FILTERS_CHILD_MAP = {
    "product": "sub_product", 
    "issue": "sub_issue"
}

def get_es():
    global _ES_INSTANCE
    if _ES_INSTANCE is None:
        _ES_INSTANCE = Elasticsearch([_ES_URL], http_auth=(_ES_USER, _ES_PASSWORD), 
            timeout=100)
    return _ES_INSTANCE



def _create_aggregation(**kwargs):

    # All fields that need to have an aggregation entry
    Field = namedtuple('Field', 'name size has_subfield')
    fields = [
        Field('has_narratives', 10, False),
        Field('company', 10000, False),
        Field('product', 10000, True),
        Field('issue', 10000, True),
        Field('state', 50, False),
        Field('zip_code', 1000, False),
        Field('timely', 10, False),
        Field('company_response', 100, False),
        Field('company_public_response', 100, False),
        Field('consumer_disputed', 100, False),
        Field('consumer_consent_provided', 100, False),
        Field('tag', 100, False),
        Field('submitted_via', 100, False)
    ]
    aggs = {}

    # Creating aggregation object for each field above
    for field in fields:
        field_aggs = {
            "filter": {
                "and": {
                    "filters": [

                    ]
                }
            }        
        }

        es_field_name = _OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(field.name, field.name)
        es_subfield_name = None
        if field.has_subfield:
            es_subfield_name = _OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(_OPTIONAL_FILTERS_CHILD_MAP.get(field.name))
            field_aggs["aggs"] = {
                field.name: {
                    "terms": {
                        "field": es_field_name,
                        "size": field.size
                    },
                    "aggs": {
                        es_subfield_name: {
                            "terms": {
                                "field": es_subfield_name,
                                "size": field.size
                            }
                        }
                    }
                }
            }
        else:
            field_aggs["aggs"] = {
                field.name: {
                    "terms": {
                        "field": es_field_name,
                        "size": field.size
                    }
                }
            }

        date_filter = {
            "range": {
                "date_received": {

                }
            }
        }
        if "min_date" in kwargs:
            date_filter["range"]["date_received"]["from"] = kwargs["min_date"]
        if "max_date" in kwargs:
            date_filter["range"]["date_received"]["to"] = kwargs["max_date"]
        
        field_aggs["filter"]["and"]["filters"].append(date_filter)
        
        # Add filter clauses to aggregation entries (only those that are not the same as field name)
        for item in kwargs:
            if item in _OPTIONAL_FILTERS and item != field.name:
                clauses = _create_and_append_bool_should_clauses(_OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(item, item), 
                    kwargs[item], field_aggs["filter"]["and"]["filters"], 
                    with_subitems=item in _OPTIONAL_FILTERS_CHILD_MAP, 
                    es_subitem_field_name=_OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(_OPTIONAL_FILTERS_CHILD_MAP.get(item)))
            elif item in _OPTIONAL_FILTERS_STRING_TO_BOOL and item != field.name:
                clauses = _create_and_append_bool_should_clauses(_OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(item, item), 
                    [ 0 if cd.lower() == "no" else 1 for cd in kwargs[item] ],
                    field_aggs["filter"]["and"]["filters"])

        aggs[field.name] = field_aggs

    return aggs

def _create_bool_should_clauses(es_field_name, value_list, 
    with_subitems=False, es_subitem_field_name=None):
    if value_list:
        if not with_subitems:
            term_list = [ {"terms": {es_field_name: [value]}} 
                for value in value_list ]
            return {"bool": {"should": term_list}}
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

            return {"bool": {"should": f_list}}

def _create_and_append_bool_should_clauses(es_field_name, value_list, 
    filter_list, with_subitems=False, es_subitem_field_name=None):
    
    filter_clauses = _create_bool_should_clauses(es_field_name, value_list, 
        with_subitems, es_subitem_field_name)

    if filter_clauses:
        filter_list.append(filter_clauses)

# List of possible arguments:
# - fmt: format to be returned: "json", "csv", "xls", or "xlsx"
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

    # base default parameters
    params = {
        "fmt": "json", 
        "field": "complaint_what_happened", 
        "size": 10, 
        "frm": 0,
        "sort": "relevance_desc"
    }

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
        body["query"] = {
            "match": {
                params.get("field"): {
                    "query": params.get("search_term"), 
                    "operator": "and"
                }
            }
        }
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


    ## Create bool should clauses for fields in _OPTIONAL_FILTERS
    for field in _OPTIONAL_FILTERS:
        if field in _OPTIONAL_FILTERS_CHILD_MAP: 
            _create_and_append_bool_should_clauses(_OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(field, field), 
                params.get(field), body["post_filter"]["and"]["filters"], with_subitems=True, 
                es_subitem_field_name=_OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(_OPTIONAL_FILTERS_CHILD_MAP.get(field), 
                    _OPTIONAL_FILTERS_CHILD_MAP.get(field)))
        else:
            _create_and_append_bool_should_clauses(_OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(field, field), 
                params.get(field), body["post_filter"]["and"]["filters"])

    for field in _OPTIONAL_FILTERS_STRING_TO_BOOL:
        if params.get(field):
            _create_and_append_bool_should_clauses(field, 
                [ 0 if cd.lower() == "no" else 1 for cd in params.get(field) ],
                body["post_filter"]["and"]["filters"])

    # format
    if params.get("fmt") == "json":
        ## Create base aggregation
        body["aggs"] = _create_aggregation(**kwargs)
        res = get_es().search(index=_COMPLAINT_ES_INDEX, body=body)
    elif params.get("fmt") in ["csv", "xls", "xlsx"]:
        p = {"format": params.get("fmt"),
                  "source": json.dumps(body)}
        p = urllib.urlencode(p)
        url = "{}/{}/{}/_data?{}".format(_ES_URL, _COMPLAINT_ES_INDEX, 
            _COMPLAINT_DOC_TYPE, p)
        response = requests.get(url, auth=(_ES_USER, _ES_PASSWORD), timeout=30)
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
