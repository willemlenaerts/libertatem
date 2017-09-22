import pickle           
destandaard = pickle.load(open("app_sentiment/bdw/input_data/1995Januari1-2015Mei24_Bart De Wever_De Standaard.p", "rb"))
demorgen = pickle.load(open("app_sentiment/bdw/input_data/1995Januari1-2015Mei24_Bart De Wever_De Morgen.p", "rb"))
detijd = pickle.load(open("app_sentiment/bdw/input_data/1995Januari1-2015Mei24_Bart De Wever_De Tijd.p", "rb"))
hetlaatstenieuws = pickle.load(open("app_sentiment/bdw/input_data/1995Januari1-2015Mei24_Bart De Wever_Het Laatste Nieuws.p", "rb"))
humo = pickle.load(open("app_sentiment/bdw/input_data/1995Januari1-2015Mei24_Bart De Wever_Humo.p", "rb"))
lesoir = pickle.load(open("app_sentiment/bdw/input_data/1995Januari1-2015Mei24_Bart De Wever_Le Soir.p", "rb"))

artikels = destandaard+demorgen+detijd+hetlaatstenieuws+humo+lesoir

# Data cleaning
# Datum string
import datetime
for artikel in artikels:
    if artikel["datum"].split(" ")[2] == "Jan." or artikel["datum"].split(" ")[2] == "Jan":
        maand = "01"
    elif artikel["datum"].split(" ")[2] == "Feb." or artikel["datum"].split(" ")[2] == "Feb":
        maand = "02"
    elif artikel["datum"].split(" ")[2] == "Maa." or artikel["datum"].split(" ")[2] == "Maa" or artikel["datum"].split(" ")[2] == "Mar.":
        maand = "03"
    elif artikel["datum"].split(" ")[2] == "Apr." or artikel["datum"].split(" ")[2] == "Apr":
        maand = "04"
    elif artikel["datum"].split(" ")[2] == "Mei." or artikel["datum"].split(" ")[2] == "Mei":
        maand = "05"
    elif artikel["datum"].split(" ")[2] == "Jun." or artikel["datum"].split(" ")[2] == "Jun":
        maand = "06"
    elif artikel["datum"].split(" ")[2] == "Jul." or artikel["datum"].split(" ")[2] == "Jul":
        maand = "07"
    elif artikel["datum"].split(" ")[2] == "Aug." or artikel["datum"].split(" ")[2] == "Aug":
        maand = "08"
    elif artikel["datum"].split(" ")[2] == "Sep." or artikel["datum"].split(" ")[2] == "Sep":
        maand = "09"
    elif artikel["datum"].split(" ")[2] == "Okt." or artikel["datum"].split(" ")[2] == "Okt":
        maand = "10"
    elif artikel["datum"].split(" ")[2] == "Nov." or artikel["datum"].split(" ")[2] == "Nov":
        maand = "11"
    elif artikel["datum"].split(" ")[2] == "Dec." or artikel["datum"].split(" ")[2] == "Dec":
        maand = "12"
        
    artikel["datum"] = artikel["datum"].split(" ")[1] + "/" + maand + "/" + artikel["datum"].split(" ")[3]
    artikel["datum"] = datetime.datetime.strptime(artikel["datum"], "%d/%m/%Y")

# Publicatie
for artikel in artikels:
    if "De Standaard" in artikel["publicatie"]:
        artikel["publicatie"] = "De Standaard"
    elif "De Morgen" in artikel["publicatie"]:
        artikel["publicatie"] = "De Morgen"
    elif "De Tijd" in artikel["publicatie"]:
        artikel["publicatie"] = "De Tijd"
    elif "Het Laatste Nieuws" in artikel["publicatie"]:
        artikel["publicatie"] = "Het Laatste Nieuws"
    elif "Humo" in artikel["publicatie"]:
        artikel["publicatie"] = "Humo"
    elif "Le Soir" in artikel["publicatie"]:
        artikel["publicatie"] = "Le Soir"
        
import pandas as pd
panda = pd.DataFrame(artikels)

# Set datum column as index
panda.datum = pd.to_datetime(panda.datum)
panda = panda.set_index("datum")
panda = panda.sort_index()

# Histogram (per week groeperen)
def perdelta(start, end, delta):
    l = []
    curr = start-delta
    while curr < end:
        l.append(curr)
        curr += delta
    l.append(curr)
    
    return l
date_interval = perdelta(panda.index[0], panda.index[-1], datetime.timedelta(days=7))

volume = dict()
volume["alles"] = []
volume["destandaard"] = []
volume["demorgen"] = []
volume["detijd"] = []
volume["hetlaatstenieuws"] = []
volume["humo"] = []
volume["lesoir"] = []
volume["datum"] = []
for i in range(len(date_interval)-1):
    volume["datum"].append(date_interval[i+1].value/1000000)
    volume["alles"].append(len(panda[(panda.index > date_interval[i]) & (panda.index <= date_interval[i+1])]))
    volume["destandaard"].append(len(panda[(panda.index > date_interval[i]) & (panda.index <= date_interval[i+1]) & (panda.publicatie == "De Standaard")]))
    volume["demorgen"].append(len(panda[(panda.index > date_interval[i]) & (panda.index <= date_interval[i+1]) & (panda.publicatie == "De Morgen")]))
    volume["detijd"].append(len(panda[(panda.index > date_interval[i]) & (panda.index <= date_interval[i+1]) & (panda.publicatie == "De Tijd")]))
    volume["hetlaatstenieuws"].append(len(panda[(panda.index > date_interval[i]) & (panda.index <= date_interval[i+1]) & (panda.publicatie == "Het Laatste Nieuws")]))
    volume["humo"].append(len(panda[(panda.index > date_interval[i]) & (panda.index <= date_interval[i+1]) & (panda.publicatie == "Humo")]))
    volume["lesoir"].append(len(panda[(panda.index > date_interval[i]) & (panda.index <= date_interval[i+1]) & (panda.publicatie == "Le Soir")]))

# Save
pickle.dump(volume,open("app_sentiment/bdw/results/histogram.p", "wb"))