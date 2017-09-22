from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

# # Import models to use in website (database - site connection)
# from app_voetbalelo.models.wereld_playoffs import game_data

# from app_voetbalelo.models.wereld_playoffs import speeldagen

# from app_voetbalelo.models.wereld_playoffs import standings_rs
# from app_voetbalelo.models.wereld_playoffs import standings_poi
# from app_voetbalelo.models.wereld_playoffs import standings_poii_a
# from app_voetbalelo.models.wereld_playoffs import standings_poii_b
# from app_voetbalelo.models.wereld_playoffs import standings_poiii

# from app_voetbalelo.models.wereld_playoffs import elo_data_rs
# from app_voetbalelo.models.wereld_playoffs import elo_data_poi
# from app_voetbalelo.models.wereld_playoffs import elo_data_poii_a
# from app_voetbalelo.models.wereld_playoffs import elo_data_poii_b
# from app_voetbalelo.models.wereld_playoffs import elo_data_poiii

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
    elo_evolution = pickle.load(open("app_voetbalelo/wereld_geschiedenis/algorithm/results/elo-evolution.p","rb"))
    countries = pickle.load(open("app_voetbalelo/wereld_geschiedenis/algorithm/results/countries.p","rb"))
    dates = pickle.load(open("app_voetbalelo/wereld_geschiedenis/algorithm/results/dates.p","rb"))
    max_elo_data = pickle.load(open("app_voetbalelo/wereld_geschiedenis/algorithm/results/max_elo_data.p","rb"))
    
    colors = {  "Aalst": "rgba(0,0,0,1)",
                "Anderlecht": "rgba(80, 40, 128,1)",
                "Antwerp":  "rgba(207, 8, 14,1)" ,
                "Bergen": "rgba(207, 8, 14,1)",
                "Beveren": "rgba(205, 179, 13,1)",
                "Cercle Brugge": "rgba(0, 153, 73,1)",
                "Charleroi": "rgba(0,0,0,1)",
                "Club Brugge": "rgba(0, 116, 189,1)",
                "Dender": "rgba(38, 55, 115,1)",
                "Eupen": "rgba(0,0,0,1)",
                "FC Brussels": "rgba(222, 36, 37,1)",
                "Geel":  "rgba(224, 30, 35,1)",
                "Genk": "rgba(25, 50, 147,1)",
                "Gent":  "rgba(0, 71, 156,1)",
                "Germinal": "rgba(39, 2, 69,1)",
                "Harelbeke":  "rgba(93, 12, 133,1)",
                "Heusden Zolder": "rgba(65, 158, 43,1)",
                "Kortrijk": "rgba(207, 8, 14,1)" ,
                "Lierse":  "rgba(205, 179, 13,1)",
                "Lokeren":"rgba(0,0,0,1)",
                "Lommel":  "rgba(0, 153, 102,1)",
                "Louvieroise": "rgba(0, 148, 72,1)" ,
                "Mechelen":  "rgba(224, 30, 35,1)",
                "Molenbeek":  "rgba(229, 20, 42,1)",
                "Mouscron": "rgba(229, 20, 42,1)",
                "Mouscron-Peruwelz": "rgba(229, 20, 42,1)",
                "Oostende": "rgba(190, 22, 35,1)" ,
                "Oud-Heverlee Leuven": "rgba(0,0,0,1)",
                "Roeselare": "rgba(0,0,0,1)"  ,
                "Seraing": "rgba(223, 19, 10,1)" , 
                "St Truiden": "rgba(205, 179, 13,1)" ,
                "Standard": "rgba(207, 8, 14,1)"  ,
                "Tubize": "rgba(217, 53, 52,1)"  ,
                "Waasland-Beveren":  "rgba(205, 179, 13,1)" ,
                "Waregem": "rgba(132, 31, 47,1)"  ,
                "Westerlo": "rgba(205, 179, 13,1)"  
    }
    
    # json.dump(colors,open("app_voetbalelo/wereld_geschiedenis/algorithm/data/colors.json", "w"))
    # import random
    # for team in teams:
    #     r = lambda: random.randint(0,255)
    #     colors[team] = '#%02X%02X%02X' % (r(),r(),r())
    
    elo_evolution = json.dumps(elo_evolution)
    countries = json.dumps(countries)
    dates = json.dumps(dates, cls=DateTimeEncoder)
    return render(request, 'apps/app_voetbalelo/wereld_geschiedenis/index.html', {"elo_evolution":elo_evolution,"countries":countries, "dates": dates, "max_elo_data":max_elo_data})
    
    
    
    