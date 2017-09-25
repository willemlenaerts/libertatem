def generate_json(country, result_seasons):
    import json
    import numpy as np
    import pulp
    import os
    
    result = result_seasons[0]
    elo_start_array = result[3]
    
    number_of_teams = len(result[0][0][0])
    
    # Make directory for save
    if not os.path.exists("app_voetbalelo/eu_domestic_leagues/result/" + country + "/"):
        os.makedirs("app_voetbalelo/eu_domestic_leagues/result/" + country + "/")
    
    # Save as result json file
    # Teams
    json.dump(result[1][0],open("app_voetbalelo/eu_domestic_leagues/result/" + country + "/teams.json","w"))
    
    # Games
    games_matrix = np.round(100*result[1][1])/100
    for i in range(len(games_matrix)):
        games_matrix[i,-3:] = 100*games_matrix[i,-3:]
    
    games_matrix = games_matrix.astype(int)
    for i in range(len(games_matrix)):
        max_index = np.argmax(games_matrix[i,-3:])+5
        games_matrix[i,max_index] = games_matrix[i,max_index] - (sum(games_matrix[i,-3:]) - 100) 
            
    json.dump(games_matrix.tolist(),open("app_voetbalelo/eu_domestic_leagues/result/" + country + "/games.json","w"))
    
    # Standing
    json.dump(result[1][2].tolist(),open("app_voetbalelo/eu_domestic_leagues/result/" + country + "/standing.json","w"))
    
    # ELO rating
    games_matrix = result[1][1]
    team_indices = []
    while len(team_indices) != number_of_teams:
        # print(len(team_indices))
        for i in reversed(range(len(games_matrix))):
            # print(i)
            ht_index = int(games_matrix[i,0])
            at_index = int(games_matrix[i,1])
            
            # Game played?
            if games_matrix[i,4] == 1:
                # Both not yet in team_indices
                if (ht_index not in team_indices) and (at_index not in team_indices):
                    team_indices.append(ht_index)
                    team_indices.append(at_index)
                    
                    dElo_ht = result[2][ht_index][-1] - result[2][ht_index][-2] 
                    dElo_at = result[2][at_index][-1] - result[2][at_index][-2] 
                    
                    if abs(dElo_ht) != abs(dElo_at):
                        # Adjust latest HT Elo (aanname)
                        adj = abs(dElo_ht) - abs(dElo_at)
                        if dElo_ht >= 0:
                            result[2][ht_index][-1] -= adj
                        else:
                            result[2][ht_index][-1] += adj
                            
                # Only hometeam not in team_indices
                elif ht_index not in team_indices:
                    team_indices.append(ht_index)
                elif at_index not in team_indices:
                    team_indices.append(at_index)
                    # # team_indices.append(at_index)
                    
                    # dElo_ht = result[2][ht_index][-1] - result[2][ht_index][-2] 
                    # dElo_at = result[2][at_index][-1] - result[2][at_index][-2] 
                    
                    # if abs(dElo_ht) != abs(dElo_at):
                    #     # Adjust latest HT Elo (aanname)
                    #     adj = abs(dElo_ht) - abs(dElo_at)
                    #     if dElo_ht >= 0:
                    #         result[2][ht_index][-1] -= adj
                    #     else:
                    #         result[2][ht_index][-1] += adj                
                
    elo = []
    for i in range(number_of_teams):
        elo.append(result[2][i][-1])
                    
    json.dump(elo,open("app_voetbalelo/eu_domestic_leagues/result/" + country + "/elo.json","w"))
    
    # End Ranking Forecast After Regular Season
    model = pulp.LpProblem("JPL Problem", pulp.LpMinimize)
    
    variable_names = []
    lowBound_dict = dict()
    upBound_dict =  dict()
    # Voor elk team
    for i in range(len(result[1][0])):
        # Elke mogelijke eindklassering
        for j in range(len(result[1][0])):
            variable_names.append(str(i) + "_" + str(j)) 
            # lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(1000*result[0][1][i,j]))
            # upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(1000*result[0][1][i,j]))
            
            if 100*result[0][1][i,j] >= 0.5:
                # 1% Meer of minder mag dan
                lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*result[0][1][i,j]))
                upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(100*result[0][1][i,j]))
            else:
                # 0% fixed
                lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*result[0][1][i,j]))
                upBound_dict[str(i) + "_" + str(j)] = float(np.floor(100*result[0][1][i,j]))  
    
    variables = pulp.LpVariable.dict("variable_%s", variable_names, lowBound = 0, upBound = 100, cat = pulp.LpInteger)
    
    # Ax=B    
    zero = len(result[1][0])*[0.0]
    one = len(result[1][0])*[1.0]
    equality = []
    for variable_names_i in range(len(result[1][0])):
        equality_vector = variable_names_i*zero + one + (len(result[1][0])-variable_names_i-1)*zero
        equality.append(dict(zip(variable_names,equality_vector)))
    
    for eq in equality:
        model += sum([eq[i]*variables[i] for i in variable_names]) == 100.0
    
    # Constraints sum for every position == 100
    equality = []   
    for variable_names_i in range(len(result[1][0])):
        equality_vector = variable_names_i*[0] + [1] + (len(result[1][0])-variable_names_i-1)*[0]
        equality_vector = len(result[1][0])*equality_vector
        equality.append(dict(zip(variable_names,equality_vector)))
    
    for eq in equality:
        model += sum([eq[i]*variables[i] for i in variable_names]) == 100.0
        
    # Constraints (ub,lb)
    for var in variable_names:
        model+= variables[var] >= lowBound_dict[var]
        model+= variables[var] <= upBound_dict[var]
    
    # solve and get result[0]
    model.solve()
    if model.solve() == -1:
        print("WARNING: Regular MIP Algorithm did not reach optimal point")
    forecast_regular_matrix = []
    for i in range(len(result[1][0])):
        forecast_regular_matrix.append([])
        # Elke mogelijke eindklassering
        for j in range(len(result[1][0])):
            forecast_regular_matrix[-1].append(int(variables[str(i) + "_" + str(j)].value()))
            
    json.dump(forecast_regular_matrix,open("app_voetbalelo/eu_domestic_leagues/result/" + country + "/standing_forecast_regular.json","w"))
    
    # ELO evolution
    # Add START OF SEASON
    for i in range(len(result[2])):
        result[2][i].insert(0,elo_start_array[i])
    json.dump(result[2],open("app_voetbalelo/eu_domestic_leagues/result/" + country + "/elo_evolution.json","w"))
    
    # # Hard coded colors
    # colors = {  "AA Gent":  "rgba(0, 71, 156,1)",
    #         "Anderlecht": "rgba(80, 40, 128,1)",
    #         "Charleroi": "rgba(0,0,0,1)",
    #         "Club Brugge": "rgba(0, 116, 189,1)",
    #         "KV Mechelen":  "rgba(224, 30, 35,1)",
    #         "Kortrijk": "rgba(207, 8, 14,1)" ,
    #         "Lokeren":"rgba(0,0,0,1)",
    #         "Moeskroen-Péruwelz": "rgba(229, 20, 42,1)",
    #         "OH Leuven": "rgba(0,0,0,1)",
    #         "Oostende": "rgba(190, 22, 35,1)" ,
    #         "Racing Genk": "rgba(25, 50, 147,1)",
    #         "STVV": "rgba(205, 179, 13,1)" ,
    #         "Standard": "rgba(207, 8, 14,1)"  ,
    #         "Waasland-Beveren":  "rgba(205, 179, 13,1)" ,
    #         "Westerlo": "rgba(205, 179, 13,1)" ,
    #         "Zulte Waregem": "rgba(132, 31, 47,1)"  ,
    # }
    # json.dump(colors,open("app_voetbalelo/eu_domestic_leagues/result/" + country + "/colors.json","w"))

    return  {"teams": result[1][0],"elo_evolution":result[2],"games":games_matrix.tolist(),
            "standing":result[1][2].tolist(),"standing_forecast_regular":forecast_regular_matrix,
            "elo":elo}