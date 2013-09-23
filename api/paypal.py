import json
import requests
from requests.auth      import HTTPBasicAuth

class PayPal( object ):
    base_url = 'https://api.sandbox.paypal.com/'
    access_token = None
    
    def __init__( self, client_id, secret, base_url = None ):
        self.client_id = client_id
        self.secret = secret
        
        if base_url:
            self.base_url = base_url
        
    def api(self, url, **kwargs):
        response = requests.post( url, **kwargs )
        if response.ok:
            reply = json.loads(response.text)
            return True, reply
        else:
            return False, response.reason
    
    def get_token(self):
        url = self.base_url + 'v1/oauth2/token'
        headers = {'Accept': 'application/json',
                   'Accept-Langquage':'en_US'
                  }
        data = {'grant_type':'client_credentials'}
        ok, reply = self.api( url,
                          headers = headers, 
                          data    = data, 
                          auth    = HTTPBasicAuth( self.client_id, self.secret ) 
                        )
        
        if ok:
            self.access_token = reply['access_token']
            return self.access_token
        
        return False

    def create_payment(self, price, return_url, cancel_url, description = None ):
        url = self.base_url + 'v1/payments/payment'
        if not self.access_token:
            self.get_token()
            
        headers = {'Content-Type':'application/json',
                   'Authorization':'Bearer {}'.format( self.access_token )
                  }
    
        data = json.dumps({ "intent":"sale",
                             "redirect_urls":{
                                              "return_url":return_url,
                                              "cancel_url":cancel_url
                                             },
                            "payer":{"payment_method":"paypal"},
                            "transactions":[{"amount":{ "total":'%.2f'%price, "currency":"USD" },"description":description}]
                          })

        ok, reply = self.api( url, headers = headers, data = data )
        if ok:
            for link in reply['links']:
                if link['rel'] == "approval_url":
                    break
            else:
                return False,None
            return reply['id'], link['href']
        
        return False,None
    
    def execute_payment(self, id, token, payer_id):
        url = self.base_url + 'v1/payments/payment/{}/execute/'.format(id)
        headers = {'Content-Type':'application/json', 
                   'Authorization':'Bearer {}'.format( self.access_token )
                  }

        data = {"payer_id":payer_id} 
        ok, reply = self.api( url, headers = headers, data = data )
        if ok:
            return repy
        return False
                   
                