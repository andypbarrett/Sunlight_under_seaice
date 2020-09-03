# Regrids melt onset data from North Polar Stereographic 25 km to EASE-Grid AVHRR 25 km
import warnings
import numpy as np
import xarray as xr

warnings.simplefilter("ignore")

from sunderseaice.readers.melt_onset import read_ps
from sunderseaice.maps.regrid import north_polar_stereo_to_ease_avhrr
from sunderseaice.maps.projections import EASEGridAVHRRNorth25

DATADIR = "/home/apbarret/Data/Melt_onset/"


def regrid_DataArray(da_in):
    '''Regrids a single DataArray'''

    ease_proj = EASEGridAVHRRNorth25()

    out_da_list = []
    for y in da_in.year:
        out_da_list.append(north_polar_stereo_to_ease_avhrr(da_in.sel(year=y).values))
    out_array = np.stack(out_da_list, axis=0)

    coords = {
        'year': da_in.year,
        'x': ease_proj.get_x_coords(),
        'y': ease_proj.get_y_coords()
    }

    return xr.DataArray(out_array, coords=coords, dims=['year', 'y', 'x'], attrs=da_in.attrs)


def regrid_Dataset(ds):
    return xr.Dataset({ds[v].name: regrid_DataArray(ds[v]) for v in ds.data_vars})


def main(fileout):

    dataset_ps = read_ps(DATADIR)

    dataset_ease = regrid_Dataset(dataset_ps)
    dataset_ease.to_netcdf(os.path.join(DATADIR, fileout))


if __name__ == "__main__":
    fileout = 'melt_and_freeze_onset_1979to2018.nc'
    main(fileout)