# Get input data for ELO ranking & Montecarlo Analysis of
# Domestic Leagues around Europe

# Data from http://www.football-data.co.uk/

# Function get_games_data() returns game data for every league in urls

# Input is urls, a list of lists consisting of:
# [0]: Name of country
# [1]: url

# Output is a list of 2 things:
# [0]:  Team names of all teams in Domestic League
# [1]:  Numpy Array of size (total games x 4)
#       [1][:,0]: Home Team (As a number, alphabetically as in [0]
#       [1][:,1]: Away Team (As a number, alphabetically as in [0]
#       [1][:,2]: Home Team Goals
#       [1][:,3]: Away Team Goals
#       [1][:,4]: Game already played (1 = yes, 0 = no)

def get_games_data(country, country_data,number_of_seasons):
    from urllib import request
    import numpy as np
    
    output = []
    
    for season in range(number_of_seasons):
        output.append([])
        # First for the current season
        if season == 0:
            start_year = int(country_data["url"].split("/")[-2][0:2])
            end_year = int(country_data["url"].split("/")[-2][2:4])
            # Get data and save as csv
            response = request.urlopen(country_data["url"])
        
        # Now for previous seasons
        else:
            start_year -= 1
            end_year -= 1
            
            url = country_data["url"].replace(str(start_year+1) + str(end_year+1), \
                                                str(start_year)+str(end_year))
            response = request.urlopen(url)
            
        csv = response.read()
        
        # Save the string to a file
        csvstr = str(csv).strip("b'")
        
        lines = csvstr.split("\\n")
        f = open("app_voetbalelo/eu_domestic_leagues/data/Games_" + country + "_" + \
                str(start_year) +str(end_year) + ".csv", "w")
        for line in lines:
           f.write(line.replace('"',"") + "\n")
        f.close() 
        
        # Now make list of lists (lines) to continue calculation
        import csv
        with open("app_voetbalelo/eu_domestic_leagues/data/Games_" + country + "_" + \
                    str(start_year) +str(end_year)  + ".csv", "rt") as f:
            reader = csv.reader(f)
            games_dummy = list(reader)
        
        games = dict()
        for i in range(len(games_dummy)):
            if games_dummy[i] != []:
                # If no FTHG or FTAG data, continue
                if games_dummy[i][4] == "" or games_dummy[i][5] == "":
                    continue
                else:
                    for j in range(len(games_dummy[i])):
                        if i == 0:
                            games[games_dummy[i][j]] = list()
                        else:
                            games[games_dummy[0][j]].append(games_dummy[i][j].lstrip().rstrip())
        
        # 2. Create output
        # Output is a list of 2 things:
        # [0]:  Team names of all teams in Domestic League
        # [1]:  Numpy Array of size (total games x 4)
        #       [1][:,0]: Home Team (As a number, alphabetically as in [0]
        #       [1][:,1]: Away Team (As a number, alphabetically as in [0]
        #       [1][:,2]: Home Team Goals
        #       [1][:,3]: Away Team Goals
        #       [1][:,4]: Game already played (1 = yes, 0 = no)
        
        
        # First find all teams
        teams = games["HomeTeam"] + games["AwayTeam"]
        teams = list(set(teams))
        teams.sort()
        output[-1].append(teams)
        
        # Make games_array
        number_of_teams = len(teams)
        total_games = len(teams)**2 - len(teams)
        games_played = len(games["HomeTeam"])
        games_array = np.zeros((total_games, 5))
        games_played_combinations = []
        for i in range(games_played):
            games_played_combinations.append((teams.index(games["HomeTeam"][i]),teams.index(games["AwayTeam"][i]))) 
            
            games_array[i,0] = teams.index(games["HomeTeam"][i])
            games_array[i,1] = teams.index(games["AwayTeam"][i])
            games_array[i,2] = int(games["FTHG"][i])
            games_array[i,3] = int(games["FTAG"][i])
            games_array[i,4] = 1
        
        # Extend games_array with games not played
        import itertools
        all_games_combinations = list(itertools.permutations(list(range(number_of_teams)), 2))
        
        dummy = games_played_combinations + all_games_combinations
        games_to_play_combinations = []
        for d in dummy:
            if dummy.count(d) == 1:
                games_to_play_combinations.append(d)
        
        for i in range(len(games_to_play_combinations)):
            games_array[games_played+i,0] = games_to_play_combinations[i][0]
            games_array[games_played+i,1] = games_to_play_combinations[i][1]
            
        output[-1].append(games_array)

    return output