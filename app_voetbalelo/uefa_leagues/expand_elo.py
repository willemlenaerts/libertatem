# Expand Games data with Elo and Win percentages
# Returns panda of all games
def expand_elo(games):
    from app_voetbalelo.uefa_leagues.get_elo_data import get_elo_data

    import json
    import pickle
    import numpy as np
    import pandas as pd
    import datetime
    import distance
    import scipy.stats # For Poisson Distribution, numpy doesn't have it
    
    # Expand games with EloHT/EloAT/OddsHomeWinOdd/OddsAwayWin/OddTie
    games["HomeElo"] = len(games["HomeTeam"])*[0]
    games["AwayElo"] = len(games["HomeTeam"])*[0]
    games["ChanceHomeWin"] = len(games["HomeTeam"])*[0]
    games["ChanceAwayWin"] = len(games["HomeTeam"])*[0]
    games["ChanceTie"] = len(games["HomeTeam"])*[0]
    
    # Make pandas from games
    panda = pd.DataFrame(games)
    panda = panda[(~panda.TYPE.str.contains("qualifying")) & (~panda.TYPE.str.contains("Play-offs"))] # Only Group Phase and later
    # panda = panda.set_index("DATE")
    panda = panda.sort_index()
    
    # Get ELO data for every dat in panda
    dates = list(set(panda.DATE))
    for date in dates:
        # Get Elo BEFORE game
        date_elo = date - datetime.timedelta(days=1)
        team_elo_date = get_elo_data(date_elo)
        
        # Match elo data with panda
        for i in range(len(panda)):
            home_team_elo = 0
            away_team_elo = 0
            if panda.DATE.iloc[i] == date:
                # Fixed assign
                team_names_panda_fixed = ["AZ","Astana","Asteras","Rubin","Sion","Celtic","Shakhtar Donetsk","Mönchengladbach","Paris","Krasnodar","Club Brugge","Lokomotiv Moskva","Qarabağ","St-Étienne","Sporting CP","Qäbälä","Plzeň","Liberec","Gent","Athletic"]
                team_names_elo_fixed = ["Alkmaar","FK Astana","Asteras Tripolis","Rubin Kazan","Sion","Celtic","Shakhtar","Gladbach","Paris SG","FC Krasnodar","Brugge","Lok Moskva","Karabakh Agdam","Saint-Etienne","Sporting","Gabala","Viktoria Plzen","Slovan Liberec","Gent","Bilbao"]

                for k in range(len(team_names_panda_fixed)):
                    if panda.HomeTeam.iloc[i] == team_names_panda_fixed[k]:
                        for j in range(len(team_elo_date)):
                            if team_elo_date[j][0] == team_names_elo_fixed[k]:
                                panda.loc[panda.index[i],"HomeElo"] = team_elo_date[j][1]
                                home_team_elo = 1
    
                    if panda.AwayTeam.iloc[i] == team_names_panda_fixed[k]:
                        for j in range(len(team_elo_date)):
                            if team_elo_date[j][0] == team_names_elo_fixed[k]:
                                panda.loc[panda.index[i],"AwayElo"] = team_elo_date[j][1] 
                                away_team_elo = 1
    
             
                # Rest 
                # HomeTeam
                if home_team_elo == 0:
                    for j in range(len(team_elo_date)):
                        if distance.levenshtein(panda.HomeTeam.iloc[i],team_elo_date[j][0]) == 0:
                            panda.loc[panda.index[i],"HomeElo"] = team_elo_date[j][1]
                            break
                        elif distance.levenshtein(panda.HomeTeam.iloc[i],team_elo_date[j][0]) == 1:
                            panda.loc[panda.index[i],"HomeElo"] = team_elo_date[j][1]
                            break
                        elif distance.levenshtein(panda.HomeTeam.iloc[i],team_elo_date[j][0]) == 2:
                            panda.loc[panda.index[i],"HomeElo"] = team_elo_date[j][1]
                            break
                    
                # AwayTeam
                if away_team_elo == 0:
                    for j in range(len(team_elo_date)):     
                        if distance.levenshtein(panda.AwayTeam.iloc[i],team_elo_date[j][0]) == 0:
                            panda.loc[panda.index[i],"AwayElo"] = team_elo_date[j][1]
                            break
                        elif distance.levenshtein(panda.AwayTeam.iloc[i],team_elo_date[j][0]) == 1:
                            panda.loc[panda.index[i],"AwayElo"] = team_elo_date[j][1]   
                            break
                        elif distance.levenshtein(panda.AwayTeam.iloc[i],team_elo_date[j][0]) == 2:
                            panda.loc[panda.index[i],"AwayElo"] = team_elo_date[j][1] 
                            break
            
    # This prints something if no Elo value found for team            
    for i in range(len(panda)):
        if panda.AwayElo.iloc[i] == 0:
            print(panda.AwayTeam.iloc[i])
     
    # Convert Elo columns to float
    panda.HomeElo = panda.HomeElo.astype(float)
    panda.AwayElo = panda.AwayElo.astype(float)
    # Calculate Win/Lose/Tie probabilities for every game
    # Parameters ELO 
    home_field_advantage = 100
    print("Elo Algorithm")
    for i in range(len(panda)):
        if (i == 0):
            print(str(i+1) + '/' + str(len(panda)))
        elif i%10 == 0:
            print(str(i) + '/' + str(len(panda)))
        elif (i == len(panda)-1):
            print(str(i+1) + '/' + str(len(panda)))
        # panda.HomeElo.iloc[i]
        W_home_e = 1/(10**(-(panda.HomeElo.iloc[i]+home_field_advantage-panda.AwayElo.iloc[i])/400)+1)
        
        # First estimate expected goals
        # Goals for Home team
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
        
        # j and k are number of goals
        for j in range(15):
            for k in range(15):
                if j > k:
                    # Home Win
                    panda.loc[panda.index[i],"ChanceHomeWin"] = panda.ChanceHomeWin.iloc[i] + scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
                if j == k:
                    # Tie
                    panda.loc[panda.index[i],"ChanceTie"] = panda.ChanceTie.iloc[i] + scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
                if j < k:
                    # Away Win
                    panda.loc[panda.index[i],"ChanceAwayWin"] =panda.ChanceAwayWin.iloc[i] + scipy.stats.distributions.poisson.pmf(j,home_goals)*scipy.stats.distributions.poisson.pmf(k,away_goals)
    
        # Make sure probabilities sum up to 1 (otherwise problem for montecarlo simulation)
        percentages = np.array([panda.ChanceHomeWin.iloc[i],panda.ChanceTie.iloc[i],panda.ChanceAwayWin.iloc[i]])
        percentages /= percentages.sum()
        
        panda.loc[panda.index[i],"ChanceHomeWin"] = percentages[0]
        panda.loc[panda.index[i],"ChanceTie"] = percentages[1]
        panda.loc[panda.index[i],"ChanceAwayWin"] = percentages[2]
        
    return panda