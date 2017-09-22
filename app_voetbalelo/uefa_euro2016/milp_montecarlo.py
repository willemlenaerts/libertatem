def milp_montecarlo(data,team_data,groups):
    ##############################################################################
    # Make data all integers and add to 100%
    ##############################################################################
    import pulp
    import numpy as np
    import pandas as pd
    
    model = pulp.LpProblem("JPL Problem", pulp.LpMinimize)
    
    variable_names = []
    variable_names_per_country = []
    countries = list(data.keys())
    lowBound_dict = dict()
    upBound_dict =  dict()
    
    # groups = {"Group E": ["Belgium"]}
    # countries = ["Belgium"]
    
    group_to_ro16 = pd.read_csv("app_voetbalelo/uefa_euro2016/data/group_to_ro16.csv")

    # Voor elk country
    for i in range(len(countries)):
        # Elke mogelijke eindklassering
        variable_names_per_country.append([])
        for j in range(len(data[countries[i]][0])):
            variable_names.append(str(i) + "_" + str(j))
            variable_names_per_country[-1].append(str(i) + "_" + str(j))
            lowBound_dict[str(i) + "_" + str(j)] = float(np.floor(1000*data[countries[i]][0][j]))
            upBound_dict[str(i) + "_" + str(j)] = float(np.ceil(1000*data[countries[i]][0][j]))
            
        # team_data
        for key in team_data[countries[i]].keys():
            variable_names.append(str(i) + "_game_" + key)  
            variable_names_per_country[-1].append(str(i) + "_game_" + key)
            lowBound_dict[str(i) + "_game_" + key] = float(np.floor(1000*team_data[countries[i]][key]))
            upBound_dict[str(i) + "_game_" + key] = float(np.ceil(1000*team_data[countries[i]][key]))
            
    variables = pulp.LpVariable.dict("variable_%s", variable_names, lowBound = 0, upBound = 1000, cat = pulp.LpInteger)
    
    # Ax=B
    # Sum of Group Phase places 1-4 IN group
    # zero = len(data[countries[0]][0])*[0.0]
    # one = 4*[1.0] + (len(data[countries[0]][0])-4)*[0.0]
    length = []
    
    ro16_games = []
    ro8_games = []
    ro4_games = []
    ro2_games = []
    for variable_names_i in range(len(countries)):
        length.append(0)
        ro16_games.append([])
        ro8_games.append([])
        ro4_games.append([])
        ro2_games.append([])
        for key in lowBound_dict.keys():
            if key.split("_")[0] == str(variable_names_i):
                length[-1] += 1
                if ("game" in key) and ("to" not in key):
                    ro16_games[-1].append(key)
    
                elif ("game" in key) and ("to" in key):
                    if key.split("_")[-1] in ["45","46","47","48"]:
                        ro8_games[-1].append(key)
                    if key.split("_")[-1] in ["49","50"]:
                        ro4_games[-1].append(key)
                    if key.split("_")[-1] in ["51"]:
                        ro2_games[-1].append(key)                        
    equality = []                
    for variable_names_i in range(len(countries)):        
        one_i = 4*[1.0] + (length[variable_names_i]-4)*[0.0]
        
        equality_vector_dummy_1 = []
        for j in range(0,variable_names_i):
            equality_vector_dummy_1 += length[j]*[0.0]
    
        equality_vector_dummy_2 = []
        for j in range(variable_names_i + 1,len(countries)):
            equality_vector_dummy_2 += length[j]*[0.0]
            
        equality_vector = equality_vector_dummy_1 + one_i + equality_vector_dummy_2
        equality.append(dict(zip(variable_names,equality_vector)))
        model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 1000.0
    
    # Sum of one place in one group between the 4 teams == 1000
    equality = [] 
    for group in groups.keys():
        for position in range(4):
            pos_array = position*[0.0] + [1.0] +  (3-position)*[0.0]
            equality_vector = []
            for variable_names_i in range(len(countries)):
                if countries[variable_names_i] in groups[group]:
                    equality_vector += pos_array + (length[variable_names_i]-4)*[0.0]
                else:
                    equality_vector += length[variable_names_i]*[0.0]
                    
            equality.append(dict(zip(variable_names,equality_vector)))        
            model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 1000.0
        
    # Constraints sum for every position == 100
    # Win% sums to 100% for all countries
    
    equality = []    
    equality_vector = []
    for variable_names_i in range(len(countries)):        
        equality_vector += 8*[0.0] + [1.0] + (length[variable_names_i]-9)*[0.0]
    
    equality.append(dict(zip(variable_names,equality_vector)))
    model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 1000.0
    
    
    # Extra constraints
    # Round of 16 games sum == Chance of progress group
    equality = []    
    for variable_names_i in range(len(countries)):
        one_i = [0.0,0.0,0.0,0.0,1.0]
        for j in range(5,length[variable_names_i]):
            if variable_names_per_country[variable_names_i][j] in ro16_games[variable_names_i]: # RO16 game
                one_i += [-1]
            else: 
                one_i += [0.0]
        
        equality_vector_dummy_1 = []
        for j in range(0,variable_names_i):
            equality_vector_dummy_1 += length[j]*[0.0]
        
        equality_vector_dummy_2 = []
        for j in range(variable_names_i + 1,len(countries)):
            equality_vector_dummy_2 += length[j]*[0.0]
            
        equality_vector = equality_vector_dummy_1 + one_i + equality_vector_dummy_2
        equality.append(dict(zip(variable_names,equality_vector)))
        model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 0.0        
    
    # Extra constraints
    # Round of 8 games sum == Chance of progress from round of 16
    equality = []    
    for variable_names_i in range(len(countries)):
        one_i = [0.0,0.0,0.0,0.0,0.0,1.0]
        for j in range(6,length[variable_names_i]):
            if variable_names_per_country[variable_names_i][j] in ro8_games[variable_names_i]: # RO16 game
                one_i += [-1]
            else: 
                one_i += [0.0]
        
        equality_vector_dummy_1 = []
        for j in range(0,variable_names_i):
            equality_vector_dummy_1 += length[j]*[0.0]
        
        equality_vector_dummy_2 = []
        for j in range(variable_names_i + 1,len(countries)):
            equality_vector_dummy_2 += length[j]*[0.0]
            
        equality_vector = equality_vector_dummy_1 + one_i + equality_vector_dummy_2
        equality.append(dict(zip(variable_names,equality_vector)))
        model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 0.0
        
     # Extra constraints
    # Round of 4 games sum == Chance of progress from round of 8
    equality = []    
    for variable_names_i in range(len(countries)):
        one_i = [0.0,0.0,0.0,0.0,0.0,0.0,1.0]
        for j in range(7,length[variable_names_i]):
            if variable_names_per_country[variable_names_i][j] in ro4_games[variable_names_i]: # RO16 game
                one_i += [-1]
            else: 
                one_i += [0.0]
        
        equality_vector_dummy_1 = []
        for j in range(0,variable_names_i):
            equality_vector_dummy_1 += length[j]*[0.0]
        
        equality_vector_dummy_2 = []
        for j in range(variable_names_i + 1,len(countries)):
            equality_vector_dummy_2 += length[j]*[0.0]
            
        equality_vector = equality_vector_dummy_1 + one_i + equality_vector_dummy_2
        equality.append(dict(zip(variable_names,equality_vector)))
        model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 0.0   
    
    # RO 16 game with winner of group == winpercentage of group
    equality = []   
    for variable_names_i in range(len(countries)):
        one_i = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0]
        for j in range(8,length[variable_names_i]):
            if variable_names_per_country[variable_names_i][j] in ro2_games[variable_names_i]: # RO16 game
                one_i += [-1]
            else: 
                one_i += [0.0]
        
        equality_vector_dummy_1 = []
        for j in range(0,variable_names_i):
            equality_vector_dummy_1 += length[j]*[0.0]
        
        equality_vector_dummy_2 = []
        for j in range(variable_names_i + 1,len(countries)):
            equality_vector_dummy_2 += length[j]*[0.0]
            
        equality_vector = equality_vector_dummy_1 + one_i + equality_vector_dummy_2
        equality.append(dict(zip(variable_names,equality_vector)))
        model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 0.0       
    
    
     # Extra constraints
    # Round of 4 games sum == Chance of progress from round of 8
    equality = []    
    for variable_names_i in range(len(countries)):
        # Get group of this country
        for group in groups.keys():
            if countries[variable_names_i] in groups[group]:
                group = group.replace("Group ","")
                break
        
        # Now get game where first placed team will get to
        game = group_to_ro16[(group_to_ro16.group == group) & (group_to_ro16.position.astype(int) == 1)].ro16game.iloc[0].astype(int)
        
        one_i = [0.0,0.0,0.0,1.0]
        for j in range(4,length[variable_names_i]):
            if variable_names_per_country[variable_names_i][j] == str(variable_names_i) + "_game_" + str(game): # RO16 game
                one_i += [-1]
            else: 
                one_i += [0.0]
        
        equality_vector_dummy_1 = []
        for j in range(0,variable_names_i):
            equality_vector_dummy_1 += length[j]*[0.0]
        
        equality_vector_dummy_2 = []
        for j in range(variable_names_i + 1,len(countries)):
            equality_vector_dummy_2 += length[j]*[0.0]
            
        equality_vector = equality_vector_dummy_1 + one_i + equality_vector_dummy_2
        equality.append(dict(zip(variable_names,equality_vector)))
        model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 0.0
    
    # Round of 4 games sum == Chance of progress from round of 8
    equality = []    
    for variable_names_i in range(len(countries)):
        # Get group of this country
        for group in groups.keys():
            if countries[variable_names_i] in groups[group]:
                group = group.replace("Group ","")
                break
        
        # Now get game where first placed team will get to
        game = group_to_ro16[(group_to_ro16.group == group) & (group_to_ro16.position.astype(int) == 2)].ro16game.iloc[0].astype(int)
        
        one_i = [0.0,0.0,1.0,0.0]
        for j in range(4,length[variable_names_i]):
            if variable_names_per_country[variable_names_i][j] == str(variable_names_i) + "_game_" + str(game): # RO16 game
                one_i += [-1]
            else: 
                one_i += [0.0]
        
        equality_vector_dummy_1 = []
        for j in range(0,variable_names_i):
            equality_vector_dummy_1 += length[j]*[0.0]
        
        equality_vector_dummy_2 = []
        for j in range(variable_names_i + 1,len(countries)):
            equality_vector_dummy_2 += length[j]*[0.0]
            
        equality_vector = equality_vector_dummy_1 + one_i + equality_vector_dummy_2
        equality.append(dict(zip(variable_names,equality_vector)))
        model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 0.0    
    
    # Round of 4 games sum == Chance of progress from round of 8
    equality = []    
    for variable_names_i in range(len(countries)):
        # Get group of this country
        for group in groups.keys():
            if countries[variable_names_i] in groups[group]:
                group = group.replace("Group ","")
                break
        
        # Now get game where first placed team will get to
        games = group_to_ro16[(group_to_ro16.group == group) & (group_to_ro16.position.astype(int) == 3)].ro16game.astype(int).tolist()
        
        one_i = [0.0,0.0,-1.0,-1.0,1.0]
        
        for j in range(5,length[variable_names_i]):
            if variable_names_per_country[variable_names_i][j] == str(variable_names_i) + "_game_" + str(games[0]): # RO16 game
                one_i += [-1.0]
            elif variable_names_per_country[variable_names_i][j] == str(variable_names_i) + "_game_" + str(games[1]): # RO16 game
                one_i += [-1.0]
            else: 
                one_i += [0.0]
        
        equality_vector_dummy_1 = []
        for j in range(0,variable_names_i):
            equality_vector_dummy_1 += length[j]*[0.0]
        
        equality_vector_dummy_2 = []
        for j in range(variable_names_i + 1,len(countries)):
            equality_vector_dummy_2 += length[j]*[0.0]
            
        equality_vector = equality_vector_dummy_1 + one_i + equality_vector_dummy_2
        equality.append(dict(zip(variable_names,equality_vector)))
        # chance_to_go_through_from_3_place = data[countries[variable_names_i]][0][4] -  data[countries[variable_names_i]][0][3] - data[countries[variable_names_i]][0][2]
        model += sum([equality[-1][i]*variables[i] for i in variable_names]) == 0.0
        
    # Constraints (ub,lb)
    for var in variable_names:
        model+= variables[var] >= lowBound_dict[var]
        model+= variables[var] <= upBound_dict[var]
    # solve and get result[0]
    model.solve()
    if model.solve() == -1:
        print("WARNING: Regular MIP Algorithm did not reach optimal point")
        
    
    data_int = dict()
    team_data_int = dict()
    for i in range(len(countries)):
        data_int[countries[i]] = list()
        team_data_int[countries[i]] = dict()
        # Elke mogelijke eindklassering
        for j in range(len(data[countries[i]][0])):
            data_int[countries[i]].append(variables[str(i) + "_" + str(j)].value()/10)
            
        for key in lowBound_dict.keys():
            if key.split("_")[0] == str(i):
                if "game" in key:
                    if "to" in key:
                        team_data_int[countries[i]][key.split("game")[-1][1:]] = variables[key].value()/10
                    else:
                        team_data_int[countries[i]][key.split("_")[-1]] = variables[key].value()/10

    return [data_int,team_data_int]