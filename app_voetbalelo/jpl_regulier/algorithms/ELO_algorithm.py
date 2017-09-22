__author__ = 'Exergos'
__project__ = 'SPI_JupilerProLeague'

########################################################################################################################
########################################################################################################################

#########################
# What does this file do?
#########################

# This file calculates the ELO Rating for every team of the Jupiler Pro League

# Python 3.3 as Interpreter
# sporza to import sporza data
# Numpy for mathematical use

######################
# What does it return?
######################

# Returns a list of 2 items
# [0]:  List of 2 things
#       [0][0]: Team names of all teams in Jupiler Pro League
#       [0][1]: List of ELO rating for every team (after last played game)

# [1]:  Array of size ((games played + games not played) x 8)
#       [1][:,0]: Home Team (As a number, alphabetically as in [0]
#       [1][:,1]: Away Team (As a number, alphabetically as in [0]
#       [1][:,2]: Home Team Goals
#       [1][:,3]: Away Team Goals
#       [1][:,4]: Game already played? (1 = yes, 0 = no)
#       [1][:,5]: Probability of Home Win
#       [1][:,6]: Probability of Tie
#       [1][:,7]: Probability of Away Win

########################################################################################################################
########################################################################################################################
def elo(input_data, simulations = 20000):
    import numpy as np
    import json
    import scipy.stats # For Poisson Distribution, numpy doesn't have it
    import pulp # For MILP percentages to integers
    from app_voetbalelo.jpl_regulier.algorithms.game_to_team import game_to_team
    input_data = game_to_team(input_data)
    
    # input_data is a list of 2 lists:
    # [0]:  Team names of all teams in Jupiler Pro League
    # [1]:  Array of size (total games x 4)
    #       [1][:,0]: Home Team (As a number, alphabetically as in [0]
    #       [1][:,1]: Away Team (As a number, alphabetically as in [0]
    #       [1][:,2]: Home Team Goals
    #       [1][:,3]: Away Team Goals
    #       [1][:,4]: Game already played (1 = yes, 0 = no)
    
    # Define some parameters that will help with reading the code
    number_of_teams = len(input_data[0])
    total_games = len(input_data[1])
    
    # Calculate ELO using ELO Formula
    # ELO parameters
    elo_start = 1500
    
    
    # Hard coded seizoen 2015/2016
    # Gebaseerd op analyse all time belgische eerste klasse
    # 0.75 * last season + 0.25 *1500 OF 1300 bij opkomende ploegen
    elo_start_array = [1797,1758,1671,1729,1651,1602,1610,1479,1300,1464,1649,1300,1707,1356,1431,1442]
    for i in range(len(elo_start_array)):
        if elo_start_array[i] >= 1500:
            elo_start_array[i] = elo_start_array[i] - (elo_start_array[i]-1500)/2
        else:
            elo_start_array[i] = elo_start_array[i] + abs((elo_start_array[i]-1500)/2)
            
    calibratiefactor = sum(elo_start_array)/(1500*16)
    for i in range(len(elo_start_array)):
        elo_start_array[i] = elo_start_array[i]/calibratiefactor
    
    K = 50
    home_field_advantage = 84 # http://clubelo.com/HFA/ for belgium
    
    # Every team starts off with 1500 before season
    # Calculate through season
    
    elo_rating_before_game = np.zeros((total_games,number_of_teams))
    elo_rating_after_game = np.zeros((total_games,number_of_teams))
    
    elo_rating_before_game[0,:] = elo_start_array
    
    # count_games_played = 0
    for i in range(total_games):
        # Calculate W_home, W_away and G parameter for game
        if input_data[1][i,2] > input_data[1][i,3]: # Home Win
            W_home = 1
            W_away = 0
        if input_data[1][i,2] == input_data[1][i,3]: # Draw
            W_home = 0.5
            W_away = 0.5
        if input_data[1][i,2] < input_data[1][i,3]: # Away Win
            W_home = 0
            W_away = 1
    
        # G
        if input_data[1][i,2] == input_data[1][i,3] or abs(input_data[1][i,2] - input_data[1][i,3]) == 1: # Draw or 1 goal difference
            G = 1
        else:
            if abs(input_data[1][i,2] - input_data[1][i,3]) == 2: # 2 goals difference
                G = 3/2
            else: # 3 or more goals difference
                G = (11 + abs(input_data[1][i,2] - input_data[1][i,3]))/8
    
        # Calculate ELO rating AFTER game
        # First game based on ELO_START_ARRAY
        if i == 0: # First game of the season
            # Home Team new ELO rating after game
            W_home_e = 1/(10**(-home_field_advantage/400)+1)
            elo_rating_after_game[i,input_data[1][i,0]] = elo_start_array[int(input_data[1][i,0])] + K*G*(W_home-W_home_e)
    
            # Away Team new ELO rating after game
            W_away_e = 1/(10**(home_field_advantage/400)+1)
            elo_rating_after_game[i,input_data[1][i,1]] = elo_start_array[int(input_data[1][i,1])] + K*G*(W_away-W_away_e)
        
        # Rest of the games played based on previous
        elif input_data[1][i,4] == 1:
            # Home Team new ELO rating after game
            W_home_e = 1/(10**(-(elo_rating_after_game[i-1,input_data[1][i,0]]+home_field_advantage-elo_rating_after_game[i-1,input_data[1][i,1]])/400)+1)
            elo_rating_after_game[i,input_data[1][i,0]] = elo_rating_after_game[i-1,input_data[1][i,0]] + K*G*(W_home-W_home_e)
    
            # Away Team new ELO rating after game
            W_away_e = 1/(10**(-(elo_rating_after_game[i-1,input_data[1][i,1]]-home_field_advantage-elo_rating_after_game[i-1,input_data[1][i,0]])/400)+1)
            elo_rating_after_game[i,input_data[1][i,1]] = elo_rating_after_game[i-1,input_data[1][i,1]] + K*G*(W_away-W_away_e)
        
        # For every team that didn't play, copy old elo into new spot
        # AFTER game
        for j in range(number_of_teams):
            if elo_rating_after_game[i,j] == 0:
                if i == 0:
                    elo_rating_after_game[i,j] = elo_start_array[j]
                else:
                    elo_rating_after_game[i,j] = elo_rating_after_game[i-1,j]
    
    
    # Now calculate Win/Loss/Draw expectancy for all games based on actual ELO (after last played game)
    # Expand input_data[1]
    input_data[1] = np.c_[input_data[1], np.zeros((total_games, 3))]  # 3 extra input_data columns (prob home win, prob tie, prob away win)
    for i in range(total_games):
        # Home Team new ELO rating after game
        if i == 0:
            # Use elo_start_array because 0-1 problem
            W_home_e = 1/(10**(-(elo_start_array[int(input_data[1][i,0])]+home_field_advantage-elo_start_array[int(input_data[1][i,1])])/400)+1)
        else:
            # Always look 1 row back (Elo BEFORE game)
            W_home_e = 1/(10**(-(elo_rating_after_game[i-1,input_data[1][i,0]]+home_field_advantage-elo_rating_after_game[i-1,input_data[1][i,1]])/400)+1)
        
        # First estimate expected goals
        # Goals for Home team
        if W_home_e < 0.5:
            home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
        else:
            home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
    
        # Goals for the Away team:
        if W_home_e < 0.8:
            away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
        else:
            away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3
    
        # Now use poisson distribution to determine for each team the chance it scores x goals
        # Combine these for both teams to calculate Win/Loss/Draw expectancy
    
        for j in range(15):
            for k in range(15):
                if j > k:
                    # Home Win
                   input_data[1][i,5] = input_data[1][i,5] + scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
                if j == k:
                    # Tie
                   input_data[1][i,6] = input_data[1][i,6] + scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
                if j < k:
                    # Away Win
                   input_data[1][i,7] = input_data[1][i,7] + scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
    
        # Make sure probabilities sum up to 1 (otherwise problem for montecarlo simulation)
        input_data[1][i,5:8] /= input_data[1][i,5:8].sum()
    
    print('ELO Algorithm finished')
    
    elo_rating_after_game = np.round(elo_rating_after_game)
    output = list([[input_data[0], elo_rating_after_game[-1,:]], input_data[1]])
    
    # For every team, the evolution of their ELO rating
    elo_evolution = list()
    for i in range(number_of_teams):
        elo_evolution.append(list())
    
    count_games = 0
    for i in range(len(input_data[1])):
        if input_data[1][i,4] == 1: # Game Played
            elo_evolution[int(input_data[1][i,0])].append(elo_rating_after_game[count_games,int(input_data[1][i,0])])
            elo_evolution[int(input_data[1][i,1])].append(elo_rating_after_game[count_games,int(input_data[1][i,1])])
            count_games += 1
    
    # Output is a list of 2 items
    # [0]:  List of 2 things
    #       [0][0]: Team names of all teams in Jupiler Pro League
    #       [0][1]: List of ELO rating for every team (after last played game)
    
    # [1]:  Array of size ((games played + games not played) x 8)
    #       [1][:,0]: Home Team (As a number, alphabetically as in [0]
    #       [1][:,1]: Away Team (As a number, alphabetically as in [0]
    #       [1][:,2]: Home Team Goals
    #       [1][:,3]: Away Team Goals
    #       [1][:,4]: Game already played? (1 = yes, 0 = no)
    #       [1][:,5]: Probability of Home Win
    #       [1][:,6]: Probability of Tie
    #       [1][:,7]: Probability of Away Win
    
    # This can in the future be used for soccer power ranking app
    # For now only output league ranking distribution data, based on montecarlo simulation:
    from app_voetbalelo.jpl_regulier.algorithms.montecarlo import montecarlo
    output = montecarlo(output,simulations,actual=1)
    
    # Save as result json file
    # Teams
    json.dump(input_data[0],open("app_voetbalelo/jpl_regulier/algorithms/result/teams.json","w"))
    
    # Games
    games_matrix = np.round(100*input_data[1])/100
    for i in range(len(games_matrix)):
        games_matrix[i,-3:] = 100*games_matrix[i,-3:]
    
    games_matrix = games_matrix.astype(int)
    for i in range(len(games_matrix)):
        max_index = np.argmax(games_matrix[i,-3:])+5
        games_matrix[i,max_index] = games_matrix[i,max_index] - (sum(games_matrix[i,-3:]) - 100) 
            
    json.dump(games_matrix.tolist(),open("app_voetbalelo/jpl_regulier/algorithms/result/games.json","w"))
    
    # Standing
    json.dump(input_data[2].tolist(),open("app_voetbalelo/jpl_regulier/algorithms/result/standing.json","w"))
    
    # ELO rating
    games_matrix = input_data[1]
    team_indices = []
    while len(team_indices) != number_of_teams:
        for i in reversed(range(len(games_matrix))):
            ht_index = int(games_matrix[i,0])
            at_index = int(games_matrix[i,1])
            
            # Game played?
            if games_matrix[i,4] == 1:
                if (ht_index not in team_indices) and (at_index not in team_indices):
                    team_indices.append(ht_index)
                    team_indices.append(at_index)
                    
                    dElo_ht = elo_evolution[ht_index][-1] - elo_evolution[ht_index][-2] 
                    dElo_at = elo_evolution[at_index][-1] - elo_evolution[at_index][-2] 
                    
                    if abs(dElo_ht) != abs(dElo_at):
                        # Adjust latest HT Elo (aanname)
                        adj = abs(dElo_ht) - abs(dElo_at)
                        if dElo_ht >= 0:
                            elo_evolution[ht_index][-1] -= adj
                        else:
                            elo_evolution[ht_index][-1] += adj
    elo = []
    for i in range(number_of_teams):
        elo.append(elo_evolution[i][-1])
                    
    json.dump(elo,open("app_voetbalelo/jpl_regulier/algorithms/result/elo.json","w"))
    
    # End Ranking Forecast After Regular Season
    model = pulp.LpProblem("JPL Problem", pulp.LpMinimize)
    
    variable_names = []
    lowBound_dict = dict()
    upBound_dict =  dict()
    # Voor elk team
    for i in range(len(input_data[0])):
        # Elke mogelijke eindklassering
        for j in range(len(input_data[0])):
            variable_names.append(str(i) + "_" + str(j)) 
            # lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(1000*output[1][i,j]))
            # upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(1000*output[1][i,j]))
            
            if 100*output[1][i,j] >= 0.5:
                # 1% Meer of minder mag dan
                lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*output[1][i,j]))
                upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(100*output[1][i,j]))
            else:
                # 0% fixed
                lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*output[1][i,j]))
                upBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*output[1][i,j]))  
           
            # if 1000*output[2][i,j] >= 100:
            #     # 1% Meer of minder mag dan
            #     lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(1000*output[1][i,j])) -10
            #     upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(1000*output[1][i,j])) + 10
            # elif 1000*output[2][i,j] < 0.1:
            #     # 0% fixed
            #     lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(1000*output[1][i,j]))
            #     upBound_dict[str(i) + "_" + str(j)] = float(np.floor(1000*output[1][i,j]))  
            # else:
            #     lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(1000*output[1][i,j]))
            #     upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(1000*output[1][i,j]))
    
            
    
    variables = pulp.LpVariable.dict("variable_%s", variable_names, lowBound = 0, upBound = 100, cat = pulp.LpInteger)
    
    # Ax=B    
    zero = len(input_data[0])*[0.0]
    one = len(input_data[0])*[1.0]
    equality = []
    for variable_names_i in range(len(input_data[0])):
        equality_vector = variable_names_i*zero + one + (len(input_data[0])-variable_names_i-1)*zero
        equality.append(dict(zip(variable_names,equality_vector)))
    
    for eq in equality:
        model += sum([eq[i]*variables[i] for i in variable_names]) == 100.0
    
    # Constraints sum for every position == 100
    equality = []   
    for variable_names_i in range(len(input_data[0])):
        equality_vector = variable_names_i*[0] + [1] + (len(input_data[0])-variable_names_i-1)*[0]
        equality_vector = len(input_data[0])*equality_vector
        equality.append(dict(zip(variable_names,equality_vector)))
    
    for eq in equality:
        model += sum([eq[i]*variables[i] for i in variable_names]) == 100.0
        
    # Constraints (ub,lb)
    for var in variable_names:
        model+= variables[var] >= lowBound_dict[var]
        model+= variables[var] <= upBound_dict[var]
    
    # solve and get output
    model.solve()
    if model.solve() == -1:
        print("WARNING: Regular MIP Algorithm did not reach optimal point")
    forecast_regular_matrix = []
    for i in range(len(input_data[0])):
        forecast_regular_matrix.append([])
        # Elke mogelijke eindklassering
        for j in range(len(input_data[0])):
            forecast_regular_matrix[-1].append(int(variables[str(i) + "_" + str(j)].value()))
            
    json.dump(forecast_regular_matrix,open("app_voetbalelo/jpl_regulier/algorithms/result/standing_forecast_regular.json","w"))
    
    ##########################################################################################
    # End Ranking Forecast After PO
    ##########################################################################################
    
    model = pulp.LpProblem("JPL Problem", pulp.LpMinimize)
    
    variable_names = []
    lowBound_dict = dict()
    upBound_dict =  dict()
    # Voor elk team
    for i in range(len(input_data[0])):
        # Elke mogelijke eindklassering
        for j in range(len(input_data[0])):
            variable_names.append(str(i) + "_" + str(j)) 
            # lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(1000*output[2][i,j]))
            # upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(1000*output[2][i,j]))
            if 100*output[2][i,j] >= 0.5:
                # 1% Meer of minder mag dan
                lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*output[2][i,j]))
                upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(100*output[2][i,j]))
            else:
                # 0% fixed
                lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*output[2][i,j]))
                upBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*output[2][i,j]))
                
            # if 1000*output[2][i,j] >= 100:
            #     # 1% Meer of minder mag dan
            #     lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(1000*output[2][i,j])) -10
            #     upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(1000*output[2][i,j])) + 10
            # elif 1000*output[2][i,j] < 0.1:
            #     # 0% fixed
            #     lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(1000*output[2][i,j]))
            #     upBound_dict[str(i) + "_" + str(j)] = float(np.floor(1000*output[2][i,j]))  
            # else:
            #     lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(1000*output[2][i,j]))
            #     upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(1000*output[2][i,j]))
            # first_decimal = 100*output[2][i,j] - np.floor(100*output[2][i,j])
            # if first_decimal > 0.7:
            #     # Ceil als decimaal groter dan 8
            #     lowBound_dict[str(i) + "_" + str(j)] = float(np.ceil(100*output[2][i,j]))
            #     upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(100*output[2][i,j]))
            # elif first_decimal < 0.3:
            #     # Floor als decimaal kleiner dan 2 (zodat 3,2 geen 4 wordt maar altijd 3)
            #     lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*output[2][i,j]))
            #     upBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*output[2][i,j]))
            # else:
            #     lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*output[2][i,j]))
            #     upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(100*output[2][i,j]))
                
    variables = pulp.LpVariable.dict("variable_%s", variable_names, lowBound = 0, upBound = 100, cat = pulp.LpInteger)
    
    # Som van 1 ploeg == 100
    # Ax=B    
    zero = len(input_data[0])*[0.0]
    one = len(input_data[0])*[1.0]
    equality = []
    for variable_names_i in range(len(input_data[0])):
        equality_vector = variable_names_i*zero + one + (len(input_data[0])-variable_names_i-1)*zero
        equality.append(dict(zip(variable_names,equality_vector)))
    
    for eq in equality:
        model += sum([eq[i]*variables[i] for i in variable_names]) == 100.0
    
    # # Procenten die bij kommagetal > zijn moeten >= blijven als integer
    # # Ax >= B
    # equality = []
    # for i in range(len(input_data[0])):
    #     sort_indices = np.argsort(output[2][i,:])
    #     for j in range(len(sort_indices)-1):
    #         variable_index_small = i*len(input_data) + sort_indices[j]
    #         variable_index_big = i*len(input_data) + sort_indices[j+1]
            
    #         # Only if small difference
    #         if output[2][i,sort_indices[j+1]] < 0.01:
    #             equality_vector = len(input_data[0])*len(input_data[0])*[0]
    #             equality_vector[variable_index_small] = 1
    #             equality_vector[variable_index_big] = -1
            
    #             equality.append(dict(zip(variable_names,equality_vector)))
    
    # for eq in equality:
    #     model += sum([eq[i]*variables[i] for i in variable_names]) <= 0.0
        
    # Som van 1 eindpositie == 100
    equality = []   
    for variable_names_i in range(len(input_data[0])):
        equality_vector = variable_names_i*[0] + [1] + (len(input_data[0])-variable_names_i-1)*[0]
        equality_vector = len(input_data[0])*equality_vector
        equality.append(dict(zip(variable_names,equality_vector)))
    
    for eq in equality:
        model += sum([eq[i]*variables[i] for i in variable_names]) == 100.0
        
    # Constraints (ub,lb)
    for var in variable_names:
        model+= variables[var] >= lowBound_dict[var]
        model+= variables[var] <= upBound_dict[var]
    
    # solve and get output
    model.solve()
    if model.solve() == -1:
        print("WARNING: PO MIP Algorithm did not reach optimal point")
    forecast_po_matrix = []
    for i in range(len(input_data[0])):
        forecast_po_matrix.append([])
        # Elke mogelijke eindklassering
        for j in range(len(input_data[0])):
            forecast_po_matrix[-1].append(int(variables[str(i) + "_" + str(j)].value()))
             
    json.dump(forecast_po_matrix,open("app_voetbalelo/jpl_regulier/algorithms/result/standing_forecast_po.json","w"))
    
    # ELO evolution
    # Add START OF SEASON
    for i in range(len(elo_evolution)):
        elo_evolution[i].insert(0,round(elo_start_array[i]))
    json.dump(elo_evolution,open("app_voetbalelo/jpl_regulier/algorithms/result/elo_evolution.json","w"))
    
    # Hard coded colors
    colors = {  "AA Gent":  "rgba(0, 71, 156,1)",
            "Anderlecht": "rgba(80, 40, 128,1)",
            "Charleroi": "rgba(0,0,0,1)",
            "Club Brugge": "rgba(0, 116, 189,1)",
            "KV Mechelen":  "rgba(224, 30, 35,1)",
            "Kortrijk": "rgba(207, 8, 14,1)" ,
            "Lokeren":"rgba(0,0,0,1)",
            "Moeskroen-Péruwelz": "rgba(229, 20, 42,1)",
            "OH Leuven": "rgba(0,0,0,1)",
            "Oostende": "rgba(190, 22, 35,1)" ,
            "Racing Genk": "rgba(25, 50, 147,1)",
            "STVV": "rgba(205, 179, 13,1)" ,
            "Standard": "rgba(207, 8, 14,1)"  ,
            "Waasland-Beveren":  "rgba(205, 179, 13,1)" ,
            "Westerlo": "rgba(205, 179, 13,1)" ,
            "Zulte Waregem": "rgba(132, 31, 47,1)"  ,
    }
    json.dump(colors,open("app_voetbalelo/jpl_regulier/algorithms/result/colors.json","w"))
    return list([output, input_data,elo_evolution])

