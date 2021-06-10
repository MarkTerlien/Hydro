#! /usr/bin/python

""" Template function """

# standard library imports
import sys
import logging

# related third party imports
import cx_Oracle
from easygui import *

# Matlib imports
import pylab
import matplotlib.patches as patches
from matplotlib.path import Path
#from matplotlib.patches import PathPatch
from numpy import asarray, concatenate, ones
from shapely.wkb import loads

# GDAL/OGR imports
from osgeo import gdal
#from osgeo import gdalconst
from osgeo import ogr
#from osgeo import osr

__author__="Terlien"
__date__ ="$9-okt-2009 11:50:05$"
__copyright__ = "Copyright 2009, ATLIS"

# Module name
MODULE_NAME = "LoadObjectDictionary"

# DB connect Parameters
DB_USER_SOURCE       = "DB_USER_SOURCE"
DB_PASSWORD_SOURCE   = "DB_PASSWORD_SOURCE"
DB_TNS_SOURCE        = "DB_TNS_SOURCE"
S57_OBJECT_FILE      = "S57_OBJECT_FILE"
S57_ATTRIBUTE_FILE   = "S57_ATTRIBUTE_FILE"
S57_FILE             = "S57 file"

# Database connection parameter values
PARAMETER_LIST_VALUE = {}
PARAMETER_LIST_VALUE [ DB_USER_SOURCE ]     = "sens"
PARAMETER_LIST_VALUE [ DB_PASSWORD_SOURCE ] = "senso"
PARAMETER_LIST_VALUE [ DB_TNS_SOURCE ]      = "10.20.0.49/sens11"
#PARAMETER_LIST_VALUE [ DB_TNS_SOURCE ]      = "82.204.46.43/senst"
PARAMETER_LIST_VALUE [ S57_OBJECT_FILE ]    = "c:/temp/ENC20ENO.7DI"
PARAMETER_LIST_VALUE [ S57_ATTRIBUTE_FILE ] = "c:/temp/ENC20ENA.7DI"
PARAMETER_LIST_VALUE [ S57_FILE ]           = "c:/temp/NO4E2831.000"

# Menu options
MNU_DATABASE_PARAMETERS   = "DATABASE_PARAMETERS"
MNU_CATALOG_MANAGEMENT    = "CATALOG_MANAGEMENT"
MNU_S57_OBJECT_FILE       = "S57_OBJECT_FILE"
MNU_S57_ATTRIBUTE_FILE    = "S57_ATTRIBUTE_FILE"
MNU_EXECUTE               = "EXECUTE"
MNU_SHOW                  = "SHOW"
MNU_S57_FROM_DB           = "S57_FROM_DB"
MNU_S57_FROM_FILE         = "S57_FROM_FILE"
MNU_GEOMETRIES_FROM_DB    = "GEOMETRIES_FROM_DB"
MNU_SELECT_S57_OBJECTS    = "SELECT_S57_OBJECTS"
MNU_EXIT                  = "EXIT"

# Menu options dictionary
MENU_OPTIONS = {}
MENU_OPTIONS [ MNU_DATABASE_PARAMETERS ] = "Set database logon parameters"
MENU_OPTIONS [ MNU_CATALOG_MANAGEMENT  ] = "Catalog management"
MENU_OPTIONS [ MNU_S57_OBJECT_FILE ]     = "Select S57 object file"
MENU_OPTIONS [ MNU_S57_ATTRIBUTE_FILE ]  = "Select S57 attribute file"
MENU_OPTIONS [ MNU_GEOMETRIES_FROM_DB ]  = "Show constructed geometries from db"
MENU_OPTIONS [ MNU_SHOW ]                = "Show parameters"
MENU_OPTIONS [ MNU_S57_FROM_DB ]         = "Show S57 features from db"
MENU_OPTIONS [ MNU_SELECT_S57_OBJECTS ]  = "Select S57 features from db"
MENU_OPTIONS [ MNU_S57_FROM_FILE ]       = "Show S57 features from file"
MENU_OPTIONS [ MNU_EXIT ]                = "Exit"

# Number of decimals coordinates
NR_DECIMALS = 8

# ENC globals
# VI = 'VI'
# VC = 'VC'
VI = 'ISO'
VC = 'BND'
CATALAOG_ID = 1

