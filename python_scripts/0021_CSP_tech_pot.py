# script calcualting CSP technical potential. Input is 1hr data output is daily

import sys
import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np

import pathlib

import set_ID


scen = sys.argv[1]

prepro_data_path = set_ID.scratch_path+'CNRM_runs/RE_analysis/manual/preprocessed/REdiff_runs/'+scen+'/'
tech_pot_path = set_ID.solar_path+'/CSP/tech_pot/'+scen+'/'
sensitivity_setting = set_ID.sensitivity_setting

var_list = ['tas',
            'rsdsdir'
           ]


### load in PREPROCESSED data (script data_prep.ipynb)

ds = dict()
for el in var_list:
    print(el)
    print(prepro_data_path+'/'+el+'_prepro_'+set_ID.year+'.nc')
    ds[el] = xr.open_mfdataset(prepro_data_path+'/'+el+'_prepro_'+set_ID.year+'.nc',
                                        engine="netcdf4", concat_dim='member', combine='nested', chunks={'time': 365})
    #ds[el].load()

print('data loaded')


# exclude areas with 10-year average daily rsdsdir of < 4000
rsdsdir_mask = ds['rsdsdir'].where(ds['rsdsdir'].resample(time='1D').sum().mean('time') > 3999) #with angled rsdsdir


#### CSP potential calculation
# calculation from Gernaat et al. 2020 Nature paper

A = 1
a = 1
nR = 0.4
nLCSP = 0.37


def CSP_tech_pot(RSDSdir, TAS):
    
    if sensitivity_setting == 'fixed_temp':
        TAS=25
    elif sensitivity_setting == 'fixed_rad':
        RSDSdir = 1000

    
    FLH = 1.83 * RSDSdir + 150    #Koeberle et al. 2015 calc
    nCSP = nR * (0.762 - (0.2125*(115-TAS)/RSDSdir.where(RSDSdir>0, other=1)))
    tech_pot = (RSDSdir/10) * A * a * nLCSP * (nCSP/FLH)  
    # turn Wh/m2 in kWh/m2
    tech_pot_kWh = tech_pot
    tech_pot_ds = tech_pot_kWh.to_dataset(name='tech_pot')
    print('tech pot calculation successful')
  #save as file
    save_name = 'tech_pot_'+scen+'_CSP_'+set_ID.year+'.nc'
    
    if sensitivity_setting != '':
        save_dir = f'{set_ID.solar_path}CSP/sensitivity_analysis/{sensitivity_setting}/tech_pot/{scen}/'
    else:
        save_dir = tech_pot_path

    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
    try:
        os.remove(save_dir + save_name)
    except:
        pass
        #save file
    tech_pot_ds.to_netcdf(save_dir + save_name)
    print(save_dir + save_name)
    return tech_pot


CSP_pot = CSP_tech_pot(rsdsdir_mask['rsdsdir'], ds['tas']['tas'])

print('--------------------2_CSP_tech_pot.py ran successfully--------------------')
