# Import libraries
import cdsapi
import shutil
import os
import gdal
import gdalnumeric
import osr
import math
import struct
import pandas as pd

print(gdal.VersionInfo('VERSION_NUM'))
gdal.SetConfigOption('CPL_LOG', 'NULL')

# Copy API file .cdsapirc to %USERPROFILE%
# Metadata: https://cds.climate.copernicus.eu/cdsapp#!/dataset/satellite-sea-surface-temperature?tab=overview

# For reading NetCDF see: https://towardsdatascience.com/read-netcdf-data-with-python-901f7ff61648

# Output folder
OUTPUT_FOLDER = 'c:/temp/'

# File name 
# INPUTFILE = 'analist/atlantische_papegaaiduiker_2008_test.csv'
INPUTFILE = 'analist/atlantische_papegaaiduiker_2008.csv'
OUTPUTFILE = 'analist/atlantische_papegaaiduiker_2008_out.csv'

# Filename NetCDF file
NETCDF_FILE = '120000-ESACCI-L4_GHRSST-SSTdepth-OSTIA-GLOB_CDR2.0-v02.0-fv01.0.nc'

# Dates
years = ['2008'] 
months = ['01','02','03','04','05','06','07','08','09','10','11','12'] 
days = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31'] 

# Function to get value from raster on x,y location
def get_value_from_raster (raster_bestand_naam, x_in, y_in):

    try:
    
        # Specify the layer name to read
        layer_name = "analysed_sst"

        # Open rasterbestand
        raster_bestand_in = gdal.Open("NETCDF:{0}:{1}".format(raster_bestand_naam, layer_name))

        # Get offset and scale factor from metadata
        offset = float(raster_bestand_in.GetMetadata()['analysed_sst#add_offset'])
        scale_factor = float(raster_bestand_in.GetMetadata()['analysed_sst#scale_factor'])
        
        # Haal geotransform array and rasterband
        gt = raster_bestand_in.GetGeoTransform()
        rb = raster_bestand_in.GetRasterBand(1)
         
        # Get row and kolom
        px = math.floor((x_in - gt[0]) / gt[1]) #x pixel
        py = math.floor((y_in - gt[3]) / gt[5]) #y pixel

        # Get value from raster
        intval=(rb.ReadAsArray(px,py,1,1) * scale_factor) + offset
        
        # Sluit raster bestand
        raster_bestand_in = None
        
        # Geef waarde terug    
        return intval 

    except Exception as e: 
        raster_bestand_in = None
        print('Error function get_value_from_raster')
        print(e)

# Start script
print('Start')

# Read file into array
input_file = open(INPUTFILE,'r')
file_rows = input_file.readlines()
input_file.close()

# Read file into dataframe
df_locations = pd.read_csv(INPUTFILE, index_col=0, sep = ',')

# Get API handle
c = cdsapi.Client()

# Iterate over years
for year in years :
    
    # Iterate over months
    for month in months:

        # Iterate over days
        for day in days :
            
            # Handle non existing days
            try :

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
                print("Getting temperature from file " + str(nc_filename))
                i = 0
                temperature_list = []
                for file_row in file_rows :

                    # Skip first line
                    if i > 0 :
                    
                        # Get temperature
                        x = float(file_row.split(',')[1])
                        y = float(file_row.split(',')[2])
                        temperature = round(get_value_from_raster(nc_filename, x, y)[0][0],2)

                        # Convert from Klevin to Celsius (-273,15)
                        temperature_celsius = temperature - 273.15
                            
                        # Append temperature
                        temperature_list.append(temperature_celsius)

                    # Next row and progress indication
                    i += 1
                    if i % 500 == 0:
                        print(str(i) + ' locations processed')
                
                # Print number of locations processed
                print(str(i) + ' locations processed')

                # Add to existing dataframe
                df_locations[year + month + day] = temperature_list

                # Remove file and zipfile
                try:
                    os.remove(nc_filename)
                    os.remove(dowloadfile)
                except:
                    None

            except :
                print('Day ' + str(year + month + day) + ' does not exist')

# Remove output file
if os.path.exists(OUTPUTFILE):
    os.remove(OUTPUTFILE)

# Write output to file
df_locations.to_csv(OUTPUTFILE)

# End script
print("End script")

