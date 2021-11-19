"""Module to read ICESat-2 files into xarray.Dataset"""

import h5py
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


def atl10(filepath):
    '''Read ATL10 (Freeboard)'''
    f = h5py.File(filepath, 'r')
    gt2l = xr.Dataset({
        'freeboard': (['x'], f['gt2l']['freeboard_beam_segment']['beam_freeboard']['beam_fb_height'][:]), 
        'geoseg_beg': (['x'], f['gt2l']['freeboard_beam_segment']['beam_freeboard']['geoseg_beg'][:]), 
        'geoseg_end': (['x'], f['gt2l']['freeboard_beam_segment']['beam_freeboard']['geoseg_end'][:]), 
        'latitude': (['x'], f['gt2l']['freeboard_beam_segment']['beam_freeboard']['latitude'][:]), 
        'longitude': (['x'], f['gt2l']['freeboard_beam_segment']['beam_freeboard']['longitude'][:])
    },)
    # Add segment center as alongtrack distance coordinate
    x = (gt2l.geoseg_beg + gt2l.geoseg_end.values) * 0.5
    gt2l.coords['x'] = x.values
    return gt2l


