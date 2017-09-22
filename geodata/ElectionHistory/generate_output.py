# Import input files and generate output file for Sway Blog
import pandas as pd
import numpy as np
import pickle
import json
import math
import time
import csv
import os
from geodata.ElectionHistory.functions.prepareElectionData import prepareElectionData

# Parameters
admin_level = 1
per_country = True

# Get input data
ElectionData = prepareElectionData(admin_level)
CountryCodes = pd.read_csv("geodata/ElectionHistory/input/CountryData/CountryCodes.csv").iso.dropna().tolist()

if per_country:
    topojson = dict()
    for CountryCode in CountryCodes:
        filename = "geodata/ElectionHistory/input/MapData/NaturalEarthData/ADM" + str(admin_level) + "/topojson/country/topo_ADM" + str(admin_level) + "_" + CountryCode + ".json"
        if os.path.isfile(filename):
            topojson[CountryCode] = json.load(open(filename,"r"))
else:
    topojson = json.load(open("geodata/ElectionHistory/input/MapData/NaturalEarthData/ADM" + str(admin_level) + "/topojson/topo_ADM" + str(admin_level) +".json","r"))
# geojson = json.load(open("geodata/ElectionHistory/input/MapData/geo_ADM" + str(admin_level) +".json","r"))
ElectionDates = dict()
for CountryCode in CountryCodes:
    ElectionDates[CountryCode] = sorted(list(set(ElectionData[ElectionData.Country == CountryCode].Date)))
    
# Create output
top_parties = dict()
constituencies = dict()
for CountryCode in CountryCodes:
    top_parties[CountryCode] = list()
    constituencies[CountryCode] = list()
    
count = 0
if per_country:
    print("Start generating output")
    
    # constituency_index = dict()
    # for i in range(len(topojson[CountryCode]["objects"]["geo_ADM" + str(admin_level) + "_" + CountryCode]["geometries"])):
    #     constituency_index[topojson[CountryCode]["objects"]["geo_ADM" + str(admin_level) + "_" + CountryCode]["geometries"][i]["properties"]["n"]] = i
    
    
    for CountryCode in CountryCodes:
        if CountryCode not in topojson.keys():
            print("WARNING: Country " + CountryCode + " not displayed on map")
            continue
        if "geometries" not in topojson[CountryCode]["objects"]["geo_ADM" + str(admin_level) + "_" + CountryCode].keys():
            print("WARNING: Country " + CountryCode + " does not have geometry")
            continue        
        print(CountryCode)
        
        for constituency in topojson[CountryCode]["objects"]["geo_ADM" + str(admin_level) + "_" + CountryCode]["geometries"]:
            # Timing
            start = time.time()

            # Get data from constituency
            if admin_level == 0:
                country_code = constituency["properties"]["c"]
                if country_code not in CountryCodes: # Not a country
                    continue
                constituencies[CountryCode].append(country_code)
            elif admin_level == 1:
                country_code = constituency["properties"]["c"]
                if country_code not in CountryCodes: # Not a country
                    continue
                constituency_name = constituency["properties"]["n"]
                constituencies[CountryCode].append(constituency_name)    
                
            # Add data to constituency
            for date in ElectionDates[country_code]:
                # Data to output
                if  admin_level == 0:
                    output_data = ElectionData[(ElectionData.Country == country_code) & (ElectionData.Date == date)].sort("Votes", ascending=False)
                elif admin_level == 1:
                    output_data = ElectionData[(ElectionData.Country == country_code) & (ElectionData.Constituency == constituency_name) & (ElectionData.Date == date)].sort("Votes", ascending=False)
                
                if len(output_data) == 0:
                    constituency["properties"][date] = ["None","None"]
                    continue
                
                if admin_level == 0:
                    top_party = output_data.Party.iloc[0]
                    top_share = output_data.Share_country.iloc[0]
                elif admin_level == 1:
                    top_party = output_data.Party.iloc[0]
                    top_share = output_data.Share_constituency.iloc[0]
                
                if pd.isnull(top_party):
                    top_party = "None"
                if pd.isnull(top_share):
                    top_share = "None"
                
                constituency["properties"][date] = [top_party,top_share]
                top_parties[country_code].append(top_party)
