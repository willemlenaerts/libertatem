################################################################################
# Bereken de ELO van alle landen mbv interlanddata FIFA
# periode 1872-2015
################################################################################

# Importeer data en sla op in panda
import pickle
import pandas as pd
import glob
import datetime
import json

# Import data
countries = pickle.load(open("app_voetbalelo/wereld_geschiedenis/algorithm/data/countries.p","rb"))
games = pickle.load(open("app_voetbalelo/wereld_geschiedenis/algorithm/data/games.p","rb"))

# Voeg wedstrijden toe die niet in FIFA database zitten
# Belgium - Croatia 0 - 1, 03/03/2010
games["AwayTeam"] = ["Croatia"] + games["AwayTeam"]
games["HomeTeam"] = ["Belgium"] + games["HomeTeam"]
games["DATE"] = ["03/03/2010"] + games["DATE"]
games["TYPE"] = ["Friendly"] + games["TYPE"]
games["FTHG"] = ["0"] + games["FTHG"]
games["FTAG"] = ["1"] + games["FTAG"]
games["LOC"] = ["Brussels, Belgium"] + games["LOC"]

# colors = dict()
# for country in countries:
#     colors[country] = "rgba(0,0,0,1)"
# json.dump(colors,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/json.dump/colors.json","w"))

# Convert datum naar datetime en creëer kolom Y (jaar)
games["Y"] = list()
for i in range(len(games["DATE"])):
    games["DATE"][i] = datetime.datetime.strptime(games["DATE"][i],"%d/%m/%Y")
    games["Y"].append(str(games["DATE"][i].year))
    
# Voeg kolommen toe die berekend zullen worden
games["HomeElo"] = len(games["HomeTeam"])*[0]
games["AwayElo"] = len(games["HomeTeam"])*[0]
games["dElo"] = len(games["HomeTeam"])*[0]
games["HomeWinExp"] = len(games["HomeTeam"])*[0]
games["AwayWinExp"] = len(games["HomeTeam"])*[0]
games["DrawExp"] = len(games["HomeTeam"])*[0]

# Make into panda and remove duplicates
games = pd.DataFrame(games).drop_duplicates()
games.DATE = pd.to_datetime(games.DATE)
games = games.set_index("DATE")
games = games.sort_index()

# Adjustments to games
games = games[(games.FTHG != "") & (games.FTHG.str.len() <= 2) & (games.FTAG.str.len() <= 2)]                                                                                                                                                                                                                                            
games.loc[games.HomeTeam == "St. Vincent / Grenadines", "HomeTeam"] = "St. Vincent and the Grenadines"
games.loc[games.AwayTeam == "St. Vincent / Grenadines", "AwayTeam"] = "St. Vincent and the Grenadines"
games.loc[games.HomeTeam == "Palestine, British Mandate", "HomeTeam"] = "Palestine British Mandate"
games.loc[games.AwayTeam == "Palestine, British Mandate", "AwayTeam"] = "Palestine British Mandate"

# Adjustments to type games
games.loc[games.TYPE == "Friendlies", "TYPE"] = "Friendly"
games.loc[games.TYPE.str.contains("Prel. Comp."), "TYPE"] = "Continental Qualifier"
games.loc[games.TYPE.str.contains("Copa América"), "TYPE"] = "Continental Final"
games.loc[games.TYPE.str.contains("Gold Cup"), "TYPE"] = "Continental Final"
games.loc[games.TYPE.str.contains("Playoff Match for FIFA Confederations Cup"), "TYPE"] = "FIFA Confederations Cup"

# Duurt ongeveer 30 seconden per seizoen (dus 10min voor 20 seizoenen)
from app_voetbalelo.wereld_geschiedenis.algorithm.elo import elo
games = elo(games)

# Save
import pickle
pickle.dump(games, open("app_voetbalelo/wereld_geschiedenis/algorithm/results/games-1872-2015.p","wb"))