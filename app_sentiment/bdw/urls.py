__author__ = 'Willem Lenaerts'

from django.conf.urls import patterns, url
from app_sentiment.bdw import views

urlpatterns = patterns('',
        url(r'^$', views.index),
        )