# Database connection class
class DbConnectionClass:
    """Connection class to Oracle database"""
    def __init__(self, DbUser, DbPass, DbConnect, parent_module):
        try :
            self.logger = logging.getLogger( parent_module + '.DbConnection')
            self.logger.info("Setup database connection")
            self.oracle_connection       = cx_Oracle.connect(DbUser, DbPass, DbConnect)
            self.oracle_cursor           = self.oracle_connection.cursor()
            self.oracle_cursor.arraysize = 100000
            self.oracle_cursor.execute("select 'established' from dual")
        except Exception, err:
            self.logger.critical("Setup database connection failed: ERROR: " + str(err))
            sys.exit("Execution stopped")
    def store_dictionary_files ( self, s57_object_file_name, s57_object_file_data, s57_attribute_file_name, s57_attribute_file_data ) :
        """Function to store files in database"""
        try :
            self.logger.info("Store directionary files in database")
            l_obj_file_clob = self.oracle_cursor.var(cx_Oracle.CLOB)
            l_obj_file_clob.setvalue(0, str(s57_object_file_data))
            l_att_file_clob = self.oracle_cursor.var(cx_Oracle.CLOB)
            l_att_file_clob.setvalue(0, str(s57_attribute_file_data))
            self.oracle_cursor.callproc("ndb_catalog_admin_pck.iud_catalog_definition",['I', s57_object_file_name, l_obj_file_clob, s57_attribute_file_name, l_att_file_clob])
        except Exception, err:
            self.logger.critical("Query on database failed: ERROR: " + str(err))
            sys.exit("Execution stopped")
    def get_features ( self, feature_code ) :
        try :
            self.logger.debug("Get features from database")
            feat = []
            if not feature_code :
                feature_code = '%'
            stmt  = "select feature_code from ndb_feature_object where feature_code like \'" + str(feature_code) + "%\'"
            self.oracle_cursor.execute( stmt )
            resultset = self.oracle_cursor.fetchmany()
            if resultset :
                for row in resultset :
                    feat.append(str(row[0]))
            self.logger.info("Number of featurs to plot " + str(len(feat)))
            return feat
        except Exception, err:
            self.logger.critical("Get features from database failed: ERROR: " + str(err))
            sys.exit("Execution stopped")
    def get_geometry ( self, feature_code ) :
        try :
            self.logger.debug("Get geometry from database")
            geom = []
            if not feature_code :
                feature_code = '99'
            stmt  = "select SDO_UTIL.TO_WKTGEOMETRY(ndb_object_iud_pck.create_feature_geometry(o.feature_code)) from ndb_feature_object o where o.feature_code = \'" + str(feature_code) + "\'"
            self.oracle_cursor.execute( stmt )
            resultset = self.oracle_cursor.fetchmany()
            if resultset :
                for row in resultset :
                    geom = str(row[0])
            return geom
        except Exception, err:
            self.logger.critical("Get geometries from database failed: ERROR: " + str(err))
            sys.exit("Execution stopped")
    def get_spatials ( self, feature_code ) :
        try :
            self.logger.debug("Get spatials from database")
            spat = {}
            stmt = 'select t2.spatial_code, t2.geometry.get_wkt()'
            stmt = stmt + ' from   ndb_feature_object t1, ndb_spatial_object t2, ndb_feat_spat_relation t3'
            stmt = stmt + ' where  t1.feature_code = t3.feat_code_from and t3.spat_code_to  = t2.spatial_code'
            if feature_code :
                stmt = stmt + ' and    t1.feature_code  = :FEATCODE'
            stmt = stmt + ' union all '
            stmt = stmt + ' select t5.spatial_code, t5.geometry.get_wkt() '
            stmt = stmt + ' from   ndb_feature_object t1, ndb_spatial_object t2, ndb_feat_spat_relation t3 '
            stmt = stmt + ' ,      ndb_spat_spat_relation t4, ndb_spatial_object t5 '
            stmt = stmt + ' where  t1.feature_code = t3.feat_code_from and t3.spat_code_to  = t2.spatial_code '
            if feature_code :
                stmt = stmt + ' and    t1.feature_code  = :FEATCODE'
            stmt = stmt + ' and    t4.spat_code_from = t2.spatial_code '
            stmt = stmt + ' and    t4.spat_code_to   = t5.spatial_code '
            if feature_code :
                self.oracle_cursor.execute( stmt, FEATCODE = feature_code )
            else :
                self.oracle_cursor.execute( stmt )
            resultset = self.oracle_cursor.fetchmany()
            if resultset :
                for row in resultset :
                    spat[str(row[0])] = str(row[1])
            self.logger.info("Number of spatials to plot: " + str(len(spat)))
            return spat
        except Exception, err:
            self.logger.critical("Get spatials from database failed: ERROR: " + str(err))
            sys.exit("Execution stopped")
    def get_mbr ( self ) :
        self.logger.info("Get MBR of features")
        stmt = 'select sdo_util.to_wktgeometry(sdo_aggr_mbr(o.geometry)) from ndb_spatial_object o'
        self.oracle_cursor.execute( stmt )
        resultset = self.oracle_cursor.fetchmany()
        if resultset :
            for row in resultset :
                mbr_geometry = str(row[0])
        return mbr_geometry
    def select_s57_objects( self, obj_class_acr, obj_sel_str ):
        self.logger.info("Select S57 of features")
        mbr_geom   = self.get_mbr()
        mbr_clob   = self.oracle_cursor.var(cx_Oracle.CLOB)
        mbr_clob.setvalue(0, str(mbr_geom))
        nr_of_rows = self.oracle_cursor.callfunc("ndb_interface_pck.select_object", str, [CATALAOG_ID, obj_class_acr, mbr_clob, obj_sel_str, 'T'])
        return nr_of_rows
    def get_spatial_rows ( self ) :
        self.logger.info("Select spatials")
        stmt = 'select spatial_code, attribute_string, sdo_util.to_wktgeometry(geometry), \'N\' from ndb_spatial_object_temp'
        self.oracle_cursor.execute( stmt )
        resultset = self.oracle_cursor.fetchmany()
        return resultset
    def get_feature_rows ( self ) :
        self.logger.info("Select features")
        stmt = 'select feature_code, object_class_acronym, feature_gtype, attribute_string , \'N\' from ndb_feature_object_temp'
        self.oracle_cursor.execute( stmt )
        resultset = self.oracle_cursor.fetchmany()
        return resultset
    def get_feat_feat_rel_rows( self ) :
        self.logger.info("Select feat-feat relations")
        stmt = 'select feat_code_from, feat_code_to, pointer_index_nr, relation_type from ndb_feat_feat_relation_temp'
        self.oracle_cursor.execute( stmt )
        resultset = self.oracle_cursor.fetchmany()
        return resultset
    def get_feat_spat_rel_rows( self ) :
        self.logger.info("Select feat-spat relations")
        stmt = 'select feat_code_from, spat_code_to, pointer_index_nr, ornt, usag, mask from ndb_feat_spat_relation_temp'
        self.oracle_cursor.execute( stmt )
        resultset = self.oracle_cursor.fetchmany()
        return resultset
    def get_spat_spat_rel_rows( self ) :
        self.logger.info("Select spat-spat relations")
        stmt = 'select spat_code_from, spat_code_to, pointer_index_nr, ornt, usag, mask, topi from ndb_spat_spat_relation_temp'
        self.oracle_cursor.execute( stmt )
        resultset = self.oracle_cursor.fetchmany()
        return resultset
    def commit_close( self ) :
        """Function to commit and close connection"""
        self.oracle_connection.commit()
        self.oracle_connection.close()

