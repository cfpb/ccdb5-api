from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import datetime
import es_interface
from complaint_search.search_input_serializer import SearchInputSerializer

@api_view(['GET'])
def search(request):
    print format
    fixed_qparam = request.query_params
    print fixed_qparam
    QPARAMS_VARS = ('fmt', 'field', 'size', 'frm', 'sort', 
        'search_term', 'min_date', 'max_date')

    QPARAMS_LISTS = ('company', 'product', 'issue', 'state', 
        'consumer_disputed', 'company_response')
    # Only those that are different
    QPARAM_SERIALIZER_MAP = {
        'from': 'frm'
    }
    print request.query_params

    print request.query_params.items()
    print request.query_params.iteritems()

    # data = { QPARAM_SERIALIZER_MAP.get(param, param): request.query_params.get(param) 
    #     if param in QPARAMS_VARS else request.query_params.getlist(param)
    #     for param in request.query_params if param in QPARAMS_VARS + QPARAMS_LISTS}

    data = {}
    for param in request.query_params:
        if param in QPARAMS_VARS:
            data[QPARAM_SERIALIZER_MAP.get(param, param)] = request.query_params.get(param) 
        elif param in QPARAMS_LISTS:
            data[QPARAM_SERIALIZER_MAP.get(param, param)] = request.query_params.getlist(param)
          # TODO: else: Error if extra parameters? Or ignore?

    serializer = SearchInputSerializer(data=data)

    print "data", data
    if serializer.is_valid():
        print "validated data", serializer.validated_data
        results = es_interface.search(**serializer.validated_data)
        return Response(results)
    else:
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def suggest(request):
    results = es_interface.suggest()
    return Response(results)

@api_view(['GET'])
def document(request, id):
    results = es_interface.document(id)
    return Response(results)
