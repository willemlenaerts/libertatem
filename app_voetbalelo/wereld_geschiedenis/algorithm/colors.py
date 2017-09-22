import pickle
import json

countries = pickle.load(open("app_voetbalelo/wereld_geschiedenis/algorithm/data/countries.p","rb"))

national_team_colors_text = open("app_voetbalelo/wereld_geschiedenis/algorithm/data/National Team Colors.txt","r")
national_team_colors = dict()

national_team_colors_text_string = national_team_colors_text.read().split("\n")
for row in national_team_colors_text_string:
    # print(row[:1])
    if row[0] != "\t" and row[0] != "\ufeff" and row[:2] != "Te":
        dummy = row.split(",")
        national_team_colors[dummy[0]] = dummy[1].lstrip().split(" & ")[0]

colors = dict()
problems = list()
color_list = []
for country in countries:
    if country in national_team_colors.keys():
        colors[country] = national_team_colors[country].split("\t")[0]
        color_list.append(colors[country])
    else:
        problems.append(country)
        
        
list(set(color_list))
color_list = {'Dark green': "rgba(0,100,0,1)",
                 'Brown': "rgba(139,69,19,1)" ,
                 'Turquoise': "rgba(0,206,209,1)",
                 'Purple': "rgba(147,112,219,1)",
                 'Marine blue': "rgba(30,144,255,1)",
                 'Yellow': "rgba(255,200,0,1)",
                 'Orange': "rgba(255,140,0,1)",
                 'Red': "rgba(178,34,34,1)",
                 'Dark blue': "rgba(0,0,128,1)",
                 'Green': "rgba(34,139,34,1)",
                 'Black': "rgba(0,0,0,1)",
                 'All blue': "rgba(65,105,225,1)",
                 'Carmine red': "rgba(165,42,42,1)",
                 'Claret': "rgba(127,23,52,1)" ,
                 'Blue': "rgba(65,105,225,1)",
                 'Sky blue': "rgba(100,149,237,1)",
                 'Grey': "rgba(139,134,130,1)",
                 'Sky Blue': "rgba(100,149,237,1)"}

for country in countries:
    colors[country] = color_list[colors[country]]
    
json.dump(colors,open("app_voetbalelo/wereld_geschiedenis/algorithm/results/json.dump/colors.json","w"))