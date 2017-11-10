'''
Georeader --

contains functions for reading national hydrography dataset 

'''

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

def getNHDWaterbodies(NHD_dir, coded=True):  
    '''
    getNHDWaterbodies

    Inputs:
    -------
    NHD_dir: directory path to extracted NHD shapefiles directory
    coded: whether or not to extract fcodes and include in output. 

    Outputs:
    -------
    Geodataframe containing NHDWaterbody data. 
    '''

    waterbodyfile = "NHDWaterbody.shp"
    codedbfile    = "NHDFCode.dbf"

    # remove trailing slash
    if NHD_dir[-1] == "/"
        NHD_dir = NHD_dir[:-1]

    
    waterbodydata = gpd.read_file("%s/%s" % (NHD_dir, waterbodyfile))

    if not coded:
        return(waterbodydata)

    codedb = gpd.read_file("%s/%s" %(NHD_dir, codedbfile))

    waterbodydatacoded = pd.merge(waterbodydata,
                                  codedb.drop('geometry', axis=1), 
                                  left_on='FCODE', right_on='FCODE',
                                  how='left')

    return(waterbodydatacoded)



