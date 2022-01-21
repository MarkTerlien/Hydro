#! /usr/bin/python

""" Template function """

# Soure of example: http://sebsauvage.net/python/gui

# standard library imports
import os
import sys
import h5py
import xml.dom.minidom
from io import BytesIO
from lxml import etree
import laspy
import numpy as np

# https://salishsea-meopar-tools.readthedocs.io/en/latest/bathymetry/ExploringBagFiles.html

__author__="Terlien"
__date__ ="$9-okt-2009 11:50:05$"
__copyright__ = "Copyright 2009, ATLIS"

INPUT_FILE  = 'data/bag/SWIslay_swath_2m.bag'
VERSION = '1.0'
NR_OF_POINTS = 25000000

if __name__ == "__main__":

    # Open BAG file
    bag = h5py.File(INPUT_FILE)
    print(type(bag))
    print(bag.name)
    print(bag.filename)

    # Get root
    root = bag['BAG_root']

    # Get elevation
    elev_node = root['elevation']
    elev = elev_node[()]
    print(elev.min(), elev.max())   

    # Get Metadata
    metadata_node = root['metadata']
    buffer = BytesIO(metadata_node[()])
    tree = etree.parse(buffer)
    metadata_root = tree.getroot()
    
    # Print XML
    print(etree.tostring(metadata_root, pretty_print=True).decode('ascii'))

    # Parse metadata XML to DOM tree
    metadata_xml = xml.dom.minidom.parseString(etree.tostring(metadata_root, pretty_print=True).decode('ascii'))

    # Parse XML based on version
    if VERSION == '2.0' :

        # Resolution
        resolution = float( metadata_xml.getElementsByTagName('gmd:MD_Dimension')[0].getElementsByTagName('gmd:resolution')[0].getElementsByTagName('gco:Measure')[0].firstChild.nodeValue)

    if VERSION == '1.0' :

        # Resolution
        resolution = float( metadata_xml.getElementsByTagName('smXML:MD_Dimension')[1].getElementsByTagName('resolution')[0].getElementsByTagName('smXML:Measure')[0].getElementsByTagName('smXML:value')[0].childNodes[0].nodeValue )

        # Coordinate system
        projection = str( metadata_xml.getElementsByTagName('projection')[0].getElementsByTagName('smXML:RS_Identifier')[0].getElementsByTagName('code')[0].childNodes[0].nodeValue ) 
        zone = str( metadata_xml.getElementsByTagName('smXML:MD_ProjectionParameters')[0].getElementsByTagName('zone')[0].childNodes[0].nodeValue ) 
        ellipsoid = str( metadata_xml.getElementsByTagName('ellipsoid')[0].getElementsByTagName('smXML:RS_Identifier')[0].getElementsByTagName('code')[0].childNodes[0].nodeValue ) 
        horizontal_datum = str( metadata_xml.getElementsByTagName('datum')[0].getElementsByTagName('smXML:RS_Identifier')[0].getElementsByTagName('code')[0].childNodes[0].nodeValue )         
        vertical_datum = str( metadata_xml.getElementsByTagName('datum')[1].getElementsByTagName('smXML:RS_Identifier')[0].getElementsByTagName('code')[0].childNodes[0].nodeValue )

    # Coordinates
    coordinates = str( metadata_xml.getElementsByTagName('gml:coordinates')[0].childNodes[0].nodeValue )
    ll_x = float(coordinates.rstrip().split()[0].rstrip().split(',')[0])
    ll_y = float(coordinates.rstrip().split()[0].rstrip().split(',')[1])

    # Define arrays to store values in las
    x_list = []
    y_list = []
    z_list = []

    # Get points and store in array
    i = 0
    j = 0
    for col in range(elev.shape[0]):

        if i > NR_OF_POINTS:
            break
        
        for row in range(elev.shape[1]):

            # Get xýz
            x = ll_x + float(col) * resolution
            y = ll_y + float(row) * resolution
            z = float( elev [ col, row ] )

            # Exclude when z = 1000000
            if int(z) != int(1000000) :
                x_list.append(x)
                y_list.append(y)
                z_list.append(z)
                i = i + 1
                if i % int(NR_OF_POINTS/100) == 0 :
                    print(str(i) + ' points processed')
                    if i > NR_OF_POINTS:
                        break
            else :
                j = j + 1
                if j % int(NR_OF_POINTS/100) == 0 :
                    print(str(j) + ' points skipped')

    
    # Store points from array in las file
    print('nr of points to store in las file: ' + str(i))
    hdr = laspy.header.Header()
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
    outfile.header.offset = [xmin,ymin,zmin]
    outfile.header.scale = [1,1,0.1]
    outfile.x = allx
    outfile.y = ally
    outfile.z = allz
    outfile.close()
   
    print( 'projection: '       + projection )
    print( 'zone: '             + zone )
    print( 'ellipsoid: '        + ellipsoid )
    print( 'horizontal datum: ' + horizontal_datum )
    print( 'vertical datum: '   + vertical_datum )
    print( 'lafile = SWIslay_swath_2m.las')

    
    



    