else:
    for constituency in topojson["objects"]["geo_ADM" + str(admin_level)]["geometries"]:
        # Timing
        start = time.time()
        if count == 0:
            print("Start generating output")
        
        # Get data from constituency
        if admin_level == 0:
            country_code = constituency["properties"]["c"]
            if country_code not in CountryCodes: # Not a country
                continue
            constituencies[CountryCode].append(country_code)
        elif admin_level == 1:
            country_code = constituency["properties"]["c"]
            if country_code not in CountryCodes: # Not a country
                continue
            constituency_name = constituency["properties"]["n"]
            constituencies[CountryCode].append(constituency_name)    
            
        # Add data to constituency
        for date in ElectionDates[country_code]:
            # Data to output
            if  admin_level == 0:
                output_data = ElectionData[(ElectionData.Country == country_code) & (ElectionData.Date == date)].sort("Votes", ascending=False)
            elif admin_level == 1:
                output_data = ElectionData[(ElectionData.Country == country_code) & (ElectionData.Constituency == constituency_name) & (ElectionData.Date == date)].sort("Votes", ascending=False)
            
            if len(output_data) == 0:
                constituency["properties"][date] = ["None","None"]
                continue
            
            top_party = output_data.Party.iloc[0]
            top_share = output_data.Share_constituency.iloc[0]
            
            if pd.isnull(top_party):
                top_party = "None"
            if pd.isnull(top_share):
                top_share = "None"
            
            constituency["properties"][date] = [top_party,top_share]
            top_parties[country_code].append(top_party)
    
    # Timing
    count += 1
    if count%25 == 0:
        stop = time.time()
        print("Constituency " + str(count) + " of " + str(len(topojson["objects"]["geo_ADM" + str(admin_level)]["geometries"])) + " || " + "ET: " + str(round((stop-start)*(len(topojson["objects"]["geo_ADM" + str(admin_level)]["geometries"])-count),0)) + "s")
    elif count == len(topojson["objects"]["geo_ADM" + str(admin_level)]["geometries"]):
        print("Algorithm finished")

# Check Party Data
for CountryCode in top_parties.keys():
    if pd.isnull(CountryCode):
        continue
    directory = "geodata/ElectionHistory/input/CountryData/" + CountryCode + "/"
    if not os.path.exists(directory):
        continue
    
    top_parties[CountryCode] = sorted(list(set(top_parties[CountryCode])))
    
    filename = directory + CountryCode + "_parties.csv"
    if os.path.isfile(filename):
        # Check of er nieuwe partijen zijn
        parties = pd.read_csv(filename)
        new_parties = list(set(top_parties[CountryCode])-set(parties.name.tolist()))
        if len(new_parties) != 0:
            name = parties.name.tolist() + new_parties
            ideology = parties.ideology.tolist() + [""]*len(new_parties)
            
            # Rewrite csv file
            with open(filename, "w", newline='') as fp:
                a = csv.writer(fp, delimiter=',')
                a.writerow(["name","ideology"])
                for i in range(len(name)):
                    a.writerow([name[i],ideology[i]])                
    else:
        # Creeer file
        with open(filename, "w", newline='') as fp:
            a = csv.writer(fp, delimiter=',')
            a.writerow(["name","ideology"])
            for i in range(len(top_parties[CountryCode])):
                a.writerow([top_parties[CountryCode][i],""])         
        

# Generate colors & dates per Country
PartyColorCodes = pd.read_csv("geodata/ElectionHistory/input/CountryData/PartyColorCodes.csv")
party_colors = dict()
election_dates = dict()
for CountryCode in CountryCodes:
    if pd.isnull(CountryCode):
        continue
    directory = "geodata/ElectionHistory/input/CountryData/" + CountryCode + "/"
    if not os.path.exists(directory):
        continue
    # Colors
    PartyCountryColorCodes = pd.read_csv("geodata/ElectionHistory/input/CountryData/" + CountryCode + "/" + CountryCode + "_parties.csv",dtype={"name":np.object,"ideology":np.object})
    party_colors[CountryCode] = dict()
    for party in top_parties[CountryCode]:
        color_series = PartyColorCodes[PartyColorCodes.ideology == PartyCountryColorCodes[PartyCountryColorCodes.name == party].ideology.iloc[0]].color
        if len(color_series) == 0:
            print(CountryCode + " || " + party)
            # party_colors[CountryCode][party] = "rgb(0,0,0)"
        else:
            party_colors[CountryCode][party] = color_series.iloc[0]
    
    # Dates
    election_dates[CountryCode] = sorted(set(ElectionData[ElectionData.Country == CountryCode].Date.tolist()))

