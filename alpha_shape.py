import os
import sys
import pandas as pd
import numpy as np
from descartes import PolygonPatch
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.getcwd()))
import alphashape
RADIUS = 3700

# Alpha shapes are often used to generalize bounding polygons containing sets of points. The alpha parameter is defined as the value a, such that an edge of a disk of radius 1/a can be drawn between any two edge members of a set of points and still contain all the points.

# See: https://alphashape.readthedocs.io/en/latest/readme.html#using-a-varying-alpha-parameter

print("Read file")
points_2d = []
fIn = open(r'data\Portsmouth\H07140.xyz','r')
fIn = open(r'data\Portsmouth\H08090.xyz','r')
row = fIn.readline()
i = 0
j = 0
while row :
    x = float(row.rstrip().split()[0])
    y = float(row.rstrip().split()[1])
    if i % 1 == 0: 
        coordinate = []
        coordinate.append(x)
        coordinate.append(y)
        points_2d.append(coordinate)
        j = j + 1
    i = i + 1
    row = fIn.readline()
fIn.close()
print(str(i) + " rows in file")
print(str(j) + " rows for hull")

print("Calculate hull")
alpha_shape = alphashape.alphashape(points_2d, RADIUS)
print("radius = " + str(1/RADIUS))
fOut = open('data/wkt.txt','w')
fOut.write(alpha_shape.wkt)
fOut.close()

print("Plot points and hulls")
fig, ax = plt.subplots()
ax.add_patch(PolygonPatch(alpha_shape, alpha=0.25, color=[1, 0, 0]))
ax.scatter(*zip(*points_2d))
plt.show()

