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
            "post_filter": {"and": {"filters": [{"range": {"created_time": {"from": "2014-04-14"}}}]}}
        }
        res = search(min_date="2014-04-14")
        mock_search.assert_called_once_with(body=body,
            index="INDEX")
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
            "post_filter": {"and": {"filters": [{"range": {"created_time": {"to": "2017-04-14"}}}]}}
        }
        res = search(max_date="2017-04-14")
        mock_search.assert_called_once_with(body=body,
            index="INDEX")
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
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"company_name": ["Bank 1"]}},
                                {"terms": {"company_name": ["Second Bank"]}}
                            ]
                        }
                    }]
                }
            }
        }
        res = search(company=["Bank 1", "Second Bank"])
        mock_search.assert_called_once_with(body=body,
            index="INDEX")
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
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"dispute_resolution": [0]}},
                                {"terms": {"dispute_resolution": [1]}}
                            ]
                        }
                    }]
                }
            }
        }
        res = search(consumer_disputed=["No", "Yes"])
        mock_search.assert_called_once_with(body=body,
            index="INDEX")
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
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [

                                {"terms": {"product_level_1.raw": ["Payday Loan"]}},
                                {
                                    "and": {
                                        "filters": [
                                            {"terms": {"product_level_1.raw": ["Mortgage"]}},
                                            {"terms": {"product.raw": ["FHA Mortgage"]}}
                                        ]
                                    }
                                }
                            ]
                        }
                    }]
                }
            }
        }
        res = search(product=["Payday Loan", u"Mortgage\u2022FHA Mortgage"])
        mock_search.assert_called_once_with(body=body,
            index="INDEX")
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
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {
                                    "and": {
                                        "filters": [
                                            {"terms": {"category_level_1.raw": ["Communication tactics"]}},
                                            {"terms": {"category.raw": ["Frequent or repeated calls"]}}
                                        ]
                                    }
                                },
                                {"terms": {"category_level_1.raw": ["Loan servicing, payments, escrow account"]}}
                            ]
                        }
                    }]
                }
            }
        }
        res = search(issue=[u"Communication tactics\u2022Frequent or repeated calls",
        "Loan servicing, payments, escrow account"])
        mock_search.assert_called_once_with(body=body,
            index="INDEX")
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
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"ccmail_state": ["CA"]}},
                                {"terms": {"ccmail_state": ["VA"]}},
                                {"terms": {"ccmail_state": ["OR"]}}
                            ]
                        }
                    }]
                }
            }
        }
        res = search(state=["CA", "VA", "OR"])
        mock_search.assert_called_once_with(body=body,
            index="INDEX")
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
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"ccmail_zipcode": ["12345"]}},
                                {"terms": {"ccmail_zipcode": ["23435"]}},
                                {"terms": {"ccmail_zipcode": ["03433"]}}
                            ]
                        }
                    }]
                }
            }
        }
        res = search(zip_code=["12345", "23435", "03433"])
        mock_search.assert_called_once_with(body=body,
            index="INDEX")
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
            }
        }
        res = search(timely=["Yes", "No"])
        mock_search.assert_called_once_with(body=body,
            index="INDEX")
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
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"comp_status_archive": ["Closed"]}},
                                {"terms": {"comp_status_archive": ["No response"]}}
                            ]
                        }
                    }]
                }
            }
        }
        res = search(company_response=["Closed", "No response"])
        mock_search.assert_called_once_with(body=body,
            index="INDEX")
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
            "post_filter": {
                "and": {
                    "filters": [{ 
                        "bool": {
                            "should": [
                                {"terms": {"company_public_response": ["Response 1"]}},
                                {"terms": {"company_public_response": ["Response 2"]}}
                            ]
                        }
                    }]
                }
            }
        }
        res = search(company_public_response=["Response 1", "Response 2"])
        mock_search.assert_called_once_with(body=body,
            index="INDEX")
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
        mock_suggest.assert_called_once_with(body=body,
            index="INDEX")
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch.object(Elasticsearch, 'suggest')
    def test_suggest_with_size__valid(self, mock_suggest):
        mock_suggest.return_value = 'OK'
        body = {"sgg": {"text": "Loan", "completion": {"field": "suggest", "size": 10}}}
        res = suggest(text="Loan", size=10)
        mock_suggest.assert_called_once_with(body=body,
            index="INDEX")
        self.assertEqual('OK', res)

    @mock.patch("complaint_search.es_interface._COMPLAINT_ES_INDEX", "INDEX")
    @mock.patch("complaint_search.es_interface._COMPLAINT_DOC_TYPE", "DOC_TYPE")
    @mock.patch.object(Elasticsearch, 'search')
    def test_document__valid(self, mock_search):
        mock_search.return_value = 'OK'
        body = {"query": {"term": {"_id": 123456}}}
        res = document(123456)
        mock_search.assert_called_once_with(body=body, doc_type="DOC_TYPE",
            index="INDEX")
        self.assertEqual('OK', res) 