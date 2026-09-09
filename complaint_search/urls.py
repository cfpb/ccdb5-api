from django.urls import path, re_path

import complaint_search.views


app_name = "complaint_search"

urlpatterns = [
    re_path(
        r"^_suggest_company/$",
        complaint_search.views.suggest_company,
        name="suggest_company",
    ),
    re_path(
        r"^_suggest_zip/$",
        complaint_search.views.suggest_zip,
        name="suggest_zip",
    ),
    re_path(
        r"^(?P<id>[0-9]+)$", complaint_search.views.document, name="complaint"
    ),
    re_path(r"^$", complaint_search.views.search, name="search"),
    path(
        "generate-download-link/",
        complaint_search.views.temp_download_link,
        name="temp_link"
    ),
    path(
        "download/<token>/",
        complaint_search.views.download_with_token,
        name="download"
    ),
]
