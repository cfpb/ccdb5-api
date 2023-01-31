from django.urls import re_path
from django.views.generic.base import RedirectView

import complaint_search.views


app_name = "complaint_search"

urlpatterns = [
    re_path(
        r"^_suggest_company",
        complaint_search.views.suggest_company,
        name="suggest_company",
    ),
    re_path(
        r"^_suggest_zip",
        complaint_search.views.suggest_zip,
        name="suggest_zip",
    ),
    re_path(r"^_suggest", complaint_search.views.suggest, name="suggest"),
    re_path(
        r"^(?P<id>[0-9]+)$", complaint_search.views.document, name="complaint"
    ),
    re_path(r"^$", complaint_search.views.search, name="search"),
    re_path(r"^geo/states", complaint_search.views.states, name="states"),
    re_path(r"^geo", RedirectView.as_view(url="/geo/states"), name="geo"),
    re_path(r"^trends", complaint_search.views.trends, name="trends"),
]
