#-------------------------------------------------------------------------------
# Name:        cron.py
# Purpose:     Periodically go through the user database and send updates
#
# Author:      Peter
#
# Created:     17/08/2013
# Copyright:   (c) Peter 2013
#-------------------------------------------------------------------------------
from datetime       import datetime, timedelta
from jinja2         import Environment, PackageLoader

from models.user    import User, Subscription
from models.search  import Search, Found
from search         import search_for
from mailer         import Mailer, Message
from config         import EMAIL
from log            import log

 
def clean_up(days = 2 ):
    """ Clean up searches by anonymous users
    """
    stale = datetime.today() - timedelta( days = days )
    for search in Search.objects():
        if not search.user and search.created <= stale:
            print "deleting {} for {}-{}".format( search.pk, search.make, search.model )
            search.delete()
    

def send_email( user, finds ):
    """ Send mail to the user about the finds
    """
    
    mail  = Mailer( host    = EMAIL['host'], 
                    port    = EMAIL['port'],
                    use_tls = EMAIL['use_tls'], 
                    usr     = EMAIL['user'], 
                    pwd     = EMAIL['password']
                  )
                   
    message = Message( From    = 'finds@finddaily.com',
                       To      = [user.email],
                       Subject = "Daily Finds"
                     )
    
    body = "Find daily results for {} \r\n".format( datetime.today().strftime('%Y-%m-%d') )
    try:
        env = Environment(loader=PackageLoader('cron', 'templates'))
        template = env.get_template('email.html')
        html = template.render(user = user, finds = finds )
    except Exception, e:
        log( 'Render template error {}'.format(str(e)))

    for find in finds:
        body += find.heading + "\r\n"

    message.Body = body
    message.Html = html
    try:
        mail.send(message)
    except Exception, e:
        log('Send mail error: {}'.format(str(e)))


def search_now():
    """ Check all active searches
    """
    today = datetime.now()
    for sub in Subscription.objects.all():
        found = []
        if sub.active and today <= sub.expires:
            if not isinstance( sub.user, User ):
                sub.delete()
                continue
            
            searches = Search.objects.filter( user = sub.user )
   
            print "Searching {} for {} at {}".format( len(searches), sub.user.username, today.strftime('%Y-%m-%d %H:%M' ) )            
  
            for search in searches:
                if search.user:
                    finds = search_for( search )
                    for find in finds:
                        print "Found: {}".format(find)
                        found.extend( finds )
        if found:
            send_email( sub.user, found )

if __name__ == '__main__':
    search_now()
    clean_up()
