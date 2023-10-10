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
            'tas',
            'va10m',
            'ua10m',
            'rsdscs',
           # 'rsdsdiff']
		]

### load in PREPROCESSED data (script data_prep.ipynb)

ds = dict()
for el in var_list:
    print(prepro_data_path+el+'_prepro_'+set_ID.year+'.nc')
    ds[el] = xr.open_mfdataset(prepro_data_path+el+'_prepro_'+set_ID.year+'.nc',
                                        engine="netcdf4", chunks={'time': 365})
   # ds[el].load()

print('data loaded')

#### PV potential calculation
# calculation from Gernaat et al. 2020 Nature paper
# A: suitability fraction (we add this later in 005)
# a: area of cell [m2] 150km (nominal resol 140km) 

A = 1 # suitability fraction -> added later 
a = 1 # (we need the area of the cell of the IMAGE grid) but this is added later
nLPV = 0.47
nPanel = 0.268 
PR = 0.85


#def PV_tech_pot(scen, RSDS, A, a, nLPV, nPanel, TAS , PR, ua10m, va10m, RSDScs, RSDSdiff):
def PV_tech_pot(scen, RSDS, A, a, nLPV, nPanel, TAS , PR, ua10m, va10m, RSDScs):
  
    if sensitivity_setting == 'fixed_temp':
        TAS=25
    elif sensitivity_setting == 'fixed_rad':
        RSDS = 1000
    elif sensitivity_setting == 'cloudy_sky':
        RSDSdiff = RSDScs - RSDS
        RSDS = RSDSdiff
        TAS=25
    elif sensitivity_setting == 'clear_sky':
        RSDS = RSDScs
        TAS=25
    elif sensitivity_setting == 'weights':
        RSDS = 1000
        TAS=25
        #set wind == 1 
        ua10m_zero=xr.zeros_like(ua10m)
        va10m_zero=xr.zeros_like(va10m)
        ua10m = ua10m_zero.where(ua10m_zero!=0, other=1)
        va10m = va10m_zero.where(va10m_zero!=0, other=1)
#    elif sensitivity_setting == 'rsdsdiff':
#        RSDS = RSDSdiff
    
    Ti = 4.3 + 0.943 * TAS + 0.028 * RSDS - 1.528 * (np.sqrt(ua10m**2 + va10m**2))
    nPV = nPanel * (1 + (-0.005)*(Ti - 25))
    tech_pot = (RSDS/1000) * A * a * nLPV * nPV * PR ##turn W/m2 into kWh/m2
    
    tech_pot = tech_pot.to_dataset(name='tech_pot')
    print('tech pot calculation successful')
  #save as file
    save_name = f'tech_pot_{scen}_{set_ID.RE_type}_{set_ID.year}.nc'
    if sensitivity_setting != '':
        save_dir = f'{set_ID.solar_path}PV/sensitivity_analysis/{sensitivity_setting}/tech_pot/{scen}/'
    else:
        save_dir = tech_pot_path
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
    try:
        os.remove(save_dir + save_name)
    except:
        pass        
        #save file
    tech_pot.to_netcdf(save_dir + save_name)
    print(save_dir+save_name)
    
    return tech_pot 

PV_tech_pot(sys.argv[1], ds['rsds']['rsds'], A, a, nLPV, nPanel, ds['tas']['tas'], PR,
                        ds['ua10m']['ua10m'], ds['va10m']['va10m'], ds['rsdscs']['rsdscs'], 
 #                       ds['rsdsdiff']['rsdsdiff'])
                )

print('--------------------2_PV_tech_pot.py ran successfully--------------------')
