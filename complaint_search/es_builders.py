import re
import copy
import abc
from collections import defaultdict, namedtuple
from complaint_search.defaults import PARAMS

class BaseBuilder(object):
    __metaclass__  = abc.ABCMeta

    # Filters for those with string type
    _OPTIONAL_FILTERS = ("product", "issue", "company", "state", "zip_code", "timely", 
        "company_response", "company_public_response", 
        "consumer_consent_provided", "submitted_via", "tag", "consumer_disputed")

    # Filters for those that need conversion from string to boolean
    _OPTIONAL_FILTERS_STRING_TO_BOOL = ("has_narrative",)

    _OPTIONAL_FILTERS_PARAM_TO_ES_MAP = {
        "product": "product.raw",
        "sub_product": "sub_product.raw",
        "issue": "issue.raw",
        "sub_issue": "sub_issue.raw",
        "company": "company.raw",
        "company_public_response": "company_public_response.raw",
        "consumer_consent_provided": "consumer_consent_provided.raw",
        "consumer_disputed": "consumer_disputed.raw"
    }

    _OPTIONAL_FILTERS_CHILD_MAP = {
        "product": "sub_product", 
        "issue": "sub_issue"
    }

    def __init__(self):
        self.params = {}

    def add(self, **kwargs):
        self.params.update(**kwargs)

    @abc.abstractmethod
    def build(self):
         """Method that will build the body dictionary."""

    def _create_bool_should_clauses(self, es_field_name, value_list, 
        with_subitems=False, es_subitem_field_name=None):
        if value_list:
            if not with_subitems:
                term_list = [ {"terms": {es_field_name: [value]}} 
                    for value in value_list ]
                return {"bool": {"should": term_list}}
            else:
                item_dict = defaultdict(list)
                for v in value_list:
                    # -*- coding: utf-8 -*-
                    v_pair = v.split(u'\u2022')
                    # No subitem
                    if len(v_pair) == 1:
                        # This will initialize empty list for item if not in item_dict yet
                        item_dict[v_pair[0]]
                    elif len(v_pair) == 2:
                        # put subproduct into list
                        item_dict[v_pair[0]].append(v_pair[1])

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

                return {"bool": {"should": f_list}}

    def _create_and_append_bool_should_clauses(self, es_field_name, value_list, 
        filter_list, with_subitems=False, es_subitem_field_name=None):
        filter_clauses = self._create_bool_should_clauses(es_field_name, value_list, 
            with_subitems, es_subitem_field_name)

        if filter_clauses:
            filter_list.append(filter_clauses)


class SearchBuilder(BaseBuilder):
    def __init__(self):
        self.params = copy.deepcopy(PARAMS)

    def build(self):
        search = {
            "from": self.params.get("frm"), 
            "size": self.params.get("size"), 
            "query": {
                "query_string": {
                    "query": "*",
                    "fields": [
                        self.params.get("field")
                    ],
                    "default_operator": "AND"
                }
            },
            "highlight": {
                "require_field_match": False,
                "fields": {
                    "complaint_what_happened": {}
                },
                "number_of_fragments": 1,
                "fragment_size": 500
            }
        }

        # sort
        sort_field, sort_order = self.params.get("sort").rsplit("_", 1)
        sort_field = "_score" if sort_field == "relevance" else sort_field
        search["sort"] = [{sort_field: {"order": sort_order}}]

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
        post_filter = {"and": {"filters": []}}

        ## date
        if self.params.get("min_date") or self.params.get("max_date"):
            date_clause = {"range": {"date_received": {}}}
            if self.params.get("min_date"):
                date_clause["range"]["date_received"]["from"] = self.params.get("min_date")
            if self.params.get("max_date"):
                date_clause["range"]["date_received"]["to"] = self.params.get("max_date")

            post_filter["and"]["filters"].append(date_clause)

        ## Create bool should clauses for fields in self._OPTIONAL_FILTERS
        for field in self._OPTIONAL_FILTERS:
            if field in self._OPTIONAL_FILTERS_CHILD_MAP: 
                self._create_and_append_bool_should_clauses(self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(field, field), 
                    self.params.get(field), post_filter["and"]["filters"], with_subitems=True, 
                    es_subitem_field_name=self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(self._OPTIONAL_FILTERS_CHILD_MAP.get(field), 
                        self._OPTIONAL_FILTERS_CHILD_MAP.get(field)))
            else:
                self._create_and_append_bool_should_clauses(self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(field, field), 
                    self.params.get(field), post_filter["and"]["filters"])

        for field in self._OPTIONAL_FILTERS_STRING_TO_BOOL:
            if self.params.get(field):
                self._create_and_append_bool_should_clauses(field, 
                    [ 0 if cd.lower() == "no" else 1 for cd in self.params.get(field) ],
                    post_filter["and"]["filters"])

        return post_filter

