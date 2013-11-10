import re
import string

from mongoengine            import *
from mongoengine.queryset   import QuerySet, queryset_manager
#from fuzzywuzzy             import process

def normalize(s):
    if not s:
        return ''
    
    for p in string.punctuation:
        s = s.replace(p, '')
        
    #s = s.replace(" ", "_")
    return s.lower().strip()


class CarManager(QuerySet):
    
    def models(self, make ):
        result = []
        car = self.get(make = make)
        for model in car.models:
            result.append( model.model)
        return result
    
    def trims(self, make, model):
        car = self.get( make = make )
        for c_model in car.models:
            if c_model.model == model:
                return c_model.trims
        return None

    def make_model(self, make, model ):
        car = self.get( make = make )
        for c_model in car.models:
            if c_model.model == model:
                return c_model
        return None
        


class Model( EmbeddedDocument ):
    model        = StringField()
    model_normal = StringField()
    trims        = ListField( StringField() )
    years        = ListField( IntField() )
    
    def __unicode__(self):
        return self.model


class Car ( Document ):
    make         = StringField()
    make_normal  = StringField( unique = True )
    models       = ListField( EmbeddedDocumentField( Model ) )
 
    def get_model(self, model ):
        """ Return the model record for the  
        """
        model = normalize( model )
        for find in self.models:
            if find.model_normal == model:
                return find
        return None
    
    meta = {'collection'       :'car',
            'allow_inheritance': False,
            'indexes'          : ['make_normal'],
            'queryset_class'   : CarManager
           }
    
    def __unicode__(self):
        return self.make


"""
class Car( Document ):

    id_number      = IntField()
    make           = StringField()
    model          = StringField()
    trim           = StringField()
    year           = IntField()
    make_normal    = StringField()
    model_normal   = StringField()
    trim_normal    = StringField()

    meta = {'collection'       :'cars',
            'allow_inheritance': False,
            'indexes'          : ['make_normal', 'model_normal'],
            'queryset_class'   : CarManager
           }


    def __unicode__(self):
        return str(self.year) +' '+ self.make +' ' + self.model
"""