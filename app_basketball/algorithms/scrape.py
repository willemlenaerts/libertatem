import app_basketball.algorithms.bbref as bbref
import numpy as np

# Get player data
players = bbref.buildPlayerDictionary()
bbref.savePlayerDictionary(players, "app_basketball/data/input/all_players_soup.json")