# The Profit Algorithm Adds profit/loss data for every game
# For the specified algorithm (All/Pi/Elo)

def profit(games, algorithm = "all", discrepancy_cutoff = 0, bet_choice = ""):
    import pandas as pd
    import numpy as np
    import time
    from app_betting.convert_odds import probability_to_decimal
    
    games = games.reset_index(drop=True)
    
    # For every game for which there is Pi/Elo/Line data
    bet = 1 # EURO

    # Numpify data necessary for calculation from games pandas
    number_of_games = len(games)
    FTHG = games.FTHG.values
    FTAG = games.FTAG.values
    HomeWinLine = games.HomeWinLine.values
    AwayWinLine = games.AwayWinLine.values
    TieLine = games.TieLine.values
    if algorithm == "All":
        Elo_HomeWin = games.Elo_HomeWin.values
        Elo_AwayWin = games.Elo_AwayWin.values
        Elo_Tie = games.Elo_Tie.values
        Pi_HomeWin = games.Pi_HomeWin.values
        Pi_AwayWin = games.Pi_AwayWin.values
        Pi_Tie = games.Pi_Tie.values
    elif algorithm == "Pi" or algorithm == "Pi_delta":
        Pi_HomeWin = games.Pi_HomeWin.values
        Pi_AwayWin = games.Pi_AwayWin.values
        Pi_Tie = games.Pi_Tie.values
    elif algorithm == "Elo":
        Elo_HomeWin = games.Elo_HomeWin.values
        Elo_AwayWin = games.Elo_AwayWin.values
        Elo_Tie = games.Elo_Tie.values
        
    # Output
    if algorithm == "All":
        Pi_profit = np.empty(number_of_games) * np.nan
        Pi_stake = np.empty(number_of_games) * np.nan
        Elo_profit  = np.empty(number_of_games) * np.nan
        Elo_stake = np.empty(number_of_games) * np.nan
    elif algorithm == "Pi" or algorithm == "Pi_delta":
        Pi_profit = np.empty(number_of_games) * np.nan
        Pi_stake = np.empty(number_of_games) * np.nan
    elif algorithm == "Elo":
        Elo_profit = np.empty(number_of_games) * np.nan
        Elo_stake = np.empty(number_of_games) * np.nan
    
    bet_placed = number_of_games*[None]
    # Timing parameters
    interval = 10*round(number_of_games/100)
    
    for i in range(number_of_games):
        # Timing
        start = time.time()
        
        # Index
        if FTHG[i] > FTAG[i]:
            game_result = "1"
        elif FTHG[i] == FTAG[i]:
            game_result = "X"
        else:
            game_result = "2"
        
        
        # Check if there is a Line
        if np.isnan(HomeWinLine[i]) or np.isnan(AwayWinLine[i]) or np.isnan(TieLine[i]):
            continue
        
        # Bet if Line > discrepancy_cutoff*Predicted Line
        if algorithm == "All" or algorithm == "Pi":
            # Pi
            bets = []
            if HomeWinLine[i] > probability_to_decimal(Pi_HomeWin[i]+ discrepancy_cutoff):
                bets.append([HomeWinLine[i],HomeWinLine[i]-probability_to_decimal(Pi_HomeWin[i]),"1"])
            if AwayWinLine[i] > probability_to_decimal(Pi_AwayWin[i] + discrepancy_cutoff):
                bets.append([AwayWinLine[i],AwayWinLine[i]-probability_to_decimal(Pi_AwayWin[i]),"2"])
            if TieLine[i] > probability_to_decimal(Pi_Tie[i]+ discrepancy_cutoff):
                bets.append([TieLine[i],TieLine[i]-probability_to_decimal(Pi_Tie[i]),"X"])
            
            # Find most profitable bet
            if bets != []:
                bets_sorted = sorted(bets, key=lambda x: x[1])
                bet_placed[i] = bets_sorted[0][2]
                # If bet correct:
                if bets_sorted[0][2] == game_result:
                    Pi_profit[i] = bet*(bets_sorted[0][0]-1)
                else:
                    Pi_profit[i] = -bet
                
                Pi_stake[i] = bet

        if algorithm == "Pi_delta":
            # Pi
            bets = []
            if bet_choice == "HomeWin":
                bets.append([HomeWinLine[i],HomeWinLine[i]-probability_to_decimal(Pi_HomeWin[i]),"1"])
            if bet_choice == "AwayWin":
                bets.append([AwayWinLine[i],AwayWinLine[i]-probability_to_decimal(Pi_AwayWin[i]),"2"])
            if bet_choice == "Draw":
                bets.append([TieLine[i],TieLine[i]-probability_to_decimal(Pi_Tie[i]),"X"])
            
            # Find most profitable bet
            if bets != []:
                bets_sorted = sorted(bets, key=lambda x: x[1])
                bet_placed[i] = bets_sorted[0][2]
                # If bet correct:
                if bets_sorted[0][2] == game_result:
                    Pi_profit[i] = bet*(bets_sorted[0][0]-1)
                else:
                    Pi_profit[i] = -bet
                
                Pi_stake[i] = bet
                
        # Elo
        if algorithm == "All" or algorithm == "Elo":
            bets = []
            if HomeWinLine[i] > discrepancy_cutoff*probability_to_decimal(Elo_HomeWin[i]):
                bets.append([HomeWinLine[i],HomeWinLine[i]/probability_to_decimal(Elo_HomeWin[i]),"1"])
            if AwayWinLine[i] > discrepancy_cutoff*probability_to_decimal(Elo_AwayWin[i]):
                bets.append([AwayWinLine[i],AwayWinLine[i]/probability_to_decimal(Elo_AwayWin[i]),"2"])
            if TieLine[i] > discrepancy_cutoff*probability_to_decimal(Elo_Tie[i]):
                bets.append([TieLine[i],TieLine[i]/probability_to_decimal(Elo_Tie[i]),"X"])
            
            # Find most profitable bet
            if bets != []:
                bets_sorted = sorted(bets, key=lambda x: x[1])
                bet_placed[i] = bets_sorted[0][2]
                
                # If bet correct:
                if bets_sorted[0][2] == game_result:
                    Elo_profit[i] = bet*(bets_sorted[0][0]-1)
                # If bet not correct
                else:
                    Elo_profit[i] = -bet
                    
                Elo_stake[i] = bet
                
        # Timing (No timing because really fast)
        # stop = time.time()
        # if (i%interval == 0) or (i == (len(games) - 1)):
        #     print("Game " + str(i) + "/" + str(len(games)) + " || RT: " + str(round((len(games) - i) * (stop-start))) + " seconds")    
    
    # Add to games pandas
    games.loc[:,'bet_placed'] = pd.Series(bet_placed, index=games.index)
    if algorithm == "All":
        games.loc[:,'Pi_profit'] = pd.Series(Pi_profit, index=games.index)
        games.loc[:,'Pi_stake'] = pd.Series(Pi_stake, index=games.index)
        games.loc[:,'Elo_profit'] = pd.Series(Elo_profit, index=games.index)
        games.loc[:,'Elo_stake'] = pd.Series(Elo_stake, index=games.index)
    elif algorithm == "Pi" or algorithm == "Pi_delta":
        games.loc[:,'Pi_profit'] = pd.Series(Pi_profit, index=games.index)
        games.loc[:,'Pi_stake'] = pd.Series(Pi_stake, index=games.index)
    elif algorithm == "Elo":
        games.loc[:,'Elo_profit'] = pd.Series(Elo_profit, index=games.index)
        games.loc[:,'Elo_stake'] = pd.Series(Elo_stake, index=games.index)
        
    return games