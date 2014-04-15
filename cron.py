#-------------------------------------------------------------------------------
# Name:        cron.py
# Purpose:     Periodically go through the user database and send updates
#
# Author:      Peter
#
# Created:     17/08/2013
# Copyright:   (c) Peter 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from datetime       import datetime, timedelta
from models.user    import User, Subscription
from models.search  import Search, Found
from search         import search_for
from mailer         import Mailer, Message


from mongoengine import *
connect('finddaily')

def clean_up():
    """ Clean up searches by anonymous users
    """
    stale = datetime.today() - timedelta( days = 2 )
    for search in Search.objects():
        if not search.user and search.created <= stale:
            print "deleting {} for {}-{}".format( search.pk, search.make, search.model )
            search.delete()
    

EMAIL_HOST          = 'smtp.webfaction.com'
EMAIL_HOST_USER     = 'douma'
EMAIL_HOST_PASSWORD = 'fishf00l'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True

def send_email( user, finds ):
    """ Send mail to the user about the finds
    """
    
    mail  = Mailer( host    = EMAIL_HOST, 
                    port    = EMAIL_PORT,
                    use_tls = EMAIL_USE_TLS, 
                    usr     = EMAIL_HOST_USER, 
                    pwd     = EMAIL_HOST_PASSWORD
                  )
                   
    message = Message( From    = "finds@finddaily.com",
                       To      = [user.email],
                       Subject = "Daily Finds"
                     )
    
    body = "Find daily results for {}".format( datetime.today().strftime('%Y-%m-%d') )
    for find in finds:
        body += find.heading + "\r\n"

    message.Body = body
    mail.send(message)


def search_now():
    """ Check all active searches
    """
    today = datetime.now()
    for sub in Subscription.objects.all():
        found = []
        if sub.active and today <= sub.expires:

            searches = Search.objects.filter( user = sub.user )
            print "Searching {} for {} at {}".format( len(searches), sub.user.username, today.strftime('%Y-%m-%d %H:%M' ) )            
  
            for search in searches:
                if search.user:
                    finds = search_for( search )
                    if finds:
                        for find in finds:
                            print "Found {}".format(find)
                        found.extend( finds )
        if found:
            send_email( sub.user, found )

if __name__ == '__main__':
    search_now()
    clean_up()
