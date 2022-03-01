"""Readers and utils for granules lists"""
from pathlib import Path

import pandas as pd
import geopandas as gpd
from shapely import wkt

from sunderseaice.filepath import GRANULE_LIST_PATH

def load_granule_list(product, version='005', floe="floe2"):
    """Loads csv file containing list of granules that 
    correspond to Polarstern position.

    :product: name of ICESat-2 product (atl03, atl07, atl10)

    :returns: geopandas.DataFrame
    """
    granule_list = (GRANULE_LIST_PATH /
                    f"{product.upper()}.{version}.polarstern.{floe}.granules_list.csv")
    df = pd.read_csv(granule_list, index_col=0, parse_dates=True)
    df['geometry'] = df['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, crs=4326)
    return gdf


def get_bounds(record, radius=20000., resolution=3, to_crs=4326):
    """Returns minx, maxx, miny, maxy for buffer region

    :geometry: shapely geometry
    """
    proj_crs = 3414
    if to_crs == proj_crs:
        bounds = record.to_crs(3413).buffer(radius, resolution).bounds
    else:
        bounds = record.to_crs(3413).buffer(radius, resolution).to_crs(to_crs).bounds
    return bounds.values
