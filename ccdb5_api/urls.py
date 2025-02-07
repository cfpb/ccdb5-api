from django.contrib import admin
from django.urls import include, re_path


urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"data-research/consumer-complaints/search/api/v1/", include("complaint_search.urls")),
]
