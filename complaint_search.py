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

def search(format="json"):
    res = None
    body = {"size": 10, "query": {"match_all": {}}}
    if format == "json":
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