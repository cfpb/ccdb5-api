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
    SORT_RELEVANCE_DESC = '-relevance'
    SORT_RELEVANCE_ASC = '+relevance'
    SORT_CREATED_DATE_DESC = '-created_date'
    SORT_CREATED_DATE_ASC = '+created_date'

    SORT_CHOICES = (
        (SORT_RELEVANCE_DESC, 'Descending Relevance'),
        (SORT_RELEVANCE_ASC, 'Ascending Relevance'),
        (SORT_CREATED_DATE_DESC, 'Descending Created Date'),
        (SORT_CREATED_DATE_ASC, 'Ascending Created Date'),
    )
    format = serializers.ChoiceField(FORMAT_CHOICES, required=False)
    field = serializers.ChoiceField(FIELD_CHOICE, required=False)
    size = serializers.IntegerField(min_value=1, max_value=100000, required=False)
    from_index = serializers.IntegerField(min_value=0, max_value=100000, required=False)
    sort = serializers.ChoiceField(SORT_CHOICES, required=False)
    search_term = serializers.CharField(max_length=200, required=False)
    min_date = serializers.DateField(required=False)
    max_date = serializers.DateField(required=False)
    company = serializers.CharField(max_length=200, required=False)
    product = serializers.CharField(max_length=200, required=False)
    issue = serializers.CharField(max_length=200, required=False)
    state = serializers.ChoiceField(STATE_CHOICES, required=False)
    # Right now the following two fields are CharField, but if there's a set 
    # of choices only for each, they will be converted to ChoicesField
    consumer_disputed = serializers.CharField(max_length=200, required=False)
    company_response = serializers.CharField(max_length=200, required=False)