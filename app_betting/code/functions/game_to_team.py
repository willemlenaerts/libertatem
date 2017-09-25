# Input: games pandas
# Output: standing pandas
def make_standing(games):
    import numpy as np
    import pandas as pd
    
    seasons = sorted(list(set(games["Season"])))
    
    # Output is standing pandas
    standing = dict()
    standing["Team"] = []
    standing["Season"] = []
    standing["Competition"] = []
    standing["W"] = []
    standing["L"] = []
    standing["T"] = []
    standing["GP"] = []
    standing["GF"] = []
    standing["GA"] = []
    standing["GD"] = []
    standing["R"] = []
    standing["PTS"] = []
    
    for season in seasons:
        # Games in this season
        games_season = games[games.Season == season]
        
        # Teams
        teams = sorted(list(set(games_season["HomeTeam"])))
        number_of_teams = len(teams)
        
        # Add teams to standing
        for team in teams:
            standing["Team"].append(team)
            standing["Season"].append(season)
            standing["Competition"].append(games_season.Competition.iloc[0])
            standing["W"].append(0)
            standing["L"].append(0)
            standing["T"].append(0)
            standing["GP"].append(0)
            standing["GF"].append(0)
            standing["GA"].append(0)
            standing["GD"].append(0)
            standing["R"].append(0)
            standing["PTS"].append(0) 
        
        # Calculate standing
        for i in range(len(games_season)):
            # Check if game already played
            if np.isnan(games_season.iloc[i]["FTHG"]):
                continue
            
            ht_game = games_season.iloc[i]["HomeTeam"]
            at_game = games_season.iloc[i]["AwayTeam"]
            fthg_game = games_season.iloc[i]["FTHG"]
            ftag_game = games_season.iloc[i]["FTAG"]
            for j in range(len(standing["Team"])):
                # HomeTeam
                if standing["Team"][j] == ht_game and standing["Season"][j] == season:
                    # Add GP
                    standing["GP"][j] += 1
                    
                    # Add W-T-L and PTS
                    if fthg_game > ftag_game:
                        standing["W"][j] += 1
                        standing["PTS"][j] += 3
                    elif fthg_game == ftag_game:
                        standing["T"][j] += 1  
                        standing["PTS"][j] += 1
                    else:
                        standing["L"][j] += 1
                        standing["PTS"][j] += 0
                    
                    # Add Goals
                    standing["GF"][j] += fthg_game
                    standing["GA"][j] += ftag_game
                    standing["GD"][j] += fthg_game-ftag_game
                
                # AwayTeam
                if standing["Team"][j] == at_game and standing["Season"][j] == season:
                    # Add GP
                    standing["GP"][j] += 1
                    
                    # Add W-T-L and PTS
                    if ftag_game > fthg_game:
                        standing["W"][j] += 1
                        standing["PTS"][j] += 3
                    elif ftag_game == fthg_game:
                        standing["T"][j] += 1  
                        standing["PTS"][j] += 1
                    else:
                        standing["L"][j] += 1
                        standing["PTS"][j] += 0
                    
                    # Add Goals
                    standing["GF"][j] += ftag_game
                    standing["GA"][j] += fthg_game
                    standing["GD"][j] += ftag_game-fthg_game                        
    # Convert to Pandas
    standing = pd.DataFrame(standing)
    
    return standing

# Rank standing pandas based on ranking rules of country
def rank(standing, country_data):
    import numpy as np
    import pandas as pd
    
    seasons = sorted(list(set(standing["Season"])))
    ranking_rules = country_data["ranking"]
    
    for season in seasons:
        # Rank
        standing_season = standing[standing.Season == season].sort_values(ranking_rules,ascending=[0,0,0])
        
        # Add ranking number (1-number_of_teams)   
        for i in range(len(standing_season)):
            standing.loc[standing_season.index[i],"R"] = i + 1
         
        
    return standing