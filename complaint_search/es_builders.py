import abc
import copy
import re
from collections import OrderedDict

from complaint_search.defaults import (
    DATA_SUB_LENS_MAP,
    DELIMITER,
    EXPORT_FORMATS,
    PARAMS,
    SOURCE_FIELDS,
)


def build_search_terms(search_term, field):
    if (re.match(r"^[A-Za-z\d\s]+$", search_term) and not
        any(keyword in search_term
            for keyword in ("AND", "OR", "NOT", "TO"))):

        # Match Query
        return {
            "match": {
                field: {
                    "query": search_term,
                    "operator": "and"
                }
            }
        }
    else:
        # QueryString Query
        return {
            "query_string": {
                "query": search_term,
                "fields": [
                    field
                ],
                "default_operator": "AND"
            }
        }


class BaseBuilder(object):
    __metaclass__ = abc.ABCMeta

    # Filters for those with string type
    _OPTIONAL_FILTERS = (
        "company",
        "company_public_response",
        "company_response",
        "consumer_consent_provided",
        "consumer_disputed",
        "issue",
        "product",
        "state",
        "submitted_via",
        "tags",
        "timely",
        "zip_code",
    )

    # Filters for those that need conversion from string to boolean
    _OPTIONAL_FILTERS_STRING_TO_BOOL = ("has_narrative",)

    # Filters that use different names in Elasticsearch
    _OPTIONAL_FILTERS_PARAM_TO_ES_MAP = {
        "company_public_response": "company_public_response.raw",
        "company": "company.raw",
        "consumer_consent_provided": "consumer_consent_provided.raw",
        "consumer_disputed": "consumer_disputed.raw",
        "issue": "issue.raw",
        "product": "product.raw",
        "sub_issue": "sub_issue.raw",
        "sub_product": "sub_product.raw",
    }

    # Filters that have a child and this maps to their child's name
    _OPTIONAL_FILTERS_CHILD_MAP = {
        "issue": "sub_issue",
        "product": "sub_product",
    }

    def _get_es_name(self, field):
        return self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(field, field)

    def _has_child(self, field):
        return field in self._OPTIONAL_FILTERS_CHILD_MAP

    def _get_child(self, field):
        return self._OPTIONAL_FILTERS_CHILD_MAP.get(field)

    def __init__(self):
        self.params = {}

    def add(self, **kwargs):
        self.params.update(**kwargs)

    @abc.abstractmethod
    def build(self):
        """Method that will build the body dictionary."""

    # This create all the bool should filter clauses for a field
    # es_field_name: a field name (to be filtered in ES)
    # value_list: a list of values to be filtered for this field
    # with_child: set to true if this field has a child field
    # es_child_field_name: if with_child is true, this holds the field
    # name of the child used (to be filtered in ES)
    def _build_bool_clauses(self, field):
        es_field_name = self._get_es_name(field)
        value_list = (
            [
                0 if cd.lower() == "no" else 1 for cd in self.params[field]
            ]
            if field in self._OPTIONAL_FILTERS_STRING_TO_BOOL
            else self.params.get(field)
        )

        if value_list:
            # The most common property for data is to not have a child element
            if not self._has_child(field):
                term_list_container = {"terms": {es_field_name: []}}

                term_list_container["terms"][es_field_name] = value_list

                return term_list_container
            else:
                item_dict = OrderedDict()
                for v in value_list:
                    v_pair = v.split(DELIMITER)
                    item_dict.setdefault(v_pair[0], [])
                    if len(v_pair) == 2:
                        # put subproduct into list
                        item_dict[v_pair[0]].append(v_pair[1])

                # Go through item_dict to create filters
                f_list = []
                for item, child in item_dict.items():
                    # Always append the item to list
                    parent_term = {"terms": {es_field_name: [item]}}
                    if not child:
                        f_list.append(parent_term)
                    else:
                        child_term = {"terms": {
                            self._get_es_name(self._get_child(field)): child
                        }}
                        parent_child_bool_structure = {"bool": {
                            "must": [], "should": []
                        }}
                        parent_child_bool_structure["bool"]["must"].append(
                            parent_term)
                        parent_child_bool_structure["bool"]["should"].append(
                            child_term)

                        f_list.append(parent_child_bool_structure)

                return f_list

    # This creates a dictionary of all filter_clauses, where the keys are the
    # field name
    def _build_filter_clauses(self):
        filter_clauses = {}
        for item in self.params:
            if item in (self._OPTIONAL_FILTERS +
                        self._OPTIONAL_FILTERS_STRING_TO_BOOL):
                filter_clauses[item] = self._build_bool_clauses(item)
        return filter_clauses

    def _build_date_range_filter(self, date_min, date_max, es_field_name):
        date_clause = {}
        timeSuffix = u'T12:00:00-05:00'
        if date_min or date_max:
            date_clause = {"range": {es_field_name: {}}}
            if date_min:
                d = str(date_min) + timeSuffix
                date_clause["range"][es_field_name]["from"] = d
            if date_max:
                d = str(date_max) + timeSuffix
                date_clause["range"][es_field_name]["to"] = d

        return date_clause


