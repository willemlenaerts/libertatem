################################################################################
# Bereken de ELO van all voetbalploegen in UEFA Europacup 1 of CL over de 
# periode 1955-2015
################################################################################

# Importeer data en sla op in panda
import pickle
import pandas as pd
import glob
import datetime

data = pickle.load(open("app_voetbalelo/uefa_geschiedenis/algorithm/data/games.p","rb"))

# Remove (f) in FTHG or FTAG
for i in range(len(data["FTHG"])):
    if " (f)" in data["FTHG"][i]:
        data["FTHG"][i] = data["FTHG"][i].split(" ")[0]
    if " (f)" in data["FTAG"][i]:
        data["FTAG"][i] = data["FTAG"][i].split(" ")[0]
        
data["HomeElo"] = len(data["DATE"])*[0]
data["AwayElo"] = len(data["DATE"])*[0]
data["HomeWinExp"] = len(data["DATE"])*[0]
data["AwayWinExp"] = len(data["DATE"])*[0]
data["DrawExp"] = len(data["DATE"])*[0]

panda = pd.DataFrame(data)

# Converteer datum naar datetime en maak er de index van de panda van
panda.Date = pd.to_datetime(panda.DATE)
panda = panda.set_index("DATE")
panda = panda.sort_index()
# panda["DATE_INDEX"] = [x*1000000 for x in list(range(len(data["DATE"])))]

# Remove games where FTHG or FTAG == " "
panda = panda[(panda.FTHG != " ") & (panda.FTAG != " ")]
panda.loc[panda.HomeTeam == 'EB/Streymur', "HomeTeam"] = 'EB Streymur'
panda.loc[panda.AwayTeam == 'EB/Streymur', "HomeTeam"] = 'EB Streymur'

# Voeg kolommen HomeElo, AwayElo, HomeWinExp, AwayWinExp, DrawExp toe
# Duurt ongeveer 30 seconden per seizoen (dus 10min voor 20 seizoenen)
from app_voetbalelo.uefa_geschiedenis.algorithm.elo import elo
panda = elo(panda)

# Save
import pickle
pickle.dump(panda, open("app_voetbalelo/uefa_geschiedenis/algorithm/results/games-1955-2015.p","wb"))