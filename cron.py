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
from models.user    import User
from models.search  import Search
from search         import search_for

from mongoengine import *
connect('finddaily')

def search_now():
    for user in User.objects.all():
        searches = Search.objects.filter( user = user.pk )
        for search in searches:
            if not search.user:
                continue
            search_for( search )

if __name__ == '__main__':
    search_now()
