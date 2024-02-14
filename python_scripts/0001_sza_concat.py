import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np
import itertools

import pathlib
import set_ID

import warnings
warnings.filterwarnings('ignore')


# load in example data to match sza time dimension to
prepro_data_path = set_ID.scratch_path+'CNRM_runs/RE_analysis/manual/preprocessed/REdiff_runs/ssp245/'
tech_pot_path = set_ID.solar_path+'/PV/tech_pot/ssp245/'
var_list = ['rsds']

ds = dict()
for el in var_list:
    print(prepro_data_path+el+'_prepro_209.nc')
    ds[el] = xr.open_mfdataset(prepro_data_path+el+'_prepro_'+set_ID.year+'.nc',
                                        engine="netcdf4", chunks={'time': 365})

# load in sza and azi data
sza = dict()
azi=dict()
for ti in [0,2]: # 0000_sza_calc.py needs to be run for 2090 and 2092
    sza[ti] = xr.open_dataset(f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/sza_209{str(ti)}.nc', engine='netcdf4')
    azi[ti] = xr.open_dataset(f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/azi_209{str(ti)}.nc', engine='netcdf4')

print('data loaded')


# copy sza and azi data to the other years of the decade (except 2092 and 2096 -> gregorian calendar)
for t in [1,3,4,5,6,7,8,9]:
    # match 2096 to 2092
    if t == 6:
        sza[t] = sza[2].assign_coords({"time": ds['rsds'].sel(time='209'+str(t)).time})
        azi[t] = azi[2].assign_coords({"time": ds['rsds'].sel(time='209'+str(t)).time})
    else:
        sza[t] = sza[0].assign_coords({"time": ds['rsds'].sel(time='209'+str(t)).time})
        azi[t] = azi[0].assign_coords({"time": ds['rsds'].sel(time='209'+str(t)).time})

# concat the data together
sza_data = xr.concat([sza[0], sza[1], sza[2], sza[3], sza[4], sza[5], sza[6], sza[7], sza[8], sza[9]], dim='time')
azi_data = xr.concat([azi[0], azi[1], azi[2], azi[3], azi[4], azi[5], azi[6], azi[7], azi[8], azi[9]], dim='time')

sza_data.to_netcdf(f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/sza_209.nc')
print(f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/sza_209.nc')
azi_data.to_netcdf(f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/azi_209.nc')
print(f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/azi_209.nc')

print('--------------------0001_sza_concat.py ran successfully--------------------')





