from django.test import TestCase
from complaint_search.es_interface import _ES_URL, _COMPLAINT_ES_INDEX, _COMPLAINT_DOC_TYPE, _ES_USER, _ES_PASSWORD, search, suggest, document
from elasticsearch import Elasticsearch
import requests
import os
import urllib
import json
import mock

class EsInterfaceTest(TestCase):
    def setUp(self):
        pass

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch('requests.get', ok=True, content="RGET_OK")
    def test_search_no_param__valid(self, mock_rget, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {"and": {"filters": []}}
        }
        res = search()
        mock_search.assert_called_once_with(body=body,
            index='INDEX')
        mock_rget.assert_not_called()
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._ES_URL", "ES_URL")
    @mock.patch("complaint_search.es_interface._ES_USER", "ES_USER")
    @mock.patch("complaint_search.es_interface._ES_PASSWORD", "ES_PASSWORD")
    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch("complaint_search.es_interface._COMPLAINT_DOC_TYPE", "DOC_TYPE")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch('requests.get', ok=True, content="RGET_OK")
    def test_search_with_fmt_nonjson__valid(self, mock_rget, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {"and": {"filters": []}}
        }
        for fmt in ["csv", "xls", "xlsx"]:
            res = search(fmt=fmt)
            param = urllib.urlencode({"format": fmt, "source": json.dumps(body)})
            other_args = {"auth": ("ES_USER", "ES_PASSWORD"), "verify": False, "timeout": 30}
            url = "ES_URL/INDEX/DOC_TYPE/_data?{}".format(param)
            mock_rget.assert_any_call(url, **other_args)
        
        mock_search.assert_not_called()
        self.assertEqual(3, mock_rget.call_count)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_field__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "test_field"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "test_field": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {"and": {"filters": []}}
        }
        res = search(field="test_field")
        mock_search.assert_called_once_with(body=body,
            index='INDEX')
        self.assertEqual('OK', res)

    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch('requests.get', ok=True, content="RGET_OK")
    def test_search_with_fmt__invalid(self, mock_rget, mock_search):
        mock_search.return_value = 'OK'
        res = search(fmt="pdf")
        self.assertIsNone(res)
        mock_search.assert_not_called()
        mock_rget.assert_not_called()

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_size__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 40, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {"and": {"filters": []}}
        }
        res = search(size=40)
        mock_search.assert_called_once_with(body=body,
            index="INDEX")
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_frm__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 20, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {"and": {"filters": []}}
        }
        res = search(frm=20)
        mock_search.assert_called_once_with(body=body,
            index="INDEX")
        self.assertEqual('OK', res)

 
    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_sort__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "post_filter": {"and": {"filters": []}}
        }

        sort_fields = [
            ("relevance_desc", "_score", "desc"), 
            ("relevance_asc", "_score", "asc"), 
            ("created_date_desc", "created_date", "desc"), 
            ("created_date_asc", "created_date", "asc")
        ]
        for s in sort_fields:
            res = search(sort=s[0])
            body["sort"] = [{s[1]: {"order": s[2]}}]
            mock_search.assert_any_call(body=body, index="INDEX")
            self.assertEqual('OK', res)

        self.assertEqual(4, mock_search.call_count)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_search_term__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "match": {
                    "what_happened": {
                        "query": "test_term", 
                        "operator": "and"
                    }
                }
            },
            "highlight": {
                "fields": {
                    "what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {"and": {"filters": []}}
        }
        res = search(search_term="test_term")
        mock_search.assert_called_once_with(body=body,
            index='INDEX')
        self.assertEqual('OK', res)

 