class SearchBuilder(BaseBuilder):
    def __init__(self):
        self.params = copy.deepcopy(PARAMS)

    def _build_highlight(self):
        highlight = {
            "require_field_match": False,
            "number_of_fragments": 1,
            "fragment_size": 500
        }
        if self.params.get("field") == "_all":
            highlight["fields"] = {source: {} for source in SOURCE_FIELDS}
        else:
            highlight["fields"] = {self.params.get("field"): {}}

        return highlight

    def _build_sort(self):
        sort_field_mapping = {
            "relevance": "_score",
            "created_date": "date_received"
        }

        sort_field, sort_order = self.params.get("sort").rsplit("_", 1)
        sort_field = sort_field_mapping.get(sort_field, "_score")
        return [{sort_field: {"order": sort_order}}]

    def _build_source(self):
        source = list(SOURCE_FIELDS)
        if self.params.get("format") in EXPORT_FORMATS:
            source.remove('has_narrative')
        if self.params.get("format") == 'csv':
            source.remove('date_received')
            source.remove('date_sent_to_company')
            source.append('date_received_formatted')
            source.append('date_sent_to_company_formatted')
        return source

    def build(self):
        search = {
            "from": self.params.get("frm"),
            "size": self.params.get("size"),
            "_source": self._build_source(),
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        self.params.get("field")
                    ],
                    "default_operator": "AND"
                }
            }
        }

        # Highlight
        if not self.params.get("no_highlight") and \
                not self.params.get("size") == 0:
            search["highlight"] = self._build_highlight()

        # sort
        if not self.params.get("size") == 0:
            search["sort"] = self._build_sort()

        # query
        search_term = self.params.get("search_term")
        if search_term:
            search["query"] = build_search_terms(
                search_term, self.params.get("field"))

        return search


class PostFilterBuilder(BaseBuilder):

    def build(self):
        filter_clauses = self._build_filter_clauses()

        post_filter = {"bool": {"should": [], "must": [], "filter": []}}

        # date_received
        date_received = self._build_date_range_filter(
            self.params.get("date_received_min"),
            self.params.get("date_received_max"),
            "date_received")

        if date_received:
            post_filter["bool"]["filter"].append(date_received)

        # company_received
        company_received = self._build_date_range_filter(
            self.params.get("company_received_min"),
            self.params.get("company_received_max"),
            "date_sent_to_company")

        if company_received:
            post_filter["bool"]["filter"].append(company_received)

        # Create filter clauses for all other filters
        for item in self.params:
            if item in (
                self._OPTIONAL_FILTERS + self._OPTIONAL_FILTERS_STRING_TO_BOOL
            ):
                # for filters selected, we are creating the field level OR
                # query that must match e.g (this OR that) AND (y or z) AND
                # servicemember
                field_level_should = {"bool": {"should": filter_clauses[item]}}
                post_filter["bool"]["filter"].append(field_level_should)

        return post_filter


