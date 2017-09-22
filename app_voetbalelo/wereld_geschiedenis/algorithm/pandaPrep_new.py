import pickle
import json
import pandas as pd
import numpy as np
import datetime
import time

# Import data (don't use database for now)
panda = pickle.load(open("app_voetbalelo/wereld_geschiedenis/algorithm/results/games-1872-2015.p","rb"))

# All countries that played in dataset:
countries = list(panda["HomeTeam"].unique())
countries.sort()

# All dates (as unix)
dates = [int(i) for i in list(panda.index.astype(np.int64) // 10 ** 6)]

# Seasons
years = sorted(list(panda["Y"].unique()))

# ELO value for every country on every date (dict with keys countries and values elo
data = dict()
max_elo = dict()
min_elo = dict()

# # For every year, define date_index
# start_index = 0
# interval_mem = 0
# date_index = dict()
# dates_index = list()
# last_year = years[0]
# for year in years:
#     if year != years[0]:
#         year_interval = int(year) - int(last_year)
#     else:
#         year_interval = 1
        
#     start = time.time()
#     dummy = []
#     for country in countries:
#         dummy.append(len(panda[(panda.Y == year) & ((panda.HomeTeam == country) | (panda.AwayTeam == country))]))
#     max_speeldagen = max(dummy) + 1 # increment before new year (null value between years)
#     if max_speeldagen == 1:
#         max_speeldagen = 10 + 1
    
#     # Date_index
#     date_index[year] = [interval_mem + 1000000*10*(year_interval-1)+1000000*int(i) for i in list(range(start_index,start_index+max_speeldagen))]
#     interval_mem += 1000000*10*(year_interval-1)
#     start_index += max_speeldagen
    
#     last_year = year
#     stop = time.time()
#     print("Year: " + year + " || Time: " + str(int(stop-start)) + " || Interval: " + str(year_interval) + " year")
#     # First search max_speeldagen
    
#     dates_index += date_index[year]

dates_reversed = dict()
for i in range(len(dates)):
    dates_reversed[str(dates[i])] = str(datetime.datetime.fromtimestamp(dates[i]/1000).year)

# Get games_table
game_table = []
for i in range(len(panda)):
    game_table.append({"datum":dates[i],
                        "type":panda.TYPE[i],
                        "wedstrijd":panda.HomeTeam[i] + " - " + panda.AwayTeam[i],
                        "score":panda.FTHG[i] + " - " + panda.FTAG[i]})

country_table = []
for counter,country in enumerate(countries):
    start = time.time()
    max_elo[country] = []
    min_elo[country] = []
    data[country] = dict()
    
    wedstrijden_totaal_string = len(pd.concat([panda[(panda.HomeTeam == country)],panda[(panda.AwayTeam == country)]]))
    winst_string = len(pd.concat([panda[(panda.HomeTeam == country) & (panda.FTHG.astype(float) > panda.FTAG.astype(float))],panda[(panda.AwayTeam == country) & (panda.FTAG.astype(float) > panda.FTHG.astype(float))]]))
    gelijk_string = len(pd.concat([panda[(panda.HomeTeam == country) & (panda.FTHG.astype(float) == panda.FTAG.astype(float))],panda[(panda.AwayTeam == country) & (panda.FTAG.astype(float) == panda.FTHG.astype(float))]]))
    verlies_string = len(pd.concat([panda[(panda.HomeTeam == country) & (panda.FTHG.astype(float) < panda.FTAG.astype(float))],panda[(panda.AwayTeam == country) & (panda.FTAG.astype(float) < panda.FTHG.astype(float))]]))
    
    # for i in range(len(panda[panda.HomeTeam == country])):
    #     wedstrijden_totaal_string += 1
    #     if int(panda[panda.HomeTeam == country].FTHG[i]) > int(panda[panda.HomeTeam == country].FTAG[i]):
    #         winst_string += 1
    #     elif int(panda[panda.HomeTeam == country].FTHG[i]) == int(panda[panda.HomeTeam == country].FTAG[i]):
    #         gelijk_string += 1
    #     else:    
    #         verlies_string += 1
    
    # for i in range(len(panda[panda.AwayTeam == country])):
    #     wedstrijden_totaal_string += 1
    #     if int(panda[panda.AwayTeam == country].FTHG[i]) > int(panda[panda.AwayTeam == country].FTAG[i]):
    #         verlies_string += 1
    #     elif int(panda[panda.AwayTeam == country].FTHG[i]) == int(panda[panda.AwayTeam == country].FTAG[i]):
    #         gelijk_string += 1
    #     else:    
    #         winst_string += 1            
    try: 
        nuelo = str(int(pd.concat([panda[(panda.HomeTeam == country) & (panda.index.astype(datetime.datetime) > datetime.datetime(2015, 1, 1,0,0))]["HomeElo"],panda[(panda.AwayTeam == country) & (panda.index.astype(datetime.datetime) > datetime.datetime(2015, 1, 1,0,0))]["AwayElo"]]).sort_index()[-1]))
    except:
        nuelo = ""
    doelpuntensaldo = sum([int(i) for i in pd.concat([panda[(panda.HomeTeam == country)]["FTHG"],panda[(panda.AwayTeam == country)]["FTAG"]])]) - sum([int(i) for i in pd.concat([panda[(panda.HomeTeam == country)]["FTAG"],panda[(panda.AwayTeam == country)]["FTHG"]])])
    doelpuntensaldo_perwedstrijd = round(doelpuntensaldo/wedstrijden_totaal_string,2)
    country_table.append({
                        "country":country,
                        "nuelo": nuelo,
                        "gemelo": str(int(sum(pd.concat([panda[(panda.HomeTeam == country)]["HomeElo"],panda[(panda.AwayTeam == country)]["AwayElo"]]))/len(pd.concat([panda[(panda.HomeTeam == country)]["HomeElo"],panda[(panda.AwayTeam == country)]["AwayElo"]])))),
                        "maxelo": str(int(max(pd.concat([panda[(panda.HomeTeam == country)]["HomeElo"],panda[(panda.AwayTeam == country)]["AwayElo"]])))),
                        "minelo": str(int(min(pd.concat([panda[(panda.HomeTeam == country)]["HomeElo"],panda[(panda.AwayTeam == country)]["AwayElo"]])))),
                        "jaren": len(list(set(pd.concat([panda[(panda.HomeTeam == country)],panda[(panda.AwayTeam == country)]]).Y))),
                        "wedstrijden":str(wedstrijden_totaal_string),
                        "wedstrijdenwinst": str(winst_string),
                        "wedstrijdengelijk":str(gelijk_string),
                        "wedstrijdenverlies":str(verlies_string),
                        "goalsvoor": sum([int(i) for i in pd.concat([panda[(panda.HomeTeam == country)]["FTHG"],panda[(panda.AwayTeam == country)]["FTAG"]])]) ,
                        "goalstegen": sum([int(i) for i in pd.concat([panda[(panda.HomeTeam == country)]["FTAG"],panda[(panda.AwayTeam == country)]["FTHG"]])]),
                        "winperc": str(round(100*(winst_string/wedstrijden_totaal_string),1)),
                        "doelpuntensaldo": doelpuntensaldo_perwedstrijd                   
                        })
    # data[country]["kampioenschappen"] = len(country_results[country])
    data[country]["gemiddelde elo"] = int(sum(pd.concat([panda[(panda.HomeTeam == country)]["HomeElo"],panda[(panda.AwayTeam == country)]["AwayElo"]]))/len(pd.concat([panda[(panda.HomeTeam == country)]["HomeElo"],panda[(panda.AwayTeam == country)]["AwayElo"]])))
    data[country]["hoogste elo"] = int(max(pd.concat([panda[(panda.HomeTeam == country)]["HomeElo"],panda[(panda.AwayTeam == country)]["AwayElo"]])))
    data[country]["laagste elo"] = int(min(pd.concat([panda[(panda.HomeTeam == country)]["HomeElo"],panda[(panda.AwayTeam == country)]["AwayElo"]])))
    
    for year in years:
        data[country][year] = list()
        dataframe_elo = pd.concat([panda[(panda.HomeTeam == country) & (panda.Y == year)]["HomeElo"],panda[(panda.AwayTeam == country) & (panda.Y == year)]["AwayElo"]]).sort_index()
        # dataframe_date_index = pd.concat([panda[(panda.HomeTeam == country) & (panda.Y == year)]["DATE_INDEX"],panda[(panda.AwayTeam == country) & (panda.Y == year)]["DATE_INDEX"]]).sort_index()
        dataframe_wedstrijd = pd.concat([country + " - " + panda[(panda.HomeTeam == country) & (panda.Y == year)]["AwayTeam"],panda[(panda.AwayTeam == country) & (panda.Y == year)]["HomeTeam"] + " - " + country ]).sort_index()
        dataframe_3 = pd.concat([panda[(panda.HomeTeam == country) & (panda.Y == year)]["FTHG"],panda[(panda.AwayTeam == country) & (panda.Y == year)]["FTHG"]]).sort_index()
        dataframe_4 = pd.concat([panda[(panda.HomeTeam == country) & (panda.Y == year)]["FTAG"],panda[(panda.AwayTeam == country) & (panda.Y == year)]["FTAG"]]).sort_index()
        dataframe_type = pd.concat([panda[(panda.HomeTeam == country) & (panda.Y == year)]["TYPE"],panda[(panda.AwayTeam == country) & (panda.Y == year)]["TYPE"]]).sort_index()

        # [0]: Datum index (niet echte datum maar plotdatum)
        data[country][year].append([int(i) for i in list(dataframe_elo.index.astype(np.int64) // 10 ** 6)])
        # data[country][year].append(date_index[year][:len(dataframe_elo)])
        
        # [1]: ELO na wedstrijd
        data[country][year].append([int(i) for i in list(dataframe_elo)])
        # data[country][year].append([int(i) for i in list(dataframe_elo)])
        
        # Get maximum elo
        # Remove None's
        
        try:
            max_elo[country].append(max(list(data[country][year][-1])))
        except:
            # Dit seizoen speelde ploeg niet
            max_elo[country].append(0)

        # Get minimum elo
        try:
            min_elo[country].append(min(list(data[country][year][-1])))
        except:
            # Dit seizoen speelde ploeg niet
            min_elo[country].append(0)
            
        # [2]: Wedstrijd in string (HomeTeam - AwayTeam)
        data[country][year].append(list(dataframe_wedstrijd))
        
        # [3]: Score (Home Goals - Away Goals)
        data[country][year].append([])
        for i in range(len(dataframe_elo)):
            data[country][year][-1].append(dataframe_3[i] + " - " + dataframe_4[i])
        
        # # [4]: Datum wedstrijd
        # dataframe_elo_index_list = [int(i) for i in list(dataframe_elo.index.astype(np.int64) // 10 ** 6)]
        # data[country][year].append([])
        # for i in range(len(date_index[year])):
        #     try:
        #         data[country][year][-1].append(dataframe_elo_index_list[i])
        #     except:
        #         data[country][year][-1].append(None)
        
        # data[country][year].append([int(i) for i in list(dataframe_elo.index.astype(np.int64) // 10 ** 6)])
        
        # [5]: Type of game
        data[country][year].append(list(dataframe_type))
        
        # # [6]: Kampioen (1: ja, 0: nee)
        # data[country][year].append(0)   
        # if len(country_results[country]) > 0:
        #     for kampioenschap_seizoen in country_results[country]:
        #         if kampioenschap_seizoen == year:
        #             data[country][year][-1] = 1
        #             break
        
    max_elo[country] = max(max_elo[country])
    min_elo[country] = min(list(filter((0).__ne__, min_elo[country])))
    
    stop = time.time()
    print("Team: " + country + " || Time: " + str(int(stop-start)) + " s")
    
max_elo_data = dict()
for country in countries:
    max_elo_data[country] = list()
    for s in range(len(years)):
        for i in range(len(data[country][years[s]][1])):
            if data[country][years[s]][1][i] == max_elo[country]:
                max_elo_data[country].append([s,i])

min_elo_data = dict()
for country in countries:
    min_elo_data[country] = list()
    for s in range(len(years)):
        for i in range(len(data[country][years[s]][1])):
            if data[country][years[s]][1][i] == min_elo[country]:
                min_elo_data[country].append([s,i])

# pickle.dump(data,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/elo-evolution.p","wb"))
# pickle.dump(countries,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/countries.p","wb"))
# pickle.dump(dates,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/dates.p","wb"))
# pickle.dump(years,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/years.p","wb"))
# pickle.dump(max_elo_data,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/max_elo_data.p","wb"))

# Per country

for country in countries:
    data_country = dict()
    data_country[country] = data[country]
    json.dump(data_country,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/json.dump/countries/" + country + ".json","w"))

json.dump(data,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/json.dump/elo-evolution.json","w"))
json.dump(dates,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/json.dump/dates.json","w"))
json.dump(dates_reversed,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/json.dump/dates_reversed.json","w"))
json.dump(country_table,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/json.dump/country_table.json","w"))
json.dump(game_table,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/json.dump/game_table.json","w"))
json.dump(countries,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/json.dump/countries.json","w"))
json.dump(years,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/json.dump/years.json","w"))
json.dump(max_elo_data,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/json.dump/max_elo_data.json","w"))
json.dump(min_elo_data,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/json.dump/min_elo_data.json","w"))