# Add all sorts of data to topojson file to display in D3 map

#################################
# INKOMEN PER GEMEENTE IN BELGIE
#################################
import csv
import pandas as pd
import numpy as np

results = []
with open("geodata/GemeentenBelgie/data/InkomenBelgie.txt", newline='') as inputfile:
    for row in csv.reader(inputfile):
        results.append(row[0].split("|"))

inkomen = dict()
for i in range(len(results[0])):
    inkomen[results[0][i].replace("\ufeff","")] = list()

for i in range(len(results)-1):
    for j in range(len(results[i+1])):
        inkomen[results[0][j].replace("\ufeff","")].append(results[i+1][j].replace("\ufeff",""))
        
inkomen = pd.DataFrame(inkomen)

# Add column Inkomen/Capita
BelastbaarInkomen = inkomen.MS_TOT_NET_TAXABLE_INC.values
Inwoners = inkomen.MS_TOT_RESIDENTS.values
InkomenPerCapita = np.empty(len(inkomen)) * np.nan

for i in range(len(inkomen)):
    InkomenPerCapita[i] = float(BelastbaarInkomen[i])/int(Inwoners[i])
    
inkomen.loc[:,'InkomenPerCapita'] = pd.Series(InkomenPerCapita, index=inkomen.index)

#################################
#################################

import json
gemeenten_topo = json.load(open("geodata/GemeentenBelgie/gemeenten_topo.json","r"))

from geodata.GemeentenBelgie.crossmatch_names import crossmatch_names


years = list(set(inkomen.CD_YEAR))
gemiddeld_inkomen_per_capita_per_jaar = dict()
test = []
for year in years:
    gemiddeld_inkomen_per_capita_per_jaar[year] = (inkomen[inkomen.CD_YEAR == year].MS_TOT_NET_TAXABLE_INC.astype(float).sum()/inkomen[inkomen.CD_YEAR == year].MS_TOT_RESIDENTS.astype(int).sum())
gemeentenamen = list(set(inkomen.TX_MUNTY_DESCR_NL)) + list(set(inkomen.TX_MUNTY_DESCR_FR))
for gemeente in gemeenten_topo["objects"]["gemeenten_geo"]["geometries"]:
    # Check naam gemeente
    naam_gemeente = gemeente["properties"]["naam"]
    # if naam_gemeente != crossmatch_names([naam_gemeente],gemeentenamen)[naam_gemeente]:
    #     print(naam_gemeente + " : " + crossmatch_names([naam_gemeente],gemeentenamen)[naam_gemeente])
    
    naam_gemeente = crossmatch_names([naam_gemeente],gemeentenamen)[naam_gemeente]  

    # Zoek in pandas
    for year in years:
        gemeente["properties"]["inkomen_" + year] = float(inkomen[((inkomen.TX_MUNTY_DESCR_FR == naam_gemeente) | (inkomen.TX_MUNTY_DESCR_NL == naam_gemeente)) & (inkomen.CD_YEAR == year)].InkomenPerCapita)
        gemeente["properties"]["inkomen_" + year + "_rel"] = gemeente["properties"]["inkomen_" + year]/gemiddeld_inkomen_per_capita_per_jaar[year]
        test.append(gemeente["properties"]["inkomen_" + year + "_rel"])
json.dump(gemeenten_topo,open("geodata/GemeentenBelgie/gemeenten_topo.json","w"))