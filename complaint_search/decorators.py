from rest_framework import status
from rest_framework.response import Response
from elasticsearch import TransportError

def catch_es_error(function):
    def wrap(request, *args, **kwargs):
        try:
            return function(request, *args, **kwargs)
        except TransportError as e:
            status_code = e.status_code if isinstance(e.status_code, int) \
                else status.HTTP_400_BAD_REQUEST
            res = {
                "error": 'Elasticsearch error: ' + e.error
            }
            return Response(res, status=status_code)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap