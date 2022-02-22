"""Reads Polarstern MOSAiC data into GeoPandas object"""
from pathlib import Path
from collections import namedtuple
import datetime as dt

from shapely.geometry import LinearRing
from shapely.geometry.polygon import orient

import pandas as pd
import geopandas as gpd

DATAPATH = Path("/home/apbarret/src/SunlightUnderSeaIce/data")
POLARSTERN_TRACK_FILE = DATAPATH / "polarstern_track_full_cruise.txt"


MosaicFloe = namedtuple("FloeDates", ['start', 'end'])
floe1 = MosaicFloe(dt.datetime(2019, 10, 4), dt.datetime(2020, 5, 17))
floe2 = MosaicFloe(dt.datetime(2020, 6, 19), dt.datetime(2020, 7, 31))
floe3 = MosaicFloe(dt.datetime(2020, 8, 21), dt.datetime(2020, 9, 20))


def read_polarstern_track():
    """Reads the drift track of the polarstern into a geopandas dataframe"""
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
    geometry = gpd.points_from_xy(df.Longitude, df.Latitude)
    gdf = gpd.GeoDataFrame(df, geometry=geometry,
                           crs="EPSG:4326")
    return gdf


def get_search_radius(gdf, radius=20000., resolution=3):
    """Returns a GeoPandas object of search buffers indexed by date"""
    original_crs = gdf.crs
    return gdf.to_crs(3413).buffer(radius, resolution).to_crs(original_crs)


def shapely_to_cmr(poly):
    """Converts shapely polygon to string containing lon, lat
       expected by CMR.  CMR expects coordinates to be counter-
       clockwise.  Code automatically reverses this"""
    poly_ccw = orient(poly, sign=1.0)
    assert LinearRing(poly_ccw.exterior.coords).is_ccw, "Polygon is not counter-clockwise"
    return ",".join([f"{x},{y}" for x, y in poly_ccw.exterior.coords])