# Write output
for CountryCode in CountryCodes:
    constituencies[CountryCode] = [x for x in constituencies[CountryCode] if x is not None]
    constituencies[CountryCode] = sorted(constituencies[CountryCode])
json.dump(constituencies,open("geodata/ElectionHistory/output/ADM" + str(admin_level) + "/constituencies.json","w"))
json.dump(party_colors,open("geodata/ElectionHistory/output/ADM" + str(admin_level) + "/party_colors.json","w"))
json.dump(election_dates,open("geodata/ElectionHistory/output/ADM" + str(admin_level) + "/election_dates.json","w"))

if per_country:
    # Generate countries data
    countries_list = sorted(list(set(ElectionData.Country)))
    for CountryCode in countries_list:
        print(CountryCode)
        # check if directory exists, otherwise make it
        directory = "geodata/ElectionHistory/output/ADM" + str(admin_level) + "/country/" + CountryCode + "/"
        if not os.path.exists(directory):
            os.makedirs(directory)
            os.makedirs(directory + "constituency/")
        
        # Topojson file
        json.dump(topojson[CountryCode],open(directory + "topo_ADM" + str(admin_level) + "_" + CountryCode + ".json","w"))

        
        # Country Data
        dummy = dict()
        for date in election_dates[CountryCode]:
            ElectionData_slice = ElectionData[(ElectionData.Country == CountryCode) & (ElectionData.Date == date)].groupby(["Country","Date","Party"],as_index=False).sum().sort("Share_country",ascending=False)
                
            dummy[date] = dict()
            dummy[date]["Parties"] = ElectionData_slice.Party.tolist()
            dummy[date]["Percent"] = ElectionData_slice.Share_country.tolist()
            dummy[date]["Total Votes"] = ElectionData_slice.Votes.sum()
            
            # Write to output
            json.dump(dummy,open(directory + CountryCode + ".json","w"))
        
        # Constituency data
        for constituency in constituencies[CountryCode]:
            dummy = dict()
            for date in election_dates[CountryCode]:
                dummy[date] = dict()
                ElectionData_slice = ElectionData[(ElectionData.Country == CountryCode) & (ElectionData.Date == date) & (ElectionData.Constituency == constituency)].sort("Share_constituency",ascending=False)
                dummy[date]["Parties"] = ElectionData_slice.Party.tolist()
                dummy[date]["Percent"] = ElectionData_slice.Share_constituency.tolist()
                dummy[date]["Total Votes"] = ElectionData_slice.Votes.sum()
    
            # Write to output
            json.dump(dummy,open(directory + "constituency/" +  str(constituencies[CountryCode].index(constituency)) + ".json","w"))





else:
    json.dump(topojson,open("geodata/ElectionHistory/output/ADM" + str(admin_level) + "/topo.json","w"))
    
# Write ISO3 to Country name dict
country_name_dict = dict()
CountryCodes_data = pd.read_csv("geodata/ElectionHistory/input/CountryData/CountryCodes.csv")

for i in range(len(CountryCodes_data)):
    if pd.notnull(CountryCodes_data.iso.iloc[i]) and pd.notnull(CountryCodes_data.iso.iloc[i]):
        if pd.notnull(CountryCodes_data.name_alt.iloc[i]):
            country_name_dict[CountryCodes_data.iso.iloc[i]] = CountryCodes_data.name_alt.iloc[i]
        else:
            country_name_dict[CountryCodes_data.iso.iloc[i]] = CountryCodes_data.name.iloc[i]

json.dump(country_name_dict,open("geodata/ElectionHistory/output/ADM" + str(admin_level) + "/country_iso_to_name.json","w"))