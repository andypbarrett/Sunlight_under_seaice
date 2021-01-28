import cartopy.crs as ccrs
import numpy as np
import xarray as xr

from sunderseaice.readers import grads

# NSIDC-EASE North projection: see http://epsg.io/3408
AuthalicSphere1924 = ccrs.Globe(semimajor_axis=6371228., semiminor_axis=6371228.)
NSIDC_EASE_North = ccrs.LambertAzimuthalEqualArea(central_latitude=90., central_longitude=0., globe=AuthalicSphere1924)
extent = [-4524683.8, 4524683.8, -4524683.8, 4524683.8]

# Geographic projection for latitude and longitudes
GEO_PROJ = ccrs.PlateCarree(globe=AuthalicSphere1924)

# Na25 grid parameters
numberColumnsX, numberRowsY = 361, 361
cellSizeX, cellSizeY = 25067.5, 25067.5
upperLeftCornerX = -4524683.8
upperLeftCornerY = -4524683.8


def read(gdatfile, ctlfile):
    '''Reads SnowModel data into an xarray.DataArray'''
    coordX = [upperLeftCornerX + ((i + 0.5) * cellSizeX)
              for i in range(numberColumnsX)]
    coordY = [upperLeftCornerY + ((i + 0.5) * cellSizeY)
              for i in range(numberRowsY)]

    dataArray = grads.read(gdatfile, ctlfile=ctlfile).squeeze()
    dataArray.coords['x'] = coordX  # ctl uses row-col index
    dataArray.coords['y'] = coordY

    return dataArray


def add_ease_north_latlon(ds):
    """Adds 2D lat and lon grids for EASE-North"""
    x2d, y2d = np.meshgrid(ds.x, ds.y)
    geo_coords = GEO_PROJ.transform_points(NSIDC_EASE_North, x2d, y2d)
    lon = geo_coords[:, :, 0]
    lat = geo_coords[:, :, 1]

    ds["lon"] = xr.DataArray(lon, coords=[ds.x, ds.y], dims=["x", "y"])
    ds["lat"] = xr.DataArray(lat, coords=[ds.x, ds.y], dims=["x", "y"])

    ds = ds.set_coords(["lat", "lon"])

    return ds
