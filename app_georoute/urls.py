__author__ = 'Willem Lenaerts'

from django.conf.urls import patterns, url
from route import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        )