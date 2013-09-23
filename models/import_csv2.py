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
import __init__

from car import Car, Model


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
    makes = []
    for row in reader:
        if header:
            header = False
            continue
        make  = normalize( row['model_make_display'] )
        model = normalize( row['model_name']         )
        trim  = row['model_trim']
        year  = int( row['model_year'] )
        print '{}-{}:{}'.format(make,model,year)
        try:
            car = Car.objects.get( make_normal = make )
        except Car.DoesNotExist:
            car = Car(  make  = row['model_make_display'],
                        make_normal = normalize ( row['model_make_display'] )
                     )


        for new_model in car.models:
            if new_model.model_normal == model:
                append = False
                break
        else:
            append = True
            new_model = Model( model_normal = model,
                               model = row['model_name']  )

        if not trim in new_model.trims:
            new_model.trims.append(trim)

        if not year in new_model.years:
            new_model.years.append( year )

        if append:
            car.models.append(new_model)

        ok = car.save()
        if not ok:
            print "Car did not save"

if __name__ == '__main__':
    main()
