import complaint_search.views


try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path


urlpatterns = [
    re_path(
        r'^_suggest_company',
        complaint_search.views.suggest_company,
        name="suggest_company"
    ),
    re_path(
        r'^_suggest_zip',
        complaint_search.views.suggest_zip,
        name="suggest_zip"
    ),
    re_path(r'^_suggest', complaint_search.views.suggest, name="suggest"),
    re_path(
        r'^(?P<id>[0-9]+)$', complaint_search.views.document, name="complaint"
    ),
    re_path(r'^$', complaint_search.views.search, name="search"),
]
