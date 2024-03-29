#### Upscaling grid from CNRM-ESM2-1 to IMAGE
import sys
import netCDF4 as nc
import xarray as xr
import pandas as pd
import os
import numpy as np

import pathlib
import importlib
from functools import reduce
import xesmf as xe

#own packages
import data_prep.data_prep as dataprep
import set_ID

import warnings
warnings.filterwarnings("ignore")


tech_pot_path = f'{set_ID.tech_pot_path}{sys.argv[1]}/'
sensitivity_setting = set_ID.sensitivity_setting

if sensitivity_setting != '':
    tech_pot_path = f'{set_ID.solar_path}{set_ID.RE_type}/sensitivity_analysis/{sensitivity_setting}/tech_pot/{sys.argv[1]}/'

# PVpot data
pot_nofrac = xr.open_mfdataset(f'{tech_pot_path}tech_pot_{sys.argv[1]}_{set_ID.RE_type}_{set_ID.year}.nc',
                                        engine="netcdf4").astype(np.float32)
print(f'{tech_pot_path}tech_pot_{sys.argv[1]}_{set_ID.RE_type}_{set_ID.year}.nc')


# IMAGE data
IMAGE_raw = xr.open_dataset(set_ID.scratch_path+'RE_analysis/LUC_file_IMAGE/SSPs/SSP2/GLCT.nc',
                                    engine="netcdf4").astype(np.float32)
IMAGE = IMAGE_raw.rename({'latitude': 'lat', 'longitude':'lon'})


# target grid
ds_out = xr.Dataset(
    {
            "lat": (IMAGE["lat"]),
            "lon": (IMAGE["lon"]),
    })



if set_ID.agg == 'weekly':
    for x in list(range(5,9+1)):

        pot_nofrac_ = pot_nofrac.sel(time=str(set_ID.year)+x)
        ds = pot_nofrac_.resample(time='7D').sum() 

        ds_in = ds['tech_pot'].astype(np.float32).load()
        regridder = xe.Regridder(ds_in, ds_out, "bilinear", reuse_weights=True, periodic=True) #,periodic=True 
        regrid_ds = regridder(ds_in)
        regrid_ds.attrs = ds_in.attrs

        # multiply by 1000000 m2 (from tech pot calcualtion (a) -> should only be done now because of the change in grid)
        #IMAGE grid is in 5 arcminutes (0.083°lat/lon). 1°=111,567km -> 0.83=9,26km -> 9,26^2=85,7476km2

        #turn kWh/m2 to kWh/km2 to kWh/cell
        output_file = regrid_ds * 1000000 * 85.7476

            ####save preprocessed & upscaled data
        save_name = f'UPSCALED_tech_pot_{sys.argv[1]}_{set_ID.RE_type}_{set_ID.year}{x}_{set_ID.agg}.nc'
        save_dir = tech_pot_path
        pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
        try:
            os.remove(save_dir + save_name)
        except:
            pass        
            #save file
        output_file.to_netcdf(save_dir + save_name)
        print(save_dir+save_name)
    print('--------------------3_remapping.py ran successfully--------------------')



elif set_ID.agg == 'weekly_5yearchunk':

    pot_nofrac_ = pot_nofrac.sel(time=slice(str(set_ID.year)+'5',str(set_ID.year)+'9'))
    ds = pot_nofrac_.resample(time='7D').sum() #.groupby('time.season').mean() #pot_nofrac

    ds_in = ds['tech_pot'].astype(np.float32).load()
    regridder = xe.Regridder(ds_in, ds_out, "bilinear", reuse_weights=True, periodic=True) #,periodic=True 
    regrid_ds = regridder(ds_in)
    regrid_ds.attrs = ds_in.attrs

    # multiply by 1000000 m2 (from tech pot calcualtion (a) -> should only be done now because of the change in grid)
    #IMAGE grid is in 5 arcminutes (0.083°lat/lon). 1°=111,567km -> 0.83=9,26km -> 9,26^2=85,7476km2

    #turn kWh/m2 to kWh/km2 to kWh/cell
    output_file = regrid_ds * 1000000 * 85.7476
    

        ####save preprocessed & upscaled data
    save_name = f'UPSCALED_tech_pot_{sys.argv[1]}_{set_ID.RE_type}_{set_ID.year}_{set_ID.agg}.nc'
    save_dir = tech_pot_path
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
    try:
        os.remove(save_dir + save_name)
    except:
        pass        
        #save file
    output_file.to_netcdf(save_dir + save_name)
    print(save_dir+save_name)
    print('--------------------3_remapping.py ran successfully--------------------')

