__author__ = 'Willem Lenaerts'

from django.conf.urls import patterns, url
from app_voetbalelo.wereld_geschiedenis import views

urlpatterns = patterns('',
        url(r'^$', views.index),
        )