# Download SVG/PNG images 
# Resize
# Save

import pandas as pd
from gi.repository import Rsvg
# from gi.repository import cairo
import cairo
import urllib.request
import json
import os
import io
from PIL import Image
# import cStringIO

output_size = 70

# Import data
team_data = pd.read_csv("app_voetbalpi/eu_domestic_leagues/data/input/team_data.csv")
competition_data = pd.read_csv("app_voetbalpi/eu_domestic_leagues/data/input/competition_data.csv")
countries = []

for directory in os.walk("app_voetbalpi/eu_domestic_leagues/data/output/"):
    directory = directory[0].replace('app_voetbalpi/eu_domestic_leagues/data/output/',"")
    if (directory != "") and ("/" not in directory):
        countries.append(directory)
    

for c in countries:
    teams = json.load(open("app_voetbalpi/eu_domestic_leagues/data/output/" + c + "/teams.json","r"))
    
    # Check if subdirectory exists
    if not os.path.exists("app_voetbalpi/eu_domestic_leagues/data/output/" + c + "/logos"):
        os.makedirs("app_voetbalpi/eu_domestic_leagues/data/output/" + c + "/logos")   
    if not os.path.exists("app_voetbalpi/eu_domestic_leagues/data/output/" + c + "/logos/" + str(output_size)):
        os.makedirs("app_voetbalpi/eu_domestic_leagues/data/output/" + c + "/logos/" + str(output_size))

    input_url = competition_data[competition_data.country == c].image_url.iloc[0]
    OUTPUTFILE = "app_voetbalpi/eu_domestic_leagues/data/output/" + c + "/logos/" + str(output_size) + "/" + c + ".png"
    
    if input_url.split(".")[-1] == "png":
        INPUTFILE = io.BytesIO(urllib.request.urlopen(input_url).read())
        img = Image.open(INPUTFILE)
        png_width = img.size[0]
        png_height = img.size[1]
        
        # Scale height, but keep dimensions intact (%)
        scale = output_size/png_height
        
        img.resize((int(png_width*scale),int(png_height*scale)), Image.ANTIALIAS).save(OUTPUTFILE)      
        competition_data.loc[competition_data.country == c,"png_width"] = int(png_width*scale)
        competition_data.loc[competition_data.country == c,"png_height"] = int(png_height*scale)
        
        
    elif input_url.split(".")[-1] == "svg":
        INPUTFILE = urllib.request.urlopen(input_url).read()
        
        # create the cairo context                                                  
        surface = cairo.SVGSurface('myoutput.svg', output_size, output_size)
        context = cairo.Context(surface)
        
        # use rsvg to render the cairo context      
        handle = Rsvg.Handle()
        svg = handle.new_from_data(INPUTFILE)
        svg_dimensions = svg.get_dimensions_sub("")
        svg_height = svg_dimensions[1].height
        svg_width = svg_dimensions[1].width
        context.scale(output_size/svg_height,output_size/svg_height) # SCALE on HEIGHT
        
        competition_data.loc[competition_data.country == c,"png_width"] = int(svg_width*output_size/svg_height)
        competition_data.loc[competition_data.country == c,"png_height"] = int(svg_height*output_size/svg_height)
        
        svg.render_cairo(context)
        surface.write_to_png(OUTPUTFILE)
    
    for t in range(len(teams)):
        
        input_url = team_data[team_data.name == teams[t]].crestUrl.iloc[0]
        OUTPUTFILE = "app_voetbalpi/eu_domestic_leagues/data/output/" + c + "/logos/" + str(output_size) + "/" + str(t) + ".png"
        
        if input_url.split(".")[-1] == "png":
            INPUTFILE = io.BytesIO(urllib.request.urlopen(input_url).read())
            img = Image.open(INPUTFILE)
            img.resize((output_size,output_size), Image.ANTIALIAS).save(OUTPUTFILE)      
            
        elif input_url.split(".")[-1] == "svg":
            INPUTFILE = urllib.request.urlopen(input_url).read()
            
            # create the cairo context                                                  
            surface = cairo.SVGSurface('myoutput.svg', output_size, output_size)
            context = cairo.Context(surface)
            
            # use rsvg to render the cairo context      
            handle = Rsvg.Handle()
            svg = handle.new_from_data(INPUTFILE)
            svg_dimensions = svg.get_dimensions_sub("")
            svg_height = svg_dimensions[1].height
            svg_width = svg_dimensions[1].width
            context.scale(output_size/svg_width,output_size/svg_height)
            
            svg.render_cairo(context)
            surface.write_to_png(OUTPUTFILE)

# Write competition data update
competition_data.to_csv("app_voetbalpi/eu_domestic_leagues/data/input/competition_data.csv")