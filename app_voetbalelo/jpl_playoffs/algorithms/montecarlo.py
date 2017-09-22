__author__ = 'Exergos'

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

def montecarlo(wedstrijden_gtt,simulations = 100):
    import numpy as np
    import time
    
    # Loop over all competitions
    competitions = ["rs","poi","poii_a","poii_b","poiii"]
    
    # Save output
    output = dict()
    
    for competition in competitions:
        print('Starting Montecarlo Simulation for ' + competition)
        # check to see if there are games still to be played in this competition
        # if int(np.sum(wedstrijden_gtt[competition][1][:,4],0)) == len(wedstrijden_gtt[competition][1]):
        #     continue
        # if int(np.sum(wedstrijden_gtt["rs"][1][:,4],0)) < len(wedstrijden_gtt["rs"][1]):
        #     if competition is not "rs":
        #         continue
        
        # Define some parameters to make code more readable
        # Define some parameters that will help with reading the code
        team_names = wedstrijden_gtt[competition][0][0]
        team_indices = wedstrijden_gtt[competition][0][1]
        number_of_teams = len(team_names)
        total_games = len(wedstrijden_gtt[competition][1])
        games_played = []
        for i in range(total_games):
            if wedstrijden_gtt[competition][1][i,4] == 1:
                games_played.append(i)
    
        # Initialize parameters for Monte Carlo Simulation
        simulation = 0
        simulation_matrix = np.zeros((total_games, simulations))
    
        # Monte Carlo Simulation
        # Simulate every game in a season, and this "simulations" times
        # This data can then be used to generate statistical output
    
        sim_start = time.time()
        while simulation < simulations:
            if simulation == 0:
                sim_start_iteration = time.time()
            for i in range(total_games):  # total games
                simulation_matrix[i, simulation] = np.random.choice([0, 1, 2], p=wedstrijden_gtt[competition][1][i, 6:9])
            if simulation == 0:
                sim_end_iteration = time.time()
                print('One Montecarlo Iteration finished in ' + str(round(sim_end_iteration - sim_start_iteration,4)) + " seconds")
                print('Expected time for full Montecarlo simulation is ' + str(round((sim_end_iteration - sim_start_iteration)*simulations,0)) + " seconds")    
            simulation += 1
        sim_end = time.time()
    
        print('Montecarlo Simulation finished for ' + competition + " in " + str(round(sim_end - sim_start,0)) + " seconds, taking " + str(simulations) + " simulations")
    
        # Adjust simulation_matrix for games already played (only if "actual" parameter = 1)!!
        # 0 for Home Win, 1 for Tie, 2 for Away Win
        simulation_matrix_regular = np.zeros((total_games, simulations))
        for i in range(total_games):
            if wedstrijden_gtt[competition][1][i,4] == 1:  # Game already played
                if wedstrijden_gtt[competition][1][i,2] > wedstrijden_gtt[competition][1][i,3]:  # Home Win
                    simulation_matrix_regular[i,:] = np.matrix(np.zeros(simulations))
                if wedstrijden_gtt[competition][1][i,2] == wedstrijden_gtt[competition][1][i,3]:  # Tie
                    simulation_matrix_regular[i,:] = np.matrix(np.ones(simulations))
                if wedstrijden_gtt[competition][1][i,2] < wedstrijden_gtt[competition][1][i,3]:  # Away Win
                    simulation_matrix_regular[i,:] = np.matrix(2*np.ones(simulations))
            else:
                simulation_matrix_regular[i,:] = simulation_matrix[i,:]
    
        # Generate Output based on Monte Carlo Simulation
        # Determine number of points & league position for every team in every simulation
    
        # points is matrix of size number_of_teams x simulation
        # unsorted (teams alphabetically) points for every team in every season
        points = np.zeros((number_of_teams, simulations))
        wins = np.zeros((number_of_teams, simulations))
        
        # Fix points and wins per PO competition
        rs_ranking = wedstrijden_gtt["rs"][2]
        if competition == "poi":
            for i in range(len(team_indices)):
                points[i,:] = np.ones((1,simulations))*np.ceil(rs_ranking[:,7]/2)[int(team_indices[i])]
                # wins[i,:] = np.ones((1,simulations))*np.ceil(rs_ranking[:,1]/2)[int(team_indices[i])]
                
        if competition == "poiii":
            if rs_ranking[:,8][int(team_indices[0])] < rs_ranking[:,8][int(team_indices[1])]:
                points[0,:] = np.ones((1,simulations))*3  
            else:
                points[1,:] = np.ones((1,simulations))*3 
                
        # league_ranking is matrix of size number_of_teams x simulation
        # sorted (descending) index of team on that position
        league_ranking = np.zeros((number_of_teams, simulations))
        league_ranking_distribution_po = list()
        for i in range(simulations):
            for j in range(total_games):
                for k in range(number_of_teams):
                    if wedstrijden_gtt[competition][1][j, 0] == team_indices[k]:  # Home Team
                        if simulation_matrix_regular[j, i] == 0:  # Home Team Victory
                            points[k, i] += 3
                            wins[k, i] += 1
                        if simulation_matrix_regular[j, i] == 1:  # Tie
                            points[k, i] += 1
                        if simulation_matrix_regular[j, i] == 2:  # Away Team Victory
                            points[k, i] += 0
                    if wedstrijden_gtt[competition][1][j, 1] == team_indices[k]:  # Away team
                        if simulation_matrix_regular[j, i] == 0:  # Home Team Victory
                            points[k, i] += 0
                        if simulation_matrix_regular[j, i] == 1:  # Tie
                            points[k, i] += 1
                        if simulation_matrix_regular[j, i] == 2:  # Away Team Victory
                            points[k, i] += 3
                            wins[k, i] += 1
    
            # Make ranking for this simulation
            # 1. Sort by points
            league_ranking[:, i] = np.argsort(points[:, i])[::-1]  # Best Team index [0], Worst team index [number_of_teams - 1]
    
            # 2. If same amount of points, most wins
            for j in range(1,len(points)):
                if points[league_ranking[j,i],i] == points[league_ranking[j-1,i],i]:
                    if wins[league_ranking[j,i],i] > wins[league_ranking[j-1,i],i]:
                        league_ranking[j,i],league_ranking[j-1,i] = league_ranking[j-1,i],league_ranking[j,i]
    
            # 3. Goal difference
        
        # # Average amount of points for every team
        # # number_of_teams (ordered alphabetically) x 1 matrix
        # points_avg = np.sum(points, axis=1) / simulations
    
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
        league_ranking_distribution = np.around(league_ranking_distribution,5)
        
        output[competition] = list([list([team_names,team_indices]), league_ranking_distribution])

    return output