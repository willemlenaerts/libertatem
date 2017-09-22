__author__ = 'Willem Lenaerts'

from django.conf.urls import patterns, url
from app_voetbalelo.jpl_playoffs import views

urlpatterns = patterns('',
        url(r'^$', views.ranking),
        )