from rasterio import Affine
from rasterio.crs import CRS

Polar_Stereo_North = "+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 " \
           "+a=6378273 +b=6356889.449 +units=m +no_defs"

EASE_Grid_North = "+proj=laea +lat_0=90 +lon_0=0 +x_0=0 +y_0=0 " \
                "+a=6371228 +b=6371228 +units=m +no_defs"

NSIDC_North_Polar_Stereographic_25 = {
    'name': 'NSIDC North Polar Stereographic 25 km grid',
    'epsg': '3411',
    'pixel_width': 25000,
    'pixel_height': -25000,
    'crs': Polar_Stereo_North,
    'bounds': [-3850000.000, 3750000., -5350000., 5850000.000],
    'shape': (448, 304),
}


EASE_Grid_AVHRR_North_25 = {
    'name': 'AVHRR 25km EASE-Grid Northern Hemisphere',
    'epsg': '', 
    'pixel_width': 25067.5,
    'pixel_height': -25067.5,
    'crs': EASE_Grid_North,
    'bounds': [-4524683.8, 4524683.8, -4524683.8, 4524683.8],
    'shape': (361, 361),
}


class Projection():

    def __init__(self, projection_dict):
        self.name = projection_dict['name']
        self.epsg = projection_dict['epsg']
        self.pixel_height = projection_dict['pixel_height']
        self.pixel_width = projection_dict['pixel_width']
        self.row_rotation = 0.
        self.column_rotation = 0.
        self.crs = projection_dict['crs']
        self.bounds = projection_dict['bounds']
        self.shape = projection_dict['shape']

        self.transform = Affine(self.pixel_width,
                                self.row_rotation,
                                self.bounds[0],
                                self.column_rotation,
                                self.pixel_height,
                                self.bounds[3])

        self.rasterio_crs = CRS.from_proj4(self.crs)
        
    def __repr__(self):
        return f'Projection: {self.name} (EPSG: {self.epsg})'


    def get_x_coords(self):
        x, _ = zip(*[self.transform * (i+0.5, 0.5) for i in range(self.shape[1])])
        return list(x)


    def get_y_coords(self):
        _, y = zip(*[self.transform * (0.5, j+0.5) for j in range(self.shape[0])])
        return list(y)
    

class EASEGridAVHRRNorth25(Projection):
    '''
    Rasterio CRS definition of EASE Grid AVHRR North 25 km projection

    https://nsidc.org/data/ease
    '''
    def __init__(self):
        super(EASEGridAVHRRNorth25, self).__init__(EASE_Grid_AVHRR_North_25)


class NSIDCNorthPolarStereo25(Projection):
    '''
    NSIDC North Polar Stereographic 25 km Grid

    https://nsidc.org/data/polar-stereo/ps_grids.html
    '''
    def __init__(self):
        super(NSIDCNorthPolarStereo25, self).__init__(NSIDC_North_Polar_Stereographic_25)
    


    
                                   
