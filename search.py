import time
from datetime       import datetime


from models.car     import Car
from models.search  import Search, Found
from models.user    import User
from log            import log

from api            import *

class Timer:    
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start
        
def search_lemonfree( search ):
    """
    Search the LemonFree database
    """
    lemonfree = LemonFree()
    kwargs = dict( make = search.make, model = search.model )
    for parameter in lemonfree.parameters:
        if parameter in search:
            kwargs[parameter] = search[parameter]
    kwargs['per_page'] = 100

    results = lemonfree.search(**kwargs)
    for result in results:
        if 'link' in result:
            url = result['link']
        elif 'sourceUrl' in result:
            url = result['sourceUrl']
        if not result['id'] in search.finds:
            found = Found( search     = search,
                           id_string  = result['id'],
                           url        = url,
                           found_by   = 'lemonfree',
                           heading    = result['title']
                         )

            try:
                found.save()
                search.add_find( found )
            except Exception, e:
                print str(e)

    search.save()
    return results


 
class SearchThreeTaps():
    """ Search 3Taps
    """
    
    def __init__(self):
        self.ttap = ThreeTaps()
    
    
    def set_location(self, search ):
        """ Set the search location 
        """
        location = {}
        if search.geo:
            location = { 'lat':search.geo[0], 'long':search.geo[1] }
        
            if search.distance:
                location['radius'] = '{}mi'.format(search.distance)
            else:
                location['radius'] = '50mi'

        self.ttap.set_location(**location)

    
    def start_search(self, search ):
        """ Search Craigslist, Ebay classified, and  LIBRE with 3taps
        """
        retvals = 'source,category,category_group,location,external_id,external_url,heading,body,annotations,expires,deleted'

 
        self.set_location(search)
        if search.model:
            annotations = '{make:"%s" AND model:"%s"}'%( search.make, search.model)
        else:
            annotations = '{make:"%s"}'%( search.make )

        kwargs = dict( source      = 'CRAIG|CARSD|EBAYM|HMNGS',
                       category    = 'VAUT',
                       annotations = annotations,
                       retvals     = retvals
                     )

        # Set the price
        if search.price_min or search.price_max:
            if not search.price_max:
                price = '{}..'.format(search.price_min)
            else:
                price = '{}..{}'.format( search.price_min, search.price_max )
            kwargs.update( price = price )


        # Check for the color in text
        text = False
        for color in search.color:
            if not text:
                color_str = color
                text = True
            else:
                color_str += '|'+ color

        if text:
            kwargs['text'] = color_str

        # Check any specific features 
        text = None
        for feature in search.features:
            if not text:
                text = feature
            else:
                text += '&{}'.format(feature)
        if text:
            kwargs['text'] = text

        return self.process_search( search, **kwargs )
    
    def process_search(self, search, **kwargs):
        """ Do the search, keep processing as long as results available
        """
        found_now = []
        count = 0 
        while True:
            if count >= 300:
                break
            
            with Timer() as t:
                results = self.ttap.search( **kwargs )
            
            #print('Request took %.03f sec.' % t.interval)
    
            if not results or not 'postings' in results:
                break

            for result in results['postings']:
            
                # Is the date in the heading what we want?
                if not self.check_date( search, result['heading'] ):
                    continue
            
                annotations = result['annotations']
                if 'make' in annotations and not annotations['make'] == search['make']:
                    print 'Wrong make {}'.format(annotations['make'])
                
                count += 1
                # Do I already have this?
                found = search.has_find( result['external_id'] )
                if found:
                
                    # Has this been deleted?
                    if result['deleted']:
                        found.deleted = True
                        found.save()       
                    continue
            
                elif result['deleted']:
                    continue

                found = Found( search     = search,
                               id_string  = result['external_id'],
                               url        = result['external_url'],
                               found_by   = 'craigslist',
                               found_on   = datetime.today(),
                               heading    = result['heading'],
                               expires    = datetime.fromtimestamp( result['expires'] ) 
                            )

                try:
                    found.save()
                except Exception, e:
                    log( line(), str(e) )

                search.finds.append(found)
                found_now.append( found )

            # Check if there are more pages or tiers
            if results['next_page'] > 0:
                kwargs['page'] = results['next_page']
            else:
                break

        search.save()
        return found_now
    
    def check_date( self, search, heading = None, annotation = None ):
        """ Check if date is within search parameters by date in title heading 
        """
    
        if search.year_from:
            span  = range( search.year_from, search.year_to + 1 )
            if heading:
                words = heading.split(' ')

                for word in words:
                    if word.isdigit() and int(word) >= 1914:
                        if int(word) in span:
                            return True
                else:
                    return False
            
            elif annotation and 'year' in annotation:
                if int(annotation['year']) in span:
                    return True
                else:
                    return False

        return True


def search_for( search ):
    """ Check all the api's for result 
    """
    api = SearchThreeTaps()
    results = api.start_search( search )
    #results = search_threetaps( search )
    #search_lemonfree( search )
    return results


def get_searches( user, search ):
    """ Get all the searches for this user
        display = get the finds for this search
    """

    if not search and not user.is_anonymous():
        searches = Search.objects.filter( user = user.pk )
        if searches.count() >= 1:
            display = searches[0]
        else:
            return None
    else:
        display = Search.objects.get( pk = search )
        if not user.is_anonymous():
            searches = Search.objects.filter( user = user.pk )
        else:
            searches = [ display ]

    try:
        finds = Found.ordered( search = display )
    except Exception, e:
        log( 'Exception Found Save: {}'.format( str(e) ) )

    return { 'searches':searches, 'display':display, 'finds':finds }
