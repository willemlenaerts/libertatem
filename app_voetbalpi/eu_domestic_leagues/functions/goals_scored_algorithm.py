# Algorithm to determine FTHG/FTAG from a expected Goal Difference (GDe)
# as defined by the Pi Rating Algorithm

import pickle
import numpy as np
import pandas as pd
import scipy.stats

poisson_lambda_home = 1.91
poisson_lambda_away = 1.16
gd_poisson = poisson_lambda_home - poisson_lambda_away

simulations = 10000
GDe_interval = 0.01
GDe_add = int(np.log10(1/GDe_interval))
GDe = np.arange(-10,10,GDe_interval)

output = dict()
output["GDe"] = []
output["chances_home_goal"] = []
output["chances_away_goal"] = []


for GDe_i in GDe:
    output["GDe"].append(GDe_i)
    if GDe_i >= 0:
        poisson_lambda_home_sim = poisson_lambda_home + (GDe_i- gd_poisson)
        poisson_lambda_away_sim = poisson_lambda_away
    else:
        poisson_lambda_home_sim = poisson_lambda_home
        poisson_lambda_away_sim = poisson_lambda_away + (-GDe_i + gd_poisson)            
    
    
    # Simulate FTHG and FTAG
    chances_home_goal = np.zeros((1,15))
    chances_away_goal = np.zeros((1,15))
    for goals in range(15):
        chances_home_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,poisson_lambda_home_sim)
        chances_away_goal[0,goals] = scipy.stats.distributions.poisson.pmf(goals,poisson_lambda_away_sim)

    # Make chances sum to 1 (we ignore more than 14 goals)
    chances_home_goal /= chances_home_goal.sum()
    chances_away_goal /= chances_away_goal.sum()
    
    output["chances_home_goal"].append(chances_home_goal[0])
    output["chances_away_goal"].append(chances_home_goal[0])
    
output = pd.DataFrame(output)
 
FTHG = np.zeros((len(GDe),simulations))
FTAG = np.zeros((len(GDe),simulations))
for i in range(len(GDe)):
    FTHG[i,:] = np.random.choice(list(range(15)), p=output[(output.GDe < (round(GDe[i],GDe_add)+GDe_interval/10)) & (output.GDe > (round(GDe[i],GDe_add)-GDe_interval/10))].chances_home_goal.iloc[0],size=simulations)
    FTAG[i,:] = np.random.choice(list(range(15)), p=output[(output.GDe < (round(GDe[i],GDe_add)+GDe_interval/10)) & (output.GDe > (round(GDe[i],GDe_add)-GDe_interval/10))].chances_away_goal.iloc[0],size=simulations)
             
pickle.dump(output,open("app_voetbalpi/eu_domestic_leagues/data/input/goal_chances.p","wb"))
pickle.dump(FTHG.astype(np.int64),open("app_voetbalpi/eu_domestic_leagues/data/input/FTHG_simulation.p","wb"))
pickle.dump(FTAG.astype(np.int64),open("app_voetbalpi/eu_domestic_leagues/data/input/FTAG_simulation.p","wb"))