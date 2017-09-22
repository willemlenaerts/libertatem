__author__ = 'Exergos'
######################
# Input?
######################

# output[season][game] =    dict()
#                           output[season][game]["game_date"]
#                           output[season][game]["game_hour"]
#                           output[season][game]["host"]
#                           output[season][game]["visitor"]
#                           output[season][game]["host_goal"]
#                           output[season][game]["visitor_goal"]
#                           output[season][game]["referee"]
#                           output[season][game]["stadium"]
#                           output[season][game]["spectators"]
#                           output[season][game]["host_goal_data"]
#                           output[season][game]["visitor_goal_data"]
#                           output[season][game]["host_yellow_card_data"]
#                           output[season][game]["visitor_yellow_card_data"]
#                           output[season][game]["host_red_card_data"]
#                           output[season][game]["visitor_red_card_data"]
#                           output[season][game]["host_starting_team"]
#                           output[season][game]["visitor_starting_team"]
#                           output[season][game]["host_substitution"]
#                           output[season][game]["visitor_substitution"]
#                           output[season][game]["host_manager"]
#                           output[season][game]["visitor_manager"]
#                           output[season][game]["minute_x with x from 1 tot 90
#                           output[season][game]["minute_x_host"] with x from 1 tot 90
#                           output[season][game]["minute_x_tie"] with x from 1 tot 90
#                           output[season][game]["minute_x_visitor"] with x from 1 tot 90

######################
# What does it return?
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

