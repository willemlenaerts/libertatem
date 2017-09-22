def get_games_data():
    import numpy as np
    import pandas as pd 
    import datetime
    import pytz
    from pytz import timezone
    
    paris = timezone('Europe/Amsterdam')
    
    output = []
    
    import csv
    with open("app_voetbalelo/uefa_euro2016/data/games.csv", "rt") as f:
        reader = csv.reader(f)
        games_dummy = list(reader)
    
    games = dict()
    for i in range(len(games_dummy)):
        if games_dummy[i] != []:
            for j in range(len(games_dummy[i])):
                if i == 0:
                    games[games_dummy[i][j]] = list()
                else:
                    if games_dummy[0][j] == "Date":
                        # Convert to datetime
                        dt = datetime.datetime.strptime(games_dummy[i][j].lstrip().rstrip(), '%d/%m/%Y %H:%M')
                        dt_dummy = paris.localize(dt) # Make aware
                        games[games_dummy[0][j]].append(dt_dummy)
                    else:
                        games[games_dummy[0][j]].append(games_dummy[i][j].lstrip().rstrip())
    
    
    output = pd.DataFrame(games)
    output = output.set_index("Date")
    output = output.sort()
    
    # Add FTHG/FTAG if not in pandas
    if "FTHG" not in list(output.keys()):
        number_of_games = len(output)
        output.loc[:,'FTHG'] = pd.Series(np.empty(number_of_games) * np.nan, index=output.index)
        output.loc[:,'FTAG'] = pd.Series(np.empty(number_of_games) * np.nan, index=output.index)
        
    return output