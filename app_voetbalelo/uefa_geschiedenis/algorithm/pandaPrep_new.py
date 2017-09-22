import pickle
import json
import pandas as pd
import numpy as np
import datetime
import time

# Import data (don't use database for now)
panda = pickle.load(open("app_voetbalelo/uefa_geschiedenis/algorithm/results/games-1955-2015.p","rb"))

# All teams that played in dataset:
teams = list(panda["HomeTeam"].unique())
teams.sort()

# All dates (as unix)
dates = [int(i) for i in list(panda.index.astype(np.int64) // 10 ** 6)]

# Seasons
seasons = sorted(list(panda["Y"].unique()))

# ELO value for every team on every date (dict with keys teams and values elo
data = dict()
max_elo = dict()
min_elo = dict()

# # For every season, define date_index
# start_index = 0
# interval_mem = 0
# date_index = dict()
# dates_index = list()
# last_season = seasons[0]
# for season in seasons:
#     if season != seasons[0]:
#         season_interval = int(season) - int(last_season)
#     else:
#         season_interval = 1
        
#     start = time.time()
#     dummy = []
#     for team in teams:
#         dummy.append(len(panda[(panda.Y == season) & ((panda.HomeTeam == team) | (panda.AwayTeam == team))]))
#     max_speeldagen = max(dummy) + 1 # increment before new season (null value between seasons)
#     if max_speeldagen == 1:
#         max_speeldagen = 10 + 1
    
#     # Date_index
#     date_index[season] = [interval_mem + 1000000*10*(season_interval-1)+1000000*int(i) for i in list(range(start_index,start_index+max_speeldagen))]
#     interval_mem += 1000000*10*(season_interval-1)
#     start_index += max_speeldagen
    
#     last_season = season
#     stop = time.time()
#     print("Year: " + season + " || Time: " + str(int(stop-start)) + " || Interval: " + str(season_interval) + " season")
#     # First search max_speeldagen
    
#     dates_index += date_index[season]

# date_index_reversed = dict()
# for season in seasons:
#     for i in range(len(date_index[season])):
#         date_index_reversed[date_index[season][i]] = season

# Get games_table
game_table = []
for i in range(len(panda)):
    game_table.append({"datum":dates[i],
                        "type":panda.TYPE[i],
                        "wedstrijd":panda.HomeTeam[i] + " - " + panda.AwayTeam[i],
                        "score":panda.FTHG[i] + " - " + panda.FTAG[i]})

team_table = []
for counter,team in enumerate(teams):
    start = time.time()
    max_elo[team] = []
    min_elo[team] = []
    data[team] = dict()
    
    wedstrijden_totaal_string = len(pd.concat([panda[(panda.HomeTeam == team)],panda[(panda.AwayTeam == team)]]))
    winst_string = len(pd.concat([panda[(panda.HomeTeam == team) & (panda.FTHG.astype(float) > panda.FTAG.astype(float))],panda[(panda.AwayTeam == team) & (panda.FTAG.astype(float) > panda.FTHG.astype(float))]]))
    gelijk_string = len(pd.concat([panda[(panda.HomeTeam == team) & (panda.FTHG.astype(float) == panda.FTAG.astype(float))],panda[(panda.AwayTeam == team) & (panda.FTAG.astype(float) == panda.FTHG.astype(float))]]))
    verlies_string = len(pd.concat([panda[(panda.HomeTeam == team) & (panda.FTHG.astype(float) < panda.FTAG.astype(float))],panda[(panda.AwayTeam == team) & (panda.FTAG.astype(float) < panda.FTHG.astype(float))]]))
    
    # for i in range(len(panda[panda.HomeTeam == team])):
    #     wedstrijden_totaal_string += 1
    #     if int(panda[panda.HomeTeam == team].FTHG[i]) > int(panda[panda.HomeTeam == team].FTAG[i]):
    #         winst_string += 1
    #     elif int(panda[panda.HomeTeam == team].FTHG[i]) == int(panda[panda.HomeTeam == team].FTAG[i]):
    #         gelijk_string += 1
    #     else:    
    #         verlies_string += 1
    
    # for i in range(len(panda[panda.AwayTeam == team])):
    #     wedstrijden_totaal_string += 1
    #     if int(panda[panda.AwayTeam == team].FTHG[i]) > int(panda[panda.AwayTeam == team].FTAG[i]):
    #         verlies_string += 1
    #     elif int(panda[panda.AwayTeam == team].FTHG[i]) == int(panda[panda.AwayTeam == team].FTAG[i]):
    #         gelijk_string += 1
    #     else:    
    #         winst_string += 1            
    try: 
        nuelo = str(int(pd.concat([panda[(panda.HomeTeam == team) & (panda.index.astype(datetime.datetime) > datetime.datetime(2015, 1, 1,0,0))]["HomeElo"],panda[(panda.AwayTeam == team) & (panda.index.astype(datetime.datetime) > datetime.datetime(2015, 1, 1,0,0))]["AwayElo"]]).sort_index()[-1]))
    except:
        nuelo = ""
    doelpuntensaldo = sum([int(i) for i in pd.concat([panda[(panda.HomeTeam == team)]["FTHG"],panda[(panda.AwayTeam == team)]["FTAG"]])]) - sum([int(i) for i in pd.concat([panda[(panda.HomeTeam == team)]["FTAG"],panda[(panda.AwayTeam == team)]["FTHG"]])])
    doelpuntensaldo_perwedstrijd = round(doelpuntensaldo/wedstrijden_totaal_string,2)
    team_table.append({ "team":team,
                        "nuelo": nuelo,
                        "gemelo": str(int(sum(pd.concat([panda[(panda.HomeTeam == team)]["HomeElo"],panda[(panda.AwayTeam == team)]["AwayElo"]]))/len(pd.concat([panda[(panda.HomeTeam == team)]["HomeElo"],panda[(panda.AwayTeam == team)]["AwayElo"]])))),
                        "maxelo": str(int(max(pd.concat([panda[(panda.HomeTeam == team)]["HomeElo"],panda[(panda.AwayTeam == team)]["AwayElo"]])))),
                        "minelo": str(int(min(pd.concat([panda[(panda.HomeTeam == team)]["HomeElo"],panda[(panda.AwayTeam == team)]["AwayElo"]])))),
                        "jaren": len(list(set(pd.concat([panda[(panda.HomeTeam == team)],panda[(panda.AwayTeam == team)]]).Y))),
                        "wedstrijden":str(wedstrijden_totaal_string),
                        "wedstrijdenwinst": str(winst_string),
                        "wedstrijdengelijk":str(gelijk_string),
                        "wedstrijdenverlies":str(verlies_string),
                        "goalsvoor": sum([int(i) for i in pd.concat([panda[(panda.HomeTeam == team)]["FTHG"],panda[(panda.AwayTeam == team)]["FTAG"]])]) ,
                        "goalstegen": sum([int(i) for i in pd.concat([panda[(panda.HomeTeam == team)]["FTAG"],panda[(panda.AwayTeam == team)]["FTHG"]])]),
                        "winperc": str(round(100*(winst_string/wedstrijden_totaal_string),1)),
                        "doelpuntensaldo": doelpuntensaldo_perwedstrijd                   
                        })
    # data[team]["kampioenschappen"] = len(team_results[team])
    data[team]["gemiddelde elo"] = int(sum(pd.concat([panda[(panda.HomeTeam == team)]["HomeElo"],panda[(panda.AwayTeam == team)]["AwayElo"]]))/len(pd.concat([panda[(panda.HomeTeam == team)]["HomeElo"],panda[(panda.AwayTeam == team)]["AwayElo"]])))
    data[team]["hoogste elo"] = int(max(pd.concat([panda[(panda.HomeTeam == team)]["HomeElo"],panda[(panda.AwayTeam == team)]["AwayElo"]])))
    data[team]["laagste elo"] = int(min(pd.concat([panda[(panda.HomeTeam == team)]["HomeElo"],panda[(panda.AwayTeam == team)]["AwayElo"]])))
    
    for season in seasons:
        data[team][season] = list()
        dataframe_elo = pd.concat([panda[(panda.HomeTeam == team) & (panda.Y == season)]["HomeElo"],panda[(panda.AwayTeam == team) & (panda.Y == season)]["AwayElo"]]).sort_index()
        # dataframe_date_index = pd.concat([panda[(panda.HomeTeam == team) & (panda.Y == season)]["DATE_INDEX"],panda[(panda.AwayTeam == team) & (panda.Y == season)]["DATE_INDEX"]]).sort_index()
        dataframe_wedstrijd = pd.concat([team + " - " + panda[(panda.HomeTeam == team) & (panda.Y == season)]["AwayTeam"],panda[(panda.AwayTeam == team) & (panda.Y == season)]["HomeTeam"] + " - " + team ]).sort_index()
        dataframe_3 = pd.concat([panda[(panda.HomeTeam == team) & (panda.Y == season)]["FTHG"],panda[(panda.AwayTeam == team) & (panda.Y == season)]["FTHG"]]).sort_index()
        dataframe_4 = pd.concat([panda[(panda.HomeTeam == team) & (panda.Y == season)]["FTAG"],panda[(panda.AwayTeam == team) & (panda.Y == season)]["FTAG"]]).sort_index()
        dataframe_type = pd.concat([panda[(panda.HomeTeam == team) & (panda.Y == season)]["TYPE"],panda[(panda.AwayTeam == team) & (panda.Y == season)]["TYPE"]]).sort_index()

        # [0]: Datum index (niet echte datum maar plotdatum)
        data[team][season].append([int(i) for i in list(dataframe_elo.index.astype(np.int64) // 10 ** 6)])
        # data[team][season].append(date_index[season][:len(dataframe_elo)])
        
        # [1]: ELO na wedstrijd
        data[team][season].append([int(i) for i in list(dataframe_elo)])
        # data[team][season].append([int(i) for i in list(dataframe_elo)])
        
        # Get maximum elo
        # Remove None's
        
        try:
            max_elo[team].append(max(list(data[team][season][-1])))
        except:
            # Dit seizoen speelde ploeg niet
            max_elo[team].append(0)

        # Get minimum elo
        try:
            min_elo[team].append(min(list(data[team][season][-1])))
        except:
            # Dit seizoen speelde ploeg niet
            min_elo[team].append(0)
            
        # [2]: Wedstrijd in string (HomeTeam - AwayTeam)
        data[team][season].append(list(dataframe_wedstrijd))
        
        # [3]: Score (Home Goals - Away Goals)
        data[team][season].append([])
        for i in range(len(dataframe_elo)):
            data[team][season][-1].append(dataframe_3[i] + " - " + dataframe_4[i])
        
        # # [4]: Datum wedstrijd
        # dataframe_elo_index_list = [int(i) for i in list(dataframe_elo.index.astype(np.int64) // 10 ** 6)]
        # data[team][season].append([])
        # for i in range(len(date_index[season])):
        #     try:
        #         data[team][season][-1].append(dataframe_elo_index_list[i])
        #     except:
        #         data[team][season][-1].append(None)
        
        # data[team][season].append([int(i) for i in list(dataframe_elo.index.astype(np.int64) // 10 ** 6)])
        
        # [5]: Type of game
        data[team][season].append(list(dataframe_type))
        
        # # [6]: Kampioen (1: ja, 0: nee)
        # data[team][season].append(0)   
        # if len(team_results[team]) > 0:
        #     for kampioenschap_seizoen in team_results[team]:
        #         if kampioenschap_seizoen == season:
        #             data[team][season][-1] = 1
        #             break
        
    max_elo[team] = max(max_elo[team])
    min_elo[team] = min(list(filter((0).__ne__, min_elo[team])))
    
    stop = time.time()
    print("Team: " + team + " || Time: " + str(int(stop-start)) + " s")
    
max_elo_data = dict()
for team in teams:
    max_elo_data[team] = list()
    for s in range(len(seasons)):
        for i in range(len(data[team][seasons[s]][1])):
            if data[team][seasons[s]][1][i] == max_elo[team]:
                max_elo_data[team].append([s,i])

min_elo_data = dict()
for team in teams:
    min_elo_data[team] = list()
    for s in range(len(seasons)):
        for i in range(len(data[team][seasons[s]][1])):
            if data[team][seasons[s]][1][i] == min_elo[team]:
                min_elo_data[team].append([s,i])

# pickle.dump(data,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/elo-evolution.p","wb"))
# pickle.dump(teams,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/teams.p","wb"))
# pickle.dump(dates,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/dates.p","wb"))
# pickle.dump(seasons,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/seasons.p","wb"))
# pickle.dump(max_elo_data,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/max_elo_data.p","wb"))

# Per team

for team in teams:
    data_team = dict()
    data_team[team] = data[team]
    json.dump(data_team,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/json.dump/teams/" + team + ".json","w"))

json.dump(data,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/json.dump/elo-evolution.json","w"))
json.dump(dates,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/json.dump/dates.json","w"))
json.dump(team_table,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/json.dump/team_table.json","w"))
json.dump(game_table,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/json.dump/game_table.json","w"))
json.dump(teams,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/json.dump/teams.json","w"))
json.dump(seasons,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/json.dump/seasons.json","w"))
json.dump(max_elo_data,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/json.dump/max_elo_data.json","w"))
json.dump(min_elo_data,open("app_voetbalelo/uefa_geschiedenis/algorithm/results/json.dump/min_elo_data.json","w"))