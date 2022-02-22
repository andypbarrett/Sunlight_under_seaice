"""Searches for ICESat-2 products that intersect with Polarstern
   MOSAiC drift"""
from pathlib import Path
import datetime as dt

import sunderseaice.download.nsidc_download as cmr

from sunderseaice.download.polarstern import (floe2,
                                              read_polarstern_track,
                                              get_search_radius,
                                              shapely_to_cmr)


def search_for_one_day(search_date, geometry, product, version):
    """Searches for a single day"""
    start_date, end_date = (search_date - dt.timedelta(hours=12),
                            search_date + dt.timedelta(hours=12))
    results = cmr.cmr_search(
        product,
        version,
        start_date.isoformat(),  # CMR API expects iso format date strings
        end_date.isoformat(),
        polygon=shapely_to_cmr(geometry),
        verbose=False,
    )
    if len(results) > 2:
        raise ValueError("More than one value returned by search")
    return results


def main(product, version, radius=20000., resolution=3, verbose=False,
         outdir='.'):
    """Search for ICESat-2 product granules on Polarstern drift and write to
       csv.

    :product: product short name.  (str) E.g. ATL03
    :version: product version. (str)
    :radius: search radius in meters (float).  Default 20000 m.
    :resolution: vertex resolution for polygon (int).  Default 3.
    """
    if verbose: print("Reading Polarstern drift track")
    gdf = read_polarstern_track()
    gdf = gdf[floe2.start:floe2.end]
    gdf = gdf[(gdf.index.hour == 12) & (gdf.index.minute == 0)] # Get midday location

    gdf_buffer = get_search_radius(gdf, radius=radius,
                                   resolution=resolution)
    npoints = len(gdf_buffer)

    if verbose: print("Searching for granules")
    gdf["granule"] = None
    gdf["metadata"] = None
    for search_date, geometry in gdf_buffer.iteritems():
        results = search_for_one_day(search_date,
                                     geometry,
                                     product=product,
                                     version=version)
        if len(results) > 0:
            if results[0].endswith('.h5'):
                gdf.loc[search_date, "granule"] = results[0]
            else:
                raise ValueError(f"Expects first result to be path to HDF5 (.h5) got {results[0]}")
            if results[1].endswith('.xml'):
                gdf.loc[search_date, "metadata"] = results[1]
            else:
                raise ValueError(f"Expects second result to be metadata (.xml) got {results[1]}")
    gdf = gdf.dropna()
    ngranules = len(gdf)

    if verbose: print(f"Found {ngranules} for {npoints}")

    csvfile = Path(outdir) / f"{product}.{version}.polarstern.floe2.granules_list.csv"
    if verbose: print(f"Writing list to {csvfile}")
    print(gdf)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Search for ICESat-2 tracks "
                                     "along Polarstern MOSAic drift")
    parser.add_argument("product", type=str,
                        help="Short name for product. E.g. ATL07")
    parser.add_argument("version", type=str,
                        help="Product version")
    parser.add_argument("--search_radius", type=float, default=20000.,
                        help="radius of circle region to search")
    parser.add_argument("--resolution", type=int, default=3,
                        help="resolution of search polygon (default=3)")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    main(args.product,
         args.version,
         radius=args.search_radius,
         resolution=args.resolution,
         verbose=args.verbose)