class AggregationBuilder(BaseBuilder):
    _AGG_FIELDS = (
        'company',
        'company_public_response',
        'company_response',
        'consumer_consent_provided',
        'consumer_disputed',
        'has_narrative',
        'issue',
        'product',
        'state',
        'submitted_via',
        'tags',
        'timely',
        'zip_code'
    )

    def __init__(self):
        BaseBuilder.__init__(self)
        self.filter_clauses = None
        self.exclude = []

    def add_exclude(self, field_name_list):
        self.exclude += field_name_list

    def build_one(self, field_name):
        # Lazy initialization
        if not self.filter_clauses:
            self.filter_clauses = self._build_filter_clauses()

        field_aggs = {
            "filter": {
                "bool": {
                    "must": [],
                    "should": [],
                    "filter": [],
                }
            }
        }

        es_field_name = self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(
            field_name, field_name
        )
        es_child_name = None
        if field_name in self._OPTIONAL_FILTERS_CHILD_MAP:
            es_child_name = self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(
                self._OPTIONAL_FILTERS_CHILD_MAP.get(field_name))
            field_aggs["aggs"] = {
                field_name: {
                    "terms": {
                        "field": es_field_name,
                        "size": 0
                    },
                    "aggs": {
                        es_child_name: {
                            "terms": {
                                "field": es_child_name,
                                "size": 0
                            }
                        }
                    }
                }
            }
        else:
            field_aggs["aggs"] = {
                field_name: {
                    "terms": {
                        "field": es_field_name,
                        "size": 0
                    }
                }
            }

        date_filter = self._build_date_range_filter(
            self.params.get("date_received_min"),
            self.params.get("date_received_max"), "date_received")

        if date_filter:
            field_aggs["filter"]["bool"]["filter"].append(date_filter)

        company_filter = self._build_date_range_filter(
            self.params.get("company_received_min"),
            self.params.get("company_received_max"), "date_sent_to_company")

        if company_filter:
            field_aggs["filter"]["bool"]["filter"].append(company_filter)

        # Add filter clauses to aggregation entries (only those that are not
        # the same as field name or part of the exclude list, which means we
        # want to list all matched aggregation)
        for item in self.params:
            include_filter = (
                item != field_name or
                (item == field_name and item in self.exclude)
            )

            if include_filter and item in (
                self._OPTIONAL_FILTERS + self._OPTIONAL_FILTERS_STRING_TO_BOOL
            ):
                field_level_should = {
                    "bool": {"should": self.filter_clauses[item]}
                }
                field_aggs["filter"]["bool"]["filter"].append(
                    field_level_should
                )

        return field_aggs

    def build(self):
        aggs = {}

        agg_fields = self._AGG_FIELDS
        if self.exclude:
            agg_fields = [field_name for field_name in self._AGG_FIELDS
                          if field_name not in self.exclude
                          or field_name in self.params]
        for field_name in agg_fields:
            aggs[field_name] = self.build_one(field_name)

        return aggs


class StateAggregationBuilder(BaseBuilder):
    _AGG_FIELDS = (
        'issue',
        'product',
        'state',
    )

    _AGG_SIZES = {
        'state': 0,
        'product': 5,
        'issue': 5
    }

    def __init__(self):
        BaseBuilder.__init__(self)
        self.filter_clauses = None
        self.exclude = []

    def add_exclude(self, field_name_list):
        self.exclude += field_name_list

    def build_one(self, field_name):
        # Lazy initialization
        if not self.filter_clauses:
            self.filter_clauses = self._build_filter_clauses()

        field_aggs = {
            "filter": {
                "bool": {
                    "must": [],
                    "should": [],
                    "filter": [],
                }
            }
        }

        es_field_name = self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(
            field_name, field_name
        )
        field_aggs["aggs"] = {
            field_name: {
                "terms": {
                    "field": es_field_name,
                    "size": self._AGG_SIZES[field_name]
                }
            }
        }

        # Get top product & issue for each state
        if field_name == 'state':
            field_aggs["aggs"]["state"]["aggs"] = {
                "product": {
                    "terms": {
                        "field": "product.raw",
                        "size": 1
                    }
                },
                "issue": {
                    "terms": {
                        "field": "issue.raw",
                        "size": 1
                    }
                }
            }

        date_filter = self._build_date_range_filter(
            self.params.get("date_received_min"),
            self.params.get("date_received_max"), "date_received")

        if date_filter:
            field_aggs["filter"]["bool"]["filter"].append(date_filter)

        company_filter = self._build_date_range_filter(
            self.params.get("company_received_min"),
            self.params.get("company_received_max"), "date_sent_to_company")

        if company_filter:
            field_aggs["filter"]["bool"]["filter"].append(company_filter)

        for item in self.params:
            if item in (
                self._OPTIONAL_FILTERS + self._OPTIONAL_FILTERS_STRING_TO_BOOL
            ) and item not in self.exclude:
                field_level_should = {
                    "bool": {"should": self.filter_clauses[item]}
                }
                field_aggs["filter"]["bool"]["filter"].append(
                    field_level_should
                )

        return field_aggs

    def build(self):
        aggs = {}

        agg_fields = self._AGG_FIELDS
        if self.exclude:
            agg_fields = [field_name for field_name in self._AGG_FIELDS
                          if field_name not in self.exclude]
        for field_name in agg_fields:
            aggs[field_name] = self.build_one(field_name)

        return aggs


