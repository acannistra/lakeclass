'''

sentinel-extract.py

selects sentinel satellite scenes for (date, geometry) pairs. 

Takes as input a geospatial shapefile

And some column names. It must contain a 'date' column or some kind
and a 'geometry' column of some kind. 

output filename column is also given, describing the column name to use when 
assigning filenames. 



'''

import argparse
import pandas as pd
import geopandas as gpd
from datetime import timedelta
from imgproc import downloader, processor
from tempfile import mkdtemp
from shutil import rmtree
from os import remove

DAYS_DELTA = 5  # number of days to search sentinel on either side of date
PLATFORM = 'Sentinel-2'

def clearDir(path):
    import os, shutil
    for f in os.listdir(folder):
        file_path = os.path.join(folder, f)
        try:
            if os.path.isfile(f):
                os.unlink(f)
            elif os.path.isdir(f): shutil.rmtree(f)
        except Exception as e:
            print("error clearing directory")
            raise

def main():
    parser = argparse.ArgumentParser(
        description='selects sentinel satellite scenes for (date, geometry) pairs.')
    parser.add_argument(
        'geodb', help='shapefile')
    parser.add_argument(
        '--day_delta', help='width of day search buffer', default=5, type=int)
    parser.add_argument('--date_col', help='column containing date')
    parser.add_argument('--bands', nargs='+', help='integer band ids', type=int)
    parser.add_argument('--smalldownload', action='store_true', help='limits each download < 1GB')
    parser.add_argument('--errorfile', help='errorfile')
    parser.add_argument('--out_dir')
    args = parser.parse_args()

    ### Setup environment.
    geodata = gpd.read_file(args.geodb)
    image_dir = mkdtemp(prefix='sentinel-2_')
    # convert to datetime
    date_col = args.date_col
    geodata[date_col] = pd.to_datetime(geodata[date_col])
    out_dir = args.out_dir
    # remove trailing slash
    if out_dir[-1] == '/': out_dir = out_dir[:-1]
    day_delta = args.day_delta
    band_ids = args.bands

    try: 
        errorfile = open(args.errorfile, 'w')
    except: 
        errorfile = None
        print("NO error logging!")

    for obj_idx, object in geodata.iterrows():
        try: 
            geo_envelope = object.geometry.envelope
            startdate = object[date_col] - timedelta(days=DAYS_DELTA)
            enddate = object[date_col] + timedelta(days=DAYS_DELTA)

            params = {
                'date': (startdate.strftime("%Y%m%d"), enddate.strftime("%Y%m%d")),
                'platformname': 'Sentinel-2'
            }

            # Query Database.
            products = downloader.searchOverlapping(geo_envelope, params)
            if(products is None):
                print("ERROR: No results on object %s" % object.name)
                continue 

            print("Found %d images containing polygon %d" % (len(products), obj_idx))

            # --only consider images which fully contain geom
            products = products[products.contains(object.geometry)]


            print("   %d fully contain lake." % len(products))

            # optionally only consider small image downloads:
            if args.smalldownload:
                products = products[products['size'].str.contains("GB") == False]
                if(len(products) == 0):
                    print("ERROR: No small images to download")
                    continue

            # Find nearest returned image by date +- DAYS_DELTA
            products = products.set_index('beginposition')
            products = products.sort_index()
            nearest = products.iloc[products.index.get_loc(
                object[date_col], method='nearest')]

            # save image metadata by index
            nearest.to_csv("%s/%s.imgmeta.csv" % (out_dir, str(object.name)))

            # Download image
            print('Downloading product %s' % nearest.uuid)
            imgpath = downloader.downloadProductAWS(nearest.title, image_dir, band_ids)


            # Open Bands
            theseBands = processor.openSentinelBands(imgpath, band_ids)

            # Extract geoms from bands
            src_epsg = geodata.crs['init'].split(":")[1] # { 'init' : 'epsg:9999' } 
            for idx, band in enumerate(band_ids):
                geom_band_outfile_str = "%s/%d_%s.tif" % (out_dir, object.name, band) 
                print(geom_band_outfile_str)
                processor.extractGeomToFile(object.geometry, theseBands[idx], src_epsg, geom_band_outfile_str)

            # Delete files
            cleardir(imgpath)
            print("Object %d complete!" % obj_idx)
        except Exception as e:
            print("ERROR: exception. \n%s" % str(e))
            if errorfile is not None:
                errorfile.write("%s: %s" % (object.name, str(e)))
       

    # Remove img tempdir
    rmtree(image_dir)

if __name__ == "__main__":
    main()
