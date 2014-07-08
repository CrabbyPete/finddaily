#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:     Create a csv from Edmonds
#
# Author:      Douma
#
# Created:     04/05/2014
# Copyright:   (c) Douma 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import csv

from api.edmunds    import Edmunds
from models.car     import Car, Model, normalize
from config         import EDMUNDS


def main():
    # Open the CSV
    f = open( 'edmonunds.csv', 'wb' )

    # Change each fieldname to the appropriate field name. I know, so difficult.
    writer = csv.DictWriter( f, fieldnames = ( "model_id",
                                               "model_make_id",
                                               "model_name",
                                               "model_trim",
                                               "model_year",
                                               "model_make_display"
                                             )
                           )
    row = { "model_id":001,
            "model_make_id":None,
            "model_name":None,
            "model_trim":'',
            "model_year":None,
            "model_make_display":None
    }

    ed = Edmunds( EDMUNDS['key'],EDMUNDS['secret'])
    makes = ed.makes()
    for make in makes['makes']:
        make_normal = normalize( make['name'] )
        row['model_make_id'] = make_normal
        row['model_make_display'] = make['name']
        for model in make['models']:
            row['model_name'] = model['name']
            for year in model['years']:
                row['model_year'] = year['year']
                writer.writerow( row )



if __name__ == '__main__':
    main()
