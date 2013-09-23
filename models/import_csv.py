#-------------------------------------------------------------------------------
# Name:        cars_json.py
# Purpose:     Take the csv and parse to a mongo json
#
# Author:      Peter
#
# Created:     17/08/2013
# Copyright:   (c) Peter 2013
#-------------------------------------------------------------------------------
import csv
import json
import string



from car import Car

from config.py   import MONGODB
from mongoengine import *
connect(MONGODB['db'], **MONGODB['options'] )


def normalize(s):
    for p in string.punctuation:
        s = s.replace(p, '')

    return s.lower().strip()

def main():

    # Open the CSV
    f = open( 'cars.csv', 'rU' )

    # Change each fieldname to the appropriate field name. I know, so difficult.
    reader = csv.DictReader( f, fieldnames = ( "model_id",
                                               "model_make_id",
                                               "model_name",
                                               "model_trim",
                                               "model_year",
                                               "model_make_display"
                                             )
                           )

    # Parse the CSV into JSON
    header = True
    for row in reader:
        if header:
            header = False
            continue

        car = Car(
                    id_number      = int( row["model_id"] ),
                    make           = row['model_make_display'],
                    model          = row['model_name'],
                    trim           = row['model_trim'],
                    year           = int( row['model_year'] ),
                    make_normal    = normalize ( row['model_make_display'] ),
                    model_normal   = normalize ( row['model_name'] ),
                    trim_normal    = normalize ( row['model_trim'] ),
                )

        car.save()


if __name__ == '__main__':
    main()
