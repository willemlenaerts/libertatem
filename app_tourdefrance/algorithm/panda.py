# Make prediction % chance to win tour based on historical data

import pickle
import pandas as pd
import datetime
import time

# tdf file, keys: START/FINISH/DATE/RESULT/CAT/TYPE/NAME
# RESULT FURTHER SPLIT: 
tdf = pickle.load(open("app_tourdefrance/algorithm/data/tdf.p","rb"))
tdf_participants = pickle.load(open("app_tourdefrance/algorithm/data/tdf_participants.p","rb"))
tdf_wiki = pickle.load(open("app_tourdefrance/algorithm/data/tdf_wiki.p","rb"))
tdf_pcs = pickle.load(open("app_tourdefrance/algorithm/data/tdf_pcs.p","rb"))

jj = dict()
for i in range(len(tdf["DATE"])):
    # 2x Jan JANSSEN in 1969: RANK van de echte in elke rit:
    if tdf["YEAR"][i] == 1969:
        jj[tdf["NAME"][i]] = list()
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
            if "Jan JANSSEN" ==  tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                jj[tdf["NAME"][i]].append([j,tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j]])

for i in range(len(tdf["DATE"])):
    # if tdf["DATE"][i] == "24/07/2015":
    #     # Add last stage
    #     tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"] = []
    #     tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"] = []
        
    #     tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["NAME"] = []
    #     tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["TIME"] = []
        
        
    # Fix error on tdf page, 1986 should be 1987
    # tdf["DATE"][976] = "16/07/1987"
    count_1986 = 0
    if tdf["DATE"][i] == "16/07/1986":
        if count_1986 == 1:
            print("jaja")
            tdf["DATE"][i] = "16/07/1987"
        count_1986 += 1
    # Jan JANSSEN Issue (enkel in stage 11 en stage 22.01 voor de echte)
    if tdf["YEAR"][i] == 1969:
        if tdf["NAME"][i].split(" ")[-1] == "11" or tdf["NAME"][i].split(" ")[-1] == "22.01":
            count_jj = 0
            for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
                if "Jan JANSSEN" ==  tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                    if count_jj == 0:
                        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j] = "JAN JANSSEN"
                    count_jj += 1
        else:
            count_jj = 0
            for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
                if "Jan JANSSEN" ==  tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                    if count_jj == 1:
                        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j] = "JAN JANSSEN"
                    count_jj += 1            
                    
    # RITUITSLAG Errors
    if tdf["NAME"][i] == "Tour de France 1947 stage 10":
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
            if "Louis GAUTHIER" ==  tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j] = "Jean-Apo LAZARIDES"

    if tdf["NAME"][i] == "Tour de France 1949 stage 11":
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
            if "Bernardo RUIZ" ==  tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j] = "Jean ROBIC"

    if tdf["NAME"][i] == "Tour de France 1962 stage 18":
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
            if "Jean-Claude LEFEBVRE" ==  tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j] = "Albertus GELDERMANS"
                
    if tdf["NAME"][i] == "Tour de France 1961 stage 10":
        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"].append("Imerio MASSIGNAN")
        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"].append('+ 12\' 21"')

    if tdf["NAME"][i] == "Tour de France 1973 stage 9":
        # Correct Times:
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
            if j != 0:
                if tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] != '+ 00\' 00"':
                    dummy_time = tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j]
                else:
                    if tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j]  != "withdrawls":
                        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = dummy_time
                        
        # Add missing riders:
        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"].append('Luis OCANA')
        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"].append('+ 08\' 50"')
        
        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"].append('Joaquim AGOSTINHO')
        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"].append('+ 08\' 50"')

        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"].append('Jose-Manuel FUENTE')
        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"].append('+ 08\' 50"')

        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"].append('Bernard THEVENET')
        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"].append('+ 08\' 50"')

    if tdf["NAME"][i] == "Tour de France 1962 stage 20":
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
            if "Tiziano GALVANIN" ==  tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j] = "Imerio MASSIGNAN"
                
    # KLASSEMENT Errors           
    if tdf["NAME"][i] == "Tour de France 1975 stage 22":
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["NAME"])):
            if "Juan ZURANO" ==  tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["NAME"][j]:
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["NAME"][j] = "Joop ZOETEMELK"

    if tdf["NAME"][i] == "Tour de France 1949 stage 21":
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["NAME"])):
            if "Marcel ERNZER" ==  tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["NAME"][j]:
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["NAME"][j] = "Jean GOLDSCHMIT"        
    
    # TIMING Errors
    if tdf["NAME"][i] == "Tour de France 1996 prologue":
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
            if "Laurent DUFAUX" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 00\' 44"' 
            if "Frédéric MONCASSIN" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 00\' 29"'
            if "Rolf SORENSEN" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 00\' 37"'
            if "Marino ALONSO" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 01\' 06"'
            if "Oscar PELLICIOLI" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 01\' 14"'   
            if "Marco DELLA VEDOVA" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 01\' 18"'
            if "Daisuke IMANAKA" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 01\' 30"'    
            if "Roberto CONTI" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 02\' 16"'   
    if tdf["NAME"][i] == "Tour de France 2006 stage 13":
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
            if tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] == '+ 00\' 00"' and "Oscar PEREIRO SIO" != tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:

                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 29\' 57"'
                
    if tdf["NAME"][i] == "Tour de France 1997 stage 19":
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
            if tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j] == "Mario TRAVERSONI":

                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '4h 03\' 17"'
            if tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j] == "Bart VOSKAMP":

                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 00\' 26"'
               
    if tdf["NAME"][i] == "Tour de France 1997 stage 14":
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
            if "Jo PLANCKAERT" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j] or \
                "Laurent PILLON" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j] or \
                "Claude LAMOUR" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j] or \
                "Andrei TCHMIL" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j] or \
                "Marc WAUTERS" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j] or \
                "Pascal LANCE" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 36\' 36"'
    if tdf["NAME"][i] == "Tour de France 1996 stage 2" or \
        tdf["NAME"][i] == "Tour de France 1996 stage 4" or \
        tdf["NAME"][i] == "Tour de France 1996 stage 5" or \
        tdf["NAME"][i] == "Tour de France 1996 stage 6" or \
        tdf["NAME"][i] == "Tour de France 1996 stage 7" or \
        tdf["NAME"][i] == "Tour de France 1996 stage 8" or \
        tdf["NAME"][i] == "Tour de France 1996 stage 10" or \
        tdf["NAME"][i] == "Tour de France 1996 stage 11" or \
        tdf["NAME"][i] == "Tour de France 1996 stage 12" or \
        tdf["NAME"][i] == "Tour de France 1996 stage 13" or \
        tdf["NAME"][i] == "Tour de France 1996 stage 14" or \
        tdf["NAME"][i] == "Tour de France 1996 stage 16" or \
        tdf["NAME"][i] == "Tour de France 1996 stage 17":
            last_time = ""
            for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
                if tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] != '+ 00\' 00"':
                    
                    last_time = tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j]
                    last_index = j
            for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
                if j > last_index and tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] == '+ 00\' 00"':
                    
                    tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j]  = last_time
                    
    if tdf["NAME"][i] == "Tour de France 2006 prologue":
        
        dummy_index = 100
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
            if "Vladimir KARPETS" == tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]:
                dummy_index = j
                test = 60*int(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j].split(" ")[1][:2]) + int(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j].split(" ")[2][:2]) + 10
                if test < 60:
                    tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 00\' ' + str(test) +'"'
                else:
                    if len(str(test-60)) == 2:
                        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 01\' ' + str(test-60) +'"'
                    else:
                        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 01\' 0' + str(test-60) +'"'
            if j > dummy_index:
                test = 60*int(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j].split(" ")[1][:2]) + int(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j].split(" ")[2][:2]) + 10
                if test < 60:
                    tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 00\' ' + str(test) +'"'
                else:
                    if len(str(test-60)) == 2:
                        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 01\' ' + str(test-60) +'"'
                    else:
                        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][j] = '+ 01\' 0' + str(test-60) +'"'               
        
