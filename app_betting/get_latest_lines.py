# Get odds from lines.bookmaker.eu
# Return pandas
def get_latest_lines():
    import urllib.request
    import pandas as pd
    import xml.etree.ElementTree as ET
    from app_betting.convert_odds import moneyline_to_decimal
    import datetime
    
    # Get Lines from XML file
    url = "http://lines.bookmaker.eu/"
    s = urllib.request.urlopen(url)
    contents = s.read()
    file = open("app_betting/data/lines.xml", 'wb')
    file.write(contents)
    file.close()
    
    # Convert XML file to Pandas of games
    tree = ET.parse("app_betting/data/lines.xml")
    root = tree.getroot()
    
    output = dict()
    output["Competition"] = []
    output["Date"] = []
    output["HomeTeam"] = []
    output["AwayTeam"] = []
    output["HomeWinLine"] = []
    output["AwayWinLine"] = []
    output["TieLine"] = []
    
    competitions = ["TURKEY - SUPER LIG","ENGLAND - PREMIER LEAGUE",'FRANCE - LIGUE 1','GERMANY - BUNDESLIGA','HOLLAND - EREDIVISIE','ITALY - SERIE A','SPAIN - LA LIGA',"UEFA - CHAMPIONS LEAGUE","UEFA - EUROPA LEAGUE","BELGIUM - JUPILER LEAGUE","PORTUGAL - 1 LIGA"]
    
    for competition in competitions:
        for league in root.iter('league'):
            if league.attrib["Description"] == competition:
                for game in league.iter('game'):
                    if game.attrib["vtm"].split(" ")[0] != "1H": # Only full game bets, not first half
                        output["Competition"].append(competition)
                        output["HomeTeam"].append(game.attrib["htm"])
                        output["AwayTeam"].append(game.attrib["vtm"])
                        date_string = game.attrib["gmdt"] + " " + game.attrib["gmtm"]
                        output["Date"].append(datetime.datetime.strptime(date_string, '%Y%m%d %H:%M:%S') + datetime.timedelta(hours=8))
                        for line in game.iter('line'):
                            if line.attrib["hoddst"] == "":
                                output["HomeWinLine"].append(0.0)
                            else:
                                output["HomeWinLine"].append(moneyline_to_decimal(line.attrib["hoddst"]))
                            if line.attrib["voddst"] == "":
                                output["AwayWinLine"].append(0.0)
                            else:
                                output["AwayWinLine"].append(moneyline_to_decimal(line.attrib["voddst"]))
                            if line.attrib["vsph"] == "":
                                output["TieLine"].append(0.0)
                            else:
                                output["TieLine"].append(moneyline_to_decimal(line.attrib["vsph"])) 
    
    # Convert Team Names
    for i in range(len(output["HomeTeam"])):
        if output["HomeTeam"][i] == "BETIS SEVILLA":
            output["HomeTeam"][i] = "BETIS"
        if output["AwayTeam"][i] == "BETIS SEVILLA":
            output["AwayTeam"][i] = "BETIS"
            
        if output["HomeTeam"][i] == 'ISTANBUL BASAKSEHIR FK':
            output["HomeTeam"][i] = "BUYUKSEHYR"
        if output["AwayTeam"][i] == 'ISTANBUL BASAKSEHIR FK':
            output["AwayTeam"][i] = "BUYUKSEHYR"  
            
        if output["HomeTeam"][i] == 'RCD ESPANYOL BARCELONA':
            output["HomeTeam"][i] = "ESPANOL"
        if output["AwayTeam"][i] == 'RCD ESPANYOL BARCELONA':
            output["AwayTeam"][i] = "ESPANOL"
    
        if output["HomeTeam"][i] == "MANCHESTER CITY":
            output["HomeTeam"][i] = "MAN CITY"
        if output["AwayTeam"][i] == "MANCHESTER CITY":
            output["AwayTeam"][i] = "MAN CITY"
    
        if output["HomeTeam"][i] == "MANCHESTER UTD":
            output["HomeTeam"][i] = "MAN UNITED"
        if output["AwayTeam"][i] == "MANCHESTER UTD":
            output["AwayTeam"][i] = "MAN UNITED"
            
        if output["HomeTeam"][i] == "BOAVISTA PORTO":
            output["HomeTeam"][i] = "BOAVISTA"
        if output["AwayTeam"][i] == "BOAVISTA PORTO":
            output["AwayTeam"][i] = "BOAVISTA"
    
        if output["HomeTeam"][i] == "SPORTING BRAGA":
            output["HomeTeam"][i] = "SP BRAGA"
        if output["AwayTeam"][i] == "SPORTING BRAGA":
            output["AwayTeam"][i] = "SP BRAGA"
    
        if output["HomeTeam"][i] == "SPORTING GIJON":
            output["HomeTeam"][i] = "SP GIJON"
        if output["AwayTeam"][i] == "SPORTING GIJON":
            output["AwayTeam"][i] = "SP GIJON"
    
        if output["HomeTeam"][i] == "SPORTING CP":
            output["HomeTeam"][i] = "SP LISBON"
        if output["AwayTeam"][i] == "SPORTING CP":
            output["AwayTeam"][i] = "SP LISBON"
            
        if output["HomeTeam"][i] == 'SS LAZIO ROMA':
            output["HomeTeam"][i] = "LAZIO"
        if output["AwayTeam"][i] == 'SS LAZIO ROMA':
            output["AwayTeam"][i] = "LAZIO"
            
        if output["HomeTeam"][i] == "ATL MADRID":
            output["HomeTeam"][i] = "ATH MADRID"
        if output["AwayTeam"][i] == "ATL MADRID":
            output["AwayTeam"][i] = "ATH MADRID"
    
        if output["HomeTeam"][i] == "1. FC COLOGNE":
            output["HomeTeam"][i] = "FC KOLN"
        if output["AwayTeam"][i] == "1. FC COLOGNE":
            output["AwayTeam"][i] = "FC KOLN"
    
        if output["HomeTeam"][i] == "DEP LA CORUNA":
            output["HomeTeam"][i] = "DEPORTIVO LA CORUNA"
        if output["AwayTeam"][i] == "DEP LA CORUNA":
            output["AwayTeam"][i] = "DEPORTIVO LA CORUNA"
    
        if output["HomeTeam"][i] == "AC CHIEVO VERONA":
            output["HomeTeam"][i] = "CHIEVO"
        if output["AwayTeam"][i] == "AC CHIEVO VERONA":
            output["AwayTeam"][i] = "CHIEVO"       
    
        if output["HomeTeam"][i] == "INTER MILANO" or output["HomeTeam"][i] == "INTER MILAN":
            output["HomeTeam"][i] = "INTER"
        if output["AwayTeam"][i] == "INTER MILANO" or output["AwayTeam"][i] == "INTER MILAN":
            output["AwayTeam"][i] = "INTER"  
           
    # Convert output to pandas
    output = pd.DataFrame(output)
    output.set_index("Date")
    
    return output