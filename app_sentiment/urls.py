from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^bdw/', include('app_sentiment.bdw.urls')),
)