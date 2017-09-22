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

# Get Input data
games = get_games_data()

simulations = 10

print("########################################")
print("Uefa Euro 2016 Algorithm")
print("########################################")
    
# Initialize output
team_data = dict()
group_data = dict()

# Expand games data with elo data
print("Get Elo Data from clubelo.com")
games = expand_elo(games)
 
# Generate standing and rank it correctly according to the UEFA tiebreaking procedure
print("Generate Group Standing and Rank according to Uefa rules")
standing = make_standing(games)
standing = rank(standing, games)

import numpy as np
import pandas as pd
import time
import random
import pulp
    
import scipy.stats # For Poisson Distribution, numpy doesn't have it
from app_voetbalelo.uefa_euro2016.expand_elo import expand_elo
from app_voetbalelo.uefa_euro2016.game_to_team import make_standing, rank, round_of_sixteen, quarterfinals, semifinals, final

games = games.sort_index()

output = dict()

#################
#################
#################
output_per_games = dict()
games_numbers = list(games.Game)
for game_numbers in games_numbers:
    output_per_games[game_numbers] = dict()
    output_per_games[game_numbers]["HomeTeam"] = list()
    output_per_games[game_numbers]["AwayTeam"] = list()
    
#################
#################
#################    

countries = list(games[~games.Group.str.contains("Final")].HomeTeam) + list(games[~games.Group.str.contains("Final")].AwayTeam)
countries = sorted(list(set(countries)))

for country in countries:
    # 4th - 3th - 2th - 1st - 1/8 win - 1/4 win - 1/2 win - Final win
    output[country] = np.zeros((1,8))

# How many group games are played
group_games = len(games[games.Group.str.contains("Group")])
group_games_played = len(games[games.Group.str.contains("Group")].FTHG.dropna())