# tdf_pcs
# Add last stage of TdF 2006 to LANDIS (missing)
tdf_pcs["2006"]["LANDIS Floyd"]["RITUITSLAG"].append(["69", "Phonak Hearing Systems",",,"])

# tdf_pcs.pop("2014",None)
# Only after WW 2 data [-1593:]
for key in tdf.keys():
    tdf[key] = tdf[key][-1593:]

for key in tdf_wiki.keys():
    tdf_wiki[key] = tdf_wiki[key][-1593:]
    
# Remove TYPE en CAT if keys
tdf.pop("TYPE", None)
tdf.pop("CAT", None)

# # Test
# stages = []
# for year in years:
#     count = 0
#     for i in range(len(tdf["YEAR"])):
#         if tdf["YEAR"][i] == year:
#             count += 1
            
#     stages.append([year,count])
    

# Order tdf["DATE"]
years = list(range(1947,2016))
for year in years:
    count_year = 0
    for i in range(len(tdf["DATE"])):
        if tdf["YEAR"][i] == year:
            t = tdf["NAME"][i].split(" ")
            if count_year == 0:
                tdf["DATE"][i] = datetime.datetime(year,1,1)
                first_index = i
                count_year += 1
                continue
            # else:
            #     # If "prologue"
            #     if t[-1] == "prologue":
            #         tdf["DATE"][i] = datetime.datetime(year,1,1)
            #         tdf["DATE"][first_index] = datetime.datetime(year,1,1) + datetime.timedelta(hours = 1)
            #         continue
            if "." in t[-1]:
                tdf["DATE"][i] = datetime.datetime(year,1,1) + datetime.timedelta(days = int(t[-1].split(".")[0]),hours = int(t[-1].split(".")[1]))
            else:
                tdf["DATE"][i] = datetime.datetime(year,1,1) + datetime.timedelta(days=int(t[-1]))

