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
    elo_evolution = pickle.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/elo-evolution.p","rb"))
    teams = pickle.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/teams.p","rb"))
    dates = pickle.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/dates.p","rb"))
    seasons = pickle.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/seasons.p","rb"))
    max_elo_data = pickle.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/max_elo_data.p","rb"))
    
    # elo_evolution = json.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/json.dump/elo-evolution.json","rb"))
    # teams = json.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/json.dump/teams.json","rb"))
    # date_index = json.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/json.dump/date_index.json","rb"))
    # seasons = json.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/json.dump/seasons.j","rb"))
    # max_elo_data = json.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/json.dump/max_elo_data.p","rb"))
    
    # colors = {  "AA GENT": "rgba(0, 71, 156,1)",
    #             "ANDERLECHT RSC": "rgba(80, 40, 128,1)",
    #             "ANTWERP FC": "rgba(207, 8, 14,1)" ,
    #             "ATHLETIC RAC.CL.BRUSSEL": "rgba(0,0,0,1)",
    #             "BEERSCHOT K.AC": "rgba(64,0,128,1)",
    #             "BEERSCHOT VAC":"rgba(138,43,226,1)",
    #             "BELGICA EDEGEM":"rgba(17,118,73,1)",
    #             "BERCHEM SP.":"rgba(205, 179, 13,1)",
    #             "BERINGEN FC":"rgba(255,0,0,1)",
    #             "BEVEREN KSK": "rgba(205, 179, 13,1)",
    #             "BEVEREN-WAES SK":"rgba(205, 179, 13,1)",
    #             "BOOM KFC": "rgba(0,0,255,1)",
    #             "CERCLE BRUGGE K.SV":"rgba(0, 153, 73,1)",
    #             "CHARLEROI R.S.C.": "rgba(0,0,0,1)",
    #             "CLUB BRUGGE KV": "rgba(0, 116, 189,1)",
    #             "COURTRAI SC":"rgba(221,0,0,1)",
    #             "CROSSING SCHAERBEEK":"rgba(8,88,45,1)",
    #             "DARING CLUB BRUSSEL":"rgba(255,0,0,1)",
    #             "DENDER E.H. FC V.": "rgba(38, 55, 115,1)",
    #             "DIEST FC": "rgba(0,0,0,1)",
    #             "DOORNIK RC": "rgba(231,218,90,1)",
    #             "DOORNIK US":"rgba(221,0,0,1)",
    #             "EENDRACHT AALST KSC":"rgba(0,0,0,1)",
    #             "EUPEN AS":"rgba(0,0,0,1)",
    #             "EXCELSIOR SC BRUSSEL":"rgba(35,48,95,1)",
    #             "GENK RC":"rgba(25, 50, 147,1)",
    #             "GENT RC":"rgba(0,0,0,1)",
    #             "GERMINAL BEERSCHOT A.":"rgba(64,0,128,1)",
    #             "GERMINAL EKEREN KFC":"rgba(249,215,22,1)",
    #             "HARELBEKE K.RC":"rgba(114,88,127,1)",
    #             "HASSELT KSC":"rgba(0,0,153,1)",
    #             "HEUSDEN-ZOLDER K.":"rgba(65, 158, 43,1)",
    #             "KORTRIJK KV":"rgba(207, 8, 14,1)" ,
    #             "KV MECHELEN":"rgba(224, 30, 35,1)",
    #             "LA LOUVIERE":"rgba(0, 148, 72,1)" ,
    #             "LEOPOLD CLUB BRUSSEL":"rgba(255,0,0,1)",
    #             "LIERSE SK":"rgba(205, 179, 13,1)",
    #             "LOKEREN KSC":"rgba(0,0,0,1)",
    #             "LOKEREN SC S.N.W.":"rgba(0,0,0,1)",
    #             "LOMMEL SK":"rgba(0, 153, 102,1)",
    #             "LUIK FC":"rgba(209,0,0,1)",
    #             "LYRA TSV":"rgba(238,0,0,1)",
    #             "MOESKROEN R. EXC.":"rgba(229, 20, 42,1)",
    #             "MOLENBEEK-BRUSSELS STR.":"rgba(255,0,0,1)",
    #             "MONS RAEC":"rgba(207, 8, 14,1)",
    #             "MONTEGNEE RC":"rgba(0,0,192,1)",
    #             "MOUSCRON-PERUWELZ R.":"rgba(229, 20, 42,1)",
    #             "OLYMPIC CHARLEROI":"rgba(0,0,0,1)",
    #             "OLYMPIC-MONTIGNIES RC":"rgba(0,0,0,1)",
    #             "OOSTENDE AS":"rgba(0,128,0,1)",
    #             "OOSTENDE KV":"rgba(190, 22, 35,1)" ,
    #             "OUD-HEVERLEE LEUVEN":"rgba(0,0,0,1)",
    #             "PATRO EISDEN":"rgba(128,65,179,1)",
    #             "R.W.D.MOLENBEEK":"rgba(229, 20, 42,1)",
    #             "RACING CLUB BRUSSEL":"rgba(0,0,0,1)",
    #             "RACING WHITE":"rgba(0,0,0,1)",
    #             "RC JET BRUSSEL":"rgba(0,168,107,1)",
    #             "RC MECHELEN":"rgba(1,90,42,1)",
    #             "ROESELARE KSV":"rgba(0,0,0,1)",
    #             "SERAING RFC":"rgba(223, 19, 10,1)", 
    #             "SKILL F.C. Bruxelles":"rgba(0,0,0,1)",
    #             "SPORTING CLUB BRUSSEL":"rgba(0,0,200,1)",
    #             "ST.NIKLAAS SK":"rgba(205, 179, 13,1)",
    #             "ST.TRUIDEN K.SV":"rgba(205, 179, 13,1)",
    #             "STADE LEUVEN K.":"rgba(139,226,147,1)",
    #             "STANDARD LUIK":"rgba(207, 8, 14,1)",
    #             "TIENEN RC":"rgba(0,0,240,1)",
    #             "TILLEUR FC":"rgba(56,114,187,1)",
    #             "TONGEREN KSK":"rgba(0,0,240,1)",
    #             "TUBANTIA FC":"rgba(255,0,0,1)",
    #             "TUBEKE A.F.C.":"rgba(217, 53, 52,1)",
    #             "TURNHOUT KFC":"rgba(0,0,240,1)",
    #             "UCCLE SPORT":"rgba(22,98,162,1)",
    #             "UNION Football Club":"rgba(0,0,0,1)",
    #             "UNION ST.GILLIS R.":"rgba(255,215,0,1)",
    #             "VERBROEDERING GEEL KFC":"rgba(0,0,240,1)",
    #             "VERVIERS FC":"rgba(0,128,0,1)",
    #             "VERVIETOIS RCS": "rgba(0,128,0,1)",
    #             "VORST CS":"rgba(0,0,0,1)",
    #             "WAASLAND RS SP.BEVEREN":"rgba(205, 179, 13,1)",
    #             "WAREGEM SV":"rgba(220, 0, 0,1)",
    #             "WATERSCHEI THOR":"rgba(254,203,51,1)",
    #             "WESTERLO KVC":"rgba(205, 179, 13,1)",
    #             "WHITE STAR R.AC":"rgba(192,0,0,1)",
    #             "WINTERSLAG KFC":"rgba(214,4,3,1)",
    #             "YR KV MECHELEN":"rgba(224, 30, 35,1)",
    #             "ZULTE-WAREGEM SV":"rgba(132, 31, 47,1)"
    #     }
        
    # colors = {  "Aalst": "rgba(0,0,0,1)",
    #             "Anderlecht": "rgba(80, 40, 128,1)",
    #             "Antwerp":  "rgba(207, 8, 14,1)" ,
    #             "Bergen": "rgba(207, 8, 14,1)",
    #             "Beveren": "rgba(205, 179, 13,1)",
    #             "Cercle Brugge": "rgba(0, 153, 73,1)",
    #             "Charleroi": "rgba(0,0,0,1)",
    #             "Club Brugge": "rgba(0, 116, 189,1)",
    #             "Dender": "rgba(38, 55, 115,1)",
    #             "Eupen": "rgba(0,0,0,1)",
    #             "FC Brussels": "rgba(222, 36, 37,1)",
    #             "Geel":  "rgba(224, 30, 35,1)",
    #             "Genk": "rgba(25, 50, 147,1)",
    #             "Gent":  "rgba(0, 71, 156,1)",
    #             "Germinal": "rgba(39, 2, 69,1)",
    #             "Harelbeke":  "rgba(93, 12, 133,1)",
    #             "Heusden Zolder": "rgba(65, 158, 43,1)",
    #             "Kortrijk": "rgba(207, 8, 14,1)" ,
    #             "Lierse":  "rgba(205, 179, 13,1)",
    #             "Lokeren":"rgba(0,0,0,1)",
    #             "Lommel":  "rgba(0, 153, 102,1)",
    #             "Louvieroise": "rgba(0, 148, 72,1)" ,
    #             "Mechelen":  "rgba(224, 30, 35,1)",
    #             "Molenbeek":  "rgba(229, 20, 42,1)",
    #             "Mouscron": "rgba(229, 20, 42,1)",
    #             "Mouscron-Peruwelz": "rgba(229, 20, 42,1)",
    #             "Oostende": "rgba(190, 22, 35,1)" ,
    #             "Oud-Heverlee Leuven": "rgba(0,0,0,1)",
    #             "Roeselare": "rgba(0,0,0,1)"  ,
    #             "Seraing": "rgba(223, 19, 10,1)" , 
    #             "St Truiden": "rgba(205, 179, 13,1)" ,
    #             "Standard": "rgba(207, 8, 14,1)"  ,
    #             "Tubize": "rgba(217, 53, 52,1)"  ,
    #             "Waasland-Beveren":  "rgba(205, 179, 13,1)" ,
    #             "Waregem": "rgba(132, 31, 47,1)"  ,
    #             "Westerlo": "rgba(205, 179, 13,1)"  
    # }
    
    json.dump(colors,open("app_voetbalelo/jpl_geschiedenis/algorithm/data/colors.json", "w"))
    # import random
    # for team in teams:
    #     r = lambda: random.randint(0,255)
    #     colors[team] = '#%02X%02X%02X' % (r(),r(),r())
    
    elo_evolution = json.dumps(elo_evolution)
    teams = json.dumps(teams)
    dates = json.dumps(dates, cls=DateTimeEncoder)
    return render(request, 'apps/app_voetbalelo/jpl_geschiedenis/index.html', {"elo_evolution":elo_evolution,"teams":teams, "dates": dates, "seasons":seasons, "max_elo_data":max_elo_data, "colors":colors})