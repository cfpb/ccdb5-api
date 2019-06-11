from __future__ import unicode_literals

import abc
import copy
import re
from collections import OrderedDict

from complaint_search.defaults import (
    DELIMITER,
    EXPORT_FORMATS,
    PARAMS,
    SOURCE_FIELDS,
)


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
        "timely",
        "zip_code",
    )

    _OPTIONAL_FILTERS_MUST = ("tags",)

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

    ## This create all the bool should filter clauses for a field
    ## es_field_name: a field name (to be filtered in ES)
    ## value_list: a list of values to be filtered for this field
    ## with_child: set to true if this field has a child field
    ## es_child_field_name: if with_child is true, this holds the field
    ## name of the child used (to be filtered in ES)
    def _build_bool_clauses(self, field):
        es_field_name = self._get_es_name(field)
        value_list = [0 if cd.lower() == "no" else 1 for cd in self.params[field]] \
            if field in self._OPTIONAL_FILTERS_STRING_TO_BOOL else self.params.get(field)

        if value_list:

            # MUST filters must be in parallel otherwise they will not execute as intended
            if field in self._OPTIONAL_FILTERS_MUST:
                term_list_container = []
                term_list = [{"terms": {es_field_name: [value]}} for value in value_list]

                return term_list

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
                        child_term = {"terms": {self._get_es_name(self._get_child(field)): child}}
                        parent_child_bool_structure = {"bool": {"must": [], "should": []}}
                        parent_child_bool_structure["bool"]["must"].append(parent_term)
                        parent_child_bool_structure["bool"]["should"].append(child_term)

                        f_list.append(parent_child_bool_structure)

                return f_list

    # This creates a dictionary of all filter_clauses, where the keys are the field name
    def _build_filter_clauses(self):
        filter_clauses = {}
        for item in self.params:
            if item in self._OPTIONAL_FILTERS + self._OPTIONAL_FILTERS_STRING_TO_BOOL + self._OPTIONAL_FILTERS_MUST:
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
                d =  str(date_max) + timeSuffix
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
            highlight["fields"] = { source: {} for source in SOURCE_FIELDS }
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
        if not self.params.get("no_highlight"):
            search["highlight"] = self._build_highlight()

        # sort
        search["sort"] = self._build_sort()

        # query
        search_term = self.params.get("search_term")
        if search_term:
            if re.match("^[A-Za-z\d\s]+$", search_term) and \
            not any(keyword in search_term
                for keyword in ("AND", "OR", "NOT", "TO")):

                # Match Query
                search["query"] = {
                    "match": {
                        self.params.get("field"): {
                            "query": search_term,
                            "operator": "and"
                        }
                    }
                }

            else:

                # QueryString Query
                search["query"] = {
                    "query_string": {
                        "query": search_term,
                        "fields": [
                            self.params.get("field")
                        ],
                        "default_operator": "AND"
                    }
                }

        return search


class PostFilterBuilder(BaseBuilder):

    def build(self):
        filter_clauses = self._build_filter_clauses()

        post_filter = {"bool": {"should": [], "must": [], "filter": []}}

        ## date_received
        date_received = self._build_date_range_filter(
            self.params.get("date_received_min"),
            self.params.get("date_received_max"),
            "date_received")

        if date_received:
            post_filter["bool"]["filter"].append(date_received)

        ## company_received
        company_received = self._build_date_range_filter(
            self.params.get("company_received_min"),
            self.params.get("company_received_max"),
            "date_sent_to_company")

        if company_received:
            post_filter["bool"]["filter"].append(company_received)

        ## Create filter clauses for all other filters
        for item in self.params:
            if item in self._OPTIONAL_FILTERS + self._OPTIONAL_FILTERS_STRING_TO_BOOL:
                # for filters selected, we are creating the field level OR query that must match
                # e.g (this OR that) AND (y or z) AND servicemember
                field_level_should = {"bool": {"should":filter_clauses[item]}}
                post_filter["bool"]["filter"].append( field_level_should )
            if item in self._OPTIONAL_FILTERS_MUST:
                post_filter["bool"]["filter"].append(filter_clauses[item])

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
            include_filter = item != field_name or (item == field_name and item in self.exclude)

            if include_filter and item in self._OPTIONAL_FILTERS + self._OPTIONAL_FILTERS_STRING_TO_BOOL:
                field_level_should = {
                    "bool": {"should": self.filter_clauses[item]}
                }
                field_aggs["filter"]["bool"]["filter"].append(
                    field_level_should
                )

            if include_filter and item in self._OPTIONAL_FILTERS_MUST:
                field_aggs["filter"]["bool"]["filter"].append(
                    self.filter_clauses[item]
                )

        return field_aggs

    def build(self):
        aggs = {}

        agg_fields = self._AGG_FIELDS
        if self.exclude:
            agg_fields = [ field_name for field_name in self._AGG_FIELDS
                if field_name not in self.exclude or field_name in self.params ]
        for field_name in agg_fields:
            aggs[field_name] = self.build_one(field_name)

        return aggs


if __name__ == "__main__":
    searchbuilder = SearchBuilder()
    print(searchbuilder.build())
    pfbuilder = PostFilterBuilder()
    print(pfbuilder.build())
    aggbuilder = AggregationBuilder()
    print(aggbuilder.build())
