import re, hashlib
import mongoengine

from datetime 					import datetime

from mongoengine 				import *
from mongoengine.queryset       import Q


class PhoneField(StringField):          # Validate phone numbers

    PHONE_REGEX = re.compile(r'1?\W*([2-9][0-8][0-9])\W*([2-9][0-9]{2})\W*([0-9]{4})(\se?x?t?(\d*))?')

    def validate(self, value):
        if not value == '':
            if not PhoneField.PHONE_REGEX.match(value):
                raise ValidationError('Invalid Phone number: %s' % value)


# User Profile, also used for those not signed in
class User( Document ):
    username      = StringField( required = True )
    email 		  = EmailField( required = True )
    password	  = StringField(required = True )
    first_name	  = StringField()
    last_name	  = StringField()
    phone         = PhoneField( default = None, required = False)
    address       = StringField(default = None)
    location	  = GeoPointField()
    joined        = DateTimeField( default = datetime.now() )

    # Local booleans
    subscribe     = BooleanField( default = True  )

    # Login booleans
    active        = BooleanField( default = True  )
    authenticated = BooleanField( default = False )

    meta = {'indexes': ['email','username'] }

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return str( self.pk )

    def set_password(self, raw_password):
        hash = hashlib.md5()
        hash.update(raw_password)
        self.password = hash.hexdigest()

    def check_password(self, raw_password):
        hash = hashlib.md5()
        hash.update(raw_password)
        if self.password == hash.hexdigest():
            return True

        return False

    meta = { 'indexes' : ['username', 'email']
           }

    def __unicode__(self):
        if self.last_name and self.first_name:
            return self.last_name + ','+self.first_name
        return self.email
		

class Payment( EmbeddedDocument ):
    id             = StringField()   # Unique string used to identify this payment
    payer_id       = StringField()   
    payment_id     = StringField()
    paid           = DateTimeField()
    amount         = DecimalField()
    months         = IntField( required = True )
    method         = StringField()

    
class Subscription( Document ):
    user     = ReferenceField( 'User', reverse_delete_rule = CASCADE )
    expires  = DateTimeField( default = datetime.now() )
    active   = BooleanField(default = False)
    
    payments   = ListField( EmbeddedDocumentField( Payment ) )

    meta = { 'indexes' : ['user'] }
