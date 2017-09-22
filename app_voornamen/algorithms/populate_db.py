# Import volgende packages
import time
import xlrd

# Return dictionary
return_data = dict()


# Open bestand
print("Open bestand...")

from exergos.settings import BASE_DIR
import os
path = os.path.join(BASE_DIR, "app_voornamen/data/voornamen.xls")
voornamen = xlrd.open_workbook(path)

# Open alle sheets
sheets = ["mannen","vrouwen"]
for i in range(len(sheets)): 
    print("Lees " + sheets[i] + " Data (" + str(i+1) + "/" + str(len(sheets)) + ")")
    sheet = voornamen.sheet_by_name(sheets[i])
    num_rows = sheet.nrows
    num_cols = sheet.ncols
    
    # print(sheet.cell_value(0, num_cols))
    # # print(num_rows)
    
    header = []
    data = []
    for curr_col in range(num_cols):
        header.append(list())
        header[-1].append(sheet.cell_value(0, curr_col))
        header[-1].append(sheet.cell_value(1, curr_col))
        header[-1].append(sheet.cell_value(2, curr_col))
        if type(header[-1][2]) is not str:
            header[-1][2] = str(int(header[-1][2]))
        data.append(list())
        # sim_start = time.time()
        for curr_row in range(num_rows-3):
            data[curr_col].append(sheet.cell_value(curr_row+3, curr_col))
        # sim_end = time.time()
        # print('One column in ' +  str(round(sim_end - sim_start,0)) + ' seconds')
    # print(header)
    # print(data[1][0:10000])

    # Vul return dictionary met key en data
    j=0
    while j < len(header):
        if header[j][0] not in return_data:
            return_data[header[j][0]] = dict()
        if header[j][1] not in return_data[header[j][0]]:
            return_data[header[j][0]][header[j][1]] = dict()
            
        return_data[header[j][0]][header[j][1]][header[j][2]] = list([data[j],data[j+1],data[j+2]])

        j = j+3

# Creëer de dict die alle data omvat
voornamen = return_data

# Verwijder alle ""
for key_1 in voornamen:
    for key_2 in voornamen[key_1]:
        for key_3 in voornamen[key_1][key_2]:
            for i in range(len(voornamen[key_1][key_2][key_3][1])):
                if voornamen[key_1][key_2][key_3][1][i] == "":
                    voornamen[key_1][key_2][key_3][0] = voornamen[key_1][key_2][key_3][0][0:i]
                    voornamen[key_1][key_2][key_3][1] = voornamen[key_1][key_2][key_3][1][0:i]
                    voornamen[key_1][key_2][key_3][2] = voornamen[key_1][key_2][key_3][2][0:i]
                    break

# Creëer alle_voornamen, een lijst die alle unieke voornamen bevat
alle_voornamen = list()
for key_1 in voornamen:
    for key_2 in voornamen[key_1]:
        for key_3 in voornamen[key_1][key_2]:
            for i in range(len(voornamen[key_1][key_2][key_3][0])):
                if voornamen[key_1][key_2][key_3][0][i] is not "":
                    alle_voornamen.append(voornamen[key_1][key_2][key_3][1][i])

alle_voornamen = list(set(alle_voornamen))

# Populate db
# This file will populate the database
# This command will generate SQL script to populate database somewhere else:

print("Starting database population script")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exergos.settings')
import app_voornamen.models

# Remove previous data in table
import django
django.setup()

# Voor elke tab
d = dict()
from django.contrib.contenttypes.models import ContentType
from django.db.models import get_model
for key_1 in voornamen:
    for key_2 in voornamen[key_1]:
        for key_3 in voornamen[key_1][key_2]:
            # Selecteer juiste tabel in database
            table_name = key_1 + "_" + key_2 + "_" + key_3
            
            print("Vullen tabel " + table_name)
            model_object = get_model("app_voornamen",table_name)
            for i in range(len(voornamen[key_1][key_2][key_3][0])):
                if voornamen[key_1][key_2][key_3][0][i] is not "":
                    d["Rang"] = int(voornamen[key_1][key_2][key_3][0][i])
                    d["Voornaam"] = voornamen[key_1][key_2][key_3][1][i]
                    d["Aantal"] = int(voornamen[key_1][key_2][key_3][2][i])
                    
                    model_object.objects.create(**d)

# Vul alle_voornamen
from app_voornamen.models import voornamen_lijst
d = dict()
for i in range(len(alle_voornamen)):
    d["Voornaam"] = alle_voornamen[i]
    voornamen_lijst.objects.create(**d)