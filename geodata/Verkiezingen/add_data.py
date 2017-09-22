# Add all sorts of data to topojson file to display in D3 map
import pandas as pd
import numpy as np
import pickle
import json
import math
import time
import ftplib
from geodata.Verkiezingen.crossmatch_names import crossmatch_names
from geodata.Verkiezingen.ordered_set import ordered_set
#################################
# HISTORISCHE VERKIEZINGSDATA
#################################
verkiezingen = pickle.load(open("geodata/Verkiezingen/input/verkiezingenBelgie.p","rb"))
bi = pd.read_csv('geodata/Verkiezingen/input/kieskantons_belgie.csv', header=0) # Bestuurlijke Indeling Belgie

kieskringen = sorted(list(set(verkiezingen[verkiezingen.Type == "Kieskring"].Plaats)))
arrondissementen = sorted(list(set(verkiezingen[verkiezingen.Type == "Arrondissement"].Plaats)))
kantons = sorted(list(set(verkiezingen[verkiezingen.Type == "Kanton"].Plaats)))

# crossmatch_names(kieskringen,list(set(bi.Kieskring)))

#################################
# TOPOJSON
#################################
GemeentenBelgieTopoJson = json.load(open("geodata/Verkiezingen/input/GemeentenBelgieTopoJson_backup.json","r"))
grootste_partij = []
gemeente_data = dict()
selectie = list(set(verkiezingen.Datum)) # ['13-06-2010','25-05-2014']
oostkantons = ['Amel#Amblève','Büllingen#Bullange','Bütgenbach#Butgenbach','Eupen','Kelmis#La Calamine','Lontzen','Burg-Reuland','Malmedy','Raeren','Sankt Vith#Saint-Vith','Waimes#Weismes']
       
