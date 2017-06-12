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
    data = {}
    if request.query_params.get('fmt'):
        data["fmt"] = request.query_params.get("fmt")
    if request.query_params.get('field'):
        data["field"] = request.query_params.get("field")
    if request.query_params.get('size'):
        data["size"] = request.query_params.get("size")
    if request.query_params.get('from'):
        data["frm"] = request.query_params.get("from")
    if request.query_params.get('sort'):
        data["sort"] = request.query_params.get("sort")
    if request.query_params.get('search_term'):
        data["search_term"] = request.query_params.get("search_term")
    if request.query_params.get("min_date"):
        data["min_date"] = request.query_params.get("min_date")
    if request.query_params.get("max_date"):
        data["max_date"] = request.query_params.get("max_date")
    if request.query_params.getlist('company'):
        data['company'] = request.query_params.getlist('company')
    if request.query_params.getlist('product'):
        data['product'] = request.query_params.getlist('product')
    if request.query_params.getlist('issue'):
        data['issue'] = request.query_params.getlist('issue')
    if request.query_params.getlist('state'):
        data['state'] = request.query_params.getlist('state')
    if request.query_params.getlist('consumer_disputed'):
        data['consumer_disputed'] = request.query_params.getlist('consumer_disputed')
    if request.query_params.getlist('company_response'):
        data['company_response'] = request.query_params.getlist('company_response')
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
