# LaSTMoV
Land Surface Temperature MODIS Visualization (LaSTMoV). Used to create heat vulnerability maps for Maricopa County using MYD11A1 V005 data.

*** 

## About

```
# NASA DEVELOP National Program Arizona Health & Air Quality II Team
# Authors: Daniel Finnell, Teresa Fenn, Richard Muench, Ashley Brodie
# Date: March 21, 2016
# Purpose: To create heat vulnerability maps for Maricopa County using MYD11A1 V005 data.
# Input: Files and folders set by the user in the first section below the imported libraries. 
#        Please define each variable, and include the ENTIRE file path for all files and folders.
#
#   moddir      The folder containing downloaded Aqua MODIS MYD11A1 V005 tile h08v05 for the 
#               desired study period. These MODIS files must be downloaded in HDF format by the 
#               user before the script can run.
#
#   shapefile   This is a shapefile of Maricopa County census tracts, and can be downloaded from the 
#               US Census Bureau.
#
#   years       This is a list of years in the study period. The list can be one year or many, but MUST be
#               in python list format. Example: ['2012', '2013', '2014']
#
#   start       The beginning day of the study period. The format is MMDDHHMM (month, day, hour, minute)
#               Example: '10312359' is October 31st at 23:59. All times are military.
#
#   end         This is the final day of the study period. The format is the same as start. For the 
#               sake of simplicity, it is recommended that the start time be 0000, and the end time be 2359.
#
#  indir        This is the folder that will hold all intermediary and output files. The script will create 
#               sub-files to organize the data.
#
#  middir       This folder will save the intermediary files created by arcpy. It is recommended that 
#               you set this variable to be Documents\ArcGIS\Default.gdb, although it is not required.
```
