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
def elo(team_data_seasons, country_data, hot, simulations = 20000, number_of_seasons=1):
    import numpy as np
    import json
    import scipy.stats # For Poisson Distribution, numpy doesn't have it
    import pulp # For MILP percentages to integers

    # team_data is a list of 2 lists:
    # [0]:  Team names of all teams in Jupiler Pro League
    # [1]:  Array of size (total games x 4)
    #       [1][:,0]: Home Team (As a number, alphabetically as in [0]
    #       [1][:,1]: Away Team (As a number, alphabetically as in [0]
    #       [1][:,2]: Home Team Goals
    #       [1][:,3]: Away Team Goals
    #       [1][:,4]: Game already played (1 = yes, 0 = no)
    season = 0
    output_seasons = []
    for team_data in reversed(team_data_seasons):
        season += 1
        # Define some parameters that will help with reading the code
        number_of_teams = len(team_data[0])
        total_games = len(team_data[1])
        
        # Calculate ELO using ELO Formula
        # ELO parameters
        if season == 1:
            elo_start_array = number_of_teams*[1500]
        else:
            # Map previous elo_start_array onto teams of new season
            teams_previous_season = team_data_seasons[-season + 1][0] 
            teams_this_season = team_data[0]
            
            elo_start_array_dummy = number_of_teams*[1300]
            for i in range(len(elo_start_array)):
                try:
                    new_index = teams_this_season.index(teams_previous_season[i])
                except:
                    continue
                
                elo_start_array_dummy[new_index] = round(0.75*elo_start_array[i] + 0.25*1500)
            
            elo_start_array = elo_start_array_dummy
            
        # Hard coded seizoen 2015/2016
        # Gebaseerd op analyse all time belgische eerste klasse
        # 0.75 * last season + 0.25 *1500 OF 1300 bij opkomende ploegen
        # elo_start_array = [1797,1758,1671,1729,1651,1602,1610,1479,1300,1464,1649,1300,1707,1356,1431,1442]
        # for i in range(len(elo_start_array)):
        #     if elo_start_array[i] >= 1500:
        #         elo_start_array[i] = elo_start_array[i] - (elo_start_array[i]-1500)/2
        #     else:
        #         elo_start_array[i] = elo_start_array[i] + abs((elo_start_array[i]-1500)/2)
                
        # calibratiefactor = sum(elo_start_array)/(1500*16)
        # for i in range(len(elo_start_array)):
        #     elo_start_array[i] = elo_start_array[i]/calibratiefactor
        
        K = 40
        home_field_advantage = 84 # http://clubelo.com/HFA/ for belgium
        
        # Every team starts off with 1500 before season
        # Calculate through season
        
        elo_rating_before_game = np.zeros((total_games,number_of_teams))
        elo_rating_after_game = np.zeros((total_games,number_of_teams))
        
        # elo_rating_before_game[0,:] = elo_start_array
        elo_rating_before_game[0,:] = 1500*np.ones((1,number_of_teams))
        
        # count_games_played = 0
        for i in range(total_games):
            # Calculate W_home, W_away and G parameter for game
            if team_data[1][i,2] > team_data[1][i,3]: # Home Win
                W_home = 1
                W_away = 0
            if team_data[1][i,2] == team_data[1][i,3]: # Draw
                W_home = 0.5
                W_away = 0.5
            if team_data[1][i,2] < team_data[1][i,3]: # Away Win
                W_home = 0
                W_away = 1
        
            # G
            if team_data[1][i,2] == team_data[1][i,3] or abs(team_data[1][i,2] - team_data[1][i,3]) == 1: # Draw or 1 goal difference
                G = 1
            else:
                if abs(team_data[1][i,2] - team_data[1][i,3]) == 2: # 2 goals difference
                    G = 3/2
                else: # 3 or more goals difference
                    G = (11 + abs(team_data[1][i,2] - team_data[1][i,3]))/8
        
            # Calculate ELO rating AFTER game
            # First game based on ELO_START_ARRAY
            if i == 0: # First game of the season
                # Home Team new ELO rating after game
                W_home_e = 1/(10**(-home_field_advantage/400)+1)
                elo_rating_after_game[i,team_data[1][i,0]] = elo_start_array[int(team_data[1][i,0])] + K*G*(W_home-W_home_e)
                # elo_rating_after_game[i,team_data[1][i,0]] = elo_start + K*G*(W_home-W_home_e)
        
                # Away Team new ELO rating after game
                W_away_e = 1/(10**(home_field_advantage/400)+1)
                elo_rating_after_game[i,team_data[1][i,1]] = elo_start_array[int(team_data[1][i,1])] + K*G*(W_away-W_away_e)
                # elo_rating_after_game[i,team_data[1][i,1]] = elo_start + K*G*(W_away-W_away_e)
            
            # Rest of the games played based on previous
            elif team_data[1][i,4] == 1:
                # Home Team new ELO rating after game
                W_home_e = 1/(10**(-(elo_rating_after_game[i-1,team_data[1][i,0]]+home_field_advantage-elo_rating_after_game[i-1,team_data[1][i,1]])/400)+1)
                elo_rating_after_game[i,team_data[1][i,0]] = elo_rating_after_game[i-1,team_data[1][i,0]] + K*G*(W_home-W_home_e)
        
                # Away Team new ELO rating after game
                W_away_e = 1/(10**(-(elo_rating_after_game[i-1,team_data[1][i,1]]-home_field_advantage-elo_rating_after_game[i-1,team_data[1][i,0]])/400)+1)
                elo_rating_after_game[i,team_data[1][i,1]] = elo_rating_after_game[i-1,team_data[1][i,1]] + K*G*(W_away-W_away_e)
            
            # For every team that didn't play, copy old elo into new spot
            # AFTER game
            for j in range(number_of_teams):
                if elo_rating_after_game[i,j] == 0:
                    if i == 0:
                        elo_rating_after_game[i,j] = elo_start_array[j]
                        # elo_rating_after_game[i,j] = elo_start
                    else:
                        elo_rating_after_game[i,j] = elo_rating_after_game[i-1,j]
        
        
        # Now calculate Win/Loss/Draw expectancy for all games based on actual ELO (after last played game)
        # Expand team_data[1]
        team_data[1] = np.c_[team_data[1], np.zeros((total_games, 3))]  # 3 extra team_data columns (prob home win, prob tie, prob away win)
        for i in range(total_games):
            # Home Team new ELO rating after game
            if i == 0:
                # Use elo_start_array because 0-1 problem
                W_home_e = 1/(10**(-(elo_start_array[int(team_data[1][i,0])]+home_field_advantage-elo_start_array[int(team_data[1][i,1])])/400)+1)
                # W_home_e = 1/(10**(-(elo_start+home_field_advantage-elo_start)/400)+1)
            
            else:
                # Always look 1 row back (Elo BEFORE game)
                W_home_e = 1/(10**(-(elo_rating_after_game[i-1,team_data[1][i,0]]+home_field_advantage-elo_rating_after_game[i-1,team_data[1][i,1]])/400)+1)
            
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
                       team_data[1][i,5] = team_data[1][i,5] + scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
                    if j == k:
                        # Tie
                       team_data[1][i,6] = team_data[1][i,6] + scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
                    if j < k:
                        # Away Win
                       team_data[1][i,7] = team_data[1][i,7] + scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
        
            # Make sure probabilities sum up to 1 (otherwise problem for montecarlo simulation)
            team_data[1][i,5:8] /= team_data[1][i,5:8].sum()
        
        print('ELO Algorithm finished')
        
        elo_rating_after_game = np.round(elo_rating_after_game)
        output = list([[team_data[0], elo_rating_after_game[-1,:]], team_data[1]])
        
        # For every team, the evolution of their ELO rating
        elo_evolution = list()
        for i in range(number_of_teams):
            elo_evolution.append(list())
        
        count_games = 0
        for i in range(len(team_data[1])):
            if team_data[1][i,4] == 1: # Game Played
                elo_evolution[int(team_data[1][i,0])].append(elo_rating_after_game[count_games,int(team_data[1][i,0])])
                elo_evolution[int(team_data[1][i,1])].append(elo_rating_after_game[count_games,int(team_data[1][i,1])])
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
        from app_voetbalelo.eu_domestic_leagues.montecarlo import montecarlo
        # Only run Montecarlo if games unplayed
        if int(np.sum(team_data[1][:,4])) != total_games:
            # print(season)
            output = montecarlo(output,country_data,simulations,hot)
        
        output_seasons.append([output, team_data, elo_evolution,elo_start_array])

        # Define elo_start_array as last elo's of this season
        elo_start_array = []
        for i in range(number_of_teams):
            elo_start_array.append(elo_evolution[i][-1])
            
    # return output, but reverse it (current season at index 0) 
    output_seasons.reverse()
    return output_seasons