#!/bin/bash

DATAPATH="/home/apbarret/Data/Snow_on_seaice/SnowModelOutput"
REANALYSIS="MERRA2"
VARIABLE="snow_depth"

# Input filepaths
GDATFILE="$DATAPATH/$REANALYSIS/snod.gdat"
CTLFILE="$DATAPATH/$REANALYSIS/SM_snod_merra2_01Aug1980-31Jul2018.ctl"

# Output netcdf filepath
NCFILE="$DATAPATH/$REANALYSIS/SnowModel_snow_depth_merra2_01Aug1980-31Jul2018.nc"

python gdat_to_netcdf.py $GDATFILE $CTLFILE $NCFILE $VARIABLE $REANALYSIS
