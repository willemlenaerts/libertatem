# Input: games pandas
# Output: standing pandas
def make_standing(games):
    import numpy as np
    import pandas as pd
    
    # Only Group Phase
    games = games[~games.Group.str.contains("Final")]
    # Output is standing pandas
    standing = dict()
    standing["Country"] = []
    standing["Group"] = []
    standing["W"] = []
    standing["L"] = []
    standing["T"] = []
    standing["GP"] = []
    standing["GF"] = []
    standing["GA"] = []
    standing["GD"] = []
    standing["R"] = []
    standing["PTS"] = []
    
    # Countrys
    countries = list(games.HomeTeam) + list(games.AwayTeam)
    countries = sorted(list(set(countries)))
    number_of_countries = len(countries)
    
    # Add countries to standing
    for country in countries:
        standing["Country"].append(country)
        standing["Group"].append(list(set(games[(games.HomeTeam == country) | (games.AwayTeam == country)].Group))[0])
        standing["W"].append(0)
        standing["L"].append(0)
        standing["T"].append(0)
        standing["GP"].append(0)
        standing["GF"].append(0)
        standing["GA"].append(0)
        standing["GD"].append(0)
        standing["R"].append(0)
        standing["PTS"].append(0) 
    
    # Get Data from games pandas
    HomeTeam = games.HomeTeam.values
    AwayTeam = games.AwayTeam.values
    Group = games.Group.values
    FTHG = games.FTHG.values
    FTAG = games.FTAG.values
    
    # Calculate standing
    for i in range(len(games)):
        # Check if game already played
        if np.isnan(FTHG[i]):
            continue
        
        for j in range(len(standing["Country"])):
            # HomeCountry
            if standing["Country"][j] == HomeTeam[i] and standing["Group"][j] == Group[i]:
                # Add GP
                standing["GP"][j] += 1
                
                # Add W-T-L and PTS
                if FTHG[i] > FTAG[i]:
                    standing["W"][j] += 1
                    standing["PTS"][j] += 3
                elif FTHG[i] == FTAG[i]:
                    standing["T"][j] += 1  
                    standing["PTS"][j] += 1
                else:
                    standing["L"][j] += 1
                    standing["PTS"][j] += 0
                
                # Add Goals
                standing["GF"][j] += FTHG[i]
                standing["GA"][j] += FTAG[i]
                standing["GD"][j] += FTHG[i]-FTAG[i]
            
            # AwayCountry
            if standing["Country"][j] == AwayTeam[i] and standing["Group"][j] == Group[i]:
                # Add GP
                standing["GP"][j] += 1
                
                # Add W-T-L and PTS
                if FTAG[i] > FTHG[i]:
                    standing["W"][j] += 1
                    standing["PTS"][j] += 3
                elif FTAG[i] == FTHG[i]:
                    standing["T"][j] += 1  
                    standing["PTS"][j] += 1
                else:
                    standing["L"][j] += 1
                    standing["PTS"][j] += 0
                
                # Add Goals
                standing["GF"][j] += FTAG[i]
                standing["GA"][j] += FTHG[i]
                standing["GD"][j] += FTAG[i]-FTHG[i]                
                
    # Convert to Pandas
    standing = pd.DataFrame(standing)
    
    return standing

