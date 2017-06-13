from django.conf.urls import include, url
import complaint_search.views

urlpatterns = [
    url(r'^_suggest', complaint_search.views.suggest),
    url(r'^(?P<id>[0-9]+)$', complaint_search.views.document),
    url(r'^$', complaint_search.views.search),
]