__author__ = 'Willem Lenaerts'

from django.conf.urls import patterns, url
from app_voetbalelo.jpl_geschiedenis import views

urlpatterns = patterns('',
        url(r'^$', views.index),
        )