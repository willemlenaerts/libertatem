import pickle
import pandas as pd
from collections import Counter
import datetime

tdf = pickle.load(open("app_tourdefrance/algorithm/results/tdf.p","rb"))

# Test all times
errors = []
for i in range(len(tdf)):
    try:
        dummy = list(tdf.RITUITSLAG.str[2][i])
    except:
        continue
    for j in range(len(dummy)):
        if j != 0 and j!= 1:
            try:
                if dummy[j] + 1000 < dummy[j-1]:
                    # if dummy.count(dummy[j]) == 1:
                    errors.append([i,tdf.NAME[i], j])
                    # if dummy.count(dummy[j-1]) == 1:
                        # errors.append([i,tdf.NAME[i], j-1])   
            except:
                pass
                
# Get years
years = []
for i in range(len(tdf)):
    years.append(datetime.datetime.fromtimestamp(tdf.index[i].value/1000000000).year)

years = list(set(sorted(years)))
# 3 renners zelfde ploeg in top 10
ritten = []
for i in range(len(tdf)):
    try:
        rituitslag = list(tdf.RITUITSLAG.str[0][i])
        rituitslag_teams = list(tdf.RITUITSLAG.str[1][i])
    except:
        pass

    # Check of team 3 keer voorkomt in eerste 10
    check = Counter(rituitslag_teams[0:10])
    for key in list(check.keys()):
        if key != "" and check[key] >= 3:
            ritten.append([i,tdf["NAME"][i],key,tdf["TERRAIN"][i]])

# Level Playing Field, algemeen klassement
test = []
for year in years:
    if year != 2015:
        tdf_year = tdf[(tdf.index > datetime.datetime(year,1,1)) & (tdf.index < datetime.datetime(year+1,1,1))]
        test.append([year,sum(list(tdf_year.KLASSEMENT.str[2][-1])[1:10])])

# Bergritten
tdf_bergritten = tdf[(tdf.TERRAIN.str.contains("mountain") == True) | (tdf.TERRAIN.str.contains("Mountain") == True)]
ritten = []
for i in range(len(tdf_bergritten)):
    try:
        rituitslag = list(tdf_bergritten.RITUITSLAG.str[0][i])
        rituitslag_teams = list(tdf_bergritten.RITUITSLAG.str[1][i])
    except:
        pass

    # Check of team 3 keer voorkomt in eerste 10
    check = Counter(rituitslag_teams[0:10])
    for key in list(check.keys()):
        if key != "" and check[key] >= 3:
            ritten.append([i,tdf_bergritten["NAME"][i],key,tdf_bergritten["TERRAIN"][i]])

# Time trials
test = []
tdf_tijdritten = tdf[(tdf.TERRAIN.str.contains("Individual time trial") == True) | (tdf.TERRAIN.str.contains("Individual Time Trial") == True)]
for year in years:
    if year != 2015:
        tdf_tijdritten_year = tdf_tijdritten[(tdf_tijdritten.index > datetime.datetime(year,1,1)) & (tdf_tijdritten.index < datetime.datetime(year+1,1,1))]
        test.append([year,sum(list(tdf_tijdritten_year.RITUITSLAG.str[2][-1])[1:10]) / sum(list(tdf_tijdritten_year.LENGTH.astype(float)))])
        
# Every rider who once was in top 3 in mountain stage AND Individual time trial
test = []
tdf_bergritten = tdf[(tdf.TERRAIN.str.contains("mountain") == True) | (tdf.TERRAIN.str.contains("Mountain") == True)]
tdf_tijdritten = tdf[(tdf.TERRAIN.str.contains("Individual time trial") == True) | (tdf.TERRAIN.str.contains("Individual Time Trial") == True)]
# tdf_berg_tijd = pd.concat([tdf_bergritten,tdf_tijdritten]).sort_index()
for year in years:
    test.append([year])
    if year != 2015:
        tdf_tijdritten_year = tdf_tijdritten[(tdf_tijdritten.index > datetime.datetime(year,1,1)) & (tdf_tijdritten.index < datetime.datetime(year+1,1,1))]
        tdf_bergritten_year = tdf_bergritten[(tdf_bergritten.index > datetime.datetime(year,1,1)) & (tdf_bergritten.index < datetime.datetime(year+1,1,1))]
        renner_bergritten = []
        for i in range(len(tdf_bergritten_year.RITUITSLAG.str[0])):
            try:
                renner_bergritten= renner_bergritten + list(tdf_bergritten_year.RITUITSLAG.str[0][i])[0:3]
            except:
                pass
        renner_tijdritten = []
        for i in range(len(tdf_tijdritten_year.RITUITSLAG.str[0])):
            try:
                renner_tijdritten = renner_tijdritten + list(tdf_tijdritten_year.RITUITSLAG.str[0][i])[0:3]
            except:
                pass
            
        for renner in renner_bergritten:
            if renner in renner_tijdritten:
                test[-1].append(renner)
        
        test[-1][1:] = list(set(test[-1][1:]))
        # tdf_berg_tijd_year = tdf_berg_tijd[(tdf_berg_tijd.index > datetime.datetime(year,1,1)) & (tdf_berg_tijd.index < datetime.datetime(year+1,1,1))]
        
