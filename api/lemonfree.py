import requests
import urllib
import json

BODYSTYLE = (
                'SUV',
                'Sedan',
                'Coupe',
                'Truck',
                'Minivan',
                'Wagon',
                'Convertible',
                'Hatchback',
                'Van',
                'Hybrid'
            )

CONDITION = ( 'new', 'used')

PARAMETERS = (
              'format',
              'make',
              'model',
              'trim',
              'bodystyle',
              'zip',
              'distance',
              'city',
              'state',
              'country',
              'price_min',
              'price_max',
              'mileage_min',
              'mileage_max',
              'year_from',
              'year_to',
              'condition',
              'state',
              'sort_by',
              'sort_dir',
              'page',
              'per_page'
            )

class LemonFree(object):
    url =  'http://api.lemonfree.com/'

    def __init__(self, key = None):
        if key:
            self.apikey = key
        else:
            self.apikey = 'd6933e825968090972356dd793a62b7c'

    def api(self, url, **kwargs):
        url = self.url + url

        kwargs['key'] = self.apikey
        kwargs['format'] = 'json'
        params = urllib.urlencode(kwargs)

        response = requests.get(url, params = params)
        try:
            return json.loads( response.text )
        except:
            return response.text

    def makes(self):
        """ Return all makes
        """
        return self.api('makes')

    def models(self, make):
        """ Return all models
        """
        return self.api('models', make = make)

    def trims( self, make, model, year = None ):
        """ Return the trims for make and model. Year is optional
        """
        kwargs = dict( make = make, model = model )
        if year:
            kwargs['year'] = year
        return  self.api('trims', **kwargs )

    def years( self, make, model, trim = None):
        kwargs = dict( make = make, model = model )
        if trim:
            kwargs['trim'] = year
        return  self.api('years', **kwargs )

    def prices( self, make, model, years = None, trim = None):
        kwargs = dict( make = make, model = model )
        if trim:
            kwargs['trim'] = year
        if years:
            kwargs['year_from'] = years[0]
            if len( years ) < 2:
                kwargs['year_to'] = years[0]
            kwargs['year_to'] = years[1]
        return  self.api('prices', **kwargs )


    def search(self,**kwargs):
        kwargs['page'] = 1
        while ( True ):
            reply = self.api('listings',**kwargs )
            if not reply or len( reply['response']['result'] ) == 0:
                return
            kwargs['page'] += 1
            for result in reply['response']['result']:
                yield result


    def listings( self, make, model,
                        years = None,
                        condition = None,
                        price_range = None,
                        milage = None,
                        zip = None,
                        distance = None
                  ):
        kwargs = dict( make = make, model = model )
        if zip:
            kwargs['zip'] = zip

        if years:
            kwargs['year_from'] = years[0]
            kwargs['year_to']   = years[1]

        kwargs['page'] = 1
        while ( True ):
            reply = self.api('listings',**kwargs )
            if not reply:
                break

            yield reply
            kwargs['page'] += 1

    @property
    def parameters(self):
        return PARAMETERS

if __name__ == '__main__':
    import pprint
    pretty = pprint.PrettyPrinter(indent=2)
    lemonfree = LemonFree('d6933e825968090972356dd793a62b7c')

    """
    reply = lemonfree.makes()
    pretty.pprint(reply)
    """
    """
    reply = lemonfree.models(make='Toyota')
    pretty.pprint(reply)
    """
    """
    reply = lemonfree.trims( make = "Toyota", model='Tacoma' )
    pretty.pprint(reply)
    """
    """
    reply = lemonfree.prices("Toyota","Tacoma",['2000','2003'])
    pretty.pprint(reply)
    """
    listings = lemonfree.listings("Toyota","Tacoma",['2000','2000'],zip='07481')
    for listing in listings:
        print listing

    pass