# Sort based on DATE
tdf["DATE"],tdf["FINISH"],tdf["START"],tdf["NAME"],tdf["RESULT"], tdf["YEAR"] = zip(*sorted(zip(tdf["DATE"],tdf["FINISH"],tdf["START"],tdf["NAME"],tdf["RESULT"], tdf["YEAR"])))
for key in tdf.keys():
    tdf[key] = list(tdf[key])

# Fix tdf_wiki["DATE"]
tdf_1974 = ["27 June 1974","28 June 1974","29 June 1974","30 June 1974", "01 July 1974","02 July 1974",\
                    "03 July 1974","04 July 1974","05 July 1974","06 July 1974","07 July 1974","08 July 1974","09 July 1974",\
                    "11 July 1974","12 July 1974","13 July 1974","14 July 1974","16 July 1974","17 July 1974",\
                    "18 July 1974","19 July 1974","20 July 1974","21 July 1974","22 July 1974","23 July 1974",\
                    "24 July 1974","25 July 1974"]

tdf_1975 = ["26 June 1975","27 June 1975","28 June 1975","29 June 1975", "30 June 1975","01 July 1975",\
                    "02 July 1975","03 July 1975","04 July 1975","05 July 1975","06 July 1975","07 July 1975","09 July 1975",\
                    "10 July 1975","11 July 1975","12 July 1975","13 July 1975","15 July 1975","16 July 1975",\
                    "17 July 1975","18 July 1975","19 July 1975","20 July 1975","21 July 1975","22 July 1975"]

tdf_2006 = ["1 July 2006","2 July 2006","3 July 2006","4 July 2006","5 July 2006","6 July 2006","7 July 2006",\
            "8 July 2006","9 July 2006","11 July 2006","12 July 2006","13 July 2006",\
            "14 July 2006","15 July 2006","16 July 2006","18 July 2006","19 July 2006", "20 July 2006",\
            "21 July 2006","22 July 2006","23 July 2006"]

count_1974 = 0
count_1975 = 0
count_2006 = 0
for i in range(len(tdf_wiki["DATE"])):
    if tdf_wiki["DATE"][i][-4:] == "1974":
        tdf_wiki["DATE"][i] = tdf_1974[count_1974]
        count_1974 += 1
        tdf_wiki["DATE"][i] = datetime.datetime.strptime(tdf_wiki["DATE"][i],"%d %B %Y").strftime("%d/%m/%Y")
    elif tdf_wiki["DATE"][i][-4:] == "1975":
        tdf_wiki["DATE"][i] = tdf_1975[count_1975]
        count_1975 += 1
        tdf_wiki["DATE"][i] = datetime.datetime.strptime(tdf_wiki["DATE"][i],"%d %B %Y").strftime("%d/%m/%Y")
    elif tdf_wiki["DATE"][i][-4:] == "2006":
        tdf_wiki["DATE"][i] = tdf_2006[count_2006]
        count_2006 += 1
        tdf_wiki["DATE"][i] = datetime.datetime.strptime(tdf_wiki["DATE"][i],"%d %B %Y").strftime("%d/%m/%Y")
    else:
        tdf_wiki["DATE"][i] = datetime.datetime.strptime(tdf_wiki["DATE"][i],"%d %B %Y").strftime("%d/%m/%Y")