# Check Dominance of TdF winner (time gains on rest of top 10 in ITT and Mountain stage)
tdf_table = list() # Year, TourWinner, TimeTrialIndex, ClimbIndex, RelativePowerIndex
stage_table = list() # Year, Date, TourWinner, Stage, Type, RelativePowerIndexperStage
test = []
stages = []
tdf_bergritten = tdf[(tdf.TERRAIN.str.contains("mountain") == True) | (tdf.TERRAIN.str.contains("Mountain") == True)]
tdf_tijdritten = tdf[(tdf.TERRAIN.str.contains("Individual time trial") == True) | (tdf.TERRAIN.str.contains("Individual Time Trial") == True)] 

compare_with = 9
errors = []
for year in years:
    if year != 1966 and year != 1960: # year != 1966 and year != 1975
        test.append([year])
        tdf_tijdritten_year = tdf_tijdritten[(tdf_tijdritten.index > datetime.datetime(year,1,1)) & (tdf_tijdritten.index < datetime.datetime(year+1,1,1))]
        tdf_bergritten_year = tdf_bergritten[(tdf_bergritten.index > datetime.datetime(year,1,1)) & (tdf_bergritten.index < datetime.datetime(year+1,1,1))]
        
        tdf_year = tdf[(tdf.index > datetime.datetime(year,1,1)) & (tdf.index < datetime.datetime(year+1,1,1))]
        
        # Find WINNER of Tdf of this year &Rest of top 10
        winner = list(tdf_year.KLASSEMENT.str[0][-1])[0]
        rest = list(tdf_year.KLASSEMENT.str[0][-1])[1:compare_with+1]
        test[-1].append(winner)
        
        # Tijdritten
        rest_time = [0]*len(rest)
        test[-1].append(0)
        for i in range(len(tdf_tijdritten_year)):
            
            
            print(tdf_tijdritten_year.NAME[i])
            try:
                ranking = list(tdf_tijdritten_year.RITUITSLAG.str[0][i])
                timing = list(tdf_tijdritten_year.RITUITSLAG.str[2][i])
            except:
                continue
            
            
            # Remove empty stages (or the stage after casartelli death in 1995 (2 withdrawls ==> not zero the ranking))            
            if len(ranking) < 4 and len(timing) < 4:
                continue
            
            rest_winner_rank = -1
            count_rest = []
            count_winner = 0
            for j in range(len(ranking)):
                if ranking[j] == winner:
                    count_winner += 1
                    winner_time = timing[j]
                    winner_rank = j + 1
                else:
                    
                    for k in range(len(rest)):
                        if ranking[j] == rest[k]:
                            count_rest.append(rest[k])
                            rest_time[k] = timing[j]
                            if j == 0:
                                rest_winner_rank = k
            
            if count_winner != 1:
                print(str(year) + " " + str(count_winner) + " " + winner)
                errors.append(["winner", i,tdf_tijdritten_year.NAME[i], winner, count_winner])
            if len(count_rest) != len(rest):
                if len(count_rest) < len(rest):
                    errors.append([i,tdf_tijdritten_year.NAME[i], list(set(rest) - set(count_rest))])
                else:
                    errors.append([i,tdf_tijdritten_year.NAME[i], list(set(count_rest) - set(rest))])
            
            stages.append([year,tdf_tijdritten_year.index[i].value/1000000000, winner, "ITT",tdf_tijdritten_year.NAME[i] ,0]) 
            for j in range(len(rest_time)):
                if winner_rank == 1:
                    test[-1][-1] += rest_time[j]
                    stages[-1][-1] +=  rest_time[j]
                    print(rest_time[j])
                else:
                    if rest_winner_rank == -1:
                        test[-1][-1] += (rest_time[j] - winner_time)
                        stages[-1][-1] +=  (rest_time[j] - winner_time)
                        print(rest_time[j] - winner_time)
                    elif rest_winner_rank == j:
                        test[-1][-1] += -winner_time/float(tdf_tijdritten_year.LENGTH[i])
                        stages[-1][-1] +=  -winner_time/float(tdf_tijdritten_year.LENGTH[i])
                        print(-winner_time)
                    else:
                        test[-1][-1] += (rest_time[j] - winner_time)
                        stages[-1][-1] +=  (rest_time[j] - winner_time)
                        print(rest_time[j] - winner_time)
            
            stages[-1][-1] = int(round(100*round(stages[-1][-1]/(compare_with*tdf_tijdritten_year.LENGTH.astype(float)[i]),2)))/100
        
        test[-1][-1] = round(test[-1][-1]/(compare_with*sum(list(tdf_tijdritten_year.LENGTH.astype(float)))),2)
        
        # Bergritten
        rest_time = [0]*len(rest)
        test[-1].append(0)
        count_real_mountain_stages = 0
        for i in range(len(tdf_bergritten_year)):
            
            print(tdf_bergritten_year.NAME[i])
            
            
            try:
                ranking = list(tdf_bergritten_year.RITUITSLAG.str[0][i])
                timing = list(tdf_bergritten_year.RITUITSLAG.str[2][i])
            except:
                continue
            
            if len(ranking) >=4 and len(ranking) < 50:
                errors.append([i,tdf_bergritten_year.NAME[i]])   
                
            if len(ranking) < 4 and len(timing) < 4:
                continue
            
            rest_winner_rank = -1
            count_rest = []
            count_winner = 0
            for j in range(len(ranking)):
                if ranking[j] == winner:
                    count_winner += 1
                    winner_time = timing[j]
                    winner_rank = j + 1
                else:
                    
                    for k in range(len(rest)):
                        if ranking[j] == rest[k]:
                            count_rest.append(rest[k])
                            rest_time[k] = timing[j]
                            if j == 0:
                                rest_winner_rank = k
            if count_winner != 1:
                print(str(year) + " " + str(count_winner) + " " + winner)       
                errors.append(["winner", i,tdf_bergritten_year.NAME[i], winner, count_winner])
            if len(count_rest) != len(rest):
                if len(count_rest) < len(rest):
                    errors.append([i,tdf_bergritten_year.NAME[i], list(set(rest) - set(count_rest))])
                else:
                    errors.append([i,tdf_bergritten_year.NAME[i], list(set(count_rest) - set(rest))])
                
            # Only REAL Mountain stages:
            # Average delta time > 10 seconds
            test_ms = 0
            for j in range(len(rest_time)):
                if winner_rank == 1:
                    test_ms += abs(rest_time[j])
                    
                else:
                    if rest_winner_rank == -1:
                        test_ms += abs(rest_time[j] - winner_time)
                        
                    elif rest_winner_rank == j:
                        test_ms += abs(-winner_time)
                        
                    else:
                        test_ms += abs(rest_time[j] - winner_time)
        
            if test_ms/compare_with < 60:
                continue
            
            count_real_mountain_stages += 1
            
            stages.append([year, tdf_bergritten_year.index[i].value/1000000000, winner, "Mountain",tdf_bergritten_year.NAME[i],0 ])
            for j in range(len(rest_time)):
                if winner_rank == 1:
                    test[-1][-1] += rest_time[j]
                    stages[-1][-1] += rest_time[j] 
                    print(rest_time[j])
                else:
                    if rest_winner_rank == -1:
                        test[-1][-1] += rest_time[j] - winner_time
                        stages[-1][-1] += rest_time[j] - winner_time
                        print(rest_time[j] - winner_time)
                    elif rest_winner_rank == j:
                        test[-1][-1] += -winner_time
                        stages[-1][-1] += -winner_time 
                        print(-winner_time)
                    else:
                        test[-1][-1] += rest_time[j] - winner_time
                        stages[-1][-1] += rest_time[j] - winner_time
                        print(rest_time[j] - winner_time)
                        
            stages[-1][-1] = round(stages[-1][-1]/(100*compare_with),2)
            
        if count_real_mountain_stages == 0:
            test[-1][-1] = "-"
        else:
            # Per 100 km (om betere vergelijking te kunnen maken met Time Trials (die wel per km worden berekend))
            test[-1][-1] = round(test[-1][-1]/(compare_with*100*count_real_mountain_stages),2) 
        
        # Calculate some sort of RELATIVE POWER INDEX for Tour Winner
        if test[-1][-1] != "-":
            test[-1].append(round(test[-1][-2] + test[-1][-1],2))
        else:
            test[-1].append(round(test[-1][-2]))

