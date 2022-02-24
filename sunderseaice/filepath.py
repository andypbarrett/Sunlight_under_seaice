"""Filepaths for sunderice.  These will need to be edited"""

from pathlib import Path
from collections import namedtuple
import datetime as dt

HOME = Path.home()
ICESAT2_PATH = HOME / 'Data' / 'ICESat-2'

GRANULE_LIST_PATH = HOME / 'src' / 'SunlightUnderSeaIce' / 'data'

GranuleInfo = namedtuple('GranuleInfo', ['product', 'hemisphere',
                                         'date', 'rgt', 'cycle', 'segment',
                                         'version', 'revision'])


def parse_granule_id(granule_id):
    fields = granule_id.split('_')
    product, hemisphere = fields[0].split('-')
    date = dt.datetime.strptime(fields[1], '%Y%m%d%H%M%S')
    rgt = fields[2][:4]
    cycle = fields[2][4:6]
    segment = fields[2][6:]
    version = fields[3]
    revision = fields[4]
    return GranuleInfo(product, hemisphere, date, rgt, cycle, segment, version, revision)


def get_icesat2_filepath(granule_url):
    """Returns path to local granule file"""
    granule_id = Path(granule_url).name
    info = parse_granule_id(Path(granule_url).stem)
    return ICESAT2_PATH / info.product / f"v{info.version}" / granule_id