# For plotting polygons with holes (from: http://sgillies.net/blog/1013/painting-punctured-polygons-with-matplotlib/)
def ring_coding(ob):
    # The codes will be all "LINETO" commands, except for "MOVETO"s at the
    # beginning of each subpath
    n = len(ob.coords)
    codes = ones(n, dtype=Path.code_type) * Path.LINETO
    codes[0] = Path.MOVETO
    return codes

def pathify(polygon):
    # Convert coordinates to path vertices. Objects produced by Shapely's
    # analytic methods have the proper coordinate order, no need to sort.
    # MTJ: Refactor to work with ogr_polygon
    # The underlying storage is made up of two parallel numpy arrays:
    # vertices: an Nx2 float array of vertices
    # codes: an N-length uint8 array of vertex types
    vertices = concatenate(
                    [asarray(polygon.exterior)]
                    + [asarray(r) for r in polygon.interiors])
    codes = concatenate(
                [ring_coding(polygon.exterior)]
                + [ring_coding(r) for r in polygon.interiors])
    return Path(vertices, codes)

# Function to start gui
def gui_start () :
    while True :
        msg   = "What do you want?"
        options = [ MENU_OPTIONS [ MNU_DATABASE_PARAMETERS ],  MENU_OPTIONS [ MNU_CATALOG_MANAGEMENT ], MENU_OPTIONS [ MNU_S57_FROM_FILE ], MENU_OPTIONS [ MNU_S57_FROM_DB ], MENU_OPTIONS [ MNU_GEOMETRIES_FROM_DB ], MENU_OPTIONS [ MNU_SELECT_S57_OBJECTS ], MENU_OPTIONS [ MNU_SHOW ], MENU_OPTIONS [ MNU_EXIT ] ]
        reply=buttonbox(msg,None,options)
        if reply == MENU_OPTIONS [ MNU_DATABASE_PARAMETERS ] :
            gui_db_parameters ()
        if reply == MENU_OPTIONS [ MNU_CATALOG_MANAGEMENT  ] :
            load_dictionary_files ()
        elif reply == MENU_OPTIONS [ MNU_S57_FROM_FILE ] :
            plot_s57_objects_from_file()
        elif reply == MENU_OPTIONS [ MNU_S57_FROM_DB ] :
            plot_s57_objects_from_db ()
        elif reply == MENU_OPTIONS [ MNU_GEOMETRIES_FROM_DB ] :
            plot_s57_geometries_from_db ()
        elif reply == MENU_OPTIONS [ MNU_SELECT_S57_OBJECTS ] :
            query_s57_database ()
        elif reply == MENU_OPTIONS [ MNU_SHOW ] :
            gui_show_parameters ()
        elif reply == MENU_OPTIONS [ MNU_EXIT ] :
            break

