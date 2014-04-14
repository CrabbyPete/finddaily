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
from models.search  import Search
from search         import search_for


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
    
def search_now():
    """ Check all active searches
    """
    today = datetime.now()
    for sub in Subscription.objects.all():
        if sub.active and today <= sub.expires:

            searches = Search.objects.filter( user = sub.user )
            print "Searching {} for {} at {}".format( len(searches), sub.user.username, today.strftime('%Y-%m-%d %H:%M' ) )            
            found = []
            for search in searches:
                if search.user:
                    finds = search_for( search )
                    found.update( finds )

if __name__ == '__main__':
    search_now()
    clean_up()
