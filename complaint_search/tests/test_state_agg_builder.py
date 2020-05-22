import copy

from django.test import TestCase

from complaint_search.es_builders import StateAggregationBuilder
from complaint_search.tests.test_es_interface import assertBodyEqual


# -------------------------------------------------------------------------
# Helper Methods
# -------------------------------------------------------------------------


class Test_StateAggregationBuilder(TestCase):
    EXPECTED = {
        "issue": {
            "aggs": {
                "issue": {
                    "terms": {
                        "field": "issue.raw",
                        "size": 5
                    }
                }
            },
            "filter": {
                "bool": {
                    "filter": [],
                    "must": [],
                    "should": []
                }
            }
        },
        "product": {
            "aggs": {
                "product": {
                    "terms": {
                        "field": "product.raw",
                        "size": 5
                    }
                }
            },
            "filter": {
                "bool": {
                    "filter": [],
                    "must": [],
                    "should": []
                }
            }
        },
        "state": {
            "aggs": {
                "state": {
                    "aggs": {
                        "issue": {
                            "terms": {
                                "field": "issue.raw",
                                "size": 1
                            }
                        },
                        "product": {
                            "terms": {
                                "field": "product.raw",
                                "size": 1
                            }
                        }
                    },
                    "terms": {
                        "field": "state",
                        "size": 0
                    }
                }
            },
            "filter": {
                "bool": {
                    "filter": [],
                    "must": [],
                    "should": []
                }
            }
        }
    }

    def add_filter(self, clause):
        self.expected['issue']['filter']['bool']['filter'].append(clause)
        self.expected['product']['filter']['bool']['filter'].append(clause)
        self.expected['state']['filter']['bool']['filter'].append(clause)

    # -------------------------------------------------------------------------
    # Test Methods
    # -------------------------------------------------------------------------

    def setUp(self):
        self.target = StateAggregationBuilder()
        self.expected = copy.deepcopy(self.EXPECTED)

    def test_company_received_filter(self):
        clause = {
            "range": {
                "date_sent_to_company": {
                    "from": "2014-04-14T12:00:00-05:00"
                }
            }
        }
        self.add_filter(clause)
        self.target.add(company_received_min="2014-04-14")

        actual = self.target.build()

        assertBodyEqual(self.expected, actual)

    def test_date_filter(self):
        clause = {
            "range": {
                "date_received": {
                    "from": "2014-04-14T12:00:00-05:00"
                }
            }
        }
        self.add_filter(clause)
        self.target.add(date_received_min="2014-04-14")

        actual = self.target.build()

        assertBodyEqual(self.expected, actual)

    def test_issue_filter(self):
        clause = {
            "bool": {
                "should": [
                    {
                        "terms": {
                            "issue.raw": [
                                "foo"
                            ]
                        }
                    }
                ]
            }
        }
        # state and product have the filter
        self.add_filter(clause)
        # but issue should not have the filter
        self.expected['issue']['filter']['bool']['filter'] = []
        self.target.add(issue=['foo'])

        actual = self.target.build()

        assertBodyEqual(self.expected, actual)

    def test_product_filter(self):
        clause = {
            "bool": {
                "should": [
                    {
                        "terms": {
                            "product.raw": [
                                "foo"
                            ]
                        }
                    }
                ]
            }
        }
        # state and issue have the filter
        self.add_filter(clause)
        # but product should not have the filter
        self.expected['product']['filter']['bool']['filter'] = []
        self.target.add(product=['foo'])

        actual = self.target.build()

        assertBodyEqual(self.expected, actual)

    def test_state_filter(self):
        clause = {
            "bool": {
                "should": {
                    "terms": {
                        "state": [
                            "CA",
                            "VA",
                            "OR"
                        ]
                    }
                }
            }
        }
        # issue and product have the filter
        self.add_filter(clause)
        # but state should not have the filter
        self.expected['state']['filter']['bool']['filter'] = []
        self.target.add(state=["CA", "VA", "OR"])

        actual = self.target.build()

        assertBodyEqual(self.expected, actual)
