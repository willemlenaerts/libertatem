__author__ = 'Exergos'

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
def elo(wedstrijden_gtt):
    import numpy as np
    import scipy.stats # For Poisson Distribution, numpy doesn't have it4
    
    # Loop over all competitions
    competitions = ["rs","poi","poii_a","poii_b","poiii"]
    
    # Save output
    output = dict()
    
    for competition in competitions:
        print("Calculating ELO rating for " + competition)
        
        # Define some parameters that will help with reading the code
        team_names = wedstrijden_gtt[competition][0][0]
        team_indices = wedstrijden_gtt[competition][0][1]
        number_of_teams = len(team_names)
        total_games = len(wedstrijden_gtt[competition][1])
        games_played = []
        for i in range(total_games):
            if wedstrijden_gtt[competition][1][i,4] == 1:
                games_played.append(i)
        
        # Define elo_start
        # Regular season
        if competition == "rs": # rs
            elo_start = [1500]*number_of_teams
        else:
            # Play-offs
            # Team indices of teams in this particular play-off
            elo_start = []
            for i in range(len(team_indices)):
                elo_start.append(output["rs"][1][int(team_indices[i])])
        
        # if no games played yet, no need to run ELO algorithm
        if len(games_played) == 0:
            elo_evolution = []
            for i in range(number_of_teams):
                elo_evolution.append([])
                elo_evolution[i].append(elo_start[i])
            output[competition] = list([list([team_names,team_indices]),elo_start,elo_evolution])
            # continue
        
        # Calculate ELO using ELO Formula
        K = 50
        home_field_advantage = 84 # http://clubelo.com/HFA/ for belgium
        
        # Every team starts off with 1500 before season
        # Calculate through season
        
        elo_rating_after_game = np.zeros((len(games_played),number_of_teams))
        
        count_games_played = 0
        for i in games_played:
            # Host/visitor index
            for j in range(len(team_indices)):
                if wedstrijden_gtt[competition][1][i,0] == team_indices[j]:
                    host_index = j
                if wedstrijden_gtt[competition][1][i,1] == team_indices[j]:
                    visitor_index = j
        
            # Calculate W_home, W_away and G parameter for game
            if wedstrijden_gtt[competition][1][i,2] > wedstrijden_gtt[competition][1][i,3]: # Home Win
                W_home = 1
                W_away = 0
            if wedstrijden_gtt[competition][1][i,2] == wedstrijden_gtt[competition][1][i,3]: # Draw
                W_home = 0.5
                W_away = 0.5
            if wedstrijden_gtt[competition][1][i,2] < wedstrijden_gtt[competition][1][i,3]: # Away Win
                W_home = 0
                W_away = 1
        
            # G
            if wedstrijden_gtt[competition][1][i,2] == wedstrijden_gtt[competition][1][i,3] or abs(wedstrijden_gtt[competition][1][i,2] - wedstrijden_gtt[competition][1][i,3]) == 1: # Draw or 1 goal difference
                G = 1
            else:
                if abs(wedstrijden_gtt[competition][1][i,2] - wedstrijden_gtt[competition][1][i,3]) == 2: # 2 goals difference
                    G = 3/2
                else: # 3 or more goals difference
                    G = (11 + abs(wedstrijden_gtt[competition][1][i,2] - wedstrijden_gtt[competition][1][i,3]))/8
        
            # Calculate ELO rating AFTER game
            if i == games_played[0]: # First game of the season
                # Home Team new ELO rating after game
                W_home_e = 1/(10**(-home_field_advantage/400)+1)
                elo_rating_after_game[count_games_played,host_index] = elo_start[int(host_index)] + K*G*(W_home-W_home_e)
        
                # Away Team new ELO rating after game
                W_away_e = 1/(10**(home_field_advantage/400)+1)
                elo_rating_after_game[count_games_played,visitor_index] = elo_start[int(visitor_index)] + K*G*(W_away-W_away_e)
            else:
                # Home Team new ELO rating after game
                W_home_e = 1/(10**(-(elo_rating_after_game[count_games_played-1,host_index]+home_field_advantage-elo_rating_after_game[count_games_played-1,visitor_index])/400)+1)
                elo_rating_after_game[count_games_played,host_index] = elo_rating_after_game[count_games_played-1,host_index] + K*G*(W_home-W_home_e)
        
                # Away Team new ELO rating after game
                W_away_e = 1/(10**(-(elo_rating_after_game[count_games_played-1,visitor_index]-home_field_advantage-elo_rating_after_game[count_games_played-1,host_index])/400)+1)
                elo_rating_after_game[count_games_played,visitor_index] = elo_rating_after_game[count_games_played-1,visitor_index] + K*G*(W_away-W_away_e)
        
            # For every team that didn't play, copy old elo into new spot
            for j in range(number_of_teams):
                if elo_rating_after_game[count_games_played,j] == 0:
                    if i == games_played[0]:
                        elo_rating_after_game[count_games_played,j] = elo_start[j]
                    else:
                        elo_rating_after_game[count_games_played,j] = elo_rating_after_game[count_games_played-1,j]
        
            count_games_played = count_games_played + 1
        
        # Now calculate Win/Loss/Draw expectancy for all games based on actual ELO (after last played game)
        # Expand wedstrijden_gtt[competition][1]
        if wedstrijden_gtt[competition][1].shape[1] == 6:
            wedstrijden_gtt[competition][1] = np.c_[wedstrijden_gtt[competition][1], np.zeros((total_games, 3))]  # 3 extra wedstrijden_gtt[competition] columns (prob home win, prob tie, prob away win)
        else:
            if wedstrijden_gtt[competition][1].shape[1] > 6:
                for i in range(wedstrijden_gtt[competition][1].shape[1]-6):
                    wedstrijden_gtt[competition][1] = np.delete(wedstrijden_gtt[competition][1],-1,1)
                wedstrijden_gtt[competition][1] = np.c_[wedstrijden_gtt[competition][1], np.zeros((total_games, 3))]  # 3 extra wedstrijden_gtt[competition] columns (prob home win, prob tie, prob away win)
                    
        for i in range(total_games):
            # Host/visitor index
            for j in range(len(team_indices)):
                if wedstrijden_gtt[competition][1][i,0] == team_indices[j]:
                    host_index = j
                if wedstrijden_gtt[competition][1][i,1] == team_indices[j]:
                    visitor_index = j
                    
            # Home Team new ELO rating after game
            if competition == "rs":
                W_home_e = 1/(10**(-(elo_rating_after_game[count_games_played-1,host_index]+home_field_advantage-elo_rating_after_game[count_games_played-1,visitor_index])/400)+1)
            else:
                W_home_e = 1/(10**(-(output["rs"][1][wedstrijden_gtt[competition][1][i,0]]+home_field_advantage-output["rs"][1][wedstrijden_gtt[competition][1][i,1]])/400)+1)
            
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
                       wedstrijden_gtt[competition][1][i,6] = wedstrijden_gtt[competition][1][i,6] + scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
                    if j == k:
                        # Tie
                       wedstrijden_gtt[competition][1][i,7] = wedstrijden_gtt[competition][1][i,7] + scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
                    if j < k:
                        # Away Win
                       wedstrijden_gtt[competition][1][i,8] = wedstrijden_gtt[competition][1][i,8] + scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
        
            # Make sure probabilities sum up to 1 (otherwise problem for montecarlo simulation)
            wedstrijden_gtt[competition][1][i,6:9] /= wedstrijden_gtt[competition][1][i,6:9].sum()
        
        print('ELO Algorithm finished')
        
        # if competition == "rs":
        #     # Round ELO (while keeping differences the same for two teams who played against eachother)
        #     for i in range(len(elo_rating_after_game)-1):
        #         if i == 0:
        #             diff0_round = np.round(elo_rating_after_game[i,int(host_index)]) - np.round(elo_start[int(host_index)])
        #             diff1_round = np.round(elo_rating_after_game[i,int(visitor_index)]) - np.round(elo_start[int(visitor_index)])
        #         else:
        #             diff0_round = np.round(elo_rating_after_game[i,int(host_index)]) - np.round(elo_rating_after_game[i-1,int(host_index)])
        #             diff1_round = np.round(elo_rating_after_game[i,int(visitor_index)]) - np.round(elo_rating_after_game[i-1,int(visitor_index)])
        #         if abs(diff0_round) - abs(diff1_round) == 0:
        #             elo_rating_after_game[i-1,:] = np.round(elo_rating_after_game[i-1,:])
        #             elo_rating_after_game[i,:] = np.round(elo_rating_after_game[i,:])
        #         else:
        #             if abs(diff0_round) > abs(diff1_round):
        #                 elo_rating_after_game[i,int(host_index)] = elo_rating_after_game[i,int(host_index)] - 0.5
        #                 elo_rating_after_game[i-1,int(host_index)] = np.round(elo_rating_after_game[i-1,int(host_index)])
        #                 elo_rating_after_game[i,int(host_index)] = np.round(elo_rating_after_game[i,int(host_index)])
        #             else:
        #                 elo_rating_after_game[i,int(visitor_index)] = elo_rating_after_game[i,int(visitor_index)] - 0.5
        #                 elo_rating_after_game[i-1,int(visitor_index)] = np.round(elo_rating_after_game[i-1,int(visitor_index)])
        #                 elo_rating_after_game[i,int(visitor_index)] = np.round(elo_rating_after_game[i,int(visitor_index)])
        
        elo_rating_after_game = np.round(elo_rating_after_game)
        
        # For every team, the evolution of their ELO rating
        elo_evolution = list()
        for i in range(number_of_teams):
            elo_evolution.append(list())
    
        count_games = 0
        for i in range(len(wedstrijden_gtt[competition][1])):
            # Host/visitor index
            for j in range(len(team_indices)):
                if wedstrijden_gtt[competition][1][i,0] == team_indices[j]:
                    host_index = j
                if wedstrijden_gtt[competition][1][i,1] == team_indices[j]:
                    visitor_index = j
            if wedstrijden_gtt[competition][1][i,4] == 1: # Game Played
                elo_evolution[int(host_index)].append(elo_rating_after_game[count_games,int(host_index)])
                elo_evolution[int(visitor_index)].append(elo_rating_after_game[count_games,int(visitor_index)])
                count_games += 1
    
        output[competition] = list([list([team_names,team_indices]),elo_rating_after_game[-1,:],elo_evolution])

    return output

