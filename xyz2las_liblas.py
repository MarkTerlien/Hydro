import liblas
import numpy as np
import ogr, osr
import datetime

# Obtain liblas from: https://www.lfd.uci.edu/~gohlke/pythonlibs/

# Define coordinate transformation
inSpatialRef = osr.SpatialReference()
inSpatialRef.ImportFromEPSG(4326)
outSpatialRef = osr.SpatialReference()
outSpatialRef.ImportFromEPSG(32619)
coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

# Lists to store points from file
x_list = []
y_list =[]
z_list = []

# Oen xyz file to read
xyz_file = open('data\\Portsmouth\\H08090.xyz','r')

# Read points and store in lists
for row in xyz_file:

    # Create a geometry from coordinates
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(float(row.split()[1]),float(row.split()[0]))

    # Transform point
    point.Transform(coordTransform)

    # Add to list
    x_list.append(point.GetX())
    y_list.append(point.GetY())
    z_list.append(float(row.split()[2]))

# Close file
xyz_file.close()

# Get dimensions for header
allx = np.array(x_list) 
ally = np.array(y_list)
allz = np.array(z_list)

# Mix
xmin = np.floor(np.min(allx))
ymin = np.floor(np.min(ally))
zmin = np.floor(np.min(allz))

# Max
xmax = np.floor(np.max(allx))
ymax = np.floor(np.max(ally))
zmax = np.floor(np.max(allz))

# Create header
h = liblas.header.Header()
h.dataformat_id = 0
h.minor_version = 1
h.min = [xmin, ymin, zmin]
h.max = [xmax, ymax, zmax]
h.scale = [0.001, 0.001, 0.001]
#h.offset = [-0.0, -0.0, -0.0]
#h.srs.proj4 = str(outSpatialRef.ExportToProj4())

# Create lasfile and write output from lists to file
las_file = liblas.file.File('test6.las', mode='w', header= h)

# Write points to las file
for i in range(len(x_list)) :
    pt = liblas.point.Point()
    pt.x = x_list[i]
    pt.y = y_list[i]
    pt.z = z_list[i]
    pt.scan_angle = 0
    pt.scan_direction = 0
    pt.return_number = 0
    pt.number_of_returns = 0
    pt.flightline_edge = 0
    pt.classification = 0
    pt.time = datetime.datetime(1970, 1, 6, 12, 44, 10, 1)
    las_file.write(pt)
las_file.close()