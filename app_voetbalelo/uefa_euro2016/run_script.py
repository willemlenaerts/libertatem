from app_voetbalelo.uefa_euro2016.expand_elo import expand_elo
from app_voetbalelo.uefa_euro2016.get_games_data import get_games_data
from app_voetbalelo.uefa_euro2016.game_to_team import make_standing, rank
from app_voetbalelo.uefa_euro2016.montecarlo import montecarlo
from app_voetbalelo.uefa_euro2016.milp_montecarlo import milp_montecarlo

import copy
import datetime
import json
import pickle
import ftplib
import time
import numpy as np
import pandas as pd
import scipy.stats # For Poisson Distribution, numpy doesn't have it4
# Get Input data
games = get_games_data()

simulations = 20000

print("########################################")
print("Uefa Euro 2016 Algorithm")
print("########################################")
    
# Initialize output
team_data = dict()
group_data = dict()

# Expand games data with elo data
print("Get Elo Data from Sway's Country Elo Algorithm")
output = expand_elo(games)
games = output[0]
elo = output[1]


# Generate standing and rank it correctly according to the UEFA tiebreaking procedure
print("Generate Group Standing and Rank according to Uefa rules")
standing = make_standing(games)
standing = rank(standing, games)

# Montecarlo
print("Montecarlo Algorithm")
output_1 = montecarlo(games,elo,simulations)
game_data = output_1[1]

# Make Integers of output
groups = dict()
group_list = list(set(games.Group))
for group in group_list:
    if "Group" in group:
        groups[group] = list(set(games[games.Group == group].HomeTeam))

output_2 = milp_montecarlo(output_1[0],output_1[2],groups)
output_int = output_2[0]
knockout_odds = output_2[1]

# Write json teams
initial_ranking = pd.read_csv("app_voetbalelo/uefa_euro2016/data/initial_ranking.csv")
colors = pd.read_csv("app_voetbalelo/uefa_euro2016/data/teams.csv")
for team in output_int.keys(): 
    team_data[team] = dict()
    team_data[team]["knockout_odds"] = knockout_odds[team]
    team_data[team]["odds"] = output_int[team]
    team_data[team]["elo"] = int(list(set(list(set(games[games.HomeTeam == team].HomeElo)) + list(set(games[games.AwayTeam == team].AwayElo))))[0])
    team_data[team]["group"] = list(set(list(set(games[games.HomeTeam == team].Group)) + list(set(games[games.AwayTeam == team].Group))))[0]
    team_data[team]["color"] = colors[colors.country == team].color.iloc[0]
    team_data[team]["info"] = [ ["Elo Rating",elo[team]["elo"]], \
                                ["Head Coach",colors[colors.country == team].manager.iloc[0]], \
                                # ["Captain",colors[colors.country == team].captain.iloc[0]],\
                                # ["Top Scorer",colors[colors.country == team].topscorer.iloc[0]]]
                                ["Appearances",colors[colors.country == team].euro_appearances.iloc[0].astype(str)],\
                                ["Titles",colors[colors.country == team].euro_titles.iloc[0].astype(str)]]        
    team_data[team]["standing"] = dict()
    for standing_key in standing.keys():
        if standing_key != "Country":
            if standing_key == "Group":
                team_data[team]["standing"]["G"] = standing[standing.Country == team][standing_key].iloc[0]
            
            # # THIS PART ONLY UNTIL TOURNAMENT STARTS
            # elif standing_key == "R":
            #     for position in ["1","2","3","4"]:
            #         if initial_ranking[(initial_ranking.group == standing[standing.Country == team][standing_key].iloc[0])][position].iloc[0] == team:
            #             team_data[team]["standing"]["GP"] = position
            #             break
            else:
                team_data[team]["standing"][standing_key] = str(standing[standing.Country == team][standing_key].iloc[0])

    team_data[team]["games"] = list()
    for i in range(len(games)):
        if "Group" in games.Group.iloc[i]:
            if team in games.HomeTeam.iloc[i]:
                team_data[team]["games"].append(dict())
                team_data[team]["games"][-1]["HomeTeam"] = team
                team_data[team]["games"][-1]["AwayTeam"] = games.AwayTeam.iloc[i]
                team_data[team]["games"][-1]["Group"] = games.AwayTeam.iloc[i]
                team_data[team]["games"][-1]["Date"] = games.index[i].value/10**9
                team_data[team]["games"][-1]["Location"] = games.Location.iloc[i]
                team_data[team]["games"][-1]["HomeElo"] = games.HomeElo.iloc[i]
                team_data[team]["games"][-1]["AwayElo"] = games.AwayElo.iloc[i]
                team_data[team]["games"][-1]["HomeWin"] = games.HomeWin.iloc[i]
                team_data[team]["games"][-1]["AwayWin"] = games.AwayWin.iloc[i]
                team_data[team]["games"][-1]["Draw"] = games.Draw.iloc[i]
                
            elif team in games.AwayTeam.iloc[i]:
                team_data[team]["games"].append(dict())
                team_data[team]["games"][-1]["HomeTeam"] = games.HomeTeam.iloc[i]
                team_data[team]["games"][-1]["AwayTeam"] = team
                team_data[team]["games"][-1]["Group"] = games.AwayTeam.iloc[i]
                team_data[team]["games"][-1]["Date"] = games.index[i].value/10**9
                team_data[team]["games"][-1]["Location"] = games.Location.iloc[i]
                team_data[team]["games"][-1]["HomeElo"] = games.HomeElo.iloc[i]
                team_data[team]["games"][-1]["AwayElo"] = games.AwayElo.iloc[i]
                team_data[team]["games"][-1]["HomeWin"] = games.HomeWin.iloc[i]
                team_data[team]["games"][-1]["AwayWin"] = games.AwayWin.iloc[i]
                team_data[team]["games"][-1]["Draw"] = games.Draw.iloc[i]               
         
