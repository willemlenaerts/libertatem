# Set sys.path to get access to all modules
import sys
import os.path
sys.path.append('/home/ubuntu/workspace/')

# Load functions
from app_voetbalelo.eu_domestic_leagues.get_games_data import get_games_data
from app_voetbalelo.eu_domestic_leagues.game_to_team import game_to_team
from app_voetbalelo.eu_domestic_leagues.ELO_algorithm import elo
from app_voetbalelo.eu_domestic_leagues.generate_json import generate_json

# Load packages
import json
import datetime
import ftplib
import pickle
import boto3

# Input is country_data
# CL/EL data: https://en.wikipedia.org/wiki/UEFA_coefficient#Current_ranking
country_data =  {
                "Belgium": {"url": "http://www.football-data.co.uk/mmz4281/1718/B1.csv",
                            "name": "Jupiler Pro League",
                            "degr_spots": 2,
                            "cl_spots": 2,
                            "el_spots": 2,
                            "ranking": ["Wins", "Goal Difference"]
                            },
                "England": {"url": "http://www.football-data.co.uk/mmz4281/1718/E0.csv",
                            "name": "Barclays Premier League",
                            "degr_spots": 3,
                            "cl_spots": 4,
                            "el_spots": 1,
                            "ranking": [ "Goal Difference", "Wins"]
                            },
                "Germany": {"url": "http://www.football-data.co.uk/mmz4281/1718/D1.csv",
                            "name": "Bundesliga",
                            "degr_spots": 2,
                            "cl_spots": 4,
                            "el_spots": 2,
                            "ranking": [ "Goal Difference", "Wins"]
                            },
                "Italy": {"url": "http://www.football-data.co.uk/mmz4281/1718/I1.csv",
                            "name": "Serie A",
                            "degr_spots": 3,
                            "cl_spots": 3,
                            "el_spots": 2,
                            "ranking": [ "Goal Difference", "Wins"]
                            },
                "Spain": {"url": "http://www.football-data.co.uk/mmz4281/1718/SP1.csv",
                            "name": "Liga BBVA",
                            "degr_spots": 3,
                            "cl_spots": 4,
                            "el_spots": 2,
                            "ranking": [ "Goal Difference", "Wins"]
                            },
                "France": {"url": "http://www.football-data.co.uk/mmz4281/1718/F1.csv",
                            "name": "Ligue 1",
                            "degr_spots": 3,
                            "cl_spots": 2,
                            "el_spots": 1,
                            "ranking": [ "Goal Difference", "Wins"]
                            },
                "Netherlands": {"url": "http://www.football-data.co.uk/mmz4281/1718/N1.csv",
                            "name": "Eredivisie",
                            "degr_spots": 2,
                            "cl_spots": 2,
                            "el_spots": 2,
                            "ranking": [ "Goal Difference", "Wins"]
                            },
                "Portugal": {"url": "http://www.football-data.co.uk/mmz4281/1718/P1.csv",
                            "name": "Primeira Liga",
                            "degr_spots": 2,
                            "cl_spots": 3,
                            "el_spots": 2,
                            "ranking": [ "Goal Difference", "Wins"]
                            },
                "Turkey": {"url": "http://www.football-data.co.uk/mmz4281/1718/T1.csv",
                            "name": "Futbol Ligi 1",
                            "degr_spots": 2,
                            "cl_spots": 3,
                            "el_spots": 2,
                            "ranking": [ "Goal Difference", "Wins"]
                            }
                }

################################################################################
# Parameters
# How many seasons to take into account for Elo algorithm?
number_of_seasons = 2

# How many simulations?
simulations = 1000

# Change Elo of teams while simulating? (hot = 1)
# Or fix on last known elo? (hot = 0)
hot = 1

# PI parameters
pi_learning_rates = pickle.load(open("app_betting/result/pi_learning_rates.p","rb"))
################################################################################

data = dict()
for country in country_data.keys():
    print("####################################################################")
    print("####################################################################")
    print(country)
    
    ################################################################################
    # 1. Get Games Data
    ################################################################################
    game_data_seasons = get_games_data(country, country_data[country],number_of_seasons)
    
    # game_data[0] is data from current season
    # game_data[0 + 1:number_of_seasons] is game data from previous seasons
    ################################################################################
    # 2. Convert Games Data to Team Data (standings), only for current season
    ################################################################################
    team_data_seasons = game_to_team(game_data_seasons,country_data[country])
    
    ################################################################################
    # 3. ELO Algorithm (including Montecarlo)
    ################################################################################
    result_seasons = elo(team_data_seasons,country_data[country], hot, simulations,number_of_seasons)
    
    ################################################################################
    # 4. Produce json files for Blog
    ################################################################################
    data[country] = generate_json(country, result_seasons)
    
    data[country]["degr_spots"] = country_data[country]["degr_spots"]
    data[country]["el_spots"] = country_data[country]["el_spots"]
    data[country]["cl_spots"] = country_data[country]["cl_spots"]
    data[country]["name"] = country_data[country]["name"]
    
    json.dump(data,open("app_voetbalelo/eu_domestic_leagues/result/data.json","w"))
    
# # Write to FTP site
# session = ftplib.FTP('ftp.sway-blog.be','sway-blog.be','Will0870')
# session.cwd('/www/data/elo-domestic-leagues')

# # Open data as JSON buffered (only way ftplib works)
# data = open("app_voetbalelo/eu_domestic_leagues/result/data.json","rb") # file to send
# session.storbinary('STOR data.json', data)     # send the file

# # Create dict with last update date
# # Save as json and load buffered
# last_update = {"date": datetime.datetime.now().strftime("%d/%m/%Y")}
# json.dump(last_update,open("app_voetbalelo/eu_domestic_leagues/result/last_update.json","w"))
# last_update = open("app_voetbalelo/eu_domestic_leagues/result/last_update.json","rb")
# session.storbinary('STOR date.json', last_update)

# session.quit()

# Upload to Amazon S3 Bucket
session = boto3.Session(region_name='eu-central-1',aws_access_key_id='AKIAIOW6REVSI6EASEIA',aws_secret_access_key='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')
s3 = session.resource('s3')
s3.Object('swayblog', 'eu_domestic_leagues/data.json').put(Body=open("app_voetbalelo/eu_domestic_leagues/result/data.json","rb"),ACL='public-read')

last_update = {"date": datetime.datetime.now().strftime("%d/%m/%Y")}
json.dump(last_update,open("app_voetbalelo/eu_domestic_leagues/result/last_update.json","w"))
s3.Object('swayblog', 'eu_domestic_leagues/date.json').put(Body=open("app_voetbalelo/eu_domestic_leagues/result/last_update.json","rb"),ACL='public-read')