# Add wiki data
tdf["TERRAIN"] = list()
tdf["LENGTH"] = list()
for i in range(len(tdf["DATE"])):
    tdf["DATE"][i] = tdf_wiki["DATE"][i]
    tdf["TERRAIN"].append(tdf_wiki["TERRAIN"][i])
    tdf["LENGTH"].append(tdf_wiki["LENGTH"][i])

count_plus = 0
# Add tdf_pcs data (DSQ riders like Armstrong et. al.)
for year in tdf_pcs.keys():
    count_year = 0
    for i in range(len(tdf["RESULT"])):
        if tdf["DATE"][i].split("/")[-1] == year:
            # Sort riders based on klassement
            rank_klass = []
            riders_klass = []
            for rider in tdf_pcs[year].keys():
                riders_klass.append(rider)
                try:
                    rank_klass.append(int(tdf_pcs[year][rider]["KLASSEMENT"][0]))
                except:
                    rank_klass.append(1000)
            
            rank_klass, riders_klass  = zip(*sorted(zip(rank_klass, riders_klass)))

            # Sort riders based on rit
            rank_rit = []
            riders_rit = []
            for rider in tdf_pcs[year].keys():
                riders_rit.append(rider)
                try:
                    rank_rit.append(int(tdf_pcs[year][rider]["RITUITSLAG"][count_year][0]))
                except:
                    rank_rit.append(1000)
            
            rank_rit, riders_rit  = zip(*sorted(zip(rank_rit, riders_rit)))            
            
            for rider_klass_i in riders_klass:
                # Add KLASSEMENT for year after last stage
                if count_year == len(tdf_pcs[year][rider_klass_i]["RITUITSLAG"])-1:
                    # if year == "2000":
                    #     print(i)
                    try:
                        rank_klass = int(tdf_pcs[year][rider_klass_i]["KLASSEMENT"][0])
                        team_klass = tdf_pcs[year][rider_klass_i]["KLASSEMENT"][1]
                        time_data_klass = tdf_pcs[year][rider_klass_i]["KLASSEMENT"][2]
                        
                        # print('test1')
                        # Adjust time to tdf time
                        if rank_klass == 1:
                            if len(time_data_klass.split(":")) == 2:
                                time_data_klass = time_data_klass.split(":")[0] + '\'' + ' ' + time_data_klass.split(":")[1] + '"'
                            else:
                                time_data_klass = time_data_klass.split(":")[0] + 'h ' + time_data_klass.split(":")[1] + '\'' + ' ' + time_data_klass.split(":")[2] + '"'
                        else:
                            if len(time_data_klass.split(":")) == 2:
                                time_data_klass = "+ " + time_data_klass.split(":")[0] + '\'' + ' ' + time_data_klass.split(":")[1] + '"'
                            else:
                                time_data_klass = "+ " + time_data_klass.split(":")[0] + 'h ' + time_data_klass.split(":")[1] + '\'' + ' ' + time_data_klass.split(":")[2] + '"' 
                        # print("test")
                        # Add to KLASSEMENT
                        tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["TIME"].insert(rank_klass-1,time_data_klass)
                        tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["RANK"].insert(rank_klass-1,str(rank_klass))
                        
                        rider_klass = rider_klass_i.split(" ")[-1] + " " + rider_klass_i.split(" ")[0]
                        tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["NAME"].insert(rank_klass-1,rider_klass)
                    except:
                        pass
            
            for rider_rit_i in riders_rit:
                
                # If rider already in results, go to next
                try:
                    rider_rit = rider_rit_i.split(" ")[-1] + " " + rider_rit_i.split(" ")[0]
                    if rider_rit in tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"]:
                        continue
                except:
                    # Team Time Trial probably
                    continue
                
                # Else, add data
                try:
                    rank = int(tdf_pcs[year][rider_rit_i]["RITUITSLAG"][count_year][0])
                    team = tdf_pcs[year][rider_rit_i]["RITUITSLAG"][count_year][1]
                    time_data = tdf_pcs[year][rider_rit_i]["RITUITSLAG"][count_year][2]
                    
                    # Adjust time to tdf time
                    if time_data == ",,":
                        if rank-2 != 0:
                            time_data = tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][rank-2]
                        else:
                            time_data = '+ 00\' 00"'
                    else:
                        if rank == 1:
                            if len(time_data.split(":")) == 2:
                                time_data = time_data.split(":")[0] + '\'' + ' ' + time_data.split(":")[1] + '"'
                            else:
                                time_data = time_data.split(":")[0] + 'h ' + time_data.split(":")[1] + '\'' + ' ' + time_data.split(":")[2] + '"'
                        else:
                            if len(time_data.split(":")) == 2:
                                time_data = "+ " + time_data.split(":")[0] + '\'' + ' ' + time_data.split(":")[1] + '"'
                            else:
                                time_data = "+ " + time_data.split(":")[0] + 'h ' + time_data.split(":")[1] + '\'' + ' ' + time_data.split(":")[2] + '"' 
                            
                except:
                    continue
                
                # Als DSQ renner als 1e geschrapt werd, check of 2e totaaltijd heeft of delta tijd
                # Voorlopig enkel als fout ontdekt bij rit 17 in 2006 (Landis vs Sastre)
                if rank == 1:
                    if "+" not in tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][0]:
                        tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"][0] = '+ 05\' 42"'
                        
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"].insert(rank-1,time_data)
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["RANK"].insert(rank-1,rank)
                
                rider_rit = rider_rit_i.split(" ")[-1] + " " + rider_rit_i.split(" ")[0]
                tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"].insert(rank-1,rider_rit)
                
                
                    
            
            count_year += 1

