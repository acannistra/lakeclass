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
from imgproc import *
from lakedata import *

DAYS_DELTA = 5  # number of days to search sentinel on either side of date
PLATFORM = 'Sentinel-2'


def main():
    parser = argparse.ArgumentParser(
        description='selects sentinel satellite scenes for (date, geometry) pairs.')''
    parser.add_argument(
        'geodb', help='shapefile')
    parser.add_argument(
        '--day_delta', help='width of day search buffer', default=5)
    parser.add_argument('--date_col', help='column containing date')
    parser.add_argument('--bands', nargs='+', help='integer band ids')
    parser.add_argument('--out_dir')
    args = parser.parse_args()

    geodata = gpd.read_file(args['geodb'])

    date_col = args['date_col']
    out_dir = args['out_dir']
    day_delta = args['day_delta']
    bands = args['bands']

    errorfile = open(args[errorfile], 'w')

    for i, object in scum.iterrows():
        geo_envelope = object.geometry.envelope
        startdate = object[date_col] - timedelta(days=DAYS_DELTA)
        enddate = object[date_col] + timedelta(days=DAYS_DELTA)

        params = {
            'date': (startdate.strftime("%Y%m%d"), enddate.strftime("%Y%m%d")),
            'platformname': 'Sentinel-2'
        }

        # Query Database.
        try:
            products = downloader.searchOverlapping(geo_envelope, params)
        except Exception:
            continue
        print("Found %d images containing polygon %d" % (len(products), i))

        # --only consider images which fully contain geom
        products = products[products.contains(object.geometry)]
        print("   %d fully contain lake." % len(products))

        # Find nearest returned image by date +- DAYS_DELTA
        products = products.set_index('beginposition')
        products = products.sort_index()
        nearest = products.iloc[products.index.get_loc(
            object[date_col], method='nearest')]

        # save image metadata.
        nearest.to_csv(str(object.name) + '.imgmeta.csv')

        # Download image
        imgpath = downloader.downloadProduct(
            [nearest.uuid], "../datafiles/sentinel-2/")





if __name__ == "__main__":
    main()
