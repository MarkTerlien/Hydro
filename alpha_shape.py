import os
import sys
import pandas as pd
import numpy as np
from descartes import PolygonPatch
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.getcwd()))
import alphashape

points_2d = [(0., 0.), (0., 1.), (1., 1.), (1., 0.), (0.5, 0.25), (0.5, 0.75), (0.25, 0.5), (0.75, 0.5)]

points_2d = []
fIn = open(r'data\meteo_stations.csv','r')
row = fIn.readline()
i = 0
while row :
    if i > 0 :
        x = float(row.split(';')[1])
        y = float(row.split(';')[2])
        coordinate = []
        coordinate.append(x)
        coordinate.append(y)
        points_2d.append(coordinate)
    i = i + 1
    row = fIn.readline()
fIn.close()

print("Read file")
points_2d = []
fIn = open(r'data\H12046_1m_MLLW_1of1.xyz','r')
row = fIn.readline()
i = 0
j = 0
while row :
    x = float(row.split(',')[0])
    y = float(row.split(',')[1])
    if i % 25 == 0: 
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
alpha_shape = alphashape.alphashape(points_2d, 0.1)
fOut = open('data/wkt.txt','w')
fOut.write(alpha_shape.wkt)
fOut.close()

print("Plot points and hulls")
fig, ax = plt.subplots()
ax.scatter(*zip(*points_2d))
ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
plt.show()