# Breidt keys uit
tdf["RITUITSLAG"] = [""]*len(tdf["DATE"])
tdf["KLASSEMENT"] = [""]*len(tdf["DATE"])
tdf["PUNTEN"] = [""]*len(tdf["DATE"])
tdf["BERGPRIJS"] = [""]*len(tdf["DATE"])
tdf["STRIJDLUST"] = [""]*len(tdf["DATE"])

for i in range(len(tdf["NAME"])):
    start = time.time()
    year = tdf["NAME"][i].split("Tour de France ")[1].split(" ")[0]
    # Rit
    if 'Individuel Temps Etape' in tdf["RESULT"][i]["RANKING"].keys():
        teams = []
        times = []
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"])):
            if tdf_participants[year] != "":
                try:
                    teams.append(tdf_participants[year][tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"][j]])
                except:
                    teams.append("")
            else:
                teams.append("")
                
        # Add time
        time_array = tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["TIME"]
        for j in range(len(time_array)):
            if time_array[j] == "withdrawls" or time_array[j] == "outside time limit" or time_array[j] == "non-race" or time_array[j] == "non-starter" or time_array[j] == "eliminated" or time_array[j] == "deceased":
                times.append(time_array[j])
                continue
            if time_array[j].split(" ")[0] != "+":
                if len(time_array[j].split(" ")) == 2:
                    minutes = int(time_array[j].split(" ")[0][:-1])
                    seconds = int(time_array[j].split(" ")[1][:-1])
                    times.append(60*minutes + seconds)
                else:
                    hours = int(time_array[j].split(" ")[0][:-1])
                    minutes = int(time_array[j].split(" ")[1][:-1])
                    seconds = int(time_array[j].split(" ")[2][:-1])
                    times.append(3600*hours + 60*minutes + seconds)
            else:
                if len(time_array[j].split(" ")) == 3:
                    minutes = int(time_array[j].split(" ")[1][:-1])
                    seconds = int(time_array[j].split(" ")[2][:-1])  
                    times.append(60*minutes + seconds)
                else:
                    hours = int(time_array[j].split(" ")[1][:-1])
                    minutes = int(time_array[j].split(" ")[2][:-1])
                    seconds = int(time_array[j].split(" ")[3][:-1])
                    times.append(3600*hours + 60*minutes + seconds) 
                    
        # tdf["RITUITSLAG"][i] = dict()
        # tdf["RITUITSLAG"][i]["NAME"] = tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"]
        # tdf["RITUITSLAG"][i]["TEAM"] = teams
        tdf["RITUITSLAG"][i] = [tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["NAME"], teams, times]

    # Geel
    if 'Individuel Temps Général' in tdf["RESULT"][i]["RANKING"].keys():
        teams = []
        times = []
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["NAME"])):
            if tdf_participants[year] != "":
                try:
                    teams.append(tdf_participants[year][tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["NAME"][j]])
                except:
                    teams.append("")
            else:
                teams.append("")
            
        # Add time
        time_array = tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["TIME"]
        for j in range(len(time_array)):
            if time_array[j] == "withdrawls" or time_array[j] == "outside time limit" or time_array[j] == "non-race"  or time_array[j] == "non-starter" or time_array[j] == "eliminated" or time_array[j] == "deceased":
                times.append(time_array[j])
                continue
            if time_array[j].split(" ")[0] != "+":
                if len(time_array[j].split(" ")) == 2:
                    minutes = int(time_array[j].split(" ")[0][:-1])
                    seconds = int(time_array[j].split(" ")[1][:-1])
                    times.append(60*minutes + seconds)
                else:
                    hours = int(time_array[j].split(" ")[0][:-1])
                    minutes = int(time_array[j].split(" ")[1][:-1])
                    seconds = int(time_array[j].split(" ")[2][:-1])
                    times.append(3600*hours + 60*minutes + seconds)
            else:
                if len(time_array[j].split(" ")) == 3:
                    minutes = int(time_array[j].split(" ")[1][:-1])
                    seconds = int(time_array[j].split(" ")[2][:-1])  
                    times.append(60*minutes + seconds)
                else:
                    hours = int(time_array[j].split(" ")[1][:-1])
                    minutes = int(time_array[j].split(" ")[2][:-1])
                    seconds = int(time_array[j].split(" ")[3][:-1])
                    times.append(3600*hours + 60*minutes + seconds)                        
        
        tdf["KLASSEMENT"][i] = [tdf["RESULT"][i]["RANKING"]['Individuel Temps Général']["NAME"], teams, times]
        
    # Bollen
    if 'Individuel Montagne Général' in tdf["RESULT"][i]["RANKING"].keys():
        teams = []
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Montagne Général']["NAME"])):
            if tdf_participants[year] != "":
                try:
                    teams.append(tdf_participants[year][tdf["RESULT"][i]["RANKING"]['Individuel Montagne Général']["NAME"][j]])
                except:
                    teams.append("")
            else:
                teams.append("")
        
        tdf["BERGPRIJS"][i] = [tdf["RESULT"][i]["RANKING"]['Individuel Montagne Général']["NAME"], teams]
        
    
    # Groen
    if 'Individuel Points Général' in tdf["RESULT"][i]["RANKING"].keys():
        teams = []
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Points Général']["NAME"])):
            if tdf_participants[year] != "":
                try:
                    teams.append(tdf_participants[year][tdf["RESULT"][i]["RANKING"]['Individuel Points Général']["NAME"][j]])
                except:
                    teams.append("")
            else:
                teams.append("")
        
        tdf["PUNTEN"][i] = [tdf["RESULT"][i]["RANKING"]['Individuel Points Général']["NAME"], teams]
        
    # Strijdlust
    if 'Individuel Combativité Général' in tdf["RESULT"][i]["RANKING"].keys():
        teams = []
        for j in range(len(tdf["RESULT"][i]["RANKING"]['Individuel Combativité Général']["NAME"])):
            if tdf_participants[year] != "":
                try:
                    teams.append(tdf_participants[year][tdf["RESULT"][i]["RANKING"]['Individuel Combativité Général']["NAME"][j]])
                except:
                    teams.append("")
            else:
                teams.append("")
        
        tdf["STRIJDLUST"][i] = [tdf["RESULT"][i]["RANKING"]['Individuel Combativité Général']["NAME"], teams]
    
    stop = time.time()
    if i%100 == 0:
        print(str(i+1) + " Ritten: " + str(round(stop-start)) + " || ETA: " + str(round((stop-start)*(len(tdf["NAME"]) - i))))
        