# Rank standing pandas based on ranking rules of country
def rank(standing,games):
    import numpy as np
    import pandas as pd
    from app_voetbalelo.uefa_euro2016.game_to_team import make_standing
    
    # Only Group Phase
    games = games[~games.Group.str.contains("Final")]
    
    # Tiebreakers UEFA Euro 2016 Group Phase
    # 1. PTS
    # 2. GD Between Tied Teams
    # 3. GF Between Tied Teams
    
    groups = sorted(list(set(standing.Group)))
    
    for group in groups:
        # Rank
        standing_group = standing[standing.Group == group].sort(["PTS"],ascending=[0])
                
        # Add ranking number  
        for i in range(len(standing_group)):
            standing_group.loc[standing_group.index[i],"R"] = i + 1    
        
        # Check for ties
        s = np.sort(standing_group.PTS, axis=None)
        points_tied = np.unique(s[s[1:] == s[:-1]])
        
        if len(points_tied) != 0:
            # There are ties
            for point_tied in points_tied:
                # Rankings associated with teams_tied
                ranking_teams_tied = sorted(list(standing_group[standing_group.PTS == point_tied].R))
                
                # Make standing of teams involved
                teams_tied = list(standing_group[standing_group.PTS == point_tied].Country)
                games_teams_tied = games[(games.HomeTeam.isin(teams_tied)) & (games.AwayTeam.isin(teams_tied))]
                
                standing_group_tied = make_standing(games_teams_tied)
                standing_group_tied = standing_group_tied.sort(["PTS","GD","GF"],ascending=[0,0,0])
                
                # Remap to initial standing
                for i in range(len(standing_group_tied)):
                    standing_group.loc[standing_group.Country == standing_group_tied.iloc[i].Country,"R"] = ranking_teams_tied[i]
                
        # Remap standing_group to standing
        for i in range(len(standing_group)):
            standing.loc[standing.Country == standing_group.iloc[i].Country,"R"] = standing_group.iloc[i].R
    
    # Add 4 third place teams that can advance
    standing_3thplaceteams = standing[standing.R == 3].sort(["PTS","GD","GF"],ascending=[0,0,0])
    dummy = list(standing_3thplaceteams.Group)[:4]
    third_place_string = ""
    for d in dummy:
        third_place_string += d.replace("Group ","")
        
    # First add column to standing        
    standing.loc[:,"R3"] = pd.Series(len(standing)*[third_place_string], index=standing.index)

    return standing
    
def round_of_sixteen(standing,games):
    import numpy as np
    import pandas as pd 
    import pickle
    
    number_of_games = len(games)
    HomeTeam = games.HomeTeam.values
    AwayTeam = games.AwayTeam.values
    Group = games.Group.values
    
    groups = sorted(list(set(games.Group)))
    positions = ["1","2"]
    third_place_string = str(standing.R3.iloc[0])
    third_place_rules = pickle.load(open("app_voetbalelo/uefa_euro2016/data/third_place_rules.p","rb"))
    
    for key in third_place_rules.keys():
        if sorted(key) == sorted(third_place_string):
            third_place_string = key
            break
        
    for i in range(number_of_games):
        if Group[i] == "1/8 Final":
            # HomeTeam
            group = HomeTeam[i].split(" ")[1]
            rank = int(HomeTeam[i].split(" ")[2])
            
            HomeTeam[i] = standing[(standing.Group == ("Group " + group)) & (standing.R == rank)].Country.iloc[0]
            
            # AwayTeam
            if group in ["A","B","C","D"] and rank == 1:
                group = third_place_rules[third_place_string][group]
                AwayTeam[i] = standing[(standing.Group == ("Group " + group)) & (standing.R == 3)].Country.iloc[0]
            else:
                group = AwayTeam[i].split(" ")[1]
                rank = int(AwayTeam[i].split(" ")[2])          
                AwayTeam[i] = standing[(standing.Group == ("Group " + group)) & (standing.R == rank)].Country.iloc[0]
                
    return games

def quarterfinals(games):
    import numpy as np
    import pandas as pd 
    import random
    
    number_of_games = len(games)
    HomeTeam = games.HomeTeam.values
    AwayTeam = games.AwayTeam.values
    Group = games.Group.values
        
    for i in range(number_of_games):
        if Group[i] == "Quarter Final":
            # HomeTeam
            game = int(HomeTeam[i])
            fthg_game = int(games[games.Game.astype(int) == game].FTHG.iloc[0])
            ftag_game = int(games[games.Game.astype(int) == game].FTAG.iloc[0])
            if fthg_game > ftag_game:
                HomeTeam[i] = games[games.Game.astype(int) == game].HomeTeam.iloc[0]
            elif ftag_game > fthg_game:
                HomeTeam[i] = games[games.Game.astype(int) == game].AwayTeam.iloc[0]
            else:
                HomeTeam[i] =random.choice([games[games.Game.astype(int) == game].HomeTeam.iloc[0],games[games.Game.astype(int) == game].AwayTeam.iloc[0]])
                
            # AwayTeam
            game = int(AwayTeam[i])
            fthg_game = int(games[games.Game.astype(int) == game].FTHG.iloc[0])
            ftag_game = int(games[games.Game.astype(int) == game].FTAG.iloc[0])
            if fthg_game > ftag_game:
                AwayTeam[i] = games[games.Game.astype(int) == game].HomeTeam.iloc[0]
            elif ftag_game > fthg_game:
                AwayTeam[i] = games[games.Game.astype(int) == game].AwayTeam.iloc[0]    
            else:
                AwayTeam[i] =random.choice([games[games.Game.astype(int) == game].HomeTeam.iloc[0],games[games.Game.astype(int) == game].AwayTeam.iloc[0]])           

    return games    
    
