from app_voetbalpi.eu_domestic_leagues.functions.get_games_data import get_games_data
from app_voetbalpi.eu_domestic_leagues.functions.game_to_team import make_standing, rank
from app_voetbalpi.eu_domestic_leagues.functions.rating_algorithms import elo,pi,get_pi_learning_rates, get_pi_probability_distribution
from app_voetbalpi.eu_domestic_leagues.functions.montecarlo import montecarlo
from app_voetbalpi.eu_domestic_leagues.functions.generate_json import generate_json
from app_voetbalpi.eu_domestic_leagues.functions.profit import profit

import pandas as pd
import pickle
import datetime
import ftplib

# Input is country_data
# CL/EL data: https://en.wikipedia.org/wiki/UEFA_coefficient#Current_ranking
country_data =  {
                # "Belgium": {"url": "http://www.football-data.co.uk/mmz4281/1516/B1.csv",
                #             "name": "Jupiler Pro League",
                #             "degr_spots": 2,
                #             "cl_spots": 2,
                #             "el_spots": 2,
                #             "ranking": ["PTS","W", "GD"]
                #             },
                "England": {"url": "http://www.football-data.co.uk/mmz4281/1516/E0.csv",
                            "name": "Barclays Premier League",
                            "degr_spots": 3,
                            "cl_spots": 4,
                            "el_spots": 1,
                            "ranking": ["PTS", "GD", "W"]
                            },
                "Germany": {"url": "http://www.football-data.co.uk/mmz4281/1516/D1.csv",
                            "name": "Bundesliga",
                            "degr_spots": 2,
                            "cl_spots": 4,
                            "el_spots": 2,
                            "ranking": ["PTS", "GD", "W"]
                            },
                "Italy": {"url": "http://www.football-data.co.uk/mmz4281/1516/I1.csv",
                            "name": "Serie A",
                            "degr_spots": 3,
                            "cl_spots": 3,
                            "el_spots": 2,
                            "ranking": ["PTS", "GD", "W"]
                            },
                "Spain": {"url": "http://www.football-data.co.uk/mmz4281/1516/SP1.csv",
                            "name": "Liga BBVA",
                            "degr_spots": 3,
                            "cl_spots": 4,
                            "el_spots": 2,
                            "ranking": ["PTS", "GD", "W"]
                            },
                "France": {"url": "http://www.football-data.co.uk/mmz4281/1516/F1.csv",
                            "name": "Ligue 1",
                            "degr_spots": 3,
                            "cl_spots": 2,
                            "el_spots": 1,
                            "ranking": ["PTS", "GD", "W"]
                            },
                "Netherlands": {"url": "http://www.football-data.co.uk/mmz4281/1516/N1.csv",
                            "name": "Eredivisie",
                            "degr_spots": 2,
                            "cl_spots": 2,
                            "el_spots": 2,
                            "ranking": ["PTS", "GD", "W"]
                            },
                "Portugal": {"url": "http://www.football-data.co.uk/mmz4281/1516/P1.csv",
                            "name": "Primeira Liga",
                            "degr_spots": 2,
                            "cl_spots": 3,
                            "el_spots": 2,
                            "ranking": ["PTS", "GD", "W"]
                            }
                # "Turkey": {"url": "http://www.football-data.co.uk/mmz4281/1516/T1.csv",
                #             "name": "Futbol Ligi 1",
                #             "degr_spots": 2,
                #             "cl_spots": 3,
                #             "el_spots": 2,
                #             "ranking": ["PTS", "GD", "W"]
                #             }
                }

################################################################################
# Parameters
# How many seasons to take into account for Pi algorithm?
number_of_seasons = 10
training_seasons = 5
calibrate_rating_algorithms = False
pi_learning_rates_rule = "Goal Difference" # "Goal Difference" or "Profit"
pi_learning_rates = pickle.load(open("app_voetbalpi/eu_domestic_leagues/data/input/pi_learning_rates.p","rb"))
pi_probability_distribution = pickle.load(open("app_voetbalpi/eu_domestic_leagues/data/input/pi_probability_distribution.p","rb"))

# Montecarlo
simulations = 10000
hot = True
################################################################################
# Calibrate Win,Draw,Loss probabilities based on deltaPi
if calibrate_rating_algorithms:
    # Get large games dataset
    games_training = pd.DataFrame()
    number_of_calibration_seasons = 15
    training_calibration_seasons = 5
    for country in country_data.keys():
        games_country = get_games_data(country, country_data[country],number_of_calibration_seasons)
        games_training = pd.concat([games_training,games_country])
    
    games_training = games_training.reset_index(drop=True)
    
    # Get Pi Learning Rates
    for country in country_data.keys():
        print("####################################################################")
        print("Training Learning Rates for Pi Rating System for " + country)
        pi_learning_rates = get_pi_learning_rates(games_training,country,training_calibration_seasons,rule=pi_learning_rates_rule)
        
    # Calculate probability distribution
    # First Add Pi Ratings
    games_training_pi = pd.DataFrame()
    for country in country_data.keys():
        games_training_country = games_training[games_training.Competition == country]
        l = pi_learning_rates[country][pi_learning_rates_rule]["l"] 
        g = pi_learning_rates[country][pi_learning_rates_rule]["g"] 
        games_training_country_pi = pi(games_training_country,l,g)
        games_training_pi = pd.concat([games_training_pi,games_training_country_pi])
    
    pi_probability_distribution = get_pi_probability_distribution(games_training_pi,training_calibration_seasons)

# Initialize Calculation
games = pd.DataFrame()
standing = pd.DataFrame()

for country in country_data.keys():
    print("####################################################################")
    print("####################################################################")
    print(country)
    
    ################################################################################
    # 1. Get Games Data & optionally, calculate parameters of Pi Rating Algorithms
    ################################################################################
    output = get_games_data(country, country_data[country],number_of_seasons)
    games_country = output[0]
    teams_country = output[1]
    
    ################################################################################
    # 2. Convert Games Data to Team Data (standings)
    ################################################################################
    standing_country = rank(make_standing(games_country), country_data[country])
    
    ################################################################################
    # 3. Run Team Rating Algorithms
    ################################################################################
    print("####################################################################")
    print("Pi Algorithm")
    l = pi_learning_rates[country][pi_learning_rates_rule]["l"] 
    g = pi_learning_rates[country][pi_learning_rates_rule]["g"] 
    games_country = pi(games_country,l,g,use_pi_probability_distribution = True)
    
    ################################################################################
    # 4. Run Montecarlo Analysis
    ################################################################################    
    montecarlo_country = montecarlo(games_country,country_data[country],l,g,simulations,hot)
    
    ################################################################################
    # 5. Combine for all countries
    ################################################################################     
    games = pd.concat([games,games_country])
    standing = pd.concat([standing,standing_country])
    
    ################################################################################
    # 5. Create json's for blog
    ################################################################################     
    generate_json(games_country,standing_country,montecarlo_country,country,country_data[country])
    
    
games = games.reset_index(drop=True)
standing = standing.reset_index(drop=True)

pickle.dump(games,open("app_voetbalpi/eu_domestic_leagues/data/output/games.p","wb"))
pickle.dump(standing,open("app_voetbalpi/eu_domestic_leagues/data/output/standing.p","wb"))