# selectie = ["08-06-1880"]
# gemeente_check = "Merksplas"
count_s = 0
for s in selectie:
    print(s)
    start = time.time()
    
    # Het Rijk Data
    if "Het Rijk" not in list(gemeente_data.keys()):
        gemeente_data["Het Rijk"] = dict()
    
    gemeente_data["Het Rijk"][s] = dict()
    gemeente_data["Het Rijk"][s]["Partijen"] = []
    gemeente_data["Het Rijk"][s]["Procent"] = []
    gemeente_data["Het Rijk"][s]["Data"] = ""    
    
    dummy = verkiezingen[(verkiezingen.Datum == s) & (verkiezingen.Type == "Rijk")]
    if len(dummy) != 0:
        if (dummy.sort("Stemmen", ascending=False).Procent.iloc[0] != 0) & (dummy.sort("Stemmen", ascending=False).Procent.iloc[0] < 100):
            procent = dummy.sort("Stemmen", ascending=False).Procent.iloc[0]
            
            # Voeg dat toe aan gemeente_data
            gemeente_data["Het Rijk"][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
            gemeente_data["Het Rijk"][s]["Procent"] = np.round(dummy.sort("Stemmen", ascending=False).Procent.tolist(),2).tolist()
            gemeente_data["Het Rijk"][s]["Data"] += "Het Rijk"
            
            if math.isnan(procent):
                continue
        else:
            procent = 100*dummy.sort("Stemmen", ascending=False).Stemmen.iloc[0]/dummy.sort("Stemmen", ascending=False).Stemmen.sum()
            procent_list = 100*dummy.sort("Stemmen", ascending=False).Stemmen/dummy.sort("Stemmen", ascending=False).Stemmen.sum()
            
            # Voeg dat toe aan gemeente_data
            gemeente_data["Het Rijk"][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
            gemeente_data["Het Rijk"][s]["Procent"] = np.round(procent_list.tolist(),2).tolist()
            gemeente_data["Het Rijk"][s]["Data"] += "Het Rijk"     
    
    for gemeente in GemeentenBelgieTopoJson["objects"]["gemeenten"]["geometries"]:
        

        
        # Check naam gemeente in topojson
        gemeente_topo = gemeente["properties"]["naam"]
        
        # if gemeente_topo != gemeente_check:
        #     continue
        
        # Check of key reeds in gemeente_data dict zit
        if gemeente_topo not in list(gemeente_data.keys()):
            gemeente_data[gemeente_topo] = dict()
            
        gemeente_data[gemeente_topo][s] = dict()
        gemeente_data[gemeente_topo][s]["Partijen"] = []
        gemeente_data[gemeente_topo][s]["Procent"] = []
        gemeente_data[gemeente_topo][s]["Data"] = ""
            
        # Vindt equivalente naam in BI
        gemeente_bi = crossmatch_names([gemeente_topo],list(set(bi.Gemeente)))[gemeente_topo]

        # Fix Oostkantons
        if (gemeente_bi in oostkantons) and (int(s.split("-")[-1]) < 1920):
            gemeente["properties"][s] = ["None","None"] 
            continue
        # Vindt kantons waar gemeente_bi ooit toe behoord heeft
        # kantons_bi = list(set(bi[bi.Gemeente == gemeente_bi].Kanton))
        kantons_bi = ordered_set(bi[bi.Gemeente == gemeente_bi].Kanton)
        # Vindt equivalent kanton in Verkiezingen
        match = False
        for kanton_bi in kantons_bi:
            if kanton_bi == "none": 
                continue
            kanton = crossmatch_names([kanton_bi],list(set(verkiezingen[(verkiezingen.Type == "Kanton")].Plaats)))[kanton_bi]
            
            # Voeg data toe
            dummy = verkiezingen[(verkiezingen.Datum == s) & (verkiezingen.Type == "Kanton") & (verkiezingen.Plaats == kanton)]
            
            if len(dummy) != 0:
                # Eerst controleren of er Stemmen/Procent data is
                if dummy.Stemmen.sum() == 0 and dummy.Procent.sum() == 0:
                    continue
                
                partij = dummy.sort("Stemmen", ascending=False).Partij.iloc[0]
                if (dummy.sort("Stemmen", ascending=False).Procent.iloc[0] != 0) & (dummy.sort("Stemmen", ascending=False).Procent.iloc[0] < 100):
                    procent = dummy.sort("Stemmen", ascending=False).Procent.iloc[0]

                    if math.isnan(procent):
                        # Voeg dat toe aan gemeente_data
                        gemeente_data[gemeente_topo][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
                        gemeente_data[gemeente_topo][s]["Procent"] = len(dummy)*[0]
                        gemeente_data[gemeente_topo][s]["Data"] += "Kanton " + kanton
                        gemeente["properties"][s] = [partij,0]
                    else:
                        # Voeg dat toe aan gemeente_data
                        gemeente_data[gemeente_topo][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
                        gemeente_data[gemeente_topo][s]["Procent"] = np.round(dummy.sort("Stemmen", ascending=False).Procent.tolist(),2).tolist()
                        gemeente_data[gemeente_topo][s]["Data"] += "Kanton " + kanton
                        gemeente["properties"][s] = [partij,round(procent,2)]
                    
                else:
                    procent = 100*dummy.sort("Stemmen", ascending=False).Stemmen.iloc[0]/dummy.sort("Stemmen", ascending=False).Stemmen.sum()
                    procent_list = 100*dummy.sort("Stemmen", ascending=False).Stemmen/dummy.sort("Stemmen", ascending=False).Stemmen.sum()

                    if math.isnan(procent):
                        # Voeg dat toe aan gemeente_data
                        gemeente_data[gemeente_topo][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
                        gemeente_data[gemeente_topo][s]["Procent"] = len(dummy)*[0]
                        gemeente_data[gemeente_topo][s]["Data"] += "Kanton " + kanton
                        gemeente["properties"][s] = [partij,0]
                    else:
                        # Voeg dat toe aan gemeente_data
                        gemeente_data[gemeente_topo][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
                        gemeente_data[gemeente_topo][s]["Procent"] = np.round(procent_list.tolist(),2).tolist()
                        gemeente_data[gemeente_topo][s]["Data"] += "Kanton " + kanton
                        gemeente["properties"][s] = [partij,round(procent,2)] 
                    
                grootste_partij.append(dummy.sort("Stemmen", ascending=False).Partij.iloc[0])
                match = True
                

                break # Dit kanton volstaat
            # else:
            #     gemeente["properties"][s] = "None"
        
        if match == False: # Nog geen data gevonden
            # Vindt arrondissementen waar gemeente_bi ooit toe behoord heeft
            # arrondissementen_bi = list(set(bi[bi.Gemeente == gemeente_bi].Arrondissement))
            arrondissementen_bi = ordered_set(bi[bi.Gemeente == gemeente_bi].Arrondissement)
            for arrondissement_bi in arrondissementen_bi:
                arrondissement = crossmatch_names([arrondissement_bi],list(set(verkiezingen[(verkiezingen.Type == "Arrondissement")].Plaats)))[arrondissement_bi]
                
                dummy = verkiezingen[(verkiezingen.Datum == s) & (verkiezingen.Type == "Arrondissement") & (verkiezingen.Plaats == arrondissement)]
                if len(dummy) != 0:
                    # Eerst controleren of er Stemmen/Procent data is
                    if dummy.Stemmen.sum() == 0 and dummy.Procent.sum() == 0:
                        continue
                    
                    # Voeg data toe
                    partij = dummy.sort("Stemmen", ascending=False).Partij.iloc[0]
                    if (dummy.sort("Stemmen", ascending=False).Procent.iloc[0] != 0)  & (dummy.sort("Stemmen", ascending=False).Procent.iloc[0] < 100):
                        procent = dummy.sort("Stemmen", ascending=False).Procent.iloc[0]
                                            
                        if math.isnan(procent):
                            # Voeg dat toe aan gemeente_data
                            gemeente_data[gemeente_topo][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
                            gemeente_data[gemeente_topo][s]["Procent"] = len(dummy)*[0]
                            gemeente_data[gemeente_topo][s]["Data"] += "Arrondissement " + arrondissement 
                            gemeente["properties"][s] = [partij,0]
                        else:
                            # Voeg dat toe aan gemeente_data
                            gemeente_data[gemeente_topo][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
                            gemeente_data[gemeente_topo][s]["Procent"] = np.round(dummy.sort("Stemmen", ascending=False).Procent.tolist(),2).tolist()
                            gemeente_data[gemeente_topo][s]["Data"] += "Arrondissement " + arrondissement 
                            gemeente["properties"][s] = [partij,round(procent,2)]                           
                    else:
                        procent = 100*dummy.sort("Stemmen", ascending=False).Stemmen.iloc[0]/dummy.sort("Stemmen", ascending=False).Stemmen.sum()
                        procent_list = 100*dummy.sort("Stemmen", ascending=False).Stemmen/dummy.sort("Stemmen", ascending=False).Stemmen.sum()
                      
                        if math.isnan(procent):
                            # Voeg dat toe aan gemeente_data
                            gemeente_data[gemeente_topo][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
                            gemeente_data[gemeente_topo][s]["Procent"] = len(dummy)*[0]
                            gemeente_data[gemeente_topo][s]["Data"] += "Arrondissement " + arrondissement 
                            gemeente["properties"][s] = [partij,0]
                        else:
                            # Voeg dat toe aan gemeente_data
                            gemeente_data[gemeente_topo][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
                            gemeente_data[gemeente_topo][s]["Procent"] = np.round(procent_list.tolist(),2).tolist()
                            gemeente_data[gemeente_topo][s]["Data"] += "Arrondissement " + arrondissement 
                            gemeente["properties"][s] = [partij,round(procent,2)] 
                    
                    grootste_partij.append(dummy.sort("Stemmen", ascending=False).Partij.iloc[0])
                    match = True
                    break # Dit arrondissement volstaat
                
        if match == False: # Nog geen data gevonden
            # Vindt kieskringen waar gemeente_bi ooit toe behoord heeft
            # kieskringen_bi = list(set(bi[bi.Gemeente == gemeente_bi].Kieskring))
            kieskringen_bi = ordered_set(bi[bi.Gemeente == gemeente_bi].Kieskring)
            for kieskring_bi in kieskringen_bi:
                kieskring = crossmatch_names([kieskring_bi],list(set(verkiezingen[(verkiezingen.Type == "Kieskring")].Plaats)))[kieskring_bi]
            
                # Voeg data toe
                dummy = verkiezingen[(verkiezingen.Datum == s) & (verkiezingen.Type == "Kieskring") & (verkiezingen.Plaats == kieskring)]
                if len(dummy) != 0:
                    # Eerst controleren of er Stemmen/Procent data is
                    if dummy.Stemmen.sum() == 0 and dummy.Procent.sum() == 0:
                        continue      
                    
                    # Voeg data toe
                    partij = dummy.sort("Stemmen", ascending=False).Partij.iloc[0]
                    if (dummy.sort("Stemmen", ascending=False).Procent.iloc[0] != 0) & (dummy.sort("Stemmen", ascending=False).Procent.iloc[0] < 100):
                        procent = dummy.sort("Stemmen", ascending=False).Procent.iloc[0]

                        if math.isnan(procent):
                            # Voeg dat toe aan gemeente_data
                            gemeente_data[gemeente_topo][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
                            gemeente_data[gemeente_topo][s]["Procent"] = len(dummy)*[0]
                            gemeente_data[gemeente_topo][s]["Data"] += "Kieskring " + kieskring 
                            gemeente["properties"][s] = [partij,0]
                        else:
                            # Voeg dat toe aan gemeente_data
                            gemeente_data[gemeente_topo][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
                            gemeente_data[gemeente_topo][s]["Procent"] = np.round(dummy.sort("Stemmen", ascending=False).Procent.tolist(),2).tolist()
                            gemeente_data[gemeente_topo][s]["Data"] += "Kieskring " + kieskring
                            gemeente["properties"][s] = [partij,round(procent,2)]  
                            
                    else:
                        procent = 100*dummy.sort("Stemmen", ascending=False).Stemmen.iloc[0]/dummy.sort("Stemmen", ascending=False).Stemmen.sum()
                        procent_list = 100*dummy.sort("Stemmen", ascending=False).Stemmen/dummy.sort("Stemmen", ascending=False).Stemmen.sum()
                        
                        
                        if math.isnan(procent):
                            # Voeg dat toe aan gemeente_data
                            gemeente_data[gemeente_topo][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
                            gemeente_data[gemeente_topo][s]["Procent"] = len(dummy)*[0]
                            gemeente_data[gemeente_topo][s]["Data"] += "Kieskring " + kieskring
                            gemeente["properties"][s] = [partij,0]
                        else:
                            # Voeg dat toe aan gemeente_data
                            gemeente_data[gemeente_topo][s]["Partijen"] = dummy.sort("Stemmen", ascending=False).Partij.tolist()
                            gemeente_data[gemeente_topo][s]["Procent"] = np.round(procent_list.tolist(),2).tolist()
                            gemeente_data[gemeente_topo][s]["Data"] += "Kieskring " + kieskring
                            gemeente["properties"][s] = [partij,round(procent,2)] 
                            
                    grootste_partij.append(dummy.sort("Stemmen", ascending=False).Partij.iloc[0])
                    match = True
                    break # Dit arrondissement volstaat 
                
        if match == False:
            gemeente["properties"][s] = ["None","None"]
            
    stop = time.time()    
    count_s += 1
    print("Remaining Time: " + str(round((len(selectie)-count_s)*(stop-start)/60)) + " min")
    
# Maak lijst van gemeenten
lijst_gemeenten = []
for gemeente in GemeentenBelgieTopoJson["objects"]["gemeenten"]["geometries"]:
    lijst_gemeenten.append(gemeente["properties"]["naam"]) # .split("#")[0]
lijst_gemeenten = sorted(lijst_gemeenten)

# Maak gesorteerde lijst van verkiezingsdata
verkiezingsdata = selectie
dummy = []
for s in selectie:
    dummy.append(s.split("-")[-1] + "-" + s.split("-")[-2])
verkiezingsdata = [x for (y,x) in sorted(zip(dummy,verkiezingsdata))]    

for gemeente in GemeentenBelgieTopoJson["objects"]["gemeenten"]["geometries"]:
    if gemeente["properties"]["naam"] == "Wemmel":
        a = gemeente
        break


json.dump(sorted(lijst_gemeenten),open("geodata/Verkiezingen/output/lijst_gemeenten.json","w"))      
json.dump(verkiezingsdata,open("geodata/Verkiezingen/output/verkiezingsdata.json","w"))      
json.dump(GemeentenBelgieTopoJson,open("geodata/Verkiezingen/output/GemeentenBelgieTopoJson.json","w"))

for gemeente in gemeente_data.keys():
    if gemeente == "Het Rijk":
        # Uitgebrachte stemmen toevoegen
        for s in selectie:
            gemeente_data[gemeente][s]["Uitgebrachte Stemmen"] = str(verkiezingen[(verkiezingen.Datum == s) & (verkiezingen.Plaats == "Het Rijk")].Stemmen.sum().astype(int))
        
        json.dump(gemeente_data[gemeente],open("geodata/Verkiezingen/output/gemeente/" + "Rijk" + ".json","w"))      
        json.dump(gemeente_data[gemeente],open("geodata/Verkiezingen/output/" + "Rijk" + ".json","w"))      
    else:
        json.dump(gemeente_data[gemeente],open("geodata/Verkiezingen/output/gemeente/" + str(lijst_gemeenten.index(gemeente))  + ".json","w"))  
        

# Write to FTP site
session = ftplib.FTP('ftp.sway-blog.be','sway-blog.be','Will0870')
session.cwd('/www/data/verkiezingen-belgie')

# Open data as JSON buffered (only way ftplib works)
lijst_gemeenten_b = open("geodata/Verkiezingen/output/lijst_gemeenten.json","rb")  
session.storbinary('STOR lijst_gemeenten.json', lijst_gemeenten_b)     # send the file
verkiezingsdata_b = open("geodata/Verkiezingen/output/verkiezingsdata.json","rb")    
session.storbinary('STOR verkiezingsdata.json', verkiezingsdata_b) 
GemeentenBelgieTopoJson_b = open("geodata/Verkiezingen/output/GemeentenBelgieTopoJson.json","rb")      
session.storbinary('STOR GemeentenBelgieTopoJson.json', GemeentenBelgieTopoJson_b) 
Rijk_b = open("geodata/Verkiezingen/output/Rijk.json","rb")
session.storbinary('STOR Rijk.json', Rijk_b)

for gemeente in gemeente_data.keys():
    if gemeente == "Het Rijk":
        dummy = open("geodata/Verkiezingen/output/gemeente/Rijk.json","rb")  
        session.storbinary('STOR gemeenten/' + "Rijk" + '.json', dummy)
    else:
        dummy = open("geodata/Verkiezingen/output/gemeente/" + str(lijst_gemeenten.index(gemeente))  + ".json","rb")  
        session.storbinary('STOR gemeenten/' + str(lijst_gemeenten.index(gemeente)) + '.json', dummy)
    

session.quit()