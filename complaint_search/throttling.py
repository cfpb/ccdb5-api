import os

from django.conf import settings

from rest_framework.throttling import AnonRateThrottle

from complaint_search.defaults import EXPORT_FORMATS


_CCDB_UI_URL = os.environ.get(
    "CCDB_UI_URL",
    "http://localhost:8000/data-research/consumer-complaints/search",
)


class CCDBRateThrottle(AnonRateThrottle):
    scope = "ccdb"

    def is_referred_from_ui(self, request, view):
        return (
            request.META.get("HTTP_REFERER")
            and request.META.get("HTTP_REFERER").find(_CCDB_UI_URL) != -1
        )

    def is_export(self, request):  # otherwise it is a search
        return (
            request.query_params.get("format")
            and request.query_params.get("format") in EXPORT_FORMATS
        )


class CCDBAnonRateThrottle(CCDBRateThrottle):
    scope = "ccdb_anon"

    def allow_request(self, request, view):
        if settings.DEBUG is True:
            return True
        if not self.is_referred_from_ui(request, view):
            return super(CCDBAnonRateThrottle, self).allow_request(
                request, view
            )
        else:
            return True


class CCDBUIRateThrottle(CCDBRateThrottle):
    scope = "ccdb_ui"

    def allow_request(self, request, view):
        if self.is_referred_from_ui(request, view):
            return super(CCDBUIRateThrottle, self).allow_request(request, view)
        else:
            return True


# class SearchUIRateThrottle(CCDBUIRateThrottle):
#     scope = 'ccdb_ui_search'
#     # rate needs to be set if use

#     def allow_request(self, request, view):
#         if not self.is_export(request):
#             return super(SearchUIRateThrottle, self).allow_request(
#                     request, view)
#         else:
#             return True


class SearchAnonRateThrottle(CCDBAnonRateThrottle):
    scope = "ccdb_anon_search"
    rate = "20/min"

    def allow_request(self, request, view):
        if not self.is_export(request):
            return super(SearchAnonRateThrottle, self).allow_request(
                request, view
            )
        else:
            return True


class ExportUIRateThrottle(CCDBUIRateThrottle):
    scope = "ccdb_ui_export"
    rate = "6/min"

    def allow_request(self, request, view):
        if self.is_export(request):
            return super(ExportUIRateThrottle, self).allow_request(
                request, view
            )
        else:
            return True


class ExportAnonRateThrottle(CCDBAnonRateThrottle):
    scope = "ccdb_anon_export"
    rate = "2/min"

    def allow_request(self, request, view):
        if self.is_export(request):
            return super(ExportAnonRateThrottle, self).allow_request(
                request, view
            )
        else:
            return True


# class DocumentUIRateThrottle(CCDBUIRateThrottle):
#     scope = 'ccdb_ui_document'
#     # rate needs to be set if use


class DocumentAnonRateThrottle(CCDBAnonRateThrottle):
    scope = "ccdb_anon_document"
    rate = "5/min"
