"""ccdb5_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/stable/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import django
from django.contrib import admin


try:
    from django.urls import include, re_path
except ImportError:
    from django.conf.urls import include
    from django.conf.urls import url as re_path

if django.VERSION >= (2, 0):
    urlpatterns = [
        re_path(r'^admin/', admin.site.urls),
        re_path('complaint_search/', include('complaint_search.urls')),
    ]
else:
    urlpatterns = [
        re_path(r'^admin/', include(admin.site.urls)),
        re_path(r'^', include('complaint_search.urls',
                              namespace="complaint_search")),
    ]
