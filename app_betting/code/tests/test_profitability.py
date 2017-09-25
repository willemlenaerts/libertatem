import pickle
import pandas as pd
import numpy as np
import time
from app_betting.convert_odds import decimal,probability_to_decimal
from app_betting.profit import profit

# Initialize games
games = pickle.load(open("app_betting/result/games.p","rb"))
training_seasons = 5
seasons = sorted(list(set(games.Season)))[training_seasons:]
games = games[games.Season.isin(seasons)]
games = games[pd.notnull(games.FTHG)]

seasons = sorted(list(set(games.Season)))
competitions = sorted(list(set(games.Competition)))

# Where Pi Prob > Bookie Prob, bet
profit_win = sum(games[(games.Date.dt.month <= 6) & (decimal(games.HomeWinLine) < games.Pi_HomeWin) & (games.FTHG > games.FTAG)].HomeWinLine-1) - games[(games.Date.dt.month <= 6) & (decimal(games.HomeWinLine) < games.Pi_HomeWin) & (games.FTHG <= games.FTAG)].shape[0]
profit_tie = sum(games[(games.Date.dt.month <= 6) & (decimal(games.TieLine) < games.Pi_Tie) & (games.FTHG == games.FTAG)].TieLine-1) - games[(games.Date.dt.month <= 6) & (decimal(games.TieLine) < games.Pi_Tie) & (games.FTHG != games.FTAG)].shape[0]
profit_loss = sum(games[(games.Date.dt.month <= 6) & (decimal(games.AwayWinLine) < games.Pi_AwayWin) & (games.FTHG < games.FTAG)].AwayWinLine-1) - games[(games.Date.dt.month <= 6) & (decimal(games.AwayWinLine) < games.Pi_AwayWin) & (games.FTHG >= games.FTAG)].shape[0]


# Bin size
min_bin = games.Pi_delta.min()-1
max_bin = games.Pi_delta.max()+1

bins = np.arange(-1.1,1.6,0.1)
bins = np.append(min_bin,bins)
bins = np.append(bins,max_bin)

# Calculate histogram
hist, bins = np.histogram(games.Pi_delta.dropna(),bins=bins)
bet_choice = ["HomeWin","AwayWin","Draw"]

# Add following to games
# Generate Output
output = dict()
output["Algorithm"] = []
output["Season"] = []
output["Competition"] = []
output["Pi_bets"] = []
output["Pi_stake"] = []
output["Pi_profit"] = []

for i in range(len(bins)-1):
    games_i = games[(games.Pi_delta >= bins[i]) & (games.Pi_delta < bins[i+1])]
    for j in range(len(bet_choice)):
        games_i_j = profit(games_i, algorithm = "Pi_delta", discrepancy_cutoff = 0,bet_choice=bet_choice[j])
        for competition in competitions:
            for season in seasons:
                output["Algorithm"].append("Pi_delta_bin_" + str(i) + "_" + bet_choice[j])
                output["Season"].append(season)
                output["Competition"].append(competition)

                output["Pi_bets"].append(len(games_i_j[(games_i_j.Competition == competition) & (games_i_j.Season == season) & (games_i_j.Pi_profit.notnull())].sort_values("Date")))
                output["Pi_stake"].append(len(games_i_j[(games_i_j.Competition == competition) & (games_i_j.Season == season) & (games_i_j.Pi_profit.notnull())].sort_values("Date")))
                output["Pi_profit"].append(games_i_j[(games_i_j.Competition == competition) & (games_i_j.Season == season) & (games_i_j.Pi_profit.notnull())].sort_values("Date").Pi_profit.sum())


output = pd.DataFrame(output) 
betting_strategies = list(set(output.Algorithm))

# Get condensed output
output_condensed = dict()
output_condensed["Strategy"] = list()
output_condensed["Stake"] = list()
output_condensed["Profit"] = list()
output_condensed["Profitability"] = list()

for betting_strategy in betting_strategies:
    output_i = output[output.Algorithm == betting_strategy]
    
    output_condensed["Strategy"].append(betting_strategy)
    output_condensed["Stake"].append(output_i.Pi_stake.sum())
    output_condensed["Profit"].append(output_i.Pi_profit.sum())
    output_condensed["Profitability"].append(100*(output_i.Pi_profit.sum()/output_i.Pi_stake.sum()))

output_condensed = pd.DataFrame(output_condensed)     
pickle.dump(list([output_condensed,bins]),open("app_betting/result/pi_profitable_betting_strategies.p","wb"))
        # Add Total
        # output["Season"].append(seasons[0].split("-")[0] + "-" + seasons[-1].split("-")[1])
        # output["Competition"].append("All")
        # output["Pi_bets"].append(sum(output["Pi_bets"]))
        # output["Pi_stake"].append(sum(output["Pi_stake"]))
        # output["Pi_profit"].append(sum(output["Pi_profit"]))
        
# Only seasons where Pi Rating is already trained    
# training_seasons = 5
# seasons = sorted(list(set(games.Season)))[training_seasons:]
# games = games[games.Season.isin(seasons)]

# Only certain months
# month_column = pd.DatetimeIndex(games.Date).month
# games.loc[:,"month"] = month_column
# months = list(range(7,13))
# games = games[games.month.isin(months)]

# Only HomeWins
# games = games[(games.FTAG == games.FTHG)]

# Bet?
# games = games[games.bet_placed == "2"]






 
# Add Total
# output["Season"].append(seasons[0].split("-")[0] + "-" + seasons[-1].split("-")[1])
# output["Competition"].append("All")
# output["Pi_bets"].append(sum(output["Pi_bets"]))
# output["Pi_stake"].append(sum(output["Pi_stake"]))
# output["Pi_profit"].append(sum(output["Pi_profit"]))

