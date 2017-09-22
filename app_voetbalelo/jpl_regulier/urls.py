from django.conf.urls import patterns, url
from app_voetbalelo.jpl_regulier import views

urlpatterns = patterns('',
        url(r'^ranking/$', views.team_table, name='ranking'),
        url(r'^games/$', views.game_table, name='games'),
        url(r'^chart/$', views.chart, name='chart'),
        )
        