"""Module to read ICESat-2 files into xarray.Dataset"""

import h5py
import xarray as xr

from sunderseaice.readers.data_dictionary import ATL03_DATA_DICT


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

    :filepath: str or pathlib.Path object containing filepath
    :beam: name of beam (gt1r, gt1l, gt2r, gt2l, gt3r, or gt3l)
    
    :variables: name of variables to read from H5 file.

    :return: xarray.Dataset object
    """
    group_name = f"{beam}/sea_ice_segments"
    sea_ice_segments_ds = xr.open_dataset(filepath, group=group_name)
    #group_name = group_name + '/' + 'heights'
    #heights_ds = xr.open_dataset(filepath, group=group_name,
    #                          drop_variables=None)
    #ds = xr.concat([sea_ice_segments_ds, heights_ds], dim='delta_time')
    ds = sea_ice_segments_ds
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
