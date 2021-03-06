import random

from flask                  import *
from flask.ext.login        import ( LoginManager, login_required, login_user,
                                     logout_user, current_user
                                   )

from datetime               import datetime, timedelta
from dateutil.relativedelta import relativedelta

from models.user            import User, Subscription
from forms                  import ( SignInForm, SignUpForm, AccountForm,
                                     SubscribeForm, UserForm, ForgotForm
                                   )
from geo                    import geocode
from payment                import subscription
from mailer                 import Mailer, Message
from config                 import EMAIL

user = Blueprint( 'user', __name__  )

login_manager = LoginManager()

def init_user(app):
    login_manager.setup_app(app)
    app.register_blueprint(user)
    pass


@login_manager.user_loader
def load_user(userid):
    """ Used by login to get a user """
    try:
        user = User.objects.get( pk = userid )
    except:
        return None
    return user


@user.route('/signup', methods=['GET', 'POST'])
def signup():
    """ Signup a new user """

    form = SignUpForm(request.form)
    if not request.method == 'POST' or not form.validate():
        context = { 'form':form }
        return render_template( 'signup.html', **context )

    username   = form.username.data
    password   = form.password.data
    email      = form.email.data
    phone      = form.phone.data
    address    = form.address.data
    subscribe  = form.subscribe.data
    duration   = form.duration.data
    pay_method = form.pay_method.data


    # Check if they they exist already
    try:
        user = User.objects.get( username = username )
    except User.DoesNotExist:
        try:
            user = User.objects.get( email = email )
        except User.DoesNotExist:
            user = User( username = username, email = email )
            user.address       = address
            user.phone         = phone
            user.address       = address
            user.subscribe     = subscribe

            user.set_password( password )

            try:
                local = geocode( user.address )
                user.location = [ float(local['lat']), float(local['lng']) ]
            except Exception, e:
                pass

            try:
                user.save()
            except Exception, e:
                print e
            else:
                # Place holder until paid subscription enabled
                if pay_method == 'free':
                    duration = 2

                expires = datetime.today() + relativedelta( months = 2 )
                subscription = Subscription( user    = user,
                                             expires = expires,
                                             active  = True )
                subscription.save()

    else:
        context = { 'error':'User already exists' }
        return render_template( 'signup.html', **context )


    login_user( user )
    return redirect( '/' )

@user.route('/account', methods=['GET','POST'])
@login_required
def account():
    if request.method == "GET":
        form = AccountForm( obj = current_user )
    else:
        form = AccountForm( request.form )
    try:
        subscribed = Subscription.objects.get( user = current_user.pk )
    except Subscription.DoesNotExist:
        subscribed = None

    if not request.method == 'POST' or not form.validate():
        context = { 'form':form, 'subscribed':subscribed }
        return render_template( 'account.html', **context )

    if form.username.data : current_user.username  = form.username.data
    if form.email.data    : current_user.email     = form.email.data
    if form.phone.data    : current_user.phone     = form.phone.data
    if form.address.data  : current_user.address   = form.address.data
    if form.subscribe.data: current_user.subscribe = form.subscribe.data
    if form.password.data : current_user.set_password( form.password.data )
    try:
        current_user.save()
    except Exception, e:
        print str(e)

    return redirect( url_for('landing') )


@user.route('/subscribe', methods=['POST'])
def subscribe():
    form = SubscribeForm( request.form )
    url = subscription( form.pay_method.data, form.duration.data )
    return redirect( url )


@user.route('/signin', methods=['GET', 'POST'])
def signin():
    """ Login a user
    """
    form = SignInForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email    = form.email.data
        password = form.password.data

        if username:
            try:
                user = User.objects.get( username = username )
            except User.DoesNotExist:
                form.username.errors = ['No such user or password']
                context = {'form':form}
                return render_template('signin.html', **context )

        elif email:
            try:
                user = User.objects.get( email = email )
            except User.DoesNotExist:
                form.username.errors = ['No such user or password']
                context = {'form':form}
                return render_template('signin.html', **context )
        else:
            form.username.errors = ['Enter a Username or Email address']
            context = {'form':form}
            return render_template('signin.html', **context )

        if user.check_password(password):
            login_user(user)
            return redirect('/')
        else:
            form.username.errors = ['No such user or password']
            context = {'form':form}
            return render_template('signin.html', **context )

    # Not a POST or invalid form
    context = {'form':form}
    return render_template( 'signin.html', **context )

@user.route('/logout')
@login_required
def logout():
    """ Logout a user
    """
    logout_user()
    return redirect('/')

def send_email( user, password ):
    """ Send new password to user
    """
    
    mail  = Mailer( host    = EMAIL['host'], 
                    port    = EMAIL['port'],
                    use_tls = EMAIL['use_tls'], 
                    usr     = EMAIL['user'], 
                    pwd     = EMAIL['password']
                  )
                   
    message = Message( From    = 'finds@finddaily.com',
                       To      = [user.email],
                       Subject = "Password Reset"
                     )
    
    body = """Your new password for FindDaily is {}
              You can reset it to what you like on your settings page once you log in with
              this password
           """.format(password )

    message.Body = body
    try:
        mail.send(message)
    except Exception, e:
        log('Send mail error: {}'.format(str(e)))


@user.route( '/forgot', methods=['GET','POST'] )
def forgot():
    form = ForgotForm(request.form)

    if request.method == 'POST' and form.validate():
        email = form.email.data
        try:
            user = User.objects.get( email = email )
        except User.DoesNotExist:
            form.email.errors = ['No such user']
            context = {'form':form}
            return render_template('forgot.html', **context )

        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        password = ''.join( map( lambda x: random.choice(chars), range(8) ))
        user.set_password( password )
        user.save()
        
        send_email( user, password )
        return redirect('/signin')
    else:
        context = {'form':form}
        return render_template('forgot.html', **context )