class LensAggregationBuilder(BaseBuilder):
    _ES_CHILD_AGG_MAP = {
        'product.raw': 'sub-product',
        'sub_product.raw': 'product',
        'issue.raw': 'sub-issue',
        'sub_issue.raw': 'issue',
        'tags': 'tags'
    }

    def __init__(self):
        super(LensAggregationBuilder, self).__init__()
        self.filter_clauses = None
        self.exclude = []

    def add_exclude(self, field_name_list):
        self.exclude += field_name_list

    def build_histogram(self, agg_name, interval, include_date_filter):
        agg = {
            "aggs": {
                agg_name: {
                    "date_histogram": {
                        "field": "date_received",
                        "interval": interval
                    }
                }
            }
        }

        # Lazy initialization
        if not self.filter_clauses:
            self.filter_clauses = self._build_filter_clauses()

        filters = {
            "filter": {
                "bool": {
                    "must": [],
                    "should": [],
                    "filter": [],
                }
            }
        }

        date_filter = self._build_date_range_filter(
            self.params.get("date_received_min"),
            self.params.get("date_received_max"), "date_received")

        if date_filter and include_date_filter:
            filters["filter"]["bool"]["filter"].append(date_filter)

        company_filter = self._build_date_range_filter(
            self.params.get("company_received_min"),
            self.params.get("company_received_max"), "date_sent_to_company")

        if company_filter:
            filters["filter"]["bool"]["filter"].append(company_filter)

        for item in self.params:
            if item in (
                self._OPTIONAL_FILTERS + self._OPTIONAL_FILTERS_STRING_TO_BOOL
            ):
                field_level_should = {
                    "bool": {"should": self.filter_clauses[item]}
                }
                filters["filter"]["bool"]["filter"].append(
                    field_level_should
                )

        agg['filter'] = filters['filter']

        return agg

    def date_extreme(self, extreme):
        return {
            extreme: {
                "field": "date_received",
                "format": "yyyy-MM-dd'T'12:00:00-05:00"
            }
        }


