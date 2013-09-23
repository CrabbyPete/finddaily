import re

from models.user                    import User
from wtforms                        import ( Form, TextField, PasswordField, BooleanField, 
                                             SubmitField, HiddenField, RadioField, SelectField     
                                           )
from flask.ext.wtf.html5            import  TelField, EmailField, IntegerField

from wtforms                        import validators
from flask.ext.mongoengine.wtf.orm  import model_form

class LoginForm( Form ):
    """ Sign in form """
    username = TextField( u'Username')
    email    = TextField( u"Email" )
    password = PasswordField(u"Password")
    submit   = SubmitField("")


def validate_phone( form, field ):
        PHONE_REGEX = re.compile(r'1?\W*([2-9][0-8][0-9])\W*([2-9][0-9]{2})\W*([0-9]{4})(\se?x?t?(\d*))?')

        if not PHONE_REGEX.match(field.data):
            raise ValidationError('Invalid Phone number: %s' % field.data)

UserForm = model_form( User )

class AccountForm( Form ):
    """ Account Form """
    username    = TextField(u"Username",[validators.Required()])
    email       = EmailField(u"E-Mail",[validators.Required(), 
                                        validators.Email(message= u'That\'s not a valid email address.')
                                       ])
    
    subscribe   = BooleanField(u'',default = True)
    phone       = TelField(u"Phone Number",[ validate_phone ] )
    password    = PasswordField(u"Password")
    new_passwrd = PasswordField(u"New Password")
    address     = TextField(u"Full Address")
    save        = SubmitField(u'', default=u"Save")
    
class SubscribeForm( Form ):
    """ Subscription form """
    duration    = IntegerField(u"Subscribe for")
    pay_method  = RadioField( u'Subscribe using', choices=[('paypal','PayPal'), 
                                                           ('dwolla','Dwolla'), 
                                                           ('bitcoin','Bitcoin'),
                                                           ('free','Free for now')
                                                          ]                     
                            )
    subscribe   = SubmitField( u"Subscribe" )



class SignUpForm( AccountForm, SubscribeForm ):
    """ Merge Account and Subscribe when someone first signs up """
    pass

class SearchForm( Form ):
    """ Main landing page search form. Longitude and Latitude are filled in with html5
    """
    longitude = HiddenField(id='longitude')
    latitude  = HiddenField(id='latitude')
    query     = TextField("", [validators.Length( min = 2, max = 256)] )
    
    submit   = SubmitField("Go" )


class ListingForm( Form):
    search      = HiddenField()
    field       = TextField("")
    make        = SelectField()
    model       = SelectField()
    trim        = SelectField()
    years_from  = TextField()
    years_to    = TextField()
    mileage     = TextField()
