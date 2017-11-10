'''
waterquality 

contains utilities for processing waterquality data from WA Ecology
'''

import geopandas as gpd
import pandas as pd
from fuzzywuzzy import process
from shapely.geometry import Point


def loadWaterQualityData(quality, locations=None):
    '''
    loadWaterQualityData:

    Inputs:
    -------
    quality: CSV file from [WA Ecology](https://www.nwtoxicalgae.org/Data.aspx)
    locations: EIMLocations file from WA Ecology defining sampling site locations. 

    Outputs: 
    --------
    pandas dataframe containing data in quality with optional
    '''
    ecodata = pd.read_csv(quality)

    # drop locationless sites (minimal loss):
    ecodata = ecodata.dropna(axis=0)

    if locations is None:
        # just the data, no location merge.
        return(ecodata)

    locdb = pd.read_csv(locations)

    # Fuzzy string match to join locations in database to locations in ecology data.
    loc_idx = dict(zip(set(ecodata.Site),
                       list(map(lambda x: process.extractOne(x, locdb.Location_Name)[2], set(ecodata.Site)))))

    loc_idx_ref = ecodata.Site.map(lambda x: loc_idx[x])

    ecodata['loc_idx'] = loc_idx_ref

    ecodataMerged = ecodata.merge(locdb[['Latitude_Decimal_Degrees',   'Longitude_Decimal_Degrees']], how='left', left_on='loc_idx', right_index=True)

    return(ecodataMerged)




