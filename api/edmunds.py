#-------------------------------------------------------------------------------
# Name:        edmunds.py
# Purpose:     edmunds api
#
# Author:      Douma
#
# Created:     19/09/2013
# Copyright:   (c) Douma 2013
#-------------------------------------------------------------------------------
import requests
import urllib
import json

EDMUNDS = {
    'key'   :'8ww8y6my4p7msagvmgqhyttj',
    'secret':'Ksc6xvFrx8vE6cBJq6mPBBP5'
}

class Edmunds( object ):
    root_url = 'https://api.edmunds.com/api/vehicle/v2/{}?fmt=json&view=basic&state=used&api_key={}'

    def success(f):
        def wrapper(*args, **argv):
            ok, reply = f( *args, **argv )
            if not ok:
                raise Exception(reply)
            else:
                return reply

        return wrapper

    def __init__(self, key, secret ):
        self.key = key
        self.secret = secret


    def api( self, endpoint, **kwargs ):
        url = self.root_url.format(endpoint, self.key)
        response = requests.get( url )

        if response.ok:
            try:
                return True, json.loads(response.text)
            except ValueError:
                return False, "Bad JSON response"

        return False, response.text

    @success
    def makes(self):
        return self.api('makes')

    @success
    def models(self, make):
        return self.api("{}/models".format(make))
        return


if __name__ == '__main__':
    from models import Car

    ed = Edmunds( EDMUNDS['key'],EDMUNDS['secret'])
    makes = ed.makes()
    for make in makes:
        make = Car.objects.get( make = make['niceName'] )
        if not make:
            print "No make {} in db"



    pass
