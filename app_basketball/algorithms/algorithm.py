import pickle
import numpy as np
import pandas as pd
import json
panda = pickle.load(open("app_basketball/data/input/panda.p","rb"))

# Get TS%_rot: (TS% from rest of team in same season)
# and NI: Narcissism Index = FGA*(TS%_rot - TS%)
# and SI: Scorers Index = (TS%-TS%_league)/TS%_league
sLength = len(panda["FGA"])
panda['TS%_rot'] = pd.Series(np.zeros(sLength), index=panda.index)
panda['NI'] = pd.Series(np.zeros(sLength), index=panda.index)
panda['SI'] = pd.Series(np.zeros(sLength), index=panda.index)

# Get seasons
seasons = list(set(panda.Season))

# output
league_average = dict()
table_ni = list()
table_si_career = list()
table_si_season = list()
scatter_plot_data_ni = dict()
scatter_plot_data_si = dict()
players_scatter_plot_si = []
x_axis_ni = dict()
y_axis_ni = dict()
x_axis_si = dict()
y_axis_si = dict()
for season in seasons:
    # season = 2014
    print("Season " + str(season) + "-" + str(int(season)+1)[-2:])
    # Only for season, no TOT data (only per team)
    panda_season = panda[(panda.Season == season) & (panda.Tm != "TOT")]
    
    # Every player who played in season
    players = list(set(panda_season["Player"]))

    # League average TS% and FGA (per player)
    try:
        ts_la = round(1000*panda_season["TS%"].dropna().astype(float).mean())/10
    except:
        ts_la = None
    try:
        fga_la = round(10*panda_season["FGA"].dropna().astype(float).mean())/10
    except:
        fga_la = None
    league_average[str(season)] = [ts_la,fga_la]
    
    for player in players:
        player_panda = panda_season[panda_season.Player == player]
        indices = list(player_panda.index)
        
        
        for index in indices:
            # TS%_rot and NI
            team = panda.iloc[index]["Tm"]
            
            team_panda = panda_season[(panda_season.Player != player) & (panda_season.Tm == team)]
            
           
            ts_rot = 0
            fga_rot = 0
            for i in range(len(team_panda)):
                if pd.isnull(team_panda.iloc[i]["TS%"]) or pd.isnull(team_panda.iloc[i]["FGA"]) or pd.isnull(team_panda.iloc[i]["G"]):
                    ts_rot += 0
                else:
                    ts_rot += float(team_panda.iloc[i]["TS%"])*float(team_panda.iloc[i]["FGA"])*int(team_panda.iloc[i]["G"])
                
                if pd.isnull(team_panda.iloc[i]["FGA"]) or pd.isnull(team_panda.iloc[i]["G"]):
                    fga_rot += 0
                else:
                    fga_rot += float(team_panda.iloc[i]["FGA"])*int(team_panda.iloc[i]["G"])
            if ts_rot == 0:
                panda.ix[index,'TS%_rot'] = None
            else:
                if fga_rot != 0:
                    ts_rot = ts_rot/fga_rot
                    panda.ix[index,'TS%_rot'] = ts_rot
                    
                    try:
                        sigma_ts_league = (league_average[str(season)][0]/100)/float(panda.iloc[index]["TS%"])
                        delta_ts_team = 100*(ts_rot-float(panda.iloc[index]["TS%"]))
                        fga = float(panda.iloc[index]["FGA"])
                        # panda.ix[index,'NI'] = ((float(panda.iloc[index]["FGA"])/10)**2)*(105*(delta_ts**2) + (390/20)*delta_ts + 1)
                        panda.ix[index,'NI'] = ((fga/10)**2)*(delta_ts_team/4 + 1)*sigma_ts_league
                        # panda.ix[index,'NI'] = (fga/10) + (delta_ts_team/2)
                    except:
                        panda.ix[index,'NI'] = None
                else:
                    panda.ix[index,'TS%_rot'] = None
                    panda.ix[index,'NI'] = None
        
            # SI
            if (not pd.isnull(panda.iloc[index]["TS%"])) and (not pd.isnull(panda.iloc[index]["PTS"])):
                pts = panda.iloc[index]["PTS"]
                ts_fraction = ((panda.iloc[index]["TS%"] - (league_average[str(season)][0]/100))/(league_average[str(season)][0]/100))
                panda.ix[index,'SI'] = pts*ts_fraction
            else:
                panda.ix[index,'SI'] = None
                
    panda_season = panda[(panda.Season == season) & (panda.Tm != "TOT") & (panda.NI.notnull())].sort("NI")
    
    
    # Table NI
    for i in range(len(panda_season)):
        if panda_season.iloc[i]["TS%"] == None or panda_season.iloc[i]["TS%"] == "" or pd.isnull(panda_season.iloc[i]["TS%"]):
            continue

        if panda_season.iloc[i]["FGA"] == None or panda_season.iloc[i]["FGA"] == "" or pd.isnull(panda_season.iloc[i]["FGA"]):
            continue
        
        if panda_season.iloc[i]["TS%_rot"] == None or panda_season.iloc[i]["TS%_rot"] == "" or pd.isnull(panda_season.iloc[i]["TS%_rot"]):
            continue
        
        if panda_season.iloc[i]["NI"] == None or panda_season.iloc[i]["NI"] == "" or pd.isnull(panda_season.iloc[i]["NI"]):
            continue

        if panda_season.iloc[i]["G"] == None or panda_season.iloc[i]["G"] == "" or pd.isnull(panda_season.iloc[i]["G"]):
            continue
        
        if panda_season.iloc[i]["Age"] == None or panda_season.iloc[i]["Age"] == "" or pd.isnull(panda_season.iloc[i]["Age"]):
            continue
        # Now select part of panda
        if int(panda_season.iloc[i]["G"]) < 30:
            continue
        
        if float(panda_season.iloc[i]["NI"]) < 8:
            continue
        
        table_ni.append({  "Player": panda_season.iloc[i]["Player"],
                        "Team": panda_season.iloc[i]["Tm"],
                        "Season": str(panda_season.iloc[i]["Season"]) + "-" + str(panda_season.iloc[i]["Season"]+1)[-2:],
                        "TS%": round(1000*float(panda_season.iloc[i]["TS%"]))/10,
                        "FGA": float(panda_season.iloc[i]["FGA"]),
                        "TS%_rot": round(1000*float(panda_season.iloc[i]["TS%_rot"]))/10,
                        "NI": round(10*float(panda_season.iloc[i]["NI"]))/10,
                        "Age": int(panda_season.iloc[i]["Age"]),
                        "TS%_league": league_average[str(season)][0]})
    
    
    # Scatter Plot NI
    scatter_plot_data_ni[str(season)] = []
    for i in range(len(panda_season)):
        if panda_season.iloc[i]["TS%"] == None or panda_season.iloc[i]["TS%"] == "" or pd.isnull(panda_season.iloc[i]["TS%"]):
            continue

        if panda_season.iloc[i]["FGA"] == None or panda_season.iloc[i]["FGA"] == "" or pd.isnull(panda_season.iloc[i]["FGA"]):
            continue

        # Now select part of panda
        if int(panda_season.iloc[i]["G"]) < 30:
            continue
        
        scatter_plot_data_ni[str(season)].append({  "x": round(10*float(panda_season.iloc[i]["FGA"]))/10,
                                    "y": round(1000*float(panda_season.iloc[i]["TS%"]))/10,
                                    "player": panda_season.iloc[i]["Player"],
                                    "season": str(panda_season.iloc[i]["Season"]) + "-" + str(panda_season.iloc[i]["Season"]+1)[-2:],
                                    "team": panda_season.iloc[i]["Tm"]})
                                
    # Scatter Plot SI
    scatter_plot_data_si[str(season)] = []
    panda_season_top20 = panda_season[(panda_season.PTS.astype(float) > 20) & (panda_season.G.astype(int) > 50)].sort("SI",ascending=False).iloc[0:20]
    for i in range(len(panda_season_top20)):
        if panda_season_top20.iloc[i]["SI"] == None or panda_season_top20.iloc[i]["SI"] == "" or pd.isnull(panda_season_top20.iloc[i]["SI"]):
            continue

        if panda_season_top20.iloc[i]["FGA"] == None or panda_season_top20.iloc[i]["FGA"] == "" or pd.isnull(panda_season_top20.iloc[i]["FGA"]):
            continue
        
        players_scatter_plot_si.append(panda_season_top20.iloc[i].Player)
        eff = float(panda_season_top20.iloc[i]["SI"])/float(panda_season_top20.iloc[i]["PTS"])
        vol = float(panda_season_top20.iloc[i]["PTS"])
        
        scatter_plot_data_si[str(season)].append({  "x": round(1000*eff)/10,
                                    "y": round(10*vol)/10,
                                    "player": panda_season_top20.iloc[i]["Player"],
                                    "season": str(panda_season_top20.iloc[i]["Season"]) + "-" + str(panda_season_top20.iloc[i]["Season"]+1)[-2:],
                                    "team": panda_season_top20.iloc[i]["Tm"],
                                    "FGA": round(10*float(panda_season_top20.iloc[i]["FGA"]))/10,
                                    "SI": round(10*float(panda_season_top20.iloc[i]["SI"]))/10})

    # Min/Max for x/y axis Scatterplot NI
    x_axis_ni[str(season)] = [0]
    y_axis_ni[str(season)] = []
    
    dummy_x = []
    dummy_y = []
    for el in scatter_plot_data_ni[str(season)]:
        dummy_x.append(el["x"]) 
        dummy_y.append(el["y"])
    
    x_axis_ni[str(season)].append(max(dummy_x))
    y_axis_ni[str(season)].append(min(dummy_y))
    y_axis_ni[str(season)].append(max(dummy_y))

    # Min/Max for x/y axis Scatterplot SI
    if scatter_plot_data_si[str(season)] != []:
        x_axis_si[str(season)] = []
        y_axis_si[str(season)] = []
        
        dummy_x = []
        dummy_y = []
        for el in scatter_plot_data_si[str(season)]:
            dummy_x.append(el["x"]) 
            dummy_y.append(el["y"])
        
        x_axis_si[str(season)].append(min(dummy_x))
        x_axis_si[str(season)].append(max(dummy_x))
        y_axis_si[str(season)].append(min(dummy_y))
        y_axis_si[str(season)].append(max(dummy_y))    