# Function to build gui for input db connection parameters
def gui_db_parameters() :
    title = 'Database connection parameters'
    msg   = "Give database connection parameters"
    field_names   = [ DB_TNS_SOURCE, DB_USER_SOURCE , DB_PASSWORD_SOURCE ]
    return_values = [ PARAMETER_LIST_VALUE [DB_TNS_SOURCE], PARAMETER_LIST_VALUE [DB_USER_SOURCE], PARAMETER_LIST_VALUE [DB_PASSWORD_SOURCE] ]
    return_values = multpasswordbox(msg, title, field_names, return_values)
    if return_values :
        PARAMETER_LIST_VALUE [DB_TNS_SOURCE]      = return_values[0]
        PARAMETER_LIST_VALUE [DB_USER_SOURCE]     = return_values[1]
        PARAMETER_LIST_VALUE [DB_PASSWORD_SOURCE] = return_values[2]

# Function to build gui for file selection
def gui_file_selection ( box_title, file_parameter ) :
    title = box_title
    msg   = 'Select file'
    file  = fileopenbox(msg, title, str(PARAMETER_LIST_VALUE[file_parameter]))
    PARAMETER_LIST_VALUE[file_parameter] = str(file)

# Function to plot features direct
def plot_s57_geometries_from_db () :
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    logger.info("Plot constructed geometries from db")
    # Ask user for feature
    feature = enterbox(msg='Give feature ID', title='Feature ID input', default='7CFE', strip=True)
    # Get features
    OracleConnection = DbConnectionClass ( PARAMETER_LIST_VALUE[ DB_USER_SOURCE ], PARAMETER_LIST_VALUE[ DB_PASSWORD_SOURCE ], PARAMETER_LIST_VALUE[ DB_TNS_SOURCE ], MODULE_NAME )
    feat_list        = OracleConnection.get_features( feature )
    # Popup select box
    msg     = "Select feature"
    title   = "Feature"
    feat_code_list = multchoicebox(msg, title, feat_list)
    # Get gemetries for selected feature
    feat_index = 0
    for feat_code in feat_code_list :
        logger.info("Plot feature " + str(feat_code))
        geom     = OracleConnection.get_geometry( feat_code )
        ogr_geom = ogr.CreateGeometryFromWkt( str(geom) )
        if ogr_geom.GetGeometryName() == 'POLYGON' :
            #path = pathify(ogr_geom)
            #patch = patches.PathPatch(path, facecolor='#cccccc', edgecolor='#999999')
            coord_list = []
            ring_index  = 0
            poly_index  = 0
            polygon     = ogr_geom
            for nr_ring in range ( polygon.GetGeometryCount() ):
                ring        = polygon.GetGeometryRef( nr_ring )
                for i in range(ring.GetPointCount()) :
                    point = [float(ring.GetX(i)), float(ring.GetY(i))]
                    coord_list.append(point)
                if ring_index == 0 :
                    logger.debug("Plot polygon")
                    poly = patches.Polygon( coord_list, facecolor='green')
                    ax.add_patch(poly)
                else :
                    None
                ring_index = ring_index + 1
            poly_index = poly_index + 1
        if ogr_geom.GetGeometryName() == 'LINESTRING' :
            logger.debug("Plot linestring")
            x = []
            y = []
            for i in range(ogr_geom.GetPointCount()) :
                x.append(ogr_geom.GetX(i))
                y.append(ogr_geom.GetY(i))
            pylab.plot(x,y,'-',color='r')
        if ogr_geom.GetGeometryName() == 'POINT' :
            logger.debug("Plot point")
            x = [ float(ogr_geom.GetX()) ]
            y = [ float(ogr_geom.GetY()) ] 
            symbol = 'o'
            color  = 'y'
            pylab.plot(x, y, symbol, color=color)
        feat_index = feat_index = 1
    logger.info ( str(feat_index) + " features plotted")
    ax.set_xlim((-180.0,180.0))
    ax.set_ylim((-90.0,90.0))
    pylab.show()

