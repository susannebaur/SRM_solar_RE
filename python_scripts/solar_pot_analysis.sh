#!/bin/bash

###### if these two variables change you need to change them manually in set_ID.py !!!!
RE_type_info="CSP"
declare -a scens=("G6sulfur" "ssp245" "ssp585")
################################################################################################################################
################################################################################################################################

###### load python environments
source /data/scratch/globc/baur/Susanne_env39/bin/activate
module load python/gloesmfpy 

###### run python scripts

###### loop over scenarios
for scen in ${scens[@]}
do
    ###### DATA ANALYSIS
#   python 0010_dataprep.py $scen
#   python 0012_radiation_calc.py $scen

    ###### TECHNICAL POTENTIAL
   if [ $RE_type_info = PV ]; then python 0020_PV_tech_pot.py $scen;
   elif [ $RE_type_info = CSP ]; then python 0021_CSP_tech_pot.py $scen;
   else echo '!!!!!!!!!!!!technical potential was not calculated because wrong/no RE type was chosen!!!!!!!!!!!!!';
   fi

    ###### REMAPPING TO IMAGE GRID
   python 0030_remapping.py $scen

  echo $scen "done"
done
#python 0040_LUC_suitability_solar.py     # doesn't depend on the CNRM scnearios and doesn't need to be rerun everytime.
python 0050_multiplication.py
######### deactivate current environment and activate baur-et-al-solar-RE because the regionmask package doesn't work in Susanne_env39 anymore 
deactivate
source /data/scratch/globc/baur/baur-et-al-solar-RE/bin/activate
#python 0060_region_aggregation.py


echo "ALL DONE"

