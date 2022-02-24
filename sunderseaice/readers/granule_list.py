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
    #df['geometry'] = df['geometry'].apply(wkt.loads)
    
    return df
