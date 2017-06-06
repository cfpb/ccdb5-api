from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import datetime
import es_interface

@api_view(['GET'])
def search(request):
    results = es_interface.search()
    return Response(results)

@api_view(['GET'])
def suggest(request):
    results = es_interface.suggest()
    return Response(results)

@api_view(['GET'])
def document(request, id):
    results = es_interface.document(id)
    return Response(results)
