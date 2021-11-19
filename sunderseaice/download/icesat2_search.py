"""Functions to search for ICESat-2 tracks along Polarstern track"""

import os
import datetime as dt
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LinearRing
from shapely.geometry.polygon import orient

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

import h5py
import xarray as xr

import download.nsidc_download as cmr
from grid import SSMI_PolarStereoNorth25km 

DATAPATH = Path("/home/apbarret/src/SunlightUnderSeaIce/data")
POLARSTERN_TRACK_FILE = DATAPATH / "polarstern_track_full_cruise.txt"

# Start and end dates for Polarstern on floe
on_floe_dates = {
    1: (dt.datetime(2019, 10, 4), dt.datetime(2020, 5, 17)),
    2: (dt.datetime(2020, 6, 19), dt.datetime(2020, 7, 31)),
    3: (dt.datetime(2020, 8, 21), dt.datetime(2020, 9, 20)),
    }

with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    map_proj = SSMI_PolarStereoNorth25km.to_cartopy()
map_extent = [-2349878.8355433852, 2349878.8355433857, -2349878.8355433852, 2349878.8355433857]

# Tasks/functions
# read_polarstern_track - done
# Prepare temporal and spatial querys
#      - select temporal frequency - default=12
#      - create search polygon, check handedness, output as list
# Loop through queries


def read_polarstern_track():
    """Reads the drift track of the polarstern into a pandas dataframe"""
    columns = ["Date", "Latitude", "Longitude", "Speed", "Course"]
    df = pd.read_csv(
        POLARSTERN_TRACK_FILE,
        skiprows=1, 
        delim_whitespace=True,
        index_col=0,
        parse_dates=True,
        header=None,
        names=columns
    )
    return df


def select_midday(df):
    """Extracts a view of DataFrame for 1200 hrs"""
    return df[(df.index.hour == 12) & (df.index.minute == 0)]


def pandas_to_geopandas(df, crs="EPSG:4326"):
    """Returns a geopandas dataseries"""
    geometry = [Point(xy) for xy in zip(df.Longitude, df.Latitude)]
    return gpd.GeoSeries(geometry, index=df.index, crs=crs)


def polarstern_cmr_track(product="ATL10", ):
    pass


def shapely_to_cmr(poly):
    """Converts shapely polygon to string containing lon, lat
       expected by CMR.  CMR expects coordinates to be counter-
       clockwise.  Code automatically reverses this"""
    poly_ccw = orient(poly, sign=1.0)  # Force polygons to be counter-clockwise
    assert LinearRing(poly_ccw.exterior.coords).is_ccw, "Polygon is not counter-clockwise"
    return ",".join([f"{x},{y}" for x, y in poly_ccw.exterior.coords])


def icesat2_granule(search_date, search_buffer, product="ATL10", version="004"):
    start_date, end_date = search_date - dt.timedelta(hours=12), search_date + dt.timedelta(hours=12)
    results = cmr.cmr_search(
        product, 
        version, 
        start_date.isoformat(),  # CMR API expects iso format date strings
        end_date.isoformat(), 
        polygon=shapely_to_cmr(search_buffers.to_crs(4326)[search_date]),
        )
    return results
    
    
def polygon_area(poly):
    x, y = map(list, zip(*poly))
    if (x[0] != x[-1]) & (y[0] != y[-1]):
        x.append(x[0])
        y.append(y[0])
    return sum([((x[i+1] - x[i]) * (y[i+1] + y[i]) * 0.5) for i in range(len(x)-1)])
    
    
def isccw(poly):
    """Return the signed area enclosed by a ring using the linear time
algorithm at http://www.cgafaq.info/wiki/Polygon_Area. A value >= 0
indicates a counter-clockwise oriented ring."""
    if polygon_area(poly) >= 0:
        return True
    else:
        return False 


def shapely_to_cmr(poly):
    """Converts shapely polygon to string containing lon, lat
       expected by CMR.  CMR expects coordinates to be counter-
       clockwise.  Code automatically reverses this"""
    poly_ccw = orient(poly, sign=1.0)  # Force polygons to be counter-clockwise
    assert LinearRing(poly_ccw.exterior.coords).is_ccw, "Polygon is not counter-clockwise"
    return ",".join([f"{x},{y}" for x, y in poly_ccw.exterior.coords])
                    #coords = list(poly.exterior.coords)
    # LinearRing(polygon_or.exterior.coords).is_ccw also works
    # polygon_or = orient(polygon, sign=1.0) returns ccw polygon
    #print(isccw)
    #if isccw(coords):
    #    pr = coords
    #else:
    #    pr = coords[::-1]
    #)


def _circle_params(point, search_radius = 1000.):
    '''Helper function to returns list of parameters for search circle'''
    #latitude, longitude = df.values
    return f'{point.x},{point.y},{int(search_radius)}'


def _bounding_box(point, search_box=0.5):
    '''Helper function to return bounding box'''
    longitude, latitude = point.x, point.y
    #latitude, longitude = df.values
    ll_lon = longitude - search_box/2.
    ll_lat = latitude - search_box/2.
    ur_lon = longitude + search_box/2.
    ur_lat = latitude + search_box/2.
    return '{0},{1},{2},{3}'.format(str(ll_lon), str(ll_lat), str(ur_lon), str(ur_lat))

