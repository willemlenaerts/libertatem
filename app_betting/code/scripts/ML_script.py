import pickle
import pandas as pd
import numpy as np
import time
import scipy
import sklearn
from app_betting.convert_odds import probability_to_decimal
from app_betting.profit import profit

# Initialize games
games = pickle.load(open("app_betting/result/games.p","rb"))
games = games[pd.notnull(games.FTHG)]
seasons = sorted(list(set(games.Season)))
competitions = sorted(list(set(games.Competition)))

# ML parameters
training_seasons = 6
seasons = sorted(list(set(games.Season)))[training_seasons:]
games = games[games.Season.isin(seasons)]
games = games[pd.notnull(games.FTHG)]
test_seasons = 3


