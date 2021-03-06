from datetime       import datetime
from decimal        import Decimal

from nltk           import word_tokenize, pos_tag, ne_chunk
from nltk.tokenize  import RegexpTokenizer
#from nltk.tag.simplify  import simplify_wsj_tag

from geo            import geocode, reverse_geocode, walk

from models.car     import Car, normalize
from models.search  import Search, Found
from models.user    import User
from log            import log


SPECIALS  = {'P':('under', 'over', 'less', 'more','about','around','near', 'for', 'between','from','within', 'in', 'to', '-'),
             'N':('dollars','miles','anywhere')
            }

COLORS     = ('white','silver','black','gray','red','natural','brown','blue','green','pink','gold')
CONDITION  = ('new','used')
BODYSTYLE  = ('suv','sedan','coupe','truck','minivan','wagon','convertible','hatchback','van','hybrid')

MAKESLANG = dict( chevy = 'Chevrolet',  vw   = 'Volkswagen' )



class Parse(object):
    search = {}
    
    def __init__(self, lati=None, longi=None, user = None ):
        self.search['search'] = data
        self.search['distance'] = 50

        if lati and longi:
            self.search.geo = [float(lati),float(longi)]
            try:
                address,zipcode = reverse_geocode(lati,longi)
            except Exception, e:
                log(  "Geosearch error {}".format( str(e) ) )
            else:
                search.zip = zipcode

        elif user and not user.is_anonymous:
            try:
                if user.location:
                    search['geo'] = user.location
                elif user.address:
                    location = geocode( user.address )
                    search.geo = [float(location['lat']), float(location['lng'])]
            except Exception, e:
                log ( 'User geo error {}'.format( str(e) ) )
            
    
    @property
    def latitude(self):
        return self.search.geo[0]
    
    @property
    def longitude(self):
        return self.search.geo[1]
    
        
    def find_make( self ):
        """ Find the car make, if any
        """
        pass

    def find_model( self ):
        """ Find the car model, and make if None
        """
        pass

    def find_dollars( words ):
        """ Find dollar ranges and numbers
        """
        pass

    def find_miles( words):
        """ Find milages
        """
        pass

    def parse(self, query ):
        tokenizer = RegexpTokenizer('\w+|\$[\d\.]+|\S+')
        self.words  = tokenizer.tokenize(query)
        
        last_number      = None
        preceeding_word  = None
        preposition      = None
        year = datetime.today().year + 1
        
        for w, word in enumerate(words):
            pass


def get_properties( query ):
    tokenizer = RegexpTokenizer('\w+|\$[\d\.]+|\S+')
    query = query.replace('-', '- ')
    words  = tokenizer.tokenize(query)
    return words

def parse_query( data, lati=None, longi=None, user=None ):
    """ parse the data string and figure out what is wanted
        data - user string query
    """
    # Create a search record
    search = Search()
    search.search = data

    search.distance = 50
    if lati and longi:
        search.geo = [float(lati),float(longi)]
        try:
            address,zipcode = reverse_geocode(lati,longi)
        except Exception, e:
            log(  "Geosearch error {}".format( str(e) ) )
        else:
            search.zip = zipcode
    elif user:
        if not user.is_anonymous():
            try:
                if user.location:
                    search.geo = user.location
                elif user.address:
                    location = geocode( user.address )
                    search.geo = [float(location['lat']), float(location['lng'])]
            except Exception, e:
                log ( 'User geo error {}'.format( str(e) ) )

    # Break up the request
    #data = data.replace('-',' - ')
    words  = word_tokenize(data)
    get_properties( data )
    #tags   = pos_tag(words)
    #chunks = ne_chunk(tags)

    dollars          = False
    last_number      = None
    preceeding_word  = None
    preposition      = None

    year = datetime.today().year + 1
    for w, word in enumerate(words):

        # Simplify the tags
        #pos  = simplify_wsj_tag(tag)

        # Is this a dollar figure
        if word == '$':
            dollars = True
            continue
        
        # Normalize everything
        word = normalize( word, ignore = ['.'] )

        # Check floating numbers first        
        if '.' in word:
            last_number = float( word )
            word = 'dollars' 
            dollars = False
                    
        if word.isdigit():
            if int(word) >= 1914 and int(word) <= year and not search.make:
                if preceeding_word in ['to', '-']:
                    search.year_to = int(word)

                elif not preceeding_word and not search.year_from:
                    search.year_from = int(word)
                    search.year_to = int(word)
                    continue

            last_number = word
            if dollars:
                word = 'dollars'
                dollars = False

        if word == 'dollars':
            if preposition == 'under':
                search.price_max = Decimal(last_number)
                search.price_min = Decimal(0)
            elif preposition == 'over':
                search.price_min = Decimal(last_number)
            elif not preposition or preposition in ['about', 'around', 'near']:
                search.price_max = Decimal(last_number + 2000)
                search.price_min = Decimal(last_number - 1000)
            preceeding_word = word
            continue

        if word == 'miles':
            if preposition == 'under':
                search.mileage_max = last_number
            elif preposition == 'over':
                search.mileage_min = last_number
            elif not preposition or preposition in ['about', 'around', 'near']:
                pass
            elif preposition in ['within','in']:
                search.distance = last_number
            continue

        if word == 'anywhere':
            search.geo = None
            continue

        # Handle adjective
        if word in COLORS:
            search.color.append( word )
            continue

        if word in CONDITION:
            search.condition = word

        if word in BODYSTYLE:
            search.bodystyle = word

        if word in SPECIALS['P']:
            preposition = word

        preceeding_word = word

        if word in MAKESLANG:
            word = MAKESLANG[ word ]


        cars = Car.objects( make_normal__startswith = word )
        for car in cars:
            if car.make_normal == word:
                search.make = car.make
            elif car.make_normal.startswith( word ):
                make = word + ' ' + words[w+1]
                if car.make_normal == make:
                    search.make = car.make

        cars = Car.objects( models__model_normal__startswith = word )
        if len( cars ) == 1:
            if not search.make:
                search.make = cars[0].make

            if search.make == cars[0].make:
                model = cars[0].get_model( word )
                if model:
                    search.model = model.model

        elif len( cars ) > 1 and search.make:
            for car in cars:
                if car.make == search.make:
                    model = car.get_model(word)
                    if model:
                        search.model = model.model
                    break

    # Done analyzing now save this for the user
    search.name = normalize(search.make)
    if search.model:
        search.name += '-'+ normalize(search.model)

    if user and not user.is_anonymous():
        search.user = User.objects.get( pk = user.pk )
        searches = Search.objects.filter( user = user.pk ).count()
    else:
        search.user = None

    try:
        search.save()
    except Exception, e:
        log ("Search Save Exception: {}".format( str(e)) )

    #print '{}-{}'.format( search.make, search.model)
    return search

if __name__ == '__main__':
    #s = parse_query( '2001 toyota tacoma')
    #s = parse_query( '2000-2001 chevy camaro')
    #s = parse_query('2000 - 2001 subaru')
    s = parse_query('toyota rav4 $8000.00-$10000')
    pass