class TrendsAggregationBuilder(LensAggregationBuilder):
    _AGG_FIELDS = (
        'company',
        'issue',
        'tags',
        'product'
    )

    _AGG_HEADING_MAP = {
        'company': 'company',
        'issue': 'issue',
        'product': 'product',
        'sub_product': 'sub-product',
        'sub_issue': 'sub-issue',
        'tags': 'tags',
    }

    def __init__(self):
        super(TrendsAggregationBuilder, self).__init__()

    def percent_change_agg(self, es_field_name, interval, trend_depth):
        return {
            "terms": {
                "field": es_field_name,
                "size": trend_depth
            },
            "aggs": {
                "trend_period": {
                    "date_histogram": {
                        "field": "date_received",
                        "interval": interval
                    },
                    "aggs": {
                        "interval_diff": {
                            "serial_diff": {"buckets_path": "_count"}
                        }
                    }
                }
            }
        }

    def get_agg_heading(self, field_name):
        return self._AGG_HEADING_MAP.get(field_name, field_name)

    def agg_setup(self, field_name, agg_heading_name, interval):
        field_aggs = {
            "aggs": {}
        }

        es_field_name = self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(
            field_name, field_name
        )

        field_aggs["aggs"][agg_heading_name] = self.percent_change_agg(
            es_field_name, interval, self.params['trend_depth'])

        # Lazy initialization
        if not self.filter_clauses:
            self.filter_clauses = self._build_filter_clauses()

        filters = {
            "filter": {
                "bool": {
                    "must": [],
                    "should": [],
                    "filter": [],
                }
            }
        }

        date_filter = self._build_date_range_filter(
            self.params.get("date_received_min"),
            self.params.get("date_received_max"), "date_received")

        if date_filter:
            filters["filter"]["bool"]["filter"].append(date_filter)

        company_filter = self._build_date_range_filter(
            self.params.get("company_received_min"),
            self.params.get("company_received_max"), "date_sent_to_company")

        if company_filter:
            filters["filter"]["bool"]["filter"].append(company_filter)

        for item in self.params:
            if item in (
                self._OPTIONAL_FILTERS + self._OPTIONAL_FILTERS_STRING_TO_BOOL
            ):
                field_level_should = {
                    "bool": {"should": self.filter_clauses[item]}
                }
                filters["filter"]["bool"]["filter"].append(
                    field_level_should
                )

        field_aggs['filter'] = filters['filter']

        return field_aggs

    def build_one_overview(self, field_name, agg_heading_name, interval):
        field_aggs = self.agg_setup(field_name, agg_heading_name, interval)

        if field_name in self._OPTIONAL_FILTERS_CHILD_MAP:
            es_child_name = self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(
                self._OPTIONAL_FILTERS_CHILD_MAP.get(field_name))
            child_agg_name = self._ES_CHILD_AGG_MAP.get(es_child_name)
            field_aggs["aggs"][agg_heading_name]["aggs"][child_agg_name] = \
                self.percent_change_agg(es_child_name, interval, 0)

        return field_aggs

    def build_one_lens(self, field_name, agg_heading_name, interval, sub_lens):
        field_aggs = self.agg_setup(field_name, agg_heading_name, interval)

        es_child_name = self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(
            sub_lens)
        child_agg_name = self._ES_CHILD_AGG_MAP.get(es_child_name)
        field_aggs["aggs"][agg_heading_name]["aggs"][child_agg_name] = \
            self.percent_change_agg(es_child_name, interval,
                                    self.params['sub_lens_depth'])

        return field_aggs

    def focus_filter(self):
        return {
            'term': {
                self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(
                    self.params['lens']): self.params['focus']
            }
        }

    def build_one_focus(self, field_name, agg_heading_name, interval):
        field_aggs = self.agg_setup(field_name, agg_heading_name, interval)

        field_aggs['filter']['bool']['must'].append(self.focus_filter())

        return field_aggs

    def build(self):
        # AZ - Only include a company aggregation if at least one company
        # filter is selected
        if 'company' in self.params and 'company' in self.exclude:
            self.exclude.remove('company')

        aggs = {}

        aggs['dateRangeArea'] = self.build_histogram(
            'dateRangeArea', self.params['trend_interval'], True)
        aggs['dateRangeBrush'] = self.build_histogram(
            'dateRangeBrush', self.params['trend_interval'], False)

        if self.params['lens'] == 'overview':
            # Reset default for overview row charts
            self.params['trend_depth'] = 5

            for field_name in self._AGG_FIELDS:
                if field_name not in self.exclude:
                    agg_heading_name = self.get_agg_heading(field_name)

                    aggs[agg_heading_name] = self.build_one_overview(
                        field_name,
                        agg_heading_name,
                        self.params['trend_interval']
                    )
        elif 'focus' in self.params:
            for field_name in DATA_SUB_LENS_MAP.get(self.params['lens']) \
                    + (self.params['lens'], ):
                agg_heading_name = self.get_agg_heading(field_name)

                aggs[agg_heading_name] = self.build_one_focus(
                    field_name,
                    agg_heading_name,
                    self.params['trend_interval']
                )

            aggs['dateRangeArea']['filter']['bool']['must']\
                .append(self.focus_filter())
            aggs['dateRangeBrush']['filter']['bool']['must']\
                .append(self.focus_filter())

        else:
            agg_heading_name = self.get_agg_heading(self.params['lens'])

            aggs[agg_heading_name] = self.build_one_lens(
                self.params['lens'],
                agg_heading_name,
                self.params['trend_interval'],
                self.params['sub_lens']
            )

        aggs['min_date'] = self.date_extreme('min')
        aggs['max_date'] = self.date_extreme('max')
        return aggs


if __name__ == "__main__":
    searchbuilder = SearchBuilder()
    print(searchbuilder.build())
    pfbuilder = PostFilterBuilder()
    print(pfbuilder.build())
    aggbuilder = AggregationBuilder()
    print(aggbuilder.build())
    stateaggbuilder = StateAggregationBuilder()
    print(stateaggbuilder.build())
    trendsaggbuilder = TrendsAggregationBuilder()
    print(trendsaggbuilder.build())
