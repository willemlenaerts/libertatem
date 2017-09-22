# Divide geojson file into its features
import json
import pandas as pd

# geojson = json.load(open("geodata/ElectionHistory/input/MapData/NaturalEarthData/ADM1/geojson/geo_ADM1.json","r"))
geojson = json.load(open("geodata/ElectionHistory/input/MapData/NaturalEarthData/ADM0/geojson/geo_ADM0.json","r"))
CountryCodes = pd.read_csv("geodata/ElectionHistory/input/CountryData/CountryCodes.csv").iso.dropna().tolist()


for CountryCode in CountryCodes:
    print(CountryCode)
    geojson_country = {"type":geojson["type"],"features":[]}
    for feature in geojson["features"]:
        CountryCode_feature = feature["properties"]["ADM0_A3"]
        
        if CountryCode == CountryCode_feature:
            geojson_country["features"].append(feature)
            
    
    # Save
    # json.dump(geojson_country,open("geodata/ElectionHistory/input/MapData/NaturalEarthData/ADM1/geojson/country/geo_ADM1_" + CountryCode + ".json","w"))
    json.dump(geojson_country,open("geodata/ElectionHistory/input/MapData/NaturalEarthData/ADM0/geojson/country/geo_ADM0_" + CountryCode + ".json","w"))
