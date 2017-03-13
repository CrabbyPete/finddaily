
from datetime 					import datetime
from mongoengine 				import *
from user                       import User
from geo                        import geocode    

class Found( Document ):
    id_string       = StringField()
    heading         = StringField()
    search          = ReferenceField( 'Search' )
    url             = URLField()
    found_by        = StringField()
    found_on        = DateTimeField( default = datetime.now() )
    rating          = IntField( default = 1 )
    good            = BooleanField( default = True  )
    trash           = BooleanField( default = False )
    notes           = StringField( default = "" )
    views           = IntField( default = 0)
    expires         = DateTimeField()

    @queryset_manager
    def ordered(doc_cls, queryset, search):
        if search.sort == 'date':
            search.finds = queryset.filter( search = search ).order_by( '-found_on')
        else:
            search.finds = queryset.filter( search = search ).order_by( '-rating' )
        search.save()
        return search.finds
    
    @queryset_manager
    def related(doc_cls, queryset, search):
         results = queryset.filter( search = search ).only( 'id_string' )
         data = [ result.id_string for result in results ]
         return data
    

    def __unicode__(self):
        return '<Found:{}>'.format(self.heading)

    meta = { 'indexes'  : ['search', 'id_string']
           }

 

class Search( Document ):
    """ Describes what someone is looking for
    """
    user            = ReferenceField( User, reverse_delete_rule = CASCADE )
    name            = StringField()         # Save search as ..
    search          = StringField()         # Original search string
    make            = StringField()
    model           = StringField()
    bodystyle       = StringField()
    condition       = StringField()
    year_from       = IntField()
    year_to         = IntField()
    price_min       = DecimalField()
    price_max       = DecimalField()
    mileage_min     = IntField()
    mileage_max     = IntField()
    zip             = StringField()
    distance        = IntField()
    city            = StringField()
    state           = StringField()
    country         = StringField()
    color           = ListField( StringField() )
    trim            = StringField()
    geo             = GeoPointField()
    features        = ListField( StringField() )
    created         = DateTimeField( default = datetime.now() )
    sort            = StringField( default = 'date' )
    anchor          = StringField()
    finds           = ListField( ReferenceField(Found,reverse_delete_rule = PULL)  )

    
    @queryset_manager
    def related(doc_cls, queryset, user):
        """ Get all searchs for a user 
        """
        data = queryset.filter( user = user )
        return data
    
    
    def has_find( self, id ):
        """ Look for a find by its id_string
        """
        try:
            found = Found.objects.get(search = self, id_string = id )
        except DoesNotExist:
            return None
        return found
    
    def get_finds(self, page = 0, page_size = 100 ):
        if not page_size:
            page_size = len(self.finds)
            
        range = page * page_size
        return self.finds[ range:range + page_size ] 

            
    def sort_finds(self, method = None ):
        """ Sort the find by method ratings or date found
        """
        if not method:
            method = self.sort

        if method == 'rating':
            finds = Found.objects.filter(search = self.pk).order_by('-rating')
            self.sort = 'rating'
        else:
            finds = Found.objects.filter(search = self.pk).order_by('-found_on')
            self.sort = 'date'

        # This causes the finds to be DeReferenced 
        self.finds = [ find for find in finds ]
        return self.finds

    @property
    def latitude(self):
        return self.geo[0]

    @property
    def longitude(self):
        return self.geo[1]

    def set_location(self, zip, miles = None ):
        self.zip = zip
        if miles:
            if miles == 'unlimited':
                del self.geo
                self.save()
                return None
            else:
                self.distance = miles
        
        try:
            location = geocode( zip )
            self.geo = [ float(location['lat']), float(location['lng']) ]
        except Exception, e:
            return None
    
        self.save()
        return self.geo

    def delete_finds(self, keep_notes = False ):
        for find in self.finds:
            if keep_notes and len( find.notes ) > 0:
                continue
            find.delete()
            
    def save(self, *args, **kwargs):
        self.sort_finds()
        super(Search, self).save( *args, **kwargs )
    
    def delete(self, *args, **kwargs ):
        """ delete all the finds associated with this search first
        """
        for find in self.finds:
            find.delete()
        
        return super(Search, self).delete( *args, **kwargs )
            
    meta = { 'indexes' : ['make', 'model','user'] }

    def __unicode__(self):
        return '<Search:{}>'.format(self.search)

