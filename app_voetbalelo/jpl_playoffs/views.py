from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

# Import models to use in website (database - site connection)
from app_voetbalelo.models.jpl_playoffs import game_data

from app_voetbalelo.models.jpl_playoffs import speeldagen

from app_voetbalelo.models.jpl_playoffs import standings_rs
from app_voetbalelo.models.jpl_playoffs import standings_poi
from app_voetbalelo.models.jpl_playoffs import standings_poii_a
from app_voetbalelo.models.jpl_playoffs import standings_poii_b
from app_voetbalelo.models.jpl_playoffs import standings_poiii

from app_voetbalelo.models.jpl_playoffs import elo_data_rs
from app_voetbalelo.models.jpl_playoffs import elo_data_poi
from app_voetbalelo.models.jpl_playoffs import elo_data_poii_a
from app_voetbalelo.models.jpl_playoffs import elo_data_poii_b
from app_voetbalelo.models.jpl_playoffs import elo_data_poiii

# To make list of lists that are not copies of each other
from itertools import repeat

# To make Google Charts accept Decimal Data
import json
import decimal
import datetime

import numpy as np

# To make sure transition from Django to Template (javascript) is smooth
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def ranking(request):
    competitions = ["rs","poi","poii_a","poii_b","poiii"]
    
    # Get data from DB
    games = game_data.objects.all()
    speeldagen_data = speeldagen.objects.all()
    standard_ranking_rs = standings_rs.objects.all()
    elo_ranking_rs = elo_data_rs.objects.all()
    standard_ranking_poi = standings_poi.objects.all()
    elo_ranking_poi = elo_data_poi.objects.all()
    standard_ranking_poii_a = standings_poii_a.objects.all()
    elo_ranking_poii_a = elo_data_poii_a.objects.all()
    standard_ranking_poii_b = standings_poii_b.objects.all()
    elo_ranking_poii_b = elo_data_poii_b.objects.all()
    standard_ranking_poiii = standings_poiii.objects.all()
    elo_ranking_poiii = elo_data_poiii.objects.all()
    
    # Teams
    teams = dict()
    for competition in competitions:
        teams[competition] = list()
    for i in range(len(standard_ranking_rs.values())):
        teams["rs"].append(standard_ranking_rs.values()[i]["team"])
    for i in range(len(standard_ranking_poi.values())):
        teams["poi"].append(standard_ranking_poi.values()[i]["team"])
    for i in range(len(standard_ranking_poii_a.values())):
        teams["poii_a"].append(standard_ranking_poii_a.values()[i]["team"])
    for i in range(len(standard_ranking_poii_b.values())):
        teams["poii_b"].append(standard_ranking_poii_b.values()[i]["team"])
    for i in range(len(standard_ranking_poiii.values())):
        teams["poiii"].append(standard_ranking_poiii.values()[i]["team"])
    
    # Colors
    colors_all = ["rgb(0, 66, 134)",
            "rgb(83, 41, 148)",
            "rgb(19, 159, 70)",
            "rgb(0, 0, 0)",
            "rgb(0, 122, 187)",
            "rgb(255, 12, 0)",
            "rgb(201, 32, 39)",
            "rgb(255, 227, 0)",
            "rgb(0, 0, 0)",
            "rgb(51, 56, 150)",
            "rgb(0, 146, 67)",
            "rgb(26, 51, 148)",
            "rgb(179, 0, 6)",
            "rgb(253, 208, 50)",
            "rgb(219, 195, 60)",
            "rgb(215, 0, 58)"]
    colors = dict()
    for competition in competitions:
        colors[competition] = list()
    for i in range(len(standard_ranking_rs.values())):
        colors["rs"].append(colors_all[i])
    for i in range(len(standard_ranking_poi.values())):
        for j in range(len(standard_ranking_rs.values())):
            if standard_ranking_poi.values()[i]["team"] == standard_ranking_rs.values()[j]["team"]:
                colors["poi"].append(colors["rs"][j])
                break
    for i in range(len(standard_ranking_poii_a.values())):
        for j in range(len(standard_ranking_rs.values())):
            if standard_ranking_poii_a.values()[i]["team"] == standard_ranking_rs.values()[j]["team"]:
                colors["poii_a"].append(colors["rs"][j])
                break
    for i in range(len(standard_ranking_poii_b.values())):
        for j in range(len(standard_ranking_rs.values())):
            if standard_ranking_poii_b.values()[i]["team"] == standard_ranking_rs.values()[j]["team"]:
                colors["poii_b"].append(colors["rs"][j])
                break
    for i in range(len(standard_ranking_poiii.values())):
        for j in range(len(standard_ranking_rs.values())):
            if standard_ranking_poiii.values()[i]["team"] == standard_ranking_rs.values()[j]["team"]:
                colors["poiii"].append(colors["rs"][j])
                break 

   # teams_rs = {{elo_history_chart.rs | safe}}[0].slice(1);
    
    
    standard_ranking_chart_values = dict()
    elo_table_headers = dict()
    elo_table_values = dict()
    table_headers = dict()
    table_values = dict()
    standard_ranking_chart_headers = ["","","PTN","M","M+", "M-", "M=","D+","D-","D+/-"]
    for competition in competitions:
        standard_ranking_chart_values[competition] = list()
        if competition == "rs":
            elo_ranking = elo_ranking_rs
            number_of_teams = len(elo_ranking_rs)
            values = standard_ranking_rs.values()
        if competition == "poi":
            elo_ranking = elo_ranking_poi
            number_of_teams = len(elo_ranking_poi)
            values = standard_ranking_poi.values()
        if competition == "poii_a":
            elo_ranking = elo_ranking_poii_a
            number_of_teams = len(elo_ranking_poii_a)
            values = standard_ranking_poii_a.values()
        if competition == "poii_b":
            elo_ranking = elo_ranking_poii_b
            number_of_teams = len(elo_ranking_poii_b)
            values = standard_ranking_poii_b.values()
        if competition == "poiii":
            elo_ranking = elo_ranking_poiii
            number_of_teams = len(elo_ranking_poiii)
            values = standard_ranking_poiii.values()
        for i in range(number_of_teams):
            standard_ranking_chart_values[competition].append(list())
            standard_ranking_chart_values[competition][i].append(values[i]["rank"])
            standard_ranking_chart_values[competition][i].append(values[i]["team"])
            standard_ranking_chart_values[competition][i].append(values[i]["points"])
            standard_ranking_chart_values[competition][i].append(values[i]["games"])
            standard_ranking_chart_values[competition][i].append(values[i]["win"])
            standard_ranking_chart_values[competition][i].append(values[i]["loss"])
            standard_ranking_chart_values[competition][i].append(values[i]["tie"])
            standard_ranking_chart_values[competition][i].append(values[i]["goals_for"])
            standard_ranking_chart_values[competition][i].append(values[i]["goals_against"])
            standard_ranking_chart_values[competition][i].append(values[i]["goal_difference"])
        
        elo_table_headers[competition] = list()
        elo_table_values[competition] = [[] for i in repeat(None, number_of_teams)]
    
        for team in range(len(elo_ranking)):
            for name, value in elo_ranking[team].get_fields():
                if name == 'team' or name == 'elo':
                    elo_table_values[competition][team].append(value)
                    if team == 0:
                        elo_table_headers[competition].append(name)
    
        # Combine table data in table_headers and table_values
        table_headers[competition] = standard_ranking_chart_headers + ["ELO"]
        table_values[competition] = list()
        for i in range(number_of_teams):
            table_values[competition].append(list())
            table_values[competition][i] = standard_ranking_chart_values[competition][i] + elo_table_values[competition][i][1:]
    
    # Data for charts (ELO forecasted,ELO history, ranking history, points history)
    forecast_chart = dict()
    history_chart = dict()
    for competition in competitions:
        forecast_chart[competition] = dict()
        history_chart[competition] = dict()
        if competition == "rs":
            number_of_teams = len(elo_ranking_rs)
            speeldagen_totaal = 30
            # elo history
            history_chart[competition]["elo"] = [[] for x in range(speeldagen_totaal+2)]
            history_chart[competition]["ranking"] = [[] for x in range(speeldagen_totaal+2)]
            history_chart[competition]["points"] = [[] for x in range(speeldagen_totaal+2)]
            
            history_chart[competition]["elo"][0].append("speeldag")
            history_chart[competition]["ranking"][0].append("speeldag")
            history_chart[competition]["points"][0].append("speeldag")
            for team in range(number_of_teams):
                for name, value in speeldagen_data[team].get_fields():
                    if name == "team":
                        history_chart[competition]["elo"][0].append(value)
                        history_chart[competition]["ranking"][0].append(value)
                        history_chart[competition]["points"][0].append(value)
                        if team == 0:
                            history_chart[competition]["elo"][1].append("start")
                            history_chart[competition]["ranking"][1].append("start")
                            history_chart[competition]["points"][1].append("start")
                            for i in range(number_of_teams):
                                history_chart[competition]["elo"][1].append(decimal.Decimal(1500))
                                history_chart[competition]["ranking"][1].append(decimal.Decimal(i+1))
                                history_chart[competition]["points"][1].append(decimal.Decimal(0))
                    for speeldag in range(speeldagen_totaal):
                        if team == 0 and name == "team":
                            history_chart[competition]["elo"][speeldag+2].append("speeldag " + str(speeldag+1))
                            history_chart[competition]["ranking"][speeldag+2].append("speeldag " + str(speeldag+1))
                            history_chart[competition]["points"][speeldag+2].append("speeldag " + str(speeldag+1))
                        if name == "elo_rs_speeldag_" + str(speeldag+1):
                            history_chart[competition]["elo"][speeldag+2].append(decimal.Decimal(value))
                        if name == "ranking_rs_speeldag_" + str(speeldag+1):
                            history_chart[competition]["ranking"][speeldag+2].append(decimal.Decimal(value))
                        if name == "points_rs_speeldag_" + str(speeldag+1):
                            history_chart[competition]["points"][speeldag+2].append(decimal.Decimal(value))
                            
        if competition == "poi":
            number_of_teams = len(elo_ranking_poi)
            speeldagen_totaal = 10
            # elo forecast
            forecast_chart[competition] = [[[] for i in repeat(None, number_of_teams+1)] for j in repeat(None, number_of_teams)]
            for team in range(number_of_teams):
                forecast_chart[competition][team][0].append("finish")
                for name, value in elo_ranking_poi[team].get_fields():
                    if name == "team":
                        forecast_chart[competition][team][0].append(value)
                    for league_positions in range(number_of_teams):
                        if name == "finish_" + str(league_positions+1):
                            forecast_chart[competition][team][number_of_teams-league_positions].append(name.strip("finish_"))
                            forecast_chart[competition][team][number_of_teams-league_positions].append(decimal.Decimal(value))
                            
            # history
            history_chart[competition]["elo"] = [[] for x in range(speeldagen_totaal+2)]
            history_chart[competition]["ranking"] = [[] for x in range(speeldagen_totaal+2)]
            history_chart[competition]["points"] = [[] for x in range(speeldagen_totaal+2)]
            
            history_chart[competition]["elo"][0].append("speeldag")
            history_chart[competition]["ranking"][0].append("speeldag")
            history_chart[competition]["points"][0].append("speeldag")
            team_indices = []
            for i in range(len(elo_ranking_poi.values())):
                for j in range(len(speeldagen_data.values())):
                    if elo_ranking_poi.values()[i]["team"] == speeldagen_data.values()[j]["team"]:
                        team_indices.append(j)
            for team in team_indices:
                for name, value in speeldagen_data[team].get_fields():
                    if name == "team":
                        history_chart[competition]["elo"][0].append(value)
                        history_chart[competition]["ranking"][0].append(value)
                        history_chart[competition]["points"][0].append(value)
                        if team == team_indices[0]:
                            history_chart[competition]["elo"][1].append("start PO I")
                            history_chart[competition]["ranking"][1].append("start PO I")
                            history_chart[competition]["points"][1].append("start PO I")
                            for i in range(number_of_teams):
                                for j in range(len(elo_ranking_rs.values())):
                                    if elo_ranking_rs.values()[j]["team"] == elo_ranking_poi.values()[i]["team"]:
                                        history_chart[competition]["elo"][1].append(decimal.Decimal(elo_ranking_rs.values()[j]["elo"]))
                                for j in range(len(standard_ranking_rs.values())):
                                    if standard_ranking_rs.values()[j]["team"] == elo_ranking_poi.values()[i]["team"]:
                                        history_chart[competition]["ranking"][1].append(decimal.Decimal(standard_ranking_rs.values()[j]["rank"]))
                                        history_chart[competition]["points"][1].append(decimal.Decimal(np.ceil(standard_ranking_rs.values()[j]["points"]/2)))
                                        
                    for speeldag in range(speeldagen_totaal):
                        if team == team_indices[0] and name == "team":
                            history_chart[competition]["elo"][speeldag+2].append("PO I speeldag " + str(speeldag+1))
                            history_chart[competition]["ranking"][speeldag+2].append("PO I speeldag " + str(speeldag+1))
                            history_chart[competition]["points"][speeldag+2].append("PO I speeldag " + str(speeldag+1))
                        if name == "elo_poi_speeldag_" + str(speeldag+1):
                            history_chart[competition]["elo"][speeldag+2].append(decimal.Decimal(value))
                        if name == "ranking_poi_speeldag_" + str(speeldag+1):
                            history_chart[competition]["ranking"][speeldag+2].append(decimal.Decimal(value))
                        if name == "points_poi_speeldag_" + str(speeldag+1):
                            history_chart[competition]["points"][speeldag+2].append(decimal.Decimal(value))
                    
            # Remove 0's and replace with zero length string
            for speeldag in range(speeldagen_totaal):
                if sum(history_chart[competition]["elo"][speeldag+2][1:]) == 0:
                    history_chart[competition]["elo"][speeldag+2][1:] = ['nan']*len(history_chart[competition]["elo"][speeldag+2][1:])
                    history_chart[competition]["ranking"][speeldag+2][1:] = ['nan']*len(history_chart[competition]["ranking"][speeldag+2][1:])
                    history_chart[competition]["points"][speeldag+2][1:] = ['nan']*len(history_chart[competition]["points"][speeldag+2][1:])
                    
            # Expand history with rs data
            elo_history_chart_rs = [[] for x in range(len(history_chart["rs"]["elo"]))]
            ranking_history_chart_rs = [[] for x in range(len(history_chart["rs"]["ranking"]))]
            points_history_chart_rs = [[] for x in range(len(history_chart["rs"]["points"]))]
            for team_po in range(len(history_chart[competition]["elo"][0])):
                for team_rs in range(len(history_chart["rs"]["elo"][0])):
                    if history_chart["rs"]["elo"][0][team_rs] == history_chart[competition]["elo"][0][team_po]:
                        for i in range(len(elo_history_chart_rs)):
                            elo_history_chart_rs[i].append(history_chart["rs"]["elo"][i][team_rs])
                            ranking_history_chart_rs[i].append(history_chart["rs"]["ranking"][i][team_rs])
                            points_history_chart_rs[i].append(history_chart["rs"]["points"][i][team_rs])
                        break
                
            for i in range(len(elo_history_chart_rs)-1):
                history_chart[competition]["elo"].insert(i+1,elo_history_chart_rs[i+1])
                history_chart[competition]["ranking"].insert(i+1,ranking_history_chart_rs[i+1])
                history_chart[competition]["points"].insert(i+1,points_history_chart_rs[i+1])
            
        if competition == "poii_a":
            number_of_teams = len(elo_ranking_poii_a)
            speeldagen_totaal = 6
            # elo forecast
            forecast_chart[competition] = [[[] for i in repeat(None, number_of_teams+1)] for j in repeat(None, number_of_teams)]
            for team in range(number_of_teams):
                forecast_chart[competition][team][0].append("finish")
                for name, value in elo_ranking_poii_a[team].get_fields():
                    if name == "team":
                        forecast_chart[competition][team][0].append(value)
                    for league_positions in range(number_of_teams):
                        if name == "finish_" + str(league_positions+1):
                            forecast_chart[competition][team][number_of_teams-league_positions].append(name.strip("finish_"))
                            forecast_chart[competition][team][number_of_teams-league_positions].append(decimal.Decimal(value))
                            
            # history
            history_chart[competition]["elo"] = [[] for x in range(speeldagen_totaal+2)]
            history_chart[competition]["ranking"] = [[] for x in range(speeldagen_totaal+2)]
            history_chart[competition]["points"] = [[] for x in range(speeldagen_totaal+2)]
            
            history_chart[competition]["elo"][0].append("speeldag")
            history_chart[competition]["ranking"][0].append("speeldag")
            history_chart[competition]["points"][0].append("speeldag")
            team_indices = []
            for i in range(len(elo_ranking_poii_a.values())):
                for j in range(len(speeldagen_data.values())):
                    if elo_ranking_poii_a.values()[i]["team"] == speeldagen_data.values()[j]["team"]:
                        team_indices.append(j)
            for team in team_indices:
                for name, value in speeldagen_data[team].get_fields():
                    if name == "team":
                        history_chart[competition]["elo"][0].append(value)
                        history_chart[competition]["ranking"][0].append(value)
                        history_chart[competition]["points"][0].append(value)
                        if team == team_indices[0]:
                            history_chart[competition]["elo"][1].append("start PO II a")
                            history_chart[competition]["ranking"][1].append("start PO II a")
                            history_chart[competition]["points"][1].append("start PO II a")
                            for i in range(number_of_teams):
                                for j in range(len(elo_ranking_rs.values())):
                                    if elo_ranking_rs.values()[j]["team"] == elo_ranking_poii_a.values()[i]["team"]:
                                        history_chart[competition]["elo"][1].append(decimal.Decimal(elo_ranking_rs.values()[j]["elo"]))
                                history_chart[competition]["ranking"][1].append(decimal.Decimal(i+1))
                                history_chart[competition]["points"][1].append(decimal.Decimal(0))
                                
                    for speeldag in range(speeldagen_totaal):
                        if team == team_indices[0] and name == "team":
                            history_chart[competition]["elo"][speeldag+2].append("PO II a speeldag " + str(speeldag+1))
                            history_chart[competition]["ranking"][speeldag+2].append("PO II a speeldag " + str(speeldag+1))
                            history_chart[competition]["points"][speeldag+2].append("PO II a speeldag " + str(speeldag+1))
                        if name == "elo_poii_a_speeldag_" + str(speeldag+1):
                            history_chart[competition]["elo"][speeldag+2].append(decimal.Decimal(value))
                        if name == "ranking_poii_a_speeldag_" + str(speeldag+1):
                            history_chart[competition]["ranking"][speeldag+2].append(decimal.Decimal(value))
                        if name == "points_poii_a_speeldag_" + str(speeldag+1):
                            history_chart[competition]["points"][speeldag+2].append(decimal.Decimal(value))
                            
            # Remove 0's and replace with zero length string
            for speeldag in range(speeldagen_totaal):
                if sum(history_chart[competition]["elo"][speeldag+2][1:]) == 0:
                    history_chart[competition]["elo"][speeldag+2][1:] = ['nan']*len(history_chart[competition]["elo"][speeldag+2][1:])
                    history_chart[competition]["ranking"][speeldag+2][1:] = ['nan']*len(history_chart[competition]["ranking"][speeldag+2][1:])
                    history_chart[competition]["points"][speeldag+2][1:] = ['nan']*len(history_chart[competition]["points"][speeldag+2][1:])
                    
            # Expand history with rs data
            elo_history_chart_rs = [[] for x in range(len(history_chart["rs"]["elo"]))]
            ranking_history_chart_rs = [[] for x in range(len(history_chart["rs"]["ranking"]))]
            points_history_chart_rs = [[] for x in range(len(history_chart["rs"]["points"]))]
            for team_po in range(len(history_chart[competition]["elo"][0])):
                for team_rs in range(len(history_chart["rs"]["elo"][0])):
                    if history_chart["rs"]["elo"][0][team_rs] == history_chart[competition]["elo"][0][team_po]:
                        for i in range(len(elo_history_chart_rs)):
                            elo_history_chart_rs[i].append(history_chart["rs"]["elo"][i][team_rs])
                            ranking_history_chart_rs[i].append(history_chart["rs"]["ranking"][i][team_rs])
                            points_history_chart_rs[i].append(history_chart["rs"]["points"][i][team_rs])
                        break
                
            for i in range(len(elo_history_chart_rs)-1):
                history_chart[competition]["elo"].insert(i+1,elo_history_chart_rs[i+1])
                history_chart[competition]["ranking"].insert(i+1,ranking_history_chart_rs[i+1])
                history_chart[competition]["points"].insert(i+1,points_history_chart_rs[i+1])
    
        if competition == "poii_b":
            number_of_teams = len(elo_ranking_poii_b)
            speeldagen_totaal = 6
            # elo forecast
            forecast_chart[competition] = [[[] for i in repeat(None, number_of_teams+1)] for j in repeat(None, number_of_teams)]
            for team in range(number_of_teams):
                forecast_chart[competition][team][0].append("finish")
                for name, value in elo_ranking_poii_b[team].get_fields():
                    if name == "team":
                        forecast_chart[competition][team][0].append(value)
                    for league_positions in range(number_of_teams):
                        if name == "finish_" + str(league_positions+1):
                            forecast_chart[competition][team][number_of_teams-league_positions].append(name.strip("finish_"))
                            forecast_chart[competition][team][number_of_teams-league_positions].append(decimal.Decimal(value))
                            
            # history
            history_chart[competition]["elo"] = [[] for x in range(speeldagen_totaal+2)]
            history_chart[competition]["ranking"] = [[] for x in range(speeldagen_totaal+2)]
            history_chart[competition]["points"] = [[] for x in range(speeldagen_totaal+2)]
            
            history_chart[competition]["elo"][0].append("speeldag")
            history_chart[competition]["ranking"][0].append("speeldag")
            history_chart[competition]["points"][0].append("speeldag")
            team_indices = []
            for i in range(len(elo_ranking_poii_b.values())):
                for j in range(len(speeldagen_data.values())):
                    if elo_ranking_poii_b.values()[i]["team"] == speeldagen_data.values()[j]["team"]:
                        team_indices.append(j)
            for team in team_indices:
                for name, value in speeldagen_data[team].get_fields():
                    if name == "team":
                        history_chart[competition]["elo"][0].append(value)
                        history_chart[competition]["ranking"][0].append(value)
                        history_chart[competition]["points"][0].append(value)
                        if team == team_indices[0]:
                            history_chart[competition]["elo"][1].append("start PO II b")
                            history_chart[competition]["ranking"][1].append("start PO II b")
                            history_chart[competition]["points"][1].append("start PO II b")
                            for i in range(number_of_teams):
                                for j in range(len(elo_ranking_rs.values())):
                                    if elo_ranking_rs.values()[j]["team"] == elo_ranking_poii_b.values()[i]["team"]:
                                        history_chart[competition]["elo"][1].append(decimal.Decimal(elo_ranking_rs.values()[j]["elo"]))
                                history_chart[competition]["ranking"][1].append(decimal.Decimal(i+1))
                                history_chart[competition]["points"][1].append(decimal.Decimal(0))
    
                    for speeldag in range(speeldagen_totaal):
                        if team == team_indices[0] and name == "team":
                            history_chart[competition]["elo"][speeldag+2].append("PO II b speeldag " + str(speeldag+1))
                            history_chart[competition]["ranking"][speeldag+2].append("PO II b speeldag " + str(speeldag+1))
                            history_chart[competition]["points"][speeldag+2].append("PO II b speeldag " + str(speeldag+1))
                        if name == "elo_poii_b_speeldag_" + str(speeldag+1):
                            history_chart[competition]["elo"][speeldag+2].append(decimal.Decimal(value))
                        if name == "ranking_poii_b_speeldag_" + str(speeldag+1):
                            history_chart[competition]["ranking"][speeldag+2].append(decimal.Decimal(value))
                        if name == "points_poii_b_speeldag_" + str(speeldag+1):
                            history_chart[competition]["points"][speeldag+2].append(decimal.Decimal(value))
                            
            # Remove 0's and replace with zero length string
            for speeldag in range(speeldagen_totaal):
                if sum(history_chart[competition]["elo"][speeldag+2][1:]) == 0:
                    history_chart[competition]["elo"][speeldag+2][1:] = ['nan']*len(history_chart[competition]["elo"][speeldag+2][1:])
                    history_chart[competition]["ranking"][speeldag+2][1:] = ['nan']*len(history_chart[competition]["ranking"][speeldag+2][1:])
                    history_chart[competition]["points"][speeldag+2][1:] = ['nan']*len(history_chart[competition]["points"][speeldag+2][1:])
                    
            # Expand history with rs data
            elo_history_chart_rs = [[] for x in range(len(history_chart["rs"]["elo"]))]
            ranking_history_chart_rs = [[] for x in range(len(history_chart["rs"]["ranking"]))]
            points_history_chart_rs = [[] for x in range(len(history_chart["rs"]["points"]))]
            for team_po in range(len(history_chart[competition]["elo"][0])):
                for team_rs in range(len(history_chart["rs"]["elo"][0])):
                    if history_chart["rs"]["elo"][0][team_rs] == history_chart[competition]["elo"][0][team_po]:
                        for i in range(len(elo_history_chart_rs)):
                            elo_history_chart_rs[i].append(history_chart["rs"]["elo"][i][team_rs])
                            ranking_history_chart_rs[i].append(history_chart["rs"]["ranking"][i][team_rs])
                            points_history_chart_rs[i].append(history_chart["rs"]["points"][i][team_rs])
                        break
                
            for i in range(len(elo_history_chart_rs)-1):
                history_chart[competition]["elo"].insert(i+1,elo_history_chart_rs[i+1])
                history_chart[competition]["ranking"].insert(i+1,ranking_history_chart_rs[i+1])
                history_chart[competition]["points"].insert(i+1,points_history_chart_rs[i+1])
                            
        if competition == "poiii":
            number_of_teams = len(elo_ranking_poiii)
            speeldagen_totaal = 5
            # elo forecast
            forecast_chart[competition] = [[[] for i in repeat(None, number_of_teams+1)] for j in repeat(None, number_of_teams)]
            for team in range(number_of_teams):
                forecast_chart[competition][team][0].append("finish")
                for name, value in elo_ranking_poiii[team].get_fields():
                    if name == "team":
                        forecast_chart[competition][team][0].append(value)
                    for league_positions in range(number_of_teams):
                        if name == "finish_" + str(league_positions+1):
                            forecast_chart[competition][team][number_of_teams-league_positions].append(name.strip("finish_"))
                            forecast_chart[competition][team][number_of_teams-league_positions].append(decimal.Decimal(value))
                            
            # history
            history_chart[competition]["elo"] = [[] for x in range(speeldagen_totaal+2)]
            history_chart[competition]["ranking"] = [[] for x in range(speeldagen_totaal+2)]
            history_chart[competition]["points"] = [[] for x in range(speeldagen_totaal+2)]
            
            history_chart[competition]["elo"][0].append("speeldag")
            history_chart[competition]["ranking"][0].append("speeldag")
            history_chart[competition]["points"][0].append("speeldag")
            team_indices = []
            for i in range(len(elo_ranking_poiii.values())):
                for j in range(len(speeldagen_data.values())):
                    if elo_ranking_poiii.values()[i]["team"] == speeldagen_data.values()[j]["team"]:
                        team_indices.append(j)
            for team in team_indices:
                for name, value in speeldagen_data[team].get_fields():
                    if name == "team":
                        history_chart[competition]["elo"][0].append(value)
                        history_chart[competition]["ranking"][0].append(value)
                        history_chart[competition]["points"][0].append(value)
                        if team == team_indices[0]:
                            history_chart[competition]["elo"][1].append("start PO III")
                            history_chart[competition]["ranking"][1].append("start PO III")
                            history_chart[competition]["points"][1].append("start PO III")
                            for i in range(number_of_teams):
                                for j in range(len(elo_ranking_rs.values())):
                                    if elo_ranking_rs.values()[j]["team"] == elo_ranking_poiii.values()[i]["team"]:
                                        history_chart[competition]["elo"][1].append(decimal.Decimal(elo_ranking_rs.values()[j]["elo"]))
                                    if standard_ranking_rs.values()[j]["team"] == elo_ranking_poiii.values()[i]["team"]:
                                        if standard_ranking_rs.values()[j]["rank"] == 15:
                                            history_chart[competition]["ranking"][1].append(decimal.Decimal(1))
                                            history_chart[competition]["points"][1].append(decimal.Decimal(3))
                                        else:
                                            history_chart[competition]["ranking"][1].append(decimal.Decimal(2))
                                            history_chart[competition]["points"][1].append(decimal.Decimal(0))
    
                    for speeldag in range(speeldagen_totaal):
                        if team == team_indices[0] and name == "team":
                            history_chart[competition]["elo"][speeldag+2].append("PO III speeldag " + str(speeldag+1))
                            history_chart[competition]["ranking"][speeldag+2].append("PO III speeldag " + str(speeldag+1))
                            history_chart[competition]["points"][speeldag+2].append("PO III speeldag " + str(speeldag+1))
                        if name == "elo_poiii_speeldag_" + str(speeldag+1):
                            history_chart[competition]["elo"][speeldag+2].append(decimal.Decimal(value))
                        if name == "ranking_poiii_speeldag_" + str(speeldag+1):
                            history_chart[competition]["ranking"][speeldag+2].append(decimal.Decimal(value))
                        if name == "points_poiii_speeldag_" + str(speeldag+1):
                            history_chart[competition]["points"][speeldag+2].append(decimal.Decimal(value))
    
            # Remove 0's and replace with zero length string
            for speeldag in range(speeldagen_totaal):
                if sum(history_chart[competition]["elo"][speeldag+2][1:]) == 0:
                    history_chart[competition]["elo"][speeldag+2][1:] = ['nan']*len(history_chart[competition]["elo"][speeldag+2][1:])
                    history_chart[competition]["ranking"][speeldag+2][1:] = ['nan']*len(history_chart[competition]["ranking"][speeldag+2][1:])
                    history_chart[competition]["points"][speeldag+2][1:] = ['nan']*len(history_chart[competition]["points"][speeldag+2][1:])
                    
                    
            # Expand history with rs data
            elo_history_chart_rs = [[] for x in range(len(history_chart["rs"]["elo"]))]
            ranking_history_chart_rs = [[] for x in range(len(history_chart["rs"]["ranking"]))]
            points_history_chart_rs = [[] for x in range(len(history_chart["rs"]["points"]))]
            for team_po in range(len(history_chart[competition]["elo"][0])):
                for team_rs in range(len(history_chart["rs"]["elo"][0])):
                    if history_chart["rs"]["elo"][0][team_rs] == history_chart[competition]["elo"][0][team_po]:
                        for i in range(len(elo_history_chart_rs)):
                            elo_history_chart_rs[i].append(history_chart["rs"]["elo"][i][team_rs])
                            ranking_history_chart_rs[i].append(history_chart["rs"]["ranking"][i][team_rs])
                            points_history_chart_rs[i].append(history_chart["rs"]["points"][i][team_rs])
                        break
                
            for i in range(len(elo_history_chart_rs)-1):
                history_chart[competition]["elo"].insert(i+1,elo_history_chart_rs[i+1])
                history_chart[competition]["ranking"].insert(i+1,ranking_history_chart_rs[i+1])
                history_chart[competition]["points"].insert(i+1,points_history_chart_rs[i+1])
                
    # Upcoming games
    upcoming_games_values = dict()
    upcoming_games_headers = ["","","", "","M+", "M=", "M-"]
    speeldagen_dict = dict()
    speeldagen_dict["rs"] = 30
    speeldagen_dict["poi"] = 10
    speeldagen_dict["poii_a"] = 6
    speeldagen_dict["poii_b"] = 6
    speeldagen_dict["poiii"] = 5
    teams_dict = dict()
    teams_dict["rs"] = 16
    teams_dict["poi"] = 6
    teams_dict["poii_a"] = 4
    teams_dict["poii_b"] = 4
    teams_dict["poiii"] = 2
    # Find actual speeldag
    speeldagen_act_dict = dict()
    for competition in competitions:
        if competition is not "rs":
            games_dummy = games.filter(competition=competition).filter(game_date__gte = datetime.datetime.now())
            if len(games_dummy) % (teams_dict[competition]/2) == 0:
                speeldagen_act_dict[competition] = (speeldagen_dict[competition]*(teams_dict[competition]/2) - len(games_dummy))/(teams_dict[competition]/2) + 1 
            else:
                speeldagen_act_dict[competition] = np.ceil((speeldagen_dict[competition]*(teams_dict[competition]/2) - len(games_dummy))/(teams_dict[competition]/2))
            
    for competition in competitions:
        if competition is not "rs":
            upcoming_games_values[competition] = list()
            for speeldag in range(speeldagen_dict[competition]):
                
                games_dummy = games.filter(competition=competition).filter(speeldag = competition + " " + str(speeldag+1))
                upcoming_games_values[competition].append(list())
                for game in range(len(games_dummy)):
                    upcoming_games_values[competition][speeldag].append(list())
                    
                    upcoming_games_values[competition][speeldag][game].append(games_dummy.values()[game]["game_date"].strftime("%d/%m")) #  %H:%M
                    upcoming_games_values[competition][speeldag][game].append(games_dummy.values()[game]["host"])
                    # Result
                    upcoming_games_values[competition][speeldag][game].append(games_dummy.values()[game]["host_goal"] + " - " + games_dummy.values()[game]["visitor_goal"])
                    upcoming_games_values[competition][speeldag][game].append(games_dummy.values()[game]["visitor"])
                    upcoming_games_values[competition][speeldag][game].append(str(round(100*games_dummy.values()[game]["host_win"],0)) + "%")
                    upcoming_games_values[competition][speeldag][game].append(str(round(100*games_dummy.values()[game]["tie"],0)) + "%")
                    upcoming_games_values[competition][speeldag][game].append(str(round(100*games_dummy.values()[game]["visitor_win"],0)) + "%")
                
    # Django to Javascript gives problems
    # Therefore, convert using jsonEncoder!
    # Do this for every team separate, otherwise problems!
    for competition in competitions:
        history_chart[competition]["elo"] = json.dumps(history_chart[competition]["elo"], cls=DecimalEncoder) 
        history_chart[competition]["ranking"] = json.dumps(history_chart[competition]["ranking"], cls=DecimalEncoder)  
        history_chart[competition]["points"] = json.dumps(history_chart[competition]["points"], cls=DecimalEncoder)  
        if competition is not "rs":
            for team in range(len(forecast_chart[competition])):
                forecast_chart[competition][team] = json.dumps(forecast_chart[competition][team], cls=DecimalEncoder)
                
    # categories
    categories = ["elo","ranking","points"]
    context_dict = {'categories':categories,'teams':teams,'colors':colors,'competitions':competitions,'speeldagen':speeldagen_dict, 'table_headers' : table_headers,'table_values' : table_values,'forecast_chart':forecast_chart,'history_chart':history_chart, 'upcoming_games_headers':upcoming_games_headers,'upcoming_games_values':upcoming_games_values, 'speeldag_actueel': speeldagen_act_dict}

    return render(request, 'apps/app_voetbalelo/jpl_playoffs/ranking.html', context_dict)
