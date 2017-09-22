#!/bin/bash
# this script will export all .shp files in a directory to .geojson files in a specified subdirectory 
# ************************************************************************************************************

# To run on terminal:
# 1. chmod +x ./yourscrip.sh
# 2. ./yourscript.sh

SOURCEDIR="./geodata/ElectionHistory/input/MapData/NaturalEarthData/ADM1/geojson/country/"
OUTPUTDIR="./geodata/ElectionHistory/input/MapData/NaturalEarthData/ADM1/topojson/country/"
for FILE in $SOURCEDIR*.json; # $SOURCEDIR # cycles through all files in directory (case-sensitive!)
do
    FILENEW=`echo | basename $FILE | sed "s/geo/topo/"` # replaces old filename
    topojson \
    -o $OUTPUTDIR$FILENEW  \
    --properties n=name --properties c=adm0_a3 \
    $FILE
done
exit