# Players scatter plot
players_scatter_plot_si = list(set(players_scatter_plot_si))
# x_axis and y_axis for whole NBA span
x_axis_si_min = []
x_axis_si_max = []
y_axis_si_min = []
y_axis_si_max = []
scatter_plot_data_si_total = []
for season in x_axis_si.keys():
    x_axis_si_min.append(x_axis_si[season][0])
    x_axis_si_max.append(x_axis_si[season][1])
    y_axis_si_min.append(y_axis_si[season][0])
    y_axis_si_max.append(y_axis_si[season][1])
    for i in range(len(scatter_plot_data_si[season])):
        scatter_plot_data_si_total.append(scatter_plot_data_si[season][i])

x_axis_si_total = []
x_axis_si_total.append(min(x_axis_si_min))
x_axis_si_total.append(max(x_axis_si_max))

y_axis_si_total = []
y_axis_si_total.append(min(y_axis_si_min))
y_axis_si_total.append(max(y_axis_si_max))



# Table SI Career
players = list(set(panda.Player))
dummy_player = []
dummy_active = []
dummy_SI = []
for player in players:
    panda_player = panda[(panda.Player == player) & (panda.Tm != "TOT")]
    
    # Check how many seasons a player was in the league
    player_seasons = len(list(set(panda_player.Season)))
    if player_seasons <5:
        continue
    indices = panda_player.index
    
    career_games = 0
    career_fga = 0
    career_points = 0
    career_SI = 0
    teams = ""
    for i in range(len(indices)):
        if pd.isnull(panda.iloc[indices[i]].SI) or pd.isnull(panda.iloc[indices[i]].G) or pd.isnull(panda.iloc[indices[i]].PTS):
            continue
        if i == 0:
            start_career = panda.iloc[indices[i]].Season
        if i == len(indices)-1:
            end_career = panda.iloc[indices[i]].Season
        career_fga += float(panda.iloc[indices[i]].FGA)*panda.iloc[indices[i]].G.astype(int)
        career_games += panda.iloc[indices[i]].G.astype(int)
        career_points += panda.iloc[indices[i]].G.astype(int)*panda.iloc[indices[i]].PTS.astype(float)
        career_SI += float(panda.iloc[indices[i]].FGA)*panda.iloc[indices[i]].G.astype(int)*panda.iloc[indices[i]].SI.astype(float)
        if panda.iloc[indices[i]].Tm not in teams:
            teams+= panda.iloc[indices[i]].Tm + "/"
        
    if career_games == 0:
        continue
    if end_career == 2014:
        end_career = "..."
    career_ppg = career_points/career_games
    career_SI = career_SI/career_fga
    if career_ppg > 20:
        # Add to table
        dummy_player.append(player)
        try:
            dummy_active.append(str(start_career) + "-" + str(int(end_career)+1))
        except:
            dummy_active.append(str(start_career) + "-" + str(end_career))
        dummy_SI.append(round(10*career_SI)/10)
        

