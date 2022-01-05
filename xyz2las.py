import laspy
import numpy as np
import ogr, osr

hdr = laspy.header.Header()

x_list = []
y_list = []
z_list = []

# Define coordinate transformation
inSpatialRef = osr.SpatialReference()
inSpatialRef.ImportFromEPSG(4326)
outSpatialRef = osr.SpatialReference()
outSpatialRef.ImportFromEPSG(32619)
coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

xyz_file = open('bag_uit_clip.xyz','r')
for row in xyz_file:

    # Create a geometry from coordinates (input = lat,lon)
    #point = ogr.Geometry(ogr.wkbPoint)
    #point.AddPoint(float(row.split()[1]), float(row.split()[0]))

    # Transform point
    #point.Transform(coordTransform)

    # Add to list
    #x_list.append(point.GetX())
    #y_list.append(point.GetY())
    x_list.append(float(row.split()[0]))
    y_list.append(float(row.split()[1]))
    z_list.append(float(row.split()[2]))

outfile = laspy.file.File("SWIslay_swath_2m.las", mode="w", header=hdr)
allx = np.array(x_list) # Four Points
ally = np.array(y_list)
allz = np.array(z_list)

xmin = np.floor(np.min(allx))
ymin = np.floor(np.min(ally))
zmin = np.floor(np.min(allz))
xmax = np.floor(np.max(allx))
ymax = np.floor(np.max(ally))
zmax = np.floor(np.max(allz))

#outfile.header.dataformat_id = 1
#outfile.header.minor_version = 1
outfile.header.offset = [xmin,ymin,zmin]
outfile.header.scale = [1,1,0.1]
#outfile.header.min = [xmin, ymin, zmin]
#outfile.header.max = [xmax, ymax, zmax]

outfile.x = allx
outfile.y = ally
outfile.z = allz

outfile.close()