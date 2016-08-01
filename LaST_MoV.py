########################################################################################################################
# NASA DEVELOP National Program Arizona Health & Air Quality II Team
# Authors: Daniel Finnell, Teresa Fenn, Richard Muench, Ashley Brodie
# Date: March 21, 2016
# Purpose: To create heat vulnerability maps for Maricopa County using MYD11A1 V005 data.
# Input: Files and folders set by the user in the first section below the imported libraries. Please define each
#        variable, and include the ENTIRE file path for all files and folders.
#
#   moddir      The folder containing downloaded Aqua MODIS MYD11A1 V005 tile h08v05 for the desired study period.
#               These MODIS files must be downloaded in HDF format by the user before the script can run.
#
#   shapefile   This is a shapefile of Maricopa County census tracts, and can be downloaded from the US Census Bureau.
#
#   years       This is a list of years in the study period. The list can be one year or many, but MUST be
#               in python list format. Example: ['2012', '2013', '2014']
#
#   start       The beginning day of the study period. The format is MMDDHHMM (month, day, hour, minute)
#               Example: '10312359' is October 31st at 23:59. All times are military.
#
#   end         This is the final day of the study period. The format is the same as start. For the sake of simplicity,
#               it is recommended that the start time be 0000, and the end time be 2359.
#
#  indir        This is the folder that will hold all intermediary and output files. The script will create sub-files
#               to organize the data.
#
#  middir       This folder will save the intermediary files created by arcpy. It is recommended that you set this
#               variable to be Documents\ArcGIS\Default.gdb, although it is not required.
########################################################################################################################

from dnppy import modis
from dnppy import core
from dnppy import raster
import os
from os import rename, listdir
import re
import string
import shutil
import subprocess
import time
import json
from datetime import datetime, timedelta
import urllib2
import csv
import sys
import numpy
import arcpy
from arcpy.sa import *

# Your input goes here. See the above comments for instructions.=======================================================
moddir = r'C:\Users\tefenn\Documents\AZ\Test\MODIS'
shapefile = r'C:\Users\tefenn\Documents\AZ\Shapefiles\FW__\Census.shp'
years = ['2013', '2014', '2015']
start = '04010000'
end = '10312359'
indir = r'C:\Users\tefenn\Documents\AZ\Test\test2'
middir = r'C:\Users\tefenn\Documents\ArcGIS\Default.gdb'
# DO NOT EDIT ANYTHING BELOW THIS LINE!!!==============================================================================

# Create necessary intermediary folders--------------------------------------------------------------------------------
mwdir = os.path.join(indir, 'MesoWest', )
if not os.path.exists(mwdir):
    os.makedirs(mwdir)
tifdir = os.path.join(indir, 'TIFF', )
if not os.path.exists(tifdir):
    os.makedirs(tifdir)
baddays = os.path.join(indir, 'baddays', )
if not os.path.exists(baddays):
    os.makedirs(baddays)

# Extract tiffs from hdf----------------------------------------------------------------------------------------------
layers = [0, 4]
lnames = ["daytime", "nighttime"]
modis.extract_from_hdf(moddir, layers, lnames, tifdir)

# Find days over 104 F using weather station data from Phoenix Airport------------------------------------------------
# Download data from API
base = 'http://api.mesowest.net/v2/stations/timeseries?token=24307d99c0054f988aca6a71f3e41658&start='
var = '&vars=air_temp&output=csv&units=temp|F&obtime=local&STID='
for date in years:
    print date
    # append the station name onto the "STID=" portion of the web address
    path_STID = base + date + start + '&end=' + date + end + var + 'KPHX'
    # Read the API response in CSV format into program memory.
    response = urllib2.urlopen(path_STID)
    output = csv.reader(response, 'excel')
    data = [row for row in output]

    # The first 8 rows are metadata from the API return
    metadata = data[0:8]
    # Put remaining rows into a list of lists
    data_rows = data[8:]

    # Create variables to store the columns in
    stn_id = [''] * len(data_rows)
    dattim = [''] * len(data_rows)
    air_temp = [0] * len(data_rows)

    # Put the variables into separate column lists
    for i in range(len(data_rows)):
        try:
            stn_id[i] = data_rows[i][0]
        except IndexError:
            pass
        try:
            dattim[i] = data_rows[i][1]
        except IndexError:
            pass
        try:
            air_temp[i] = data_rows[i][2]
        except IndexError:
            pass
    # joins columns and saves output
    f = numpy.column_stack((stn_id, dattim, air_temp))
    g = []
    name = date + '_KPHX' + '.csv'
    api_outname = os.path.join(mwdir, name)
    head = 'stn_id, dattim, air_temp'
    with open(api_outname, 'wb+') as api_work:
        for line in f:
            g.append(line)
        numpy.savetxt(api_work, g, fmt='%s', delimiter=',', header=head)
