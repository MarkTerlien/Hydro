import os
import glob
import requests
from osgeo import ogr
from osgeo import osr

# Set global spatial reference
spatialRef = osr.SpatialReference()
spatialRef.ImportFromEPSG(4326)  

# Function to get and store survey metadaya
def store_survey(survey_name_in, surveyLayer_in, survey_id_in) :

    try: 

        # Build URL
        url = 'https://www.ngdc.noaa.gov/next-catalogs/rest/sounding/catalog/survey?surveys=' + str(survey_name_in)

        # Execute HTTP request
        response = requests.get(url)

        # Get result
        if response.status_code == 200 :
            
            # Get response as json
            print ('Request OK')

            # Get survey definition
            surveyDefn = surveyLayer_in.GetLayerDefn()
            
            # Make survey feature
            surveyFeature = ogr.Feature(surveyDefn)
            surveyFeature.SetField('surveyId', survey_id_in)
            surveyFeature.SetField('surveyName', response.json()['items'][0]['surveyId'] )
            surveyFeature.SetField('locality', response.json()['items'][0]['locality'])
            surveyFeature.SetField('sublocality', response.json()['items'][0]['sublocality'])
            surveyFeature.SetField('platform', response.json()['items'][0]['platform'])
            surveyFeature.SetField('startTime', response.json()['items'][0]['startTime'])
            surveyFeature.SetField('endTime', response.json()['items'][0]['endTime'])
            surveyFeature.SetField('surveyYear', response.json()['items'][0]['surveyYear'])
            surveyFeature.SetField('pointCount', response.json()['items'][0]['pointCount'])
            surveyFeature.SetGeometry(ogr.CreateGeometryFromWkt(str(response.json()['items'][0]['geometry'])))
            surveyLayer_in.CreateFeature(surveyFeature)
        
        else :
            print ('Request failed with :' + str(response.status_code))

    except :
        print('Error storing survey')
        raise


# Function to store soundings
def store_soundings(sounding_file_in, soundingLayer_in, survey_id_in):

    try:

        # Get sounding definition
        soundingDefn = soundingLayer_in.GetLayerDefn()

        # Open csv file
        csv_file = open(sounding_file_in)
        lines = csv_file.readlines()

        # Itereer over lijnen
        for line in lines: 
            
            # Ophalen waardes
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(float(line.split()[0]), float(line.split()[1]))
            geom_wkt = point.ExportToWkt()
            depth = line.split()[2]

            # Create and add sounding feature to layer
            soundingFeature = ogr.Feature(soundingDefn)
            soundingFeature.SetField('SurveyId', survey_id_in)
            soundingFeature.SetField('Depth', float(depth))
            soundingFeature.SetGeometry(ogr.CreateGeometryFromWkt(str(geom_wkt)))
            soundingLayer_in.CreateFeature(soundingFeature)

    except :
        print('Error storing sounding data')
        raise

# Write geopackage
print('Begin script')
try: 

    # Create Geopackage file
    DriverName = "GPKG"     
    FileName = 'data/survey_database.gpkg'
    driver = ogr.GetDriverByName(DriverName)
    if os.path.exists(FileName):
        driver.DeleteDataSource(FileName)
    fOut = driver.CreateDataSource(FileName)

    # Make layer for surveys
    surveyLayer = fOut.CreateLayer('Survey', spatialRef, geom_type=ogr.wkbPolygon)
    surveyLayer.CreateField(ogr.FieldDefn('surveyId', ogr.OFTInteger))
    surveyLayer.CreateField(ogr.FieldDefn('surveyName', ogr.OFTString))
    surveyLayer.CreateField(ogr.FieldDefn('locality', ogr.OFTString))
    surveyLayer.CreateField(ogr.FieldDefn('sublocality', ogr.OFTString))
    surveyLayer.CreateField(ogr.FieldDefn('platform', ogr.OFTString))
    surveyLayer.CreateField(ogr.FieldDefn('startTime', ogr.OFTDateTime))
    surveyLayer.CreateField(ogr.FieldDefn('endTime', ogr.OFTDateTime))
    surveyLayer.CreateField(ogr.FieldDefn('surveyYear', ogr.OFTInteger))
    surveyLayer.CreateField(ogr.FieldDefn('pointCount', ogr.OFTInteger))
    
    # Make layer for soundings
    soundingLayer = fOut.CreateLayer('Sounding', spatialRef, geom_type=ogr.wkbPoint)
    soundingLayer.CreateField(ogr.FieldDefn('SurveyId', ogr.OFTInteger))
    soundingLayer.CreateField(ogr.FieldDefn('Depth', ogr.OFTReal))
    soundingDefn = soundingLayer.GetLayerDefn()

    # Write buffer layer
    i = 0
    for survey_file_path in glob.glob('data/Portsmouth/*.xyz'):

        # Check if file extension is .xyz
        if os.path.splitext(survey_file_path)[1] == '.xyz' :

            # Get survey name to get metadata from web API
            i = i + 1
            survey_name = os.path.splitext(os.path.basename(survey_file_path))[0]

            # Get metadata and store via eb API
            print('Store survey metadata for survey ' + str(survey_name))
            store_survey(survey_name, surveyLayer, i) 
        
            # Store soundings for survey
            print('Store soudings for survey ' + str(survey_name))
            store_soundings(survey_file_path, soundingLayer, i)

    # Close file
    fOut.Destroy()

    # End script
    print('End script')

except:
    print('Error')
    fOut.Destroy()

