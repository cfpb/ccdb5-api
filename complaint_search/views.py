from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import datetime
import es_interface
from complaint_search.search_input_serializer import SearchInputSerializer

@api_view(['GET'])
def search(request):
    fixed_qparam = request.QUERY_PARAMS
    serializer = SearchInputSerializer(data=fixed_qparam)
    print fixed_qparam
    # print serializer.validated_data
    if serializer.is_valid():
        print serializer.validated_data
        results = es_interface.search()
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
