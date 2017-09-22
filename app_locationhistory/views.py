from django.shortcuts import render

# Create your views here.
def index(request):
    import json
    with open('app_locationhistory/algorithm/data/Willem_Lenaerts_Belgie.geojson') as f:
        data = json.load(f)
    
    for feature in data["features"]:
        feature["properties"]["province"] = "" # no null because leaflet can't work with that
    return render(request, 'apps/app_locationhistory/index.html', {"data":data})
