from datetime       import datetime

from models.car     import Car
from models.search  import Search, Found
from models.user    import User

from api            import *

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
                search.finds.append( result['id'] )
            except Exception, e:
                print str(e)

    search.save()
    return results


def check_date( search, heading = None, annotation = None ):
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
        elif 'year' in annotation:
            print annotation['year']
            if int(annotation['year']) in span:
                return True
            else:
                return False

    return True

def mark_deleted( id ):
    finds = Found.objects.filter( id_string = id )
    for find in finds:
        find.deleted = True
        find.save()
        

def search_threetaps( search ):
    """ Search Craigslist, Ebay classified, and  LIBRE with 3taps
    """
    ttap = ThreeTaps()
    retvals = 'source,category,category_group,location,external_id,external_url,heading,annotations,expires,deleted'

    if search.geo:
        location = { 'lat':search.geo[0], 'long':search.geo[1] }
        if search.distance:
            location['radius'] = '{}mi'.format(search.distance)
        else:
            location['radius'] = '50mi'

        ttap.set_location(**location)

    if search.model:
        annotations = '{make:"%s" AND model:"%s"}'%( search.make, search.model)
    else:
        annotations = '{make:"%s"}'%( search.make )

    kwargs = dict( source      = 'CRAIG|CARSD|EBAYM|HMNGS',
#                   status      = 'offered',
                   category    = 'VAUT',
                   annotations = annotations,
                   retvals     = retvals
                 )

    if search.price_min or search.price_max:
        if not search.price_max:
            price = '{}..'.format(search.price_min)
        else:
            price = '{}..{}'.format( search.price_min, search.price_max )
        kwargs.update( price = price )


    text = False
    for color in search.color:
        if not text:
            color_str = color
            text = True
        else:
            color_str += '|'+ color

    if text:
        kwargs['txt'] = color_str

    text = None
    for feature in search.features:
        if not text:
            text = feature
        else:
            text += '&{}'.format(feature)
    if text:
        kwargs['text'] = text

    # Do the search, keep processing as long as results available
    found_now = []
    while True:
        try:
            results = ttap.search( **kwargs )
        except Exception, e:
            print str(e)
            break

        for result in results['postings']:
            
            # Is the date in the heading what we want?
            if not check_date( search, heading = result['heading'] ):
                continue
            

            # Do I already have this?
            if result['external_id'] in search.finds:
                
                 # Has this been deleted?
                if result['deleted']:
                    mark_deleted( result['external_id'] )
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
                print str(e)

            search.finds.append( result['external_id'] )
            found_now.append( result['external_id'] )

        # Check if there are more pages or tiers
        if results['next_page'] > 0:
            kwargs['page'] = results['next_page']
        else:
            break
        """
        elif results['next_tier'] > 0:
            results = ttap.search( source='CRAIG',  annotations = annotations, tier = results['next_tier'] )
        """
    search.save()
    return found_now


def search_for( search ):
    """ Check all the api's for result 
    """
    
    results = search_threetaps( search )
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
        print str(e)

    return { 'searches':searches, 'display':display, 'finds':finds }