# # Only use last 1000 races
# for key in tdf.keys():
#     tdf[key] = tdf[key][1600:]
# Date adjust
for i in range(len(tdf["DATE"])):
    tdf["DATE"][i] = datetime.datetime.strptime(tdf["DATE"][i],"%d/%m/%Y")

# Add columns
# tdf["DATE_INDEX"] = [""]*len(tdf["DATE"])
# tdf["TERRAIN"] = [""]*len(tdf["DATE"])
# tdf["LENGTH"] = [""]*len(tdf["DATE"])
    
tdf = pd.DataFrame(tdf)
tdf.DATE = pd.to_datetime(tdf.DATE)
tdf = tdf.set_index("DATE")
tdf = tdf.sort_index()

# Now add wiki data (correct DATE, TERRAIN and LENGTH)
# Enkel naoorlogs

# test
test = []
years = list(range(1947,2016))
for year in years:
    count_wiki = 0
    for i in range(len(tdf_wiki["DATE"])):
        if tdf_wiki["DATE"][i][-4:] == str(year):
            count_wiki += 1
    test.append([len(tdf[(tdf.index > datetime.datetime(year,1,1)) & (tdf.index < datetime.datetime(year+1,1,1))]),count_wiki])
    
# tdf = tdf[tdf.index > datetime.datetime(1946,1,1)]
# tdf_wiki["DATE"] = tdf_wiki["DATE"][-len(tdf):]
# tdf_wiki["TERRAIN"] = tdf_wiki["TERRAIN"][-len(tdf):]
# tdf_wiki["LENGTH"] = tdf_wiki["LENGTH"][-len(tdf):]

