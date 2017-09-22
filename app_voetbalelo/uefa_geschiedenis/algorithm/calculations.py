# Some calculations for the article on blog
import numpy as np
import pandas as pd
import pickle
import json
import math

# panda = pickle.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/1995-2015.p","rb"))
# teams = pickle.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/teams.p","rb"))
# seasons = pickle.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/seasons.p","rb"))

panda = pickle.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/1895-2015.p","rb"))
teams = json.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/json.dump/teams.json","r"))
seasons = json.load(open("app_voetbalelo/jpl_geschiedenis/algorithm/results/json.dump/seasons.json","r"))


# dElo per game
dElo_game = dict()
panda.sort(['dElo'], ascending=False).iloc[0:9]

# dElo per season
dElo_season = [[],[],[]]
for team in teams:
    for season in seasons:
        dummy = pd.concat([panda[(panda.HomeTeam == team) & (panda.S == season)]["HomeElo"],panda[(panda.AwayTeam == team) & (panda.S == season)]["AwayElo"]]).sort_index()
        try:
            dElo_season[0].append(max(dummy)-min(dummy))
        except:
            dElo_season[0].append(0)
        dElo_season[1].append(team)
        dElo_season[2].append(season)

zipped = zip(dElo_season[0],dElo_season[1],dElo_season[2])
        
# Avg Elo total
elo_mean = [[],[]]
for team in teams:
    elo_mean[0].append(team)
    dummy = pd.concat([panda[(panda.HomeTeam == team)]["HomeElo"],panda[(panda.AwayTeam == team)]["AwayElo"]]).sort_index()
    elo_mean[1].append(dummy.mean())
    
zipped = sorted(zip(elo_mean[1],elo_mean[0]))

sum_total = 0
for row in a:
    sum_total+= row[0]

# Avg Elo per season
elo_mean = [[],[],[]]
for team in teams:
    for season in seasons:
        elo_mean[0].append(team)
        elo_mean[1].append(season)
        dummy = pd.concat([panda[(panda.HomeTeam == team) & (panda.S == season)]["HomeElo"],panda[(panda.AwayTeam == team) & (panda.S == season)]["AwayElo"]]).sort_index()
        if math.isnan(dummy.mean()):
            elo_mean[2].append(0)
        else:
            elo_mean[2].append(dummy.mean())
    
zipped = zip(elo_mean[2],elo_mean[0],elo_mean[1])

# Dynastie
years = 5
kamp = 3
start_year = 1895
stop_year = 2015-years+1
years_list = list(range(start_year,stop_year))
intervals = []
for i in range(len(years_list)):
    intervals.append([])
    for j in range(years):
        intervals[-1].append(str(years_list[i]+j) + "-" + str(years_list[i]+j+1)[2:])
        
teams_list = []
interval_list = []
elo_avg_list = []

for team in teams:
    for interval in intervals:
        elo_avg_list_dummy = []
        for season in interval:
            dummy = pd.concat([panda[(panda.HomeTeam == team) & (panda.S == season)]["HomeElo"],panda[(panda.AwayTeam == team) & (panda.S == season)]["AwayElo"]]).sort_index()
            if len(dummy) == 0:
                elo_avg_list_dummy.append(0)
            else:
                elo_avg_list_dummy.append(sum(dummy)/len(dummy))
        teams_list.append(team)
        interval_list.append(str(interval[0]) + "--" + str(interval[-1]))
        elo_avg_list.append(sum(elo_avg_list_dummy)/len(interval))
            
a = sorted(zip(elo_avg_list,teams_list,interval_list))            

# Kampioensjaren, avg elo


# Goals per game (per season)
gpg = dict()
gpg_totaal = []
for season in seasons:
    gpg[season] = (sum(panda[panda.S == season]["FTHG"].astype(float)) + sum(panda[panda.S == season]["FTHG"].astype(float)))/len(panda[panda.S == season])
    gpg_totaal.append(gpg[season])
    
gpg_totaal_avg = sum(gpg_totaal)/len(gpg_totaal)