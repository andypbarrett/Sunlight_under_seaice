#!/bin/bash

product="ATL03"
version="005"
floe="floe2"

outpath="/home/apbarret/Data/ICESat-2/$product/v$version"
csv_filepath="/home/apbarret/src/SunlightUnderSeaIce/data"

csvfile="$csv_filepath/$product.$version.polarstern.$floe.granules_list.csv"

granule_list=`tail -n +2 $csvfile | cut -d',' -f7`
granule_list+=" "
granule_list+=`tail -n +2 $csvfile | cut -d',' -f8`

wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies --no-check-certificate --auth-no-challenge=on -r --reject "index.html*" --continue -nd -np -e robots=off $granule_list -P $outpath