# Add probability data to upcoming games (from spi and elo)
def extend_upcoming_prob(input_data_game,input_data_team, algorithm):
    for i in range(len(input_data_game[0])):
        for j in range(len(input_data_team[1])):
            if input_data_game[0][i]["host"] == input_data_team[0][int(input_data_team[1][j,0])] and input_data_game[0][i]["visitor"] == input_data_team[0][int(input_data_team[1][j,1])]:
                input_data_game[0][i]["host_" + algorithm] = input_data_team[1][j,5]
                input_data_game[0][i]["tie_" + algorithm] = input_data_team[1][j,6]
                input_data_game[0][i]["visitor_" + algorithm] = input_data_team[1][j,7]

    return input_data_game

def upset(input_data):
    import numpy as np
    # only for last season
    for i in range(len(input_data[0])):
        # only for games played
        if input_data[0][i]["played"] == "1":
            host_win = input_data[0][i]["host_elo"]
            visitor_win = input_data[0][i]["visitor_elo"]
            tie = input_data[0][i]["tie_elo"]
            gd = int(input_data[0][i]["host_goal"]) - int(input_data[0][i]["visitor_goal"])

            # host win
            if input_data[0][i]["result"] == "1":
                if host_win >= 0.5:
                    gdx = 10*host_win - 4
                    upset1 = 25*(host_win-0.5)**2
                    lh = np.array([[2*gdx,1,0],[gdx**2,gdx,1],[1,1,1]])
                    rh = np.array([0,0,upset1])
                    coeff = np.linalg.solve(lh,rh)
                else:
                    gdx = 1
                    upset3 = -10*host_win+5
                    lh = np.array([[2*gdx,1,0],[gdx**2,gdx,1],[9,3,1]])
                    rh = np.array([0,0,upset3])
                    coeff = np.linalg.solve(lh,rh)

                input_data[0][i]["upset"] = (1-host_win)/host_win + coeff[0]*gd**2 + coeff[1]*gd + coeff[2]

            # visitor win
            if input_data[0][i]["result"] == "-1": # visitor win
                if visitor_win >= 0.5:
                    gdx = -(10*visitor_win - 4)
                    upset1 = 25*(visitor_win-0.5)**2
                    lh = np.array([[2*gdx,1,0],[gdx**2,gdx,1],[1,1,1]])
                    rh = np.array([0,0,upset1])
                    coeff = np.linalg.solve(lh,rh)
                else:
                    gdx = -1
                    upset3 = -10*visitor_win+5
                    lh = np.array([[2*gdx,1,0],[gdx**2,gdx,1],[1,1,1]])
                    rh = np.array([0,0,upset3])
                    coeff = np.linalg.solve(lh,rh)


                input_data[0][i]["upset"] = (1-visitor_win)/visitor_win + coeff[0]*gd**2 + coeff[1]*gd + coeff[2]

            # tie
            if input_data[0][i]["result"] == "0": # tie
                input_data[0][i]["upset"] = max(host_win,visitor_win) / tie

    return input_data

def excitement(input_data):
    # only for last season
    for i in range(len(input_data[0])):
        if input_data[0][i]["played"] == "1":
            # number of times during game that the result changes
            result_changes = 0
            number_of_goals = int(input_data[0][i]["host_goal"]) + int(input_data[0][i]["visitor_goal"])
            # Check for gd not equal to 0 in first minute
            if sign(int(input_data[0][i]["minute_" + str(1)])) != 0:
                result_changes += 1
            for j in range(1,90):
                # Check if league change
                if sign(int(input_data[0][i]["minute_" + str(j+1)])) != sign(int(input_data[0][i]["minute_" + str(j)])):
                    result_changes += abs(sign(int(input_data[0][i]["minute_" + str(j+1)]))) + abs(sign(int(input_data[0][i]["minute_" + str(j)])))

            input_data[0][i]["excitement"] = result_changes + (input_data[0][i]["upset"]*number_of_goals)**1/2 + input_data[0][i]["upset"]**1/3

    return input_data

# For use within excitement function
def sign(number):
    """Will return 1 for positive,
    -1 for negative, and 0 for 0"""
    try:return number/abs(number)
    except ZeroDivisionError:return 0