def query_s57_database():
    logger.info("Query_s57_database")
    OracleConnection     = DbConnectionClass ( PARAMETER_LIST_VALUE[ DB_USER_SOURCE ], PARAMETER_LIST_VALUE[ DB_PASSWORD_SOURCE ], PARAMETER_LIST_VALUE[ DB_TNS_SOURCE ], MODULE_NAME )
    object_class_acronym = enterbox(msg='Give Acronym'      , title='S57 acronym input'  , default='', strip=True)
    object_select_string = enterbox(msg='Give select string', title='Select string input', default='', strip=True)
    nr_of_rows           = OracleConnection.select_s57_objects(object_class_acronym, object_select_string)
    nr_of_rows_list      = nr_of_rows.rstrip().split(',')
    logger.info("Plot results")
    logger.info("Nr of features            :" + str(nr_of_rows_list[0]))
    logger.info("Nr of feat-spat relations :" + str(nr_of_rows_list[1]))
    logger.info("Nr of feat-feat relations :" + str(nr_of_rows_list[2]))
    logger.info("Nr of spatials            :" + str(nr_of_rows_list[3]))
    logger.info("Nr of spat-spat relations :" + str(nr_of_rows_list[4]))
    msg   = "Select what to Show"
    title = "S57 query tool"
    options = ["Feature","Spatial","Feat-Spat relation","Feat-Feat relation","Spat-Spat relation"]
    choices = multchoicebox(msg,title, options)
    result_list = []
    if "Feature" in choices :
        logger.info("Get features")
        result_list.append("-----------------------------\n")
        result_list.append("-- FEATURES\n")
        result_list.append("-----------------------------\n")
        resultset = OracleConnection.get_feature_rows()
        if resultset :
            logger.info("Features found")
            i = 0
            for row in resultset :
                i = i + 1
                result_list.append("Feature number   : " + str(i)      + "\n" )
                result_list.append("Feature code     : " + str(row[0]) + "\n" )
                result_list.append("Object class acr : " + str(row[1]) + "\n" )
                result_list.append("feature gtype    : " + str(row[2]) + "\n" )
                result_list.append("Attribute string : " + str(row[3]) + "\n")
                result_list.append("-----------------------------\n")
    if "Spatial" in choices :
        logger.info("Get spatials")
        result_list.append("-----------------------------\n")
        result_list.append("-- SPATIALS\n")
        result_list.append("-----------------------------\n")
        resultset = OracleConnection.get_spatial_rows()
        if resultset :
            logger.info("Spatials found")
            i = 0
            for row in resultset :
                i = i + 1
                result_list.append("Spatial number   : " + str(i)      + "\n" )
                result_list.append("Spatial code     : " + str(row[0]) + "\n"   )
                result_list.append("Attribute string : " + str(row[1]) + "\n" )
                result_list.append("Geometry         : " + str(row[2]) + "\n" )
                result_list.append("Readonly         : " + str(row[3]) + "\n" )
                result_list.append("-----------------------------\n")
    if "Feat-Feat relation" in choices :
        logger.info("Get feat-feat relations")
        result_list.append("-----------------------------\n")
        result_list.append("-- FEATURE TO FEATURE RELATIONS\n")
        result_list.append("-----------------------------\n")
        resultset = OracleConnection.get_feat_feat_rel_rows()
        if resultset :
            logger.info("Feat-feat relations found")
            i = 0
            for row in resultset :
                i = i + 1
                result_list.append("Feat_feat relation : " + str(i)      + "\n" )
                result_list.append("Feat_code_from   : " + str(row[0]) + "\n" )
                result_list.append("Feat_code_to     : " + str(row[1]) + "\n" )
                result_list.append("Pointer_index_nr : " + str(row[2]) + "\n" )
                result_list.append("Relation_type    : " + str(row[3]) + "\n" )
                result_list.append("-----------------------------\n")
    if "Feat-Spat relation" in choices :
        logger.info("Get feat-spat relations")
        result_list.append("-----------------------------\n")
        result_list.append("-- FEATURE TO SPATIAL RELATIONS\n")
        result_list.append("-----------------------------\n")
        resultset = OracleConnection.get_feat_spat_rel_rows()
        if resultset :
            logger.info("Feat-spat relations found")
            i = 0
            for row in resultset :
                i = i + 1
                result_list.append("Feat_spat relation : " + str(i)      + "\n" )
                result_list.append("Feat_code_from   : " + str(row[0]) + "\n" )
                result_list.append("Spat_code_to     : " + str(row[1]) + "\n" )
                result_list.append("Pointer_index_nr : " + str(row[2]) + "\n" )
                result_list.append("Orientation      : " + str(row[3]) + "\n" )
                result_list.append("Usage            : " + str(row[4]) + "\n" )
                result_list.append("Mask             : " + str(row[5]) + "\n" )
                result_list.append("-----------------------------\n")
    if "Spat-Spat relation" in choices :
        logger.info("Get spat-spat relations")
        result_list.append("-----------------------------\n")
        result_list.append("-- SPATIAL TO SPATIAL RELATIONS\n")
        result_list.append("-----------------------------\n")
        resultset = OracleConnection.get_spat_spat_rel_rows()
        if resultset :
            logger.info("Spat-spat relations found")
            i = 0
            for row in resultset :
                i = i + 1
                result_list.append("Feat_spat relation : " + str(i)      + "\n" )
                result_list.append("Spat_code_from   : " + str(row[0]) + "\n" )
                result_list.append("Spat_code_to     : " + str(row[1]) + "\n" )
                result_list.append("Pointer_index_nr : " + str(row[2]) + "\n" )
                result_list.append("Orientation      : " + str(row[3]) + "\n" )
                result_list.append("Usage            : " + str(row[4]) + "\n" )
                result_list.append("Mask             : " + str(row[5]) + "\n" )
                result_list.append("Topoly indicator : " + str(row[6]) + "\n" )
                result_list.append("-----------------------------\n")
    textbox ("S57 features", "S57 features elements found", result_list)
    OracleConnection.commit_close()