# tdf_1974 = ["27 June 1974","28 June 1974","29 June 1974","30 June 1974", "01 July 1974","02 July 1974",\
#                     "03 July 1974","04 July 1974","05 July 1974","06 July 1974","07 July 1974","08 July 1974","09 July 1974",\
#                     "11 July 1974","12 July 1974","13 July 1974","14 July 1974","16 July 1974","17 July 1974",\
#                     "18 July 1974","19 July 1974","20 July 1974","21 July 1974","22 July 1974","23 July 1974",\
#                     "24 July 1974","25 July 1974"]

# tdf_1975 = ["26 June 1975","27 June 1975","28 June 1975","29 June 1975", "30 June 1975","01 July 1975",\
#                     "02 July 1975","03 July 1975","04 July 1975","05 July 1975","06 July 1975","07 July 1975","09 July 1975",\
#                     "10 July 1975","11 July 1975","12 July 1975","13 July 1975","15 July 1975","16 July 1975",\
#                     "17 July 1975","18 July 1975","19 July 1975","20 July 1975","21 July 1975","22 July 1975"]
                    
# tdf_2006 = tdf[(tdf.index > datetime.datetime(2006,1,1)) & (tdf.index < datetime.datetime(2007,1,1))].index

# count_1974 = 0
# count_1975 = 0
# count_2006 = 0
# for i in range(len(tdf_wiki["DATE"])):
#     if tdf_wiki["DATE"][i][-4:] == "1974":
#         tdf_wiki["DATE"][i] = tdf_1974[count_1974]
#         count_1974 += 1
#         tdf_wiki["DATE"][i] = datetime.datetime.strptime(tdf_wiki["DATE"][i],"%d %B %Y")
#     elif tdf_wiki["DATE"][i][-4:] == "1975":
#         tdf_wiki["DATE"][i] = tdf_1975[count_1975]
#         count_1975 += 1
#         tdf_wiki["DATE"][i] = datetime.datetime.strptime(tdf_wiki["DATE"][i],"%d %B %Y")
#     elif tdf_wiki["DATE"][i][-4:] == "2006":
#         tdf_wiki["DATE"][i] = datetime.datetime.fromtimestamp(tdf_2006[count_2006].value/1000000000)
#         count_2006 += 1
#     else:
#         tdf_wiki["DATE"][i] = datetime.datetime.strptime(tdf_wiki["DATE"][i],"%d %B %Y")
    
# # Sort tdf_wiki based on DATE
# tdf_wiki["DATE"], tdf_wiki["TERRAIN"], tdf_wiki["LENGTH"] = zip(*sorted(zip(tdf_wiki["DATE"], tdf_wiki["TERRAIN"], tdf_wiki["LENGTH"])))


# # # Add DATE, TERRAIN and LENGTH data
# for i in range(len(tdf)):
#     tdf.loc[(tdf.index == tdf.index[i]), "DATE_INDEX"] = tdf_wiki["DATE"][i]
#     tdf.loc[(tdf.index == tdf.index[i]), "TERRAIN"] = tdf_wiki["TERRAIN"][i]
#     tdf.loc[(tdf.index == tdf.index[i]), "LENGTH"] = tdf_wiki["LENGTH"][i]

# tdf.DATE_INDEX = pd.to_datetime(tdf.DATE_INDEX)
# tdf = tdf.set_index("DATE_INDEX")
# tdf = tdf.sort_index()

pickle.dump(tdf,open("app_tourdefrance/algorithm/results/tdf.p","wb"))
# tdf = tdf[tdf.index > datetime.datetime(1990,1,1)]