for simulation in range(simulations):
    start = time.time()
    if simulation == 0:
        print("Starting Montecarlo Simulation ... Calculating Expected Time")
    elif simulation == simulations - 1:
        print("Simulation Finished")

    # Simulate Rest of Games
    games_simulated = games.copy(deep=True)
    
    HomeTeam = games_simulated.HomeTeam.values
    HomeElo = games_simulated.HomeElo.values
    AwayTeam = games_simulated.AwayTeam.values
    AwayElo = games_simulated.AwayElo.values
    Group = games_simulated.Group.values

    FTHG = games_simulated.FTHG.values
    FTAG = games_simulated.FTAG.values        
    
    # First GROUP GAMES
    if group_games_played != group_games:
        # Loop through all games
        for i in range(len(games_simulated)):
            # Check if group game and game not played yet
            if ("Group" in Group[i]) and (np.isnan(FTHG[i])):
                # There's only Home Field Advantage for France
                if HomeElo[i] == "France":
                    home_field_advantage = 80
                elif AwayElo[i] == "France":
                    home_field_advantage = -80
                else:
                    home_field_advantage = 0
                
                # ELO calculate expected goals for Home and Away Team
                W_home_e = 1/(10**(-(HomeElo[i]+home_field_advantage-AwayElo[i])/400)+1)
                
                # Expected Goals for Home country
                if W_home_e < 0.5:
                    home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                else:
                    home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
            
                # Expected Goals for the Away country:
                if W_home_e < 0.8:
                    away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
                else:
                    away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3
                
                # Simulate FTHG and FTAG
                chances_home_goal = np.zeros((1,15))
                chances_away_goal = np.zeros((1,15))
                for goals in range(15):
                    chances_home_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,home_goals)
                    chances_away_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,away_goals)
                
                # Make chances sum to 1 (we ignore more than 14 goals)
                chances_home_goal /=chances_home_goal.sum()
                chances_away_goal /= chances_away_goal.sum()
                
                games_simulated.loc[games_simulated.index[i],"FTHG"] = np.random.choice(list(range(15)), p=chances_home_goal[0])
                games_simulated.loc[games_simulated.index[i],"FTAG"] = np.random.choice(list(range(15)), p=chances_away_goal[0])
                FTHG[i] = np.random.choice(list(range(15)), p=chances_home_goal[0])
                FTAG[i] = np.random.choice(list(range(15)), p=chances_away_goal[0])
            
    # Make Standing and Rank 
    standing = rank(make_standing(games_simulated),games_simulated)
    
    # Add to output
    for country in list(standing.Country):
        rank_int = int(standing[standing.Country == country].R)
       # 4th - 3th - 2th - 1st - 1/8 win - 1/4 win - 1/2 win - Final win
        output[country][0,4-rank_int] += 1
    
    #############
    # 1/8 Finals
    #############
    games_simulated = round_of_sixteen(standing,games_simulated)
    games_simulated = expand_elo(games_simulated)
    
    # Recalibrate some data
    HomeTeam = games_simulated.HomeTeam.values
    HomeElo = games_simulated.HomeElo.values
    AwayTeam = games_simulated.AwayTeam.values
    AwayElo = games_simulated.AwayElo.values        
    
    for i in range(len(games_simulated)):
        # Check if group game and game not played yet
        if Group[i] == "1/8 Final":
            # There's only Home Field Advantage for France
            if HomeElo[i] == "France":
                home_field_advantage = 80
            elif AwayElo[i] == "France":
                home_field_advantage = -80
            else:
                home_field_advantage = 0
            
            # ELO calculate expected goals for Home and Away Team
            W_home_e = 1/(10**(-(HomeElo[i]+home_field_advantage-AwayElo[i])/400)+1)
            
            # Expected Goals for Home country
            if W_home_e < 0.5:
                home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
            else:
                home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
        
            # Expected Goals for the Away country:
            if W_home_e < 0.8:
                away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
            else:
                away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3
            
            # Simulate FTHG and FTAG
            chances_home_goal = np.zeros((1,15))
            chances_away_goal = np.zeros((1,15))
            for goals in range(15):
                chances_home_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,home_goals)
                chances_away_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,away_goals)
            
            # Make chances sum to 1 (we ignore more than 14 goals)
            chances_home_goal /=chances_home_goal.sum()
            chances_away_goal /= chances_away_goal.sum()
            
            games_simulated.loc[games_simulated.index[i],"FTHG"] = np.random.choice(list(range(15)), p=chances_home_goal[0])
            games_simulated.loc[games_simulated.index[i],"FTAG"] = np.random.choice(list(range(15)), p=chances_away_goal[0])
            FTHG[i] = np.random.choice(list(range(15)), p=chances_home_goal[0])
            FTAG[i] = np.random.choice(list(range(15)), p=chances_away_goal[0])        
    
    
    #############
    # Quarter Finals
    #############
    games_simulated = quarterfinals(games_simulated)
    games_simulated = expand_elo(games_simulated)
    
    # Recalibrate some data
    HomeTeam = games_simulated.HomeTeam.values
    HomeElo = games_simulated.HomeElo.values
    AwayTeam = games_simulated.AwayTeam.values
    AwayElo = games_simulated.AwayElo.values         
    
    for i in range(len(games_simulated)):
        # Check if group game and game not played yet
        if Group[i] == "Quarter Final":
            # There's only Home Field Advantage for France
            if HomeElo[i] == "France":
                home_field_advantage = 80
            elif AwayElo[i] == "France":
                home_field_advantage = -80
            else:
                home_field_advantage = 0
            
            # ELO calculate expected goals for Home and Away Team
            W_home_e = 1/(10**(-(HomeElo[i]+home_field_advantage-AwayElo[i])/400)+1)
            
            # Expected Goals for Home country
            if W_home_e < 0.5:
                home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
            else:
                home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
        
            # Expected Goals for the Away country:
            if W_home_e < 0.8:
                away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
            else:
                away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3
            
            # Simulate FTHG and FTAG
            chances_home_goal = np.zeros((1,15))
            chances_away_goal = np.zeros((1,15))
            for goals in range(15):
                chances_home_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,home_goals)
                chances_away_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,away_goals)
            
            # Make chances sum to 1 (we ignore more than 14 goals)
            chances_home_goal /=chances_home_goal.sum()
            chances_away_goal /= chances_away_goal.sum()
            
            games_simulated.loc[games_simulated.index[i],"FTHG"] = np.random.choice(list(range(15)), p=chances_home_goal[0])
            games_simulated.loc[games_simulated.index[i],"FTAG"] = np.random.choice(list(range(15)), p=chances_away_goal[0])
            FTHG[i] = np.random.choice(list(range(15)), p=chances_home_goal[0])
            FTAG[i] = np.random.choice(list(range(15)), p=chances_away_goal[0])          
    
    
    #############
    # Semi Finals
    #############
    games_simulated = semifinals(games_simulated)
    games_simulated = expand_elo(games_simulated)
    
    # Recalibrate some data
    HomeTeam = games_simulated.HomeTeam.values
    HomeElo = games_simulated.HomeElo.values
    AwayTeam = games_simulated.AwayTeam.values
    AwayElo = games_simulated.AwayElo.values         
    
    for i in range(len(games_simulated)):
        # Check if group game and game not played yet
        if Group[i] == "Semi Final":
            # There's only Home Field Advantage for France
            if HomeElo[i] == "France":
                home_field_advantage = 80
            elif AwayElo[i] == "France":
                home_field_advantage = -80
            else:
                home_field_advantage = 0
            
            # ELO calculate expected goals for Home and Away Team
            W_home_e = 1/(10**(-(HomeElo[i]+home_field_advantage-AwayElo[i])/400)+1)
            
            # Expected Goals for Home country
            if W_home_e < 0.5:
                home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
            else:
                home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
        
            # Expected Goals for the Away country:
            if W_home_e < 0.8:
                away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
            else:
                away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3
            
            # Simulate FTHG and FTAG
            chances_home_goal = np.zeros((1,15))
            chances_away_goal = np.zeros((1,15))
            for goals in range(15):
                chances_home_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,home_goals)
                chances_away_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,away_goals)
            
            # Make chances sum to 1 (we ignore more than 14 goals)
            chances_home_goal /=chances_home_goal.sum()
            chances_away_goal /= chances_away_goal.sum()
            
            games_simulated.loc[games_simulated.index[i],"FTHG"] = np.random.choice(list(range(15)), p=chances_home_goal[0])
            games_simulated.loc[games_simulated.index[i],"FTAG"] = np.random.choice(list(range(15)), p=chances_away_goal[0])
            FTHG[i] = np.random.choice(list(range(15)), p=chances_home_goal[0])
            FTAG[i] = np.random.choice(list(range(15)), p=chances_away_goal[0])           
    
    
    #############
    # Final
    #############
    games_simulated = final(games_simulated)
    games_simulated = expand_elo(games_simulated)
    
    # Recalibrate some data
    HomeTeam = games_simulated.HomeTeam.values
    HomeElo = games_simulated.HomeElo.values
    AwayTeam = games_simulated.AwayTeam.values
    AwayElo = games_simulated.AwayElo.values         
    
    for i in range(len(games_simulated)):
        # Check if group game and game not played yet
        if Group[i] == "Final":
            # There's only Home Field Advantage for France
            if HomeElo[i] == "France":
                home_field_advantage = 80
            elif AwayElo[i] == "France":
                home_field_advantage = -80
            else:
                home_field_advantage = 0
            
            # ELO calculate expected goals for Home and Away Team
            W_home_e = 1/(10**(-(HomeElo[i]+home_field_advantage-AwayElo[i])/400)+1)
            
            # Expected Goals for Home country
            if W_home_e < 0.5:
                home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
            else:
                home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
        
            # Expected Goals for the Away country:
            if W_home_e < 0.8:
                away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
            else:
                away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3
            
            # Simulate FTHG and FTAG
            chances_home_goal = np.zeros((1,15))
            chances_away_goal = np.zeros((1,15))
            for goals in range(15):
                chances_home_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,home_goals)
                chances_away_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,away_goals)
            
            # Make chances sum to 1 (we ignore more than 14 goals)
            chances_home_goal /=chances_home_goal.sum()
            chances_away_goal /= chances_away_goal.sum()
            
            games_simulated.loc[games_simulated.index[i],"FTHG"] = np.random.choice(list(range(15)), p=chances_home_goal[0])
            games_simulated.loc[games_simulated.index[i],"FTAG"] = np.random.choice(list(range(15)), p=chances_away_goal[0])
            FTHG[i] = np.random.choice(list(range(15)), p=chances_home_goal[0])
            FTAG[i] = np.random.choice(list(range(15)), p=chances_away_goal[0])      
            
    # Add 1/8, QF, SF, F to output
    # 4th - 3th - 2th - 1st - 1/8 win - 1/4 win - 1/2 win - Final win
    for country in list(standing.Country):
        quarter_finalists = list(games_simulated[(games_simulated.Group == "Quarter Final")].HomeTeam) + list(games_simulated[(games_simulated.Group == "Quarter Final")].AwayTeam) 
        quarter_finalists = list(set(quarter_finalists))
        if country in quarter_finalists:
            output[country][0,4] += 1
            
        semi_finalists = list(games_simulated[(games_simulated.Group == "Semi Final")].HomeTeam) + list(games_simulated[(games_simulated.Group == "Semi Final")].AwayTeam) 
        semi_finalists = list(set(semi_finalists))
        if country in semi_finalists:
            output[country][0,5] += 1
            
        finalists = list(games_simulated[(games_simulated.Group == "Final")].HomeTeam) + list(games_simulated[(games_simulated.Group == "Final")].AwayTeam) 
        finalists = list(set(finalists))
        if country in finalists:
            output[country][0,6] += 1
        
        if int(games_simulated[(games_simulated.Group == "Final")].FTHG.iloc[0]) > int(games_simulated[(games_simulated.Group == "Final")].FTAG.iloc[0]):
            winner = games_simulated[(games_simulated.Group == "Final")].HomeTeam.iloc[0]
        elif int(games_simulated[(games_simulated.Group == "Final")].FTHG.iloc[0]) < int(games_simulated[(games_simulated.Group == "Final")].FTAG.iloc[0]):
            winner = games_simulated[(games_simulated.Group == "Final")].AwayTeam.iloc[0]
        else:
            winner = random.choice([games_simulated[(games_simulated.Group == "Final")].HomeTeam.iloc[0],games_simulated[(games_simulated.Group == "Final")].AwayTeam.iloc[0]])

        if country == winner:
            output[country][0,7] += 1
    
    #################
    #################
    #################
    for game_numbers in games_numbers:
        output_per_games[game_numbers]["HomeTeam"].append(games_simulated[games_simulated.Game == game_numbers].HomeTeam.iloc[0])
        output_per_games[game_numbers]["AwayTeam"].append(games_simulated[games_simulated.Game == game_numbers].AwayTeam.iloc[0])
    #################
    #################
    #################  
    stop = time.time()
    if (simulation != 0) and (simulation%(simulations/10) == 0):
        print("Simulation " + str(simulation) + "/" + str(simulations) + " -- ET: " + str(round((stop-start)*(simulations-simulation)/60)) + " minutes")  
    
      
# Average
for country in output.keys():
    output[country] = output[country]/simulations