#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Douma
#
# Created:     26/11/2012
# Copyright:   (c) Douma 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import requests
import urllib
import json

from collections    import OrderedDict

SEARCH_TERMS = [
    'category_group',
    'category',
    'country',
    'state',
    'metro',
    'region',
    'county',
    'city',
    'locality',
    'zipcode',
    'radius',
    'lat',
    'long',
    'source',
    'external_id',
    'heading',
    'body',
    'text',
    'timestamp',
    'id',
    'price',
    'currency',
    'annotations',
    'status',
    'has_image',
    'include_deleted',
    'only_deleted'
]



class ThreeTaps(object):

    search_url     = 'http://search.3taps.com'
    reference_url  = 'http://reference.3taps.com'
    polling_url    = 'http://polling.3taps.com'

    def success(f):
        def wrapper(*args, **argv):
            ok, reply = f( *args, **argv )
            if not ok:
                raise Exception(reply)
            else:
                return reply

        return wrapper

    def __init__(self, token=None):
        """ Intialize
        """
        if not token:
            self.auth_token='8e3279f1eb704df797a7be534abb6c49'
        else:
            self.auth_token = token

    def api( self, method, url, **kwargs ):
        """ Api interface
            method POST or GET
            argc the function to call
            **kwargs parameters for a POST
        """
        if not 'rpp' in kwargs:
            kwargs['rpp']=100

        # Encode parameters
        url += '?auth_token={}'.format(self.auth_token)
        url += '&' + urllib.urlencode(kwargs)

        if method == 'POST':
            response = requests.post( url, data = data )
        elif method == 'GET':
            response = requests.get( url )

        if response.ok:
            try:
                return True, json.loads(response.text)
            except ValueError:
                return False, "Bad JSON response"

        return False, response.text

    @success
    def search( self, **kwargs ):
        """ Search for stuff
        """
        args = OrderedDict()
        try:
            args.update(self.location)
        except AttributeError:
            pass
        
        # Make sure it stays ordered
        for k,v in kwargs.items():
            args[k] = v
            

        return self.api( 'GET',self.search_url, **args )


    @success
    def get_sources( self ):
        return self.api('GET', self.reference_url+'/sources' )


    @success
    def get_locations( self, level ):
        """ Get valid locations from 3taps
        """
        if level in [ 'country', 'state','metro', 'region',
                      'county', 'city', 'locality', 'zipcode']:

            kwargs = {'level':level}
            return self.api( 'GET',
                              self.reference_url+'/locations',
                              **kwargs
                           )

    @success
    def location_lookup( self, code ):
        """ Look up a location and return details
        """
        kwargs = {'code':code}
        return self.api( 'GET',
                          self.reference_url+'/locations/lookup',
                          **kwargs
                       )

    def set_location( self, **location ):
        """ Set location
            location = dict() values =
        """
        if 'lat' in location and 'long' in location and 'radius' in location:
            self.location = OrderedDict( [('lat'   ,location['lat']),
                                          ('long'  ,location['long']),
                                          ('radius', location['radius'])]
                                        )
        else:
            self.location = None


    @success
    def get_category_groups( self ):
        """ Get category groups
        """
        return self.api( 'GET', self.reference_url+'/category_groups' )

    def set_category_group( self, group ):
        self.category_group = group


    @success
    def get_categories(self, value = None):
        """ Get specific categories
        """
        return self.api( 'GET', self.reference_url+'/categories' )

    def set_category( self, category ):
        self.category = category


def main():
    ttap = ThreeTaps()

    sources = ttap.get_sources()

    locations = ttap.get_locations('country')
    for local in locations['locations']:
       # print local
       pass

    groups = ttap.get_category_groups()

    categories = ttap.get_categories()

    result = ttap.search( source ='CRAIG',
                          state  = "USA-NJ",
                          category = 'VAUT',
                          annotations = {'make':'toyota','model':'tacoma'} )

    result = ttap.search(source='CRAIG',heading='Toyota',zipcode="07481")
    result = ttap.search(source='CRAIG',text="2001 Toyota Tacoma",state="USA-NJ")
    result = ttap.search(source='CRAIG',text='ferrari')
    result = ttap.search(source='BKPGE',)
    pass

if __name__ == '__main__':
    main()
