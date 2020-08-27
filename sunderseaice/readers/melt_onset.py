# Reads Polar Stereographic melt onset grids
import glob
import os
from packaging import version

import numpy as np
import xarray as xr


def get_filelist(dirpath):
    return sorted(glob.glob(os.path.join(dirpath, '*meltfreeze.nc')))

    
def year_from_filename(f):
    return int(os.path.basename(f)[0:4])


def get_years_from_filenames(filelist):
    return [year_from_filename(f) for f in filelist]


def get_ps_coords(dim):
    if dim == 'x':
        return np.arange(304)
    elif dim == 'y':
        return np.arange(448)

    
def read_ps(dirpath):
    '''reads melt onset files into xarray'''
    filelist = get_filelist(dirpath)
    
    year = get_years_from_filenames(filelist)

    # Workaround until rasterio installed on sunlight_under_seaice
    if version.parse(xr.__version__) <= version.parse('0.12.1'):
        args = dict(paths=filelist, concat_dim='year')
    else:
        args = dict(paths=filelist, combine='nested', concat_dim='year')
        
    ds = xr.open_mfdataset(**args)
    ds.coords['year'] = year
    ds.coords['x'] = get_ps_coords('x')
    ds.coords['y'] = get_ps_coords('y')
    ds.attrs.pop('Year', None)  # year is spurious attribute
    
    return ds


    
