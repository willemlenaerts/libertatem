# This file transforms the scraped data from "tracking.dodentocht.be" 
# into inputs for the project on the Sway Blog
import json
import pickle
import datetime
tijd = pickle.load(open("app_dodentocht/algorithms/data/input/tijd.p","rb"))
snelheid = pickle.load(open("app_dodentocht/algorithms/data/input/snelheid.p","rb"))
posten = pickle.load(open("app_dodentocht/algorithms/data/input/posten.p","rb"))

####################################################################
# 1. posten
####################################################################
######################
# posts & km
######################
for key in posten.keys():
    posten[key] = float(posten[key].replace(",","."))

posts = list(posten.keys())
km = []
for post in posts:
    km.append(posten[post])

zipped = sorted(zip(km,posts))

km = [point[0] for point in zipped]
posts = [point[1] for point in zipped]

json.dump(posts,open("app_dodentocht/algorithms/data/results/posts.json","w"))
json.dump(km,open("app_dodentocht/algorithms/data/results/km.json","w"))

####################################################################
# 2. tijd & snelheid
####################################################################

# Pas namen aan
for i in range(len(tijd["Deelnemer"])):
    tijd["Deelnemer"][i] = tijd["Deelnemer"][i].replace("/","-")
    snelheid["Deelnemer"][i] = snelheid["Deelnemer"][i].replace("/","-")

    tijd["Deelnemer"][i] = tijd["Deelnemer"][i].replace("\\","")
    snelheid["Deelnemer"][i] = snelheid["Deelnemer"][i].replace("\\","")

    tijd["Deelnemer"][i] = tijd["Deelnemer"][i].replace("'","")
    snelheid["Deelnemer"][i] = snelheid["Deelnemer"][i].replace("'","")
    
    tijd["Deelnemer"][i] = tijd["Deelnemer"][i].replace("!","")
    snelheid["Deelnemer"][i] = snelheid["Deelnemer"][i].replace("!","")

    tijd["Deelnemer"][i] = tijd["Deelnemer"][i].replace("?","")
    snelheid["Deelnemer"][i] = snelheid["Deelnemer"][i].replace("?","")
    # Remove numbers
    for j in range(0,10):
        tijd["Deelnemer"][i] = tijd["Deelnemer"][i].replace(str(j),"")
        snelheid["Deelnemer"][i] = snelheid["Deelnemer"][i].replace(str(j),"")
    
    # Remove leading space
    snelheid["Deelnemer"][i] = snelheid["Deelnemer"][i].lstrip()  
    tijd["Deelnemer"][i] = tijd["Deelnemer"][i].lstrip()

    # Remove trailing space
    snelheid["Deelnemer"][i] = snelheid["Deelnemer"][i].rstrip()  
    tijd["Deelnemer"][i] = tijd["Deelnemer"][i].rstrip()
    
    # Remove double space
    snelheid["Deelnemer"][i] = snelheid["Deelnemer"][i].replace("  "," ")
    tijd["Deelnemer"][i] = tijd["Deelnemer"][i].replace("  "," ")
    
    # Hoofdletters
    snelheid["Deelnemer"][i] = snelheid["Deelnemer"][i].title()  
    tijd["Deelnemer"][i] = tijd["Deelnemer"][i].title()

# Make datetimes van tijd data
for i in range(len(tijd["Start"])):
    for j in range(len(posts)):
        if tijd[posts[j]][i] == "":
            continue
        hour = int(tijd[posts[j]][i].split(":")[0])
        minute = int(tijd[posts[j]][i].split(":")[1])
        if j == 0:
            day = 14
        elif j > 0 and j < 10:
            if hour < 21:
                day = 15
            else:
                day = 14
        else:
            day = 15
        tijd[posts[j]][i] = datetime.datetime(year = 2015, month = 8, day = day, hour = hour,minute = minute)
            
# Maak ranking gebaseerd op eindtijd
tijd["Totaal"] = list()
snelheid["Totaal_tijd"] = list()
for i in range(len(tijd["Aankomst"])):
    if tijd["Aankomst"][i] == "":
        tijd["Totaal"].append(150000000)
        snelheid["Totaal_tijd"].append(150000000)
    else:
        duur_s = tijd["Aankomst"][i]-tijd["Start"][i]
        tijd["Totaal"].append(duur_s.days*24 + duur_s.seconds/3600)
        snelheid["Totaal_tijd"].append(duur_s.days*24 + duur_s.seconds/3600)
        
import pandas as pd
tijd = pd.DataFrame(tijd)
tijd = tijd.set_index("Totaal")
tijd = tijd.sort_index()

snelheid = pd.DataFrame(snelheid)
snelheid = snelheid.set_index("Totaal_tijd")
snelheid = snelheid.sort_index()

tijd = tijd[(tijd.Deelnemer != "Null") & (tijd.Deelnemer != "null")]
snelheid = snelheid[(snelheid.Deelnemer != "Null") & (snelheid.Deelnemer != "null")]

# Verwijder iedereen die niet gestart is
tijd = tijd[tijd.Weert.notnull()]
snelheid = snelheid[snelheid.Weert.notnull()]

