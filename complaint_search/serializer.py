from localflavor.us.us_states import STATE_CHOICES
from rest_framework import serializers

from complaint_search.defaults import PARAMS


class SearchInputSerializer(serializers.Serializer):

    # Format Choices
    FORMAT_DEFAULT = "default"
    FORMAT_CSV = "csv"

    FORMAT_CHOICES = (
        (FORMAT_DEFAULT, "DEFAULT"),
        (FORMAT_CSV, "CSV"),
    )

    # Field Choices
    FIELD_NARRATIVE = "complaint_what_happened"
    FIELD_COMPANY = "company"
    FIELD_ALL = "all"
    FIELD_ALL_ES = "_all"

    FIELD_CHOICES = (
        (FIELD_NARRATIVE, "complaint_what_happened field"),
        (FIELD_COMPANY, "company field"),
        (FIELD_ALL, "all fields"),
        (FIELD_ALL_ES, "all fields"),
    )

    FIELD_MAP = {FIELD_ALL: "all"}

    # Sort Choices
    SORT_RELEVANCE_DESC = "relevance_desc"
    SORT_RELEVANCE_ASC = "relevance_asc"
    SORT_CREATED_DATE_DESC = "created_date_desc"
    SORT_CREATED_DATE_ASC = "created_date_asc"

    SORT_CHOICES = (
        (SORT_RELEVANCE_DESC, "Descending Relevance"),
        (SORT_RELEVANCE_ASC, "Ascending Relevance"),
        (SORT_CREATED_DATE_DESC, "Descending Created Date"),
        (SORT_CREATED_DATE_ASC, "Ascending Created Date"),
    )

    format = serializers.ChoiceField(FORMAT_CHOICES, default=PARAMS["format"])
    field = serializers.ChoiceField(FIELD_CHOICES, default=PARAMS["field"])
    size = serializers.IntegerField(
        min_value=0, max_value=100000, default=PARAMS["size"]
    )
    frm = serializers.IntegerField(
        min_value=0, max_value=10000, default=PARAMS["frm"]
    )
    sort = serializers.ChoiceField(SORT_CHOICES, default=PARAMS["sort"])
    search_term = serializers.CharField(max_length=200, required=False)
    date_received_min = serializers.DateField(required=False)
    date_received_max = serializers.DateField(required=False)
    page = serializers.IntegerField(
        min_value=1, max_value=10000, default=PARAMS["page"]
    )
    company_received_min = serializers.DateField(required=False)
    company_received_max = serializers.DateField(required=False)
    company = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    product = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    issue = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    state = serializers.ListField(
        child=serializers.ChoiceField(STATE_CHOICES), required=False
    )
    zip_code = serializers.ListField(
        child=serializers.CharField(min_length=5, max_length=5), required=False
    )
    search_after = serializers.CharField(max_length=200, required=False)
    timely = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    company_response = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    company_public_response = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    has_narrative = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    submitted_via = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    no_aggs = serializers.BooleanField(default=PARAMS["no_aggs"])
    no_highlight = serializers.BooleanField(default=PARAMS["no_highlight"])

    # oh these had to be Python variables
    # couldn't just get away with a '-' prefix >:(
    not_company = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    not_company_public_response = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    not_company_response = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    not_issue = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    not_product = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    not_state = serializers.ListField(
        child=serializers.ChoiceField(STATE_CHOICES), required=False
    )
    not_tags = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False
    )
    not_zip = serializers.ListField(
        child=serializers.CharField(min_length=5, max_length=5), required=False
    )

    def to_internal_value(self, data):
        ret = super(SearchInputSerializer, self).to_internal_value(data)
        if ret.get("field"):
            ret["field"] = SearchInputSerializer.FIELD_MAP.get(
                ret["field"], ret["field"]
            )
        return ret

    def validate_product(self, value):
        """
        Valid Product format where if subproduct is presented, it should
        be prefixed with the parent product and a bullet point u2022
        """
        if value:
            for p in value:
                # -*- coding: utf-8 -*-
                if p.count("\u2022") > 1:
                    raise serializers.ValidationError(
                        'Product is malformed, it needs to be "product" or '
                        '"product\u2022subproduct"'
                    )

        return value

    def validate_issue(self, value):
        r"""
        Valid Issue format where if subissue is presented, it should
        be prefixed with the parent product and a bullet point \u2022
        """
        if value:
            for p in value:
                # -*- coding: utf-8 -*-
                if p.count("\u2022") > 1:
                    raise serializers.ValidationError(
                        'Issue is malformed, it needs to be "issue" or '
                        '"issue\u2022subissue"'
                    )

        return value

    def validate(self, data):
        """
        Check that from is a multiple of size
        """
        if data["size"] != 0 and data["frm"] % data["size"] != 0:
            raise serializers.ValidationError(
                "frm is not zero or a multiple of size"
            )
        return data


class SuggestInputSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=200, required=False)
    size = serializers.IntegerField(
        min_value=1, max_value=100000, required=False
    )


class SuggestFilterInputSerializer(SearchInputSerializer):
    text = serializers.CharField(max_length=100, required=True)
