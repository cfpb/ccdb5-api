from django.test import TestCase
from complaint_search.es_interface import _ES_URL, _COMPLAINT_ES_INDEX, _COMPLAINT_DOC_TYPE, _ES_USER, _ES_PASSWORD, search, suggest, document
from elasticsearch import Elasticsearch
import requests
import os
import urllib
import json
import deep
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
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {"and": {"filters": []}},
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search()
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        mock_rget.assert_not_called()
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._ES_URL", "ES_URL")
    @mock.patch("complaint_search.es_interface._ES_USER", "ES_USER")
    @mock.patch("complaint_search.es_interface._ES_PASSWORD", "ES_PASSWORD")
    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch("complaint_search.es_interface._COMPLAINT_DOC_TYPE", "DOC_TYPE")
    @mock.patch.object(Elasticsearch, 'search')
    @mock.patch('requests.get', ok=True, content="RGET_OK")
    @mock.patch('json.dumps')
    @mock.patch('urllib.urlencode')
    def test_search_with_fmt_nonjson__valid(self, mock_urlencode, mock_jdump, mock_rget, mock_search):
        mock_search.return_value = 'OK'
        mock_jdump.return_value = 'JDUMPS_OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {"and": {"filters": []}},
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        for fmt in ["csv", "xls", "xlsx"]:
            res = search(fmt=fmt)
            self.assertEqual(len(mock_jdump.call_args), 2)
            self.assertEqual(1, len(mock_jdump.call_args[0]))
            act_body = mock_jdump.call_args[0][0]
            diff = deep.diff(body, act_body)
            if diff:
                print "fmt={}".format(fmt)
                diff.print_full()
            self.assertEqual(len(mock_urlencode.call_args), 2)
            self.assertEqual(1, len(mock_urlencode.call_args[0]))
            param = {"format": fmt, "source": "JDUMPS_OK"}
            act_param = mock_urlencode.call_args[0][0]
            self.assertEqual(param, act_param)

        self.assertEqual(mock_jdump.call_count, 3)
        self.assertEqual(mock_urlencode.call_count, 3)
        
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
            "post_filter": {"and": {"filters": []}},
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }

        }
        res = search(field="test_field")
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
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
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {"and": {"filters": []}},
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
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
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {"and": {"filters": []}},
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(frm=20)
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
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
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "post_filter": {"and": {"filters": []}},
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
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
                    "complaint_what_happened": {
                        "query": "test_term", 
                        "operator": "and"
                    }
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {"and": {"filters": []}},
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(search_term="test_term")
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_min_date__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [
                        {
                            "range": {
                                "date_received": {
                                    "from": "2014-04-14"
                                }
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "from": "2014-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "from": "2014-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "from": "2014-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "from": "2014-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "from": "2014-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "from": "2014-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "from": "2014-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "from": "2014-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "from": "2014-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "from": "2014-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "from": "2014-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "from": "2014-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "from": "2014-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(min_date="2014-04-14")
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_max_date__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [
                        {
                            "range": {
                                "date_received": {
                                    "to": "2017-04-14"
                                }
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "to": "2017-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "to": "2017-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "to": "2017-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "to": "2017-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "to": "2017-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "to": "2017-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "to": "2017-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "to": "2017-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "to": "2017-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "to": "2017-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "to": "2017-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "to": "2017-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {
                                            "to": "2017-04-14"
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(max_date="2017-04-14")
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_company__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [
                        { 
                            "bool": {
                                "should": [
                                    {"terms": {"company": ["Bank 1"]}},
                                    {"terms": {"company": ["Second Bank"]}}
                                ]
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company": ["Bank 1"]}},
                                            {"terms": {"company": ["Second Bank"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company": ["Bank 1"]}},
                                            {"terms": {"company": ["Second Bank"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company": ["Bank 1"]}},
                                            {"terms": {"company": ["Second Bank"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company": ["Bank 1"]}},
                                            {"terms": {"company": ["Second Bank"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company": ["Bank 1"]}},
                                            {"terms": {"company": ["Second Bank"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company": ["Bank 1"]}},
                                            {"terms": {"company": ["Second Bank"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company": ["Bank 1"]}},
                                            {"terms": {"company": ["Second Bank"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company": ["Bank 1"]}},
                                            {"terms": {"company": ["Second Bank"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company": ["Bank 1"]}},
                                            {"terms": {"company": ["Second Bank"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company": ["Bank 1"]}},
                                            {"terms": {"company": ["Second Bank"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company": ["Bank 1"]}},
                                            {"terms": {"company": ["Second Bank"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company": ["Bank 1"]}},
                                            {"terms": {"company": ["Second Bank"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(company=["Bank 1", "Second Bank"])
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        diff = deep.diff(body, act_body)
        if diff:
            print "company"
            diff.print_full()
        self.assertIsNone(deep.diff(body, act_body))
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)


    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_product__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [
                        { 
                            "bool": {
                                "should": [

                                    {"terms": {"product.raw": ["Payday Loan"]}},
                                    {
                                        "and": {
                                            "filters": [
                                                {"terms": {"product.raw": ["Mortgage"]}},
                                                {"terms": {"sub_product.raw": ["FHA Mortgage"]}}
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [

                                            {"terms": {"product.raw": ["Payday Loan"]}},
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"product.raw": ["Mortgage"]}},
                                                        {"terms": {"sub_product.raw": ["FHA Mortgage"]}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [

                                            {"terms": {"product.raw": ["Payday Loan"]}},
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"product.raw": ["Mortgage"]}},
                                                        {"terms": {"sub_product.raw": ["FHA Mortgage"]}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [

                                            {"terms": {"product.raw": ["Payday Loan"]}},
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"product.raw": ["Mortgage"]}},
                                                        {"terms": {"sub_product.raw": ["FHA Mortgage"]}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [

                                            {"terms": {"product.raw": ["Payday Loan"]}},
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"product.raw": ["Mortgage"]}},
                                                        {"terms": {"sub_product.raw": ["FHA Mortgage"]}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [

                                            {"terms": {"product.raw": ["Payday Loan"]}},
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"product.raw": ["Mortgage"]}},
                                                        {"terms": {"sub_product.raw": ["FHA Mortgage"]}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [

                                            {"terms": {"product.raw": ["Payday Loan"]}},
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"product.raw": ["Mortgage"]}},
                                                        {"terms": {"sub_product.raw": ["FHA Mortgage"]}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [

                                            {"terms": {"product.raw": ["Payday Loan"]}},
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"product.raw": ["Mortgage"]}},
                                                        {"terms": {"sub_product.raw": ["FHA Mortgage"]}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [

                                            {"terms": {"product.raw": ["Payday Loan"]}},
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"product.raw": ["Mortgage"]}},
                                                        {"terms": {"sub_product.raw": ["FHA Mortgage"]}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [

                                            {"terms": {"product.raw": ["Payday Loan"]}},
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"product.raw": ["Mortgage"]}},
                                                        {"terms": {"sub_product.raw": ["FHA Mortgage"]}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [

                                            {"terms": {"product.raw": ["Payday Loan"]}},
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"product.raw": ["Mortgage"]}},
                                                        {"terms": {"sub_product.raw": ["FHA Mortgage"]}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [

                                            {"terms": {"product.raw": ["Payday Loan"]}},
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"product.raw": ["Mortgage"]}},
                                                        {"terms": {"sub_product.raw": ["FHA Mortgage"]}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [

                                            {"terms": {"product.raw": ["Payday Loan"]}},
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"product.raw": ["Mortgage"]}},
                                                        {"terms": {"sub_product.raw": ["FHA Mortgage"]}}
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(product=["Payday Loan", u"Mortgage\u2022FHA Mortgage"])
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        diff = deep.diff(body, act_body)
        if diff:
            print "product"
            diff.print_full()
        self.assertIsNone(deep.diff(body, act_body))
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)  

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_issue__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {
                                    "and": {
                                        "filters": [
                                            {"terms": {"issue.raw": ["Communication tactics"]}},
                                            {"terms": {"sub_issue.raw": ["Frequent or repeated calls"]}}
                                        ]
                                    }
                                },
                                {"terms": {"issue.raw": ["Loan servicing, payments, escrow account"]}}
                            ]
                        }
                    }]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"issue.raw": ["Communication tactics"]}},
                                                        {"terms": {"sub_issue.raw": ["Frequent or repeated calls"]}}
                                                    ]
                                                }
                                            },
                                            {"terms": {"issue.raw": ["Loan servicing, payments, escrow account"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"issue.raw": ["Communication tactics"]}},
                                                        {"terms": {"sub_issue.raw": ["Frequent or repeated calls"]}}
                                                    ]
                                                }
                                            },
                                            {"terms": {"issue.raw": ["Loan servicing, payments, escrow account"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"issue.raw": ["Communication tactics"]}},
                                                        {"terms": {"sub_issue.raw": ["Frequent or repeated calls"]}}
                                                    ]
                                                }
                                            },
                                            {"terms": {"issue.raw": ["Loan servicing, payments, escrow account"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"issue.raw": ["Communication tactics"]}},
                                                        {"terms": {"sub_issue.raw": ["Frequent or repeated calls"]}}
                                                    ]
                                                }
                                            },
                                            {"terms": {"issue.raw": ["Loan servicing, payments, escrow account"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"issue.raw": ["Communication tactics"]}},
                                                        {"terms": {"sub_issue.raw": ["Frequent or repeated calls"]}}
                                                    ]
                                                }
                                            },
                                            {"terms": {"issue.raw": ["Loan servicing, payments, escrow account"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"issue.raw": ["Communication tactics"]}},
                                                        {"terms": {"sub_issue.raw": ["Frequent or repeated calls"]}}
                                                    ]
                                                }
                                            },
                                            {"terms": {"issue.raw": ["Loan servicing, payments, escrow account"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"issue.raw": ["Communication tactics"]}},
                                                        {"terms": {"sub_issue.raw": ["Frequent or repeated calls"]}}
                                                    ]
                                                }
                                            },
                                            {"terms": {"issue.raw": ["Loan servicing, payments, escrow account"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"issue.raw": ["Communication tactics"]}},
                                                        {"terms": {"sub_issue.raw": ["Frequent or repeated calls"]}}
                                                    ]
                                                }
                                            },
                                            {"terms": {"issue.raw": ["Loan servicing, payments, escrow account"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"issue.raw": ["Communication tactics"]}},
                                                        {"terms": {"sub_issue.raw": ["Frequent or repeated calls"]}}
                                                    ]
                                                }
                                            },
                                            {"terms": {"issue.raw": ["Loan servicing, payments, escrow account"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"issue.raw": ["Communication tactics"]}},
                                                        {"terms": {"sub_issue.raw": ["Frequent or repeated calls"]}}
                                                    ]
                                                }
                                            },
                                            {"terms": {"issue.raw": ["Loan servicing, payments, escrow account"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"issue.raw": ["Communication tactics"]}},
                                                        {"terms": {"sub_issue.raw": ["Frequent or repeated calls"]}}
                                                    ]
                                                }
                                            },
                                            {"terms": {"issue.raw": ["Loan servicing, payments, escrow account"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {
                                                "and": {
                                                    "filters": [
                                                        {"terms": {"issue.raw": ["Communication tactics"]}},
                                                        {"terms": {"sub_issue.raw": ["Frequent or repeated calls"]}}
                                                    ]
                                                }
                                            },
                                            {"terms": {"issue.raw": ["Loan servicing, payments, escrow account"]}}
                                        ]
                                    }
                                }   
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(issue=[u"Communication tactics\u2022Frequent or repeated calls",
        "Loan servicing, payments, escrow account"])
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        diff = deep.diff(body, act_body)
        if diff:
            print "issue"
            diff.print_full()
            print "body"
            print body
            print "act_body"
            print act_body
        self.assertIsNone(deep.diff(body, act_body))
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)  

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_state__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"state": ["CA"]}},
                                {"terms": {"state": ["VA"]}},
                                {"terms": {"state": ["OR"]}}
                            ]
                        }
                    }]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"state": ["CA"]}},
                                            {"terms": {"state": ["VA"]}},
                                            {"terms": {"state": ["OR"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"state": ["CA"]}},
                                            {"terms": {"state": ["VA"]}},
                                            {"terms": {"state": ["OR"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"state": ["CA"]}},
                                            {"terms": {"state": ["VA"]}},
                                            {"terms": {"state": ["OR"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"state": ["CA"]}},
                                            {"terms": {"state": ["VA"]}},
                                            {"terms": {"state": ["OR"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"state": ["CA"]}},
                                            {"terms": {"state": ["VA"]}},
                                            {"terms": {"state": ["OR"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"state": ["CA"]}},
                                            {"terms": {"state": ["VA"]}},
                                            {"terms": {"state": ["OR"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"state": ["CA"]}},
                                            {"terms": {"state": ["VA"]}},
                                            {"terms": {"state": ["OR"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"state": ["CA"]}},
                                            {"terms": {"state": ["VA"]}},
                                            {"terms": {"state": ["OR"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"state": ["CA"]}},
                                            {"terms": {"state": ["VA"]}},
                                            {"terms": {"state": ["OR"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"state": ["CA"]}},
                                            {"terms": {"state": ["VA"]}},
                                            {"terms": {"state": ["OR"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"state": ["CA"]}},
                                            {"terms": {"state": ["VA"]}},
                                            {"terms": {"state": ["OR"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"state": ["CA"]}},
                                            {"terms": {"state": ["VA"]}},
                                            {"terms": {"state": ["OR"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(state=["CA", "VA", "OR"])
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        diff = deep.diff(body, act_body)
        if diff:
            print "state"
            diff.print_full()
        self.assertIsNone(deep.diff(body, act_body))
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_zip_code__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"zip_code": ["12345"]}},
                                {"terms": {"zip_code": ["23435"]}},
                                {"terms": {"zip_code": ["03433"]}}
                            ]
                        }
                    }]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"zip_code": ["12345"]}},
                                            {"terms": {"zip_code": ["23435"]}},
                                            {"terms": {"zip_code": ["03433"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"zip_code": ["12345"]}},
                                            {"terms": {"zip_code": ["23435"]}},
                                            {"terms": {"zip_code": ["03433"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"zip_code": ["12345"]}},
                                            {"terms": {"zip_code": ["23435"]}},
                                            {"terms": {"zip_code": ["03433"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"zip_code": ["12345"]}},
                                            {"terms": {"zip_code": ["23435"]}},
                                            {"terms": {"zip_code": ["03433"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"zip_code": ["12345"]}},
                                            {"terms": {"zip_code": ["23435"]}},
                                            {"terms": {"zip_code": ["03433"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"zip_code": ["12345"]}},
                                            {"terms": {"zip_code": ["23435"]}},
                                            {"terms": {"zip_code": ["03433"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"zip_code": ["12345"]}},
                                            {"terms": {"zip_code": ["23435"]}},
                                            {"terms": {"zip_code": ["03433"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"zip_code": ["12345"]}},
                                            {"terms": {"zip_code": ["23435"]}},
                                            {"terms": {"zip_code": ["03433"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"zip_code": ["12345"]}},
                                            {"terms": {"zip_code": ["23435"]}},
                                            {"terms": {"zip_code": ["03433"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"zip_code": ["12345"]}},
                                            {"terms": {"zip_code": ["23435"]}},
                                            {"terms": {"zip_code": ["03433"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"zip_code": ["12345"]}},
                                            {"terms": {"zip_code": ["23435"]}},
                                            {"terms": {"zip_code": ["03433"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"zip_code": ["12345"]}},
                                            {"terms": {"zip_code": ["23435"]}},
                                            {"terms": {"zip_code": ["03433"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(zip_code=["12345", "23435", "03433"])
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        diff = deep.diff(body, act_body)
        if diff:
            print "zip_code"
            diff.print_full()
        self.assertIsNone(deep.diff(body, act_body))
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_timely__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"timely": ["Yes"]}},
                                {"terms": {"timely": ["No"]}}
                            ]
                        }
                    }]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"timely": ["Yes"]}},
                                            {"terms": {"timely": ["No"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"timely": ["Yes"]}},
                                            {"terms": {"timely": ["No"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"timely": ["Yes"]}},
                                            {"terms": {"timely": ["No"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"timely": ["Yes"]}},
                                            {"terms": {"timely": ["No"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"timely": ["Yes"]}},
                                            {"terms": {"timely": ["No"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"timely": ["Yes"]}},
                                            {"terms": {"timely": ["No"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"timely": ["Yes"]}},
                                            {"terms": {"timely": ["No"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"timely": ["Yes"]}},
                                            {"terms": {"timely": ["No"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"timely": ["Yes"]}},
                                            {"terms": {"timely": ["No"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"timely": ["Yes"]}},
                                            {"terms": {"timely": ["No"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"timely": ["Yes"]}},
                                            {"terms": {"timely": ["No"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"timely": ["Yes"]}},
                                            {"terms": {"timely": ["No"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(timely=["Yes", "No"])
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        diff = deep.diff(body, act_body)
        if diff:
            print "timely"
            diff.print_full()
        self.assertIsNone(deep.diff(body, act_body))
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_company_response__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"company_response": ["Closed"]}},
                                {"terms": {"company_response": ["No response"]}}
                            ]
                        }
                    }]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_response": ["Closed"]}},
                                            {"terms": {"company_response": ["No response"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_response": ["Closed"]}},
                                            {"terms": {"company_response": ["No response"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_response": ["Closed"]}},
                                            {"terms": {"company_response": ["No response"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_response": ["Closed"]}},
                                            {"terms": {"company_response": ["No response"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_response": ["Closed"]}},
                                            {"terms": {"company_response": ["No response"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_response": ["Closed"]}},
                                            {"terms": {"company_response": ["No response"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_response": ["Closed"]}},
                                            {"terms": {"company_response": ["No response"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_response": ["Closed"]}},
                                            {"terms": {"company_response": ["No response"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_response": ["Closed"]}},
                                            {"terms": {"company_response": ["No response"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_response": ["Closed"]}},
                                            {"terms": {"company_response": ["No response"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_response": ["Closed"]}},
                                            {"terms": {"company_response": ["No response"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_response": ["Closed"]}},
                                            {"terms": {"company_response": ["No response"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(company_response=["Closed", "No response"])
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        diff = deep.diff(body, act_body)
        if diff:
            print "company_response"
            diff.print_full()
        self.assertIsNone(deep.diff(body, act_body))
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)
        
    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_company_public_response__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"company_public_response.raw": ["Response 1"]}},
                                {"terms": {"company_public_response.raw": ["Response 2"]}}
                            ]
                        }
                    }]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_public_response.raw": ["Response 1"]}},
                                            {"terms": {"company_public_response.raw": ["Response 2"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_public_response.raw": ["Response 1"]}},
                                            {"terms": {"company_public_response.raw": ["Response 2"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_public_response.raw": ["Response 1"]}},
                                            {"terms": {"company_public_response.raw": ["Response 2"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_public_response.raw": ["Response 1"]}},
                                            {"terms": {"company_public_response.raw": ["Response 2"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_public_response.raw": ["Response 1"]}},
                                            {"terms": {"company_public_response.raw": ["Response 2"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_public_response.raw": ["Response 1"]}},
                                            {"terms": {"company_public_response.raw": ["Response 2"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_public_response.raw": ["Response 1"]}},
                                            {"terms": {"company_public_response.raw": ["Response 2"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_public_response.raw": ["Response 1"]}},
                                            {"terms": {"company_public_response.raw": ["Response 2"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_public_response.raw": ["Response 1"]}},
                                            {"terms": {"company_public_response.raw": ["Response 2"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_public_response.raw": ["Response 1"]}},
                                            {"terms": {"company_public_response.raw": ["Response 2"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_public_response.raw": ["Response 1"]}},
                                            {"terms": {"company_public_response.raw": ["Response 2"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"company_public_response.raw": ["Response 1"]}},
                                            {"terms": {"company_public_response.raw": ["Response 2"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(company_public_response=["Response 1", "Response 2"])
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        diff = deep.diff(body, act_body)
        if diff:
            print "company_public_response.raw"
            diff.print_full()
        self.assertIsNone(deep.diff(body, act_body))
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_consumer_consent_provided__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"consumer_consent_provided.raw": ["yes"]}},
                                {"terms": {"consumer_consent_provided.raw": ["no"]}}
                            ]
                        }
                    }]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_consent_provided.raw": ["yes"]}},
                                            {"terms": {"consumer_consent_provided.raw": ["no"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_consent_provided.raw": ["yes"]}},
                                            {"terms": {"consumer_consent_provided.raw": ["no"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_consent_provided.raw": ["yes"]}},
                                            {"terms": {"consumer_consent_provided.raw": ["no"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_consent_provided.raw": ["yes"]}},
                                            {"terms": {"consumer_consent_provided.raw": ["no"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_consent_provided.raw": ["yes"]}},
                                            {"terms": {"consumer_consent_provided.raw": ["no"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_consent_provided.raw": ["yes"]}},
                                            {"terms": {"consumer_consent_provided.raw": ["no"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_consent_provided.raw": ["yes"]}},
                                            {"terms": {"consumer_consent_provided.raw": ["no"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_consent_provided.raw": ["yes"]}},
                                            {"terms": {"consumer_consent_provided.raw": ["no"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_consent_provided.raw": ["yes"]}},
                                            {"terms": {"consumer_consent_provided.raw": ["no"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_consent_provided.raw": ["yes"]}},
                                            {"terms": {"consumer_consent_provided.raw": ["no"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_consent_provided.raw": ["yes"]}},
                                            {"terms": {"consumer_consent_provided.raw": ["no"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_consent_provided.raw": ["yes"]}},
                                            {"terms": {"consumer_consent_provided.raw": ["no"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(consumer_consent_provided=["yes", "no"])
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        diff = deep.diff(body, act_body)
        if diff:
            print "consumer_consent_provided.raw"
            diff.print_full()
        self.assertIsNone(deep.diff(body, act_body))
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_submitted_via__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"submitted_via": ["mail"]}},
                                {"terms": {"submitted_via": ["web"]}}
                            ]
                        }
                    }]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"submitted_via": ["mail"]}},
                                            {"terms": {"submitted_via": ["web"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"submitted_via": ["mail"]}},
                                            {"terms": {"submitted_via": ["web"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"submitted_via": ["mail"]}},
                                            {"terms": {"submitted_via": ["web"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"submitted_via": ["mail"]}},
                                            {"terms": {"submitted_via": ["web"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"submitted_via": ["mail"]}},
                                            {"terms": {"submitted_via": ["web"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"submitted_via": ["mail"]}},
                                            {"terms": {"submitted_via": ["web"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"submitted_via": ["mail"]}},
                                            {"terms": {"submitted_via": ["web"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"submitted_via": ["mail"]}},
                                            {"terms": {"submitted_via": ["web"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"submitted_via": ["mail"]}},
                                            {"terms": {"submitted_via": ["web"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"submitted_via": ["mail"]}},
                                            {"terms": {"submitted_via": ["web"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"submitted_via": ["mail"]}},
                                            {"terms": {"submitted_via": ["web"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"submitted_via": ["mail"]}},
                                            {"terms": {"submitted_via": ["web"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(submitted_via=["mail", "web"])
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        diff = deep.diff(body, act_body)
        if diff:
            print "submitted_via"
            diff.print_full()
        self.assertIsNone(deep.diff(body, act_body))
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_tag__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"tag": ["Older American"]}},
                                {"terms": {"tag": ["Servicemember"]}}
                            ]
                        }
                    }]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"tag": ["Older American"]}},
                                            {"terms": {"tag": ["Servicemember"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"tag": ["Older American"]}},
                                            {"terms": {"tag": ["Servicemember"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"tag": ["Older American"]}},
                                            {"terms": {"tag": ["Servicemember"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"tag": ["Older American"]}},
                                            {"terms": {"tag": ["Servicemember"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"tag": ["Older American"]}},
                                            {"terms": {"tag": ["Servicemember"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"tag": ["Older American"]}},
                                            {"terms": {"tag": ["Servicemember"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"tag": ["Older American"]}},
                                            {"terms": {"tag": ["Servicemember"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"tag": ["Older American"]}},
                                            {"terms": {"tag": ["Servicemember"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"tag": ["Older American"]}},
                                            {"terms": {"tag": ["Servicemember"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"tag": ["Older American"]}},
                                            {"terms": {"tag": ["Servicemember"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"tag": ["Older American"]}},
                                            {"terms": {"tag": ["Servicemember"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"tag": ["Older American"]}},
                                            {"terms": {"tag": ["Servicemember"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(tag=["Older American", "Servicemember"])
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        diff = deep.diff(body, act_body)
        if diff:
            print "tag"
            diff.print_full()
        self.assertIsNone(deep.diff(body, act_body))
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_consumer_disputed__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"consumer_disputed": [0]}},
                                {"terms": {"consumer_disputed": [1]}}
                            ]
                        }
                    }]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_disputed": [0]}},
                                            {"terms": {"consumer_disputed": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_disputed": [0]}},
                                            {"terms": {"consumer_disputed": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_disputed": [0]}},
                                            {"terms": {"consumer_disputed": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_disputed": [0]}},
                                            {"terms": {"consumer_disputed": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_disputed": [0]}},
                                            {"terms": {"consumer_disputed": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_disputed": [0]}},
                                            {"terms": {"consumer_disputed": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_disputed": [0]}},
                                            {"terms": {"consumer_disputed": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_disputed": [0]}},
                                            {"terms": {"consumer_disputed": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_disputed": [0]}},
                                            {"terms": {"consumer_disputed": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_disputed": [0]}},
                                            {"terms": {"consumer_disputed": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_disputed": [0]}},
                                            {"terms": {"consumer_disputed": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"consumer_disputed": [0]}},
                                            {"terms": {"consumer_disputed": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(consumer_disputed=["No", "Yes"])
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        diff = deep.diff(body, act_body)
        if diff:
            print "consumer_disputed"
            diff.print_full()
        self.assertIsNone(deep.diff(body, act_body))
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'search')
    def test_search_with_has_narratives__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {
            "from": 0, 
            "size": 10, 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        "complaint_what_happened"
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            },
            "sort": [{"_score": {"order": "desc"}}],
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"has_narratives": [0]}},
                                {"terms": {"has_narratives": [1]}}
                            ]
                        }
                    }]
                }
            },
            "aggs": {
                "has_narratives": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "has_narratives": {
                            "terms": {
                                "field": "has_narratives",
                                "size": 10
                            }
                        }
                    }
                },
                "company": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"has_narratives": [0]}},
                                            {"terms": {"has_narratives": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company": {
                            "terms": {
                                "field": "company",
                                "size": 10000
                            }
                        }
                    }
                },
                "product": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"has_narratives": [0]}},
                                            {"terms": {"has_narratives": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_product.raw": {
                                    "terms": {
                                        "field": "sub_product.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "issue": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"has_narratives": [0]}},
                                            {"terms": {"has_narratives": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 10000
                            },
                            "aggs": {
                                "sub_issue.raw": {
                                    "terms": {
                                        "field": "sub_issue.raw",
                                        "size": 10000
                                    }
                                }
                            }
                        }
                    }
                },
                "state": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"has_narratives": [0]}},
                                            {"terms": {"has_narratives": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "state": {
                            "terms": {
                                "field": "state",
                                "size": 50
                            }
                        }
                    }
                },
                "zip_code": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"has_narratives": [0]}},
                                            {"terms": {"has_narratives": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "zip_code": {
                            "terms": {
                                "field": "zip_code",
                                "size": 1000
                            }
                        }
                    }
                },
                "timely": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"has_narratives": [0]}},
                                            {"terms": {"has_narratives": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "timely": {
                            "terms": {
                                "field": "timely",
                                "size": 10
                            }
                        }
                    }
                },
                "company_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"has_narratives": [0]}},
                                            {"terms": {"has_narratives": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_response": {
                            "terms": {
                                "field": "company_response",
                                "size": 100
                            }
                        }
                    }
                },
                "company_public_response": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"has_narratives": [0]}},
                                            {"terms": {"has_narratives": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "company_public_response": {
                            "terms": {
                                "field": "company_public_response.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_disputed": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"has_narratives": [0]}},
                                            {"terms": {"has_narratives": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_disputed": {
                            "terms": {
                                "field": "consumer_disputed",
                                "size": 100
                            }
                        }
                    }
                },
                "consumer_consent_provided": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"has_narratives": [0]}},
                                            {"terms": {"has_narratives": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "consumer_consent_provided": {
                            "terms": {
                                "field": "consumer_consent_provided.raw",
                                "size": 100
                            }
                        }
                    }
                },
                "tag": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"has_narratives": [0]}},
                                            {"terms": {"has_narratives": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "tag": {
                            "terms": {
                                "field": "tag",
                                "size": 100
                            }
                        }
                    }
                },
                "submitted_via": {
                    "filter": {
                        "and": {
                            "filters": [
                                {
                                    "range": {
                                        "date_received": {}
                                    }
                                },
                                { 
                                    "bool": {
                                        "should": [
                                            {"terms": {"has_narratives": [0]}},
                                            {"terms": {"has_narratives": [1]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "submitted_via": {
                            "terms": {
                                "field": "submitted_via",
                                "size": 100
                            }
                        }
                    }
                }

            }
        }
        res = search(has_narratives=["No", "Yes"])
        self.assertEqual(len(mock_search.call_args), 2)
        self.assertEqual(0, len(mock_search.call_args[0]))
        self.assertEqual(2, len(mock_search.call_args[1]))
        act_body = mock_search.call_args[1]['body']
        diff = deep.diff(body, act_body)
        if diff:
            print "has_narratives"
            diff.print_full()
        self.assertIsNone(deep.diff(body, act_body))
        self.assertDictEqual(mock_search.call_args[1]['body'], body)
        self.assertEqual(mock_search.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)


    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'suggest')
    def test_suggest_with_no_param__valid(self, mock_suggest):
        mock_suggest.return_value = 'OK'
        body = {}
        res = suggest()
        mock_suggest.assert_not_called()
        self.assertEqual({}, res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'suggest')
    def test_suggest_with_text__valid(self, mock_suggest):
        mock_suggest.return_value = 'OK'
        body = {"sgg": {"text": "Mortgage", "completion": {"field": "suggest", "size": 6}}}
        res = suggest(text="Mortgage")
        self.assertEqual(len(mock_suggest.call_args), 2)
        self.assertEqual(0, len(mock_suggest.call_args[0]))
        self.assertEqual(2, len(mock_suggest.call_args[1]))
        act_body = mock_suggest.call_args[1]['body']
        self.assertDictEqual(mock_suggest.call_args[1]['body'], body)
        self.assertEqual(mock_suggest.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'suggest')
    def test_suggest_with_size__valid(self, mock_suggest):
        mock_suggest.return_value = 'OK'
        body = {"sgg": {"text": "Loan", "completion": {"field": "suggest", "size": 10}}}
        res = suggest(text="Loan", size=10)
        self.assertEqual(len(mock_suggest.call_args), 2)
        self.assertEqual(0, len(mock_suggest.call_args[0]))
        self.assertEqual(2, len(mock_suggest.call_args[1]))
        act_body = mock_suggest.call_args[1]['body']
        self.assertDictEqual(mock_suggest.call_args[1]['body'], body)
        self.assertEqual(mock_suggest.call_args[1]['index'], 'INDEX')
        self.assertEqual('OK', res)

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