# Add probability data to upcoming games (from spi and elo)
def extend_upcoming_prob(wedstrijden,wedstrijden_gtt):
     # Loop over all competitions
    competitions = ["rs","poi","poii_a","poii_b","poiii"]
    
    for competition in competitions:
        # Define some parameters that will help with reading the code
        team_names = wedstrijden_gtt[competition][0][0]
        team_indices = wedstrijden_gtt[competition][0][1]
        number_of_teams = len(team_names)
        total_games = len(wedstrijden_gtt[competition][1])
        games_played = []
        for i in range(total_games):
            if wedstrijden_gtt[competition][1][i,4] == 1:
                games_played.append(i)
                
        for i in range(len(wedstrijden)):
            for j in range(len(wedstrijden_gtt[competition][1])):
                if wedstrijden[i]["host"] == wedstrijden_gtt["rs"][0][0][int(wedstrijden_gtt[competition][1][j,0])] \
                and wedstrijden[i]["visitor"] == wedstrijden_gtt["rs"][0][0][int(wedstrijden_gtt[competition][1][j,1])] \
                and wedstrijden[i]["competition"] == competition:
                    wedstrijden[i]["host_win"] = wedstrijden_gtt[competition][1][j,6]
                    wedstrijden[i]["tie"] = wedstrijden_gtt[competition][1][j,7]
                    wedstrijden[i]["visitor_win"] = wedstrijden_gtt[competition][1][j,8]

    return