# Write to json files
######################
######################
# namen
######################
namen = list(tijd.Deelnemer)
json.dump(namen,open("app_dodentocht/algorithms/data/results/namen.json","w"))

######################
# opgaves & inrace
######################
opgaves = []
inrace = []
for i in range(len(posts)):
    inrace.append(len(tijd[tijd[posts[i]].notnull()]))
    if i == 0:
        dummy = 0
    else:
        dummy = len(tijd[tijd[posts[i-1]].isnull()])
    opgaves.append(len(tijd[tijd[posts[i]].isnull()])-dummy)

json.dump(opgaves,open("app_dodentocht/algorithms/data/results/opgaves.json","w"))
json.dump(inrace,open("app_dodentocht/algorithms/data/results/inrace.json","w"))

######################
# participants (totaal, en aantal aangekomen)
######################
participants = []
participants.append(inrace[0])
participants.append(inrace[-1])

json.dump(participants,open("app_dodentocht/algorithms/data/results/participants.json","w"))

#######################
# Gemiddelde
#######################
gemiddelde = dict()
# gemiddelde["time"] = []
gemiddelde["time_graph"] = [None]
gemiddelde["speed"] = [None]
for i in range(0,len(posts)-1):
    tijd_delta = tijd[tijd["Aankomst"].notnull()][posts[i+1]] - tijd[tijd["Aankomst"].notnull()][posts[i]]
    tijd_delta_gem = tijd_delta.astype(int).mean()
    gemiddelde["time_graph"].append(round(((tijd_delta_gem//10**9)/60))*60*10**9)
    
    df_snelheid = snelheid[(snelheid["Aankomst"] != "") & (snelheid[posts[i+1]] != "")][posts[i+1]]
    gemiddelde["speed"].append(round(df_snelheid.str.replace(',',".").astype(float).mean(),1))
    
# speed_total
df_snelheid = snelheid[snelheid["Aankomst"] != ""]["Totaal"]
gemiddelde["speed_total"] = round(df_snelheid.str.replace(',',".").astype(float).mean(),1)

# time_total
gem_time_total_hours = (sum(gemiddelde["time_graph"][1:])//10**9)/3600

# time_total
seconds = gem_time_total_hours*3600
hours = int(seconds //3600)
if len(str(hours)) < 2:
    hours_string = "0" + str(hours) + ":"
elif len(str(hours)) == 2:
    hours_string = str(hours) + ":"
else:
    hours_string = ""

minutes = int((seconds - hours*3600)/60)
if len(str(minutes)) < 2:
    minutes_string = "0" + str(minutes)
elif len(str(minutes)) == 2:
    minutes_string = str(minutes) 
else:
    minutes_string = ""   

if hours_string == "":
    minutes_string = ""   
    
gemiddelde["time_total"] =  hours_string + minutes_string


json.dump(gemiddelde,open("app_dodentocht/algorithms/data/results/gemiddelde.json","w"))

#######################
# Rest per NAAM
#######################
# Remove previous
import shutil
shutil.rmtree('app_dodentocht/algorithms/data/results/pernaam')

# Create directory
import os
if not os.path.exists('app_dodentocht/algorithms/data/results/pernaam'):
    os.makedirs('app_dodentocht/algorithms/data/results/pernaam')
    
for i in range(len(tijd)):
    pernaam = dict()
    pernaam["time"] = []
    pernaam["time_graph"] = []
    pernaam["speed"] = []
    for post in posts:
        if pd.notnull(tijd[post].iloc[i]):
            pernaam["time_graph"].append(tijd[post].iloc[i].strftime('%Y-%m-%dT%H:%M:%S'))
            pernaam["time"].append(tijd[post].iloc[i].strftime('%H:%M'))
        else:
            pernaam["time_graph"].append(None)
            pernaam["time"].append(None)
            
        if snelheid[post].iloc[i] == "":
            pernaam["speed"].append(0)
        else:
            pernaam["speed"].append(round(float(snelheid[post].iloc[i].replace(",",".")),1))
            
    pernaam["speed_total"] = round(float(snelheid["Totaal"].iloc[i].replace(",",".")),1)
    
    # time_total
    seconds = tijd.index[i]*3600
    hours = int(seconds //3600)
    if len(str(hours)) < 2:
        hours_string = "0" + str(hours) + ":"
    elif len(str(hours)) == 2:
        hours_string = str(hours) + ":"
    else:
        hours_string = ""
    
    minutes = int((seconds - hours*3600)/60)
    if len(str(minutes)) < 2:
        minutes_string = "0" + str(minutes)
    elif len(str(minutes)) == 2:
        minutes_string = str(minutes) 
    else:
        minutes_string = ""   
    
    if hours_string == "":
        minutes_string = ""   
        
    pernaam["time_total"] =  hours_string + minutes_string
     
    pernaam["name"] = tijd.Deelnemer.iloc[i]
    pernaam["position"] = i
    
    json.dump(pernaam,open("app_dodentocht/algorithms/data/results/pernaam/" + str(i) + ".json","w"))