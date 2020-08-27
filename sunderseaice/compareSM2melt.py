#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 20:21:31 2020

@author: stroeve
This program computes the time-delay between melt onset and snow disappearing
First testing that I can read the data and put everything into the same grid before adding parcel trajectories
"""


import os

import tqdm

import datetime as dt

from pathlib import Path
import rasterio
from rasterio.crs import CRS as rcrs
from rasterio import warp
import cartopy


import itertools
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
from netCDF4 import Dataset #netcdf routines that you need to install into python

from read_grads import read_grads
from sunderseaice.readers import snowmodel

def regrid_melt_onset_to_ease_north(ingrid):
    '''It does what it says on the tin

    ingrid - numpy array in NSIDC North Polar Stereographic grid
    '''
    
    src_proj = {'pixel_width': 25000,
                'pixel_height': 25000,
                'ccrs': {'central_latitude': 90.0,
                         'central_longitude': -45.0,
                         'false_easting': 0.0,
                         'false_northing': 0.0,
                         'true_scale_latitude': 70 },
                'bounds': [-3850000.000, 3750000., -5350000., 5850000.000]}
    src_globe = ccrs.Globe(datum=None, semimajor_axis=6378273., semiminor_axis=6356889.449)
    src_crs = ccrs.Stereographic(**src_proj['ccrs'], globe=src_globe)
    
    #define 25-km EASE grid
    dst_proj = {'pixel_width': 25067.5,
                'pixel_height': 25067.5,
                'ccrs': {'central_latitude': 90.,
                         'central_longitude': 0.,
                         'false_easting': 0.0,
                         'false_northing': 0.0},
                'bounds': [-4524683.8, 4524683.8, -4524683.8, 4524683.8]}
    dst_globe = ccrs.Globe(datum=None, semimajor_axis=6371228, semiminor_axis=6371228)
    dst_crs = ccrs.LambertAzimuthalEqualArea(**dst_proj['ccrs'], globe=dst_globe)
    dst_size = (361, 361)

    

# Get EASE grid

EASE_grid = Dataset('/Users/stroeve/Documents/seaice/grid.nc')
lons = np.array(EASE_grid['lon'])
lats = np.array(EASE_grid['lat'])


datapath = '/Users/stroeve/Documents/seaice/seaice_melt'
###########SNOW DEPTH PART########
#read in the snow depth data
#this part loads the snowmodel data and saves it into an xarray.dataarray

datafile=os.path.join(datapath,'snod.gdat')
ctlfile = os.path.join(datapath,'SM_snod_merra2_01Aug1980-31Jul2018.ctl')

snod=snowmodel.read(datafile,ctlfile)

snod=snod.squeeze()

# #to acess some values
# snod[100,180,180].values 
# #another way is
# snod.y[180].values, snod.x[180].values

#covert to the EASE grid with map
SphericalEarth = ccrs.Globe(semimajor_axis=6371228., semiminor_axis=6371228.)
NSIDC_EASE = ccrs.LambertAzimuthalEqualArea(central_latitude=90., central_longitude=0., globe=SphericalEarth)

extent = [-4524683.8, 4524683.8, -4524683.8, 4524683.8]
fig=plt.figure(figsize=(7, 7))
ax = fig.add_subplot(111, projection=NSIDC_EASE)
ax.set_extent(extent, NSIDC_EASE)
ax.coastlines()
ax.gridlines()
snod.sel(time='2000-01-01').plot(ax=ax)

####################################

#this function will take the day of year from the melt onset fields and convert to date
def doy_to_date(doy,year):
    # some function that takes in day of
    # year and returns a datetime.date object

    first_day = dt.date(year=year,month=1,day=1)
    date_obj = first_day + dt.timedelta(days=doy)

    return(date_obj)

def get_SM_depths_from_date(my_date):
    #takes in a  date and gets the SM-LG snow depths for that date. This function on the variable snod much be defined prior to the use of the function
    #specify the day that SM-LG data begins
    start_date=dt.date(year=1980,month=8,day=1)
    
    #calculate the number of days between the start of SM-LG and the date we're interested in 
    delta=(my_date - start_date).days #Int
    
    #get the data out of the array using the index computed in previous line
#    data=snod['snod'][delta] #361x361 numpy array
    data=snod[delta] #361x361 numpy array based on the delta time index
    return(data)

###########MELT ONSET PART#########
#we need to reproject all the sea ice melt onset files to match the SnowModel grid.
#Define NSIDC PS grid
#The default ellipsoid is WGS84. However, the NSIDC PS grid uses the Hugh's 1880 ellipsoid. To account for this, a separate Globe object has to be created and passed to the Stereographic object.



#initialise a dictionary
my_dict = {}
my_dict_melt={}
#melt=np.empty(shape=(40,361,361))
#year_save=np.empty(shape=(40), dtype=int)

fdir=Path(datapath)
files=fdir.glob('*.nc')
for j in files:
    #load data
    rootgrp=Dataset(j,"r")
    year=getattr(rootgrp,'Year') #pull year 

    #extract out melt onset and early melt
    melt=rootgrp.variables['Melt'][:]
    earlymelt=rootgrp.variables['Earlymelt'][:]
    rootgrp.close() #close out the netcdf file

    #regrid to the EASE grid
    #convert source and destination cartopy crs to rasterio crs
    src_rcrs = rcrs.from_string(src_crs.proj4_init)
    #src_rcrs = rcrs.from_string('+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +a=6378273 +b=6356889.449 +units=m +no_defs')

    dst_rcrs = rcrs.from_string(dst_crs.proj4_init)
    #dst_rcrs = rcrs.from_string('+proj=laea +lat_0=90 +lon_0=0 +x_0=0 +y_0=0 +a=6371228 +b=6371228 +units=m +no_defs')

    # Get shape of source grid
    source_height, source_width = melt.shape

    # Define source affine transformation
    src_transform = rasterio.Affine(src_proj['pixel_width'], # pixel width
                                0.,                      # row rotation
                                src_proj['bounds'][0],   # Left coordinate
                                0.,                      # Column rotation
                                -1*src_proj['pixel_height'], # pixel height
                                src_proj['bounds'][3])

    # Define destination affine transformation
    dst_transform = rasterio.Affine(dst_proj['pixel_width'], # pixel width
                                0.,                      # row rotation
                                dst_proj['bounds'][0],   # Left coordinate
                                0.,                      # Column rotation
                                -1*dst_proj['pixel_height'], # pixel height
                                dst_proj['bounds'][3])
    #Initialize the destination arrays
    melt_ease=np.empty(dst_size,dtype=float)
    earlymelt_ease=np.empty(dst_size,dtype=float)

    #do reprojection
    warp.reproject(source=melt.astype(float),
              src_crs=src_rcrs,
              src_nodata=np.nan,
              src_transform=src_transform,
              destination=melt_ease,
              dst_transform=dst_transform,
              dst_crs=dst_rcrs,
              dst_nodata=np.nan,
              SOURCE_EXTRA=0,
              resampling=warp.Resampling.nearest)
    warp.reproject(source=earlymelt.astype(float),
              src_crs=src_rcrs,
              src_nodata=np.nan,
              src_transform=src_transform,
              destination=earlymelt_ease,
              dst_transform=dst_transform,
              dst_crs=dst_rcrs,
              dst_nodata=np.nan,
              SOURCE_EXTRA=0,
              resampling=warp.Resampling.nearest)
    
    #mask out all the invalid values and make them Nans
    melt_ease=np.ma.masked_where(melt_ease < 75, melt_ease)
    melt_ease=np.ma.masked_where(melt_ease > 410, melt_ease)
    melt_ease=np.ma.filled(melt_ease, np.nan)

# fill your dictionary object with a tiny, two-entry dictionary, which just has the data for each variable in that year.
  # my_dict[year] = {'melt':melt_ease, 'earlymelt':earlymelt_easetest}
  #  my_dict_melt[year]={'melt':melt_ease}
    my_dict_melt[year]=melt_ease #remove the "melt" label in order to loop through it as an array

#to reference a particular year you can type melt_1981=my_dict['1981']['melt']    
    imgplot=plt.imshow(melt_ease, clim=(75,210))
    plt.colorbar() # give it a colorbar
    plt.title(year+ ' Melt') # title it
    plt.savefig(datapath+year+'meltexample.pdf') # save it
    plt.show() # show it and clear the graphics buffer



depths_at_melt_onset={} #an empty dictionary to be filled

#dictionary to fill, keys will be years
#corresponding items will be grids of depth at melt onset
for year in tqdm.tqdm(my_dict_melt.keys()):
    #set up array full of nans
    #these will ultimately be replaced with snow depth at melt onset (where applicable)
    array_to_fill=np.full((361,361),np.nan) #a 361x361 numpy array of nans
    
    #get the grid of melt onset dates from the melt dictionary
    
    melt_onset_dates_for_year=my_dict_melt[year] #a 361x361 array
#    print(type(melt_onset_dates_for_year))
#    print(melt_onset_dates_for_year.shape)
    
    #iterate through every element of the met onset date grid, using i,j indexes
#    valid_melt=melt_onset_dates_for_year[(melt_onset_dates_for_year > 75) & (melt_onset_dates_for_year < 410)] 
    for i,j in itertools.product(range(361),range(361)):
        #for each eleemtn of the melt onset date grid, we have an integer for the day of year or nan
        doy=melt_onset_dates_for_year[i,j]
#        print('day of year for melt ',i,j,doy)
        if ~np.isnan(doy): #if the value is not nan then we get depth at melt onset
            #np.isnan(x) ius a function that comes back true if x is a value that the numpy module recognises as not a number
            #putting a ~ in front of it flips the true/false value so ~np.isan(x) comes back true if x is a good value, and false if it's a nan
            #so while the code iterates through all the values of doy in the array, the if statement is executed if the doy is meaningful
            
            #convert day of year of melt onset to date of melt onset
            date=doy_to_date(doy,int(year)) #a datetime.date object
            
            #get snow depth at that element (i,j) for that date
            depth_for_given_date=get_SM_depths_from_date(date)[i,j] # a float array
            
            #put this depth into the empty array we inialized for this year
            array_to_fill[i,j]=depth_for_given_date
            
    #once all the elements of the array have been filled that can be filled, 
    #store the grid of depths at melt onset in the dictionary initialized earlier
    depths_at_melt_onset[year] = array_to_fill # Fill the dictionary with 361x361 arrays, indexed by year
            
       
#make plots of the snow deeth for each melt onset date
fig = plt.figure(figsize=(30,30))

axs = fig.subplots(6,7,subplot_kw={'projection': ccrs.NorthPolarStereo()})
axs = axs.ravel()



for counter, year in enumerate(depths_at_melt_onset.keys()):
    
    ax = axs[counter]
    
    depths = depths_at_melt_onset[year] # A 361 x 361 array
    
#    ax.add_feature(cartopy.feature.LAND, edgecolor='black',zorder=1)
    plot = ax.pcolormesh(lons,lats,depths,vmin=0,vmax=1,transform=ccrs.PlateCarree())
    ax.set_extent([-180,180,90,66], ccrs.PlateCarree())
    ax.set_title(str(year),fontsize=30)
    
fig.subplots_adjust(right=0.87)
cbar_ax = fig.add_axes([0.89, 0.15, 0.02, 0.7])
cbar = fig.colorbar(plot, cax=cbar_ax)
cbar.ax.tick_params(labelsize=35)
cbar.ax.set_ylabel('Snow Depth (m)', fontsize =35)

plt.subplots_adjust(wspace=0.05,hspace=0.15)

plt.savefig('multiplot_depth_at_melt_onset.png', dpi=500)
       
#   test=melt_ease[(melt_ease > 75) & (melt_ease < 410)]

  #  melt=np.array(my_dict_melt)
#   melt[j,:,:]=melt_ease









