# Import games
import pickle
import pandas as pd
from app_betting.crossmatch_names import crossmatch_names
from app_betting.get_latest_lines import get_latest_lines
import datetime

games = pickle.load(open("app_betting/result/games.p","rb"))
games_names = sorted(list(set(pd.concat([games.HomeTeam,games.AwayTeam]))))
bet_history = pickle.load(open("app_betting/result/bet_history.p","rb"))

################################################################################
################################################################################
# CHECK OLD BETS
# lines_names = sorted(list(set(pd.concat([bet_history.HomeTeam,bet_history.AwayTeam]))))
# crossmatches = crossmatch_names(games_names,lines_names)

# for i in range(len(bet_history)):
    # Search in games to check if game played already
    # Check Result and calculate Profit


################################################################################
################################################################################
# NEW BETS

# Get Latest Betting Lines
lines = get_latest_lines()
lines = lines[lines.Date > datetime.datetime.now()]
lines_names = sorted(list(set(pd.concat([lines.HomeTeam,lines.AwayTeam]))))

# Crossmatch names games/lines

crossmatches = crossmatch_names(lines_names,games_names)

crossmatches
print("Check Crossmatches, and if necessary adjust in get_latest_lines.py")

bets = dict()
bets["HomeTeam"] = []
bets["HomePi_H"] = []
bets["AwayTeam"] = []
bets["AwayPi_A"] = []
bets["Pi_delta"] = []
bets["Bet"] = []
bets["Line"] = []
bets["Profit"] = []
bets["Result"] = []
bets["Date"] = []

betting_strategies_all = pickle.load(open("app_betting/result/pi_profitable_betting_strategies.p","rb"))
bins = betting_strategies_all[1]
betting_strategies = betting_strategies_all[0]
betting_strategies = betting_strategies[betting_strategies.Profitability > 0].Strategy

for i in range(len(lines)):
    # Add Teams
    bets["HomeTeam"].append(lines.HomeTeam.iloc[i])
    bets["AwayTeam"].append(lines.AwayTeam.iloc[i])
    bets["Date"].append(lines.Date.iloc[i])
    bets["Profit"].append(None)
    bets["Result"].append(None)
    
    # Add Pi ratings
    last_game_HomeTeam = games[((games.HomeTeam == crossmatches[lines.HomeTeam.iloc[i]]) | (games.AwayTeam == crossmatches[lines.HomeTeam.iloc[i]])) & (games.HomePi.notnull())].sort("Date").iloc[-1]
    if last_game_HomeTeam.HomeTeam == crossmatches[lines.HomeTeam.iloc[i]]:
        HomePi_H_new = last_game_HomeTeam.HomePi_H + last_game_HomeTeam.dHomePi_H
    else:
        HomePi_H_new = last_game_HomeTeam.AwayPi_H + last_game_HomeTeam.dAwayPi_H

    last_game_AwayTeam = games[((games.HomeTeam == crossmatches[lines.AwayTeam.iloc[i]]) | (games.AwayTeam == crossmatches[lines.AwayTeam.iloc[i]])) & (games.HomePi.notnull())].sort("Date").iloc[-1]
    if last_game_AwayTeam.HomeTeam == crossmatches[lines.AwayTeam.iloc[i]]:
        AwayPi_A_new = last_game_AwayTeam.HomePi_A + last_game_AwayTeam.dHomePi_A
    else:
        AwayPi_A_new = last_game_AwayTeam.AwayPi_A + last_game_AwayTeam.dAwayPi_A

    # AwayPi_A_new = last_game_HomeTeam.AwayPi_A + last_game_HomeTeam.dAwayPi_A
    
    bets["HomePi_H"].append(HomePi_H_new)
    bets["AwayPi_A"].append(AwayPi_A_new)
    bets["Pi_delta"].append(HomePi_H_new - AwayPi_A_new)
    
    # Check if game is bettable according to Profitable betting strategies
    bet_placed = False
    for betting_strategy in betting_strategies:
        bin_number = int(betting_strategy.split("_")[3])
        lower = bins[bin_number]
        upper = bins[bin_number+1]
        if bets["Pi_delta"][-1] >= lower and bets["Pi_delta"][-1] < upper:
            if betting_strategy.split("_")[4] == "HomeWin":
                bets["Bet"].append("1")
                bets["Line"].append(round(lines.HomeWinLine.iloc[i],2))
                bet_placed = True
            elif betting_strategy.split("_")[4] == "AwayWin":
                bets["Bet"].append("2")
                bets["Line"].append(round(lines.AwayWinLine.iloc[i],2))
                bet_placed = True
            elif betting_strategy.split("_")[4] == "Draw":
                bets["Bet"].append("X")
                bets["Line"].append(round(lines.TieLine.iloc[i],2))
                bet_placed = True
                
        if bet_placed:
            break
        
    if bet_placed == False:
        bets["Bet"].append(None)
        bets["Line"].append(None)
        
bets = pd.DataFrame(bets)
bets = bets[bets.Bet.notnull()].sort("Bet")

# Find NEW bets
for i in range(len(bets)):
    new = True
    for j in range(len(bet_history)):
        if  bets.HomeTeam.iloc[i] == bet_history.HomeTeam.iloc[j] and \
            bets.AwayTeam.iloc[i] == bet_history.AwayTeam.iloc[j] and \
            bets.Date.iloc[i] == bet_history.Date.iloc[j]:
                new = False
                
    if new:
        print("Bet " + bets.Bet.iloc[i] + " on game " + bets.HomeTeam.iloc[i] + " - " + bets.AwayTeam.iloc[i])


# Add bets to bet_history
bet_history = pd.concat([bet_history,bets]).reset_index(drop=True)
bet_history = bet_history.drop_duplicates(subset=["HomeTeam","AwayTeam","Date"]).sort("Date")
pickle.dump(bet_history,open("app_betting/result/bet_history.p","wb"))