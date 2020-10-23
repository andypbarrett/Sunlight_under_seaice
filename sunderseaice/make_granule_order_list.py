# Generates a list of granule https urls for IceSAT-2 data
# Follow instructions in https://nsidc.org/support/faq/what-options-are-available-bulk-downloading-data-https-earthdata-login-enabled
import os
import urllib.parse as urlparse
import re
import datetime as dt


ROOT_HTTPS_URL = "https://n5eil01u.ecs.nsidc.org/ATLAS"

granules = [
    "ATL03_20190726213326_04400404_003_01.h5",
    "ATL03_20190726213835_04400405_003_01.h5",
    "ATL03_20190805215948_05930404_003_01.h5",
    ]


def gran_ID(gran):
    """
    Parses granule id to get parameters
    """
    
    rx = re.compile('(ATL\d{2})_(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})'
           '(\d{2})_(\d{4})(\d{2})(\d{2})_(\d{3})_(\d{2}).h5$')

    (product,
     year,
     month,
     day,
     hour,
     minute,
     second,
     reference_ground_track,
     orbital_cycle,
     segment,
     version,
     revision) = rx.findall(gran).pop()
    
    result = {
        "producer_granule_id": gran,
        "product": product,
        "version": version,
        "timestamp": dt.datetime(int(year), int(month), int(day),
                                 int(hour), int(minute), int(second)),
        }
    return result


def make_granule_order_list():

    urldict = urlparse.urlparse(ROOT_HTTPS_URL)
    
    for gran in granules:
        gran_dict = gran_ID(gran)
        path = os.path.join(
            urldict[2],
            f"{gran_dict['product']}.{gran_dict['version']}",
            f"{gran_dict['timestamp'].strftime('%d.%m.%d')}",
            gran_dict['producer_granule_id']
        )
        print(path)
        
                     

        
if __name__ == "__main__":
    make_granule_order_list()
