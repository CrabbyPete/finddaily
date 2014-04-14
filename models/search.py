
from datetime 					import datetime
from mongoengine 				import *
from user                       import User
    
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
    finds           = ListField()

    
    @queryset_manager
    def related(doc_cls, queryset, user):
        """ Get all searchs for a user 
        """
        data = queryset.filter( user = user )
        return data
    
    def sort_finds(self, method = None ):
        """ Sort the find by method ratings or date found
        """
        if not method:
            return self

        if method == 'rating':
            finds = Found.objects.filter(search = self.pk).order_by('-rating')
            self.sort = 'rating'
        else:
            finds = Found.objects.filter(search = self.pk).order_by('-found_on')
            self.sort = 'date'

        self.finds = [ find.id_string for find in finds ]
        self.save()
        return self
    
    meta = { 'indexes' : ['make', 'model','user'] }

    def unicode(self):
        return self.search


class Found( Document ):
    id_string       = StringField()
    heading         = StringField()
    search          = ReferenceField( Search , reverse_delete_rule = CASCADE)
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
    
    def save(self):
        return super(Found, self).save()
    
    meta = { 'indexes'  : ['search', 'id_string']
           }
