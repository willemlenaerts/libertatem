def generate_json(games_country,standing_country,montecarlo_country,country,country_data):
    import json
    import numpy as np
    import pandas as pd
    import pulp
    import os
    import ftplib
    from app_voetbalpi.eu_domestic_leagues.functions.milp import milp,milp_forecast
    from app_voetbalpi.eu_domestic_leagues.functions.game_to_team import make_standing, rank
    
    # team.json
    team = dict()
    teams = sorted(list(montecarlo_country.keys()))
    countries = sorted(list(set(games_country.Competition)))
    seasons = sorted(list(set(games_country.Season)))
    number_of_teams = len(teams)
    gamedays = (number_of_teams - 1)*2
    
    # name,elo,standing,elo_evolution,squad_value,...
    decimals = 1
    montecarlo_country = milp(montecarlo_country,decimals = decimals)
    
    team_data = pd.read_csv("app_voetbalpi/eu_domestic_leagues/data/input/team_data.csv")
    for t in teams:
        team[t] = dict()
        team[t]["name"] = t
        team[t]["short_name"] = team_data[team_data.name == t].shortName.astype(str).iloc[0]
        team[t]["squad_value"] = team_data[team_data.name == t].squadMarketValue.astype(str).iloc[0]
        team[t]["odds"] = montecarlo_country[t]
        team[t]["standing"] = standing_country[(standing_country.Season == seasons[-1]) & (standing_country.Team == t)].astype(str).to_dict(orient="list")
        team[t]["odds_champion"] = montecarlo_country[t][0]
        team[t]["odds_ucl"] = np.round(np.sum(montecarlo_country[t][:country_data["cl_spots"]]),decimals)
        team[t]["odds_uel"] = np.round(np.sum(montecarlo_country[t][country_data["cl_spots"]:(country_data["cl_spots"] + country_data["el_spots"])]),decimals)
        team[t]["odds_relegation"] =  np.round(np.sum(montecarlo_country[t][-country_data["degr_spots"]:]),decimals)
        team[t]["color"] = "rgb(0,0,0)" # get from team_data in future
        
        
        games_country_dummy = games_country[(games_country.Season == seasons[-1]) & ((games_country.HomeTeam == t) | (games_country.AwayTeam == t))]
        
        if t == games_country_dummy.iloc[-1].HomeTeam:
            team[t]["Pi_Home"] = round(100*(games_country_dummy.iloc[-1].HomePi_H + games_country_dummy.iloc[-1].dHomePi_H))/100
            team[t]["Pi_Away"] = round(100*(games_country_dummy.iloc[-1].HomePi_A + games_country_dummy.iloc[-1].dHomePi_A))/100
            team[t]["Pi"] = round(100*((team[t]["Pi_Home"] + team[t]["Pi_Away"])/2))/100
        else:
            team[t]["Pi_Home"] = round(100*(games_country_dummy.iloc[-1].AwayPi_H + games_country_dummy.iloc[-1].dAwayPi_H))/100
            team[t]["Pi_Away"] = round(100*(games_country_dummy.iloc[-1].AwayPi_A + games_country_dummy.iloc[-1].dAwayPi_A))/100
            team[t]["Pi"] = round(100*((team[t]["Pi_Home"] + team[t]["Pi_Away"])/2))/100
    
        
        for i in range(len(team[t]["standing"]["GA"])):
            team[t]["standing"]["GA"][i] = str(int(float(team[t]["standing"]["GA"][i])))
            team[t]["standing"]["GD"][i] = str(int(float(team[t]["standing"]["GD"][i])))
            team[t]["standing"]["GF"][i] = str(int(float(team[t]["standing"]["GF"][i])))
        
    # games.json
    games = dict()
    for t in teams:
        games[t] = games_country[(games_country.Season == seasons[-1]) & ((games_country.HomeTeam == t) | (games_country.AwayTeam == t))].astype(str).to_dict(orient="list")
        
        # Make Forecast odds sum to 100%
        games[t] = milp_forecast(games[t],decimals=0)
        
        # Add standing (standing AFTER game)
        current_gameday = int(team[t]["standing"]["GP"][0])
        games[t]["rank"] = []
        for g in range(gamedays):
            if g >= current_gameday:
                games[t]["rank"].append("nan")
                continue
            games_country_gameday = games_country[(games_country.Season == seasons[-1])].sort("Date")[0:int(g*(number_of_teams/2)+ (number_of_teams/2))]
            standing_country_gameday = rank(make_standing(games_country_gameday[(games_country_gameday.Season == seasons[-1])]),country_data)
            games[t]["rank"].append(standing_country_gameday[(standing_country_gameday.Team == t)].R.astype(str).iloc[0])
        
        for i in range(len(games[t]["FTHG"])):
            if games[t]["FTHG"][i] == "nan":
                continue
            games[t]["FTHG"][i] = str(int(float(games[t]["FTHG"][i])))
            games[t]["FTAG"][i] = str(int(float(games[t]["FTAG"][i])))
            games[t]["GD"][i] = str(int(float(games[t]["GD"][i])))
    
    
    # games_table.json
    games_table = list()
    for g in range(gamedays):
        games_country_gameday = games_country[(games_country.Season == seasons[-1])].sort("Date")[int(g*(number_of_teams/2)):int(g*(number_of_teams/2)+ (number_of_teams/2))]
        games_table.append(games_country_gameday.astype(str).to_dict(orient="list"))
        
        # Integer Odds
        games_table[-1] = milp_forecast(games_table[-1],decimals=0)
        
        # Integer Goals
        for i in range(len(games_table[-1]["FTHG"])):
            if games_table[-1]["FTHG"][i] == "nan":
                continue
            games_table[-1]["FTHG"][i] = str(int(float(games_table[-1]["FTHG"][i])))
            games_table[-1]["FTAG"][i] = str(int(float(games_table[-1]["FTAG"][i])))
    
    # games_graph.json
    games_graph = dict()
    games_graph["rank"] = list()
    games_graph["Pi"] = list()
    games_graph["Pi_Home"] = list()
    games_graph["Pi_Away"] = list()
    
    for t in teams:
        games_graph["rank"].append([])
        games_graph["Pi"].append([])
        games_graph["Pi_Home"].append([])
        games_graph["Pi_Away"].append([])
        
        current_gameday = int(team[t]["standing"]["GP"][0])
        for g in range(gamedays):    
            # Rank
            games_graph["rank"][-1].append({"x":g+1,"y": games[t]["rank"][g]})
            
            if g >= current_gameday: 
                games_graph["Pi_Home"][-1].append({"x":g+1,"y": "nan"})
                games_graph["Pi_Away"][-1].append({"x":g+1,"y": "nan"})
                games_graph["Pi"][-1].append({"x":g+1,"y":"nan"})   
    
                continue
            
            # Pi Rating
            games_country_dummy = games_country[(games_country.Season == seasons[-1])].iloc[int(g*(number_of_teams/2)):int(g*(number_of_teams/2)+ (number_of_teams/2))]
            games_country_dummy = games_country_dummy[((games_country_dummy.HomeTeam == t) | (games_country_dummy.AwayTeam == t))]
            
            if len(games_country_dummy) == 0:
                games_graph["Pi_Home"][-1].append({"x":g+1,"y": "nan"})
                games_graph["Pi_Away"][-1].append({"x":g+1,"y": "nan"})
                games_graph["Pi"][-1].append({"x":g+1,"y":"nan"})   
    
                continue
            
            if t == games_country_dummy.iloc[-1].HomeTeam:
                hp = round(100*(games_country_dummy.iloc[-1].HomePi_H + games_country_dummy.iloc[-1].dHomePi_H))/100
                ap = round(100*(games_country_dummy.iloc[-1].HomePi_A + games_country_dummy.iloc[-1].dHomePi_A))/100
                
                games_graph["Pi_Home"][-1].append({"x":g+1,"y": hp})
                games_graph["Pi_Away"][-1].append({"x":g+1,"y": ap})
                games_graph["Pi"][-1].append({"x":g+1,"y":round(100*((hp+ap)/2))/100})
            else:
                hp = round(100*(games_country_dummy.iloc[-1].AwayPi_H + games_country_dummy.iloc[-1].dAwayPi_H))/100
                ap = round(100*(games_country_dummy.iloc[-1].AwayPi_A + games_country_dummy.iloc[-1].dAwayPi_A))/100
                
                games_graph["Pi_Home"][-1].append({"x":g+1,"y": hp})
                games_graph["Pi_Away"][-1].append({"x":g+1,"y": ap})
                games_graph["Pi"][-1].append({"x":g+1,"y":round(100*((hp+ap)/2))/100})     
    
    
    countries_output = dict()
    competition_data = pd.read_csv("app_voetbalpi/eu_domestic_leagues/data/input/competition_data.csv")
    
    countries_output["info"] = [["Country",country], \
                                ["Competition",competition_data[competition_data.country == country].name.iloc[0]],\
                                ["First Season",competition_data[competition_data.country == country].first_season.iloc[0]],\
                                ["Teams",str(int(competition_data[competition_data.country == country].teams.iloc[0]))]]
                                            
    countries_output["png_width"] = str(int(competition_data[competition_data.country == country].png_width.iloc[0]))
    countries_output["png_height"] = str(int(competition_data[competition_data.country == country].png_height.iloc[0]))
      
    # Write json
    if not os.path.exists("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/"):
        os.makedirs("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/")    
    
    json.dump(team,open("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/" + "team.json","w"))
    json.dump(teams,open("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/" + "teams.json","w"))
    json.dump(games,open("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/" + "games.json","w"))
    json.dump(games_table,open("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/" + "games_table.json","w"))
    json.dump(games_graph,open("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/" + "games_graph.json","w"))
    json.dump(countries_output,open("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/" + "country_data.json","w"))
    
    # Write to FTP site
    session = ftplib.FTP('ftp.sway-blog.be','sway-blog.be','Will0870')
    session.cwd('/www/data/pi-domestic-leagues')
    
    if  country in session.nlst():
        session.cwd(country)
    else:
        session.mkd(country)
        session.cwd(country)
        
    # Open data as JSON buffered (only way ftplib works)
    data = open("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/" + "team.json","rb") # file to send
    session.storbinary('STOR team.json', data)     # send the file
    data = open("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/" + "teams.json","rb") # file to send
    session.storbinary('STOR teams.json', data)     # send the file
    data = open("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/" + "games.json","rb") # file to send
    session.storbinary('STOR games.json', data)     # send the file
    data = open("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/" + "games_table.json","rb") # file to send
    session.storbinary('STOR games_table.json', data)     # send the file    
    data = open("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/" + "games_graph.json","rb") # file to send
    session.storbinary('STOR games_graph.json', data)     # send the file 
    data = open("app_voetbalpi/eu_domestic_leagues/data/output/" + country + "/" + "country_data.json","rb") # file to send
    session.storbinary('STOR country_data.json', data)     # send the file 
    session.quit()