print 'Data downloaded from mesowest API!'

# Locate days where high air temperature is above 104 Fahrenheit from csv files of weather station data.
stations = core.list_files(False, mwdir, 'KPHX.csv', 'days.csv')
for year in stations:
    with open(year) as annum:
        path, filename = os.path.split(year)
        year_name = filename[0:4]
        print year_name
        temp = csv.reader(annum)
        data = [row for row in temp]
        begin = 0
        highT = []
        high2 = []
        high_spot = []
        output = []
        # create highT
        for h in range(len(data)):
            try:
                ht = data[h][2]
                highT.append(ht)
            except IndexError:
                continue
        for i in highT:
            if i != '':
                try:
                    i2 = int(float(i))
                    high2.append(i2)
                except ValueError:
                    continue
        # Find days over 104 F and append to a list for each year/station
        for item in high2:
            if item != '':
                if 104 <= item <= 118:
                    location = high2.index(item, begin+1)
                    high_spot.append(location)
                    begin = location
        # Get data for those days
        for x in high_spot:
            answer = data[x]
            output.append(answer)
        # Save output
    g = []
    days = os.path.join(mwdir, year_name + 'study_days.csv')
    head = 'stn_id, dattim, air_temp'
    with open(days, 'wb+') as day_work:
        for line in output:
            g.append(line)
        numpy.savetxt(day_work, g, fmt='%s', delimiter=',', header=head)
    print 'Days over 104 F located for', year_name, '!'

# Compile a list of unique days in julian format and yyyy-mm-dd format. Saves to a csv.
    ymd = []
    outdays = []
    gooddays = []
    with open(days) as many:
        sol = csv.reader(many)
        f = [row[1] for row in sol]
        for d in f[1:]:
            date = d[0:4] + d[5:7] + d[8:10]
            ymd.append(date)
        for i in ymd:
            if i not in outdays:
                outdays.append(i)
        for j in outdays:
            dateobj = datetime.strptime(j, "%Y%m%d")
            entry = dateobj.strftime("%Y%j")
            gooddays.append(entry)
    # Compare julian to ymd
        yd_list = []
        yd_final = []
        for e in f[1:]:
            yd = e[0:10]
            yd_list.append(yd)
        for h in yd_list:
            if h not in yd_final:
                yd_final.append(h)
        # Create table for csv
        julian = [''] * len(gooddays)
        common = [''] * len(yd_final)
        for z in range(len(gooddays)):
            julian[z] = gooddays[z]
            common[z] = yd_final[z]
    # Save days to csv
    f = numpy.column_stack((julian, common))
    g = []
    unique = os.path.join(mwdir, year_name + 'unique_days.csv')
    with open(unique, 'wb+') as uwork:
        for line in f:
                g.append(line)
        numpy.savetxt(uwork, g, fmt='%s', delimiter=',')
    print 'List of unique days compiled for', year_name, '!'

