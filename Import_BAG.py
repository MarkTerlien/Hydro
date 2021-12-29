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

INPUT_FILE  = 'H12698_MB_4m_MLLW_2of3.bag'


if __name__ == "__main__":

    bag = h5py.File(INPUT_FILE)
    print(type(bag))
    print(bag.name)
    print(bag.filename)

    for item in bag.items():
        print(item)

    for value in bag.values():
        print(value)

    print(list(bag['BAG_root'].items()))

    root = bag['BAG_root']
    print(root.name)
    print(root.parent)
    print(list(root.items()))

    elev_node = root['elevation']
    print(type(elev_node))
    elev = elev_node[()]

    print(elev.min(), elev.max())   

    #elev[elev > 10000] = np.NAN
    #print(np.nanmin(elev), np.nanmax(elev))
    #print(type(elev))

    # Metadata
    metadata_node = root['metadata']
    #print(type(metadata_node))
    #print(metadata_node)
    buffer = BytesIO(metadata_node[()])
    tree = etree.parse(buffer)
    root = tree.getroot()
    #print(etree.tostring(root, pretty_print=True).decode('ascii'))

    metadata_xml = xml.dom.minidom.parseString(etree.tostring(root, pretty_print=True).decode('ascii'))
    print('westBoundLongitude: ' + str( metadata_xml.getElementsByTagName('gmd:westBoundLongitude')[0].getElementsByTagName('gco:Decimal')[0].firstChild.nodeValue))
    print('eastBoundLongitude: ' + str( metadata_xml.getElementsByTagName('gmd:eastBoundLongitude')[0].getElementsByTagName('gco:Decimal')[0].firstChild.nodeValue))
    print('southBoundLatitude: ' + str( metadata_xml.getElementsByTagName('gmd:southBoundLatitude')[0].getElementsByTagName('gco:Decimal')[0].firstChild.nodeValue))
    print('northBoundLatitude: ' + str( metadata_xml.getElementsByTagName('gmd:northBoundLatitude')[0].getElementsByTagName('gco:Decimal')[0].firstChild.nodeValue))

    resolution = float( metadata_xml.getElementsByTagName('gmd:MD_Dimension')[0].getElementsByTagName('gmd:resolution')[0].getElementsByTagName('gco:Measure')[0].firstChild.nodeValue)

    coordinates = str( metadata_xml.getElementsByTagName('gml:coordinates')[0].childNodes[0].nodeValue )
    print('gml:coordinates: ' + str( coordinates ))
    ll_x = float(coordinates.rstrip().split()[0].rstrip().split(',')[0])
    ll_y = float(coordinates.rstrip().split()[0].rstrip().split(',')[1])
    print( ll_x)
    print( ll_y)

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
    
    



    
