def elo(games):
    import numpy as np
    import pandas as pd
    import scipy.stats # For Poisson Distribution, numpy doesn't have it
    import time
    
    # Sort games from earliest to most recent
    games = games.sort_values("Date")
    games = games.reset_index(drop=True)
    
    # sLength = len(games)
    # games.loc[:,'HomeElo'] = pd.Series(np.zeros(sLength), index=games.index)
    # games.loc[:,'AwayElo'] = pd.Series(np.zeros(sLength), index=games.index)
    # games.loc[:,'dElo'] = pd.Series(np.zeros(sLength), index=games.index)
    # games.loc[:,'Elo_HomeWin'] = pd.Series(np.zeros(sLength), index=games.index)
    # games.loc[:,'Elo_AwayWin'] = pd.Series(np.zeros(sLength), index=games.index)
    # games.loc[:,'Elo_TieWin'] = pd.Series(np.zeros(sLength), index=games.index)
    
    # Numpify data necessary for calculation from games pandas
    number_of_games = len(games)
    HomeTeam = games.HomeTeam.values
    AwayTeam = games.AwayTeam.values
    FTHG = games.FTHG.values
    FTAG = games.FTAG.values
    Date = games.Date.values
    
    # Output
    HomeElo = np.empty(number_of_games) * np.nan
    AwayElo  = np.empty(number_of_games) * np.nan
    dElo = np.empty(number_of_games) * np.nan
    Elo_HomeWin = np.empty(number_of_games) * np.nan
    Elo_AwayWin = np.empty(number_of_games) * np.nan
    Elo_Tie = np.empty(number_of_games) * np.nan

    # Elo Rating System Parameters
    # K = Weight attributed to game (the higher, the higher dElo)
    K = 40
    # Home Field Advantage (is being added to the HomeTeam)
    home_field_advantage = 84 # http://clubelo.com/HFA/ for belgium
    
    # Timing parameters
    interval = 10*round(number_of_games/100)
    
    for i in range(number_of_games):
        # Check if game already played
        if np.isnan(FTHG[i]):
            continue
        
        # Timing
        start = time.time()
        
        # Find last Elo rating of HomeTeam
        try:
            last_HomeTeam_index = np.max(np.where(HomeTeam[(np.where(~np.isnan(HomeElo)))] == HomeTeam[i]))
        except:
            last_HomeTeam_index = 0
        
        try:
            last_AwayTeam_index = np.max(np.where(AwayTeam[(np.where(~np.isnan(AwayElo)))] == HomeTeam[i]))
        except:
            last_AwayTeam_index = 0
        
        if last_HomeTeam_index > last_AwayTeam_index:
            HomeElo[i] = HomeElo[last_HomeTeam_index] + dElo[last_HomeTeam_index] 
        elif last_AwayTeam_index > last_HomeTeam_index:
            HomeElo[i] = AwayElo[last_AwayTeam_index] - dElo[last_AwayTeam_index]          
        else:
            # Both 0, therefore initialize Elo Rating
            HomeElo[i] = 1500.0

        # Find last Elo rating of AwayTeam
        try:
            last_HomeTeam_index = np.max(np.where(HomeTeam[(np.where(~np.isnan(HomeElo)))] == HomeTeam[i]))
        except:
            last_HomeTeam_index = 0
        
        try:
            last_AwayTeam_index = np.max(np.where(AwayTeam[(np.where(~np.isnan(AwayElo)))] == HomeTeam[i]))
        except:
            last_AwayTeam_index = 0
        
        if last_HomeTeam_index > last_AwayTeam_index:
            AwayElo[i] = HomeElo[last_HomeTeam_index] + dElo[last_HomeTeam_index] 
        elif last_AwayTeam_index > last_HomeTeam_index:
            AwayElo[i] = AwayElo[last_AwayTeam_index] - dElo[last_AwayTeam_index]          
        else:
            # Both 0, therefore initialize Elo Rating
            AwayElo[i] = 1500.0
            
        ########################################################################
        ########################################################################
        # Calculate dElo
        ########################################################################
        # G (More goals == Bigger dElo)
        if FTHG[i] == FTAG[i] or abs(FTHG[i] - FTAG[i] ) == 1: # Draw or 1 goal difference
            G = 1
        else:
            if abs(FTHG[i] - FTAG[i]) == 2: # 2 goals difference
                G = 3/2
            else: # 3 or more goals difference
                G = (11 + abs(FTHG[i] - FTAG[i]))/8        

        ######################################################################## 
        # Calculation
        # W = Result of the Game
        if FTHG[i] > FTAG[i]: # Home Win
            W = 1
        elif FTHG[i] == FTAG[i]: # Draw
            W = 0.5
        else: # Away Win
            W = 0
        
        # Rating Difference = Elo difference between HomeTeam and AwayTeam
        rating_difference = HomeElo[i] + home_field_advantage - AwayElo[i]
        
        # We = Expected Result of the Game
        We = 1/(10**(-rating_difference/400)+1)
        
        # dElo
        dElo[i] = K*G*(W-We)
        ########################################################################
        ########################################################################
        # Calculate Win/Tie/Loss Expectancy
        # First calculate Expected Goals of HomeTeam and AwayTeam
        if We < 0.5:
            expected_fthg_game = 0.2 + 1.1*np.sqrt(We/0.5)
        else:
            expected_fthg_game = 1.69 / (1.12*np.sqrt(2 - We/0.5)+0.18)
        if We < 0.8:
            expected_ftag_game = -0.96 + 1/(0.1+0.44*np.sqrt((We+0.1)/0.9))
        else:
            expected_ftag_game = 0.72*np.sqrt((1 - We)/0.3)+0.3        
        
        # For a range of expected fthg and ftag, calculate probability using Poisson distribution
        Elo_HomeWin[i] = 0
        Elo_AwayWin[i] = 0
        Elo_Tie[i] = 0
        for fthg in range(15):
            for ftag in range(15):     
                if fthg > ftag:
                    Elo_HomeWin[i] += scipy.stats.distributions.poisson.pmf(fthg,expected_fthg_game)*scipy.stats.distributions.poisson.pmf(ftag,expected_ftag_game)
                elif fthg == ftag:
                    Elo_Tie[i] += scipy.stats.distributions.poisson.pmf(fthg,expected_fthg_game)*scipy.stats.distributions.poisson.pmf(ftag,expected_ftag_game)
                else:
                    Elo_AwayWin[i] += scipy.stats.distributions.poisson.pmf(fthg,expected_fthg_game)*scipy.stats.distributions.poisson.pmf(ftag,expected_ftag_game)
        
        # Make sure probabilities sum up to 1 (otherwise problem for montecarlo simulation)
        dummy = np.array([Elo_HomeWin[i],Elo_Tie[i], Elo_AwayWin[i]])
        dummy /= dummy.sum()                    
        Elo_HomeWin[i] = dummy[0]
        Elo_AwayWin[i] = dummy[2]
        Elo_Tie[i] = dummy[1]
        
        ########################################################################
        # Timing
        stop = time.time()
        if (i%interval == 0) or (i == (len(games) - 1)):
            print("Game " + str(i) + "/" + str(len(games)) + " || RT: " + str(round((len(games) - i) * (stop-start))) + " seconds")
            
            
    # Add to games pandas
    games.loc[:,'HomeElo'] = pd.Series(HomeElo, index=games.index)
    games.loc[:,'AwayElo'] = pd.Series(AwayElo, index=games.index)
    games.loc[:,'dElo'] = pd.Series(dElo, index=games.index)
    games.loc[:,'Elo_HomeWin'] = pd.Series(Elo_HomeWin, index=games.index)
    games.loc[:,'Elo_AwayWin'] = pd.Series(Elo_AwayWin, index=games.index)    
    games.loc[:,'Elo_Tie'] = pd.Series(Elo_Tie, index=games.index)    
    
    return games
    
