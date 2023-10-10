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

solar_path = set_ID.solar_path
RE_type = set_ID.RE_type


plots_path = f'{solar_path}{RE_type}/plots/LED/'
data_path = f'{solar_path}{RE_type}/tech_pot_suit_prot_pop/'

scens = set_ID.scens
area_setting = '_cw'

data = dict()

for year in ['201', '209']:
    for scen in scens:   
        data[f'{scen}_{year[:3]}'] = xr.open_dataset(f'{data_path}{scen}/{scen}_{RE_type}_{year}_weekly_suit_prot_pop_{area_setting}.nc',
                                        engine="netcdf4")
    

qt_value=0.2

def LED_calculation(scen):
    ########## get quantiles
    data_prepped = dict()

    # get the 20th percentile for each season
    data_interim = data[scen+'_201'].groupby('time.season')#.quantile(qt_value, dim=qt_dim)
    ######### because of chunking error cannot do the quantile calc and have to do these lines below ################
    l = list()
    for name, group in data_interim:
        group=group.chunk(dict(time=-1))
        group = group.quantile(qt_value, dim='time')
        group.coords['season'] = name
        l.append(group)
    data_prepped[scen+'_201'] = xr.concat(l, dim='season')
    data_prepped[scen+'_201'] = data_prepped[scen+'_201'].mean('member')

    data_prepped[scen+'_201'] = data_prepped[scen+'_201'].load()

    ########## get count of days
    low_energy_count_year = dict()
    for year in list(range(2095,2099+1)):
    #for year in list(range(2090,2099+1)):
        data_year = data[scen+'_209'].sel(time=str(year))

        # Calculate how many days per season are below the 20th percentile in this specific year
        low_energy_count_sea = dict()
        for sea in set_ID.seasons:
            # get 2015-24 value per season
            q_val_pres = data_prepped[scen+'_201']['tech_pot'].sel(season=sea)
            # get the seasonal data of the year
            data_sea = data_year.sel(time=data_year['time.season']==sea)['tech_pot']

            # count days where seasonal data is below the 20th percentile of seasonal 201 average
            low_energy_count_sea[sea] = data_sea.where(data_sea<q_val_pres).count(dim='time')
        # add days of all 4 seasons together
        low_energy_count_year[str(year)] = (low_energy_count_sea['DJF'].sum('member') + low_energy_count_sea['MAM'].sum('member') + low_energy_count_sea['JJA'].sum('member') + low_energy_count_sea['SON'].sum('member'))/6
        

        #save
        save_name=f'LED_{year}{area_setting}.nc'
        save_dir = f'/data/scratch/globc/baur/RE_analysis/solar/{RE_type}/LED/{scen}/'
        pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
        try:
            os.remove(save_dir + save_name)
        except:
            pass   

        low_energy_count_year[str(year)].to_netcdf(save_dir + save_name)
        print(save_dir + save_name)


for scen in scens:
    LED_calculation(scen)
    
    ### take mean over those 10 years   
    #low_energy_count = (low_energy_count_year['2095']+low_energy_count_year['2096']+low_energy_count_year['2097']+low_energy_count_year['2098']+low_energy_count_year['2099'])/5
    #low_energy_count = (low_energy_count_year['2098']+low_energy_count_year['2099'])/2


print('--------------------0061_LED_calc.py ran successfully--------------------')

    