# Make sure sum of CI over all years = sum of TTI over all years
sum_tti = 0
sum_ci = 0
for t in test:
    sum_tti += t[2]
    sum_ci += t[3]

for t in test:
    t[3] = round(t[3]*(sum_tti/sum_ci),2)
    t[4] = round(t[2] + t[3],2)


sum_tt = dict()
sum_ms = dict()
for s in stages:
    if s[0] not in sum_tt.keys():
        sum_tt[s[0]] = [0,0]
        sum_ms[s[0]] = [0,0]
    if s[3] == "Mountain":
        sum_ms[s[0]][0] += s[5]
        sum_ms[s[0]][1] += 1                
    else:
        sum_tt[s[0]][0] += s[5]
        sum_tt[s[0]][1] += 1

for s in stages:
    for t in test:
        if s[0] == t[0]: 
            if s[3] == "Mountain":
                s[5] = round(s[5]*(t[3]/(sum_ms[s[0]][0]/sum_ms[s[0]][1])),2)
            else:
                s[5] = round(s[5]*(t[2]/(sum_tt[s[0]][0]/sum_tt[s[0]][1])),2)

# for s in stages:
#     if s[3] == "Mountain":
#         s[5] = round(s[5]*(sum_tti/sum_ci),2)
    
# Fill tdf_table
for t in test:
    tdf_table.append({  "Year": t[0],
                        "TourWinner": t[1],
                        "TimeTrialIndex": t[2] , 
                        "ClimbIndex": t[3], 
                        "RelativePowerIndex": t[4]
                    })
    
