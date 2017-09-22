__author__ = 'Exergos'

########################################################################################################################
########################################################################################################################

#########################
# What does this file do?
#########################

# This Scrape file gets Jupiler Pro League results data from sporza.be
# Compared to "sporza.py" it gets data from all seasons, including goal minutes
# Python 3.3 as Interpreter
# BeautifulSoup to Scrape
# Numpy for Array use

######################
# What does it return?
######################

# output[season][game] =    dict()
#                           output[season][game]["game_date"]
#                           output[season][game]["game_hour"]
#                           output[season][game]["host"]
#                           output[season][game]["visitor"]
#                           output[season][game]["result"]
#                           output[season][game]["host_goal"]
#                           output[season][game]["visitor_goal"]
#                           output[season][game]["referee"]
#                           output[season][game]["stadium"]
#                           output[season][game]["spectators"]
#                           output[season][game]["host_goal_data"]
#                           output[season][game]["visitor_goal_data"]
#                           output[season][game]["host_yellow_card_data"]
#                           output[season][game]["visitor_yellow_card_data"]
#                           output[season][game]["host_red_card_data"]
#                           output[season][game]["visitor_red_card_data"]
#                           output[season][game]["host_starting_team"]
#                           output[season][game]["visitor_starting_team"]
#                           output[season][game]["host_substitution"]
#                           output[season][game]["visitor_substitution"]
#                           output[season][game]["host_manager"]
#                           output[season][game]["visitor_manager"]
#                           output[season][game]["minute_x with x from 1 tot 90
#                           output[season][game]["minute_x_host"] with x from 1 tot 90
#                           output[season][game]["minute_x_tie"] with x from 1 tot 90
#                           output[season][game]["minute_x_visitor"] with x from 1 tot 90

########################################################################################################################
########################################################################################################################