# def upset(wedstrijden):
#     import numpy as np
#     # only for last season
#     for i in range(len(wedstrijden[0])):
#         # only for games played
#         if wedstrijden[0][i]["played"] == "1":
#             host_win = wedstrijden[0][i]["host_elo"]
#             visitor_win = wedstrijden[0][i]["visitor_elo"]
#             tie = wedstrijden[0][i]["tie_elo"]
#             gd = int(wedstrijden[0][i]["host_goal"]) - int(wedstrijden[0][i]["visitor_goal"])

#             # host win
#             if wedstrijden[0][i]["result"] == "1":
#                 if host_win >= 0.5:
#                     gdx = 10*host_win - 4
#                     upset1 = 25*(host_win-0.5)**2
#                     lh = np.array([[2*gdx,1,0],[gdx**2,gdx,1],[1,1,1]])
#                     rh = np.array([0,0,upset1])
#                     coeff = np.linalg.solve(lh,rh)
#                 else:
#                     gdx = 1
#                     upset3 = -10*host_win+5
#                     lh = np.array([[2*gdx,1,0],[gdx**2,gdx,1],[9,3,1]])
#                     rh = np.array([0,0,upset3])
#                     coeff = np.linalg.solve(lh,rh)

#                 wedstrijden[0][i]["upset"] = (1-host_win)/host_win + coeff[0]*gd**2 + coeff[1]*gd + coeff[2]

