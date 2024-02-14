import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np
import itertools

import pathlib

# own packages
import set_ID
import data_prep.data_prep as dataprep



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
std=set_ID.std
thres=set_ID.thres
area_setting=set_ID.area_setting

if ID != '':
    output_path =  f'{set_ID.solar_path}{RE_type}/tech_pot_{ID}/'
elif ID == '':
    output_path = f'{set_ID.solar_path}{RE_type}/tech_pot/'

############################## Include suitability factors in the tech pot calculation

pot_highres = dict()
IMAGE=dict()
pop_density=dict()

if sensitivity_setting != '':
    tech_pot_path = f'{set_ID.solar_path}{set_ID.RE_type}/sensitivity_analysis/{sensitivity_setting}/tech_pot/'
else:
    tech_pot_path = f'{set_ID.tech_pot_path}'


for scen in set_ID.scens:
    ### PV_pot or CSP_pot that is regridded to image grid
    try:
        pot_highres[scen] = xr.open_dataset(f'{tech_pot_path}{scen}/UPSCALED_tech_pot_{scen}_{RE_type}_{year}_{agg}.nc',
                                        engine="netcdf4").rename({'__xarray_dataarray_variable__':'tech_pot'})
    except ValueError:
        pot_highres[scen] = xr.open_dataset(f'{tech_pot_path}{scen}/UPSCALED_tech_pot_{scen}_{RE_type}_{year}_{agg}.nc',
                                        engine="netcdf4")
        
    land_mask = xr.open_mfdataset(f'{set_ID.scratch_path}RE_analysis/LUC_file_IMAGE/SSPs/SSP2/GLCT.nc',
                                        engine="netcdf4").sel(time='2100-01-01').rename({'latitude':'lat', 'longitude':'lon'})

### PV suitability factors
    if 'suit' in ID:
        if 'LUC' in area_setting:
            
             ### use ssp585 LUC as underlying for G6
            if scen == 'G6sulfur' or scen == 'G6solar':
                ssp='ssp5'
            else:
                #ssp='ssp5'
                ssp=scen[:4]
        else:
            ssp='ssp2'
            
        IMAGE[scen] = xr.open_dataset(f'{set_ID.LUC_path}{RE_type}_{ssp}_default.nc', 
                             engine="netcdf4").rename({'latitude':'lat', 'longitude': 'lon'})
            

### population density distance weighting
    if 'pop' in ID:
        if 'pop' in area_setting:
            ### use ssp585 LUC as underlying for G6
            if scen == 'G6sulfur' or scen == 'G6solar':
                ssp='ssp5'.upper()
            else:
                #ssp='ssp5'
                ssp=scen[:4].upper()
        else:
            ssp='SSP2'
        pop_density[scen] = xr.open_mfdataset(f'{set_ID.pop_density_path}weighted_distance_std{str(std)}_thres{str(thres)}_209_{ssp}.nc',
                                        engine="netcdf4")
            

### Protected areas
if 'prot' in ID:
    protected_areas = xr.open_mfdataset(f'{set_ID.protect_path}merged_protected_areas.nc',
                                        engine="netcdf4")
    protected_areas = protected_areas.fillna(-999)
    


# multiply to get the tech potential with the suitability factors
# remove protected areas
_tech_pot_suit = dict()
for scen in scens:
    
    _tech_pot_suit[scen] = pot_highres[scen]['tech_pot']
    
    #multiplication with suitability factors 
    if 'suit' in ID:
        
        # choose middle of decade for IMAGE (2095, 2035,..)
        if 'LUC' in area_setting:
            _tech_pot_suit[scen] = _tech_pot_suit[scen] * IMAGE[scen].sel(time = year+'5')['frac'].where(IMAGE[scen]['frac']>0).mean('time')       
        else:
            _tech_pot_suit[scen] = _tech_pot_suit[scen] * IMAGE[scen].sel(time = '2095')['frac'].where(IMAGE[scen]['frac']>0).mean('time')  
    
    #pop density
    if 'pop' in ID:
        _tech_pot_suit[scen] = _tech_pot_suit[scen] * pop_density[scen]['weighted_density']
    
    #remove protected areas
    if 'prot' in ID:
        _tech_pot_suit[scen] = _tech_pot_suit[scen].where(protected_areas.mean('member')==-999)
        
        
    # remove values over the ocean
    _tech_pot_suit[scen] = _tech_pot_suit[scen].where(land_mask['GLCT']>0)   

    
    # set attributes
    _tech_pot_suit[scen].attrs['experiment_id'] = scen
    

    #save as file
    save_name = f'{scen}_{RE_type}_{year}_{agg}_{ID}_{sensitivity_setting}{area_setting}.nc'
    save_dir = output_path+scen+'/'
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
    try:
        os.remove(save_dir + save_name)
    except:
        pass        
    #save file
    _tech_pot_suit[scen].to_netcdf(save_dir + save_name)
    print(save_dir + save_name)

    
################## write global potential number out to .txt-file
if agg == 'all_mean':
    _tech_pot_suit_TWh = dict()

    ### output in PWh/yr
    outfile = open(f'{set_ID.solar_path}{RE_type}/global_tech_pop.txt', "a")
    print(ID)
    for scen in scens:
        print(scen) 
        #convert to TWh/yr
        _tech_pot_suit_TWh[scen] =  _tech_pot_suit[scen].mean('member') * 1e-9 * 8760
        # do area weighting
        if ID == '':
            weighted_file = dataprep.area_weighting_array(_tech_pot_suit_TWh[scen])
        else:
            weighted_file = dataprep.area_weighting_array(_tech_pot_suit_TWh[scen]['tech_pot'])
        #get global sum and convert to PWh/yr
        print(str(round((weighted_file/1000).sum().values.item(), 3)))
        outfile.write(ID+', '+scen+', '+str(year_ind)+', '+str(round((weighted_file/1000).sum().values.item(), 3))+', '+sensitivity_setting+', '+area_setting[1:]+"\n")
    outfile.close()
    
print('--------------------5_multiplication.py ran successfully--------------------')

