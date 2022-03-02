"""Module to read ICESat-2 files into xarray.Dataset"""

import numpy as np

import h5py
import xarray as xr

from sunderseaice.readers.data_dictionary import ATL03_DATA_DICT, ATL07_DATA_DICT


def convert_attributes(attrs):
    return {k: (v.decode() if isinstance(v, bytes) else v) for k, v in attrs.items()}


def h5var_to_dataarray(f, group_path, dim_name='segment'):
    """Generates an xarray.DataArray from an H5 variables

    :f: h5 file object
    :group_path: path to variables

    :returns: xarray.DataArray - with dummy variables
    """
    assert group_path in f, f"{group_path} not found in {f.filename}"
    
    dataset = f[group_path]
    da = xr.DataArray(dataset[:],
                        attrs=convert_attributes(dataset.attrs),
                        name=dataset.name.split('/')[-1])
    #TODO: mask out _FillValue
    return da

    
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


def load_atl07(filepath, beam,
               variables = []):
    """Loads ATL07 sea ice height variables.  

    Height and geolocation variables are in different groups so variables are read from
    the HDF5 file separately.

    The common dimension for the two groups, delta_time, is not unique, so dim is changed
    to height_segment_id (folling A.Petty's advice).  This allows the two groups to be
    concatenated.

    :filepath: str or pathlib.Path object containing filepath
    :beam: name of beam (gt1r, gt1l, gt2r, gt2l, gt3r, or gt3l)
    
    :variables: name of variables to read from H5 file.

    :return: xarray.Dataset object
    """
    with h5py.File(filepath, 'r') as f:
        data_arrays = {}
        for var, group in ATL07_DATA_DICT.items():
            data_arrays[var] = h5var_to_dataarray(f, f"{beam}/{group}")
    ds = xr.Dataset(data_arrays)
    ds = ds.swap_dims({'dim_0': 'height_segment_id'})
    ds = ds.set_coords(['latitude', 'longitude', 'delta_time'])
    return ds


def load_atl10(filepath, beam):
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


def load_atl03(filepath, beam, group="heights",
          drop_variables=['pce_mframe_cnt', 'ph_id_channel',
                          'ph_id_count', 'ph_id_pulse']):
    """Read ATL03 geolocated photons into xarray

    :filepath: str or pathlib.Path containing filepath

    :beam: beam identifier (gt1r, gt1l, gt2r, gt2l, gt3r, gt3l).  
           Should I return a single beam.  I think so because beams do not have a common
           geolocation
    
    :returns: xarray.Dataset containing photon data group and geolocation
    """
    group = f"{beam}/{group}" 
    ds = xr.open_dataset(filepath, group=group, chunks="auto",
                         drop_variables=drop_variables)
    return ds
