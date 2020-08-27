# Reads Polar Stereographic melt onset grids
import glob
import os

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

    da = xr.open_mfdataset(filelist, combine='nested', concat_dim='year')
    da.coords['year'] = year
    da.coords['x'] = get_ps_coords('x')
    da.coords['y'] = get_ps_coords('y')
    
    print(da)
    

    
