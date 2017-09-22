# Montecarlo Analysis based on Pi Rating Algorithm

########################################################################################################################
########################################################################################################################

def montecarlo(games_country,country_data,l,g,simulations,hot = True):
    import numpy as np
    import pandas as pd
    import pickle
    import time
    import math
    import pickle
    import scipy.stats # For Poisson Distribution, numpy doesn't have it
    from app_voetbalpi.eu_domestic_leagues.functions.game_to_team import make_standing, rank
    
    # Sort games from earliest to most recent
    games_country = games_country.sort("Date")
    games_country = games_country.reset_index(drop=True)
    
    Season = games_country.Season.values
    seasons = sorted(list(set(Season)))
    
    games_country = games_country[(games_country.Season == seasons[-1]) | (games_country.Season == seasons[-2])]
    
    # Numpify data necessary for calculation from games pandas
    number_of_games = len(games_country)
    teams = sorted(list(set(games_country[games_country.Season == "2015-16"].HomeTeam)))
    number_of_teams = len(teams)
    
    HomeTeam = games_country.HomeTeam.values
    AwayTeam = games_country.AwayTeam.values
    Competition = games_country.Competition.values
    
    league_ranking_distribution = dict()
    for team in teams:
        league_ranking_distribution[team] = np.zeros(number_of_teams)
    
    # Games played/Not Yet Played
    games_played =  len(games_country.FTHG.dropna())
    games_not_played = number_of_games - games_played
    
    # Parameters of Pi Rating System
    c = 3
    sd_gd = 1.75
    
    # Parameters of poisson goal distribution
    poisson_lambda_home = 1.91
    poisson_lambda_away = 1.16
    gd_poisson = poisson_lambda_home - poisson_lambda_away
    
    FTHG_simulation = pickle.load(open("app_voetbalpi/eu_domestic_leagues/data/input/FTHG_simulation.p","rb"))
    FTAG_simulation = pickle.load(open("app_voetbalpi/eu_domestic_leagues/data/input/FTAG_simulation.p","rb"))
    
    GDe_interval = 0.01
    GDe_i = np.arange(-10,10,GDe_interval)
    
    # Timing parameters
    interval = 10*round(number_of_games/50)
    
    for simulation in range(simulations):
        sim_start = time.time()
        games_country_sim = games_country.copy(deep=True)

        FTHG = games_country_sim.FTHG.values
        FTAG = games_country_sim.FTAG.values
        Date = games_country_sim.Date.values
        GD = games_country_sim.GD.values
        GDe = games_country_sim.GDe.values
        HomePi = games_country_sim.HomePi.values
        HomePi_H = games_country_sim.HomePi_H.values
        HomePi_A = games_country_sim.HomePi_A.values
        AwayPi = games_country_sim.AwayPi.values
        AwayPi_H = games_country_sim.AwayPi_H.values
        AwayPi_A = games_country_sim.AwayPi_A.values
        dHomePi = games_country_sim.dHomePi.values
        dHomePi_H = games_country_sim.dHomePi_H.values
        dHomePi_A = games_country_sim.dHomePi_A.values
        dAwayPi = games_country_sim.dAwayPi.values
        dAwayPi_H = games_country_sim.dAwayPi_H.values
        dAwayPi_A = games_country_sim.dAwayPi_A.values
        Pi_HomeWin =games_country_sim.Pi_HomeWin.values
        Pi_AwayWin = games_country_sim.Pi_AwayWin.values
        Pi_Tie = games_country_sim.Pi_Tie.values
        Pi_delta = games_country_sim.Pi_delta.values 
        
        s = time.time()
        for i in range(games_played,number_of_games):    
            # Find last Pi rating of HomeTeam
            found = False
            for j in reversed(range(0,i)):
                if HomeTeam[j] == HomeTeam[i]:
                    last_HomeTeam_index = j
                    found = True
                    break
            if not found:
                last_HomeTeam_index = 0
    
            found = False
            for j in reversed(range(0,i)):
                if AwayTeam[j] == HomeTeam[i]:
                    last_AwayTeam_index = j
                    found = True
                    break
            if not found:
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
            found = False
            for j in reversed(range(0,i)):
                if HomeTeam[j] == AwayTeam[i]:
                    last_HomeTeam_index = j
                    found = True
                    break
            if not found:
                last_HomeTeam_index = 0
    
            found = False
            for j in reversed(range(0,i)):
                if AwayTeam[j] == AwayTeam[i]:
                    last_AwayTeam_index = j
                    found = True
                    break
            if not found:
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
            
            Pi_delta[i] = HomePi_H[i] - AwayPi_A[i]
            
            # Calculate EXPECTED Goal Difference
            if HomePi_H[i] > 0:
                expected_gd_h = 10**(abs(HomePi_H[i])/c) - 1
            else:
                expected_gd_h = -(10**(abs(HomePi_H[i])/c) - 1)
            
            if AwayPi_A[i] > 0:
                expected_gd_a = 10**(abs(AwayPi_A[i])/c) - 1
            else:
                expected_gd_a = -(10**(abs(AwayPi_A[i])/c) - 1)
    
            GDe[i] = expected_gd_h - expected_gd_a
    
            
            GDe_index = np.searchsorted(GDe_i,GDe[i])
            
            FTHG[i] = FTHG_simulation[GDe_index,simulation]
            FTAG[i] = FTAG_simulation[GDe_index,simulation]
            GD[i] = FTHG[i] - FTAG[i]
    
            # Recalculate Pi Rating
            if hot:
                # Calculate 
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
            else:
                dHomePi_H[i] = 0
                dHomePi_A[i] = 0
                dAwayPi_H[i] = 0
                dAwayPi_A[i] = 0
                dHomePi[i] = 0
                dAwayPi[i] = 0
    
        step1 = make_standing(games_country_sim[games_country_sim.Season == seasons[-1]])
        standing_country_sim = rank(step1, country_data)
        
        # League Ranking Distribution
        standing_country_sim = standing_country_sim.to_dict(orient="list")
        for t in range(len(standing_country_sim["Team"])):
            ranking = standing_country_sim["R"][t]-1
            league_ranking_distribution[standing_country_sim["Team"][t]][ranking] += 1/simulations
 
        sim_stop = time.time()
        if simulation%interval == 0:
            print(str(simulation) + "/" + str(simulations) + " simulations finished")
            print('Estimated Time Left: ' +  str(round((simulations-simulation)*(sim_stop - sim_start),0)) +  ' seconds')
    
    # league_ranking_distribution = pd.DataFrame(league_ranking_distribution)

    return league_ranking_distribution