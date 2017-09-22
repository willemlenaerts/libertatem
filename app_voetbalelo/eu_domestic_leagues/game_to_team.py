__author__ = 'Willem Lenaerts'
######################
# input data
######################

# Returns a list of 2 items
# [0]:  List of 2 things
#       [0][0]: Team names of all teams in Jupiler Pro League

# [1]:  Array of size ((games played + games not played) x 5)
#       [1][:,0]: Home Team (As a number, alphabetically as in [0]
#       [1][:,1]: Away Team (As a number, alphabetically as in [0]
#       [1][:,2]: Home Team Goals
#       [1][:,3]: Away Team Goals
#       [1][:,4]: Game already played? (1 = yes, 0 = no)

def game_to_team(game_data_seasons,country_data):
    import numpy as np
    
    ranking_rules = country_data["ranking"]
    output = []
    for game_data in game_data_seasons:
        teams = game_data[0]
        number_of_teams = len(game_data[0])
        game_data = game_data[1]
        # Make ranking
        # Games Played - Wins - Losses - Ties - Goals For - Goals Against - Goal Diff - Points
        team_data = np.zeros((number_of_teams,9))
        for i in range(len(game_data)):
            if game_data[i,4] == 1: # Game played
                # Games played
                team_data[game_data[i,0],0] = team_data[game_data[i,0],0] + 1
                team_data[game_data[i,1],0] = team_data[game_data[i,1],0] + 1
        
                # Goals for and against Host
                team_data[game_data[i,0],4] = team_data[game_data[i,0],4] +  game_data[i,2]
                team_data[game_data[i,0],5] = team_data[game_data[i,0],5] +  game_data[i,3]
        
                # Goals for and against Visitor
                team_data[game_data[i,1],4] = team_data[game_data[i,1],4] +  game_data[i,3]
                team_data[game_data[i,1],5] = team_data[game_data[i,1],5] +  game_data[i,2]
        
                # Goal difference
                team_data[game_data[i,0],6] = team_data[game_data[i,0],6] + game_data[i,2] - game_data[i,3]
                team_data[game_data[i,1],6] = team_data[game_data[i,1],6] - game_data[i,2] + game_data[i,3]
        
                if game_data[i,2] > game_data[i,3]: # Host win
                    # Points
                    team_data[game_data[i,0],7] = team_data[game_data[i,0],7] + 3
        
                    # Win Host
                    team_data[game_data[i,0],1] = team_data[game_data[i,0],1] + 1
        
                    # Loss Visitor
                    team_data[game_data[i,1],2] = team_data[game_data[i,1],2] + 1
                else:
                    if game_data[i,2] == game_data[i,3]: # Tie
                        # Points
                        team_data[game_data[i,0],7] = team_data[game_data[i,0],7] + 1
                        team_data[game_data[i,1],7] = team_data[game_data[i,1],7] + 1
        
                        # Tie Host
                        team_data[game_data[i,0],3] = team_data[game_data[i,0],3] + 1
        
                        # Tie Visitor
                        team_data[game_data[i,1],3] = team_data[game_data[i,1],3] + 1
                    else: # Visitor Win
                        # Points
                        team_data[game_data[i,1],7] = team_data[game_data[i,1],7] + 3
        
                        # Loss Host
                        team_data[game_data[i,0],2] = team_data[game_data[i,0],2] + 1
        
                        # Win Visitor
                        team_data[game_data[i,1],1] = team_data[game_data[i,1],1] + 1
        
        # Determine Rank (Add as 8th column)
        # First add team indices as last column
        team_data = np.c_[ team_data, np.arange(number_of_teams)]
        
        if ranking_rules == [ "Goal Difference", "Wins"]:
            team_data = team_data[np.lexsort((team_data[:,1],team_data[:,6],team_data[:,7]))[::-1]]
        else:
            team_data = team_data[np.lexsort((team_data[:,6],team_data[:,1],team_data[:,7]))[::-1]]
        
        # Add ranking
        team_data[:,8] = np.arange(1,number_of_teams+1)
        team_data = team_data[np.argsort(team_data[:, 9])]
       
        # Make Output
        output.append([teams, game_data, team_data])
    
    # What does module return?
    return output