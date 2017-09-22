from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^playoffs/', include('app_voetbalelo.jpl_playoffs.urls')), 
    url(r'^regulier/', include('app_voetbalelo.jpl_regulier.urls')),
    url(r'^geschiedenis/', include('app_voetbalelo.jpl_geschiedenis.urls')),
    url(r'^wereld/', include('app_voetbalelo.wereld_geschiedenis.urls')),
)