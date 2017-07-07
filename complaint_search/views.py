from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings
from datetime import datetime
from elasticsearch import TransportError
import es_interface
from complaint_search.decorators import catch_es_error
from complaint_search.serializer import SearchInputSerializer, SuggestInputSerializer


@api_view(['GET'])
@catch_es_error
def search(request):
    fixed_qparam = request.query_params
    QPARAMS_VARS = ('fmt', 'field', 'size', 'frm', 'sort', 
        'search_term', 'min_date', 'max_date')

    QPARAMS_LISTS = ('company', 'product', 'issue', 'state', 
        'zip_code', 'timely', 'consumer_disputed', 'company_response',
        'company_public_response', 'consumer_consent_provided', 
        'has_narratives', 'submitted_via', 'tag')

    # This works too but it may be harder to read
    # data = { param: request.query_params.get(param) 
    #     if param in QPARAMS_VARS else request.query_params.getlist(param)
    #     for param in request.query_params if param in QPARAMS_VARS + QPARAMS_LISTS}

    data = {}
    for param in request.query_params:
        if param in QPARAMS_VARS:
            data[param] = request.query_params.get(param) 
        elif param in QPARAMS_LISTS:
            data[param] = request.query_params.getlist(param)
          # TODO: else: Error if extra parameters? Or ignore?

    serializer = SearchInputSerializer(data=data)

    if serializer.is_valid():
        results = es_interface.search(**serializer.validated_data)

        FMT_CONTENT_TYPE_MAP = {
            "json": "application/json",
            "csv": "text/csv",
            "xls": "application/vnd.ms-excel",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }

        # Local development requires CORS support
        headers = {}
        if settings.DEBUG:
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET'
            }

        # Putting response together based on format
        fmt = serializer.validated_data.get("fmt", 'json')
        if fmt == 'json':
            return Response(results, headers=headers)
        elif fmt in ('csv', 'xls', 'xlsx'):
            media_type = FMT_CONTENT_TYPE_MAP.get(fmt)
            response = HttpResponse(results, content_type=media_type)
            for header in headers:
                response[header] = headers[header]

            filename = 'complaints-{}.{}'.format(datetime.now().strftime('%Y-%m-%d_%H_%M'), fmt)
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

            return response
    else:
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@catch_es_error
def suggest(request):
    QPARAMS_VARS = ("text", "size")
    data = { k:v for k,v in request.query_params.iteritems() if k in QPARAMS_VARS }
    serializer = SuggestInputSerializer(data=data)
    if serializer.is_valid():
        results = es_interface.suggest(**serializer.validated_data)
        return Response(results)
    else:
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@catch_es_error
def document(request, id):
    results = es_interface.document(id)
    return Response(results)