def pi(games,l,g,use_pi_probability_distribution=False):
    import numpy as np
    import pandas as pd
    import scipy.stats # For Poisson Distribution, numpy doesn't have it
    import time
    import math
    import pickle
    
    # Sort games from earliest to most recent
    games = games.sort_values("Date")
    games = games.reset_index(drop=True)
    
    # Numpify data necessary for calculation from games pandas
    number_of_games = len(games)
    HomeTeam = games.HomeTeam.values
    AwayTeam = games.AwayTeam.values
    FTHG = games.FTHG.values
    FTAG = games.FTAG.values
    Date = games.Date.values
    
    # Output
    GD = np.empty(number_of_games) * np.nan
    GDe = np.empty(number_of_games) * np.nan
    HomePi = np.empty(number_of_games) * np.nan
    HomePi_H = np.empty(number_of_games) * np.nan
    HomePi_A = np.empty(number_of_games) * np.nan
    AwayPi = np.empty(number_of_games) * np.nan
    AwayPi_H = np.empty(number_of_games) * np.nan
    AwayPi_A = np.empty(number_of_games) * np.nan
    dHomePi = np.empty(number_of_games) * np.nan
    dHomePi_H = np.empty(number_of_games) * np.nan
    dHomePi_A = np.empty(number_of_games) * np.nan
    dAwayPi = np.empty(number_of_games) * np.nan
    dAwayPi_H = np.empty(number_of_games) * np.nan
    dAwayPi_A = np.empty(number_of_games) * np.nan
    Pi_HomeWin = np.empty(number_of_games) * np.nan
    Pi_AwayWin = np.empty(number_of_games) * np.nan
    Pi_Tie = np.empty(number_of_games) * np.nan
    Pi_delta = np.empty(number_of_games) * np.nan
    # Parameters of Pi Rating System
    c = 3
    sd_gd = 1.75
    
    # Timing parameters
    interval = 10*round(number_of_games/50)
    
    # pi_probability_distribution
    if use_pi_probability_distribution:
        pi_probability_distribution = pickle.load(open("app_betting/result/pi_probability_distribution.p","rb"))
    for i in range(number_of_games):
        # Check if game already played
        if np.isnan(FTHG[i]):
            continue
        
        # Timing
        start = time.time()
        
        # game_index = games.index[i]
        # ht_game = games.iloc[i]["HomeTeam"]
        # at_game = games.iloc[i]["AwayTeam"]
        # fthg_game = games.iloc[i]["FTHG"]
        # ftag_game = games.iloc[i]["FTAG"]
        
        # Find last Pi rating of HomeTeam
        try:
            last_HomeTeam_index = np.max(np.where(HomeTeam[(np.where(~np.isnan(HomePi)))] == HomeTeam[i]))
        except:
            last_HomeTeam_index = 0
        
        try:
            last_AwayTeam_index = np.max(np.where(AwayTeam[(np.where(~np.isnan(AwayPi)))] == HomeTeam[i]))
        except:
            last_AwayTeam_index = 0
        
        if last_HomeTeam_index > last_AwayTeam_index:
            HomePi_H[i] = HomePi_H[last_HomeTeam_index] + dHomePi_H[last_HomeTeam_index]
            HomePi_A[i] = HomePi_A[last_HomeTeam_index] + dHomePi_A[last_HomeTeam_index]
            HomePi[i] = (HomePi_H[i] + HomePi_A[i])/2        
        elif last_AwayTeam_index > last_HomeTeam_index:
            HomePi_H[i] = AwayPi_H[last_AwayTeam_index] + dAwayPi_H[last_AwayTeam_index]
            HomePi_A[i] = AwayPi_A[last_AwayTeam_index] + dAwayPi_A[last_AwayTeam_index]
            HomePi[i] = (HomePi_H[i] + HomePi_A[i])/2             
        else:
            # Both 0, therefore initialize Pi Rating
            HomePi_H[i] = 0.0
            HomePi_A[i] = 0.0
            HomePi[i] = (HomePi_H[i] + HomePi_A[i])/2            
            
        # Find last Pi rating of AwayTeam
        try:
            last_HomeTeam_index = np.max(np.where(HomeTeam[(np.where(~np.isnan(HomePi)))] == AwayTeam[i]))
        except:
            last_HomeTeam_index = 0
        
        try:
            last_AwayTeam_index = np.max(np.where(AwayTeam[(np.where(~np.isnan(AwayPi)))] == AwayTeam[i]))
        except:
            last_AwayTeam_index = 0
        
        if last_HomeTeam_index > last_AwayTeam_index:
            AwayPi_H[i] = HomePi_H[last_HomeTeam_index] + dHomePi_H[last_HomeTeam_index]
            AwayPi_A[i] = HomePi_A[last_HomeTeam_index] + dHomePi_A[last_HomeTeam_index]
            AwayPi[i] = (AwayPi_H[i] + AwayPi_A[i])/2        
        elif last_AwayTeam_index > last_HomeTeam_index:
            AwayPi_H[i] = AwayPi_H[last_AwayTeam_index] + dAwayPi_H[last_AwayTeam_index]
            AwayPi_A[i] = AwayPi_A[last_AwayTeam_index] + dAwayPi_A[last_AwayTeam_index]
            AwayPi[i] = (AwayPi_H[i] + AwayPi_A[i])/2           
        else:
            # Both 0, therefore initialize Pi Rating
            AwayPi_H[i] = 0.0
            AwayPi_A[i] = 0.0
            AwayPi[i] = (AwayPi_H[i] + AwayPi_A[i])/2
    
        ########################################################################
        ########################################################################
        # Calculate dHomePi_H, dHomePi_A, dAwayPi_H, dAwayPi_A
        ########################################################################
        GD[i] = FTHG[i] - FTAG[i]
        if HomePi_H[i] > 0:
            expected_gd_h = 10**(abs(HomePi_H[i])/c) - 1
        else:
            expected_gd_h = -(10**(abs(HomePi_H[i])/c) - 1)
        
        if AwayPi_A[i] > 0:
            expected_gd_a = 10**(abs(AwayPi_A[i])/c) - 1
        else:
            expected_gd_a = -(10**(abs(AwayPi_A[i])/c) - 1)
            
        GDe[i] = expected_gd_h - expected_gd_a
        e  = abs(GD[i] - GDe[i])
        if GDe[i] < GD[i]:
            dHomePi_H[i] = c*math.log10(1 + e)*l
            dAwayPi_A[i] = -c*math.log10(1 + e)*l
        else:
            dHomePi_H[i] = -c*math.log10(1 + e)*l
            dAwayPi_A[i] = c*math.log10(1 + e)*l
            
        dHomePi_A[i] = dHomePi_H[i]*g
        dAwayPi_H[i] = dAwayPi_A[i]*g
        
        dHomePi[i] = (dHomePi_H[i] + dHomePi_A[i])/2
        dAwayPi[i] = (dAwayPi_H[i] + dAwayPi_A[i])/2
        
        Pi_delta[i] = HomePi_H[i] - AwayPi_A[i]
        ########################################################################
        # Calculate Win/Tie/Loss Expectancy
        # Depending on pi_probability_distribution
        
        if not use_pi_probability_distribution:
            # First calculate Expected Goals of HomeTeam and AwayTeam
            # Goal Difference is normally distributed with a Standard Deviation of 1.75
            # See: https://www.pinnaclesports.com/en/betting-articles/betting-strategy/how-to-use-standard-deviation-for-handicap-betting
            
            Pi_HomeWin[i] = 0
            Pi_AwayWin[i] = 0
            Pi_Tie[i] = 0
            for gd in range(-10,11):   
                if gd > 0:
                    Pi_HomeWin[i] += scipy.stats.distributions.norm(GDe[i],sd_gd).pdf(gd)
                elif gd == 0:
                    Pi_Tie[i] += scipy.stats.distributions.norm(GDe[i],sd_gd).pdf(gd)
                else:
                    Pi_AwayWin[i] += scipy.stats.distributions.norm(GDe[i],sd_gd).pdf(gd)
            
            # Make sure probabilities sum up to 1 (otherwise problem for montecarlo simulation)
            dummy = np.array([Pi_HomeWin[i],Pi_Tie[i], Pi_AwayWin[i]])
            dummy /= dummy.sum()                    
            Pi_HomeWin[i] = dummy[0]
            Pi_AwayWin[i] = dummy[2]
            Pi_Tie[i] = dummy[1]
        else:
            # pi_probability_distribution is matrix that gives P(W), P(D), P(A)
            # for every Pi_delta
            Pi_HomeWin[i] = float(pi_probability_distribution[(Pi_delta[i] >= pi_probability_distribution.lb) & (Pi_delta[i] < pi_probability_distribution.ub)].Win)
            Pi_Tie[i] = float(pi_probability_distribution[(Pi_delta[i] >= pi_probability_distribution.lb) & (Pi_delta[i] < pi_probability_distribution.ub)].Tie)
            Pi_AwayWin[i] = float(pi_probability_distribution[(Pi_delta[i] >= pi_probability_distribution.lb) & (Pi_delta[i] < pi_probability_distribution.ub)].Loss)
        ########################################################################
        # Timing
        stop = time.time()
        
        if i == 0:
            print("Expected Time to Generate Pi Rating for " + str(len(games)) + " Games: " + str(round((len(games) - i) * (stop-start))) + " s")
            
            
    # Add everything to games pandas
    games.loc[:,'GD'] = pd.Series(GD, index=games.index)
    games.loc[:,'GDe'] = pd.Series(GDe, index=games.index)
    games.loc[:,'HomePi'] = pd.Series(HomePi, index=games.index)
    games.loc[:,'HomePi_H'] = pd.Series(HomePi_H, index=games.index)
    games.loc[:,'HomePi_A'] = pd.Series(HomePi_A, index=games.index)
    games.loc[:,'AwayPi'] = pd.Series(AwayPi, index=games.index)
    games.loc[:,'AwayPi_H'] = pd.Series(AwayPi_H, index=games.index)
    games.loc[:,'AwayPi_A'] = pd.Series(AwayPi_A, index=games.index)
    games.loc[:,'dHomePi'] = pd.Series(dHomePi, index=games.index)
    games.loc[:,'dHomePi_H'] = pd.Series(dHomePi_H, index=games.index)
    games.loc[:,'dHomePi_A'] = pd.Series(dHomePi_A, index=games.index)
    games.loc[:,'dAwayPi'] = pd.Series(dAwayPi, index=games.index)
    games.loc[:,'dAwayPi_H'] = pd.Series(dAwayPi_H, index=games.index)
    games.loc[:,'dAwayPi_A'] = pd.Series(dAwayPi_A, index=games.index)
    games.loc[:,'Pi_HomeWin'] = pd.Series(Pi_HomeWin, index=games.index)
    games.loc[:,'Pi_AwayWin'] = pd.Series(Pi_AwayWin, index=games.index)
    games.loc[:,'Pi_Tie'] = pd.Series(Pi_Tie, index=games.index)    
    games.loc[:,'Pi_delta'] = pd.Series(Pi_delta, index=games.index)  
    
    # Add Pi Prediction Error e = abs(GD - GDe)
    e = abs(games.FTHG - games.FTAG - games.GDe)
    games.loc[:,'Pi_e'] = pd.Series(e, index=games.index)  
    
    return games

