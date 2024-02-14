import os
import numpy as np
import sys

################################     SOLAR     ##############################################
################################### to set ##################################################

## RE type
RE_type = 'CSP'
## Scenario
scens = [
        'G6sulfur',
#        'G6solar',
        'ssp585',
        'ssp245',
        ]
year = '209' #203

members = [1,2,3,4,5,6]


# aggregation
agg = 'all_mean' #'seasonal_mean' 'all_mean' 'yearly'

seasons = [
    'DJF',
    'MAM',
    'JJA',
    'SON'
]

ID='suit_prot_pop' # 'prot' / 'suit_prot' / 'suit_prot_pop' / ''
sensitivity_setting = 'fixed_temp' # 'rsds_PV' / 'fixed_temp' / '' / 'fixed_rad' / 'cloudy_sky' / 'clear_sky'
#suitfactors = 'default' #noforest #nocrop #nodesert
area_setting = '_cw' # '_cw' / '_LUC' / '_LUCpop'

#for population density weighting
std = 200
thres = 500


###############################################################################################


# directories
scratch_path = ''
archive_path = ''
RE_path = f'{scratch_path}RE_analysis/'
solar_path = f'{RE_path}solar/'
LUC_path = f'{RE_path}/LUC_file_IMAGE/SSPs/regridded_and_selected/'
tech_pot_path = f'{solar_path}{RE_type}/tech_pot/'
protect_path = f'{RE_path}protected_areas/WDPA/'
pop_density_path = f'{RE_path}LUC_file_IMAGE/pop_density_weighted/'
phys_drivers_path = f'{solar_path}{RE_type}/physical_drivers/'
LED_path = f'{solar_path}{RE_type}/LED/'
if sensitivity_setting == 'fixed_temp':
    tech_pot_path = f'{solar_path}{RE_type}/sensitivity_analysis/fixed_temp/tech_pot/'



#other settings
year_ind = year[:3]+'0' 
if ID == '':
    suitfactors = ''
    
    
    
