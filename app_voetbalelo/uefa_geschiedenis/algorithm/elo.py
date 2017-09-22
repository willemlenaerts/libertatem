def elo(panda):
    import numpy as np
    import scipy.stats # For Poisson Distribution, numpy doesn't have it4
    import time
    
    count = 0
    season_check = ""
    
    # Goals per game adjustments
    seasons = sorted(list(panda["S"].unique()))
    gpg = dict()
    gpg_totaal = []
    for season in seasons:
        gpg[season] = (sum(panda[panda.S == season]["FTHG"].astype(float)) + sum(panda[panda.S == season]["FTHG"].astype(float)))/len(panda[panda.S == season])
        gpg_totaal.append(gpg[season])
    
    gpg_totaal_avg = sum(gpg_totaal)/len(gpg_totaal)

    for i in range(len(panda.index)):
        
        # if count == 0:
        start = time.time()
        # Get relevent data from this row
        date = panda.index[i]
        season = panda.S[i]
        home_team = panda.HomeTeam[i]
        away_team = panda.AwayTeam[i]
        home_goals = int(panda.FTHG[i])
        away_goals = int(panda.FTAG[i])
        
        # Check the previous rows for occurence of the home and away team
        try:
            # Test: was home team vorige match home of away team
            if  panda[(panda.HomeTeam == home_team) & (panda.index < panda.index[i] )].sort_index(ascending = False).index[0] >\
                panda[(panda.AwayTeam == home_team) & (panda.index < panda.index[i] )].sort_index(ascending = False).index[0]:
                if panda.S[i] != season_check: # Season changed:
                    # Calculate how much of previous season should be taken in new calculation
                    season_diff = int(panda.S[i].split("-")[0]) - int(season_check.split("-")[0])
                    overflow = (3/16)*season_diff + (0.25 - 3/16)
                    if overflow > 1:
                        overflow = 1
                    
                    elo_start_home =(1-overflow)*panda[(panda.HomeTeam == home_team) & (panda.index < panda.index[i] )].sort_index(ascending = False).HomeElo[0] + overflow*1500
                else:
                    elo_start_home = panda[(panda.HomeTeam == home_team) & (panda.index < panda.index[i] )].sort_index(ascending = False).HomeElo[0]
            else:
                if panda.S[i] != season_check: # Season changed:    
                    elo_start_home = (1-overflow)*panda[(panda.AwayTeam == home_team) & (panda.index < panda.index[i] )].sort_index(ascending = False).AwayElo[0] + overflow*1500
                else:
                    elo_start_home = panda[(panda.AwayTeam == home_team) & (panda.index < panda.index[i] )].sort_index(ascending = False).AwayElo[0]
        except IndexError:
            elo_start_home = 1500
        try:
            # Test: was away team vorige match home of away team
            if  panda[(panda.HomeTeam == away_team) & (panda.index < panda.index[i] )].sort_index(ascending = False).index[0] >\
                panda[(panda.AwayTeam == away_team) & (panda.index < panda.index[i] )].sort_index(ascending = False).index[0]:
                if panda.S[i] != season_check: # Season changed:    
                    # Calculate how much of previous season should be taken in new calculation
                    season_diff = int(panda.S[i].split("-")[0]) - int(season_check.split("-")[0])
                    overflow = (3/16)*season_diff + (0.25 - 3/16)
                    if overflow > 1:
                        overflow = 1
                        
                    elo_start_away = (1-overflow)*panda[(panda.HomeTeam == away_team) & (panda.index < panda.index[i] )].sort_index(ascending = False).HomeElo[0] + overflow*1500
                else:
                    elo_start_away = panda[(panda.HomeTeam == away_team) & (panda.index < panda.index[i] )].sort_index(ascending = False).HomeElo[0]
            else:
                if panda.S[i] != season_check: # Season changed:    
                    elo_start_away = (1-overflow)*panda[(panda.AwayTeam == away_team) & (panda.index < panda.index[i] )].sort_index(ascending = False).AwayElo[0] + overflow*1500
                else:
                    elo_start_away = panda[(panda.AwayTeam == away_team) & (panda.index < panda.index[i] )].sort_index(ascending = False).AwayElo[0]
        except IndexError:
            elo_start_away = 1500
        
        # Start Elo algorithm
        ########################################################################
        # Parameters
        ########################################################################
        K = 50
        home_field_advantage = 84 # http://clubelo.com/HFA/ for belgium
        
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
                G = (3/2)*(gpg_totaal_avg/gpg[season])
            else: # 3 or more goals difference
                G = ((11 + abs(home_goals - away_goals))/8)*(gpg_totaal_avg/gpg[season])
        
        # max goals (for poisson distribution calculation)
        max_goals = 16
        
        ########################################################################
        # Calculations
        ########################################################################  
        # Elo & dElo
        W_home_e = 1/(10**(-(elo_start_home + home_field_advantage-elo_start_away)/400)+1)
        panda.loc[(panda.index == panda.index[i]) & (panda["HomeTeam"] == home_team),"HomeElo"] = elo_start_home + K*G*(W_home-W_home_e)
        
        W_away_e = 1/(10**(-(elo_start_away-home_field_advantage-elo_start_home)/400)+1)
        panda.loc[(panda.index == panda.index[i]) & (panda["AwayTeam"] == away_team),"AwayElo"] = elo_start_away + K*G*(W_away-W_away_e)
        
        panda.loc[(panda.index == panda.index[i]) & (panda["AwayTeam"] == away_team),"dElo"] = np.round(abs(elo_start_away - panda.loc[(panda.index == panda.index[i]) & (panda["AwayTeam"] == away_team),"AwayElo"]))
        
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
        
        panda.loc[(panda.index == panda.index[i]) & (panda["HomeTeam"] == home_team),"HomeWinExp"] = exp[0,0]
        panda.loc[(panda.index == panda.index[i]) & (panda["HomeTeam"] == home_team),"DrawExp"]= exp[0,1]
        panda.loc[(panda.index == panda.index[i]) & (panda["HomeTeam"] == home_team),"AwayWinExp"] = exp[0,2]
        
        # if count == 0:
        stop = time.time()
        print("One iteration: " + str(stop-start) + " s")
        print("Remaining time: " + str((stop-start)*(len(panda)-count-1)) + " s")
        
        if count%100:
            print("Progress: " + str(count+1) + "/" + str(len(panda))) 
        
        count += 1
        season_check = panda.S[i]

    return panda