def game_to_team(wedstrijden):
    # Loop over all competitions
    competitions = ["rs","poi","poii_a","poii_b","poiii"]
    
    # Save output
    output = dict()
    
    for competition in competitions:
        # Get some parameters
        games_played = []
        speeldagen = [] # list van speeldagen (nummers)
        for i in range(len(wedstrijden)):
            if wedstrijden[i]["played"] == True and wedstrijden[i]["competition"] == competition:
                games_played.append(i)
                speeldagen.append(int(wedstrijden[i]["speeldag"].split(" ")[1]))
        speeldagen = list(set(speeldagen))
        
        if competition == "rs":
            total_games = 16*15
            
        if competition == "poi":
            total_games = 6*5
            
        if competition == "poii_a":
            total_games = 4*3
            
        if competition == "poii_b":
            total_games = 4*3
            
        if competition == "poiii":
            total_games = 5
            
        # Get team names & indices
        team_names = []
        for i in range(len(wedstrijden)):
            if wedstrijden[i]["competition"] == competition:
                team_names.append(wedstrijden[i]["host"])
        team_names = sorted(set(team_names))
        
        # Make sure team indices are consistent over all competitions
        if competition == "rs":
            team_names_all = team_names
        team_indices = []
        for i in range(len(team_names)):
            for j in range(len(team_names_all)):
                if team_names[i] == team_names_all[j]:
                    team_indices.append(j)
        
        number_of_teams = len(team_names)
        
        # Sort games based on date
        import time
        dates = []
        dates_index = []
        for i in range(len(wedstrijden)):
            if wedstrijden[i]["competition"] == competition:
                dates.append(wedstrijden[i]["game_date"])
                dates_index.append(i)
        
        dates_sort_index = [dates_index for (dates,dates_index) in sorted(zip(dates,dates_index))]
        # dates_sort_index = [i[0] for i in sorted(enumerate(dates), key=lambda x:x[1])]
        
        # Get game_data
        # Host team index - Visiting team index - Host goals - Visitor Goals - Played - Speeldag
        import numpy as np
        game_data = np.zeros((total_games, 6))
        count_games = 0
        for i in dates_sort_index:
            for j in range(number_of_teams):
                if wedstrijden[i]["host"] == team_names[j]:
                    game_data[count_games,0] = team_indices[j]
                    
                if wedstrijden[i]["visitor"] == team_names[j]:
                    game_data[count_games,1] = team_indices[j]
                    
            if wedstrijden[i]["played"] == True:
                game_data[count_games,2] = int(wedstrijden[i]["host_goal"])
                game_data[count_games,3] = int(wedstrijden[i]["visitor_goal"])
                game_data[count_games,4] = 1
            game_data[count_games,5] = int(wedstrijden[i]["speeldag"].split(" ")[1]) 
            count_games = count_games + 1
        
        # Make ranking
        # Games Played - Wins - Losses - Ties - Goals For - Goals Against - Goal Diff - Points
        ranking = np.zeros((number_of_teams,9))
        
        # Adjust ranking for playoffs I and III
        if competition == "poi":
            for i in range(len(team_indices)):
                ranking[i,7] = np.ceil(output["rs"][2][:,7]/2)[int(team_indices[i])]
                
        if competition == "poiii":
            if output["rs"][2][:,8][int(team_indices[0])] < output["rs"][2][:,8][int(team_indices[1])]:
                ranking[0,7] = 3     
            else:
                ranking[1,7] = 3
        
        # Make ranking
        # Save each step of ranking and points in evolution list
        ranking_evolution = [[] for x in range(number_of_teams)]
        points_evolution = [[] for x in range(number_of_teams)]
        for speeldag in speeldagen:
            for i in range(len(game_data)):
                if game_data[i,4] == 1 and game_data[i,5] == speeldag: # Wedstrijd gespeeld op deze speeldag
                    # Get correct indices
                    for j in range(len(team_indices)):
                        if game_data[i,0] == team_indices[j]:
                            host_index = j
                        if game_data[i,1] == team_indices[j]:
                            visitor_index = j
                    # Games played
                    ranking[host_index,0] = ranking[host_index,0] + 1
                    ranking[visitor_index,0] = ranking[visitor_index,0] + 1
            
                    # Goals for and against Host
                    ranking[host_index,4] = ranking[host_index,4] +  game_data[i,2]
                    ranking[host_index,5] = ranking[host_index,5] +  game_data[i,3]
            
                    # Goals for and against Visitor
                    ranking[visitor_index,4] = ranking[visitor_index,4] +  game_data[i,3]
                    ranking[visitor_index,5] = ranking[visitor_index,5] +  game_data[i,2]
            
                    # Goal difference
                    ranking[host_index,6] = ranking[host_index,6] + game_data[i,2] - game_data[i,3]
                    ranking[visitor_index,6] = ranking[visitor_index,6] - game_data[i,2] + game_data[i,3]
            
                    if game_data[i,2] > game_data[i,3]: # Host win
                        # Points
                        ranking[host_index,7] = ranking[host_index,7] + 3
            
                        # Win Host
                        ranking[host_index,1] = ranking[host_index,1] + 1
            
                        # Loss Visitor
                        ranking[visitor_index,2] = ranking[visitor_index,2] + 1
                    else:
                        if game_data[i,2] == game_data[i,3]: # Tie
                            # Points
                            ranking[host_index,7] = ranking[host_index,7] + 1
                            ranking[visitor_index,7] = ranking[visitor_index,7] + 1
            
                            # Tie Host
                            ranking[host_index,3] = ranking[host_index,3] + 1
            
                            # Tie Visitor
                            ranking[visitor_index,3] = ranking[visitor_index,3] + 1
                        else: # Visitor Win
                            # Points
                            ranking[visitor_index,7] = ranking[visitor_index,7] + 3
            
                            # Loss Host
                            ranking[host_index,2] = ranking[host_index,2] + 1
            
                            # Win Visitor
                            ranking[visitor_index,1] = ranking[visitor_index,1] + 1
                    
            # Determine ranking
            ranking_speeldag = ranking
            # Determine Rank (Add as 8th column)
            # First by points
            ranking_speeldag[:,8] = np.argsort(ranking_speeldag[:, 7])[::-1]
            
            # Then by W (column
            for i in range(len(ranking_speeldag)-1):
                # If points equal
                if ranking_speeldag[ranking_speeldag[i,8],7] == ranking_speeldag[ranking_speeldag[i+1,8],7]:
                    # Check wins
                    if ranking_speeldag[ranking_speeldag[i,8],1] < ranking_speeldag[ranking_speeldag[i+1,8],1]:
                        # If i+1 has more wins than i, change ranking_speeldag
                        # ranking_speeldag[ranking_speeldag[i,8],8],ranking_speeldag[ranking_speeldag[i+1,8],8] = ranking_speeldag[ranking_speeldag[i+1,8],8],ranking_speeldag[ranking_speeldag[i,8],8]
                        ranking_speeldag[i,8],ranking_speeldag[i+1,8] = ranking_speeldag[i+1,8],ranking_speeldag[i,8]
                        continue
                    else:
                        # If wins also equal
                        if ranking_speeldag[ranking_speeldag[i,8],1] == ranking_speeldag[ranking_speeldag[i+1,8],1]:
                            # Check Goal Difference
                            if ranking_speeldag[ranking_speeldag[i,8],6] < ranking_speeldag[ranking_speeldag[i+1,8],6]:
                                # If i+1 has better GD than i, change ranking_speeldag
                                # ranking_speeldag[ranking_speeldag[i,8],8],ranking_speeldag[ranking_speeldag[i+1,8],8]= ranking_speeldag[ranking_speeldag[i+1,8],8],ranking_speeldag[ranking_speeldag[i,8],8]
                                ranking_speeldag[i,8],ranking_speeldag[i+1,8] = ranking_speeldag[i+1,8],ranking_speeldag[i,8]
                                continue
            
                                # Then by GD
            
                                # Then by GF
            
            # Map indices back to league ranking_speeldag
            dummy = np.zeros((1,number_of_teams))
            for i in range(len(ranking_speeldag)):
                dummy[0,ranking_speeldag[i,8]] = i+1
            ranking_speeldag[:,8] = dummy
                        
            # sla ranking_evolution en points_evolution op
            for i in range(number_of_teams):
                points_evolution[i].append(ranking_speeldag[i,7])
                ranking_evolution[i].append(ranking_speeldag[i,8])
        
        # als er nog geen speeldagen geweest zijn
        if not speeldagen:
            # Determine ranking
            ranking_speeldag = ranking
            # Determine Rank (Add as 8th column)
            # First by points
            ranking_speeldag[:,8] = np.argsort(ranking_speeldag[:, 7])[::-1]
            
            # Then by W (column
            for i in range(len(ranking_speeldag)-1):
                # If points equal
                if ranking_speeldag[ranking_speeldag[i,8],7] == ranking_speeldag[ranking_speeldag[i+1,8],7]:
                    # Check wins
                    if ranking_speeldag[ranking_speeldag[i,8],1] < ranking_speeldag[ranking_speeldag[i+1,8],1]:
                        # If i+1 has more wins than i, change ranking_speeldag
                        # ranking_speeldag[ranking_speeldag[i,8],8],ranking_speeldag[ranking_speeldag[i+1,8],8] = ranking_speeldag[ranking_speeldag[i+1,8],8],ranking_speeldag[ranking_speeldag[i,8],8]
                        ranking_speeldag[i,8],ranking_speeldag[i+1,8] = ranking_speeldag[i+1,8],ranking_speeldag[i,8]
                        continue
                    else:
                        # If wins also equal
                        if ranking_speeldag[ranking_speeldag[i,8],1] == ranking_speeldag[ranking_speeldag[i+1,8],1]:
                            # Check Goal Difference
                            if ranking_speeldag[ranking_speeldag[i,8],6] < ranking_speeldag[ranking_speeldag[i+1,8],6]:
                                # If i+1 has better GD than i, change ranking_speeldag
                                # ranking_speeldag[ranking_speeldag[i,8],8],ranking_speeldag[ranking_speeldag[i+1,8],8]= ranking_speeldag[ranking_speeldag[i+1,8],8],ranking_speeldag[ranking_speeldag[i,8],8]
                                ranking_speeldag[i,8],ranking_speeldag[i+1,8] = ranking_speeldag[i+1,8],ranking_speeldag[i,8]
                                continue
            
                                # Then by GD
            
                                # Then by GF
            
            # Map indices back to league ranking_speeldag
            dummy = np.zeros((1,number_of_teams))
            for i in range(len(ranking_speeldag)):
                dummy[0,ranking_speeldag[i,8]] = i+1
            ranking_speeldag[:,8] = dummy                
                        
                        
        
        ranking = ranking_speeldag 
        
        
        # Save everything to output dict
        output[competition] = list([list([team_names,team_indices]), game_data, ranking, ranking_evolution,points_evolution])

    # What does module return?
    return output