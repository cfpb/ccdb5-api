from django.http import JsonResponse
import datetime
import es_interface


def search(request):
    results = es_interface.search()
    return JsonResponse(results)


def suggest(request):
    results = es_interface.suggest()
    return JsonResponse(results)


def document(request, id):
    results = es_interface.document(id)
    return JsonResponse(results)