elif set_ID.agg == 'yearly':
    ds = pot_nofrac.resample(time='1Y').mean() #pot_nofrac

    ds_in = ds['tech_pot'].load()
    regridder = xe.Regridder(ds_in, ds_out, "bilinear", reuse_weights=True, periodic=True) #,periodic=True 
    regrid_ds = regridder(ds_in)
    regrid_ds.attrs = ds_in.attrs
    
    # multiply by 1000000 m2 (from tech pot calcualtion (a) -> should only be done now because of the change in grid)
    #IMAGE grid is in 5 arcminutes (0.083°lat/lon). 1°=111,567km -> 0.83=9,26km -> 9,26^2=85,7476km2

    output_file = regrid_ds * 85747600
    

    ####save preprocessed & upscaled data
    save_name = f'UPSCALED_tech_pot_{sys.argv[1]}_{set_ID.RE_type}_{set_ID.year}_{set_ID.agg}.nc'
    save_dir = tech_pot_path
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
    try:
        os.remove(save_dir + save_name)
    except:
        pass        
        #save file
    output_file.to_netcdf(save_dir + save_name)
    print(save_dir+save_name)
    print('--------------------3_remapping.py ran successfully--------------------')
    
elif set_ID.agg == 'all_mean':
    ds = pot_nofrac.mean('time') #pot_nofrac

    ds_in = ds['tech_pot'].load()
    print(ds_in.sel(member=2).sum().values)
    regridder = xe.Regridder(ds_in, ds_out, "bilinear", reuse_weights=True, periodic=True) #,periodic=True 
    regrid_ds = regridder(ds_in)
    regrid_ds.attrs = ds_in.attrs
    
    # multiply by 1000000 m2 (from tech pot calcualtion (a) -> should only be done now because of the change in grid)
    #IMAGE grid is in 5 arcminutes (0.083°lat/lon). 1°=111,567km -> 0.83=9,26km -> 9,26^2=85,7476km2

    output_file = regrid_ds * 85747600
    
    
    ####save preprocessed & upscaled data
    save_name = f'UPSCALED_tech_pot_{sys.argv[1]}_{set_ID.RE_type}_{set_ID.year}_{set_ID.agg}.nc'
    save_dir = tech_pot_path
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
    try:
        os.remove(save_dir + save_name)
    except:
        pass        
        #save file
    output_file.to_netcdf(save_dir + save_name)
    print(save_dir+save_name)
    print('--------------------3_remapping.py ran successfully--------------------')

elif set_ID.agg == 'seasonal_mean':
    #OPTION3 seasonal 10-year mean
    ds_season = pot_nofrac.groupby('time.season').mean('time')
    ds_export = dict()

    for sea in ds_season.season.values:
        ds_in = ds_season.sel(season=sea)['tech_pot'].load()

        regridder = xe.Regridder(ds_in, ds_out, "bilinear", reuse_weights=True,periodic=True)
        regrid_ds = regridder(ds_in)
        regrid_ds.attrs = ds_in.attrs
        regrid_ds.attrs['season'] = sea
        ds_export[sea] = regrid_ds
    
    
    #concat the seasonal datasets so that I have 1 dataset with season as a dimension
    ds_ = xr.concat(list(ds_export.values()), dim='season')
    
    # multiply by 1000000 m2 (from tech pot calcualtion (a) -> should only be done now because of the change in grid)
    #IMAGE grid is in 5 arcminutes (0.083°lat/lon). 1°=111,567km -> 0.83=9,26km -> 9,26^2=85,7476km2

    output_file = ds_ * 85747600
    
    
    ####save preprocessed & upscaled data
    save_name = f'UPSCALED_tech_pot_{sys.argv[1]}_{set_ID.RE_type}_{set_ID.year}_{set_ID.agg}.nc'
    save_dir = tech_pot_path
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True) 
    try:
        os.remove(save_dir + save_name)
    except:
        pass        
        #save file
    output_file.to_netcdf(save_dir + save_name)
    print(save_dir+save_name)
    print('--------------------3_remapping.py ran successfully--------------------')
    