# Function to build map
def plot_s57_objects_from_db() :
    logger.info("Plot_s57_objects_from_db")
    # Ask user for feature
    feature = enterbox(msg='Give feature ID', title='Feature ID input', default='7CFE', strip=True)
    # Get features
    OracleConnection = DbConnectionClass ( PARAMETER_LIST_VALUE[ DB_USER_SOURCE ], PARAMETER_LIST_VALUE[ DB_PASSWORD_SOURCE ], PARAMETER_LIST_VALUE[ DB_TNS_SOURCE ], MODULE_NAME )
    feat_list        = OracleConnection.get_features( feature )
    # Popup select box
    msg     = "Select feature"
    title   = "Feature"
    feat_code_list = multchoicebox(msg, title, feat_list)
    # Get spaials for selected feature
    for feat_code in feat_code_list :
        spat_list = OracleConnection.get_spatials( feat_code )
        nr_spat = 0
        # Write spatials to plot array
        for spat_code in spat_list.keys() :
            logger.debug("Plot spatial " + str(spat_code) )
            logger.debug(str(spat_list[spat_code]))
            ogr_geom = ogr.CreateGeometryFromWkt( str(spat_list[spat_code]) )
            x_vi = []
            y_vi = []
            x_vc = []
            y_vc = []
            x_ve = []
            y_ve = []
            if ogr_geom.GetGeometryName() == 'POINT' :
                if VC in str(spat_code) :
                    x_vc.append(round(float(ogr_geom.GetX()),NR_DECIMALS))
                    y_vc.append(round(float(ogr_geom.GetY()),NR_DECIMALS))
                    symbol = 'o'
                    color  = 'g'
                    pylab.plot(x_vc,y_vc,symbol,color=color)
                elif VI in str(spat_code) :
                    x_vi.append(round(float(ogr_geom.GetX()),NR_DECIMALS))
                    y_vi.append(round(float(ogr_geom.GetY()),NR_DECIMALS))
                    symbol = 'o'
                    color  = 'r'
                    pylab.plot(x_vi,y_vi,symbol,color=color)
            if ogr_geom.GetGeometryName() == 'LINESTRING' :
                for i in range(ogr_geom.GetPointCount()) :
                    x_ve.append(round(float(ogr_geom.GetX(i)),NR_DECIMALS))
                    y_ve.append(round(float(ogr_geom.GetY(i)),NR_DECIMALS))
                    symbol = '-'
                    color  = 'y'
                    pylab.plot(x_ve,y_ve,symbol,color=color)
            nr_spat = nr_spat + 1
        logger.info ( str(nr_spat) + " spatials plotted for feature " + str(feat_code))
    pylab.axis('equal')
    #pylab.xlim([3.7,4.0])
    #pylab.ylim([50.0,53.0])
    OracleConnection.commit_close()
    pylab.xlabel("Longitud")
    pylab.ylabel("Latitud")
    pylab.grid(True)
    pylab.title("Spatials")
    pylab.show()

