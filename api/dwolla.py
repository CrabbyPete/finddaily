import time
import requests
import hmac
import base64
import hashlib


class Dwolla(object):
    base_url = 'https://www.dwolla.com/payment/pay'
    
    def __init__(self, key, secret, account_id, callback = None, redirect ):
        self.key = key
        self.secret = secret
        self.account_id
        if callback:
            self.callback = callback
    
        if redirect:
            self.redirect = redirect
            
            
    def hmac_sha1(self, timestamp, order_id ):
        timestamp = time.time()
        query = '{}&{}&{}&{}'.format(self.key,timestamp,order_id)
        signature = hmac.new(self.secret, query, hashlib.sha1).digest()
        return signature

    def api(self, url, **kwargs):
        response = requests.post( url, **kwargs )
        if response.ok:
            reply = json.loads(response.text)
            return True, reply
        else:
            return False, response.reason
    
    def order(self, price, id, decsription ):
        timestamp = time.time()
        data = dict ( key                 = DWOL,
                      signature           = self.hmac_sha1(timestamp, id),
                      timestamp           = timestamp,
                      callback            = self.callback,
                      redirect            = self.redirect,
                      allowFundingSources = True,
                      destinationId       = id,
                      amount              = price,
                      shipping            = 0.00,
                      tax                 = 0.00,
                      name                = 'Subscription Fee',
                      description         = description
                    )
        reply = self.api(self.base_url, data=data)
        if ok:
            return reply