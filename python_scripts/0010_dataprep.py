#script works for both PV and CSP
import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np
import sys

import pathlib
import importlib
from functools import reduce

# own packages
import data_prep.data_prep as dataprep
import set_ID

#print(sys.argv[1]) # G6solar

# place to save the processed files
raw_data_path = f'{set_ID.archive_path}{sys.argv[1]}_REdiff/'
prepro_data_path = f'{set_ID.scratch_path}CNRM_runs/RE_analysis/manual/preprocessed/REdiff_runs/{sys.argv[1]}/'

members = set_ID.members
year = set_ID.year


if set_ID.RE_type == 'PV':
    var_list = [
               'rsds',      
               'tas',
               'ua10m',
               'va10m',
               'rsdscs']
            #  'rsdsdiff']
elif set_ID.RE_type == 'CSP':
    var_list = ['rsds',
                'tas',
                'rsdsdiff']
else:
    print('need to indicate which type of RE (PV or CSP)')



ds_raw = dict()
single_members = dict()

wind_vars=['ua10m', 'va10m']


for el in var_list:
    print(el)
    for i in members:
        single_members[str(i)] = xr.open_mfdataset(raw_data_path+'AOESM_'+sys.argv[1]+'_REdiff_r'+str(i)+'/merged/'+el+'_HOM1hr_*_'+year+'*-*.nc',
                                                   combine = 'nested',
                                        engine="netcdf4")
        
        if el in wind_vars: 
            if year == '201':
                single_members[str(i)] = single_members[str(i)].sel(time=slice(year+"5-01-01 01", str(int(year)+1)+"5-01-01 00"))
            elif year == '202':
                single_members[str(i)] = single_members[str(i)].sel(time=slice(year+"5-01-01 01", str(int(year)+1)+"0-01-01 00"))
            else:
                single_members[str(i)] = single_members[str(i)].sel(time=slice(year+"0-01-01 01", str(int(year)+1)+"0-01-01 00"))
        
        try:
            single_members[str(i)] = single_members[str(i)].drop('time_bnds')
        except:
            single_members[str(i)] = single_members[str(i)].drop('time_bounds')
        
#     for i in members:
    

    ds_raw[el] = xr.concat([single_members['1'],single_members['2'],single_members['3'],single_members['4'], single_members['5'], single_members['6']], dim='member')
    
    #ds_raw[el].load()

print('data loaded')

def data_prep(ds_in):
    ds_ = dict()
    for var in var_list:
        if var == 'tas':
            ds_[var] = dataprep.change_T_unit(ds_in[var])
        else:
            ds_[var] = ds_in[var]
  #      ds_[var] = dataprep.area_weighting(ds_[var]) #do area weighting at the end
  #      ds_[var] = dataprep.ensemble_mean(ds_[var])  #take ensemble mean also at the end
        # keep attributes
        ds_[var].attrs = ds_in[var].attrs
    return ds_

ds = data_prep(ds_raw)

# change time coordinates to make them correspond to each other
if set_ID.RE_type == 'PV':
    
    if year in ('201', '202'):
            ds['ua10m'].coords['time'] = pd.date_range(set_ID.year[:3]+'5'+'-01-01', periods=ds['tas']['time'].values.shape[0],freq='H')
            ds['va10m'].coords['time'] = pd.date_range(set_ID.year[:3]+'5'+'-01-01', periods=ds['tas']['time'].values.shape[0],freq='H')
    else:
        ds['ua10m'].coords['time'] = pd.date_range(set_ID.year[:3]+'0'+'-01-01', periods=ds['tas']['time'].values.shape[0],freq='H')
        ds['va10m'].coords['time'] = pd.date_range(set_ID.year[:3]+'0'+'-01-01', periods=ds['tas']['time'].values.shape[0],freq='H')
    ds['tas'] = ds['tas'].resample(time='H').sum()
    ds['rsds'] = ds['rsds'].resample(time='H').sum()
    ds['rsdscs'] = ds['rsdscs'].resample(time='H').sum()
#    ds['rsdsdiff'] = ds['rsdsdiff'].resample(time='H').sum()
        
elif set_ID.RE_type == 'CSP':
    ds['tas'] = ds['tas'].resample(time='H').sum()
    ds['rsds'] = ds['rsds'].resample(time='H').sum()
    ds['rsdsdiff'] = ds['rsdsdiff'].resample(time='H').sum()
    ds['rsdsdir'] = (ds['rsds']['rsds'] - ds['rsdsdiff']['rsdsdiff']).to_dataset(name ='rsdsdir')
    var_list.append('rsdsdir')
else:
    print('something went wrong')


# save processed files
for v in var_list:
    save_dir= prepro_data_path
    save_name=v+'_prepro_'+set_ID.year+'.nc'
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
    try:
        os.remove(save_dir + save_name)
    except:
        pass   

    ds[v].to_netcdf(save_dir+save_name)
    print(save_dir+save_name)

print('--------------------1_dataprep.py ran successfully--------------------')
