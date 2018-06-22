from rest_framework import status
from rest_framework.response import Response
from elasticsearch import TransportError


def catch_es_error(function):
    def wrap(request, *args, **kwargs):
        try:
            return function(request, *args, **kwargs)
        except TransportError as e:
            status_code = 424  # HTTP_424_FAILED_DEPENDENCY
            res = {
                "error": 'There was an error calling Elasticsearch'
            }
            return Response(res, status=status_code)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