# Function to build gui to show parameters
def gui_show_parameters () :
    txt = ""
    for parameter in PARAMETER_LIST_VALUE :
        txt = txt + str(parameter) + ": " + str(PARAMETER_LIST_VALUE[parameter]) + "\n"
    title = "Parameters"
    msg  = "Parameter values"
    textbox(msg, title, txt, None)

# Function to plot features from S57 file
def plot_s57_objects_from_file ( ) :
    logger.info("Plot s57 features from file")
    fig = pylab.figure()
    ax  = fig.add_subplot(111)
    # Get file
    gui_file_selection ( MENU_OPTIONS [ MNU_S57_FROM_FILE ], S57_FILE  )
    # Clear S57 options if set or our results will be messed up.
    if gdal.GetConfigOption( 'OGR_S57_OPTIONS', '' ) != '':
        gdal.SetConfigOption( 'OGR_S57_OPTIONS', 'RETURN_PRIMITIVES=ON' )
    # Open s57 FILE
    ds             = ogr.Open( PARAMETER_LIST_VALUE [ S57_FILE ] )
    # Popup select box for feature
    msg               = "Select feature type"
    title             = "Feature type"
    feat_type_list    = [ ds.GetLayer(i).GetName() for i in xrange(ds.GetLayerCount()) ]
    feature_type_list = multchoicebox(msg, title, feat_type_list)
    # Plot selected feature types
    if len(feature_type_list) > 0 :
        for feature_type in feature_type_list :
            src_features   = ds.GetLayerByName( feature_type )
            feature        = src_features.GetNextFeature()
            nr_features    = 0
            nr_points      = 0
            x = []
            y = []
            z = []
            while feature is not None:
                nr_features   = nr_features + 1
                ogr_geom      = feature.GetGeometryRef()
                spatial_type  = ogr_geom.GetGeometryName()
                for j in range( feature.GetFieldCount() ) :
                    if feature.IsFieldSet(j) :
                        field_def  = feature.GetFieldDefnRef(j)
                        field_name = field_def.GetName()
                        logger.debug("Field name    = " + str(field_name) + " has value " + str(feature.GetFieldAsString(field_name)))
                logger.debug("Processing feature = " + str(nr_features)                )
                logger.debug("Spatial type       = " + str(spatial_type)               )
                logger.debug("Number of points   = " + str(ogr_geom.GetGeometryCount()))
                if str(spatial_type) == 'POINT' :
                    x.append(ogr_geom.GetX())
                    y.append(ogr_geom.GetY())
                    ax.plot(x,y,'o',color='g')
                    x = []
                    y = []
                if str(spatial_type) == 'LINESTRING' :
                    for i in range(ogr_geom.GetPointCount()) :
                        x.append(ogr_geom.GetX(i))
                        y.append(ogr_geom.GetY(i))
                    ax.plot(x,y,'-',color='r')
                    x = []
                    y = []
                if str(spatial_type) == 'POLYGON' :
                    ring_index  = 0
                    poly_index  = 0
                    mult_index  = 0
                    polygon      = ogr_geom
                    coord_list   = []
                    for nr_ring in range ( polygon.GetGeometryCount() ):
                        ring        = polygon.GetGeometryRef( nr_ring )
                        for i in range(ring.GetPointCount()) :
                            point = [float(ring.GetX(i)), float(ring.GetY(i))]
                            coord_list.append(point)
                        if ring_index == 0 :
                            logger.debug("Plot polygon")
                            poly = patches.Polygon( coord_list, facecolor='green')
                            ax.add_patch(poly)
                        else :
                            None
                        ring_index = ring_index + 1
                    poly_index = poly_index + 1
                if str(spatial_type) == 'MULTIPOLYGON' :
                    for nr_polygon in range ( ogr_geom_in.GetGeometryCount() ) :
                        polygon      = ogr_geom_in.GetGeometryRef( nr_polygon )
                        for nr_ring in range ( polygon.GetGeometryCount() ):
                            ring        = polygon.GetGeometryRef( nr_ring )
                            coord_list  = []
                            for i in range(ring.GetPointCount()) :
                                point = [float(ring.GetX(i)), float(ring.GetY(i))]
                                coord_list.append(point)
                            if ring_index == 0 :
                                logger.debug("Plot polygon")
                                poly = patches.Polygon( coord_list, facecolor='green')
                                ax.add_patch(poly)
                            else :
                                None
                            ring_index = ring_index + 1
                        poly_index = poly_index + 1
                        ring_index = 0
                    mult_index = mult_index + 1
                if str(spatial_type) == 'MULTIPOINT' :
                    for i in range(ogr_geom.GetGeometryCount()):
                        nr_points = nr_points + 1
                        ogr_point = ogr_geom.GetGeometryRef( i )
                        x_v = ogr_point.GetX()
                        y_v = ogr_point.GetY()
                        z_v = ogr_point.GetZ()
                        if  nr_points == 1 :
                            x_min = x_v
                            x_max = x_v
                            y_min = y_v
                            y_max = y_v
                            z_min = z_v
                            z_max = z_v
                            x.append(x_v)
                            y.append(y_v)
                            z.append(z_v)
                        else :
                            if x_v < x_min :
                                x_min = x_v
                            if x_v > x_max :
                                x_max = x_v
                            if y_v < y_min :
                                y_min = y_v
                            if y_v > y_max :
                                y_max = y_v
                            if z_v < z_min :
                                z_min = z_v
                            if z_v > z_max :
                                z_max = z_v
                            x.append(x_v)
                            y.append(y_v)
                            z.append(z_v)
                    #pylab.scatter(x,y,c=z,edgecolors='none',vmin=z_min,vmax=z_max)
                    ax.scatter(x,y,c=z,edgecolors='none',vmin=z_min,vmax=z_max)
                    #pylab.colorbar()
                    #ax.colorbar()
                    x = []
                    y = []
                    z = []
                feature = src_features.GetNextFeature()
        ds.Destroy()
        ax.set_xlim((-180.0,180.0))
        ax.set_ylim((-90.0,90.0))
        pylab.xlabel("Longitud")
        pylab.ylabel("Latitud")
        pylab.grid(True)
        pylab.title(feature_type)
        pylab.show()
    else :
        logger.info("No features selected")
    
