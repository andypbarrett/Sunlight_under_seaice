# Tools to regrid melt onset
import numpy as np

# import rasterio
# from rasterio.crs import CRS as rcrs
from rasterio import warp as rio_warp

from sunderseaice.maps.projections import EASEGridAVHRRNorth25, NSIDCNorthPolarStereo25


def north_polar_stereo_to_ease_avhrr(ingrid):
    src_proj = NSIDCNorthPolarStereo25()
    dst_proj = EASEGridAVHRRNorth25()

    # src_crs = rcrs.from_string(src_proj['crs'])
    # src_transform = get_transform(src_proj)

    # dst_crs = rcrs.from_string(dst_proj['crs'])
    # dst_transform = get_transform(dst_proj)

    outgrid = np.empty(dst_proj.shape, dtype=float)

    rio_warp.reproject(source=ingrid.astype(float),
                       src_crs=src_proj.rasterio_crs,
                       src_nodata=np.nan,
                       src_transform=src_proj.transform,
                       destination=outgrid,
                       dst_transform=dst_proj.transform,
                       dst_crs=dst_proj.rasterio_crs,
                       dst_nodata=np.nan,
                       SOURCE_EXTRA=0,
                       resampling=rio_warp.Resampling.nearest)

    return outgrid