class AggregationBuilder(BaseBuilder):
    
    def build(self):
    # All fields that need to have an aggregation entry
        Field = namedtuple('Field', 'name size has_subfield')
        fields = [
            Field('has_narrative', 0, False),
            Field('company', 0, False),
            Field('product', 0, True),
            Field('issue', 0, True),
            Field('state', 0, False),
            Field('zip_code', 0, False),
            Field('timely', 0, False),
            Field('company_response', 0, False),
            Field('company_public_response', 0, False),
            Field('consumer_disputed', 0, False),
            Field('consumer_consent_provided', 0, False),
            Field('tag', 0, False),
            Field('submitted_via', 0, False)
        ]

        aggs = {}

        # Creating aggregation object for each field above
        for field in fields:
            field_aggs = {
                "filter": {
                    "and": {
                        "filters": [

                        ]
                    }
                }        
            }

            es_field_name = self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(field.name, field.name)
            es_subfield_name = None
            if field.has_subfield:
                es_subfield_name = self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(self._OPTIONAL_FILTERS_CHILD_MAP.get(field.name))
                field_aggs["aggs"] = {
                    field.name: {
                        "terms": {
                            "field": es_field_name,
                            "size": field.size
                        },
                        "aggs": {
                            es_subfield_name: {
                                "terms": {
                                    "field": es_subfield_name,
                                    "size": field.size
                                }
                            }
                        }
                    }
                }
            else:
                field_aggs["aggs"] = {
                    field.name: {
                        "terms": {
                            "field": es_field_name,
                            "size": field.size
                        }
                    }
                }

            date_filter = {
                "range": {
                    "date_received": {

                    }
                }
            }
            if "min_date" in self.params:
                date_filter["range"]["date_received"]["from"] = self.params["min_date"]
            if "max_date" in self.params:
                date_filter["range"]["date_received"]["to"] = self.params["max_date"]
            
            field_aggs["filter"]["and"]["filters"].append(date_filter)
            
            # Add filter clauses to aggregation entries (only those that are not the same as field name)
            for item in self.params:
                if item in self._OPTIONAL_FILTERS and item != field.name:
                    clauses = self._create_and_append_bool_should_clauses(self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(item, item), 
                        self.params[item], field_aggs["filter"]["and"]["filters"], 
                        with_subitems=item in self._OPTIONAL_FILTERS_CHILD_MAP, 
                        es_subitem_field_name=self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(self._OPTIONAL_FILTERS_CHILD_MAP.get(item)))
                elif item in self._OPTIONAL_FILTERS_STRING_TO_BOOL and item != field.name:
                    clauses = self._create_and_append_bool_should_clauses(self._OPTIONAL_FILTERS_PARAM_TO_ES_MAP.get(item, item), 
                        [ 0 if cd.lower() == "no" else 1 for cd in self.params[item] ],
                        field_aggs["filter"]["and"]["filters"])

            aggs[field.name] = field_aggs

        return aggs        

if __name__ == "__main__":
    searchbuilder = SearchBuilder()
    print searchbuilder.build()
    pfbuilder = PostFilterBuilder()
    print pfbuilder.build()
    aggbuilder = AggregationBuilder()
    print aggbuilder.build()

