'''
Downloader --

Utilities for downloading sentinel-2 images.

'''

import os
from sentinelsat import SentinelAPI
from pandas.core.indexes.base import Index
import zipfile

try: 
    SENTINEL_USER = os.environ['SENTINEL_API_USER']
    SENTINEL_PASS = os.environ['SENTINEL_API_PASS']
except KeyError:
    raise ImportError("Environment variables SENTINEL_API_USER and"
                      " SENTINEL_API_PASS must be set")


def searchOverlapping(geom, search_args):
    '''
    use sentinel API to search for scenes that overlap with geom

    Inputs:
    -------
    geom: shapely geometry.
    search_args : passed onto SentinelAPI.query, read the docs.

    Outputs:
    -------
    Geodataframe with Sentinel Products overlapping with geom.
    '''

    api = SentinelAPI(SENTINEL_USER,
                      SENTINEL_PASS,
                      'https://scihub.copernicus.eu/dhus/')

    products = api.query(geom, **search_args)
    if len(products) == 0: 
        return(None)
    return(api.to_geodataframe(products))


def downloadProductSentinel(product, dest_dir, remove_zip=False):
    '''
    download and extract sentinel product zip file. 

    Inputs: 
    ------
    product: must be a product identifier, like '93b051ba-504c-4746-8f74-c422187d33aa'. These are 
    typically the indices of the dataframe containing
    the products. 

    dest_dir: imagery destination directory. 

    remove_zip: whether to delete zipfile. 


    Outputs:
    -------
    zipfilepath, imagepath (.SAFE)
    '''

    api = SentinelAPI(SENTINEL_USER,
                      SENTINEL_PASS,
                      'https://scihub.copernicus.eu/dhus/')



    downloadResult = api.download_all(product, directory_path = dest_dir)

    if type(product) == Index:
        #strings from now on
        product = product[0]

    zipfilePath = downloadResult[0][product]['path']

    file = zipfile.ZipFile(zipfilePath, 'r')
    file.extractall(dest_dir)

    dirname = zipfilePath.split('.')[0] + '.SAFE/'

    return(zipfilePath, dirname)



def downloadProductAWS(productTitle, dest_dir, bands=None, threading=True):
    '''
    uses sentinelhub/AWS downloader. (*way* quicker)
    
    productTitle is NOT the ID. it's the filename. 
    
    bands should be list of integers or none. 
    '''
    from sentinelhub import download_safe_format
    
    ret_fpath = os.path.join(dest_dir, "%s.SAFE" % productTitle)
    
    params = {
        'product_id' : productTitle,
        'folder'  : dest_dir, 
        'threaded_download' : threading
    }
    
    if bands is not None:
        bands = ["B%02d" %b for b in bands] #S-2 radiometric bands are BXX
        download_safe_format(bands=bands, **params)
    else:
        download_safe_format(**params)
        
    return(ret_fpath)

    

