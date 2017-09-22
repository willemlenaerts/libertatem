__author__ = 'Exergos'
__project__ = 'SPI_JupilerProLeague'

########################################################################################################################
########################################################################################################################

#########################
# What does this file do?
#########################

# This file simulates outcomes for the Jupiler Pro League based on the SPI algorithm and the ELO algorithm
# It uses the a Monte Carlo Simulation

# Python 3.3 as Interpreter

######################
# What does it return?
######################
# A list of 2 things:
# [0]:  List of 2 things
#       [0][0]: Team names of all teams in Jupiler Pro League
#       [0][1]: Array of size (number of teams x 3)
#               [0][1][:,0]: SPI
#               [0][1][:,1]: Off Rating
#               [0][1][:,2]: Def Rating
# Or, in case of ELO simulation:
#       [0][1]: Array of size (number of teams x 1)
#               [0][1][:,0]: ELO

# [1]:  A size (number_of_teams x number_of_teams) matrix with the percentage chance of every team to end up in every
#       possible league position

########################################################################################################################
########################################################################################################################

def montecarlo(panda, simulations,league, ucl_third):
    import numpy as np
    import pandas as pd
    import time
    import random
    import pulp
    # test = 0
    if league == "uel":
        third_place_teams = ucl_third
        third_place_teams_list = []
        for t in third_place_teams[0]:
            third_place_teams_list += t
        third_place_teams_list = list(set(third_place_teams_list))
        third_place_teams_elo = ucl_third[1]
    elif league == "ucl":
        third_place_teams = list()
        third_place_teams_elo = list()
        
    import scipy.stats # For Poisson Distribution, numpy doesn't have it
    from app_voetbalelo.uefa_leagues.game_to_team import make_standing, rank
    from app_voetbalelo.uefa_leagues.montecarlo import teams_advancing
    output = dict()
    teams = sorted(list(set(panda.HomeTeam)))
    teams_league = sorted(list(set(panda.HomeTeam)))
    for team in teams:
        if league == "ucl":
            # 4th - 3th - 2th - 1st - 1/8 win - 1/4 win - 1/2 win - Final win
            output[team] = np.zeros((1,8))
        elif league == "uel":
            # 4th - 3th - 2th - 1st - 1/16 win - 1/8 win - 1/4 win - 1/2 win - Final win
            output[team] = np.zeros((1,9))
    stop = 0
    for simulation in range(simulations):
        start = time.time()
        if simulation == 0:
            print("Starting Montecarlo Simulation ... Calculating Expected Time")
        elif simulation == simulations - 1:
            print("Simulation Finished")
        elif simulation%(simulations/10) == 0:
            print("Simulation " + str(simulation) + "/" + str(simulations) + " -- ET: " + str(round((stop-start)*(simulations-simulation)/60)) + " minutes")
            
        # First, simulate rest of GROUP STAGE
        panda_simulated = panda.copy(deep=True)
        home_field_advantage = 100
        
        for i in range(len(panda_simulated)):
        
            # Simulate games not played
            if panda_simulated.FTHG.iloc[i] == "":
                # ELO calculate expected goals for Home and Away Team
                W_home_e = 1/(10**(-(panda_simulated.HomeElo.iloc[i]+home_field_advantage-panda_simulated.AwayElo.iloc[i])/400)+1)
                
                # Expected Goals for Home team
                if W_home_e < 0.5:
                    home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                else:
                    home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
            
                # Expected Goals for the Away team:
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
                
                panda_simulated.loc[panda_simulated.index[i],"FTHG"] = np.random.choice(list(range(15)), p=chances_home_goal[0])
                panda_simulated.loc[panda_simulated.index[i],"FTAG"] = np.random.choice(list(range(15)), p=chances_away_goal[0])
            
    
        # # Check if still in group phase or further
        # if "Group stage" in panda_simulated.TYPE.iloc[-1]:
        ##################
        # GROUP PHASE
        ##################
        # Calculate standing and rank
        standing = make_standing(panda_simulated)
        standing = rank(standing, panda_simulated)
      
        # Add positions to output
        for group in standing.keys():
            for i in range(len(standing[group][1])):
                team = standing[group][0][int(standing[group][1][i,0])]
                output[team][0,-i+3] += 1
        
        if league == "uel":
            #################
            # 1/16 FINAL
            #################
            if "Round of 32" not in list(set(panda_simulated.TYPE)):
                # Get First & Second placed teams from group phase and their last Elo rating
                first_place_teams = []
                second_place_teams = []
                round_of_32_elo = dict()
                for group in standing.keys():
                    first_place_teams.append(standing[group][0][int(standing[group][1][0,0])])
                    last_game = panda[(panda.HomeTeam == first_place_teams[-1])|(panda.AwayTeam == first_place_teams[-1])].sort("DATE").iloc[-1]
                    if last_game.HomeTeam == first_place_teams[-1]:
                        round_of_32_elo[first_place_teams[-1]] = last_game.HomeElo
                    else:
                        round_of_32_elo[first_place_teams[-1]] = last_game.AwayElo
            
                    second_place_teams.append(standing[group][0][int(standing[group][1][1,0])])
                    last_game = panda[(panda.HomeTeam == second_place_teams[-1])|(panda.AwayTeam == second_place_teams[-1])].sort("DATE").iloc[-1]
                    if last_game.HomeTeam == second_place_teams[-1]:
                        round_of_32_elo[second_place_teams[-1]] = last_game.HomeElo
                    else:
                        round_of_32_elo[second_place_teams[-1]] = last_game.AwayElo
                
                # ADD CHAMPIONS LEAGUE THIRD PLACE TEAMS TO TEAMS
                # 4 Third PLace finishers with most points go to top seed
                # 4 Third Place finishers with low points go to bottom seed
                # for now, just random
                for team in third_place_teams[simulation]:
                    if team not in output.keys():
                        output[team] = np.zeros((1,9))
                
                round_of_32_elo.update(third_place_teams_elo[simulation])
                for i in range(4):
                    first_place_teams.append(random.choice(third_place_teams[simulation]))
                    third_place_teams[simulation].pop(third_place_teams[simulation].index(first_place_teams[-1]))
                    
                    second_place_teams.append(random.choice(third_place_teams[simulation]))
                    third_place_teams[simulation].pop(third_place_teams[simulation].index(second_place_teams[-1]))                    
                    
                # Combine teams to create Round of 32  
                round_of_32 = []
                for i in range(16):
                    round_of_32.append([random.choice(first_place_teams),random.choice(second_place_teams)])
                    
                    # Remove selected teams from teams still to be selected
                    first_place_teams.pop(first_place_teams.index(round_of_32[-1][0]))
                    second_place_teams.pop(second_place_teams.index(round_of_32[-1][1]))
                    
                # ELO calculate expected goals for Home and Away Team
                # First placed team plays HOME game LAST
                round_of_16_teams = []
                for game in round_of_32:
                    ###########
                    # FIRST LEG
                    ###########
                    W_home_e = 1/(10**(-(round_of_32_elo[game[1]] + home_field_advantage - round_of_32_elo[game[0]])/400)+1)
                    
                    # Expected Goals for Home team
                    if W_home_e < 0.5:
                        home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                    else:
                        home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
                
                    # Expected Goals for the Away team:
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
                    
                    FTHG_first_leg = np.random.choice(list(range(15)), p=chances_home_goal[0])
                    FTAG_first_leg = np.random.choice(list(range(15)), p=chances_away_goal[0])
                    
                    ###########
                    # SECOND LEG
                    ###########
                    W_home_e = 1/(10**(-(round_of_32_elo[game[0]] + home_field_advantage - round_of_32_elo[game[1]])/400)+1)
                    
                    # Expected Goals for Home team
                    if W_home_e < 0.5:
                        home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                    else:
                        home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
                
                    # Expected Goals for the Away team:
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
                    
                    FTHG_second_leg = np.random.choice(list(range(15)), p=chances_home_goal[0])
                    FTAG_second_leg = np.random.choice(list(range(15)), p=chances_away_goal[0])
                    
                    # Who continues?
                    if FTHG_first_leg + FTAG_second_leg > FTAG_first_leg + FTHG_second_leg:
                        round_of_16_teams.append(game[1])
                    elif FTHG_first_leg + FTAG_second_leg < FTAG_first_leg + FTHG_second_leg:
                        round_of_16_teams.append(game[0])
                    else:
                        if FTAG_second_leg > FTAG_first_leg:
                            round_of_16_teams.append(game[1])
                        elif FTAG_second_leg < FTAG_first_leg:
                            round_of_16_teams.append(game[0])
                        else: 
                            # PENALTIES
                            round_of_16_teams.append(game[int(random.choice([0,1]))])
                            
                        # Round of 16 in pandas, so games are already simulated         
            else:
                round_of_32 = panda_simulated[panda_simulated.TYPE == "Round of 32"]
                round_of_32_elo = dict()
                for i in range(len(round_of_32)):
                    if round_of_32.iloc[i].HomeTeam in list(round_of_32_elo.keys()):
                        continue
                    else:
                        round_of_32_elo[round_of_32.iloc[i].HomeTeam] = round_of_32.iloc[i].HomeElo
                round_of_16_teams = teams_advancing(round_of_32)
                
            # Write to output
            for team in round_of_16_teams:
                output[team][0,4] += 1
        
        
        #################
        # 1/8 FINAL
        #################
        # Test:
        # if (int(output["Paris"][0,3]) != 0) & (test == 0):
        #     print(output)
        #     print(panda_simulated)
        #     print(make_standing(panda_simulated))
        #     print(standing)
        #     test += 1
        if league == "ucl":
            # Round of 16 not in pandas yet ==> Simulate games 
            if "Round of 16" not in list(set(panda_simulated.TYPE)):
                # Get First & Second placed teams from group phase and their last Elo rating
                first_place_teams = []
                second_place_teams = []
                third_place_teams.append([])
                third_place_teams_elo.append(dict())
                round_of_16_elo = dict()
                for group in standing.keys():
                    first_place_teams.append(standing[group][0][int(standing[group][1][0,0])])
                    last_game = panda[(panda.HomeTeam == first_place_teams[-1])|(panda.AwayTeam == first_place_teams[-1])].sort("DATE").iloc[-1]
                    if last_game.HomeTeam == first_place_teams[-1]:
                        round_of_16_elo[first_place_teams[-1]] = last_game.HomeElo
                    else:
                        round_of_16_elo[first_place_teams[-1]] = last_game.AwayElo
            
                    second_place_teams.append(standing[group][0][int(standing[group][1][1,0])])
                    last_game = panda[(panda.HomeTeam == second_place_teams[-1])|(panda.AwayTeam == second_place_teams[-1])].sort("DATE").iloc[-1]
                    if last_game.HomeTeam == second_place_teams[-1]:
                        round_of_16_elo[second_place_teams[-1]] = last_game.HomeElo
                    else:
                        round_of_16_elo[second_place_teams[-1]] = last_game.AwayElo
                    
                    third_place_teams[-1].append(standing[group][0][int(standing[group][1][2,0])])
                    last_game = panda[(panda.HomeTeam == third_place_teams[-1][-1])|(panda.AwayTeam == third_place_teams[-1][-1])].sort("DATE").iloc[-1]
                    if last_game.HomeTeam == third_place_teams[-1][-1]:
                        third_place_teams_elo[-1][third_place_teams[-1][-1]] = last_game.HomeElo
                    else:
                        third_place_teams_elo[-1][third_place_teams[-1][-1]] = last_game.AwayElo
            
                # Combine teams to create Round of 16  
                round_of_16 = []
                for i in range(8):
                    round_of_16.append([random.choice(first_place_teams),random.choice(second_place_teams)])
                    
                    # Remove selected teams from teams still to be selected
                    first_place_teams.pop(first_place_teams.index(round_of_16[-1][0]))
                    second_place_teams.pop(second_place_teams.index(round_of_16[-1][1]))     
                
                # ELO calculate expected goals for Home and Away Team
                # First placed team plays HOME game LAST
                round_of_8_teams = []
                for game in round_of_16:
                    ###########
                    # FIRST LEG
                    ###########
                    W_home_e = 1/(10**(-(round_of_16_elo[game[1]] + home_field_advantage - round_of_16_elo[game[0]])/400)+1)
                    
                    # Expected Goals for Home team
                    if W_home_e < 0.5:
                        home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                    else:
                        home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
                
                    # Expected Goals for the Away team:
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
                    
                    FTHG_first_leg = np.random.choice(list(range(15)), p=chances_home_goal[0])
                    FTAG_first_leg = np.random.choice(list(range(15)), p=chances_away_goal[0])
                    
                    ###########
                    # SECOND LEG
                    ###########
                    W_home_e = 1/(10**(-(round_of_16_elo[game[0]] + home_field_advantage - round_of_16_elo[game[1]])/400)+1)
                    
                    # Expected Goals for Home team
                    if W_home_e < 0.5:
                        home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                    else:
                        home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
                
                    # Expected Goals for the Away team:
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
                    
                    FTHG_second_leg = np.random.choice(list(range(15)), p=chances_home_goal[0])
                    FTAG_second_leg = np.random.choice(list(range(15)), p=chances_away_goal[0])
                    
                    # Who continues?
                    if FTHG_first_leg + FTAG_second_leg > FTAG_first_leg + FTHG_second_leg:
                        round_of_8_teams.append(game[1])
                    elif FTHG_first_leg + FTAG_second_leg < FTAG_first_leg + FTHG_second_leg:
                        round_of_8_teams.append(game[0])
                    else:
                        if FTAG_second_leg > FTAG_first_leg:
                            round_of_8_teams.append(game[1])
                        elif FTAG_second_leg < FTAG_first_leg:
                            round_of_8_teams.append(game[0])
                        else: 
                            # PENALTIES
                            round_of_8_teams.append(game[int(random.choice([0,1]))])                
            
            # Round of 16 in pandas, so games are already simulated         
            else:
                # Get third place teams
                third_place_teams.append([])
                third_place_teams_elo.append(dict())
                for group in standing.keys():
                    third_place_teams[-1].append(standing[group][0][int(standing[group][1][2,0])])
                    last_game = panda[(panda.HomeTeam == third_place_teams[-1][-1])|(panda.AwayTeam == third_place_teams[-1][-1])].sort("DATE").iloc[-1]
                    if last_game.HomeTeam == third_place_teams[-1][-1]:
                        third_place_teams_elo[-1][third_place_teams[-1][-1]] = last_game.HomeElo
                    else:
                        third_place_teams_elo[-1][third_place_teams[-1][-1]] = last_game.AwayElo 
                
                round_of_16 = panda_simulated[panda_simulated.TYPE == "Round of 16"]
                round_of_16_elo = dict()
                for i in range(len(round_of_16)):
                    if round_of_16.iloc[i].HomeTeam in list(round_of_16_elo.keys()):
                        continue
                    else:
                        round_of_16_elo[round_of_16.iloc[i].HomeTeam] = round_of_16.iloc[i].HomeElo
                round_of_8_teams = teams_advancing(round_of_16)
    
        elif league == "uel":
            if "Round of 16" not in list(set(panda_simulated.TYPE)):
                # Start with round_of_8_teams as input
                round_of_16_elo = round_of_32_elo
        
                # Combine teams to create Round of 8 
                round_of_16 = []
                for i in range(8):
                    round_of_16.append([random.choice(round_of_16_teams)])
                    round_of_16_teams.pop(round_of_16_teams.index(round_of_16[-1][0]))
                    
                    round_of_16[-1].append(random.choice(round_of_16_teams))
                    round_of_16_teams.pop(round_of_16_teams.index(round_of_16[-1][1]))
    
                    
                # ELO calculate expected goals for Home and Away Team
                # First placed team plays HOME game LAST
                round_of_8_teams = []
                for game in round_of_16:
                    ###########
                    # FIRST LEG
                    ###########
                    W_home_e = 1/(10**(-(round_of_16_elo[game[1]] + home_field_advantage - round_of_16_elo[game[0]])/400)+1)
                    
                    # Expected Goals for Home team
                    if W_home_e < 0.5:
                        home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                    else:
                        home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
                
                    # Expected Goals for the Away team:
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
                    
                    FTHG_first_leg = np.random.choice(list(range(15)), p=chances_home_goal[0])
                    FTAG_first_leg = np.random.choice(list(range(15)), p=chances_away_goal[0])
                    
                    ###########
                    # SECOND LEG
                    ###########
                    W_home_e = 1/(10**(-(round_of_16_elo[game[0]] + home_field_advantage - round_of_16_elo[game[1]])/400)+1)
                    
                    # Expected Goals for Home team
                    if W_home_e < 0.5:
                        home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                    else:
                        home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
                
                    # Expected Goals for the Away team:
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
                    
                    FTHG_second_leg = np.random.choice(list(range(15)), p=chances_home_goal[0])
                    FTAG_second_leg = np.random.choice(list(range(15)), p=chances_away_goal[0])
                    
                    # Who continues?
                    if FTHG_first_leg + FTAG_second_leg > FTAG_first_leg + FTHG_second_leg:
                        round_of_8_teams.append(game[1])
                    elif FTHG_first_leg + FTAG_second_leg < FTAG_first_leg + FTHG_second_leg:
                        round_of_8_teams.append(game[0])
                    else:
                        if FTAG_second_leg > FTAG_first_leg:
                            round_of_8_teams.append(game[1])
                        elif FTAG_second_leg < FTAG_first_leg:
                            round_of_8_teams.append(game[0])
                        else: 
                            # PENALTIES
                            round_of_8_teams.append(game[int(random.choice([0,1]))])
                    
    
            # Round of 16 in pandas, so games are already simulated         
            else:
                round_of_16 = panda_simulated[panda_simulated.TYPE == "Round of 16"]
                round_of_16_elo = dict()
                for i in range(len(round_of_16)):
                    if round_of_16.iloc[i].HomeTeam in list(round_of_16_elo.keys()):
                        continue
                    else:
                        round_of_16_elo[round_of_16.iloc[i].HomeTeam] = round_of_16.iloc[i].HomeElo
                round_of_8_teams = teams_advancing(round_of_16)
                
        # Write to output
        for team in round_of_8_teams:
            if league == "ucl":
                output[team][0,4] += 1
            elif league == "uel":
                output[team][0,5] += 1
    
        #################
        # 1/4 FINAL
        #################
        if "Quarter" not in list(set(panda_simulated.TYPE)):
            # Start with round_of_8_teams as input
            round_of_8_elo = round_of_16_elo
            
            # Combine teams to create Round of 8 
            round_of_8 = []
            for i in range(4):
                round_of_8.append([random.choice(round_of_8_teams)])
                round_of_8_teams.pop(round_of_8_teams.index(round_of_8[-1][0]))
                
                round_of_8[-1].append(random.choice(round_of_8_teams))
                round_of_8_teams.pop(round_of_8_teams.index(round_of_8[-1][1]))
                
            # ELO calculate expected goals for Home and Away Team
            # First placed team plays HOME game LAST
            round_of_4_teams = []
            for game in round_of_8:
                ###########
                # FIRST LEG
                ###########
                W_home_e = 1/(10**(-(round_of_8_elo[game[1]] + home_field_advantage - round_of_8_elo[game[0]])/400)+1)
                
                # Expected Goals for Home team
                if W_home_e < 0.5:
                    home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                else:
                    home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
            
                # Expected Goals for the Away team:
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
                
                FTHG_first_leg = np.random.choice(list(range(15)), p=chances_home_goal[0])
                FTAG_first_leg = np.random.choice(list(range(15)), p=chances_away_goal[0])
                
                ###########
                # SECOND LEG
                ###########
                W_home_e = 1/(10**(-(round_of_8_elo[game[0]] + home_field_advantage - round_of_8_elo[game[1]])/400)+1)
                
                # Expected Goals for Home team
                if W_home_e < 0.5:
                    home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                else:
                    home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
            
                # Expected Goals for the Away team:
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
                
                FTHG_second_leg = np.random.choice(list(range(15)), p=chances_home_goal[0])
                FTAG_second_leg = np.random.choice(list(range(15)), p=chances_away_goal[0])
                
                # Who continues?
                if FTHG_first_leg + FTAG_second_leg > FTAG_first_leg + FTHG_second_leg:
                    round_of_4_teams.append(game[1])
                elif FTHG_first_leg + FTAG_second_leg < FTAG_first_leg + FTHG_second_leg:
                    round_of_4_teams.append(game[0])
                else:
                    if FTAG_second_leg > FTAG_first_leg:
                        round_of_4_teams.append(game[1])
                    elif FTAG_second_leg < FTAG_first_leg:
                        round_of_4_teams.append(game[0])
                    else: 
                        # PENALTIES
                        round_of_4_teams.append(game[int(random.choice([0,1]))])
                        
        else:
            round_of_8 = panda_simulated[panda_simulated.TYPE == "Quarter-finals"]
            round_of_8_elo = dict()
            for i in range(len(round_of_8)):
                if round_of_8.iloc[i].HomeTeam in list(round_of_8_elo.keys()):
                    continue
                else:
                    round_of_8_elo[round_of_8.iloc[i].HomeTeam] = round_of_8.iloc[i].HomeElo
            round_of_4_teams = teams_advancing(round_of_8)
                    
        # Write to output
        for team in round_of_4_teams:
            if league == "ucl":
                output[team][0,5] += 1
            elif league == "uel":
                output[team][0,6] += 1        
            
        #################
        # 1/2 FINAL
        #################
        if "Semi" not in list(set(panda_simulated.TYPE)):
            # Start with round_of_8_teams as input
            round_of_4_elo = round_of_8_elo
            
            # Combine teams to create Round of 8 
            round_of_4 = []
            for i in range(2):
                round_of_4.append([random.choice(round_of_4_teams)])
                round_of_4_teams.pop(round_of_4_teams.index(round_of_4[-1][0]))
                
                round_of_4[-1].append(random.choice(round_of_4_teams))
                round_of_4_teams.pop(round_of_4_teams.index(round_of_4[-1][1]))
                
            # ELO calculate expected goals for Home and Away Team
            # First placed team plays HOME game LAST
            final_teams = []
            for game in round_of_4:
                ###########
                # FIRST LEG
                ###########
                W_home_e = 1/(10**(-(round_of_4_elo[game[1]] + home_field_advantage - round_of_4_elo[game[0]])/400)+1)
                
                # Expected Goals for Home team
                if W_home_e < 0.5:
                    home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                else:
                    home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
            
                # Expected Goals for the Away team:
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
                
                FTHG_first_leg = np.random.choice(list(range(15)), p=chances_home_goal[0])
                FTAG_first_leg = np.random.choice(list(range(15)), p=chances_away_goal[0])
                
                ###########
                # SECOND LEG
                ###########
                W_home_e = 1/(10**(-(round_of_4_elo[game[0]] + home_field_advantage - round_of_4_elo[game[1]])/400)+1)
                
                # Expected Goals for Home team
                if W_home_e < 0.5:
                    home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                else:
                    home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
            
                # Expected Goals for the Away team:
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
                
                FTHG_second_leg = np.random.choice(list(range(15)), p=chances_home_goal[0])
                FTAG_second_leg = np.random.choice(list(range(15)), p=chances_away_goal[0])
                
                # Who continues?
                if FTHG_first_leg + FTAG_second_leg > FTAG_first_leg + FTHG_second_leg:
                    final_teams.append(game[1])
                elif FTHG_first_leg + FTAG_second_leg < FTAG_first_leg + FTHG_second_leg:
                    final_teams.append(game[0])
                else:
                    if FTAG_second_leg > FTAG_first_leg:
                        final_teams.append(game[1])
                    elif FTAG_second_leg < FTAG_first_leg:
                        final_teams.append(game[0])
                    else: 
                        # PENALTIES
                        final_teams.append(game[int(random.choice([0,1]))])
        
        else:
            round_of_4 = panda_simulated[panda_simulated.TYPE == "Semi-finals"]
            round_of_4_elo = dict()
            for i in range(len(round_of_4)):
                if round_of_4.iloc[i].HomeTeam in list(round_of_4_elo.keys()):
                    continue
                else:
                    round_of_4_elo[round_of_4.iloc[i].HomeTeam] = round_of_4.iloc[i].HomeElo
            final_teams = teams_advancing(round_of_4)            
                        
                    
        # Write to output
        for team in final_teams:
            if league == "ucl":
                output[team][0,6] += 1
            elif league == "uel":
                output[team][0,7] += 1   
            
        #################
        # FINAL
        #################
        if "Final" not in list(set(panda_simulated.TYPE)):
            # Start with round_of_8_teams as input
            final_elo = round_of_4_elo
            
            # Combine teams to create Round of 8 
            final = []
            for i in range(1):
                final.append([random.choice(final_teams)])
                final_teams.pop(final_teams.index(final[-1][0]))
                
                final[-1].append(random.choice(final_teams))
                final_teams.pop(final_teams.index(final[-1][1]))
                
            # ELO calculate expected goals for Home and Away Team
            # First placed team plays HOME game LAST
            winner = []
            for game in final:
                ###########
                # FIRST LEG
                ###########
                # NO home_field_advantage in final
                home_field_advantage = 0 
                
                W_home_e = 1/(10**(-(final_elo[game[1]] + home_field_advantage - final_elo[game[0]])/400)+1)
                
                # Expected Goals for Home team
                if W_home_e < 0.5:
                    home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                else:
                    home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
            
                # Expected Goals for the Away team:
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
                
                FTHG = np.random.choice(list(range(15)), p=chances_home_goal[0])
                FTAG = np.random.choice(list(range(15)), p=chances_away_goal[0])
    
                
                # Who wins?
                if FTHG > FTAG:
                    winner.append(game[1])
                elif FTHG < FTAG:
                    winner.append(game[0])
                else:
                    winner.append(game[int(random.choice([0,1]))])
        else:
            final = panda_simulated[panda_simulated.TYPE == "Final"]
            final_elo = dict()
            for i in range(len(final)):
                if final.iloc[i].HomeTeam in list(final_elo.keys()):
                    continue
                else:
                    final_elo[final.iloc[i].HomeTeam] = final.iloc[i].HomeElo
            winner = teams_advancing(final)                
        # Write to output
        for team in winner:
            if league == "ucl":
                output[team][0,7] += 1
            elif league == "uel":
                output[team][0,8] += 1 
        
        # Timing
        stop = time.time()
                
    # Average
    for team in output.keys():
        output[team] = output[team]/simulations

    ##############################################################################
    # Make output all integers and add to 100%
    ##############################################################################
    model = pulp.LpProblem("JPL Problem", pulp.LpMinimize)
    
    variable_names = []
    teams = list(output.keys())
    lowBound_dict = dict()
    upBound_dict =  dict()
    # Voor elk team
    for i in range(len(teams)):
        # Elke mogelijke eindklassering
        for j in range(len(output[teams[i]][0])):
            # if teams[i] in teams_league:
            variable_names.append(str(i) + "_" + str(j))
            
            if league == "uel":
                if (teams[i] in third_place_teams_list) and (j<4):
                    lowBound_dict[str(i) + "_" + str(j)] = 0.0
                    upBound_dict[str(i) + "_" + str(j)] = 0.0
                    continue
                
            lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(1000*output[teams[i]][0][j]))
            upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(1000*output[teams[i]][0][j])) 
            # if 100*output[teams[i]][0][j] >= 0.5:
            #     # 1% Meer of minder mag dan
            #     lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*output[teams[i]][0][j]))
            #     upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(100*output[teams[i]][0][j]))                   
            # else:
            #     # 0% fixed
            #     lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*output[teams[i]][0][j]))
            #     upBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*output[teams[i]][0][j]))  
    
    variables = pulp.LpVariable.dict("variable_%s", variable_names, lowBound = 0, upBound = 1000, cat = pulp.LpInteger)
    
    # Ax=B
    # Sum of Group Phase places 1-4 IN group
    zero = len(output[teams[0]][0])*[0.0]
    one = 4*[1.0] + (len(output[teams[0]][0])-4)*[0.0]
    # if league == "uel":
    #     one_uel = len(output[teams[0]][0])*[0.0]
    equality = []
    for variable_names_i in range(len(teams)):
        if teams[variable_names_i] in teams_league:
            equality_vector = variable_names_i*zero + one + (len(teams)-variable_names_i-1)*zero
            equality.append(dict(zip(variable_names,equality_vector)))
            
            if league == "uel":
                if teams[variable_names_i] in third_place_teams_list:
                    model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 0.0
                else:
                    model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 1000.0
            else:
                model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 1000.0
        # else:
        #     # For third place UCL teams in UEL (sum of group phase == 0)
        #     equality_vector = variable_names_i*zero + one_uel + (len(teams)-variable_names_i-1)*zero
        #     equality.append(dict(zip(variable_names,equality_vector)))
        #     model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 0.0
        
    # Ax=B
    # Sum of Group Phase places 1-4 BETWEEN groups
    fourth = [1.0] + (len(output[teams[0]][0])-1)*[0.0]
    third = [0.0,1.0] + (len(output[teams[0]][0])-2)*[0.0]
    second = [0.0,0.0,1.0] + (len(output[teams[0]][0])-3)*[0.0]
    first = [0.0,0.0,0.0,1.0] + (len(output[teams[0]][0])-4)*[0.0]
    equality = []
    for group in standing.keys():
        equality_vector_fourth = len(teams)*zero
        equality_vector_third = len(teams)*zero
        equality_vector_second = len(teams)*zero
        equality_vector_first = len(teams)*zero
        
        for variable_names_i in range(len(teams)):
            if teams[variable_names_i] in standing[group][0]:
                len_output = len(output[teams[variable_names_i]][0])
                equality_vector_fourth[variable_names_i*len_output:(variable_names_i*len_output+len_output)] = fourth
                equality_vector_third[variable_names_i*len_output:(variable_names_i*len_output+len_output)] = third
                equality_vector_second[variable_names_i*len_output:(variable_names_i*len_output+len_output)] = second
                equality_vector_first[variable_names_i*len_output:(variable_names_i*len_output+len_output)] = first
    
        equality.append(dict(zip(variable_names,equality_vector_fourth)))
        model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 1000.0        
    
        equality.append(dict(zip(variable_names,equality_vector_third)))
        model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 1000.0
        
        equality.append(dict(zip(variable_names,equality_vector_second)))
        model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 1000.0
        
        equality.append(dict(zip(variable_names,equality_vector_first)))
        model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 1000.0
    
    # Knockout phase
    zero = len(output[teams[0]][0])*[0.0]
    one = 4*[0.0] + [1.0] + (len(output[teams[0]][0])-5)*[0.0]
    if "Round of 32" in list(set(panda.TYPE)):
        teams_checked = []
        if type(round_of_32) == list:
            teams_checked = round_of_32
        else:
            for i in range(len(round_of_32)):
                ht = round_of_32.iloc[i].HomeTeam
                at = round_of_32.iloc[i].AwayTeam
                if [ht,at] in teams_checked or [at,ht] in teams_checked:
                    continue
                else:
                    teams_checked.append([ht,at])
                
        equality = []
        for game in teams_checked:
            equality_vector = len(teams)*zero
            index_ht = teams.index(game[0])
            index_at = teams.index(game[1])
            equality_vector[index_ht*len(zero):(index_ht+1)*len(zero)] = one
            equality_vector[index_at*len(zero):(index_at+1)*len(zero)] = one
        
            equality.append(dict(zip(variable_names,equality_vector)))                    
            model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 1000.0     

    zero = len(output[teams[0]][0])*[0.0]
    if league == "uel":
        one = 5*[0.0] + [1.0] + (len(output[teams[0]][0])-6)*[0.0]
    elif league == "ucl":
        one = 4*[0.0] + [1.0] + (len(output[teams[0]][0])-5)*[0.0]
    if "Round of 16" in list(set(panda.TYPE)):
        teams_checked = []
        if type(round_of_16) == list:
            teams_checked = round_of_16
        else:
            for i in range(len(round_of_16)):
                ht = round_of_16.iloc[i].HomeTeam
                at = round_of_16.iloc[i].AwayTeam
                if [ht,at] in teams_checked or [at,ht] in teams_checked:
                    continue
                else:
                    teams_checked.append([ht,at])
                
        equality = []
        for game in teams_checked:
            equality_vector = len(teams)*zero
            index_ht = teams.index(game[0])
            index_at = teams.index(game[1])
            equality_vector[index_ht*len(zero):(index_ht+1)*len(zero)] = one
            equality_vector[index_at*len(zero):(index_at+1)*len(zero)] = one
        
            equality.append(dict(zip(variable_names,equality_vector)))                    
            model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 1000.0         
            
    zero = len(output[teams[0]][0])*[0.0]
    if league == "uel":
        one = 6*[0.0] + [1.0] + (len(output[teams[0]][0])-7)*[0.0]
    elif league == "ucl":
        one = 5*[0.0] + [1.0] + (len(output[teams[0]][0])-6)*[0.0]
    if "Quarter-finals" in list(set(panda.TYPE)):
        teams_checked = []
        if type(round_of_8) == list:
            teams_checked = round_of_8
        else:
            for i in range(len(round_of_8)):
                ht = round_of_8.iloc[i].HomeTeam
                at = round_of_8.iloc[i].AwayTeam
                if [ht,at] in teams_checked or [at,ht] in teams_checked:
                    continue
                else:
                    teams_checked.append([ht,at])
                
        equality = []
        for game in teams_checked:
            equality_vector = len(teams)*zero
            index_ht = teams.index(game[0])
            index_at = teams.index(game[1])
            equality_vector[index_ht*len(zero):(index_ht+1)*len(zero)] = one
            equality_vector[index_at*len(zero):(index_at+1)*len(zero)] = one
        
            equality.append(dict(zip(variable_names,equality_vector)))                    
            model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 100.0                    
            
    zero = len(output[teams[0]][0])*[0.0]
    if league == "uel":
        one = 7*[0.0] + [1.0] + (len(output[teams[0]][0])-8)*[0.0]
    elif league == "ucl":
        one = 6*[0.0] + [1.0] + (len(output[teams[0]][0])-7)*[0.0]
    if "Semi-finals" in list(set(panda.TYPE)):
        teams_checked = []
        if type(round_of_4) == list:
            teams_checked = round_of_4
        else:
            for i in range(len(round_of_4)):
                ht = round_of_4.iloc[i].HomeTeam
                at = round_of_4.iloc[i].AwayTeam
                if [ht,at] in teams_checked or [at,ht] in teams_checked:
                    continue
                else:
                    teams_checked.append([ht,at])
                
        equality = []
        for game in teams_checked:
            equality_vector = len(teams)*zero
            index_ht = teams.index(game[0])
            index_at = teams.index(game[1])
            equality_vector[index_ht*len(zero):(index_ht+1)*len(zero)] = one
            equality_vector[index_at*len(zero):(index_at+1)*len(zero)] = one
        
            equality.append(dict(zip(variable_names,equality_vector)))                    
            model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 1000.0                    
            
    
    # Constraints sum for every position == 100
    # Win% sums to 100% for all teams
    equality = []   
    # for variable_names_i in range(len(teams)):
    equality_vector = len(teams)*((len(output[teams[0]][0])-1)*[0]+ [1])
    equality.append(dict(zip(variable_names,equality_vector)))
    
    for eq in equality:
        model += sum([eq[i]*variables[i] for i in variable_names]) == 1000.0
        
    # Constraints (ub,lb)
    for var in variable_names:
        model+= variables[var] >= lowBound_dict[var]
        model+= variables[var] <= upBound_dict[var]
    
    # solve and get result[0]
    model.solve()
    if model.solve() == -1:
        print("WARNING: Regular MIP Algorithm did not reach optimal point")
        
    
    output_int = dict()
    for i in range(len(teams)):
        output_int [teams[i]] = list()
        # Elke mogelijke eindklassering
        for j in range(len(output[teams[i]][0])):
            output_int[teams[i]].append(variables[str(i) + "_" + str(j)].value()/10)
    
    
    if league == "ucl":
        # print(output)
        # import json
        # json.dump(output,open("app_voetbalelo/uefa_leagues/data/test/output.json","w"))
        output = [output_int,third_place_teams,third_place_teams_elo]
    elif league == "uel":
        output = output_int

    return output
    
