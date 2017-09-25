from app_betting.code.functions.scraping.scrapeFootballdatacouk import scrapeFootballdatacouk

import numpy as np
import pandas as pd
import pickle
import datetime
import os
import datetime

# 1. Get all historical games + betting quotes data
updategames = True
if updategames:
    # Remove games file
    if os.path.isfile("app_betting/data/working/games.p"):
        os.remove("app_betting/data/working/games.p")
    
    # Get countries
    countries = ["Belgium","England","Germany","Italy","Spain","France","Netherlands","Portugal","Turkey","Greece"]
    
    # Get seasons
    number_of_seasons = 10
    seasons = list()
    current_year = datetime.datetime.now().year
    for n in range(number_of_seasons):
        seasons.append(str(current_year - n)+ "-" + str(current_year - n + 1))
    
    for country in countries:
        print(country)
        games = scrapeFootballdatacouk(country,seasons)
else:
   games = pickle.load(open("app_betting/data/working/games.p","rb")) 
   
# 2. Test strategies
bookies = ["B365","BS","BW","GB","IW","LB","PS","P","SO","SB","SJ","SY","VC","WH"]

# 2a: compare results with http://www.sportdw.com/2013/09/backing-draws-profitable-strategy.html
games_bet = games[(games.Div == "E0") & (games.Date > "2010-06-01") & (games.Date < "2011-06-01")]
games_bet = games[(games.Div == "E0") & (games.Date > "2012-06-01") & (games.Date < "2013-06-01")]
profit = sum(games_bet[games_bet.FTHG == games_bet.FTAG].BWD-1) - games_bet[games_bet.FTHG != games_bet.FTAG].shape[0]

# 2a: if odds of 1 bookie >> odds of other bookies
betmaxminratio = 1.7
betresult = "D"

bookies_result = np.array([s + betresult for s in bookies])
bookies_result = bookies_result[np.array([i in games.keys() for i in np.array([s + betresult for s in bookies])])]

games_bet = games[games[bookies_result].max(axis=1) > betmaxminratio*games[bookies_result].min(axis=1)]

if betresult == "H":
    profit = sum(games_bet[games_bet.FTHG > games_bet.FTAG][bookies_result].max(axis=1)-1) - games_bet[games_bet.FTHG <= games_bet.FTAG].shape[0]
    print(profit) 
elif betresult == "A":
    profit = sum(games_bet[games_bet.FTHG < games_bet.FTAG][bookies_result].max(axis=1)-1) - games_bet[games_bet.FTHG >= games_bet.FTAG].shape[0]
    print(profit)     
elif betresult == "D":
    profit = sum(games_bet[games_bet.FTHG == games_bet.FTAG][bookies_result].max(axis=1)-1) - games_bet[games_bet.FTHG != games_bet.FTAG].shape[0]
    print(profit) 