# sporza_big gets ALL data from sporza website
def sporza_scrape():
    print("Starting scrape of sporza.be")
    # Time algorithm
    import time
    import datetime

    # Scraping tools
    from bs4 import BeautifulSoup
    import urllib.request

    # Open Main Website
    main_site = "http://sporza.be/cm/sporza/matchcenter/mc_voetbal/jupilerleague_1516/"
    
    # Stupid hack: in welke PO zitten ploegen?
    poi = ["Anderlecht","AA Gent","Club Brugge","Standard","Kortrijk","Charleroi"]
    poii_a = ["KV Mechelen","Racing Genk","Waasland-Beveren","Zulte Waregem"]
    poii_b = ["Lokeren","Moeskroen-Péruwelz","Oostende","Westerlo"]
    poiii = ["Cercle Brugge","Lierse SK"]
    
    # All speeldagen URL's
    speeldagen_url = []
    for i in range(20):
        speeldagen_url.append("JPL_speeldag_" + str(i+1))
        
    for i in range(2):
        speeldagen_url.append("MG_speeldag_" + str(i+21))
        
    for i in range(7):
        speeldagen_url.append("JPL_speeldag_" + str(i+23))
        
    for i in range(1):
        speeldagen_url.append("MG_speeldag_" + str(i+30))   
        
    for i in range(4):
        speeldagen_url.append("MG_speeldag_" + str(i+1) + "_PO_I_II_III")
        
    for i in range(1):
        speeldagen_url.append("MG_speeldag_" + str(i+5) + "_PO_I")
        
    for i in range(1):
        speeldagen_url.append("MG_speeldag_" + str(i+6) + "_PO_I_" + "speeldag_" + str(i+5) + "_PO_II_III") 
        
    for i in range(1):
        speeldagen_url.append("MG_speeldag_" + str(i+7) + "_PO_I_" + "speeldag_" + str(i+6) + "_PO_II")
        
    for i in range(3):
        speeldagen_url.append("MG_speeldag_" + str(i+8) + "_PO_I")
    
    # Sla alle data van alle matchen op
    wedstrijden = []
    
    # Speeldag per speeldag
    for speeldag_url in speeldagen_url: 
        # Open speeldag webpagina
        print("Scraping " + speeldag_url)
        speeldag_html = BeautifulSoup(urllib.request.urlopen(main_site + speeldag_url))
        
        # Wedstrijden op deze speeldag
        wedstrijden_url = speeldag_html.find_all("td", class_=["score"])
        for i in range(len(wedstrijden_url)):
            wedstrijd_url = "http://sporza.be" + wedstrijden_url[i].find("a")["href"]
            wedstrijden_url[i] = wedstrijd_url
            
        # Wedstrijd per wedstrijd
        for wedstrijd_url in wedstrijden_url:
            # Allerlaatste wedstrijd niet downloaden (PO II Finale)
            if speeldag_url ==  speeldagen_url[-1] and wedstrijd_url == wedstrijden_url[-1]:
                break
            
            # Creëer dict om wedstrijd op te slaan
            wedstrijden.append(dict())
            
            # Open wedstrijd webpagina
            print("Scraping " + wedstrijd_url)
            wedstrijd_html = BeautifulSoup(urllib.request.urlopen(wedstrijd_url))
            
            # Welke competitie? (rs, poi, poiI, poiii)
            if wedstrijd_html.find("a",class_=["matchgroup"]).get_text() == "Play-offs":
                for team in poi:
                    if wedstrijd_html.find_all("dt")[0].get_text().replace('\n','') == team:
                        wedstrijden[-1]["competition"] = "poi"
                        break
                for team in poii_a:
                    if wedstrijd_html.find_all("dt")[0].get_text().replace('\n','') == team:
                        wedstrijden[-1]["competition"] = "poii_a"
                        break
                for team in poii_b:
                    if wedstrijd_html.find_all("dt")[0].get_text().replace('\n','') == team:
                        wedstrijden[-1]["competition"] = "poii_b"
                        break
                for team in poiii:
                    if wedstrijd_html.find_all("dt")[0].get_text().replace('\n','') == team:
                        wedstrijden[-1]["competition"] = "poiii"
                        break
            else:
                wedstrijden[-1]["competition"] = "rs"
                
            # Welke speeldag?
            if wedstrijden[-1]["competition"] == "rs" or wedstrijden[-1]["competition"] == "poi":
                wedstrijden[-1]["speeldag"] = wedstrijden[-1]["competition"] + " " + speeldag_url.split("_")[2]
            else:
                dummy = len(speeldag_url.split("_"))
                if dummy == 7:
                    wedstrijden[-1]["speeldag"] = wedstrijden[-1]["competition"] + " " + speeldag_url.split("_")[2]
                if dummy == 9:
                    wedstrijden[-1]["speeldag"] = wedstrijden[-1]["competition"] + " " + speeldag_url.split("_")[6]
                if dummy == 10:
                    wedstrijden[-1]["speeldag"] = wedstrijden[-1]["competition"] + " " + speeldag_url.split("_")[6]
                    
            # Voeg wedstrijddata toe
            wedstrijd_html.find(id="metadata").find("strong").replaceWith("")
            wedstrijden[-1]["game_date"] = datetime.datetime.strptime(wedstrijd_html.find(id="metadata").get_text().replace('\n',''),"%d/%m/%Y %H:%M")
            
            # Host
            wedstrijden[-1]["host"] = wedstrijd_html.find_all("dt")[0].get_text().replace('\n','')
    
            # Visitor
            wedstrijden[-1]["visitor"] = wedstrijd_html.find_all("dt")[1].get_text().replace('\n','')
            
            
            # Check of wedstrijd al gespeeld is:
            if wedstrijd_html.find("span", class_=["json-progress"]).get_text().replace('\n','') == "einde":
                wedstrijden[-1]["played"] = True
            else:
                wedstrijden[-1]["played"] = False
            
            if wedstrijden[-1]["played"]:
                # Host goals
                wedstrijden[-1]["host_goal"] = wedstrijd_html.find_all("dd",class_=["score"])[0].get_text().replace('\n','')
        
                # Visitor goals
                wedstrijden[-1]["visitor_goal"] = wedstrijd_html.find_all("dd",class_=["score"])[1].get_text().replace('\n','')
        
                # Result
                if int(wedstrijden[-1]["host_goal"]) > int(wedstrijden[-1]["visitor_goal"]):
                    wedstrijden[-1]["result"] = "1"
                else:
                    if int(wedstrijden[-1]["host_goal"]) == int(wedstrijden[-1]["visitor_goal"]):
                        wedstrijden[-1]["result"] = "0"
                    else:
                        wedstrijden[-1]["result"] = "-1"
        
                if len(wedstrijd_html.find_all(class_="GENERIC")) is not 0: # Forfait or Lack of data check
                    # Referee
                    wedstrijden[-1]["referee"] = wedstrijd_html.find_all("ul",class_=["lineupmetadata"])[0].get_text().split('\n')[1].replace('scheidsrechter: ','')
        
                    # Stadium
                    wedstrijden[-1]["stadium"] = wedstrijd_html.find_all("ul",class_=["lineupmetadata"])[0].get_text().split('\n')[2].replace('stadion: ','')
        
                    # Spectators
                    wedstrijden[-1]["spectators"] = wedstrijd_html.find_all("ul",class_=["lineupmetadata"])[0].get_text().split('\n')[4].replace('toeschouwers: ','')
        
                    # Goal Data
                    wedstrijden[-1]["host_goal_data"] = sporza_scrape_function(wedstrijd_html.find_all("ol",class_=["eventset1"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventsethalftime"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventset2"])[0],
                                                               "host goal")
                    wedstrijden[-1]["visitor_goal_data"] = sporza_scrape_function(wedstrijd_html.find_all("ol",class_=["eventset1"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventsethalftime"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventset2"])[0],
                                                               "visitor goal")
        
                    # Yellow Cards
                    wedstrijden[-1]["host_yellow_card_data"] = sporza_scrape_function(wedstrijd_html.find_all("ol",class_=["eventset1"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventsethalftime"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventset2"])[0],
                                                               "host yellow_card")
                    wedstrijden[-1]["visitor_yellow_card_data"] = sporza_scrape_function(wedstrijd_html.find_all("ol",class_=["eventset1"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventsethalftime"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventset2"])[0],
                                                               "visitor yellow_card")
        
                    # Red Cards
                    wedstrijden[-1]["host_red_card_data"] = sporza_scrape_function(wedstrijd_html.find_all("ol",class_=["eventset1"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventsethalftime"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventset2"])[0],
                                                               "host red_card")
        
                    wedstrijden[-1]["visitor_red_card_data"] = sporza_scrape_function(wedstrijd_html.find_all("ol",class_=["eventset1"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventsethalftime"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventset2"])[0],
                                                               "visitor red_card")
        
                    # Starting Team
                    home_starting_team_dummy = wedstrijd_html.find_all(class_="GENERIC")[1].get_text().split('\n')[3].split(', ')
                    home_starting_team_dummy[-1] = home_starting_team_dummy[-1][0:-1]
                    wedstrijden[-1]["host_starting_team"] = '//'.join(home_starting_team_dummy)
        
                    away_starting_team_dummy = wedstrijd_html.find_all(class_="GENERIC")[0].get_text().split('\n')[3].split(', ')
                    away_starting_team_dummy[-1] = away_starting_team_dummy[-1][0:-1]
                    wedstrijden[-1]["visitor_starting_team"] = '//'.join(away_starting_team_dummy)
        
                    # Substitutions
                    wedstrijden[-1]["host_substitution"] = sporza_scrape_function(wedstrijd_html.find_all("ol",class_=["eventset1"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventsethalftime"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventset2"])[0],
                                                               "host inout")
                    wedstrijden[-1]["visitor_substitution"] = sporza_scrape_function(wedstrijd_html.find_all("ol",class_=["eventset1"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventsethalftime"])[0],
                                                               wedstrijd_html.find_all("ol",class_=["eventset2"])[0],
                                                               "visitor inout")
        
                    # Managers
                    wedstrijden[-1]["host_manager"] = wedstrijd_html.find(class_=["coach"]).get_text().replace('\n\xa0\n\n','').split('\n')[0]
                    wedstrijden[-1]["visitor_manager"] = wedstrijd_html.find(class_=["coach"]).get_text().replace('\n\xa0\n\n','').split('\n')[1]
                else:
                    # Just add empty string
                    wedstrijden[-1]["referee"] = ''
                    wedstrijden[-1]["stadium"] = ''
                    wedstrijden[-1]["spectators"] = ''
                    wedstrijden[-1]["host_goal_data"] = ''
                    wedstrijden[-1]["visitor_goal_data"] = ''
                    wedstrijden[-1]["host_yellow_card_data"] = ''
                    wedstrijden[-1]["visitor_yellow_card_data"] = ''
                    wedstrijden[-1]["host_red_card_data"] = ''
                    wedstrijden[-1]["visitor_red_card_data"] = ''
                    wedstrijden[-1]["host_starting_team"] = ''
                    wedstrijden[-1]["visitor_starting_team"] = ''
                    wedstrijden[-1]["host_substitution"] = ''
                    wedstrijden[-1]["visitor_substitution"] = ''
                    wedstrijden[-1]["host_manager"] = ''
                    wedstrijden[-1]["visitor_manager"] = ''
            
            # Wedstrijd nog niet gespeeld
            else:
                # Just add empty string
                wedstrijden[-1]["referee"] = ''
                wedstrijden[-1]["stadium"] = ''
                wedstrijden[-1]["spectators"] = ''
                wedstrijden[-1]["host_goal"] = ''
                wedstrijden[-1]["visitor_goal"] = ''
                wedstrijden[-1]["result"] = ''
                wedstrijden[-1]["host_goal_data"] = ''
                wedstrijden[-1]["visitor_goal_data"] = ''
                wedstrijden[-1]["host_yellow_card_data"] = ''
                wedstrijden[-1]["visitor_yellow_card_data"] = ''
                wedstrijden[-1]["host_red_card_data"] = ''
                wedstrijden[-1]["visitor_red_card_data"] = ''
                wedstrijden[-1]["host_starting_team"] = ''
                wedstrijden[-1]["visitor_starting_team"] = ''
                wedstrijden[-1]["host_substitution"] = ''
                wedstrijden[-1]["visitor_substitution"] = ''
                wedstrijden[-1]["host_manager"] = ''
                wedstrijden[-1]["visitor_manager"] = ''
                
    # Save to file sporza.p
    import pickle
    pickle.dump(wedstrijden, open("app_playoffs/algorithms/data/sporza.p", "wb"))
    
    return wedstrijden

# helper function for sporza_scrape()
def sporza_scrape_function(first_half,halftime,second_half,info):
    # Take into account first and second yellow
    if info == "host yellow_card" or info == "visitor yellow_card":
        dummy_data = second_half.find_all(class_=info + "1") \
                     + second_half.find_all(class_=info + "2") \
                     + halftime.find_all(class_=info + "1") \
                     + halftime.find_all(class_=info + "2") \
                     + first_half.find_all(class_=info + "1") \
                     + first_half.find_all(class_=info + "2")
    else:
        # Take into account own goals
        if info == "host goal" or info == "visitor goal":
            dummy_data = second_half.find_all(class_=info.replace(" goal"," own_goal")) \
                         +second_half.find_all(class_=info.replace(" goal"," penalty_scored")) \
                         + second_half.find_all(class_=info) \
                         + halftime.find_all(class_=info.replace(" goal"," own_goal")) \
                         + halftime.find_all(class_=info.replace(" goal"," penalty_scored")) \
                         + halftime.find_all(class_=info) \
                         + first_half.find_all(class_=info.replace(" goal"," own_goal")) \
                         + first_half.find_all(class_=info.replace(" goal"," penalty_scored")) \
                         + first_half.find_all(class_=info)
        else:
            dummy_data = second_half.find_all(class_=info) \
                         + halftime.find_all(class_=info) \
                         + first_half.find_all(class_=info)
    
    
    dummy_data_string = ''
    for k in range(len(dummy_data)):
        if k == 0:
            dummy_data_string = dummy_data[k]['title']
        else:
            dummy_data_string = dummy_data_string + '//' + dummy_data[k]['title']
    dummy_data_string = dummy_data_string.replace('<br>','//') # For substitutions in same minute
    
    return dummy_data_string