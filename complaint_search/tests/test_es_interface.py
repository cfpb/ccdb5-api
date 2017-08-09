from django.test import TestCase
from complaint_search.es_interface import _ES_URL, _COMPLAINT_ES_INDEX, _COMPLAINT_DOC_TYPE, _ES_USER, _ES_PASSWORD, get_meta, search, suggest, document
from elasticsearch import Elasticsearch
import requests
import os
import copy
import urllib
import json
import deep
import mock

class EsInterfaceTest(TestCase):
    # -------------------------------------------------------------------------
    # Helper Attributes
    # -------------------------------------------------------------------------
    MOCK_SEARCH_SIDE_EFFECT = [
        {
            "search" : "OK", 
            "_scroll_id": "This_is_a_scroll_id",
            "hits": {
                "hits": [0, 1, 2, 3]
            }
        }, 
        {
            "aggregations": {
                "max_date": {
                    "value_as_string": "2017-01-01"
                }
            }
        }
    ]

    MOCK_COUNT_RETURN_VALUE = { "count": 100 }

    MOCK_SEARCH_RESULT = {
        'search': 'OK', 
        "_scroll_id": "This_is_a_scroll_id",
        "hits": {
            "hits": [0, 1, 2, 3]
        },
        '_meta': {
            'total_record_count': 100, 
            'last_updated': '2017-01-01', 
            'license': 'CC0'
        }
    }

    MOCK_SCROLL_SIDE_EFFECT = [
        {
            "hits": {
                "hits": [4, 5, 6, 7]
            }
        }, 
        {
            "hits": {
                "hits": [8, 9, 10, 11]
            }
        }
    ]
    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def to_absolute(self, fileName):
        import os.path
        # where is this module?
        thisDir = os.path.dirname(__file__)
        return os.path.join(thisDir, "expected_results", fileName)

    def load(self, shortName):
        import json
        fileName = self.to_absolute(shortName + '.json')
        with open(fileName, 'r') as f:
            return json.load(f)


    def setUp(self):
        pass

    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    def test_get_meta(self, mock_count, mock_search):
        mock_search.return_value = self.MOCK_SEARCH_SIDE_EFFECT[1]
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE

        res = get_meta()
        self.assertDictEqual(self.MOCK_SEARCH_RESULT["_meta"], res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    @mock.patch('requests.get', ok=True, content="RGET_OK")
    def test_search_no_param__valid(self, mock_rget, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        mock_scroll.return_value = self.MOCK_SEARCH_SIDE_EFFECT[0]
        body = self.load("search_no_param__valid")
        res = search()
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        mock_rget.assert_not_called()
        self.assertDictEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._ES_URL", "ES_URL")
    @mock.patch("complaint_search.es_interface._ES_USER", "ES_USER")
    @mock.patch("complaint_search.es_interface._ES_PASSWORD", "ES_PASSWORD")
    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch("complaint_search.es_interface._COMPLAINT_DOC_TYPE", "DOC_TYPE")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch('requests.get', ok=True, content="RGET_OK")
    @mock.patch('json.dumps')
    @mock.patch('urllib.urlencode')
    def test_search_with_format_nonjson__valid(self, mock_urlencode, mock_jdump, mock_rget, mock_search):
        mock_search.return_value = 'OK'
        mock_jdump.return_value = 'JDUMPS_OK'
        body = self.load("search_with_format_nonjson__valid")
        for format in ["csv", "xls", "xlsx"]:
            res = search(format=format)
            self.assertEqual(len(mock_jdump.call_args), 2)
            self.assertEqual(1, len(mock_jdump.call_args[0]))
            act_body = mock_jdump.call_args[0][0]
            diff = deep.diff(act_body, body)
            if diff:
                print "format={}".format(format)
                diff.print_full()
            self.assertIsNone(deep.diff(act_body, body))
            self.assertEqual(len(mock_urlencode.call_args), 2)
            self.assertEqual(1, len(mock_urlencode.call_args[0]))
            param = {"format": format, "source": "JDUMPS_OK"}
            act_param = mock_urlencode.call_args[0][0]
            self.assertEqual(param, act_param)

        self.assertEqual(mock_jdump.call_count, 3)
        self.assertEqual(mock_urlencode.call_count, 3)
        
        mock_search.assert_not_called()
        self.assertEqual(3, mock_rget.call_count)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_field__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        mock_scroll.return_value = self.MOCK_SEARCH_SIDE_EFFECT[0]
        body = self.load("search_with_field__valid")
        res = search(field="test_field")
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertDictEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch('requests.get', ok=True, content="RGET_OK")
    def test_search_with_format__invalid(self, mock_rget, mock_search):
        mock_search.return_value = 'OK'
        res = search(format="pdf")
        self.assertIsNone(res)
        mock_search.assert_not_called()
        mock_rget.assert_not_called()

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_size__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_size__valid")
        res = search(size=40)
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertDictEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_frm__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        mock_scroll.side_effect = copy.deepcopy(self.MOCK_SCROLL_SIDE_EFFECT)
        body = self.load("search_with_frm__valid")
        res = search(frm=20)
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        self.assertEqual(mock_scroll.call_count, 2)
        search_result = copy.deepcopy(self.MOCK_SEARCH_RESULT)
        search_result['hits']['hits'] = self.MOCK_SCROLL_SIDE_EFFECT[1]['hits']['hits']
        self.assertDictEqual(search_result, res)

 
    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_sort__valid(self, mock_scroll, mock_count, mock_search):

        sort_fields = [
            ("relevance_desc", "_score", "desc"), 
            ("relevance_asc", "_score", "asc"), 
            ("created_date_desc", "created_date", "desc"), 
            ("created_date_asc", "created_date", "asc")
        ]

        # 4 is the length of sort_field
        # mock_search.side_effect = []
        # mock_count.side_effect = []
        # for i in range(4):

        # This create copies of MOCK_SEARCH_SIDE_EFFECT 4 times, and flatten the list out
        mock_search.side_effect = [ item for sublist in [ copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT) 
            for i in range(4) ] for item in sublist ]
        mock_count.side_effect = [ copy.deepcopy(self.MOCK_COUNT_RETURN_VALUE) 
            for i in range(4) ]
        body = self.load("search_with_sort__valid")

        for s in sort_fields:
            res = search(sort=s[0])
            body["sort"] = [{s[1]: {"order": s[2]}}]
            mock_search.assert_any_call(body=body, index="INDEX", doc_type=_COMPLAINT_DOC_TYPE, scroll="10m")
            self.assertEqual(self.MOCK_SEARCH_RESULT, res)

        mock_scroll.assert_not_called()
        self.assertEqual(8, mock_search.call_count)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_search_term_match__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_search_term_match__valid")
        res = search(search_term="test term")
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "search term match"
            diff.print_full()
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_search_term_qsq_and__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_search_term_qsq_and__valid")
        res = search(search_term="test AND term")
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "search term qsq and"
            diff.print_full()
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_search_term_qsq_or__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_search_term_qsq_or__valid")
        res = search(search_term="test OR term")
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "search term qsq or"
            diff.print_full()
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_search_term_qsq_not__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_search_term_qsq_not__valid")
        res = search(search_term="test NOT term")
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "search term qsq not"
            diff.print_full()
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_search_term_qsq_to__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_search_term_qsq_to__valid")
        res = search(search_term="term TO test")
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "search term qsq to"
            diff.print_full()
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_min_date__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_min_date__valid")
        res = search(min_date="2014-04-14")
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_max_date__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_max_date__valid")
        res = search(max_date="2017-04-14")
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_company__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_company__valid")
        res = search(company=["Bank 1", "Second Bank"])
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "company"
            diff.print_full()
        self.assertIsNone(deep.diff(act_body, body))
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)


    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_product__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_product__valid")
        res = search(product=["Payday Loan", u"Mortgage\u2022FHA Mortgage"])
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "product"
            diff.print_full()
        self.assertIsNone(deep.diff(act_body, body))
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_issue__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_issue__valid")
        res = search(issue=[u"Communication tactics\u2022Frequent or repeated calls",
        "Loan servicing, payments, escrow account"])
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "issue"
            diff.print_full()
        self.assertIsNone(deep.diff(act_body, body))
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)  

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_state__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_state__valid")
        res = search(state=["CA", "VA", "OR"])
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "state"
            diff.print_full()
        self.assertIsNone(deep.diff(act_body, body))
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_zip_code__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_zip_code__valid")
        res = search(zip_code=["12345", "23435", "03433"])
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "zip_code"
            diff.print_full()
        self.assertIsNone(deep.diff(act_body, body))
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertDictEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_timely__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_timely__valid")
        res = search(timely=["Yes", "No"])
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "timely"
            diff.print_full()
        self.assertIsNone(deep.diff(act_body, body))
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_company_response__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_company_response__valid")
        res = search(company_response=["Closed", "No response"])
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "company_response"
            diff.print_full()
        self.assertIsNone(deep.diff(act_body, body))
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)
        
    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_company_public_response__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_company_public_response__valid")
        res = search(company_public_response=["Response 1", "Response 2"])
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "company_public_response.raw"
            diff.print_full()
        self.assertIsNone(deep.diff(act_body, body))
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_consumer_consent_provided__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_consumer_consent_provided__valid")
        res = search(consumer_consent_provided=["yes", "no"])
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "consumer_consent_provided.raw"
            diff.print_full()
        self.assertIsNone(deep.diff(act_body, body))
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_submitted_via__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_submitted_via__valid")
        res = search(submitted_via=["mail", "web"])
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "submitted_via"
            diff.print_full()
        self.assertIsNone(deep.diff(act_body, body))
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_tag__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_tag__valid")
        res = search(tag=["Older American", "Servicemember"])
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "tag"
            diff.print_full()
        self.assertIsNone(deep.diff(act_body, body))
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_consumer_disputed__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_consumer_disputed__valid")
        res = search(consumer_disputed=["No", "Yes"])
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "consumer_disputed"
            diff.print_full()
        self.assertIsNone(deep.diff(act_body, body))
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch.object(Elasticsearch, 'count')
    @mock.patch.object(Elasticsearch, 'scroll')
    def test_search_with_has_narrative__valid(self, mock_scroll, mock_count, mock_search):
        mock_search.side_effect = copy.deepcopy(self.MOCK_SEARCH_SIDE_EFFECT)
        mock_count.return_value = self.MOCK_COUNT_RETURN_VALUE
        body = self.load("search_with_has_narrative__valid")
        res = search(has_narrative=["No", "Yes"])
        self.assertEqual(2, len(mock_search.call_args_list))
        self.assertEqual(2, len(mock_search.call_args_list[0]))
        self.assertEqual(0, len(mock_search.call_args_list[0][0]))
        self.assertEqual(4, len(mock_search.call_args_list[0][1]))
        act_body = mock_search.call_args_list[0][1]['body']
        diff = deep.diff(act_body, body)
        if diff:
            print "has_narrative"
            diff.print_full()
        self.assertIsNone(deep.diff(act_body, body))
        self.assertDictEqual(mock_search.call_args_list[0][1]['body'], body)
        self.assertEqual(mock_search.call_args_list[0][1]['index'], 'INDEX')
        mock_scroll.assert_not_called()
        self.assertEqual(self.MOCK_SEARCH_RESULT, res)


    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'suggest')
    def test_suggest_with_no_param__valid(self, mock_suggest):
        mock_suggest.return_value = {
            "sgg": [
                {
                    'options': [
                        {
                            "text": "test 1",
                            "score": 1.0
                        },
                        {
                            "text": "test 2",
                            "score": 1.0
                        }
                    ]
                }
            ]
        }
        body = {}
        res = suggest()
        mock_suggest.assert_not_called()
        self.assertEqual([], res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'suggest')
    def test_suggest_with_text__valid(self, mock_suggest):
        mock_suggest.return_value = {
            "sgg": [
                {
                    'options': [
                        {
                            "text": "test 1",
                            "score": 1.0
                        },
                        {
                            "text": "test 2",
                            "score": 1.0
                        }
                    ]
                }
            ]
        }
        body = {"sgg": {"text": "Mortgage", "completion": {"field": "suggest", "size": 6}}}
        res = suggest(text="Mortgage")
        self.assertEqual(len(mock_suggest.call_args), 2)
        self.assertEqual(0, len(mock_suggest.call_args[0]))
        self.assertEqual(2, len(mock_suggest.call_args[1]))
        act_body = mock_suggest.call_args[1]['body']
        self.assertDictEqual(mock_suggest.call_args[1]['body'], body)
        self.assertEqual(mock_suggest.call_args[1]['index'], 'INDEX')
        self.assertEqual(['test 1', 'test 2'], res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'suggest')
    def test_suggest_with_size__valid(self, mock_suggest):
        mock_suggest.return_value = {
            "sgg": [
                {
                    'options': [
                        {
                            "text": "test 1",
                            "score": 1.0
                        },
                        {
                            "text": "test 2",
                            "score": 1.0
                        }
                    ]
                }
            ]
        }
        body = {"sgg": {"text": "Loan", "completion": {"field": "suggest", "size": 10}}}
        res = suggest(text="Loan", size=10)
        self.assertEqual(len(mock_suggest.call_args), 2)
        self.assertEqual(0, len(mock_suggest.call_args[0]))
        self.assertEqual(2, len(mock_suggest.call_args[1]))
        act_body = mock_suggest.call_args[1]['body']
        self.assertDictEqual(mock_suggest.call_args[1]['body'], body)
        self.assertEqual(mock_suggest.call_args[1]['index'], 'INDEX')
        self.assertEqual(['test 1', 'test 2'], res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch("complaint_search.es_interface._COMPLAINT_DOC_TYPE", "DOC_TYPE")
    @mock.patch.object(Elasticsearch, 'search')
    def test_document__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {"query": {"term": {"_id": 123456}}}
        res = document(123456)
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(3, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['doc_type'], 'DOC_TYPE')
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res) 