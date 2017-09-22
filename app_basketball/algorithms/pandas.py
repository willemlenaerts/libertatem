import json
import pandas as pd
from bs4 import BeautifulSoup 

data = json.load(open("app_basketball/data/input/all_players.json","r"))

output = dict()
output_adv = dict()
output["Player"] = []
output_adv["Player"] = []

count = 0
count_error = 0
# player = "Joe Fulks"
error_check = dict()
for player in data.keys():
    # if player == "Willie Long" or player == 'Monte Towe':
    #     continue
    player_data = data[player]
    soup = player_data["overview_url_content"]
    try:
        per_game_table = soup.split("\n\n\nPer Game\n\n\n")[1].split("\n\n\n\nPer 36 Minutes\n\n\n\n")[0].replace("\n"," ").lstrip().rstrip()
        advanced_table = soup.split("\n\n\nAdvanced\n\n\n")[1].split("\n\n\n\nPlayoffs Totals\n\n\n\n")[0].replace("\n"," ").lstrip().rstrip()
    
    except:
        count_error += 1
        continue
    
    per_game_table_season = per_game_table.split("  ")
    advanced_table_season = advanced_table.split("  ")
    
    if count == 0:
        columns = per_game_table_season[0].split(" ")
        columns_adv = advanced_table_season[0].split(" ") + ["none_1"] + advanced_table_season[1].split(" ") + ["none_2"] + advanced_table_season[2].split(" ")
        for column in columns:
            output[column] = list()
        for column in columns_adv:
            output_adv[column] = list()
            
    per_game_table_season = per_game_table_season[2:]
    advanced_table_season = advanced_table_season[4:]
    
    for i in range(len(per_game_table_season)):
        if "Career" in per_game_table_season[i]:
            career_index  = i
    per_game_table_season = per_game_table_season[:career_index-1]
    
    for i in range(len(advanced_table_season)):
        if "Career" in advanced_table_season[i]:
            career_index_adv  = i
    advanced_table_season = advanced_table_season[:career_index_adv-1]       
    # Remove everything after career_index -1
    
    
    season_len = len(output["Season"])
    tov_len = len(output["TOV"])
    pf_len = len(output["PF"])
    pts_len  = len(output["PTS"])
    col = 0
    for season in per_game_table_season:
        if 'Career' in season:
            break
        
        season = season.rstrip()
        season = season.split(" ")
        if len(season)-1 == len(columns): 
            output["Player"].append(player)
            for i in range(len(columns)):
                if columns[i] in ["Tm","Lg","Pos"]:
                    output[columns[i]].append(season[i+1].split("-")[0])
                elif columns[i] in ["Season","Age","G"]:
                    output[columns[i]].append(int(season[i+1].split("-")[0]))
                else:
                    try:
                        output[columns[i]].append(float(season[i+1].split("-")[0]))
                    except:
                        output[columns[i]].append(None)
        else: # Some data not available
            if len(season) == 1:
                if col >= len(columns):
                    break
                
                # if len(season) > 1 and season[0] == "":
                cols = len(season)
                for i in range(cols):
                    if season[i] == "":
                        output[columns[i+col]].append(None)
                    elif columns[i+col] in ["Tm","Lg","Pos"]:
                        output[columns[i+col]].append(season[i].split("-")[0])
                    elif columns[i+col] in ["Season","Age","G"]:
                        try:
                            output[columns[i+col]].append(int(season[i].split("-")[0]))
                        except:
                            output[columns[i+col]].append(None)
                    else:
                        try:
                            output[columns[i+col]].append(float(season[i].split("-")[0]))
                        except:
                            output[columns[i+col]].append(None)
                    
                    # output[columns[i+col]].append(season[i].split("-")[0])
                    
                try:
                    output[columns[cols+col]].append(None)
                except:
                    pass # Max column bereikt
                col += len(season) + 1            
            elif "-" in season[1]: # Start of row (season)
                col = 0
                output["Player"].append(player)
                col += len(season)
                cols = len(season)-1
                for i in range(cols):
                    output[columns[i]].append(season[i+1].split("-")[0])
                output[columns[cols]].append(None)
            else: # Not start of row
                if col >= len(columns):
                    break
                
                # if len(season) > 1 and season[0] == "":
                cols = len(season)
                for i in range(cols):
                    if season[i] == "":
                        output[columns[i+col]].append(None)
                    elif columns[i+col] in ["Tm","Lg","Pos"]:
                        output[columns[i+col]].append(season[i].split("-")[0])
                    elif columns[i+col] in ["Season","Age","G"]:
                        try:
                            output[columns[i+col]].append(int(season[i].split("-")[0]))
                        except:
                            output[columns[i+col]].append(None)
                    else:
                        try:
                            output[columns[i+col]].append(float(season[i].split("-")[0]))
                        except:
                            output[columns[i+col]].append(None)
                    # output[columns[i+col]].append(season[i].split("-")[0])
                    
                try:
                    output[columns[cols+col]].append(None)
                except:
                    pass # Max column bereikt
                col += len(season) + 1
                    
    if (len(output["Season"]) -season_len) != (len(output["TOV"]) - tov_len) or (len(output["Season"]) -season_len) != (len(output["PF"]) - pf_len)  or (len(output["Season"]) -season_len) != (len(output["PTS"]) - pts_len) :
        error_check[player] = [len(output["TOV"]),len(output["PF"]),len(output["PTS"])]
    
    # count += 1
    # if count%100 == 0:
    #     ##print(count)
    
    col = 0
    for season in advanced_table_season:
        if 'Career' in season:
            break
        
        season = season.rstrip()
        season = season.split(" ")
        # print(season)
        if len(season)-1 == len(columns_adv): 
            # ##print("huh")
            output_adv["Player"].append(player)
            for i in range(len(columns_adv)):
                if columns_adv[i] in ["Tm","Lg","Pos"]:
                    output_adv[columns_adv[i]].append(season[i+1].split("-")[0])
                elif columns_adv[i] in ["Season","Age","G"]:
                    output_adv[columns_adv[i]].append(int(season[i+1].split("-")[0]))
                else:
                    output_adv[columns_adv[i]].append(float(season[i+1].split("-")[0]))
        else: # Some data not available
            if len(season) == 1:
                if "-" in season[0]:
                    if "-" == season[0][0]: # Negative Number
                        if col >= len(columns_adv):
                            #print("b")
                            continue
                        
                        # if len(season) > 1 and season[0] == "":
                        cols = len(season)
                        for i in range(cols):
                            output_adv[columns_adv[i+col]].append(float(season[i]))
                            
                        try:
                            output_adv[columns_adv[cols+col]].append(None)
                        except:
                            pass # Max column bereikt
                        col += len(season) + 1 
                        ##print(col)
                        ##print(cols)
                        ##print("-----")   
                    else: # New Row, season
                        ##print("S")
                        col = 0
                        output_adv["Player"].append(player)
                        col += len(season)+1
                        cols = len(season)
                        for i in range(cols):
                            output_adv[columns_adv[i]].append(season[i].split("-")[0])
                        output_adv[columns_adv[cols]].append(None)
                        ##print(col)
                        ##print(cols)
                        ##print("-----")   
                else:
                    ##print("1")
                    if col >= len(columns_adv):
                        print("a")
                        continue
                    
                    # if len(season) > 1 and season[0] == "":
                    cols = len(season)
                    for i in range(cols):
                        if season[i] == "":
                            output_adv[columns_adv[i+col]].append(None)
                        elif columns_adv[i+col] in ["Tm","Lg","Pos"]:
                            output_adv[columns_adv[i+col]].append(season[i].split("-")[0])
                        elif columns_adv[i+col] in ["Season","Age","G"]:
                            try:
                                output_adv[columns_adv[i+col]].append(int(season[i].split("-")[0]))
                            except:
                                output_adv[columns_adv[i+col]].append(None)
                        else:
                            try:
                                if "-" in season[i]:
                                    output_adv[columns_adv[i+col]].append(float(season[i]))
                                else:
                                    output_adv[columns_adv[i+col]].append(float(season[i].split("-")[0]))
                                
                            except:
                                output_adv[columns_adv[i+col]].append(None)
                            
                        # output_adv[columns_adv[i+col]].append(season[i].split("-")[0])
                    try:
                        output_adv[columns_adv[cols+col]].append(None)
                    except:
                        pass # Max column bereikt
                    col += len(season) + 1   
                    ##print(col)
                    ##print(cols)
                    ##print("-----")
            elif "-" in season[0]:
                if "-" == season[0][0]: # negative number
                    if col >= len(columns_adv):
                        #print("b")
                        continue
                    
                    # if len(season) > 1 and season[0] == "":
                    cols = len(season)
                    for i in range(cols):
                        if season[i] == "":
                            output_adv[columns_adv[i+col]].append(None)
                        elif columns_adv[i+col] in ["Tm","Lg","Pos"]:
                            output_adv[columns_adv[i+col]].append(season[i].split("-")[0])
                        elif columns_adv[i+col] in ["Season","Age","G"]:
                            try:
                                output_adv[columns_adv[i+col]].append(int(season[i].split("-")[0]))
                            except:
                                output_adv[columns_adv[i+col]].append(None)
                        else:
                            try:
                                if "-" in season[i]:
                                    output_adv[columns_adv[i+col]].append(float(season[i]))
                                else:
                                    output_adv[columns_adv[i+col]].append(float(season[i].split("-")[0]))
                            except:
                                output_adv[columns_adv[i+col]].append(None)                    
    
                    try:
                        output_adv[columns_adv[cols+col]].append(None)
                    except:
                        pass # Max column bereikt
                    col += len(season) + 1 
                    ##print(col)
                    ##print(cols)
                    ##print("-----")            
                else: # Season
                    ##print("S")
                    col = 0
                    output_adv["Player"].append(player)
                    col += len(season)+1
                    cols = len(season)
                    for i in range(cols):
                        if "-" == season[i][0]:
                            if columns_adv[i] in ["Tm","Lg","Pos"]:
                                output_adv[columns_adv[i]].append(season[i])
                            elif columns_adv[i] in ["Season","Age","G"]:
                                output_adv[columns_adv[i]].append(int(season[i]))
                            else:
                                output_adv[columns_adv[i]].append(float(season[i]))
                        else:
                            if columns_adv[i] in ["Tm","Lg","Pos"]:
                                output_adv[columns_adv[i]].append(season[i].split("-")[0])
                            elif columns_adv[i] in ["Season","Age","G"]:
                                output_adv[columns_adv[i]].append(int(season[i].split("-")[0]))
                            else:
                                output_adv[columns_adv[i]].append(float(season[i].split("-")[0]))                    
                    output_adv[columns_adv[cols]].append(None)
                    ##print(col)
                    ##print(cols)
                    ##print("-----")   
            elif "-" in season[1]:
                if "-" == season[1][0]: # negative number
                    if col >= len(columns_adv):
                        #print("c")
                        continue
                    
                    # if len(season) > 1 and season[0] == "":
                    cols = len(season)
                    for i in range(cols):
                        if season[i] == "":
                            output_adv[columns_adv[i+col]].append(None)
                        elif columns_adv[i+col] in ["Tm","Lg","Pos"]:
                            output_adv[columns_adv[i+col]].append(season[i].split("-")[0])
                        elif columns_adv[i+col] in ["Season","Age","G"]:
                            try:
                                output_adv[columns_adv[i+col]].append(int(season[i].split("-")[0]))
                            except:
                                output_adv[columns_adv[i+col]].append(None)
                        else:
                            try:
                                if "-" in season[i]:
                                    output_adv[columns_adv[i+col]].append(float(season[i]))
                                else:
                                    output_adv[columns_adv[i+col]].append(float(season[i].split("-")[0]))
                            except:
                                output_adv[columns_adv[i+col]].append(None)
                                
                        # output_adv[columns_adv[i+col]].append(float(season[i]))
                    try:
                        output_adv[columns_adv[cols+col]].append(None)
                    except:
                        pass # Max column bereikt
                    col += len(season) + 1 
                    ##print(col)
                    ##print(cols)
                    ##print("-----")            
                else: # Season
                    ##print("S")
                    col = 0
                    output_adv["Player"].append(player)
                    col += len(season)
                    cols = len(season)-1
                    for i in range(cols):
                        if "-" == season[i+1][0]:
                            if columns_adv[i] in ["Tm","Lg","Pos"]:
                                output_adv[columns_adv[i]].append(season[i+1])
                            elif columns_adv[i] in ["Season","Age","G"]:
                                output_adv[columns_adv[i]].append(int(season[i+1]))
                            else:
                                output_adv[columns_adv[i]].append(float(season[i+1]))
                        else:
                            if columns_adv[i] in ["Tm","Lg","Pos"]:
                                output_adv[columns_adv[i]].append(season[i+1].split("-")[0])
                            elif columns_adv[i] in ["Season","Age","G"]:
                                output_adv[columns_adv[i]].append(int(season[i+1].split("-")[0]))
                            else:
                                output_adv[columns_adv[i]].append(float(season[i+1].split("-")[0]))                            
                    output_adv[columns_adv[cols]].append(None)
                    ##print(col)
                    ##print(cols)
                    ##print("-----")            
            else: # Not start of row
                if col >= len(columns_adv):
                    # print("d")
                    continue
                
                # if len(season) > 1 and season[0] == "":
                cols = len(season)
                for i in range(cols):
                    # print("a")
                    if season[i] == "":
                        output_adv[columns_adv[i+col]].append(None)
                    elif columns_adv[i+col] in ["Tm","Lg","Pos"]:
                        output_adv[columns_adv[i+col]].append(season[i].split("-")[0])
                    elif columns_adv[i+col] in ["Season","Age","G"]:
                        try:
                            output_adv[columns_adv[i+col]].append(int(season[i].split("-")[0]))
                        except:
                            output_adv[columns_adv[i+col]].append(None)
                    else:
                        try:
                            # print(float(season[i]))
                            output_adv[columns_adv[i+col]].append(float(season[i]))
                        except:
                            # print("c")
                            output_adv[columns_adv[i+col]].append(None)
                    
                try:
                    output_adv[columns_adv[cols+col]].append(None)
                except:
                    pass # Max column bereikt
                col += len(season) + 1 
                ##print(col)
                ##print(cols)
                ##print("-----")
        
    # if (len(output_adv["Season"]) -season_len) != (len(output["TOV"]) - tov_len) or (len(output["Season"]) -season_len) != (len(output["PF"]) - pf_len)  or (len(output["Season"]) -season_len) != (len(output["PTS"]) - pts_len) :
    #     error_check[player] = [len(output["TOV"]),len(output["PF"]),len(output["PTS"])]
    
    count += 1
    if count%100 == 0:
        print(count)

# Test
for key in output.keys():
    print(key + " " + str(len(output[key])))
for key in output_adv.keys():
    print(key + " " + str(len(output_adv[key])))
playerseasons = []
playerseasons_adv = []
for i in range(len(output["Season"])):
    playerseasons.append(output["Player"][i] + " " + str(output["Tm"][i]) + " " + str(output["Season"][i]))
for i in range(len(output_adv["Season"])):
    playerseasons_adv.append(output_adv["Player"][i] + " " + str(output_adv["Tm"][i]) +  " " + str(output_adv["Season"][i]))
    
a = list(set(playerseasons)-set(playerseasons_adv))

output.update(output_adv)
output.pop("none_1",None)
output.pop("none_2",None)

# Make Pandas
output = pd.DataFrame(output)
# output.set_index("Season")

# Make Pandas columns correct type
output.Season = output.Season.astype(int)
# output.Age.astype(int)

import pickle
pickle.dump(output,open("app_basketball/data/input/panda.p","wb"))