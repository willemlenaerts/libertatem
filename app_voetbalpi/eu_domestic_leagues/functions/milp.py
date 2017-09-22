def milp(montecarlo_country,decimals = 1):
    import pulp
    import numpy as np
    # End Ranking Forecast After Regular Season
    model = pulp.LpProblem("", pulp.LpMinimize)
    
    variable_names = []
    lowBound_dict = dict()
    upBound_dict =  dict()
    
    teams = sorted(list(montecarlo_country.keys()))
    positions = list(range(len(montecarlo_country[teams[0]])))
    
    integer_max = 10**(decimals+2)
    # For every team
    for team in teams:
        for position in positions:
            variable_names.append(team + "_" + str(position)) 
    
            lowBound_dict[team + "_" + str(position)] = float(np.floor(integer_max*montecarlo_country[team][position]))
            upBound_dict[team + "_" + str(position)] = float(np.ceil(integer_max*montecarlo_country[team][position]))
    
            if (decimals == 0) and integer_max*montecarlo_country[team][position]<0.5:
                lowBound_dict[team + "_" + str(position)] = float(np.floor(integer_max*montecarlo_country[team][position]))
                upBound_dict[team + "_" + str(position)] = float(np.floor(integer_max*montecarlo_country[team][position]))
    
    variables = pulp.LpVariable.dict("variable_%s", variable_names, lowBound = 0, upBound = integer_max, cat = pulp.LpInteger)
    
    # Ax=B    
    zero = len(montecarlo_country[teams[0]])*[0.0]
    one = len(montecarlo_country[teams[0]])*[1.0]
    equality = []
    for t in range(len(teams)):
        equality_vector = t*zero + one + (len(teams)-t-1)*zero
        equality.append(dict(zip(variable_names,equality_vector)))
    
    for eq in equality:
        model += sum([eq[i]*variables[i] for i in variable_names]) == integer_max
    
    # Constraints sum for every position == integer_max
    equality = []
    for p in range(len(positions)):
        equality_vector = p*[0] + [1] + (len(positions)-p-1)*[0]
        equality_vector = len(teams)*equality_vector
        equality.append(dict(zip(variable_names,equality_vector)))
    
    for eq in equality:
        model += sum([eq[i]*variables[i] for i in variable_names]) == integer_max
        
    # Constraints (ub,lb)
    for var in variable_names:
        model+= variables[var] >= lowBound_dict[var]
        model+= variables[var] <= upBound_dict[var]
    
    # solve and get result[0]
    model.solve()
    if model.solve() == -1:
        print("WARNING: Regular MIP Algorithm did not reach optimal point")
    
    montecarlo_country_output = dict()
    for team in teams:
        montecarlo_country_output[team] = []
        for position in positions:
            montecarlo_country_output[team].append(variables[team + "_" + str(position)].value()/10**decimals)

    return montecarlo_country_output
    
def milp_forecast(games,decimals = 0):
    import pulp
    import numpy as np
    # End Ranking Forecast After Regular Season
    model = pulp.LpProblem("", pulp.LpMinimize)
    
    variables = games["Pi_HomeWin"] + games["Pi_AwayWin"] + games["Pi_Tie"]
    variable_names = []
    lowBound_dict = dict()
    upBound_dict =  dict()
    
    integer_max = 10**(decimals+2)
    # For every team
    for i in range(len(variables)):
        variable_names.append(str(i)) 

        lowBound_dict[str(i)] = float(np.floor(integer_max*float(variables[i])))
        upBound_dict[str(i)] = float(np.ceil(integer_max*float(variables[i])))
    
    variables = pulp.LpVariable.dict("variable_%s", variable_names, lowBound = 0, upBound = integer_max, cat = pulp.LpInteger)
    
    # Ax=B    
    equality = []
    for i in range(len(games["Pi_HomeWin"])):
        equality_vector = 3*(i*[0] + [1] + (len(games["Pi_HomeWin"])-i-1)*[0])
        equality.append(dict(zip(variable_names,equality_vector)))
    
    for eq in equality:
        model += sum([eq[i]*variables[i] for i in variable_names]) == integer_max

    # Constraints (ub,lb)
    for var in variable_names:
        model+= variables[var] >= lowBound_dict[var]
        model+= variables[var] <= upBound_dict[var]
    
    # solve and get result[0]
    model.solve()
    if model.solve() == -1:
        print("WARNING: Regular MIP Algorithm did not reach optimal point")
    
    montecarlo_country_output = dict()
    
    games["Pi_HomeWin"] = []
    games["Pi_AwayWin"] = []
    games["Pi_Tie"] = []
    
    for i in range(len(variables)):
        if i < int(len(variables)/3):
            if decimals == 0:
                games["Pi_HomeWin"].append(str(int(variables[str(i)].value()/10**decimals)))
            else:
                games["Pi_HomeWin"].append(str(variables[str(i)].value()/10**decimals))
        elif i < 2*int(len(variables)/3):
            if decimals == 0:
                games["Pi_AwayWin"].append(str(int(variables[str(i)].value()/10**decimals)))
            else:
                games["Pi_AwayWin"].append(str(variables[str(i)].value()/10**decimals))
        else:
            if decimals == 0:
                games["Pi_Tie"].append(str(int(variables[str(i)].value()/10**decimals)))
            else:
                games["Pi_Tie"].append(str(variables[str(i)].value()/10**decimals))

    return games