zipped = reversed(sorted(zip(dummy_SI,dummy_player,dummy_active)))

dummy_SI,dummy_player,dummy_active = zip(*zipped)

for i in range(len(dummy_SI)):
    table_si_career.append({   "Rank": i+1,
                        "Player": dummy_player[i],
                        # "Teams": teams[:-1],
                        "Active": dummy_active[i],
                        "SI": dummy_SI[i]
                    })

# Table SI Season (top 100)
panda_top_100 = panda[(panda.Tm != "TOT") & (panda.G > 50) & (panda.PTS > 20) & (panda.SI.notnull())].sort("SI", ascending=False).iloc[0:100]
for i in range(len(panda_top_100)):
    table_si_season.append({   "Rank": i+1,
                        "Player": panda_top_100.iloc[i]["Player"],
                        "Team": panda_top_100.iloc[i]["Tm"],
                        "Season": str(panda_top_100.iloc[i]["Season"]) + "-" + str(panda_top_100.iloc[i]["Season"]+1)[-2:],
                        "SI": round(10*panda_top_100.iloc[i]["SI"])/10
                    })
                    
json.dump(league_average,open("app_basketball/data/output/league_average.json","w"))
json.dump(table_ni,open("app_basketball/data/output/table_ni.json","w"))
json.dump(table_si_career,open("app_basketball/data/output/table_si_career.json","w"))
json.dump(table_si_season,open("app_basketball/data/output/table_si_season.json","w"))
json.dump(x_axis_ni,open("app_basketball/data/output/x_axis_ni.json","w"))
json.dump(y_axis_ni,open("app_basketball/data/output/y_axis_ni.json","w"))
json.dump(x_axis_si,open("app_basketball/data/output/x_axis_si.json","w"))
json.dump(y_axis_si,open("app_basketball/data/output/y_axis_si.json","w"))

# players_scatter_plot_si = []
# for i in range(len(scatter_plot_data_si_total)):
#     players_scatter_plot_si.append(scatter_plot_data_si_total[i]["player"])
# players_scatter_plot_si = list(set(players_scatter_plot_si))

json.dump(scatter_plot_data_si_total,open("app_basketball/data/output/scatter_plot_data_si_total.json","w"))
json.dump(players_scatter_plot_si,open("app_basketball/data/output/players_scatter_plot_si.json","w"))
json.dump(x_axis_si_total,open("app_basketball/data/output/x_axis_si_total.json","w"))
json.dump(y_axis_si_total,open("app_basketball/data/output/y_axis_si_total.json","w"))

for year in scatter_plot_data_ni.keys():
    json.dump(scatter_plot_data_ni[year],open("app_basketball/data/output/Scatter Plot NI per Year/" + year + ".json","w"))
for year in scatter_plot_data_si.keys():
    json.dump(scatter_plot_data_si[year],open("app_basketball/data/output/Scatter Plot SI per Year/" + year + ".json","w"))