# Reads grads files
import os
import re
import datetime as dt

import numpy as np
import xarray as xr

def make_ctlfn(gradsfn):
    return gradsfn.replace('.gdat', '.ctl')
    

def check_ctl_exists(ctlfn):
    assert os.path.exists(ctlfn), f'Cannot find {ctlfn} in data directory'


def parsedate(s):
    if re.search('\d{2}Z', s):
        return dt.datetime.strptime(s, '%HZ%d%b%Y')
    else:
        return dt.datetime.strptime(s, '%d%b%Y')

    
def parse_tincr(s):
    m = re.search('(\d+)([a-zA-Z]{2})', s)
    assert m, 'Timestep unknown'
    step, unit = m.groups()

    assert unit in ['hr', 'dy', 'mo'], f'Unknown unit for timestep: {unit}'  
    if unit == 'dy':
        return dt.timedelta(days=int(step))
    elif unit == 'mo':
        return dt.timedelta(months=int(step))
    elif unit == 'hr':
        return dt.timedelta(hours=int(step))
    
        
def parse_xyzdim(line):
    maxfield = 4
    castas = [int, str, float, float]
    fields = [c(e) for c, e in zip(castas, line.split())]
    fields = fields + [None for i in range(maxfield - len(fields))]  # Deals with missing increment field
    return dict(zip(["ndim", "scale", "start", "increment"], fields))


def parse_tdim(line):
    fields = line.split()
    return dict(zip(["ndim", "scale", "start", "increment"],
                    [int(fields[0]), fields[1].upper(), parsedate(fields[2]), parse_tincr(fields[3])]))
                         
                        
def read_ctl(ctlfn):
    endvar = re.compile('endvars', re.IGNORECASE)
    ctldict = {}
    with open(ctlfn) as f:
        for line in f.readlines():
            if endvar.search(line):
                break
            key, value = line.strip().split(None, 1)
            ctldict[key.upper()] = value
    return ctldict


def parse_ctl(ctl):
    ctl['XDEF'] = parse_xyzdim(ctl['XDEF'])
    ctl['YDEF'] = parse_xyzdim(ctl['YDEF'])
    ctl['ZDEF'] = parse_xyzdim(ctl['ZDEF'])
    ctl['TDEF'] = parse_tdim(ctl['TDEF'])                 
    return ctl
                     
                  
def get_shape(ctl):
    return (ctl['TDEF']['ndim'],
            ctl['XDEF']['ndim'],
            ctl['YDEF']['ndim'],
            ctl['ZDEF']['ndim'])


def calc_end(dimdef):
    '''Calculate end of dimension range'''
    incr = dimdef['increment'] if dimdef['increment'] else 0.
    return dimdef['start'] + (incr * dimdef['ndim'])


def generate_xyzdim(dimdef):
    '''Generate a dimension'''
    if dimdef['ndim'] > 1:
        dim = np.arange(dimdef['start'], calc_end(dimdef), dimdef['increment'])
    else:
        dim = [dimdef['start']]
    return dim
    
    
def generate_tdim(dimdef):
    '''Generate time dimension'''
    return [dimdef['start'] + dimdef['increment'] * i for i in np.arange(0, dimdef['ndim'])]

    
def read_gdat(gradsfile, shape):
    '''Reads a .gdat file'''
    data = np.fromfile(gradsfile, 'float32').reshape(*shape)
    return data
    
    
def read_grads(gradsfile, ctlfile=None):
    '''Reads a grads file

    gradsfile - path the a gdat file

    ctlfile - path to ctlfile.  If ctlfile is not passed to function a
              file with the same root name is used.  If this is not present then
              an exception is raised.

    '''

    if not ctlfile:
        ctlfile = make_ctlfn(gradsfile)
    check_ctl_exists(ctlfile)

    ctl = read_ctl(ctlfile) # Put this in a class
    ctl = parse_ctl(ctl)
    shape = get_shape(ctl)

    data = read_gdat(gradsfile, shape)
    data = np.where(data > float(ctl['UNDEF']), data, np.nan)
    x = generate_xyzdim(ctl['XDEF'])
    y = generate_xyzdim(ctl['YDEF'])
    z = generate_xyzdim(ctl['ZDEF'])
    t = generate_tdim(ctl['TDEF'])
    
    da = xr.DataArray(data, coords={'time': t, 'x': x, 'y': y, 'z': z},
                      dims=['time', 'x', 'y', 'z']).chunk({'time': 100})
    
    return da
