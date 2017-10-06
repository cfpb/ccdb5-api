from django.conf.urls import include, url
import complaint_search.views

urlpatterns = [
    url(
        r'^_suggest_zip',
        complaint_search.views.suggest_zip,
        name="suggest_zip"
    ),
    url(r'^_suggest', complaint_search.views.suggest, name="suggest"),
    url(r'^(?P<id>[0-9]+)$', complaint_search.views.document, name="document"),
    url(r'^$', complaint_search.views.search, name="search"),
]
