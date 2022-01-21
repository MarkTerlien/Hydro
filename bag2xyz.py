#! /usr/bin/python

""" Template function """

# Soure of example: http://sebsauvage.net/python/gui

# standard library imports
import os, sys
try:
    import h5py
except ImportError:
    raise ImportError
try:
    import xml.dom.minidom
except ImportError:
    raise ImportError

from io import BytesIO

import h5py
from lxml import etree
import matplotlib.pyplot as plt
import numpy as np

# https://salishsea-meopar-tools.readthedocs.io/en/latest/bathymetry/ExploringBagFiles.html

__author__="Terlien"
__date__ ="$9-okt-2009 11:50:05$"
__copyright__ = "Copyright 2009, ATLIS"

INPUT_FILE  = 'data/bag/SWIslay_swath_2m.bag'
VERSION = '1.0'

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

    if VERSION == '2.0' :
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

    fOut   = open('bag_uit.xyz', 'w')
    i = 0
    for col in range(elev.shape[0]):
        for row in range(elev.shape[1]):
            z = float( elev [ col, row ] )
            x = ll_x + float(col) * resolution
            y = ll_y + float(row) * resolution
            i = i + 1
            output_line = str(x) + ' ' + str(y) + ' ' + str(z) + "\n"
            fOut.write( output_line )
            if i % 100000 == 0 :
                print(str(i) + ' points processed')
                if i == 1000000:
                    break
    fOut.close()
    print('nr of points: ' + str(i))

    sys.exit(1)
   
    
    bag.values()
    bag.items()
    root=bag['BAG_root']
    metadata_node=root['BAG_root/metadata']
    metadata = ''.join(metadata_node.value)
    elev_node=root['elevation']
    elev=elev_node.value

    sys.exit(1)

    from osgeo import gdal
    bag = gdal.OpenShared(INPUT_FILE)
    bagmetadata = bag.GetMetadata("xml:BAG")[0]   
    metadata_xml = xml.dom.minidom.parseString(bagmetadata)

    print(bag['/BAG_root/elevation'].value)
    sys.exit(1)




    print('westBoundLongitude: ' + str( metadata_xml.getElementsByTagName('westBoundLongitude')[0].childNodes[0].nodeValue ))
    print('eastBoundLongitude: ' + str( metadata_xml.getElementsByTagName('eastBoundLongitude')[0].childNodes[0].nodeValue ))
    print('southBoundLatitude: ' + str( metadata_xml.getElementsByTagName('southBoundLatitude')[0].childNodes[0].nodeValue ))
    print('northBoundLatitude: ' + str( metadata_xml.getElementsByTagName('northBoundLatitude')[0].childNodes[0].nodeValue ))





 

    # Return root as dictionary object
    root = bag['/BAG_root']

    print("root.keys (HDF5 datasets)")
    print(root.keys())
    print("root.values")
    print(root.values())
    print("root.items")
    print(root.items())

    print(''.join(bag['/BAG_root/metadata']))

    sys.exit(0)
 
    metadata_xml = xml.dom.minidom.parseString(str(''.join(bag['/BAG_root/metadata'])))
    #print metadata_xml.toprettyxml()
    print('westBoundLongitude: ' + str( metadata_xml.getElementsByTagName('westBoundLongitude')[0].childNodes[0].nodeValue ))
    print('eastBoundLongitude: ' + str( metadata_xml.getElementsByTagName('eastBoundLongitude')[0].childNodes[0].nodeValue ))
    print('southBoundLatitude: ' + str( metadata_xml.getElementsByTagName('southBoundLatitude')[0].childNodes[0].nodeValue ))
    print('northBoundLatitude: ' + str( metadata_xml.getElementsByTagName('northBoundLatitude')[0].childNodes[0].nodeValue ))

    print(metadata_xml.getElementsByTagName('smXML:MD_Dimension')[0].getElementsByTagName('dimensionName')[0].childNodes[0].nodeValue)
    print('rows: '   + str( metadata_xml.getElementsByTagName('smXML:MD_Dimension')[0].getElementsByTagName('dimensionSize')[0].childNodes[0].nodeValue ))
    unit_y = float( metadata_xml.getElementsByTagName('smXML:MD_Dimension')[0].getElementsByTagName('resolution')[0].getElementsByTagName('smXML:Measure')[0].getElementsByTagName('smXML:value')[0].childNodes[0].nodeValue )
    print('--unit: ' + str( unit_y ))
    print(metadata_xml.getElementsByTagName('smXML:MD_Dimension')[1].getElementsByTagName('dimensionName')[0].childNodes[0].nodeValue)
    print('cols: '   + str( metadata_xml.getElementsByTagName('smXML:MD_Dimension')[1].getElementsByTagName('dimensionSize')[0].childNodes[0].nodeValue ))
    unit_x = float( metadata_xml.getElementsByTagName('smXML:MD_Dimension')[1].getElementsByTagName('resolution')[0].getElementsByTagName('smXML:Measure')[0].getElementsByTagName('smXML:value')[0].childNodes[0].nodeValue )
    print('--unit: ' + str( unit_x ))

    coordinates = str( metadata_xml.getElementsByTagName('gml:coordinates')[0].childNodes[0].nodeValue )
    print('gml:coordinates: ' + str( coordinates ))
    ll_x = float(coordinates.rstrip().split()[0].rstrip().split(',')[0])
    ll_y = float(coordinates.rstrip().split()[0].rstrip().split(',')[1])
    print( ll_x)
    print( ll_y)

    # Write metadata
    output_file = os.path.dirname( INPUT_FILE ) + "/" + os.path.basename( INPUT_FILE ).split(".")[0] + str(".txt")
    projection       = str( metadata_xml.getElementsByTagName('projection')[0].getElementsByTagName('smXML:RS_Identifier')[0].getElementsByTagName('code')[0].childNodes[0].nodeValue ) 
    zone             = str( metadata_xml.getElementsByTagName('smXML:MD_ProjectionParameters')[0].getElementsByTagName('zone')[0].childNodes[0].nodeValue ) 
    ellipsoid        = str( metadata_xml.getElementsByTagName('ellipsoid')[0].getElementsByTagName('smXML:RS_Identifier')[0].getElementsByTagName('code')[0].childNodes[0].nodeValue ) 
    horizontal_datum = str( metadata_xml.getElementsByTagName('datum')[0].getElementsByTagName('smXML:RS_Identifier')[0].getElementsByTagName('code')[0].childNodes[0].nodeValue )         
    vertical_datum   = str( metadata_xml.getElementsByTagName('datum')[1].getElementsByTagName('smXML:RS_Identifier')[0].getElementsByTagName('code')[0].childNodes[0].nodeValue )         
    
    print(output_file)
    fOut   = open( output_file, 'w')
    fOut.write( 'projection       : ' + projection + "\n" )
    fOut.write( 'zone             : ' + zone + "\n" )
    fOut.write( 'ellipsoid        : ' + ellipsoid + "\n" )
    fOut.write( 'horizontal datum : ' + horizontal_datum + "\n" )
    fOut.write( 'vertical  datum  : ' + vertical_datum + "\n" )
    fOut.close()
    
    print( 'projection: '       + projection )
    print( 'zone: '             + zone )
    print( 'ellipsoid: '        + ellipsoid )
    print( 'horizontal datum: ' + horizontal_datum )
    print( 'vertical datum: '   + vertical_datum )

    elevation   = bag['/BAG_root/elevation'].value
    print('Grid dimensions elevation   : ' + str(elevation.shape))

    # Grid starts at 0,0
    # Ignore z values larger than 0
    output_file = os.path.dirname( INPUT_FILE ) + "/" + os.path.basename( INPUT_FILE ).split(".")[0] + str(".xyz")
    print(output_file)
    
    



    