# Write json games
games_json = dict()
for i in range(len(games)):
    # Only knockout games
    if games.Group.iloc[i] == "1/8 Final":
        games_json[games.Game.iloc[i]] = dict()
        games_json[games.Game.iloc[i]]["HomeTeam"] = games.HomeTeam.iloc[i]
        games_json[games.Game.iloc[i]]["AwayTeam"] = games.AwayTeam.iloc[i]
        games_json[games.Game.iloc[i]]["Location"] = games.Location.iloc[i]
        games_json[games.Game.iloc[i]]["Date"] = games.index[i].value/10**9
        
    elif games.Group.iloc[i] == "Quarter Final":
        games_json[games.Game.iloc[i]] = dict()
        games_json[games.Game.iloc[i]]["HomeTeam"] = games.HomeTeam.iloc[i]
        games_json[games.Game.iloc[i]]["AwayTeam"] = games.AwayTeam.iloc[i]
        games_json[games.Game.iloc[i]]["Location"] = games.Location.iloc[i]
        games_json[games.Game.iloc[i]]["Date"] = games.index[i].value/10**9
        
        games_json[games.HomeTeam.iloc[i]]["To"] = games.Game.iloc[i] + " HomeTeam"
        games_json[games.AwayTeam.iloc[i]]["To"] = games.Game.iloc[i] + " AwayTeam"

    elif games.Group.iloc[i] == "Semi Final":
        games_json[games.Game.iloc[i]] = dict()
        games_json[games.Game.iloc[i]]["HomeTeam"] = games.HomeTeam.iloc[i]
        games_json[games.Game.iloc[i]]["AwayTeam"] = games.AwayTeam.iloc[i]
        games_json[games.Game.iloc[i]]["Location"] = games.Location.iloc[i]
        games_json[games.Game.iloc[i]]["Date"] = games.index[i].value/10**9
        
        games_json[games.HomeTeam.iloc[i]]["To"] = games.Game.iloc[i] + " HomeTeam"     
        games_json[games.AwayTeam.iloc[i]]["To"] = games.Game.iloc[i] + " AwayTeam"     
        
    elif games.Group.iloc[i] == "Final":
        games_json[games.Game.iloc[i]] = dict()
        games_json[games.Game.iloc[i]]["HomeTeam"] = games.HomeTeam.iloc[i]
        games_json[games.Game.iloc[i]]["AwayTeam"] = games.AwayTeam.iloc[i]
        games_json[games.Game.iloc[i]]["Location"] = games.Location.iloc[i]
        games_json[games.Game.iloc[i]]["Date"] = games.index[i].value/10**9
        
        games_json[games.HomeTeam.iloc[i]]["To"] = games.Game.iloc[i] + " HomeTeam"     
        games_json[games.AwayTeam.iloc[i]]["To"] = games.Game.iloc[i] + " AwayTeam"        

