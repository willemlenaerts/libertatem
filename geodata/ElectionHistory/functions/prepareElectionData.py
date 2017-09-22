# function that cleans input ElectionData
# Input: admin_level (= 0 or 1)

def prepareElectionData(admin_level):
    import pandas as pd
    import numpy as np
    import json
    import os
    from geodata.ElectionHistory.functions.constituencyToADM1 import constituencyToADM1
    
    # Print
    print("Fetching and Cleaning data")
    
    # Import input file
    dtype = {
        "Country": np.object,
        "Year":np.float64,
        "Month":np.float64,
        "SubNational":np.object,
        "Constituency":np.object,
        "Magnitude":np.float64,
        "Party":np.object,
        "Turnout":np.object, #np.float64
        "Votes":np.float64,
        "Share":np.float64
        }
    
    # Get ElectionData
    ElectionData = pd.DataFrame()
    regions = ["WesternEurope","EasternEurope","NorthAmerica","LatinAmerica","Africa","Asia","Oceania","Carribean"] # ,
    for region in regions:
        ElectionData = pd.concat([ElectionData,pd.read_csv("geodata/ElectionHistory/input/ElectionData/Elections" + region + ".csv",sep=";",dtype=dtype)])
        ElectionData["Turnout"].convert_objects(convert_numeric='force')
    
    CountryCodes = pd.read_csv("geodata/ElectionHistory/input/CountryData/CountryCodes.csv")
    topojson = json.load(open("geodata/ElectionHistory/input/MapData/NaturalEarthData/ADM" + str(admin_level) + "/topojson/topo_ADM" + str(admin_level) +".json","r"))
    
    # Soms probleem met eerste kolom bij lezen door read_csv
    col_name = ElectionData.columns[0]
    ElectionData = ElectionData.rename(columns = {"Country":'Country','\ufeffCountry':'Country'})
    
    # Clean Input CSV stuff
    # Countries
    # ElectionData.Country = ElectionData.Country.apply(lambda x: x.split('Western Europe')[1].lstrip().rstrip() if len(x.split('Western Europe'))>1 else x)
    CountryCodes = pd.read_csv("geodata/ElectionHistory/input/CountryData/CountryCodes.csv")
    d = dict()
    for i in range(len(CountryCodes)):
        if pd.isnull(CountryCodes.iso.iloc[i]):
            # Not a recognized country with an ISO code (Kosovo and Somaliland)
            d[CountryCodes.name.iloc[i]] = "None"
        else:
            d[CountryCodes.name.iloc[i]] = CountryCodes.iso.iloc[i]
            if not pd.isnull(CountryCodes.name_alt.iloc[i]):
                d[CountryCodes.name_alt.iloc[i]] = CountryCodes.iso.iloc[i]
        
    ElectionData.Country = ElectionData.Country.apply(lambda x: d[x.lstrip().rstrip()])
    ElectionData = ElectionData[ElectionData.Country != "None"] # This removes Kosovo and Somaliland Data (appr. 1800 rows)
    
    ############################################################################
    # Clean up the columns
    # Constituency
    ElectionData.SubNational = ElectionData.SubNational.apply(lambda x: x.lstrip().rstrip() if not pd.isnull(x) else x)
    ElectionData.Constituency = ElectionData.Constituency.apply(lambda x: x.lstrip().rstrip() if not pd.isnull(x) else x)
    
    # Year
    ElectionData.Year = ElectionData.Year.apply(lambda x: float(str(int(x))[-4:]))
    
    # Month
    ElectionData.Month = ElectionData.Month.apply(lambda x: np.nan if x == 990 else x)
    
    # Create date
    year = ElectionData.Year.values
    month = ElectionData.Month.values
    date = np.empty(len(ElectionData), dtype=object)
    
    for i in range(len(ElectionData)):
        try:
            date[i] = str(int(year[i])) + "-" + str(int(month[i]))
        except:
            try:
                date[i] = str(int(year[i])) + "-0"
            except:
                pass
    
    ElectionData.loc[:,'Date'] = pd.Series(date, index=ElectionData.index)
    del ElectionData['Year']
    del ElectionData['Month']
    
    # Drop where there are no votes
    ElectionData = ElectionData[~pd.isnull(ElectionData.Votes)].reset_index(drop=True)
    
    # Reset index
    ElectionData = ElectionData.reset_index(drop=True)
    ################################################################################
    # 1. Constituencies ElectionData to topojson ADM1
    if admin_level == 1:
        ElectionDataCountries = sorted(list(set(ElectionData.Country)))
        for CountryCode in ElectionDataCountries:
            directory = "geodata/ElectionHistory/input/CountryData/" + CountryCode + "/"
            if not os.path.exists(directory):
                os.makedirs(directory)
                
            # Import conversion data
            filename = directory + CountryCode + "_constituencies.csv"
            if os.path.isfile(filename):
                # Load file
                conversion = pd.read_csv("geodata/ElectionHistory/input/CountryData/" + CountryCode + "/" + CountryCode + "_constituencies.csv")
            else:
                # Create file
                conversion = constituencyToADM1(ElectionData,topojson,CountryCode)
            
            # Convert
            d = dict()
            for i in range(len(conversion)):
                d[conversion.Constituency.iloc[i]] = conversion.ADM1.iloc[i]
            
            ElectionData.loc[ElectionData[ElectionData.Country == CountryCode].Constituency.index,"Constituency"] = ElectionData[ElectionData.Country == CountryCode].Constituency.apply(lambda x: d[x] if x in d.keys() else np.nan)
        
        # Drop where Constituency = nan
        ElectionData = ElectionData[~pd.isnull(ElectionData.Constituency)].reset_index(drop=True)
    ################################################################################
    # 2. GroupBy 
    # Make extra column= weighted percentage 
        
    # First, get votes per admin_level (in this case countries)
    dummyElectionData = ElectionData.groupby(["Country","Date"],as_index=False).sum()
    dummycountries = sorted(list(set(dummyElectionData.Country)))
    dummy = dict()
    for dummycountry in dummycountries:
        dummy[dummycountry] = dict()
        dummydates = list(set(dummyElectionData[dummyElectionData.Country == dummycountry].Date))
        for dummydate in dummydates:
            dummy[dummycountry][dummydate] = ""
                
    country = dummyElectionData.Country.values
    date = dummyElectionData.Date.values
    votes = dummyElectionData.Votes.values
    
    for i in range(len(country)):        
        dummy[country[i]][date[i]] = votes[i]
        
    
    # Now calculate weighted share (so that it sums for every country/date combination to 100%)
    votes = ElectionData.Votes.values
    country = ElectionData.Country.values
    date = ElectionData.Date.values
    
    # Outputs
    weighted_share_country = np.empty(len(ElectionData), dtype=np.float64)
    for i in range(len(votes)):
        weighted_share_country[i] = votes[i]/dummy[country[i]][date[i]]
        
    # First, get votes per admin_level (in this case constituencies)
    dummyElectionData = ElectionData.groupby(["Country","Date","Constituency"],as_index=False).sum()
    dummycountries = sorted(list(set(dummyElectionData.Country)))
    dummy = dict()
    for dummycountry in dummycountries:
        dummy[dummycountry] = dict()
        dummydates = list(set(dummyElectionData[dummyElectionData.Country == dummycountry].Date))
        for dummydate in dummydates:
            dummy[dummycountry][dummydate] = dict()
            dummyconstituencies = list(set(dummyElectionData[(dummyElectionData.Country == dummycountry) & (dummyElectionData.Date == dummydate)].Constituency))
            for dummyconstituency in dummyconstituencies:
                dummy[dummycountry][dummydate][dummyconstituency] = ""
                
    country = dummyElectionData.Country.values
    constituency = dummyElectionData.Constituency.values
    date = dummyElectionData.Date.values
    votes = dummyElectionData.Votes.values
    
    for i in range(len(country)):  
        dummy[country[i]][date[i]][constituency[i]] = votes[i]        
    
    # Now calculate weighted share (so that it sums for every country/date/constituency combination to 100%)
    votes = ElectionData.Votes.values
    country = ElectionData.Country.values
    constituency = ElectionData.Constituency.values
    date = ElectionData.Date.values
    
    # Outputs
    weighted_share_constituency = np.empty(len(ElectionData), dtype=np.float64)
    for i in range(len(votes)):
        weighted_share_constituency[i] = votes[i]/dummy[country[i]][date[i]][constituency[i]]
    
    # Change Share Column
    ElectionData.loc[:,"Share_country"] = pd.Series(weighted_share_country,index=ElectionData.index)
    ElectionData.loc[:,"Share_constituency"] = pd.Series(weighted_share_constituency,index=ElectionData.index)
    
    # GroupBy
    if admin_level == 1:
        ElectionData = ElectionData.groupby(["Country","Date","Constituency","Party"],as_index=False).sum()
    elif admin_level == 0:
        ElectionData = ElectionData.groupby(["Country","Date","Party"],as_index=False).sum() # "Constituency"

    return ElectionData
    