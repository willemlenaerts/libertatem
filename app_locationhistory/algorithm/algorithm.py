# Plot Google location history
import numpy as np
import json
import datetime
import time

# Get location data
with open("app_locationhistory/algorithm/data/Locatiegeschiedenis_Willem_Lenaerts.json", 'r') as fh:
    user_locations = json.loads(fh.read())
 
# Get area data   
with open("app_locationhistory/algorithm/data/municipalities-belgium.geojson", 'r') as fh:
    areas = json.loads(fh.read())
    
# Clean data: lists of (long,lat) tuples
user_locations_poly = []
for user_location in user_locations["locations"]:
    user_locations_poly.append((user_location["longitudeE7"]/float(1e7) ,user_location["latitudeE7"]/float(1e7) ))
    
areas_poly = []
count = 0
for area in areas["features"]:
    areas_poly.append([])
    if area["geometry"]["type"] == "MultiPolygon":
        for area_point in area["geometry"]["coordinates"][0][0]:
            areas_poly[-1].append((area_point[0],area_point[1]))
        count += 1
    elif area["geometry"]["type"] == "GeometryCollection":
        for geocol in area["geometry"]["geometries"]:
            for area_point in geocol["coordinates"][0]:
                areas_poly[-1].append((area_point[0],area_point[1])) 
        count += 1

# Check for every user location where it was:
user_area = []
for i in range(len(areas_poly)):
    user_area.append(0)

print("Starting PIP (point in polygon) search.")
count = 0
for user_location_poly in user_locations_poly:
    
    if count == 0:
        start = time.time()
    x = user_location_poly[0]
    y = user_location_poly[1]
    
    for i in range(len(areas_poly)):
        inside = point_inside_polygon(x,y,areas_poly[i])
        if inside == True:
            user_area[i] += 1
            break
    
    if count == 10:
        stop = time.time()
        print("One search takes " + str((stop-start)/(count)) + " seconds.")
        print("Entire search will take " + str((((stop-start)/count)*len(user_locations_poly))/60) + " minutes.")
    count += 1

# Add percentage and hours spent in areas
for i in range(len(areas["features"])):
    areas["features"][i]["properties"]["perc"] = user_area[i]/sum(user_area)
    areas["features"][i]["properties"]["hours"] = user_area[i]/60

# Update area file with these properties
with open('app_locationhistory/algorithm/data/Willem_Lenaerts_Belgie.geojson', 'w') as outfile:
    json.dump(areas, outfile)
    
def point_inside_polygon(x,y,poly):

    n = len(poly)
    inside =False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside
    