# Train gamma and lambda parameter of Pi Rating System based on historic Betting Performance
def get_pi_learning_rates(games,country,years_to_develop_ratings,rule="Goal Difference"):
    from app_betting.profit import profit
    from app_betting.rating_algorithms import pi
    
    import os
    import numpy as np
    import pandas as pd
    import pickle
    
    # Possible g and l values
    g = np.arange(0.05,1.05,0.05)
    l = np.arange(0.005,0.105,0.005)
    
    # for every l and g combo
    total_iterations = len(l)*len(g)
    iteration = 0
    
    # Only games of country
    games = games[games.Competition == country].reset_index(drop=True).sort_values("Date")
    
    # Remove Seasons where Pi Ratings are initialized
    seasons = sorted(list(set(games.Season)))[years_to_develop_ratings:]
    
    output = dict()
    output["l"] = []
    output["g"] = []
    output[rule] = []
    for l_i in l:
        for g_i in g:
            iteration += 1
            output["l"].append(l_i)
            output["g"].append(g_i)
            
            print("Iteration " + str(iteration) + "/" + str(total_iterations) + " || " + str("Lambda: ") + str(l_i) + " & Gamma: " + str(g_i))
            
            # Calculate Pi Ratings
            games_ij = pi(games,l_i,g_i)

            # Remove Seasons where Pi Ratings are initialized
            games_ij = games_ij[games_ij.Season.isin(seasons)]    
            
            if rule == "Profit":
                # Based on most profitable l,g
                # Calculate profitability
                games_ij = profit(games_ij,"Pi",0)
                
                # Select l,g combo with highest profitability
                output[rule].append(games_ij["Pi_profit"].sum())
            
            elif rule == "Goal Difference":
                # Based on lowest average e² = (GDe-GD)²
                output[rule].append((games_ij.Pi_e.dropna()**2).sum()/len(games_ij.Pi_e.dropna()))

    output = pd.DataFrame(output)
    
    # Get best l,g
    if rule == 'Profit': # HIGHEST is the best
        l_output = output.sort_values(rule,ascending = False).iloc[0].l
        g_output = output.sort_values(rule,ascending = False).iloc[0].g
    elif rule == "Goal Difference": # LOWEST is the best
        l_output = output.sort_values(rule,ascending = True).iloc[0].l
        g_output = output.sort_values(rule,ascending = True).iloc[0].g
    
    # Save
    
    if os.path.isfile("app_betting/result/pi_learning_rates.p"):
        pi_learning_rates = pickle.load(open("app_betting/result/pi_learning_rates.p","rb"))
        if rule in pi_learning_rates[country].keys():
            pi_learning_rates[country][rule]["l"] = l_output
            pi_learning_rates[country][rule]["g"] = g_output
            pi_learning_rates[country][rule]["all_data"] = output
        else:
            pi_learning_rates[country][rule] = dict()
            pi_learning_rates[country][rule]["l"] = l_output
            pi_learning_rates[country][rule]["g"] = g_output  
            pi_learning_rates[country][rule]["all_data"] = output
    else:
        pi_learning_rates = dict()
        pi_learning_rates[country] = dict()
        pi_learning_rates[country][rule] = dict()
        pi_learning_rates[country][rule]["l"] = l_output
        pi_learning_rates[country][rule]["g"] = g_output
        pi_learning_rates[country][rule]["all_data"] = output
    
    pickle.dump(pi_learning_rates, open("app_betting/result/pi_learning_rates.p","wb"))
    
    return pi_learning_rates
    