# Topojson France
topo = json.load(open("app_voetbalelo/uefa_euro2016/data/topo_ADM0_FRA.json","r"))
topo_result = copy.deepcopy(topo)
topo_result["objects"]["geo_ADM0_FRA"]["geometries"] = []
for subunit in topo["objects"]["geo_ADM0_FRA"]["geometries"]:
    if subunit["properties"]["n"] == "France":
        topo_result["objects"]["geo_ADM0_FRA"]["geometries"].append(subunit)

# Cities
cities = pd.read_csv("app_voetbalelo/uefa_euro2016/data/cities.csv", index_col=False)
cities_result = []
for i in range(len(cities)):
    cities_result.append(   {"City":cities.city.iloc[i], \
                            "Stadium":cities.stadium.iloc[i], \
                            "Capacity":cities.capacity.iloc[i].astype(str), \
                            "Lat":cities.lat.iloc[i].astype(str), \
                            "Long":cities.long.iloc[i].astype(str)})


json.dump(topo_result,open("app_voetbalelo/uefa_euro2016/result/topo_france.json","w"))
json.dump(cities_result,open("app_voetbalelo/uefa_euro2016/result/cities.json","w"))
json.dump(team_data,open("app_voetbalelo/uefa_euro2016/result/team_data.json","w"))
json.dump(game_data,open("app_voetbalelo/uefa_euro2016/result/game_data.json","w"))
json.dump(games_json,open("app_voetbalelo/uefa_euro2016/result/games.json","w"))
teams = list(team_data.keys())
json.dump(teams,open("app_voetbalelo/uefa_euro2016/result/teams.json","w"))

# Write to FTP site
session = ftplib.FTP('ftp.sway-blog.be','sway-blog.be','Will0870')
session.cwd('/www/data/elo-uefa-euro2016')

# Open data as JSON buffered (only way ftplib works)
data = open("app_voetbalelo/uefa_euro2016/result/game_data.json","rb") # file to send
session.storbinary('STOR game_data.json', data)     # send the file
data = open("app_voetbalelo/uefa_euro2016/result/team_data.json","rb") # file to send
session.storbinary('STOR data.json', data)     # send the file
data = open("app_voetbalelo/uefa_euro2016/result/teams.json","rb") # file to send
session.storbinary('STOR teams.json', data)     # send the file
data = open("app_voetbalelo/uefa_euro2016/result/games.json","rb") # file to send
session.storbinary('STOR games.json', data)     # send the file
data = open("app_voetbalelo/uefa_euro2016/result/topo_france.json","rb") # file to send
session.storbinary('STOR topo_france.json', data)     # send the file
data = open("app_voetbalelo/uefa_euro2016/result/cities.json","rb") # file to send
session.storbinary('STOR cities.json', data)     # send the file

# Create dict with last update date
# Save as json and load buffered
last_update = {"date": datetime.datetime.now().strftime("%d/%m/%Y")}
json.dump(last_update,open("app_voetbalelo/uefa_euro2016/result/last_update.json","w"))
last_update = open("app_voetbalelo/uefa_euro2016/result/last_update.json","rb")
session.storbinary('STOR date.json', last_update)

session.quit()