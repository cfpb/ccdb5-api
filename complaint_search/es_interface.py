import os
import urllib
import json
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

def _create_and_append_to_filter_list(es_field_name, value_list, filter_list):
    if value_list:
        term_list = [ {"terms": {es_field_name: [value]}} for value in value_list ]
        filter_list.append({"bool": {"should": term_list}})

# def search(fmt="json"):
def search(fmt="json", field="what_happened", size=10, frm=0, 
    sort="-relevance", search_term=None, min_date=None, max_date=None, 
    company=None, product=None, subproduct=None, issue=None, subissue=None, 
    state=None, consumer_disputed=None, company_response=None):

    res = None
    body = {"from": frm, "size": size, "query": {"match_all": {}}}

    # sort
    sort_order = "desc" if sort[0] == "-" else "asc"
    sort_field = "_score" if sort[1:] == "relevance" else sort[1:]
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

    if min_date:
        body["post_filter"]["and"]["filters"][1]["range"]["created_time"]["from"] = min_date

    if max_date:
        body["post_filter"]["and"]["filters"][1]["range"]["created_time"]["to"] = max_date

    _create_and_append_to_filter_list("company_name", company, body["post_filter"]["and"]["filters"])
    # if company:
    #     term_list = [ {"terms": {"company_name": [c]}} for c in company ]
    #     body["post_filter"]["and"]["filters"].append({"bool": {"should": term_list}})

    if consumer_disputed:
        _create_and_append_to_filter_list("dispute_resolution", 
            [ 0 if cd.lower() == "no" else 1 for cd in consumer_disputed ],
            body["post_filter"]["and"]["filters"])
    # if consumer_disputed:
    #     disputed_mapped_list = [ 0 if cd.lower() == "no" else 1 for cd in consumer_disputed ]
    #     disputed_list = [ {"terms": {"dispute_resolution": [d]}} for d in disputed_mapped_list ]
    #     body["post_filter"]["and"]["filters"].append({"bool": {"should": disputed_list}})

    if product:
        print "inside product"
        product_dict = {}
        for p in product:
            p_pair = p.split("/")
            print p_pair
            # No subproduct
            if len(p_pair) == 1:
                # initialize list for product if not in product_dict yet
                if product_dict.get(p_pair[0]) is None:
                    product_dict[p_pair[0]] = []

            elif len(p_pair) == 2:
                # initialize list for product if not in product_dict yet
                if product_dict.get(p_pair[0]) is None:
                    product_dict[p_pair[0]] = []
                # put subproduct into list
                product_dict[p_pair[0]].append(p_pair[1])

        print "product_dict", product_dict
        # Go through product_dict to create filters
        filter_list = []
        for product, subproducts in product_dict.iteritems():
            product_term = {"terms": {"product_level_1.raw": [product]}}
            # Product without any subproducts
            if not subproducts:
                filter_list.append(product_term)
            else:
                subproduct_term = {"terms": {"product.raw": subproducts}}
                filter_list.append({"and": {"filters": [product_term, subproduct_term]}})

        body["post_filter"]["and"]["filters"].append({"bool": {"should": filter_list}})

    if issue:
        issue_list = [ {"and": {"filters": [{"terms": {"category_level_1.raw": [i]}}]}} for i in issue ]
        body["post_filter"]["and"]["filters"].append({"bool": {"should": issue_list}})

    if state:
        state_list = [ {"terms": {"ccmail_state": [s]}} for s in state ]
        body["post_filter"]["and"]["filters"].append({"bool": {"should": state_list}})

    if company_response:
        cresponse_list = [ {"terms": {"comp_status_archive": [r]}} for r in company_response ]
        body["post_filter"]["and"]["filters"].append({"bool": {"should": cresponse_list}})

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