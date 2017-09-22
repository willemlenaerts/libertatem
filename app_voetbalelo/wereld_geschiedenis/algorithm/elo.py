def elo(games):
    import numpy as np
    import scipy.stats # For Poisson Distribution, numpy doesn't have it4
    import time
    import datetime
    
    # Remove wrong elements from games
    # games = games[(games.FTHG != "") & (games.FTHG.str.len() <= 2) & (games.FTAG.str.len() <= 2)]              
    count = 0
    for i in range(len(games.index)):
        
        # if count == 0:
        start = time.time()
        # Get relevent data from this row
        date = games.index[i]
        home_team = games.HomeTeam[i]
        away_team = games.AwayTeam[i]
        type_game = games.TYPE[i]
        game_played = 1
        try:
            home_goals = int(games.FTHG[i])
            away_goals = int(games.FTAG[i])
        except ValueError:
            # Match not played, abandoned,...
            game_played = 0
        
        # Check the previous rows for occurence of the home and away team
        try:
            # Test: was home team vorige match home of away team
            if  games[(games.HomeTeam == home_team) & (games.index < games.index[i] )].sort_index(ascending = False).index[0] >\
                games[(games.AwayTeam == home_team) & (games.index < games.index[i] )].sort_index(ascending = False).index[0]:
                
                elo_start_home = games[(games.HomeTeam == home_team) & (games.index < games.index[i] )].sort_index(ascending = False).HomeElo[0]
            else:
                elo_start_home = games[(games.AwayTeam == home_team) & (games.index < games.index[i] )].sort_index(ascending = False).AwayElo[0]
        except IndexError:
            first_game_home_team = games[(games.HomeTeam == home_team) | (games.AwayTeam == home_team)].sort_index(ascending = True).index[0]
            if first_game_home_team.value/1000000000 < datetime.datetime(1925, 1, 1,0,0).timestamp():
                elo_start_home = 1500
            elif first_game_home_team.value/1000000000 < datetime.datetime(1950, 1, 1,0,0).timestamp():
                elo_start_home = 1400
            elif first_game_home_team.value/1000000000 < datetime.datetime(1975, 1, 1,0,0).timestamp():
                elo_start_home = 1300
            elif first_game_home_team.value/1000000000 >= datetime.datetime(1975, 1, 1,0,0).timestamp():
                elo_start_home = 1200
        try:
            # Test: was away team vorige match home of away team
            if  games[(games.HomeTeam == away_team) & (games.index < games.index[i] )].sort_index(ascending = False).index[0] >\
                games[(games.AwayTeam == away_team) & (games.index < games.index[i] )].sort_index(ascending = False).index[0]:
                
                elo_start_away = games[(games.HomeTeam == away_team) & (games.index < games.index[i] )].sort_index(ascending = False).HomeElo[0]
            else:
        
                elo_start_away = games[(games.AwayTeam == away_team) & (games.index < games.index[i] )].sort_index(ascending = False).AwayElo[0]
        except IndexError:
            first_game_away_team = games[(games.HomeTeam == away_team) | (games.AwayTeam == away_team)].sort_index(ascending = True).index[0]
            if first_game_away_team.value/1000000000 < datetime.datetime(1925, 1, 1,0,0).timestamp():
                elo_start_away = 1500
            elif first_game_away_team.value/1000000000 < datetime.datetime(1950, 1, 1,0,0).timestamp():
                elo_start_away = 1400
            elif first_game_away_team.value/1000000000 < datetime.datetime(1975, 1, 1,0,0).timestamp():
                elo_start_away = 1300
            elif first_game_away_team.value/1000000000 >= datetime.datetime(1975, 1, 1,0,0).timestamp():
                elo_start_away = 1200
        
        # Start Elo algorithm
        ########################################################################
        # Parameters
        ########################################################################
        # Parameters form www.eloratings.net/system.html
        worldcups = [   (1930, "Uruguay"),(1934,"Italy"),(1938,"France"),(1950,"Brazil"),(1954,"Switzerland"),
                        (1958,"Sweden"),(1962, "Chile"),(1966,"England"),(1970,"Mexico"),(1974,"Germany FR"),
                        (1978, "Argentina"),(1982,"Spain"),(1986,"Mexico"),(1990,"Italy"),(1994,"USA"),
                        (1998,"France"),(2002,"Japan"),(2002,"Korea Republic"),(2006,"Germany"),(2010,"South Africa"),(2014,"Brazil")]
                        
        if game_played == 1:
            
            if type_game == "Friendly":
                K = 20
                home_field_advantage = 50
            elif type_game == 'FIFA World Cup™ Final':
                games_worldcup = games[(games.TYPE =='FIFA World Cup™ Final')][datetime.datetime(date.year-1,1,1):datetime.datetime(date.year+1,1,1)]
                final_delta = games_worldcup.index[-1]-date
                
                # Check if game is third place playoff (this is equal to friendly)
                # This game is played 1 day before final, therefore check final_delta == 1
                if home_team == games_worldcup.iloc[-2].HomeTeam and\
                    away_team == games_worldcup.iloc[-2].AwayTeam and\
                    final_delta == 1:
                    K = 20
                else:
                    K = 60
                for worldcup in worldcups:
                    if home_team == worldcup[1] and\
                    datetime.datetime.fromtimestamp(date.value/1000000000) > datetime.datetime(worldcup[0]-1,1,1,0,0) and \
                    datetime.datetime.fromtimestamp(date.value/1000000000) < datetime.datetime(worldcup[0]+1,1,1,0,0):
                        home_field_advantage = 80
                    elif away_team == worldcup[1] and\
                    datetime.datetime.fromtimestamp(date.value/1000000000) > datetime.datetime(worldcup[0]-1,1,1,0,0) and \
                    datetime.datetime.fromtimestamp(date.value/1000000000) < datetime.datetime(worldcup[0]+1,1,1,0,0):
                        home_field_advantage = -80
                    else:
                        home_field_advantage = 0
            elif type_game == 'FIFA World Cup™ Qualifier' or type_game == 'Continental Qualifier':
                K = 40
                home_field_advantage = 80
            elif type_game == 'Continental Final' or type_game == 'Olympic Football Tournament Final' or type_game == 'FIFA Confederations Cup':
                K = 50
                home_field_advantage = 0
            elif type_game == 'Olympic Football Tournament Quali 1908-1956':
                K = 30
                home_field_advantage = 60
            elif type_game == "FIFA Confederations Cup":
                K = 40
                home_field_advantage = 0                
        
            # Calculate W_home, W_away and G parameter for game
            if home_goals > away_goals: # Home Win
                W_home = 1
                W_away = 0
            if home_goals == away_goals: # Draw
                W_home = 0.5
                W_away = 0.5
            if home_goals < away_goals: # Away Win
                W_home = 0
                W_away = 1
            
            # G
            if home_goals == away_goals or abs(home_goals - away_goals) == 1: # Draw or 1 goal difference
                G = 1
            else:
                if abs(home_goals - away_goals) == 2: # 2 goals difference
                    G = 3/2
                elif abs(home_goals - away_goals) == 3: # 3 goals difference
                    G = 7/4
                else: # 3 or more goals difference
                    G =  1 + 3/4 + (abs(home_goals - away_goals)-3)/8
            
            # max goals (for poisson distribution calculation)
            max_goals = 16
        
            ########################################################################
            # Calculations
            ########################################################################  
            # Elo & dElo
            W_home_e = 1/(10**(-(elo_start_home + home_field_advantage-elo_start_away)/400)+1)
            games.loc[(games.index == games.index[i]) & (games["HomeTeam"] == home_team),"HomeElo"] = elo_start_home + K*G*(W_home-W_home_e)
            
            W_away_e = 1/(10**(-(elo_start_away-home_field_advantage-elo_start_home)/400)+1)
            games.loc[(games.index == games.index[i]) & (games["AwayTeam"] == away_team),"AwayElo"] = elo_start_away + K*G*(W_away-W_away_e)
            
            games.loc[(games.index == games.index[i]) & (games["AwayTeam"] == away_team),"dElo"] = np.round(abs(elo_start_away - games.loc[(games.index == games.index[i]) & (games["AwayTeam"] == away_team),"AwayElo"]).astype(float))             
            # Win/Draw/Loss expectancy
            # First estimate expected goals
            # Goals for Home team:
            if W_home_e < 0.5:
                home_goals_est = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
            else:
                home_goals_est = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
            
            # Goals for the Away team:
            if W_home_e < 0.8:
                away_goals_est = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
            else:
                away_goals_est = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3       
            
            # Now use poisson distribution to determine for each team the chance it scores x goals
            # Combine these for both teams to calculate Win/Loss/Draw expectancy
            home_win_exp = 0
            away_win_exp = 0
            draw_exp = 0
            exp = np.zeros((1, 3))
            for j in range(max_goals):
                for k in range(max_goals):
                    if j > k:
                        # Home Win
                       exp[0,0] = exp[0,0]  + scipy.stats.distributions.poisson.pmf(j,home_goals_est)*scipy.stats.distributions.poisson.pmf(k,away_goals_est)
                    if j == k:
                        # Tie
                       exp[0,1] = exp[0,1] + scipy.stats.distributions.poisson.pmf(j,home_goals_est)*scipy.stats.distributions.poisson.pmf(k,away_goals_est)
                    if j < k:
                        # Away Win
                       exp[0,2] = exp[0,2] + scipy.stats.distributions.poisson.pmf(j,home_goals_est)*scipy.stats.distributions.poisson.pmf(k,away_goals_est)   
                      
            # Make sure probabilities sum up to 1
            exp /= exp.sum()
            
            games.loc[(games.index == games.index[i]) & (games["HomeTeam"] == home_team),"HomeWinExp"] = exp[0,0]
            games.loc[(games.index == games.index[i]) & (games["HomeTeam"] == home_team),"DrawExp"]= exp[0,1]
            games.loc[(games.index == games.index[i]) & (games["HomeTeam"] == home_team),"AwayWinExp"] = exp[0,2]
        
        else:
            # Game not played for some reason, ELO doortrekken
            games.loc[(games.index == games.index[i]) & (games["HomeTeam"] == home_team),"HomeElo"] = elo_start_home
            games.loc[(games.index == games.index[i]) & (games["AwayTeam"] == away_team),"AwayElo"] = elo_start_away
            games.loc[(games.index == games.index[i]) & (games["AwayTeam"] == away_team),"dElo"] = np.round(abs(elo_start_away - games.loc[(games.index == games.index[i]) & (games["AwayTeam"] == away_team),"AwayElo"]).astype(float))
            
            
        # if count == 0:
        stop = time.time()
        print("One iteration: " + str(stop-start) + " s")
        print("Remaining time: " + str((stop-start)*(len(games)-count-1)) + " s")
        
        if count%100:
            print("Progress: " + str(count+1) + "/" + str(len(games))) 
        
        count += 1

    return games