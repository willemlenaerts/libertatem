def montecarlo(games,elo, simulations):
    import numpy as np
    import pandas as pd
    import time
    import random
    import pulp
        
    import scipy.stats # For Poisson Distribution, numpy doesn't have it
    from app_voetbalelo.uefa_euro2016.game_to_team import make_standing, rank, round_of_sixteen, quarterfinals, semifinals, final
    
    games = games.sort_index()
    
    output = dict()
    output_per_game = dict()
    game_numbers = list(games.Game)
    for game_number in game_numbers:
        output_per_game[game_number] = dict()
        output_per_game[game_number]["HomeTeam"] = list()
        output_per_game[game_number]["AwayTeam"] = list()
    
    output_per_team = dict()
    teams = list(set(games[games.Game.astype(int) < 37].HomeTeam))
    for team in teams:
        output_per_team[team] = list()
        
    countries = list(games[~games.Group.str.contains("Final")].HomeTeam) + list(games[~games.Group.str.contains("Final")].AwayTeam)
    countries = sorted(list(set(countries)))
    
    for country in countries:
        # 4th - 3th - 2th - 1st - Knockout - 1/8 win - 1/4 win - 1/2 win - Final win
        output[country] = np.zeros((1,9))
    
    # How many group games are played
    group_games = len(games[games.Group.str.contains("Group")])
    group_games_played = len(games[games.Group.str.contains("Group")].FTHG.dropna())
    
    for simulation in range(simulations):
        start = time.time()
        if simulation == 0:
            print("Starting Montecarlo Simulation ... Calculating Expected Time")
        elif simulation == simulations - 1:
            print("Simulation Finished")
        
        # Simulate Rest of Games
        games_simulated = games.copy(deep=True)
        
        HomeTeam = games_simulated.HomeTeam.values
        HomeElo = games_simulated.HomeElo.values
        AwayTeam = games_simulated.AwayTeam.values
        AwayElo = games_simulated.AwayElo.values
        Group = games_simulated.Group.values
        Game = games_simulated.Game.values
        FTHG = games_simulated.FTHG.values
        FTAG = games_simulated.FTAG.values        
        
        start_group = time.time()
        # First GROUP GAMES
        if group_games_played != group_games:
            # Loop through all games
            for i in range(len(games_simulated)):
                # Check if group game and game not played yet
                if ("Group" in Group[i]) and (np.isnan(FTHG[i])):
                    # There's only Home Field Advantage for France
                    if HomeTeam[i] == "France":
                        home_field_advantage = 80
                    elif AwayTeam[i] == "France":
                        home_field_advantage = -80
                    else:
                        home_field_advantage = 0
                    
                    # ELO calculate expected goals for Home and Away Team
                    W_home_e = 1/(10**(-(HomeElo[i]+home_field_advantage-AwayElo[i])/400)+1)
                    
                    # Expected Goals for Home country
                    if W_home_e < 0.5:
                        home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                    else:
                        home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
                
                    # Expected Goals for the Away country:
                    if W_home_e < 0.8:
                        away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
                    else:
                        away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3
                    
                    # Simulate FTHG and FTAG
                    chances_home_goal = np.zeros((1,15))
                    chances_away_goal = np.zeros((1,15))
                    for goals in range(15):
                        chances_home_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,home_goals)
                        chances_away_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,away_goals)
                    
                    # Make chances sum to 1 (we ignore more than 14 goals)
                    chances_home_goal /=chances_home_goal.sum()
                    chances_away_goal /= chances_away_goal.sum()
                    
                    games_simulated.loc[games_simulated.Game.astype(int) == int(Game[i]),"FTHG"] = np.random.choice(list(range(15)), p=chances_home_goal[0])
                    games_simulated.loc[games_simulated.Game.astype(int) == int(Game[i]),"FTAG"] = np.random.choice(list(range(15)), p=chances_away_goal[0])
                    FTHG[i] = np.random.choice(list(range(15)), p=chances_home_goal[0])
                    FTAG[i] = np.random.choice(list(range(15)), p=chances_away_goal[0])
                
        # Make Standing and Rank 
        standing = rank(make_standing(games_simulated),games_simulated)
        
        # Add to output
        for country in list(standing.Country):
            rank_int = int(standing[standing.Country == country].R)
           # 4th - 3th - 2th - 1st - Knockout - 1/8 win - 1/4 win - 1/2 win - Final - Final win
            output[country][0,4-rank_int] += 1
        
        stop_group = time.time()
        
        # print("Group: " + str(round(1000*(stop_group-start_group))/1000))
        #############
        # 1/8 Finals
        #############
        start_18 = time.time()
        games_simulated = round_of_sixteen(standing,games_simulated)
        
        # Recalibrate some data
        HomeTeam = games_simulated.HomeTeam.values
        HomeElo = games_simulated.HomeElo.values
        AwayTeam = games_simulated.AwayTeam.values
        AwayElo = games_simulated.AwayElo.values        
        HomeWin = games_simulated.HomeWin.values
        AwayWin = games_simulated.AwayWin.values
        Draw = games_simulated.Draw.values         
        for i in range(len(games_simulated)):
            # Check if group game and game not played yet
            if Group[i] == "1/8 Final":
                # There's only Home Field Advantage for France
                if HomeTeam[i] == "France":
                    home_field_advantage = 80
                elif AwayTeam[i] == "France":
                    home_field_advantage = -80
                else:
                    home_field_advantage = 0
                
                # ELO calculate expected goals for Home and Away Team
                HomeElo[i] = elo[HomeTeam[i]]["elo"]
                AwayElo[i] = elo[AwayTeam[i]]["elo"]
                HomeWin[i] = elo[HomeTeam[i]][AwayTeam[i]][0]
                AwayWin[i] = elo[HomeTeam[i]][AwayTeam[i]][2]
                Draw[i] = elo[HomeTeam[i]][AwayTeam[i]][1]
                W_home_e = 1/(10**(-(HomeElo[i]+home_field_advantage-AwayElo[i])/400)+1)
                
                # Expected Goals for Home country
                if W_home_e < 0.5:
                    home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                else:
                    home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
            
                # Expected Goals for the Away country:
                if W_home_e < 0.8:
                    away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
                else:
                    away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3
                
                # Simulate FTHG and FTAG
                chances_home_goal = np.zeros((1,15))
                chances_away_goal = np.zeros((1,15))
                for goals in range(15):
                    chances_home_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,home_goals)
                    chances_away_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,away_goals)
                
                # Make chances sum to 1 (we ignore more than 14 goals)
                chances_home_goal /=chances_home_goal.sum()
                chances_away_goal /= chances_away_goal.sum()
                
                games_simulated.loc[games_simulated.Game.astype(int) == int(Game[i]),"FTHG"] = np.random.choice(list(range(15)), p=chances_home_goal[0])
                games_simulated.loc[games_simulated.Game.astype(int) == int(Game[i]),"FTAG"] = np.random.choice(list(range(15)), p=chances_away_goal[0])
                FTHG[i] = np.random.choice(list(range(15)), p=chances_home_goal[0])
                FTAG[i] = np.random.choice(list(range(15)), p=chances_away_goal[0])        
        
        stop_18 =time.time()
        # print("18F: " + str(round(1000*(stop_18-start_18))/1000))
        #############
        # Quarter Finals
        #############
        start_qf = time.time()
        games_simulated = quarterfinals(games_simulated)
        stop_qf = time.time()
        # print("QF 1: " +  str(round(1000*(stop_qf-start_qf))/1000))
        
        start_qf = time.time()
        HomeTeam = games_simulated.HomeTeam.values
        HomeElo = games_simulated.HomeElo.values
        AwayTeam = games_simulated.AwayTeam.values
        AwayElo = games_simulated.AwayElo.values         
        HomeWin = games_simulated.HomeWin.values
        AwayWin = games_simulated.AwayWin.values
        Draw = games_simulated.Draw.values         
        for i in range(len(games_simulated)):
            # Check if group game and game not played yet
            if Group[i] == "Quarter Final":
                # There's only Home Field Advantage for France
                if HomeTeam[i] == "France":
                    home_field_advantage = 80
                elif AwayTeam[i] == "France":
                    home_field_advantage = -80
                else:
                    home_field_advantage = 0
                
                # ELO calculate expected goals for Home and Away Team
                HomeElo[i] = elo[HomeTeam[i]]["elo"]
                AwayElo[i] = elo[AwayTeam[i]]["elo"]
                HomeWin[i] = elo[HomeTeam[i]][AwayTeam[i]][0]
                AwayWin[i] = elo[HomeTeam[i]][AwayTeam[i]][2]
                Draw[i] = elo[HomeTeam[i]][AwayTeam[i]][1]
                W_home_e = 1/(10**(-(HomeElo[i]+home_field_advantage-AwayElo[i])/400)+1)
                
                # Expected Goals for Home country
                if W_home_e < 0.5:
                    home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                else:
                    home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
            
                # Expected Goals for the Away country:
                if W_home_e < 0.8:
                    away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
                else:
                    away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3
                
                # Simulate FTHG and FTAG
                chances_home_goal = np.zeros((1,15))
                chances_away_goal = np.zeros((1,15))
                for goals in range(15):
                    chances_home_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,home_goals)
                    chances_away_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,away_goals)
                
                # Make chances sum to 1 (we ignore more than 14 goals)
                chances_home_goal /=chances_home_goal.sum()
                chances_away_goal /= chances_away_goal.sum()
                
                games_simulated.loc[games_simulated.Game.astype(int) == int(Game[i]),"FTHG"] = np.random.choice(list(range(15)), p=chances_home_goal[0])
                games_simulated.loc[games_simulated.Game.astype(int) == int(Game[i]),"FTAG"] = np.random.choice(list(range(15)), p=chances_away_goal[0])
                FTHG[i] = np.random.choice(list(range(15)), p=chances_home_goal[0])
                FTAG[i] = np.random.choice(list(range(15)), p=chances_away_goal[0])          
        
        stop_qf = time.time()
        # print("QF 3: " +  str(round(1000*(stop_qf-start_qf))/1000)) 
        # print("QF: " + str(round(1000*(stop_qf-start_qf))/1000))
        #############
        # Semi Finals
        #############
        start_sf = time.time()
        games_simulated = semifinals(games_simulated)
        
        # Recalibrate some data
        HomeTeam = games_simulated.HomeTeam.values
        HomeElo = games_simulated.HomeElo.values
        AwayTeam = games_simulated.AwayTeam.values
        AwayElo = games_simulated.AwayElo.values         
        HomeWin = games_simulated.HomeWin.values
        AwayWin = games_simulated.AwayWin.values
        Draw = games_simulated.Draw.values         
        for i in range(len(games_simulated)):
            # Check if group game and game not played yet
            if Group[i] == "Semi Final":
                # There's only Home Field Advantage for France
                if HomeTeam[i] == "France":
                    home_field_advantage = 80
                elif AwayTeam[i] == "France":
                    home_field_advantage = -80
                else:
                    home_field_advantage = 0
                
                # ELO calculate expected goals for Home and Away Team
                HomeElo[i] = elo[HomeTeam[i]]["elo"]
                AwayElo[i] = elo[AwayTeam[i]]["elo"]
                HomeWin[i] = elo[HomeTeam[i]][AwayTeam[i]][0]
                AwayWin[i] = elo[HomeTeam[i]][AwayTeam[i]][2]
                Draw[i] = elo[HomeTeam[i]][AwayTeam[i]][1]
                W_home_e = 1/(10**(-(HomeElo[i]+home_field_advantage-AwayElo[i])/400)+1)
                
                # Expected Goals for Home country
                if W_home_e < 0.5:
                    home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                else:
                    home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
            
                # Expected Goals for the Away country:
                if W_home_e < 0.8:
                    away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
                else:
                    away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3
                
                # Simulate FTHG and FTAG
                chances_home_goal = np.zeros((1,15))
                chances_away_goal = np.zeros((1,15))
                for goals in range(15):
                    chances_home_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,home_goals)
                    chances_away_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,away_goals)
                
                # Make chances sum to 1 (we ignore more than 14 goals)
                chances_home_goal /=chances_home_goal.sum()
                chances_away_goal /= chances_away_goal.sum()
                
                games_simulated.loc[games_simulated.Game.astype(int) == int(Game[i]),"FTHG"] = np.random.choice(list(range(15)), p=chances_home_goal[0])
                games_simulated.loc[games_simulated.Game.astype(int) == int(Game[i]),"FTAG"] = np.random.choice(list(range(15)), p=chances_away_goal[0])
                FTHG[i] = np.random.choice(list(range(15)), p=chances_home_goal[0])
                FTAG[i] = np.random.choice(list(range(15)), p=chances_away_goal[0])           
        
        stop_sf = time.time()
        # print("SF: " + str(round(1000*(stop_sf-start_sf))/1000))
        #############
        # Final
        #############
        start_f = time.time()
        games_simulated = final(games_simulated)
        
        # Recalibrate some data
        HomeTeam = games_simulated.HomeTeam.values
        HomeElo = games_simulated.HomeElo.values
        AwayTeam = games_simulated.AwayTeam.values
        AwayElo = games_simulated.AwayElo.values         
        HomeWin = games_simulated.HomeWin.values
        AwayWin = games_simulated.AwayWin.values
        Draw = games_simulated.Draw.values         
        for i in range(len(games_simulated)):
            # Check if group game and game not played yet
            if Group[i] == "Final":
                # There's only Home Field Advantage for France
                if HomeTeam[i] == "France":
                    home_field_advantage = 80
                elif AwayTeam[i] == "France":
                    home_field_advantage = -80
                else:
                    home_field_advantage = 0
                
                # ELO calculate expected goals for Home and Away Team
                HomeElo[i] = elo[HomeTeam[i]]["elo"]
                AwayElo[i] = elo[AwayTeam[i]]["elo"]
                HomeWin[i] = elo[HomeTeam[i]][AwayTeam[i]][0]
                AwayWin[i] = elo[HomeTeam[i]][AwayTeam[i]][2]
                Draw[i] = elo[HomeTeam[i]][AwayTeam[i]][1]
                W_home_e = 1/(10**(-(HomeElo[i]+home_field_advantage-AwayElo[i])/400)+1)
                
                # Expected Goals for Home country
                if W_home_e < 0.5:
                    home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                else:
                    home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
            
                # Expected Goals for the Away country:
                if W_home_e < 0.8:
                    away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
                else:
                    away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3
                
                # Simulate FTHG and FTAG
                chances_home_goal = np.zeros((1,15))
                chances_away_goal = np.zeros((1,15))
                for goals in range(15):
                    chances_home_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,home_goals)
                    chances_away_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,away_goals)
                
                # Make chances sum to 1 (we ignore more than 14 goals)
                chances_home_goal /=chances_home_goal.sum()
                chances_away_goal /= chances_away_goal.sum()
                
                games_simulated.loc[games_simulated.Game.astype(int) == int(Game[i]),"FTHG"] = np.random.choice(list(range(15)), p=chances_home_goal[0])
                games_simulated.loc[games_simulated.Game.astype(int) == int(Game[i]),"FTAG"] = np.random.choice(list(range(15)), p=chances_away_goal[0])
                FTHG[i] = np.random.choice(list(range(15)), p=chances_home_goal[0])
                FTAG[i] = np.random.choice(list(range(15)), p=chances_away_goal[0])      
            
        stop_f = time.time()
        # print("Final: " + str(round(1000*(stop_f-start_f))/1000))
        
        start_output = time.time()
        # Add 1/8, QF, SF, F to output
        # 4th - 3th - 2th - 1st - Knockout - 1/8 win - 1/4 win - 1/2 win - Final win
        round_of_sixteen_finalists = list(games_simulated[(games_simulated.Group == "1/8 Final")].HomeTeam) + list(games_simulated[(games_simulated.Group == "1/8 Final")].AwayTeam) 
        round_of_sixteen_finalists = list(set(round_of_sixteen_finalists))
        quarter_finalists = list(games_simulated[(games_simulated.Group == "Quarter Final")].HomeTeam) + list(games_simulated[(games_simulated.Group == "Quarter Final")].AwayTeam) 
        quarter_finalists = list(set(quarter_finalists))
        semi_finalists = list(games_simulated[(games_simulated.Group == "Semi Final")].HomeTeam) + list(games_simulated[(games_simulated.Group == "Semi Final")].AwayTeam) 
        semi_finalists = list(set(semi_finalists))
        finalists = list(games_simulated[(games_simulated.Group == "Final")].HomeTeam) + list(games_simulated[(games_simulated.Group == "Final")].AwayTeam) 
        finalists = list(set(finalists))   
        if int(games_simulated[(games_simulated.Group == "Final")].FTHG.iloc[0]) > int(games_simulated[(games_simulated.Group == "Final")].FTAG.iloc[0]):
            winner = games_simulated[(games_simulated.Group == "Final")].HomeTeam.iloc[0]
        elif int(games_simulated[(games_simulated.Group == "Final")].FTHG.iloc[0]) < int(games_simulated[(games_simulated.Group == "Final")].FTAG.iloc[0]):
            winner = games_simulated[(games_simulated.Group == "Final")].AwayTeam.iloc[0]
        else:
            winner = random.choice([games_simulated[(games_simulated.Group == "Final")].HomeTeam.iloc[0],games_simulated[(games_simulated.Group == "Final")].AwayTeam.iloc[0]])
        for country in list(standing.Country):
            if country in round_of_sixteen_finalists:
                output[country][0,4] += 1            
            
            if country in quarter_finalists:
                output[country][0,5] += 1
                
            if country in semi_finalists:
                output[country][0,6] += 1
        
            if country in finalists:
                output[country][0,7] += 1
        
            if country == winner:
                output[country][0,8] += 1
        stop_output = time.time()
        # print("Output: " + str(round(1000*(stop_output-start_output))/1000))
    
        start_output_pg = time.time()
        for game_number in game_numbers:
            output_per_game[game_number]["HomeTeam"].append(games_simulated[games_simulated.Game == game_number].HomeTeam.iloc[0])
            output_per_game[game_number]["AwayTeam"].append(games_simulated[games_simulated.Game == game_number].AwayTeam.iloc[0])
        stop_output_pg = time.time()
        # print("Output per game: " + str(round(1000*(stop_output_pg-start_output_pg))/1000))
        
        start_output_pt = time.time()
        for team in teams:
            output_per_team[team].append(games_simulated[((games_simulated.HomeTeam == team) | (games_simulated.AwayTeam == team)) & (games_simulated.Game.astype(int) >= 37)].Game.tolist())
        stop_output_pt = time.time()
        # print("Output per team: " + str(round(1000*(stop_output_pt-start_output_pt))/1000))
                
        stop = time.time()
        if (simulation != 0) and (simulation%(simulations/10) == 0):
            print("Simulation " + str(simulation) + "/" + str(simulations) + " -- ET: " + str(round((stop-start)*(simulations-simulation)/60)) + " minutes")  
            
    # Average
    for country in output.keys():
        output[country] = output[country]/simulations
    
    # Output per team
    team_data = dict()
    for team in teams:
        team_data[team] = dict()
        for i in range(len(output_per_team[team])):
            for j in range(len(output_per_team[team][i])):
                if j == 0:
                    if output_per_team[team][i][j] in team_data[team].keys():
                        team_data[team][output_per_team[team][i][j]] += 1
                    else:
                        team_data[team][output_per_team[team][i][j]] = 1
                else:
                    if output_per_team[team][i][j-1] + "_to_" + output_per_team[team][i][j] in team_data[team].keys():
                        team_data[team][output_per_team[team][i][j-1] + "_to_" + output_per_team[team][i][j]] += 1
                    else:
                        team_data[team][output_per_team[team][i][j-1] + "_to_" + output_per_team[team][i][j]] = 1
        
        for key in team_data[team].keys():
            team_data[team][key] = team_data[team][key]/simulations
            
    # Output per game
    # For every game, most probable HomeTeam/AwayTeam/Game
    from collections import Counter
    
    game_data = dict()
    for game_number in game_numbers:
        game_data[game_number] = dict()
        game_data[game_number]["HomeTeam"] = [ite for ite, it in Counter(output_per_game[game_number]["HomeTeam"]).most_common(1)][0]
        game_data[game_number]["AwayTeam"] = [ite for ite, it in Counter(output_per_game[game_number]["AwayTeam"]).most_common(1)][0]
        
        game_dummy = []
        for i in range(len(output_per_game[game_number]["HomeTeam"])):
            game_dummy.append(output_per_game[game_number]["HomeTeam"][i] + " - " + output_per_game[game_number]["AwayTeam"][i])
        
        game_data[game_number]["Game"] = [ite for ite, it in Counter(game_dummy).most_common(1)][0]
        
    return [output,game_data,team_data]