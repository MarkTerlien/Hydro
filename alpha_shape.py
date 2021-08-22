import os
import sys
import pandas as pd
import numpy as np
import psycopg2
import glob

from datetime import datetime, timedelta
from descartes import PolygonPatch
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.getcwd()))

import alphashape
RADIUS = 1000
#RADIUS = 100

# Build connect string
db_connect="dbname=hydro user=postgres password=postgres"

# Set survey id
survey_count = 1

# Open database connection and get cursor
conn = psycopg2.connect(db_connect)
cur = conn.cursor()

# Alpha shapes are often used to generalize bounding polygons containing sets of points. The alpha parameter is defined as the value a, such that an edge of a disk of radius 1/a can be drawn between any two edge members of a set of points and still contain all the points.

# See: https://alphashape.readthedocs.io/en/latest/readme.html#using-a-varying-alpha-parameter

for file_name in glob.glob("data\\Portsmouth\\*.xyz"):
    
    # Give filename
    print("Read file " + file_name)

    # Get name of the survey
    survey_name = file_name[16:][:-4]
    print(survey_name)

    # Delete survey from table
    print("Delete survey")
    cur.execute("delete from public.survey where name = %s", (survey_name,))

    # Open file
    points_2d = []
    fIn = open(file_name,'r')

    # Read lines into array
    row = fIn.readline()
    i = 0
    j = 0
    while row :
        x = float(row.rstrip().split()[0])
        y = float(row.rstrip().split()[1])
        if i % 2 == 0: 
            coordinate = []
            coordinate.append(x)
            coordinate.append(y)
            points_2d.append(coordinate)
            j = j + 1
        i = i + 1
        row = fIn.readline()
    fIn.close()

    # Print numbers
    print(str(i) + " rows in file")
    print(str(j) + " rows for hull")

    # Set survey company
    if survey_count % 2 == 0 :
        survey_organisation = 'NOAA'
    else :
        survey_organisation = 'Fugro'

    # Calculate the hull
    print("Calculate hull")
    alpha_shape = alphashape.alphashape(points_2d, RADIUS)
    alpha_shape_wkt = alpha_shape.wkt

    # Get date
    survey_date = datetime.date(datetime.now()) + timedelta(survey_count * 3)
    print(survey_date)
    
    # Insert hull
    cur.execute("INSERT INTO public.survey(name, organisation, nr_of_points, hull, survey_date) VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326), %s )",(survey_name, survey_organisation, i, alpha_shape_wkt, survey_date))
    survey_count = survey_count + 1
    #print("radius = " + str(1/RADIUS))
    #fOut = open('data/wkt.txt','w')
    #fOut.write(alpha_shape.wkt)
    #fOut.close()
    

#print("Plot points and hulls")
#fig, ax = plt.subplots()
#ax.add_patch(PolygonPatch(alpha_shape, alpha=0.25, color=[1, 0, 0]))
#ax.scatter(*zip(*points_2d))
#plt.show()

# Close database
conn.commit()
conn.close()
print('Database connection closed')