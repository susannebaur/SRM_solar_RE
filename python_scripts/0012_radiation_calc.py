import sys
import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np

import pathlib

import set_ID


prepro_data_path = set_ID.scratch_path+'CNRM_runs/RE_analysis/manual/preprocessed/REdiff_runs/'+sys.argv[1]+'/'
tech_pot_path = set_ID.solar_path+'/PV/tech_pot/'+sys.argv[1]+'/'
sensitivity_setting = set_ID.sensitivity_setting

var_list = ['rsds',
            'rsdsdiff'
           ]

### load in PREPROCESSED data (script data_prep.ipynb)

ds = dict()
for el in var_list:
    print(prepro_data_path+el+'_prepro_'+set_ID.year+'.nc')
    ds[el] = xr.open_mfdataset(prepro_data_path+el+'_prepro_'+set_ID.year+'.nc',
                                        engine="netcdf4", chunks={'time': 365})
   # ds[el].load()
sza = xr.open_dataset(f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/sza_209.nc', engine='netcdf4')['sza']
azi = xr.open_dataset(f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/azi_209.nc', engine='netcdf4')['azi']

print('data loaded')

cos_sza = np.cos(np.radians(sza))
sin_sza = np.sin(np.radians(sza))
cos_azi = np.cos(np.radians(azi))
cos_beta = np.cos(np.radians(ds['rsds'].lat))
sin_beta = np.sin(np.radians(ds['rsds'].lat))


# calculate rsdsdir and export for CSP
ds['rsdsdir'] = (ds['rsds']['rsds'] - ds['rsdsdiff']['rsdsdiff']) / cos_sza.where(cos_sza > 0.05, other=1)

cos_PV = cos_sza * cos_beta + sin_sza * abs(sin_beta) * abs(cos_azi)

ds['rsdsPV'] = ds['rsdsdir'] * cos_PV + ((1 + cos_beta)/2) * ds['rsdsdiff']['rsdsdiff']


# convert to dataset and export
ds['rsdsPV'].to_dataset(name='rsdsPV').to_netcdf(f'{prepro_data_path}rsdsPV_prepro_{set_ID.year}.nc')
print(f'{prepro_data_path}rsdsPV_prepro_{set_ID.year}.nc')
ds['rsdsdir'].to_dataset(name='rsdsdir').to_netcdf(f'{prepro_data_path}rsdsdir_prepro_{set_ID.year}.nc')
print(f'{prepro_data_path}rsdsdir_prepro_{set_ID.year}.nc')


print('--------------------0012_radiation_calc.py ran successfully--------------------')





