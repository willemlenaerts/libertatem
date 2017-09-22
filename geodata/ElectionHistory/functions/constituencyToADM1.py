# Function that links ElectionData constituencies to topojson ADM1 regions
# This is done by an algorithm, manual correction is STILL necessary

def constituencyToADM1(ElectionData,topojson,CountryCode):
    import json
    import os
    import csv
    import pandas as pd 
    import numpy as np
    
    from geodata.ElectionHistory.functions.crossmatch_names import crossmatch_names
    
    # Crossmatching algorithm
    # Constituency names
    constituencies = sorted(list(set(ElectionData[ElectionData.Country == CountryCode].Constituency.dropna())))
    
    # ADM1 names
    adm1 = []
    for constituency in topojson["objects"]["geo_ADM1"]["geometries"]:
        if constituency["properties"]["c"] == CountryCode:
            if constituency["properties"]["n"] != None:
                adm1.append(constituency["properties"]["n"])
    
    crossmatches = crossmatch_names(constituencies,adm1)
    
    # Write To CSV
    keys_list = list(crossmatches.keys())
    values_list = []
    for key in keys_list:
        values_list.append(crossmatches[key])
        
    zipped = zip(values_list, keys_list)
    zipped = sorted(zipped)
    values, keys = zip(*zipped)    
    
    with open('geodata/ElectionHistory/input/CountryData/' + CountryCode + '/' + CountryCode + '_constituencies.csv', "w", newline='') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerow(["ADM1","Constituency"])
        for i in range(len(values)):
            a.writerow([values[i],keys[i]])
            
    conversion = pd.read_csv("geodata/ElectionHistory/input/CountryData/" + CountryCode + "/" + CountryCode + "_constituencies.csv")

    return conversion