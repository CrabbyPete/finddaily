# Python imports

# Import Flask
from flask                  import *
from flask.ext.login        import current_user

# Import locals
from forms                  import SearchForm
from parse                  import parse_query
from search                 import search_for
from config                 import SECRET_KEY

# Blueprint apps
from user                   import user, init_user
from listings               import listings
from payment                import payment

from models.search          import Found

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Initialize the user so you can add it to the blueprint
init_user( app )
app.register_blueprint( listings )
app.register_blueprint( payment  )

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    return value.strftime(format)


@app.route('/', methods=['GET', 'POST'])
def landing():
    """ Landing page """

    form = SearchForm(request.form)

    if request.method == 'POST' and form.validate():
        search = parse_query( form.query.data, form.latitude.data, form.longitude.data, current_user )
        if not search.make:
            search.delete()
            form.query.errors = ["Unknown make or model"]
            context = {'user':current_user, 'form':form }
            return render_template( 'landing.html', **context )

        search_for( search )
        return redirect( url_for('listings.landing', search = search.pk, page =  0) )

    context = { 'user':current_user, 'form':form }
    return render_template( 'landing.html', **context )


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.errorhandler(500)
def internal_error(error):
    msg = log(str(error) )
    return "500 error:{}".format(msg)

if __name__ == '__main__':
    app.run(debug = False,  port=8000)
