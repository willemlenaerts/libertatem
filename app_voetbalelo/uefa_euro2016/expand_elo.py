def expand_elo(games):
    import numpy as np
    import pandas as pd
    import datetime
    import distance
    from fuzzywuzzy import fuzz
    import scipy.stats # For Poisson Distribution, numpy doesn't have it
    from app_voetbalelo.uefa_euro2016.get_elo_data import get_elo_data
    import pulp
    
    elo = get_elo_data()
    
    # Output elo
    output_elo = dict()
    
    # Crossmatch games and elo country names
    games_names = list(games.HomeTeam) + list(games.AwayTeam)
    games_names = sorted(list(set(games_names)))
    
    elo_names = list(elo.country)
    
    crossmatch_names = dict()
    for game_name in games_names:
        if game_name == "Rep Ireland":
            crossmatch_names[game_name] = "Republic of Ireland"
            continue
        distance_dummy = []
        for elo_name in elo_names:
            if fuzz.ratio(game_name.lower(),elo_name.lower()) == 100:
                distance_dummy = [(100,elo_name)]
                break
            distance_dummy.append((fuzz.partial_ratio(game_name.lower(),elo_name.lower()),elo_name))
        
        # Check highest distance (== closest string match)
        # crossmatch_names.append([games_name,sorted(distance_dummy, reverse=True)[0][1]])
        crossmatch_names[game_name] = sorted(distance_dummy, reverse=True)[0][1]
    
    # Data from games to use in algorithm
    HomeTeam = games.HomeTeam.values
    AwayTeam = games.AwayTeam.values
    
    countries = list(games[~games.Group.str.contains("Final")].HomeTeam) + list(games[~games.Group.str.contains("Final")].AwayTeam)
    countries = list(set(countries))
    
    # Add to games pandas
    number_of_games = len(games)
    HomeElo = np.empty(number_of_games) * np.nan
    AwayElo = np.empty(number_of_games) * np.nan
    HomeWin = np.empty(number_of_games) * np.nan
    AwayWin = np.empty(number_of_games) * np.nan
    Draw = np.empty(number_of_games) * np.nan
    
    for i in range(len(games)):
        if (HomeTeam[i] in countries) and (AwayTeam[i] in countries):
            HomeElo[i] = int(elo[elo.country == crossmatch_names[HomeTeam[i]]].elo)
            AwayElo[i] = int(elo[elo.country == crossmatch_names[AwayTeam[i]]].elo)
            
            if HomeTeam[i] not in output_elo.keys():
                output_elo[HomeTeam[i]] = dict()
                output_elo[HomeTeam[i]]["elo"] = HomeElo[i]
            if AwayTeam[i] not in output_elo.keys():
                output_elo[AwayTeam[i]] = dict()
                output_elo[AwayTeam[i]]["elo"] = AwayElo[i]  
                
            # First estimate expected goals
            # Goals for Home team
            if games.HomeTeam.iloc[i] == "France":
                home_field_advantage = 80
            elif games.AwayTeam.iloc[i] == "France":
                home_field_advantage = -80
            else:
                home_field_advantage = 0
            
            W_home_e = 1/(10**(-(HomeElo[i]+home_field_advantage-AwayElo[i])/400)+1)
            if W_home_e < 0.5:
                home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
            else:
                home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
        
            # Goals for the Away team:
            if W_home_e < 0.8:
                away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
            else:
                away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3
        
            # Now use poisson distribution to determine for each team the chance it scores x goals
            # Combine these for both teams to calculate Win/Loss/Draw expectancy
            
            dummy = np.zeros((1,3))
            for j in range(15):
                for k in range(15):
                    if j > k:
                        # Home Win
                       dummy[0,0] += scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
                    if j == k:
                        # Tie
                       dummy[0,1] += scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
                    if j < k:
                        # Away Win
                       dummy[0,2] += scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
        
            # Make sure probabilities sum up to 1 (otherwise problem for montecarlo simulation)
            dummy[0,0:3] /= dummy[0,0:3].sum()     
            
            # MILP to get integer values that sum to 100 (1)
            model = pulp.LpProblem("Game Odds Problem", pulp.LpMinimize)  
            variable_names = []
            lowBound_dict = dict()
            upBound_dict =  dict()
            
            # Voor elke odd
            for t in range(3):
                variable_names.append(str(t)) 
    
                lowBound_dict[str(t)] = float(np.floor(100*dummy[0,t]))
                upBound_dict[str(t)] = float(np.ceil(100*dummy[0,t]))
            
            variables = pulp.LpVariable.dict("variable_%s", variable_names, lowBound = 0, upBound = 100, cat = pulp.LpInteger)            
            # Ax=B
            # Sum of Group Phase places 1-4 IN group
            equality_vector = 3*[1.0]
            equality = dict(zip(variable_names,equality_vector))
            model += sum([equality[t]*variables[t] for t in variable_names]) == 100.0            
    
            # Constraints (ub,lb)
            for var in variable_names:
                model+= variables[var] >= lowBound_dict[var]
                model+= variables[var] <= upBound_dict[var]
        
            # solve and get result[0]
            model.solve()
            if model.solve() == -1:
                print("WARNING: Regular MIP Algorithm did not reach optimal point")
                
            
            dummy_int = list()
            for t in range(3):
                dummy_int.append(int(variables[str(t)].value()))    
                    
            HomeWin[i] = dummy_int[0]
            AwayWin[i] = dummy_int[2]
            Draw[i] = dummy_int[1]
            
    games.loc[:,'HomeElo'] = pd.Series(HomeElo, index=games.index)
    games.loc[:,'AwayElo'] = pd.Series(AwayElo, index=games.index)
    games.loc[:,'HomeWin'] = pd.Series(HomeWin, index=games.index)
    games.loc[:,'AwayWin'] = pd.Series(AwayWin, index=games.index)
    games.loc[:,'Draw'] = pd.Series(Draw, index=games.index)
    
    
    # Add to output
    for home_country in output_elo.keys():
        for away_country in countries:
            if home_country != away_country:
                ht_elo = output_elo[home_country]["elo"]
                at_elo = output_elo[away_country]["elo"]
    
                # First estimate expected goals
                # Goals for Home team
                if home_country == "France":
                    home_field_advantage = 80
                elif away_country == "France":
                    home_field_advantage = -80
                else:
                    home_field_advantage = 0
                
                W_home_e = 1/(10**(-(ht_elo +home_field_advantage-at_elo)/400)+1)
                if W_home_e < 0.5:
                    home_goals = 0.2 + 1.1*np.sqrt(W_home_e/0.5)
                else:
                    home_goals = 1.69 / (1.12*np.sqrt(2 - W_home_e/0.5)+0.18)
            
                # Goals for the Away team:
                if W_home_e < 0.8:
                    away_goals = -0.96 + 1/(0.1+0.44*np.sqrt((W_home_e+0.1)/0.9))
                else:
                    away_goals = 0.72*np.sqrt((1 - W_home_e)/0.3)+0.3
            
                # Now use poisson distribution to determine for each team the chance it scores x goals
                # Combine these for both teams to calculate Win/Loss/Draw expectancy
                
                dummy = np.zeros((1,3))
                for j in range(15):
                    for k in range(15):
                        if j > k:
                            # Home Win
                           dummy[0,0] += scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
                        if j == k:
                            # Tie
                           dummy[0,1] += scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
                        if j < k:
                            # Away Win
                           dummy[0,2] += scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
            
                # Make sure probabilities sum up to 1 (otherwise problem for montecarlo simulation)
                dummy[0,0:3] /= dummy[0,0:3].sum()     
                
                # MILP to get integer values that sum to 100 (1)
                model = pulp.LpProblem("Game Odds Problem", pulp.LpMinimize)  
                variable_names = []
                lowBound_dict = dict()
                upBound_dict =  dict()
                
                # Voor elke odd
                for t in range(3):
                    variable_names.append(str(t)) 
        
                    lowBound_dict[str(t)] = float(np.floor(100*dummy[0,t]))
                    upBound_dict[str(t)] = float(np.ceil(100*dummy[0,t]))
                
                variables = pulp.LpVariable.dict("variable_%s", variable_names, lowBound = 0, upBound = 100, cat = pulp.LpInteger)            
                # Ax=B
                # Sum of Group Phase places 1-4 IN group
                equality_vector = 3*[1.0]
                equality = dict(zip(variable_names,equality_vector))
                model += sum([equality[t]*variables[t] for t in variable_names]) == 100.0            
    
                # Constraints (ub,lb)
                for var in variable_names:
                    model+= variables[var] >= lowBound_dict[var]
                    model+= variables[var] <= upBound_dict[var]
            
                # solve and get result[0]
                model.solve()
                if model.solve() == -1:
                    print("WARNING: Regular MIP Algorithm did not reach optimal point")
                    
                
                dummy_int = list()
                for t in range(3):
                    dummy_int.append(int(variables[str(t)].value()))    
                        
                output_elo[home_country][away_country] = dummy_int

    return [games,output_elo]