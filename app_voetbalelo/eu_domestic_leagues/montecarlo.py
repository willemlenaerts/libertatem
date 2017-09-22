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

def montecarlo(data, country_data, simulations, hot = 1):
    import numpy as np
    import time
    import scipy.stats # For Poisson Distribution, numpy doesn't have it
    from app_voetbalelo.eu_domestic_leagues.game_to_team import game_to_team
    
    # data
    # # [0]:  List of 2 things
    # #       [0][0]: Team names of all teams in Jupiler Pro League
    # #       [0][1]: List of ELO/(SPI,off_rating,def_rating) rating for every team (after last played game)
    #
    # # [1]:  Array of size ((games played + games not played) x 8)
    # #       [1][:,0]: Home Team (As a number, alphabetically as in [0]
    # #       [1][:,1]: Away Team (As a number, alphabetically as in [0]
    # #       [1][:,2]: Home Team Goals
    # #       [1][:,3]: Away Team Goals
    # #       [1][:,4]: Game already played? (1 = yes, 0 = no)
    # #       [1][:,5]: Probability of Home Win
    # #       [1][:,6]: Probability of Tie
    # #       [1][:,7]: Probability of Away Win

    # Define some parameters to make code more readable
    total_games = len(data[1])  # All possible games in a season
    games_played = int(np.sum(data[1][:,4]))
    number_of_teams = len(data[0][0])
    # print(total_games)
    # print(np.sum(data[1][:,4]))
    # Initialize parameters for Monte Carlo Simulation
    # simulation = 0
    # simulation_matrix = np.zeros((total_games, simulations))

    # Monte Carlo Simulation
    # Simulate every game in a season, and this "simulations" times
    # This data can then be used to generate statistical output
    
    K = 40
    home_field_advantage = 84 # http://clubelo.com/HFA/ for belgium
    
    # Output is league ranking
    league_ranking = np.zeros((number_of_teams, simulations))
    
    for simulation in range(simulations):
        sim_start = time.time()
        games = np.copy(data[1])
        running_elo = np.copy(data[0][1])
        # for i in range(total_games):  # total games
        #     # Game played already?
        #     if int(games[i,4]) == 0:
        for i in range(games_played,total_games):       
            # Get Elo for both teams
            ht_elo = running_elo[int(games[i,0])]
            at_elo = running_elo[int(games[i,1])]
            
            # Calculate game score
            W_home_e = 1/(10**(-(ht_elo+home_field_advantage-at_elo)/400)+1)
            
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
            
            games[i,2] = np.random.choice(list(range(15)), p=chances_home_goal[0])
            games[i,3] = np.random.choice(list(range(15)), p=chances_away_goal[0])                
            games[i,4] = 1
            
            # Check if hot ==> update running_elo
            if hot == 1:
                # dElo = K × G x (W - We)
                if games[i,2] > games[i,3]: # Home Win
                    W_home = 1
                elif games[i,2] == games[i,3]: # Draw
                    W_home = 0.5
                elif games[i,2] < games[i,3]: # Away Win
                    W_home = 0

                # G
                if games[i,2] == games[i,3] or abs(games[i,2] - games[i,3]) == 1: # Draw or 1 goal difference
                    G = 1
                else:
                    if abs(games[i,2] - games[i,3]) == 2: # 2 goals difference
                        G = 3/2
                    else: # 3 or more goals difference
                        G = (11 + abs(games[i,2] - games[i,3]))/8
                
                running_elo[int(games[i,0])] += K * G * (W_home - W_home_e)
                running_elo[int(games[i,1])] -= K * G * (W_home - W_home_e)
        
        # All games simulated
        # Now calculate standing & rank according to rules of league
        gtt_input = [data[0][0],games]
        end_ranking = game_to_team([gtt_input],country_data)

        end_ranking = end_ranking[0][2]
        
        # Sort by ranking
        end_ranking = end_ranking[np.argsort(end_ranking[:, 8])]
        
        league_ranking[:, simulation] = end_ranking[:,9]

        sim_stop = time.time()
        if simulation%100 == 0:
            print(str(simulation) + "/" + str(simulations) + " simulations finished")
            print('Estimated Time Left: ' +  str(round((simulations-simulation)*(sim_stop - sim_start),0)) +  ' seconds')
  
    # Percentage chance to end up in certain league position
    # number_of_teams (ordered alphabetically) x number_of_teams (ranking)
    league_ranking_distribution = np.zeros((number_of_teams, number_of_teams))
    # league_ranking_distribution_elo = np.zeros((number_of_teams, number_of_teams))
    for i in range(number_of_teams):
        # Some teams may not get simulated on every position
        # For example a very good team might never simulate in last place
        # For that reason we have to check this and extend array if necessary (with 0 values)
        possible_positions_i = np.unique(np.where(league_ranking == i)[0])
        amount_per_position_i = np.bincount(np.where(league_ranking == i)[0]) / simulations
        # Remove zeros from amount_per_position_i
        amount_per_position_i = amount_per_position_i[amount_per_position_i != 0]
        for j in range(len(possible_positions_i)):
            league_ranking_distribution[i, possible_positions_i[j]] = amount_per_position_i[j]

    # Round all numbers to 2 digits behind comma
    data[0][1] = np.around(data[0][1],2)
    league_ranking_distribution = np.around(league_ranking_distribution,5)

    return list([data[0],league_ranking_distribution])