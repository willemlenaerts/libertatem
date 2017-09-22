# Make prediction % chance to win tour based on historical data

import pickle
import pandas as pd
import datetime
import time

# tdf file, keys: START/FINISH/DATE/RESULT/CAT/TYPE/NAME
# RESULT FURTHER SPLIT: 
tdf = pickle.load(open("app_tourdefrance/algorithm/data/tdf.p","rb"))

dsq_ritten = []
for i in range(len(tdf["DATE"])):
    try:
        aantal_renners = len(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["RANK"])
    except:
        continue
    
    dummy = list(reversed(tdf["RESULT"][i]["RANKING"]['Individuel Temps Etape']["RANK"]))
    for j in range(len(dummy)):
        try:
            ranking = int(dummy[j])
            break
        except:
            pass
    ranking = ranking + j
    if aantal_renners != ranking:
        dsq_ritten.append([i,tdf["DATE"][i],tdf["NAME"][i],ranking-aantal_renners])
        
dsq_renners = dict()
dsq_renners["Lance ARMSTRONG"] =dict()
dsq_renners["Lance ARMSTRONG"]["1999"] = dict()
dsq_renners["Lance ARMSTRONG"]["1999"]["RITUITSLAG"] = [1,42,28,24,70,70,116,66,1,1,5,31,19,36,60,4,11,51,31,1,86]