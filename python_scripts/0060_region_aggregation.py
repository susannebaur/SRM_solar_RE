import set_ID
from pathlib import Path

import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np
import itertools
import matplotlib.pyplot as plt

import pathlib

### https://regionmask.readthedocs.io/en/stable/defined_scientific.html#ar6-regions
import regionmask
regions_mask = regionmask.defined_regions.ar6.land

# regions_mask.map_keys
import data_prep.data_prep as dataprep
import set_ID


## RE type
RE_type = set_ID.RE_type
## Scenario
scens = set_ID.scens
year = set_ID.year
year_ind = set_ID.year_ind
# aggregation
agg = set_ID.agg 
ID=set_ID.ID 
sensitivity_setting = set_ID.sensitivity_setting
area_setting = set_ID.area_setting



if ID != '':
    data_path =  f'{set_ID.solar_path}{RE_type}/tech_pot_{ID}/'
elif ID == '':
    data_path = f'{set_ID.solar_path}{RE_type}/tech_pot/'
    
    
output_path = data_path

# load in data
data = dict()

for scen in scens:   
    interim = xr.open_dataset(f'{data_path}{scen}/{scen}_{RE_type}_{year}_{agg}_{ID}_{sensitivity_setting}{area_setting}.nc',
                                        engine="netcdf4")
    # area weighting
    data[scen] = dataprep.area_weighting_array(interim)
    

    

## Get the mean potential over one region     

# regions_mask (no data -> data is the region number) excluding Antarctica
#mask = regions_mask.mask(data['G6solar'])
mask = regions_mask.mask(data['G6sulfur'])
mask = mask.where(mask < 44)


def region_aggregation(ds, scen):
    reg = ds.groupby(mask).mean('stacked_lat_lon')
    # extract the abbreviations and the names of the regions from regionmask
    abbrevs = regionmask.defined_regions.ar6.land[reg.mask.values].abbrevs
    names = regionmask.defined_regions.ar6.land[reg.mask.values].names
    reg.coords['abbrevs'] = ('mask', abbrevs)
    reg.coords['names'] = ('mask', names)
    
    #save as file
    save_name = f'{scen}_{RE_type}_{year}_{agg}_{ID}_{sensitivity_setting}_regions{area_setting}.nc'
    save_dir = output_path+scen+'/region_aggregated/'
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
    try:
        os.remove(save_dir + save_name)
    except:
        pass        
    #save file
    reg.to_netcdf(save_dir + save_name)
    print(save_dir + save_name)

for scen in scens:
    region_aggregation(data[scen], scen)

print('--------------------6_region_aggregation.py ran successfully--------------------')
