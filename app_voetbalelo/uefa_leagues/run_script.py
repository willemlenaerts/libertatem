# Set sys.path to get access to all modules
import sys
import os.path
sys.path.append('/home/ubuntu/workspace/')

from app_voetbalelo.uefa_leagues.expand_elo import expand_elo
from app_voetbalelo.uefa_leagues.game_to_team import make_standing, rank
from app_voetbalelo.uefa_leagues.montecarlo import montecarlo
from app_voetbalelo.uefa_leagues.get_elo_data import get_elo_data
from app_voetbalelo.uefa_leagues.get_elo_team import get_elo_team
from app_voetbalelo.uefa_leagues.functions.ordered_set import ordered_set

import copy
import datetime
import json
import pickle
import ftplib
import boto3

# Get Input data
import pickle
games = pickle.load(open("app_voetbalelo/uefa_leagues/data/games.p","rb"))
leagues = ["ucl","uel"]
simulations = 50

team_data = dict()
group_data = dict()
knockout_round = dict()
for league in leagues:
    if league == "ucl":
        print("########################################")
        print("Uefa Champions League Algorithm")
        print("########################################")
    else:
        print("########################################")
        print("Uefa Europa League Algorithm")
        print("########################################")
        
    # Initialize output
    team_data[league] = dict()
    # group_data[league] = dict()
    
    # # Expand games data with elo data
    print("Get Elo Data from clubelo.com")
    panda = expand_elo(games[league])
     
    # Generate standing and rank it correctly according to the UEFA tiebreaking procedure
    print("Generate Group Standing and Rank according to Uefa rules")
    standing = make_standing(panda)
    standing = rank(standing, panda)
    
    # Montecarlo
    print("Montecarlo Algorithm")
    
    if league == "ucl":
        ucl_third = []
        output = montecarlo(panda,simulations,league,ucl_third)
        third_place_teams = output[1]
        third_place_teams_elo = output[2]
        output = output[0]
    elif league == "uel":
        ucl_third = [third_place_teams,third_place_teams_elo]
        output = montecarlo(panda,simulations,league,ucl_third)

    # Write json
    import numpy as np
    team_elo = get_elo_data(datetime.datetime.now())
    for team in output.keys():
        team_data[league][team] = dict()
        team_data[league][team]["odds"] = output[team]
        team_data[league][team]["elo"] = round(get_elo_team(team,team_elo))
        
        for group in standing.keys():
            if team in standing[group][0]:
                team_index = standing[group][0].index(team)
                team_data[league][team]["group"] = group.split(" ")[1]
                for i in range(len(standing[group][1].tolist())):
                    if int(standing[group][1].tolist()[i][0]) == team_index:
                        team_data[league][team]["ranking"] = i
                        team_data[league][team]["standing"] = standing[group][1].tolist()[i]
                        break
        
    # Knockout rounds
    knockout_round[league] = []
    knockout_rounds = ordered_set((panda[~panda.TYPE.str.contains("Group")].TYPE))
    for i in range(len(knockout_rounds)):
        knockout_round[league].append(dict())
        knockout_round[league][-1]["round"] = knockout_rounds[i]
        knockout_round[league][-1]["odds_index"] = 4+i
        knockout_round[league][-1]["games"] = []
        
        dummy = panda[panda.TYPE == knockout_rounds[i]]
        for i in range(len(dummy)):
            ht = dummy.iloc[i].HomeTeam
            at = dummy.iloc[i].AwayTeam
            if [ht,at] in knockout_round[league][-1]["games"] or [at,ht] in knockout_round[league][-1]["games"]:
                continue
            else:
                knockout_round[league][-1]["games"].append([ht,at])
    
json.dump(team_data,open("app_voetbalelo/uefa_leagues/result/team_data.json","w"))
teams = pickle.load(open("app_voetbalelo/uefa_leagues/data/teams.p","rb"))
json.dump(teams,open("app_voetbalelo/uefa_leagues/result/teams.json","w"))
json.dump(knockout_round,open("app_voetbalelo/uefa_leagues/result/knockout_round.json","w"))

# # Write to FTP site
# session = ftplib.FTP('ftp.sway-blog.be','sway-blog.be','Will0870')
# session.cwd('/www/data/elo-uefa-leagues')

# # Open data as JSON buffered (only way ftplib works)
# data = open("app_voetbalelo/uefa_leagues/result/team_data.json","rb") # file to send
# session.storbinary('STOR data.json', data)     # send the file
# data = open("app_voetbalelo/uefa_leagues/result/teams.json","rb") # file to send
# session.storbinary('STOR teams.json', data)     # send the file
# data = open("app_voetbalelo/uefa_leagues/result/knockout_round.json","rb") # file to send
# session.storbinary('STOR knockout_round.json', data)     # send the file
# # Create dict with last update date
# # Save as json and load buffered
# last_update = {"date": datetime.datetime.now().strftime("%d/%m/%Y")}
# json.dump(last_update,open("app_voetbalelo/uefa_leagues/result/last_update.json","w"))
# last_update = open("app_voetbalelo/uefa_leagues/result/last_update.json","rb")
# session.storbinary('STOR date.json', last_update)

# session.quit()

# Upload to Amazon S3 Bucket

session = boto3.Session(region_name='eu-central-1',aws_access_key_id='AKIAIOW6REVSI6EASEIA',aws_secret_access_key='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')
s3 = session.resource('s3')
s3.Object('swayblog', 'uefa_leagues/data.json').put(Body=open("app_voetbalelo/uefa_leagues/result/team_data.json","rb"),ACL='public-read')
s3.Object('swayblog', 'uefa_leagues/teams.json').put(Body=open("app_voetbalelo/uefa_leagues/result/teams.json","rb"),ACL='public-read')
s3.Object('swayblog', 'uefa_leagues/kockout_round.json').put(Body=open("app_voetbalelo/uefa_leagues/result/knockout_round.json","rb"),ACL='public-read')

last_update = {"date": datetime.datetime.now().strftime("%d/%m/%Y")}
json.dump(last_update,open("app_voetbalelo/uefa_leagues/result/last_update.json","w"))
s3.Object('swayblog', 'uefa_leagues/date.json').put(Body=open("app_voetbalelo/uefa_leagues/result/last_update.json","rb"),ACL='public-read')