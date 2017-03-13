import requests
import time
import json

import uuid
import paypalrestsdk as paypal_api
from dwolla             import DwollaGateway


from flask              import *
from flask.ext.login    import current_user
from datetime           import datetime
from dateutil           import relativedelta

from config             import PAYPAL, PRICE, DWOLLA
from models.user        import User, Subscription, Payment

from decimal            import Decimal, getcontext

payment = Blueprint( 'payment', __name__ )

# Setup PayPal API
PAL = paypal_api.set_config( mode          = "sandbox", 
                             client_id     = PAYPAL['client_id'],
                             client_secret = PAYPAL['secret']
                            )
#PAL.get_token()


# Setup Dwolla API
DWL = DwollaGateway( DWOLLA['key'], DWOLLA['secret'], DWOLLA['redirect'] )
DWL.set_mode('TEST')
                    
                    
def paypal( price, id, description ):
    
    pay = paypal_api.Payment( { "intent":"sale",
                                   "redirect_urls":{ "return_url":'{}/{}'.format( PAYPAL['return_url'],id ),
                                                     "cancel_url":'{}/{}'.format( PAYPAL['cancel_url'],id )
                                                    },
                                    "payer":{"payment_method":"paypal"},
                                    "transactions":[{"amount":{ "total":'%.2f'%price, "currency":"USD" },
                                                     "description":description
                                                   }]
                                  }
                                )
    reply = pay.create()
    if reply:
        for link in pay['links']:
            if link['rel'] == "approval_url":
                return pay['id'], link['href']
    return None
    
@payment.route('/paypal_return/<string:id>', methods=['GET', 'POST'])  
def paypal_return( id = None ):
    subs = Subscription.objects.get( payments__id = id )
    for payment in subs.payments:
        if payment.id == id:
            break
    
    pay = paypal_api.Payment.find( payment.payment_id )
    response = pay.execute( {"payer_id": request.args['PayerID']} )
    
    if not pay.paid:
        now = datetime.now()
        if subs.expires > now:
            subs.expires = subs.expires + relativedelta( months = payment.months )
        else:
            subs.expires = now + relativedelta( months = payment.months )
        
        pay.paid = datetime.now()
        subs.active = True
        subs.save()
    
    return redirect( url_for( 'user.account') )
    


@payment.route('/paypal_cancel/<string:id>', methods=['GET', 'POST'])   
def paypal_cancel( id  = None):
    subs = Subscription.objects.get( payments__id = id )
    for payment in subs.payments:
        if payment.id == id:
            break
        
    token = request.form['token']
    return redirect( url_for('landing') )


def bitcoin(months):
    pass

def dwolla(price, id, description):
    DWL.start_gateway_session()
    DWL.add_gateway_product(description, price)
    url = DWL.get_gateway_URL(DWOLLA['account'], id, callback=DWOLLA['callback'] )
    return id, url


@payment.route('/dwolla_return/', methods=['GET', 'POST']) 
def dwolla_return():
    if 'error' in request.args:
        return redirect( url_for( 'user.account') )

    id = request.args['orderId']
    subs = Subscription.objects.get( payments__id = id )
    for pay in subs.payments:
        if pay.id == id:
            break
    
    if not pay.paid:
        now = datetime.now()
        if subs.expires > now:
            subs.expires = subs.expires + relativedelta( months = pay.months )
        else:
            subs.expires = now + relativedelta( months = pay.months )
        
        pay.paid = datetime.now()
        subs.active = True
        subs.save()     

    return redirect( url_for( 'user.account') )

           
PAY_METHODS = { 'dwolla':dwolla, 
                'paypal':paypal,
                'bitcoin':bitcoin
              }
         
def subscription( method, months ):
    try:
        subs = Subscription.objects.get( user = current_user.pk )
    except Subscription.DoesNotExist:
        user = User.objects.get( pk = current_user.pk )
        subs = Subscription( user = user )
    price = float( PRICE ) * float ( months )   

    try:
        id = str( uuid.uuid4().int >> 64 )
        description = 'Subscription for {} months'.format(months)
        payment_id, link  = PAY_METHODS[method]( price, id, description )
    except Exception, e:
        print str(e)
        return url_for('landing')  # Change this to some error notification
    
    
    payment = Payment( id = id, 
                       payment_id = payment_id,
                       months = months,
                       amount = price,
                       method = method  
                     )
    
    subs.payments.append( payment )
    subs.save()
    return link
    
