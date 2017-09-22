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

# def game_to_team(panda):

import numpy as np

def make_standing(panda):
    standing = dict()
    # elimination = dict()
    
    groups = sorted(list(set(panda[panda.TYPE.str.contains("Group")].TYPE.str.replace("Group stage ",""))))
    
    for group in groups:
        standing[group] = list()
        
        # Games in this group
        panda_group = panda[panda.TYPE.str.contains(group)]
        
        # Teams
        standing[group].append(sorted(list(set(panda_group.HomeTeam))))
        number_of_teams = len(standing[group][-1])
        
        # Calculate standing
        # Team Index - Games Played - Wins - Losses - Ties - Goals For - Goals Against - Goal Diff - Points
        standing[group].append(np.zeros((number_of_teams,9)))
        # Add Team Index
        for i in range(number_of_teams):
            standing[group][1][i,0] = i
            
        for i in range(len(panda_group)):
            if panda_group.iloc[i].FTHG != "": # Make sure game is played
                # # print("test")
                HTindex = standing[group][0].index(panda_group.iloc[i].HomeTeam)
                ATindex = standing[group][0].index(panda_group.iloc[i].AwayTeam)

                # Add game
                standing[group][1][HTindex,1] += 1
                standing[group][1][ATindex,1] += 1
                
                # Win/Loss/Tie
                if int(panda_group.iloc[i].FTHG) > int(panda_group.iloc[i].FTAG):
                    standing[group][1][HTindex,2] += 1
                    standing[group][1][ATindex,3] += 1
                    
                    # Add points
                    standing[group][1][HTindex,8] += 3
                elif int(panda_group.iloc[i].FTHG) == int(panda_group.iloc[i].FTAG):
                    standing[group][1][HTindex,4] += 1
                    standing[group][1][ATindex,4] += 1  
                    
                    # Add points
                    standing[group][1][HTindex,8] += 1
                    standing[group][1][ATindex,8] += 1
                else:
                    standing[group][1][HTindex,3] += 1
                    standing[group][1][ATindex,2] += 1     
                    
                    # Add points
                    standing[group][1][ATindex,8] += 3
                
                # Goals
                standing[group][1][HTindex,5] += int(panda_group.iloc[i].FTHG)
                standing[group][1][HTindex,6] += int(panda_group.iloc[i].FTAG)
    
                standing[group][1][ATindex,5] += int(panda_group.iloc[i].FTAG)
                standing[group][1][ATindex,6] += int(panda_group.iloc[i].FTHG)
        
        # Goal Difference
        for i in range(len(standing[group][1])):
            standing[group][1][i,7] = standing[group][1][i,5] - standing[group][1][i,6]
            standing[group][1][i,7] = standing[group][1][i,5] - standing[group][1][i,6]
    
    return standing
    