# To get P(W), P(T), P(A) based on large set of historic games
# Given a deltaPi value, what are the win, draw, loss probabilities?

def get_pi_probability_distribution(games,years_to_develop_ratings):
    import numpy as np
    import pandas as pd
    import pickle
    
    # Remove Seasons where Pi Ratings are initialized
    seasons = sorted(list(set(games.Season)))[years_to_develop_ratings:]
    games_training = games[games.Season.isin(seasons)]
    
    # Bin size
    min_bin = games_training.Pi_delta.min()-1
    max_bin = games_training.Pi_delta.max()+1
    
    bins = np.arange(-1.1,1.6,0.1)
    bins = np.append(min_bin,bins)
    bins = np.append(bins,max_bin)
    
    # Calculate histogram
    hist, bins = np.histogram(games_training.Pi_delta.dropna(),bins=bins)
    
    output = dict()
    output["lb"] = []
    output["ub"] = []
    output["Win"] = []
    output["Tie"] = []
    output["Loss"] = []
    for i in range(len(bins)-1):
        # Select only games in bin edges
        output["lb"].append(bins[i])
        output["ub"].append(bins[i+1])
        games_training_i = games_training[(games_training.Pi_delta >= bins[i]) & (games_training.Pi_delta < bins[i+1])]
        
        wins = 0
        losses = 0
        ties = 0
        
        for game_i in range(len(games_training_i)):
            if games_training_i.iloc[game_i].GD > 0 :
                wins += 1
            elif games_training_i.iloc[game_i].GD == 0:
                ties += 1
            else:
                losses += 1
        
        # Calculate Percentages
        output["Win"].append(wins/hist[i])
        output["Tie"].append(ties/hist[i])
        output["Loss"].append(losses/hist[i])
    
    output = pd.DataFrame(output)   
    
    # Save to file
    pickle.dump(output, open("app_betting/result/pi_probability_distribution.p","wb"))
    
    return output