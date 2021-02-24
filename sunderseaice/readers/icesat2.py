"""Module to read ICESat-2 files into xarray.Dataset"""

import xarray as xr


def load_atl20_month(filepath):
    """
    Loads datasets in monthly group of ATL20 h5 file with coordinates

    :filepath: path to ATL20 h5 file

    :returns: xarray.Dataset object
    """
    ds = xr.merge([
        xr.open_dataset(filepath),
        xr.open_dataset(filepath, group="monthly", decode_times=False)
        ])
    ds = ds.set_coords(['grid_lat', 'grid_lon'])
    return ds

