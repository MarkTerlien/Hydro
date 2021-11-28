# Hydrographic soundings files are categorized. File statistics (counts and sizes) are provided in terms of these categories. Queries and orders can filter on these categories, giving some degree of control over the content of an order. The most basic query provided for sounding datasets is the ability to get a list of these categories. To obtain a list of all file categories issue a GET request having the following URL pattern:

# URL: https://www.ngdc.noaa.gov/next-web/docs/guide/catalog.html

# https://www.ngdc.noaa.gov/next-catalogs/rest/sounding/catalog/survey?geometry=-71,42,-69,44
# https://www.ngdc.noaa.gov/next-catalogs/rest/sounding/catalog/survey?surveys=H09010

# Courses:
# https://www.w3schools.com/python/python_lists.asp
# https://www.w3schools.com/python/python_dictionaries.asp

# Change geometry type column to MultiPolygon
# ALTER TABLE survey ALTER COLUMN survey_geom type geometry(Geometry, 4326) ;

# Import libraries
import requests
import json
import psycopg2
import glob
import file_helper

# Function to get survey polygon
def store_survey_data(survey_name) :

    # Build URL
    url = 'https://www.ngdc.noaa.gov/next-catalogs/rest/sounding/catalog/survey?surveys=' + str(survey_name)

    # Execute HTTP request
    response = requests.get(url)

    # Get result
    if response.status_code == 200 :
        
        # Get response as json
        print ('Request OK')
        print(json.dumps(response.json(), indent=8, sort_keys=True))
        
        # Get attribute values from json
        hblockDir   = response.json()['items'][0]['hblockDir'] 
        locality    = response.json()['items'][0]['locality']
        modifyTime  = response.json()['items'][0]['modifyTime']
        platform    = response.json()['items'][0]['platform']
        pointCount  = response.json()['items'][0]['pointCount']
        startTime   = response.json()['items'][0]['startTime']
        endTime     = response.json()['items'][0]['endTime']
        sublocality = response.json()['items'][0]['sublocality']
        surveyId    = response.json()['items'][0]['surveyId']
        surveyYear  = response.json()['items'][0]['surveyYear']
        geom_wkt    = response.json()['items'][0]['geometry']

        # Open connection
        db_connection = psycopg2.connect(host="localhost", port ="5433", database="engineer2122", user="postgres", password="postgres")
        cur = db_connection.cursor()

        # Execute update
        sql = 'update survey set survey_geom = ST_GeomFromText(%s,4326) where survey_name = %s'
        cur.execute(sql,(boundary_wkt,survey_name))

        # Sla op
        db_connection.commit()

        # Close database
        db_connection.close()
    
    else :
        print ('Request failed with :' + str(response.status_code))

# Run function
for filepath in glob.iglob('data\*.xyz'):
    survey_name = file_helper.get_file_name_without_path_and_extension(filepath)
    print('Ophalen survey boundary at API for survey ' + str(survey_name))
    store_survey_data(survey_name)

# Einde script
print('End script')
