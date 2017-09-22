from django.shortcuts import render
# Create your views here.
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound
from django.http import HttpResponse

# Import models to use in website (database - site connection)

# Import forms
from app_voornamen import forms
from app_voornamen.models import voornamen_lijst

# Access database tables based on variable string concatenation
from django.db.models import get_model
import json

# keys
keys_1 = ["m","v"]
keys_2 = ["vl","br","wal","be"]
keys_3 = ["18","18_65","65","alles"]
# Create your views here.
def index(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = forms.NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            name = form.cleaned_data['name']
            birthyear = form.cleaned_data['birthyear']
            gender = form.cleaned_data['gender']
            location = form.cleaned_data['location']
            
            # Get names from database to use autocomplete:
            namen_db = voornamen_lijst.objects.all().values_list("Voornaam")
            namen = list()
            for i in range(len(namen_db)):
                namen.append(namen_db[i][0])
            
            # Get data
            if gender == "man":
                key_1 = "m"
            else:
                key_1 = "v"
            
            if location == "belgië":
                key_2 = "be"
            elif location == "vlaanderen":
                key_2 = "vl"
            elif location == "brussel":
                key_2 = "br"
            else:
                key_2 = "wal"
                
            if 2015 - int(birthyear) <= 18:
                key_3 = "18";
            elif 2015- int(birthyear) < 65:
                key_3 = "18_65";
            else:
                key_3 = "65";
            
            # First, check if name exists in table
            table_name = key_1 + "_" + key_2 + "_" + key_3
            model_object = get_model("app_voornamen",table_name)
            try:
                data_name = model_object.objects.filter(Voornaam=name)
                rang = data_name.values()[0]["Rang"]
            except IndexError:
                rang = 0
            
            # # If rang = 0, return name not found
            # if rang == 0:
            #     return HttpResponseNotFound('<h1>Page not found</h1>')
            
            # Voorkomen in elke locatie en leeftijdscategorie
            aantal_matrix = []
            count = 0
            for key_2_option in keys_2:
                aantal_matrix.append([])
                for key_3_option in keys_3:
                    table_name = key_1 + "_" + key_2_option + "_" + key_3_option
                    model_object = get_model("app_voornamen",table_name)
                    data_name = model_object.objects.filter(Voornaam=name)
                    if len(data_name) == 0:
                        aantal_matrix[count].append(0)
                    else:
                        aantal_matrix[count].append(data_name.values()[0]["Aantal"])
                count = count + 1
                    
            table_name = key_1 + "_" + key_2 + "_alles"
            model_object = get_model("app_voornamen",table_name)
            data_name = model_object.objects.filter(Voornaam=name)
            if len(data_name) == 0:
                aantal = 0
                rang_alles = 0
            else:
                aantal = data_name.values()[0]["Aantal"]
                rang_alles = data_name.values()[0]["Rang"]
            
            # Voornaam in andere location
            voornamen_location = []
            locations = []
            for key_2_option in keys_2:
                table_name = key_1 + "_" + key_2_option + "_" + key_3
                model_object = get_model("app_voornamen",table_name)
                data_name = model_object.objects.filter(Rang=rang)
                if len(data_name) == 0:
                    voornamen_location.append("")
                    locations.append(key_2_option)
                else:
                    voornamen_location.append(data_name.values()[0]["Voornaam"])
                    locations.append(key_2_option)
                    
            # Voornaam in andere generation
            voornamen_birthyear = []
            birthyears = []
            for key_3_option in keys_3:            
                table_name = key_1 + "_" + key_2 + "_" + key_3_option
                model_object = get_model("app_voornamen",table_name)
                data_name = model_object.objects.filter(Rang=rang)
                if len(data_name) == 0:
                    voornamen_birthyear.append("")
                    birthyears.append(key_3_option)
                else:
                    voornamen_birthyear.append(data_name.values()[0]["Voornaam"])
                    birthyears.append(key_3_option) 
            
                    
            aantal_matrix_dummy = []
            for i in range(len(aantal_matrix)):
                aantal_matrix_dummy.append([])
                for j in range(len(aantal_matrix[i])):
                    aantal_matrix_dummy[i].append(json.dumps(aantal_matrix[i][j]))
                    
            aantal_matrix_dummy = json.dumps(aantal_matrix_dummy)  
            voornamen_location = json.dumps(voornamen_location)
            locations = json.dumps(locations)
            voornamen_birthyear = json.dumps(voornamen_birthyear)
            birthyears = json.dumps(birthyears)
            
            return HttpResponse(json.dumps({"namen" : namen, "rang": rang, "aantal": aantal, "aantal_matrix":aantal_matrix_dummy, "voornamen_location":voornamen_location, "locations":locations, "voornamen_birthyear":voornamen_birthyear, "birthyears":birthyears}), content_type = "application/json")
            # return render(request, 'index.html', {'form': form, "namen" : namen, "rang": rang, "aantal": aantal})
            

    # if a GET (or any other method) we'll create a blank form
    # When first rendering the site, this is what is used
    else:
        form = forms.NameForm()


    # Get names from database to use autocomplete:
    namen_db = voornamen_lijst.objects.all().values_list("Voornaam")
    namen = list()
    for i in range(len(namen_db)):
        namen.append(namen_db[i][0])

    return render(request, 'apps/app_voornamen/index.html', {'form': form, "namen" : namen})