from flask              import *
from flask.ext.login    import current_user

from parse              import normalize
from search             import get_searches, search_for
from models.search      import Found, Search
from models.car         import Car
from forms              import ListingForm


listings = Blueprint( 'listings', __name__ )

# Used to make the settings dropdown faster
MAKES = [car.make for car in Car.objects().order_by('make')] 
print "Ready"


@listings.route('/landing/', methods = ['GET'])
@listings.route('/landing/<string:search>/<int:page>',methods=['GET'])
def landing(search = None, page = 0 ):
    """ Listings page """
    
    # If there is no search, get the first on off the list
    if current_user.is_anonymous():
        searches = []
    else:
        searches  = Search.related( current_user.pk )
    
    if not search:
        if len( searches ) > 0:
            display = searches[0]
        else:
            return redirect( url_for('landing') )
    else:
        display = Search.objects.get( pk = search )
    
    make   = Car.objects.get( make = display.make )
    models = [ model.model for model in make.models]
    model  = make.get_model(display.model)
    trims  = ['Any']
    if model:
        for trim in model.trims:
            trims.append(trim)

    # Show all the finds for a search
    finds     = []
    range = page * 100
    for find in display.finds[ range:range+100 ]:
        try:
            finds.append( Found.objects.get( search = display.pk, id_string = find ) ) 
        except Exception, e:
            print str(e)                                              
 
    context = dict( display  = display,
                    searches = searches,
                    finds    = finds,
                    page     = page,
                    pages    = len( display.finds )/100,
                    makes    = MAKES,
                    models   = models,
                    trims    = trims
                  )
 
    return render_template( 'listings.html', **context )

@listings.route('/sort/<string:search>/<string:key>', methods = ['GET'])
def sort( search = None, key= None ):
    """ Sort by date or stars 
    """
    search = Search.objects.get( pk = search )
    search.sort_finds(key)
    return redirect( url_for('listings.landing',search=search.pk, page=0) ) 

@listings.route('/save', methods = ['POST'])
def save():
    """ Save form from listings 
    """
    form = request.form
    search = Search.objects.get( pk = form['search'] )
 
    car  = None
    cars = None
    change = False
    
    if not form['name'] == search.name:
        search.name = form['name']
        change = True
    
    make   = form['make']
    model  = form['model'].split('&')
    model = model[1]

    trim  = form['trim']
    
    if not make == search.make or not model == search.model:
        car = Car.objects.make_model( make, model )
        if car:
            search.make = make
            search.model = model
            change = True
            
    if not trim == search.trim:
        search.trim = trim
        change = True
            
    if form['year_from'] and not int( form['year_from'] ) == search.year_from:
        search.year_from = int( form['year_from'])
        change = True

    if form['year_to'] and not form['year_to'] == search.year_to:
        search.year_to = int( form['year_to'])
        change = True

    if form['mileage']:
        miles = search.get( 'mileage_max', None )
        if miles and search.miles != form['milage']:
            search.mileage_min = 0
            search.mileage_max = int( form['milage'] )
            change = True
        
    if form['color_1'] or form['color_2']:
        colors = search.color
        if form['color_1']:
            if not form['color_1'] in search.color:
                search.color.append( form['color_1'] )
                change = True
        if form['color_2']:
            if not form['color_2'] in search.color:
                search.color.append( form['color_2'] )
                change = True
        for color in colors:
            if not color == form['color_1'] or not color == form['color_2']:
                search.color.remove(color)

 
    if form['option_1'] or form['option_2'] or form['option_3']:
        pass

    if change:
        search_for( search )
        
    return redirect( url_for('listings.landing',search=search.pk) )    
    

@listings.route('/click/<string:find>',methods=['GET'])
def click( find = None):
    """ When someone clicks on a heading url, increment the views count 
    """
    # Increment the views counter and save it
    found = Found.objects.get( pk = find )
    found.views += 1
    found.save()
    
    # redirect them to the listing url
    return redirect( found.url )


@listings.route('/delete/<string:search>',methods=['GET'])
def delete( search = None ):
    """ Delete a particular search
    """
    search = Search.objects.get( pk = search )
    search.delete()
    return redirect( url_for('listings.landing'))
    

@listings.route('/trash/<string:find>',methods=['GET'])
def trash( find = None ):
    """ Ajax call to trash a particular find
    """
    found = Found.objects.get( pk = find )
    found.trash = True
    found.save()
    
    return "",204   


@listings.route('/notes/<string:find>',methods=['GET','POST'])
def notes( find = None ):
    """ Ajax call to handle notes
    """
    find = Found.objects.get( pk = find )
    if request.method == 'GET':
        return render_template('note.html', find = find )

    find.notes = request.form['note']
    find.save()

    return '',204
 
@listings.route('/stars/',methods=['GET'])
@listings.route('/stars/<string:find>/<int:score>',methods=['GET'])
def stars( find = None, score = 0):
    """ Ajax call to set the ratings stars
    """
    find = Found.objects.get( pk = find )
    find.rating = score
    find.save()
    
    return '',204

@listings.route('/models/', methods=['GET'])
@listings.route('/models/<string:make>', methods=['GET'])
def models( make = None ):
    html = ""
    if make:
        models = Car.objects.models( make )
        for model in models:
            html += "<option value='{}&{}' >{}</option>".format( make,model,model  )

    return html

@listings.route('/trims/', methods=['GET'])
@listings.route('/trims/<string:make_model>', methods=['GET'])
def trims( make_model = None ):
    make,model = make_model.split('&')
    html = ""
    trims = Car.objects.trims( make, model )
    for trim in trims:
        html += '<option>{}</option>'.format( trim )
    return html
