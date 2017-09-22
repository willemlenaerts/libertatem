# Rename Flags from ISO2 to ISO3
import os
import glob
import pandas as pd
from PIL import Image

input_directory = "geodata/ElectionHistory/input/Flags/ISO2/"
output_directory = "geodata/ElectionHistory/input/Flags/ISO3/"

iso_conversion = pd.read_csv("geodata/ElectionHistory/input/Flags/iso_conversion.csv",sep=";")

input_files = glob.glob(input_directory + "*.png")
for imageFile in input_files:
    filepath,filename = os.path.split(imageFile)
    iso2_name = filename.split(".")[0]
    if len(iso2_name) > 2:
        continue
    
    if len(iso_conversion[iso_conversion.ISO2 == iso2_name].ISO3) != 1:
        continue
    
    iso3_name = iso_conversion[iso_conversion.ISO2 == iso2_name].ISO3.iloc[0]

    # Save
    im = Image.open(imageFile)
    im.save(output_directory + iso3_name + ".png","png")
