from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

# # Import models to use in website (database - site connection)
# from app_voetbalelo.models.jpl_playoffs import game_data

# from app_voetbalelo.models.jpl_playoffs import speeldagen

# from app_voetbalelo.models.jpl_playoffs import standings_rs
# from app_voetbalelo.models.jpl_playoffs import standings_poi
# from app_voetbalelo.models.jpl_playoffs import standings_poii_a
# from app_voetbalelo.models.jpl_playoffs import standings_poii_b
# from app_voetbalelo.models.jpl_playoffs import standings_poiii

# from app_voetbalelo.models.jpl_playoffs import elo_data_rs
# from app_voetbalelo.models.jpl_playoffs import elo_data_poi
# from app_voetbalelo.models.jpl_playoffs import elo_data_poii_a
# from app_voetbalelo.models.jpl_playoffs import elo_data_poii_b
# from app_voetbalelo.models.jpl_playoffs import elo_data_poiii

# To make list of lists that are not copies of each other
from itertools import repeat

# To make Google Charts accept Decimal Data
import json
import decimal
import datetime

import numpy as np

# To make sure transition from Django to Template (javascript) is smooth
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

# Definition to make datetime python object JSON serializable
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        else:
            return super(DateTimeEncoder, self).default(obj)
            
import pickle


def index(request):
    # Import data (don't use database for now)
    histogram = pickle.load(open("app_sentiment/bdw/results/histogram.p","rb"))

    return render(request, 'apps/app_sentiment/bdw/index.html', {"histogram":histogram})