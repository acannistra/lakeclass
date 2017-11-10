'''

sentinel-extract.py

selects sentinel satellite scenes for (date, geometry) pairs. 

Takes as input two files: metadata and geodb


'''

import argparse
import pandas as pd
from imgproc import *
from lakedata import *


def main():
    parser = argparse.ArgumentParser(
        description='selects sentinel satellite scenes for (date, geometry) pairs.')
    parser.add_argument(
        'metadata', help='csv must contain \'date\' and \'geoid\'columns')
    parser.add_argument(
        'geodb', help='shapefile, must contain \'geoid\' polygon identifier.')
    args = parser.parse_args()

    metadata = pd.read_csv(args['metadata'])
    #assert('contains' is in metadata.columns)
    geodata  = gpd.read_file(args['geodb'])

    



if __name__ == "__main__":
    main()