def semifinals(games):
    import numpy as np
    import pandas as pd 
    import random
    
    number_of_games = len(games)
    HomeTeam = games.HomeTeam.values
    AwayTeam = games.AwayTeam.values
    Group = games.Group.values
        
    for i in range(number_of_games):
        if Group[i] == "Semi Final":
            # HomeTeam
            game = int(HomeTeam[i])
            fthg_game = int(games[games.Game.astype(int) == game].FTHG.iloc[0])
            ftag_game = int(games[games.Game.astype(int) == game].FTAG.iloc[0])
            if fthg_game > ftag_game:
                HomeTeam[i] = games[games.Game.astype(int) == game].HomeTeam.iloc[0]
            elif ftag_game > fthg_game:
                HomeTeam[i] = games[games.Game.astype(int) == game].AwayTeam.iloc[0]
            else:
                HomeTeam[i] =random.choice([games[games.Game.astype(int) == game].HomeTeam.iloc[0],games[games.Game.astype(int) == game].AwayTeam.iloc[0]])
                
            # AwayTeam
            game = int(AwayTeam[i])
            fthg_game = int(games[games.Game.astype(int) == game].FTHG.iloc[0])
            ftag_game = int(games[games.Game.astype(int) == game].FTAG.iloc[0])
            if fthg_game > ftag_game:
                AwayTeam[i] = games[games.Game.astype(int) == game].HomeTeam.iloc[0]
            elif ftag_game > fthg_game:
                AwayTeam[i] = games[games.Game.astype(int) == game].AwayTeam.iloc[0]    
            else:
                AwayTeam[i] =random.choice([games[games.Game.astype(int) == game].HomeTeam.iloc[0],games[games.Game.astype(int) == game].AwayTeam.iloc[0]])           

    return games    
    
def final(games):
    import numpy as np
    import pandas as pd 
    import random
    
    number_of_games = len(games)
    HomeTeam = games.HomeTeam.values
    AwayTeam = games.AwayTeam.values
    Group = games.Group.values
        
    for i in range(number_of_games):
        if Group[i] == "Final":
            # HomeTeam
            game = int(HomeTeam[i])
            fthg_game = int(games[games.Game.astype(int) == game].FTHG.iloc[0])
            ftag_game = int(games[games.Game.astype(int) == game].FTAG.iloc[0])
            if fthg_game > ftag_game:
                HomeTeam[i] = games[games.Game.astype(int) == game].HomeTeam.iloc[0]
            elif ftag_game > fthg_game:
                HomeTeam[i] = games[games.Game.astype(int) == game].AwayTeam.iloc[0]
            else:
                HomeTeam[i] =random.choice([games[games.Game.astype(int) == game].HomeTeam.iloc[0],games[games.Game.astype(int) == game].AwayTeam.iloc[0]])
                
            # AwayTeam
            game = int(AwayTeam[i])
            fthg_game = int(games[games.Game.astype(int) == game].FTHG.iloc[0])
            ftag_game = int(games[games.Game.astype(int) == game].FTAG.iloc[0])
            if fthg_game > ftag_game:
                AwayTeam[i] = games[games.Game.astype(int) == game].HomeTeam.iloc[0]
            elif ftag_game > fthg_game:
                AwayTeam[i] = games[games.Game.astype(int) == game].AwayTeam.iloc[0]    
            else:
                AwayTeam[i] =random.choice([games[games.Game.astype(int) == game].HomeTeam.iloc[0],games[games.Game.astype(int) == game].AwayTeam.iloc[0]])           

    return games  