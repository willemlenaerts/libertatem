# Scrape historical soccer game data
# Data from http://www.football-data.co.uk/

# Function scrapeFootballdatacouk(country,seasons)
# Inputs:
# - country (string of country name, e.g. 'Belgium')
# - seasons (list, seasons to scrape, e.g. ['2014-2015','2015-2016'])

# Output:
# - Pandas dataframe with a row per game and lots of columns with info about the game (results + betting quotes)
#   This will be saved in /data/working

def scrapeFootballdatacouk(country,seasons):
    # Packages
    import csv
    import requests
    import numpy as np
    import pandas as pd
    import datetime
    import pickle
    import os
    import datetime
    
    # URL's to contact
    urls =  {   "Belgium": "http://www.football-data.co.uk/mmz4281/[SEASON]/B1.csv",
                "England": "http://www.football-data.co.uk/mmz4281/[SEASON]/E0.csv",
                "Germany": "http://www.football-data.co.uk/mmz4281/[SEASON]/D1.csv",
                "Italy": "http://www.football-data.co.uk/mmz4281/[SEASON]/I1.csv",
                "Spain": "http://www.football-data.co.uk/mmz4281/[SEASON]/SP1.csv",
                "France": "http://www.football-data.co.uk/mmz4281/[SEASON]/F1.csv",
                "Netherlands": "http://www.football-data.co.uk/mmz4281/[SEASON]/N1.csv",
                "Portugal": "http://www.football-data.co.uk/mmz4281/[SEASON]/P1.csv",
                "Turkey": "http://www.football-data.co.uk/mmz4281/[SEASON]/T1.csv",
                "Greece": "http://www.football-data.co.uk/mmz4281/[SEASON]/G1.csv"
    }
    
    # Output
    if os.path.isfile("app_betting/data/working/games.p"):
        games = pickle.load(open("app_betting/data/working/games.p","rb"))
    else:
        games = pd.DataFrame()
    
    url = urls[country]
    for season in seasons:
        # Get season string in the correct Football-data.co.uk format ('2015-2016' ==> '1516')
        season = "".join([x[2:4] for x in season.split("-")])
        
        # Make URL, contact URL, and save as CSV in /data/input/footballdataukco
        url = urls[country].replace("[SEASON]",season)
        with requests.Session() as s:
            download = s.get(url)
        
        csvfile = list(csv.reader(download.content.decode('utf-8').splitlines(), delimiter=','))
        
        with open("app_betting/data/input/footballdataukco/games_" + country + "_" + season + ".csv", "w") as outputfile:
            mywriter = csv.writer(outputfile)
            for row in csvfile:
                mywriter.writerow(row)
    
        # Append to games dataframe
        games_to_add = pd.read_csv("app_betting/data/input/footballdataukco/games_" + country + "_" + season + ".csv", index_col=False)
        games_to_add.Date = pd.to_datetime(games_to_add.Date.str.strip(), format='%d/%m/%y')
        
        games = pd.concat([games,games_to_add])

    # Remove Unnamed columns
    games.drop(games.keys()[[i.find('Unnamed') > -1 for i in games.keys()]],axis=1,inplace=True)
    
    # Remove all nan rows
    games.dropna(how='all',inplace=True)

    # Save games
    pickle.dump(games,open("app_betting/data/working/games.p","wb"))
    
    print("Acquired Game Data for " + country )
    
    return games