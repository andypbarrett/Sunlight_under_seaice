import readers.snowmodel as snowmodel
from readers.snowmodel import NSIDC_EASE_North

from pathlib import Path


global_attributes = {
    'title': 'snow depth on sea ice',
    'institution': 'CIRA, Colorado State University',
    'creator': 'Glen.Liston@colostate.edu',
    'source': 'SnowModel-LG,',
    'projection': 'NSIDC EASE',
    'proj4_string': NSIDC_EASE_North.proj4_init,
    'crs': 'EPSG:3408',
    'reference': ('Liston, G. E., Itkin, P., Stroeve, J., Tschudi, M., Stewart, J. S., & Pedersen, S. H., et al. (2020). '
                  'A Lagrangian snow‐evolution system for sea‐ice applications (SnowModel‐LG): Part I—Model description. '
                  'Journal of Geophysical Research: Oceans, 125, e2019JC015913. https://doi.org/10.1029/2019JC015913'),
}

lon_attributes = {
    'long_name': 'longitude',
    'units': 'degrees_east'
} 

lat_attributes = {
    'long_name': 'latitude',
    'units': 'degrees_north'
}

time_attributes = {
    'long_name': 'time',
}

x_attributes = {
    'long_name': 'x-coordinate of projection',
    'standard_name': 'projection_x_coordinate',
    'units': 'm',    
}

y_attributes = {
    'long_name': 'y-coordinate of projection',
    'standard_name': 'projection_y_coordinate',
    'units': 'm',    
}

snow_depth_attributes = {
    'long_name': 'snow depth',
    'standard_name': 'surface_snow_thickness_where_sea_ice',
    'units': 'm'
}

snow_density_attributes = {
    'long_name': 'snow density',
    'standard_name': 'snow_density_where_sea_ice',
    'units': 'kg m-3'
}


def add_variable_attributes(ds, variable_name):
    if variable_name == "snow_depth":
        ds[variable_name].attrs = snow_depth_attributes
    elif variable_name == "snow_density":
        ds[variable_name].attrs = snow_density_attributes
    else:
        raise ValueError(f"Attribute dictionary for {variable_name} does not exist. "
                         f"No attributes added to {variable_name}\n"
                         f"Add variable attribute dictionary to gdat_to_netcdf.py")

    
def add_attributes(ds, variable_name, reanalysis):
    """
    Adds global and variable attributes
    
    :ds: xarray.Dataset
    :variable_name: name of variable
    """
    global_attributes['source'] = global_attributes.get('source', '') + reanalysis
    ds.attrs = global_attributes

    try:
        add_variable_attributes(ds, variable_name)
    except ValueError as error:
        print(error)

    if "x" in ds.coords:
        ds.x.attrs = x_attributes
    else:
        raise KeyError("x is not a coordinates in xarray.Dataset")
    
    if "y" in ds.coords:
        ds.y.attrs = y_attributes
    else:
        raise KeyError("y is not a coordinate in xarray.Dataset")

    if "lat" in ds.coords:
        ds.lat.attrs = lat_attributes
    else:
        raise KeyError("lat is not a coordinate in xarray.Dataset")

    if "lon" in ds.coords:
        ds.lon.attrs = lon_attributes
    else:
        raise KeyError("lon is not a coordinate in xarray.Dataset")

    if "time" in ds.coords:
        ds.time.attrs = time_attributes
    else:
        raise KeyError("time is not a coordinate in xarray.Dataset")
    

def write_to_netcdf(ds, outfile):
    encoding = {
        'snow_depth': {
            'zlib': True,
            'complevel': 9,
            'chunksizes': (100, 361, 361),
            '_FillValue': -9999.99
            },
        }
    ds.load()  # Speeds up write if loaded first
    ds.to_netcdf(outfile, encoding=encoding)


def gdat_to_netcdf(datafile, ctlfile, outfile, variable_name, reanalysis, verbose=False):
    """
    Converts gdat formatted file to a CF compliant netcdf
    
    :datafile: path to gdat file
    :ctlfile: path to ctl file
    :outfile: path to output netcdf file
    :variable_name: name of variable (currently snow_depth or snow_density)
    """

    if verbose: print(f"Converting {datafile} to {outfile}")

    if verbose: print(f"   reading {datafile}")
    ds = snowmodel.read(datafile, ctlfile).to_dataset(name=variable_name)
    ds = ds.drop("z")  # z-dimension is not needed here

    if verbose: print(f"   adding lat and lon grids")
    ds = snowmodel.add_ease_north_latlon(ds)

    if verbose: print(f"   adding attributes")
    add_attributes(ds, variable_name, reanalysis)

    if verbose: print(f"   writing to {outfile}")
    write_to_netcdf(ds, outfile)
    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert gdat files to netcdf for SnowModel output")
    parser.add_argument("gdatfile", type=str, help="Path to gdat file to convert")
    parser.add_argument("ctlfile", type=str, help="Path to ctl file associated with gdat file")
    parser.add_argument("ncfile", type=str, help="Path to netcdf file")
    parser.add_argument("variable_name", type=str, help="Name of variable to convert",
                        choices=["snow_depth", "snow_density"])
    parser.add_argument("reanalysis", type=str, help="Reanalysis used to force SnowModel",
                        choices=["ERA5", "MERRA2"])
    parser.add_argument("--verbose", "-v", action="store_true")
    
    args = parser.parse_args()
    
    gdat_to_netcdf(args.gdatfile, args.ctlfile, args.ncfile, args.variable_name, args.reanalysis,
                   verbose=args.verbose)