# Fill stage_table
from datetime import datetime
for s in stages:
    stage_type = "ITT"
    if s[3] == "Mountain":
        stage_type = "M"
    stage_table.append({"Year": s[0], 
                        "Date": datetime.fromtimestamp(int(s[1])).strftime('%d/%m/%Y'), 
                        "TourWinner": s[2], 
                        "Type": stage_type, 
                        "Stage": s[4].split(" ")[-1], 
                        "RelativePowerIndexperStage": s[5]
                })

# Make RPI graph
rpi = []
for i in range(len(tdf_table)):
    rpi.append({"x": tdf_table[i]["Year"],
                "y": tdf_table[i]["RelativePowerIndex"],
                "TourWinner": tdf_table[i]["TourWinner"]})

# Make Stacked CI/TTI = RPI Graph
ci = []
tti = []
for i in range(len(tdf_table)):
    if tdf_table[i]["ClimbIndex"] == "-":
        continue
    ci.append({"x": tdf_table[i]["Year"],
                "y": tdf_table[i]["ClimbIndex"],
                "TourWinner": tdf_table[i]["TourWinner"],
                "RPI": tdf_table[i]["RelativePowerIndex"],
                "TTI": tdf_table[i]["TimeTrialIndex"]})
                
    tti.append({"x": tdf_table[i]["Year"],
                "y": tdf_table[i]["TimeTrialIndex"],
                "RPI": tdf_table[i]["RelativePowerIndex"],
                "CI": tdf_table[i]["ClimbIndex"],
                "TourWinner": tdf_table[i]["TourWinner"]})
    
# Make graph
scatter_plot_tdf = []
x_axis_tdf_dummy = []
y_axis_tdf_dummy = []
winners_tdf = []
for i in range(len(tdf_table)):
    if tdf_table[i]["ClimbIndex"] == "-":
        continue
    winners_tdf.append(tdf_table[i]["TourWinner"])
    x_axis_tdf_dummy.append(tdf_table[i]["TimeTrialIndex"])
    y_axis_tdf_dummy.append(tdf_table[i]["ClimbIndex"])
    scatter_plot_tdf.append({  "x": tdf_table[i]["TimeTrialIndex"],
                                "y": tdf_table[i]["ClimbIndex"],
                                "TourWinner": tdf_table[i]["TourWinner"] ,
                                "RelativePowerIndex": tdf_table[i]["RelativePowerIndex"],
                                "Year":tdf_table[i]["Year"]})

winners_tdf = list(set(winners_tdf))
x_axis_tdf = []
y_axis_tdf = []
x_axis_tdf.append(min(x_axis_tdf_dummy))
x_axis_tdf.append(max(x_axis_tdf_dummy))
y_axis_tdf.append(min(y_axis_tdf_dummy))
y_axis_tdf.append(max(y_axis_tdf_dummy))

import json
json.dump(tdf_table, open("app_tourdefrance/algorithm/results/json/tdf_table.json","w"))
json.dump(stage_table, open("app_tourdefrance/algorithm/results/json/stage_table.json","w"))

json.dump(rpi,open("app_tourdefrance/algorithm/results/json/rpi.json","w"))
json.dump(ci,open("app_tourdefrance/algorithm/results/json/ci.json","w"))
json.dump(tti,open("app_tourdefrance/algorithm/results/json/tti.json","w"))

json.dump(scatter_plot_tdf,open("app_tourdefrance/algorithm/results/json/scatter_plot_tdf.json","w"))
json.dump(x_axis_tdf,open("app_tourdefrance/algorithm/results/json/x_axis_tdf.json","w"))
json.dump(y_axis_tdf,open("app_tourdefrance/algorithm/results/json/y_axis_tdf.json","w"))
json.dump(winners_tdf,open("app_tourdefrance/algorithm/results/json/winners_tdf.json","w"))