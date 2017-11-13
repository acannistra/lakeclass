'''
Processor ---

Utilities for processing (loading, cropping, combining, displaying) 
Sentinel-2 images. 

'''
import rasterio
from rasterio import mask
from functools import partial
import pyproj
from shapely.ops import transform
from shapely.geometry import mapping
import numpy as np
import glob
from os import path

def _stackBands(bands):
    '''
    stacks bands in one raster, (x, y, d) array where d is number of 
    bands in bands. 

    Inputs:
    -------
    bands: array of single-band rasterio objects. 

    Outputs:
    -------
    (x,y,d) array
    '''

    subarrs = []

    for b in bands:
        _b = b.read()
        _b = np.transpose(_b, [1,2,0]) ## (x, y, 1)
        subarrs.append(_b)

    stack = np.stack(subarrs, axis=2) ## stack 3rd dimension

    return (stack)

def extractGeom(geom, raster, geom_epsg):
    '''
    extracts the geometry geom from the raster, returns the masked array 
    from rasterio.mask.mask. 

    Inputs:
    -------
    geom: shapely geometry
    raster: rasterio raster object
    src_epsg: EPSG code of geometry projection
    
    Outputs:
    --------
    Same as rasterio.mask.mask
    '''

    project_fun = partial(pyproj.transform, 
                          pyproj.Proj(init="epsg:%s" % geom_epsg), 
                          pyproj.Proj(init=raster.crs['init']))

    geom = transform(project_fun, geom)

    return(mask.mask(raster, [mapping(geom)], crop=True))


def extractGeomToFile(geom, raster, geom_epsg, file):
    '''
    Saves extracted raster to TIFF file. (file must have .TIFF extension)
    
    '''
    # extract raster
    image, transform = extractGeom(geom, raster, geom_epsg)

    # copy old raster metadata to new one. 
    outfile_meta = raster.meta.copy()

    # update metadata
    outfile_meta.update({"driver": "GTiff",
                         "height": image.shape[1],
                         "width": image.shape[2],
                         "transform": transform})
    #write file
    with rasterio.open(file, 'w', **outfile_meta) as dest:
        dest.write(image)



def openSentinelBands(imgpath, bands):
    '''
    Helper for Sentinel-2 file structure + opening multiple band files for reading.
    '''
    bandRasts = []
    for band_id in bands:
        file = glob.glob(path.join(imgpath, 'GRANULE', '*', "IMG_DATA", '*B%02d.jp2' % band_id))[0]
        bandRasts.append(rasterio.open(file, 'r'))
    return(bandRasts)




