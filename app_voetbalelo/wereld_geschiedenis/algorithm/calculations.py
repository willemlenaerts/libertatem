# # Check average ELO
import pickle
countries = pickle.load(open("app_voetbalelo/wereld_geschiedenis/algorithm/results/countries.p","rb"))
games = pickle.load(open("app_voetbalelo/wereld_geschiedenis/algorithm/results/wereld_newrules.p","rb"))

# elo = []
# for country in countries:
#     if games[(games.HOME_TEAM == country)].sort_index(ascending = False).index[0] >\
#     games[(games.AWAY_TEAM == country)].sort_index(ascending = False).index[0]:
#         elo.append(games[(games.HOME_TEAM == country)].sort_index(ascending = False).HomeElo[0])
#     else:
#         elo.append(games[(games.AWAY_TEAM == country)].sort_index(ascending = False).AwayElo[0])


# Some calculations for the article on blog
import numpy as np
import pandas as pd
import pickle
import math
import datetime

# dElo per game
dElo_game = dict()
games.sort(['dElo'], ascending=False).iloc[0:9]

# # dElo per season
# dElo_season = [[],[],[]]
# for country in countries:
#     dummy = pd.concat([games[(games.HomeTeam == country) & (games.S == season)]["HomeElo"],games[(games.AwayTeam == country) & (games.S == season)]["AwayElo"]]).sort_index()
#     try:
#         dElo_season[0].append(max(dummy)-min(dummy))
#     except:
#         dElo_season[0].append(0)
#     dElo_season[1].append(country)
#     dElo_season[2].append(season)

# zipped = zip(dElo_season[0],dElo_season[1],dElo_season[2])
        
# Avg Elo total (per year, not per game because skewed towards modern days)
# elo_mean = [[],[]]
# years = list(range(1872,2016))
# # datetime.datetime.fromtimestamp(games.index[0].value/1000000000).year
# for country in countries:
#     elo_mean[0].append(country)
#     elo_mean[1].append([])
#     for year in years:
#         dummy = pd.concat([games[(games.HOME_TEAM == country)]["HomeElo"],games[(games.AWAY_TEAM == country)]["AwayElo"]]).sort_index()
#         dummy = dummy[datetime.datetime(year,1,1):datetime.datetime(year+1,1,1)]
#         if not math.isnan(dummy.mean()):
#             elo_mean[1][-1].append(dummy.mean())
#     elo_mean[1][-1] = sum(elo_mean[1][-1])/len(elo_mean[1][-1])
# zipped = sorted(zip(elo_mean[1],elo_mean[0]))

# # Avg Elo per season
# elo_mean = [[],[],[]]
# for country in countries:
#     for season in seasons:
#         elo_mean[0].append(country)
#         elo_mean[1].append(season)
#         dummy = pd.concat([games[(games.HomeTeam == country) & (games.S == season)]["HomeElo"],games[(games.AwayTeam == country) & (games.S == season)]["AwayElo"]]).sort_index()
#         if math.isnan(dummy.mean()):
#             elo_mean[2].append(0)
#         else:
#             elo_mean[2].append(dummy.mean())

# zipped = zip(elo_mean[2],elo_mean[0],elo_mean[1])

# Max Elo
# max_country = [[],[],[],[],[],[]]
# for country in countries:
#     if games[(games.HOME_TEAM == country)].sort(["HomeElo"]).HomeElo[-1] > games[(games.AWAY_TEAM == country)].sort(["AwayElo"]).AwayElo[-1]:
#         max_country[0].append(games[(games.HOME_TEAM == country)].sort(["HomeElo"]).HOME_TEAM[-1])
#         max_country[1].append(games[(games.HOME_TEAM == country)].sort(["HomeElo"]).AWAY_TEAM[-1])
#         max_country[2].append(games[(games.HOME_TEAM == country)].sort(["HomeElo"]).FTHG[-1])
#         max_country[3].append(games[(games.HOME_TEAM == country)].sort(["HomeElo"]).FTAG[-1])
#         max_country[4].append(games[(games.HOME_TEAM == country)].sort(["HomeElo"]).HomeElo[-1])
#         max_country[5].append(games[(games.HOME_TEAM == country)].sort(["HomeElo"]).index[-1])
#     else:
#         max_country[0].append(games[(games.AWAY_TEAM == country)].sort(["AwayElo"]).AWAY_TEAM[-1])
#         max_country[1].append(games[(games.AWAY_TEAM == country)].sort(["AwayElo"]).HOME_TEAM[-1])
#         max_country[2].append(games[(games.AWAY_TEAM == country)].sort(["AwayElo"]).FTHG[-1])
#         max_country[3].append(games[(games.AWAY_TEAM == country)].sort(["AwayElo"]).FTAG[-1])
#         max_country[4].append(games[(games.AWAY_TEAM == country)].sort(["AwayElo"]).AwayElo[-1])
#         max_country[5].append(games[(games.AWAY_TEAM == country)].sort(["AwayElo"]).index[-1])    
        
# zipped = sorted(zip(max_country[4],max_country[0],max_country[1],max_country[2],max_country[3],max_country[5]))