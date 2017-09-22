# Get input data for ELO ranking & Montecarlo Analysis of
# Domestic Leagues around Europe

# Data from http://www.football-data.co.uk/

# Function get_games_data() returns game data for every league in urls

# Input is urls, a list of lists consisting of:
# [0]: Name of country
# [1]: url

# Output is games panda with columns:
# HomeTeam - AwayTeam - FTHG - FTAG - Date

def get_games_data(country, country_data,number_of_seasons):
    from urllib import request
    import numpy as np
    import pandas as pd
    import datetime
    import http.client
    import json
    
    output_games = dict()
    output_games["HomeTeam"] = []
    output_games["AwayTeam"] = []
    output_games["FTHG"] = []
    output_games["FTAG"] = []
    output_games["HomeWinLine"] = []
    output_games["AwayWinLine"] = []
    output_games["TieLine"] = []
    output_games["Date"] = []    
    output_games["Season"] = []
    output_games["Competition"] = []
    
    start_year = int(country_data["url"].split("/")[-2][0:2])
    end_year = int(country_data["url"].split("/")[-2][2:4])
    
    if len(str(start_year)) == 1:
        start_year_string = "0" + str(start_year)
    else:
        start_year_string = str(start_year)
    
    if len(str(end_year)) == 1:
        end_year_string = "0" + str(end_year)
    else:
        end_year_string = str(end_year)
        
    no_bet_line = 0
    for season in range(number_of_seasons):
        
        if len(str(start_year-season)) == 1:
            start_year_season_string = "0" + str(start_year-season)
        else:
            start_year_season_string = str(start_year-season)
    
        if len(str(end_year-season)) == 1:
            end_year_season_string = "0" + str(end_year-season)
        else:
            end_year_season_string = str(end_year-season)
        # First for the current season
        url = country_data["url"].replace(start_year_string + end_year_string, \
                                            start_year_season_string+end_year_season_string)
        response = request.urlopen(url)
            
        csv = response.read()
        
        # Save the string to a file
        csvstr = str(csv).strip("b'")
        
        lines = csvstr.split("\\n")
        f = open("app_betting/data/Games_" + country + "_" + \
                str(start_year) +str(end_year) + ".csv", "w")
        for line in lines:
           f.write(line.replace('"',"") + "\n")
        f.close() 
        
        # Now make list of lists (lines) to continue calculation
        import csv
        with open("app_betting/data/Games_" + country + "_" + \
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
                    for j in range(len(games_dummy[0])):
                        if i == 0:
                            games[games_dummy[i][j]] = list()
                        else:
                            if j < len(games_dummy[i]):
                                games[games_dummy[0][j]].append(games_dummy[i][j].lstrip().rstrip())
                            else:
                                games[games_dummy[0][j]].append(None)
        
        # 2. Create output_games
        # First find all teams
        teams = games["HomeTeam"] + games["AwayTeam"]
        teams = list(set(teams))
        teams.sort()
    
        # Make games_array
        number_of_teams = len(teams)
        total_games = len(teams)**2 - len(teams)
        games_played = len(games["HomeTeam"])
        games_array = np.zeros((total_games, 5))
        games_played_combinations = []
        
        # Priority of bookmakers
        bookmakers_all = ["BW","B365","GB","IW"]
        bookmakers = []
        
        # Check if they are in games data
        for bookmaker in bookmakers_all:
            if (bookmaker + "H") in games.keys():
                bookmakers.append(bookmaker)
    
        for i in range(games_played):
            games_played_combinations.append((teams.index(games["HomeTeam"][i]),teams.index(games["AwayTeam"][i]))) 
            
            output_games["HomeTeam"].append(games["HomeTeam"][i].lstrip().rstrip())
            output_games["AwayTeam"].append(games["AwayTeam"][i].lstrip().rstrip())
            output_games["FTHG"].append(int(games["FTHG"][i].lstrip().rstrip()))
            output_games["FTAG"].append(int(games["FTAG"][i].lstrip().rstrip()))
            if len(games["Date"][i].lstrip().rstrip().split("/")[-1]) == 2:
                output_games["Date"].append(datetime.datetime.strptime(games["Date"][i].lstrip().rstrip(), '%d/%m/%y'))
            else:
                output_games["Date"].append(datetime.datetime.strptime(games["Date"][i].lstrip().rstrip(), '%d/%m/%Y'))
            
            if (start_year-season) < 30:
                output_games["Season"].append(str(2000 + start_year-season) + "-" + end_year_season_string)
            else:
                output_games["Season"].append(str(1900 + start_year-season) + "-" + end_year_season_string)
            output_games["Competition"].append(country)
            
            # Add Bookmaker Lines
            # Home
            line_added = False
            for bookmaker in bookmakers:
                if games[bookmaker + "H"][i] != "":
                    output_games["HomeWinLine"].append(float(games[bookmaker + "H"][i] .lstrip().rstrip()))
                    line_added = True
                    break
            
            if not line_added:
                no_bet_line += 1
                output_games["HomeWinLine"].append(None)
    
            # Tie
            line_added = False
            for bookmaker in bookmakers:
                if games[bookmaker + "D"][i] != "":
                    output_games["TieLine"].append(float(games[bookmaker + "D"][i] .lstrip().rstrip()))
                    line_added = True
                    break
            
            if not line_added:
                no_bet_line += 1
                output_games["TieLine"].append(None)
                
            # Away
            line_added = False
            for bookmaker in bookmakers:
                if games[bookmaker + "A"][i] != "":
                    output_games["AwayWinLine"].append(float(games[bookmaker + "A"][i] .lstrip().rstrip()))
                    line_added = True
                    break
            
            if not line_added:
                no_bet_line += 1
                output_games["AwayWinLine"].append(None)
    
                    
        # Extend games_array with games not played
        import itertools
        all_games_combinations = list(itertools.permutations(list(range(number_of_teams)), 2))
        
        dummy = games_played_combinations + all_games_combinations
        games_to_play_combinations = []
        for d in dummy:
            if dummy.count(d) == 1:
                games_to_play_combinations.append(d)
        
        for i in range(len(games_to_play_combinations)):
            output_games["HomeTeam"].append(teams[int(games_to_play_combinations[i][0])].lstrip().rstrip())
            output_games["AwayTeam"].append(teams[int(games_to_play_combinations[i][1])].lstrip().rstrip())
            output_games["FTHG"].append(None)
            output_games["FTAG"].append(None)
            output_games["HomeWinLine"].append(None)
            output_games["AwayWinLine"].append(None)
            output_games["TieLine"].append(None)
            output_games["Date"].append(None)
            if (start_year-season) < 30:
                output_games["Season"].append(str(2000 + start_year-season) + "-" + end_year_season_string)
            else:
                output_games["Season"].append(str(1900 + start_year-season) + "-" + end_year_season_string)
            output_games["Competition"].append(country)
            
    # Convert to Pandas
    output_games = pd.DataFrame(output_games)
    output_games = output_games.sort("Date")
    seasons = sorted(list(set(output_games.Season)))
    
    # Add api.football-data.org data for last season
    
    connection = http.client.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': '8e69a754c2da4e6aa86118ea3da2517a', 'X-Response-Control': 'minified' }
    games_this_season = []
    
    soccerseasons = pd.read_csv("app_voetbalpi/eu_domestic_leagues/data/input/country_conversion.csv")
    for i in range(len(soccerseasons)):
        if soccerseasons["name_fd.co.uk"].iloc[i] == country:
            id_soccerseason = soccerseasons["id_api.fd.org"].iloc[i].astype(str)
            
            connection.request('GET', '/v1/soccerseasons/' + id_soccerseason + "/fixtures", None, headers )
            response = json.loads(connection.getresponse().read().decode())
            for f in response["fixtures"]:
                games_this_season.append(f)
            
    # Add data to output_games
    clubname_conversions = pd.read_csv("app_voetbalpi/eu_domestic_leagues/data/input/clubname_conversion.csv")
    
    for i in range(len(clubname_conversions)):
        output_games.loc[output_games.HomeTeam == clubname_conversions["name_fd.co.uk"].iloc[i],"HomeTeam"] = clubname_conversions["name_api.fd.org"].iloc[i]
        output_games.loc[output_games.AwayTeam == clubname_conversions["name_fd.co.uk"].iloc[i],"AwayTeam"] = clubname_conversions["name_api.fd.org"].iloc[i]
    
    # Change date of future games
    for game in games_this_season:
        output_games.loc[(output_games.Season == seasons[-1]) & (output_games.HomeTeam == game["homeTeamName"]) & (output_games.AwayTeam == game["awayTeamName"]),"Date"] = datetime.datetime.strptime(game["date"], '%Y-%m-%dT%H:%M:%SZ')

    # Get team data
    connection = http.client.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': '8e69a754c2da4e6aa86118ea3da2517a', 'X-Response-Control': 'minified' }
    teams_this_season = []
    
    soccerseasons = pd.read_csv("app_voetbalpi/eu_domestic_leagues/data/input/country_conversion.csv")
    for i in range(len(soccerseasons)):
        if soccerseasons["name_fd.co.uk"].iloc[i] == country:
            id_soccerseason = soccerseasons["id_api.fd.org"].iloc[i].astype(str)
            
            connection.request('GET', '/v1/soccerseasons/' + id_soccerseason + "/teams", None, headers )
            response = json.loads(connection.getresponse().read().decode())
            for f in response["teams"]:
                teams_this_season.append(f)    
    
    
    output_teams = pd.DataFrame(teams_this_season)
    
    # Add new teams to team_data
    team_data = pd.read_csv("app_voetbalpi/eu_domestic_leagues/data/input/team_data.csv")
    teams_to_write = list(set(output_teams.name) - set(team_data.name))
    with open("app_voetbalpi/eu_domestic_leagues/data/input/team_data.csv", 'a') as f:
        output_teams[output_teams.name.isin(teams_to_write)].to_csv(f, header=False,index=False)

    start_year_string = seasons[0].split("-")[0]
    end_year_string = str(int(seasons[-1].split("-")[0]) + 1)
    
    print("Acquired Game Data for " + country + " for Period " + start_year_string + "-" + end_year_string + " || " + str(no_bet_line) + " Betting Lines Missing")
    return [output_games,output_teams]