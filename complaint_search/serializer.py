from rest_framework import serializers
from localflavor.us.us_states import STATE_CHOICES

class SearchInputSerializer(serializers.Serializer):

    ### Format Choices
    FORMAT_JSON = 'json'
    FORMAT_CSV = 'csv'
    FORMAT_XLS = 'xls'
    FORMAT_XLSX = 'xlsx'

    FORMAT_CHOICES = (
        (FORMAT_JSON, 'JSON'),
        (FORMAT_CSV, 'CSV'),
        (FORMAT_XLS, 'XLS'),
        (FORMAT_XLSX, 'XLSX'), )

    ### Field Choices
    FIELD_NARRATIVE = 'complaint_what_happened'
    FIELD_RESPONSE = 'company_public_response'
    FIELD_ALL = 'all'

    FIELD_CHOICE = (
        (FIELD_NARRATIVE, 'complaint_what_happened field'),
        (FIELD_RESPONSE, 'company_public_response field'),
        (FIELD_ALL, 'all fields'),
    )
    ### Sort Choices
    SORT_RELEVANCE_DESC = 'relevance_desc'
    SORT_RELEVANCE_ASC = 'relevance_asc'
    SORT_CREATED_DATE_DESC = 'created_date_desc'
    SORT_CREATED_DATE_ASC = 'created_date_asc'

    SORT_CHOICES = (
        (SORT_RELEVANCE_DESC, 'Descending Relevance'),
        (SORT_RELEVANCE_ASC, 'Ascending Relevance'),
        (SORT_CREATED_DATE_DESC, 'Descending Created Date'),
        (SORT_CREATED_DATE_ASC, 'Ascending Created Date'),
    )
    fmt = serializers.ChoiceField(FORMAT_CHOICES, required=False)
    field = serializers.ChoiceField(FIELD_CHOICE, required=False)
    size = serializers.IntegerField(min_value=1, max_value=100000, required=False)
    frm = serializers.IntegerField(min_value=0, max_value=100000, required=False)
    sort = serializers.ChoiceField(SORT_CHOICES, required=False)
    search_term = serializers.CharField(max_length=200, required=False)
    min_date = serializers.DateField(required=False)
    max_date = serializers.DateField(required=False)
    company = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False)
    product = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False)
    issue = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False)
    state = serializers.ListField(
        child=serializers.ChoiceField(STATE_CHOICES), required=False)
    # Right now the following two fields are CharField, but if there's a set 
    # of choices only for each, they will be converted to ChoicesField
    consumer_disputed = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False)
    company_response = serializers.ListField(
        child=serializers.CharField(max_length=200), required=False)

    def validate_product(self, value):
        """
        Valid Product format where if subproduct is presented, it should
        be prefixed with the parent product and a bullet point u2022
        """
        if value:
            for p in value:
                # -*- coding: utf-8 -*-
                if p.count(u'\u2022') > 1:
                    raise serializers.ValidationError(u"Product is malformed, it needs to be \"product\" or \"product\u2022subproduct\"")

        return value

    def validate_issue(self, value):
        """
        Valid Issue format where if subissue is presented, it should
        be prefixed with the parent product and a bullet point \u2022
        """
        if value:
            for p in value:
                # -*- coding: utf-8 -*-
                if p.count(u'\u2022') > 1:
                    raise serializers.ValidationError(u"Issue is malformed, it needs to be \"issue\" or \"issue\u2022subissue\"")

        return value
class SuggestInputSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=200, required=False)
    size = serializers.IntegerField(min_value=1, max_value=100000, required=False)
    