# Delete MODIS files that do not belong to days over 104 F within the study period
    modis_list = core.list_files(False, tifdir)

    # pull out just the filenames of modis_list
    modis_fnames = [os.path.basename(x) for x in modis_list]
    modis_datestrings = [x.split(".")[1].replace("A", "") for x in modis_fnames]

    # perform the deletion if the modis tile doesn't match with the good dates
    print 'MODIS files sorting into good days and bad days. This may take awhile...'
    check = julian[0]
    for i, modis_datestring in enumerate(modis_datestrings):
        if modis_datestring[0:4] == check[0:4]:
            if modis_datestring not in julian:
                shutil.move(modis_list[i], baddays)
        else:
            continue
    print 'MODIS files sorted!'

# Process MODIS-------------------------------------------------------------------------------------------------------
# Clip MODIS to Maricopa County
    print "Clipping MODIS files..."
    clpdir = os.path.join(indir, 'Clipped', year_name, )
    tiles = core.list_files(False, tifdir, '.tif', ['.tfw', '.ovr', '.aux', '.xml'])
    if not os.path.exists(clpdir):
        os.makedirs(clpdir)
    for tif in tiles:
        path, filename = os.path.split(tif)
        if filename[9:13] == check[0:4]:
            clpname = os.path.join(clpdir, filename)
            arcpy.gp.ExtractByMask_sa(tif, shapefile, clpname)
        else:
            continue
    print 'MODIS files clipped!'

# Renames MODIS to abbreviated YEAR-DATE
    os.chdir(clpdir)
    directory = os.listdir(clpdir)

    for filename in directory:
        if filename.find('daytime') != -1:
            if filename.find('aux') != -1:
                dayname = '{0}_{1}.{2}.{3}.{4}'.format(filename[9:16], filename[42:49], filename.split('.')[-3],
                                                       filename.split('.')[-2], filename.split('.')[-1])
                os.rename(filename, dayname)
            elif filename.find('tif.xml') != -1:
                dayname = '{0}_{1}.{2}.{3}'.format(filename[9:16], filename[42:49], filename.split('.')[-2],
                                                   filename.split('.')[-1])
                os.rename(filename, dayname)
            else:
                dayname = filename[9:16] + '_' + filename[42:49] + '.' + filename.split('.')[-1]
                os.rename(filename, dayname)
        else:
            if filename.find('aux') != -1:
                nightname = '{0}_{1}.{2}.{3}.{4}'.format(filename[9:16], filename[42:51], filename.split('.')[-3],
                                                         filename.split('.')[-2], filename.split('.')[-1])
                os.rename(filename, nightname)
            elif filename.find('tif.xml') != -1:
                nightname = '{0}_{1}.{2}.{3}'.format(filename[9:16], filename[42:51], filename.split('.')[-2],
                                                     filename.split('.')[-1])
                os.rename(filename, nightname)
            else:
                nightname = filename[9:16] + '_' + filename[42:51] + '.' + filename.split('.')[-1]
                os.rename(filename, nightname)
    print 'MODIS files renamed!'

# Convert MODIS from digital number to Fahrenheit
    arcpy.CheckOutExtension('Spatial')
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = middir

    fdir = os.path.join(indir, 'Fahrenheit', year_name, )
    ctof = core.list_files(False, clpdir, ".tif", ['.ovr', '.xml', '.tfw', '.aux'])
    if not os.path.exists(fdir):
        os.makedirs(fdir)

    for tif in ctof:
        path, filename = os.path.split(tif)
        try:
            Modis_F_Output = os.path.join(fdir, filename)
            decimal = arcpy.gp.Float_sa(tif)
            kelvin = arcpy.gp.Times_sa(decimal, .02)
            celcius = arcpy.gp.Minus_sa(kelvin, 273.15)
            celfahr = arcpy.gp.Times_sa(celcius, 1.8)
            fahrenheit = arcpy.gp.Plus_sa(celfahr, 32, Modis_F_Output)
        except:
            print tif, 'does not have valid statistics (.aux.xml file) cannot convert to Fahrenheit'
        print tif, 'to fahrenheit'
    fname = core.list_files(True, fdir)
    for name in fname:
        core.rename(name, '.tif_F', '_F')
    print "MODIS files converted to Fahrenheit for", year_name, "!"

