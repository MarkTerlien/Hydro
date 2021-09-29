# Import libraries
import cdsapi
import shutil
import os
import gdal
import gdalnumeric
import osr
import math
import struct

print(gdal.VersionInfo('VERSION_NUM'))

# Copy API file .cdsapirc to %USERPROFILE%
# Metadata: https://cds.climate.copernicus.eu/cdsapp#!/dataset/satellite-sea-surface-temperature?tab=overview

# Output folder
OUTPUT_FOLDER = 'c:/temp/'

# Filename NetCDF file
NETCDF_FILE = '120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_CDR2.0-v02.0-fv01.0.nc'
SCALE_FACTOR = 0.0099999998
OFFSET = 273.14999

# Dates
years = ['2011'] #,'2017']
months = ['01'] #,'February','March']
days = ['01'] #,'02','03']

# Function to get value from raster on x,y location
def get_value_from_raster (raster_bestand_naam, x_in, y_in):

    try:
    
        # Specify the layer name to read
        layer_name = "analysed_sst"
        print(raster_bestand_naam)
        netcdf_fname = "c:/temp/20110102120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_CDR2.0-v02.0-fv01.0.nc"

        # Open rasterbestand
        raster_bestand_in = gdal.Open("NETCDF:{0}:{1}".format(raster_bestand_naam, layer_name))
        
        # Haal geotransform array and rasterband
        gt = raster_bestand_in.GetGeoTransform()
        rb = raster_bestand_in.GetRasterBand(1)
        
        # Get row and kolom
        px = math.floor((x_in - gt[0]) / gt[1]) #x pixel
        py = math.floor((y_in - gt[3]) / gt[5]) #y pixel

        # Get value from raster
        intval=(rb.ReadAsArray(px,py,1,1) * SCALE_FACTOR) + OFFSET
        
        # Sluit raster bestand
        raster_bestand_in = None
        
        # Geef waarde terug    
        return intval 

    except Exception as e: 
        raster_bestand_in = None
        print('Error function get_value_from_raster')
        print(e)

# get UTM zone
def get_utm_zone(utm_zone):

    # Get zone and N/S from input
    zone = utm_zone[:-1]
    if utm_zone[-1] == 'S' :
        south = True
    else:
        south = False

    # Get code
    epsg_code = 32600
    epsg_code += int(zone)
    if south is True:
        epsg_code += 100

    print (epsg_code) # will be 32736

    spatref = osr.SpatialReference()
    spatref.ImportFromEPSG(epsg_code)
    wkt_crs = spatref.ExportToWkt()
    print (wkt_crs) 

# Get API handle
c = cdsapi.Client()

# Iterate over years
for year in years :
    
    # Iterate over months
    for month in months:

        # Iterate over days
        for day in days :
            
            # Define name of download file
            dowloadfile = OUTPUT_FOLDER + year + month + day + '.zip'

            # Execute API call for year/month/day
            c.retrieve(
                'satellite-sea-surface-temperature',
                {
                    'variable': 'all',
                    'format': 'zip',
                    'processinglevel': 'level_4',
                    'sensor_on_satellite': 'combined_product',
                    'version': '2_0',
                    'year': [year,],
                    'month': [month,],
                    'day': [day,]
                },
                dowloadfile)

            # Unzip file
            shutil.unpack_archive(dowloadfile, OUTPUT_FOLDER)

            # Define NetCDF filename
            nc_filename = OUTPUT_FOLDER + year + month + day + NETCDF_FILE

            # Open file with locations
            # For each row
            # Get location
            # Determine EPSG code with get_utm_zone('24S')
            # Transform to WGS84

            # Get temperature
            temperature = get_value_from_raster (nc_filename, -16.4544, 28.3548)[0][0]
            print(temperature)

            # Remove file and zipfile
            try:
                os.remove(nc_filename)
                os.remove(dowloadfile)
            except:
                None