def teams_advancing(pandas):
    import pandas as pd
    import random
    
    teams = list(set(pandas.HomeTeam))
    teams_checked = []
    round_of_8_teams = []
    for team in teams:
        games = pandas[(pandas.HomeTeam == team) | (pandas.AwayTeam == team)]
        
        if list(set(games.HomeTeam))[0] in teams_checked or list(set(games.HomeTeam))[1] in teams_checked:
            continue
        else:
            teams_checked += list(set(games.HomeTeam))
        
        FTHG_first_leg = int(games.iloc[0].FTHG)
        FTAG_first_leg = int(games.iloc[0].FTAG)
        
        FTHG_second_leg = int(games.iloc[1].FTHG)
        FTAG_second_leg = int(games.iloc[1].FTAG)
        
        # Who continues?
        if FTHG_first_leg + FTAG_second_leg > FTAG_first_leg + FTHG_second_leg:
            round_of_8_teams.append(games.iloc[0].HomeTeam)
        elif FTHG_first_leg + FTAG_second_leg < FTAG_first_leg + FTHG_second_leg:
            round_of_8_teams.append(games.iloc[0].AwayTeam)
        else:
            if FTAG_second_leg > FTAG_first_leg:
                round_of_8_teams.append(games.iloc[1].AwayTeam)
            elif FTAG_second_leg < FTAG_first_leg:
                round_of_8_teams.append(games.iloc[0].AwayTeam)
            else: 
                # PENALTIES
                round_of_8_teams.append(games.iloc[int(random.choice([0,1]))].HomeTeam)
                
    return round_of_8_teams