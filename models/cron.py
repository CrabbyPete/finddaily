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


from mongoengine import *
connect('finddaily')

def main():
    for user in User.objects.all():
        searches = Search.objects.filter( user = user.pk )
        for search in searches:
             search_for( search )

if __name__ == '__main__':
    main()
