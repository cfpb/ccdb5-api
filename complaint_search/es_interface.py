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
                print v_pair
                # No subitem
                if len(v_pair) == 1:
                    # This will initialize empty list for item if not in item_dict yet
                    item_dict[v_pair[0]]
                elif len(v_pair) == 2:
                    # put subproduct into list
                    item_dict[v_pair[0]].append(v_pair[1])

            print "item_dict", item_dict
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

def search(fmt="json", field="what_happened", size=10, frm=0, 
    sort="relevance_desc", search_term=None, min_date=None, max_date=None, 
    company=None, product=None, subproduct=None, issue=None, subissue=None, 
    state=None, consumer_disputed=None, company_response=None):

    res = None
    body = {
        "from": frm, 
        "size": size, 
        "query": {"match_all": {}},
        "highlight": {
            "fields": {
                field: {}
            },
            "number_of_fragments": 1,
            "fragment_size": 500
        }
    }

    # sort
    sort_field, sort_order = sort.split("_")
    sort_field = "_score" if sort_field == "relevance" else sort_field
    body["sort"] = [{sort_field: {"order": sort_order}}]

    # query
    if search_term:
        body["query"] = {"match": {field: {"query": search_term, "operator": "and"}}}
    else:
        body["query"] = {
            "query_string": {
                "query": "*",
                "fields": [
                    field
                ],
                "default_operator": "AND"
            }
        }

    # post-filter
    body["post_filter"] = {"and": {"filters": []}}

    ## date
    if min_date or max_date:
        body["post_filter"]["and"]["filters"].append({"range": {"created_time": {}}})

        if min_date:
            body["post_filter"]["and"]["filters"][1]["range"]["created_time"]["from"] = min_date
        if max_date:
            body["post_filter"]["and"]["filters"][1]["range"]["created_time"]["to"] = max_date

    ## company
    _create_and_append_bool_should_clauses("company_name", company, 
        body["post_filter"]["and"]["filters"])

    ## consumer_disputed
    if consumer_disputed:
        _create_and_append_bool_should_clauses("dispute_resolution", 
            [ 0 if cd.lower() == "no" else 1 for cd in consumer_disputed ],
            body["post_filter"]["and"]["filters"])

    ## product
    _create_and_append_bool_should_clauses("product_level_1.raw", product,
        body["post_filter"]["and"]["filters"], with_subitems=True, 
        es_subitem_field_name="product.raw")

    ## issue
    _create_and_append_bool_should_clauses("category_level_1.raw", issue,
        body["post_filter"]["and"]["filters"], with_subitems=True, 
        es_subitem_field_name="category.raw")

    ## state
    _create_and_append_bool_should_clauses("ccmail_state", state, 
        body["post_filter"]["and"]["filters"])

    ## company_response
    _create_and_append_bool_should_clauses("comp_status_archive", company_response, 
        body["post_filter"]["and"]["filters"])


    print "body", body
    # format
    if fmt == "json":
        print body
        print _COMPLAINT_ES_INDEX
        res = get_es().search(index=_COMPLAINT_ES_INDEX, body=body)
    elif format in ["csv", "xls", "xlsx"]:
        params = {"format": format,
                  "source": json.dumps(body)}
        params = urllib.urlencode(params)
        url = "{}/{}/{}/_data?{}".format(_ES_URL, _COMPLAINT_ES_INDEX, 
            _COMPLAINT_DOC_TYPE, params)
        response = requests.get(url, auth=(_ES_USER, _ES_PASSWORD), verify=False, 
            timeout=30)
        if response.ok:
            res = response.content
    return res

def suggest(text=None, size=6):
    if text is None:
        return {}
    body = {"sgg": {"text": text, "completion": {"field":"suggest", "size": size}}}
    res = get_es().suggest(index=_COMPLAINT_ES_INDEX, body=body)
    return res

def document(complaint_id):
    doc_query = {"query": {"term": {"_id": complaint_id}}}
    res = get_es().search(index=_COMPLAINT_ES_INDEX, doc_type='complaint', body=doc_query)
    return res

if __name__ == '__main__':
    print search()
    print suggest()
    print suggest("mortgage", 8)
    print document(1707680)
    print type(search(format='csv'))
    print type(search(format='xls'))
    print type(search(format='xlsx'))