#             # visitor win
#             if wedstrijden[0][i]["result"] == "-1": # visitor win
#                 if visitor_win >= 0.5:
#                     gdx = -(10*visitor_win - 4)
#                     upset1 = 25*(visitor_win-0.5)**2
#                     lh = np.array([[2*gdx,1,0],[gdx**2,gdx,1],[1,1,1]])
#                     rh = np.array([0,0,upset1])
#                     coeff = np.linalg.solve(lh,rh)
#                 else:
#                     gdx = -1
#                     upset3 = -10*visitor_win+5
#                     lh = np.array([[2*gdx,1,0],[gdx**2,gdx,1],[1,1,1]])
#                     rh = np.array([0,0,upset3])
#                     coeff = np.linalg.solve(lh,rh)


#                 wedstrijden[0][i]["upset"] = (1-visitor_win)/visitor_win + coeff[0]*gd**2 + coeff[1]*gd + coeff[2]

#             # tie
#             if wedstrijden[0][i]["result"] == "0": # tie
#                 wedstrijden[0][i]["upset"] = max(host_win,visitor_win) / tie

#     return wedstrijden

# def excitement(wedstrijden):
#     # only for last season
#     for i in range(len(wedstrijden[0])):
#         if wedstrijden[0][i]["played"] == "1":
#             # number of times during game that the result changes
#             result_changes = 0
#             number_of_goals = int(wedstrijden[0][i]["host_goal"]) + int(wedstrijden[0][i]["visitor_goal"])
#             # Check for gd not equal to 0 in first minute
#             if sign(int(wedstrijden[0][i]["minute_" + str(1)])) != 0:
#                 result_changes += 1
#             for j in range(1,90):
#                 # Check if league change
#                 if sign(int(wedstrijden[0][i]["minute_" + str(j+1)])) != sign(int(wedstrijden[0][i]["minute_" + str(j)])):
#                     result_changes += abs(sign(int(wedstrijden[0][i]["minute_" + str(j+1)]))) + abs(sign(int(wedstrijden[0][i]["minute_" + str(j)])))

#             wedstrijden[0][i]["excitement"] = result_changes + (wedstrijden[0][i]["upset"]*number_of_goals)**1/2 + wedstrijden[0][i]["upset"]**1/3

#     return wedstrijden

# # For use within excitement function
# def sign(number):
#     """Will return 1 for positive,
#     -1 for negative, and 0 for 0"""
#     try:return number/abs(number)
#     except ZeroDivisionError:return 0