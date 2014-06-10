#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Douma
#
# Created:     04/05/2014
# Copyright:   (c) Douma 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from api.edmunds    import Edmunds
from models.car     import Car, Model, normalize


def add_make():
    pass

def add_model( make, model ):
    years = set( model.years)
    trims = set( model.trims )

    for year in model['years']:
        years |= set( [year['year']] )
    for trim in year['styles']:
        trims |= set( [ trim['name'] ] )

    model.years = years
    model.trims = list( trims )

    make.models.append( model )

def main():
    ed = Edmunds( EDMUNDS['key'],EDMUNDS['secret'])
    makes = ed.makes()
    for make in makes['makes']:
        make_normal = normalize( make['name'] )
        try:
            my_make = Car.objects.get( make_normal = make_normal)
        except Car.DoesNotExist:
            my_make = Car( make_normal = make_normal, make = make['name'] )

        models = ed.models( make['niceName'] )
        for model in models['models']:
            model_name = normalize( model['name'] )
            if not my_make.get_model(model_name):
                my_model = Model( name = model['name'],
                                  model_normal = model_name)


                my_make.models.append( my_model )
        result = my_make.save()

if __name__ == '__main__':
    main()
