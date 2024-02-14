import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np
import itertools

import pathlib
import set_ID

import pvlib
from pvlib.location import Location

import warnings
warnings.filterwarnings('ignore')


year = '2092'


prepro_data_path = f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/REdiff_runs/ssp245/'
base_file=xr.open_mfdataset(f'{prepro_data_path}tas_prepro_209.nc').sel(member=1).sel(time=year)

_file = xr.zeros_like(base_file)
_file = _file.load()


for lat in _file['lat']:
    for lon in _file['lon']:
        mask = (_file.coords["lat"] == lat) & (_file.coords["lon"] == lon)

        site = Location(lat.values.item(), lon.values.item(), 'UTC', 100) # latitude, longitude, time_zone, altitude, name
        times = pd.date_range(year+'-01-01 00:00:00', year+'-12-31 23:59:00', closed='left', freq='H', tz=site.tz)
        solpos = site.get_solarposition(times)
        sza_data = solpos['zenith']#[1:]
#        azi_data = solpos['azimuth']

        _file['tas'] = xr.where(mask, sza_data.values, _file['tas'])
       # _file['tas'] = xr.where(mask, azi_data.values, _file['tas'])

    
_file.rename({'tas':'sza'}).to_netcdf(f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/sza_{year}.nc')


print('--------------------0000_sza_calc.py ran successfully--------------------')