# Function to start DB procedure to load dictionary files
def load_dictionary_files () :
    # Load object defintion file
    gui_file_selection ( MENU_OPTIONS [ MNU_S57_OBJECT_FILE ], S57_OBJECT_FILE )
    logger.info("Object file: " + str(S57_OBJECT_FILE) )
    # Load attribute defintion file
    gui_file_selection ( MENU_OPTIONS [ MNU_S57_ATTRIBUTE_FILE ], S57_ATTRIBUTE_FILE  )
    logger.info("Attribute file: " + str(S57_ATTRIBUTE_FILE) )
    # Build database connection and store dictionary file
    OracleConnection = DbConnectionClass ( PARAMETER_LIST_VALUE[ DB_USER_SOURCE ], PARAMETER_LIST_VALUE[ DB_PASSWORD_SOURCE ], PARAMETER_LIST_VALUE[ DB_TNS_SOURCE ], MODULE_NAME )
    OracleConnection.store_dictionary_files ( PARAMETER_LIST_VALUE [ S57_OBJECT_FILE ], open(PARAMETER_LIST_VALUE [ S57_OBJECT_FILE ]).read(), PARAMETER_LIST_VALUE [ S57_ATTRIBUTE_FILE ], open(PARAMETER_LIST_VALUE [ S57_ATTRIBUTE_FILE ]).read()  )
    OracleConnection.commit_close()
    logger.info("Catalog sucessfully imported")

if __name__ == "__main__":
    try:
        try :
            # Initialize logger
            logger = logging.getLogger(MODULE_NAME)
            #logger.setLevel(logging.INFO)
            logger.setLevel(logging.DEBUG)
            stream_hdlr = logging.StreamHandler()
            formatter   = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            stream_hdlr.setFormatter(formatter)
            logger.addHandler(stream_hdlr)
            # Start GUI
            gui_start ()
        except Exception, err:
            logger.info ( "Installation failed: ERROR: %s\n" % str(err) )
    except Exception, err:
        print "Installation failed: ERROR: %s\n" % str(err)
        sys.exit(1)
    else:
        sys.exit(0)