def rank(standing, panda):
    for group in standing.keys():
        # Games in this group
        panda_group = panda[panda.TYPE.str.contains(group)]
        
        # Determine Rank (Add as 8th column)
        # Tiebreakers for Champions League groups, see https://en.wikipedia.org/wiki/2015%E2%80%9316_UEFA_Champions_League_group_stage#Tiebreakers
        # In short:
        # 1. Points
        standing[group][1] = standing[group][1][np.argsort((standing[group][1][:,8]))[::-1]]
        # if group == "Group F":
            # print(standing[group][1]) 
        # Check if there are ties
        s = np.sort(standing[group][1][:,8], axis=None)
        points_tied = np.unique(s[s[1:] == s[:-1]])
        # if group == "Group F":
            # print(points_tied)
            
        # For every tie between multiple teams, calculate standing between these teams
        for point_tie in points_tied:
            teams_tied = []
            teams_tied_names = []
            rank_tied = []
            for i in range(len(standing[group][1])):
                if standing[group][1][i,8] == point_tie:
                    # teams_tied = index of teams_tied
                    teams_tied.append(int(standing[group][1][i,0]))
                    teams_tied_names.append(standing[group][0][teams_tied[-1]])
                    rank_tied.append(i)
            # if group == "Group F":
                # print(teams_tied)     
            # if group == "Group F":
                # print(rank_tied) 
            # Ranking for teams tied
            panda_group_teams_tied = panda_group[(panda_group.HomeTeam.isin(teams_tied_names)) & (panda_group.AwayTeam.isin(teams_tied_names))]
            # if group == "Group F":
                # print(panda_group_teams_tied)            
            # Make standing
            standing_teams_tied = make_standing(panda_group_teams_tied)
            # if group == "Group F":
                # print(standing_teams_tied)
            # Rank based on
            # 1. Points > GD > G+ > Away Goals > GD TOTAL
            if len(teams_tied) == 2:
                # Add Away goals to standing (9th column)
                # Add TOTAL Goal Difference to standing (10th column)
                dummy_ag = []
                dummy_gd = []
                sorted_teams_tied = sorted(zip(teams_tied,teams_tied_names))
                for i in range(len(sorted_teams_tied)):
                    try:
                        dummy_ag.append(int(panda_group_teams_tied[panda_group_teams_tied.AwayTeam == sorted_teams_tied[i][1]]["FTAG"]))
                        for j in range(len(standing[group][1])):
                            if int(standing[group][1][j,0]) == sorted_teams_tied[i][0]:
                                dummy_gd.append(int(standing[group][1][j,7]))
                                break
                    except:
                        pass
                if (len(dummy_ag) == len(teams_tied_names)) & (len(dummy_gd) == len(teams_tied_names)):
                    standing_teams_tied[group][1] = np.c_[ standing_teams_tied[group][1], np.array(dummy_ag), np.array(dummy_gd) ]
                    # standing_teams_tied[group][1] = standing_teams_tied[group][1][np.lexsort((standing_teams_tied[group][1][:,8],standing_teams_tied[group][1][:,7],standing_teams_tied[group][1][:,5],standing_teams_tied[group][1][:,9],standing_teams_tied[group][1][:,10]))[::-1]]
                    standing_teams_tied[group][1] = standing_teams_tied[group][1][np.lexsort((standing_teams_tied[group][1][:,10],standing_teams_tied[group][1][:,9],standing_teams_tied[group][1][:,5],standing_teams_tied[group][1][:,7],standing_teams_tied[group][1][:,8]))[::-1]]
                else:
                    
                    # standing_teams_tied[group][1] = standing_teams_tied[group][1][np.lexsort((standing_teams_tied[group][1][:,8],standing_teams_tied[group][1][:,7],standing_teams_tied[group][1][:,5]))[::-1]]
                    standing_teams_tied[group][1] = standing_teams_tied[group][1][np.lexsort((standing_teams_tied[group][1][:,5],standing_teams_tied[group][1][:,7],standing_teams_tied[group][1][:,8]))[::-1]]
                
            else:
                standing_teams_tied[group][1] = standing_teams_tied[group][1][np.lexsort((standing_teams_tied[group][1][:,5],standing_teams_tied[group][1][:,7],standing_teams_tied[group][1][:,8]))[::-1]]
                
            # if group == "Group F":
                # print(standing_teams_tied[group][1])
            # EXTRA RANKING CRITERIA HERE IF NECESSARY 
            
            # Remap ranking
            # Remap team index
            
            for i in range(len(standing_teams_tied[group][1])):
                standing_teams_tied[group][1][i,0] = standing[group][0].index(standing_teams_tied[group][0][int(standing_teams_tied[group][1][i,0])])
            
            # if group == "Group F":
                # print(standing_teams_tied[group][1])     
                
            # Switches to be made in standing[group][1]
            switches = [] 
            for i in range(len(standing_teams_tied[group][1])):
                if teams_tied[i] != int(standing_teams_tied[group][1][i,0]):
                    current_position = rank_tied[i]
                    # if group == "Group F":
                        # print(current_position)
                    for j in range(len(standing_teams_tied[group][1])):
                        if teams_tied[i] == int(standing_teams_tied[group][1][j,0]):
                            correct_position = rank_tied[i] + (j-i)
                            break
            
                    # if [correct_position,current_position] not in switches:
                    switches.append([current_position,correct_position])
            # if group == "Group F":
                # print(switches)
            
            dummy_ranking = np.zeros(standing[group][1].shape)
            for switch in switches:
                # Not on the correct spot, swith with next one
                dummy_ranking[switch[1],:] = standing[group][1][switch[0],:]
                
            for i in range(len(dummy_ranking)):
                if (dummy_ranking[i,:] == np.zeros(dummy_ranking[i,:].shape)).all():
                    dummy_ranking[i,:] = standing[group][1][i,:]
                # standing[group][1][switch[1],:] , standing[group][1][switch[0],:] = standing[group][1][switch[0],:],standing[group][1][switch[1],:]
            standing[group][1] = dummy_ranking
            # if group == "Group F":
                # print(standing[group][1])       
    return standing