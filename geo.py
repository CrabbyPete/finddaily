import urllib,urllib2,time,json,requests
"""


"""
root_url = "http://maps.googleapis.com/maps/api/geocode/json?"
def walk(seq, look_for ):
    """
    Walk through the dictionary to find a value
    """
    if isinstance( seq, list ):
        for value in seq:
            found = walk( value, look_for )
            if found:
                return found

    elif isinstance( seq, dict ):
        for key,value in seq.iteritems():
            if key == look_for:
                return (key,value)

            if isinstance( value, dict ) or isinstance( value, list ):
                found = walk( value, look_for )
                if found:
                    return found
    return None



#https://developers.google.com/maps/documentation/geocoding/#ReverseGeocoding
def reverse_geocode(lat,lng):
    #coords = "%f,%f" %(lat,lng)
    values = {'latlng' :"%s,%s" %(lat,lng),'sensor':'false'}
    data = urllib.urlencode(values)
    url = root_url+data
    response = requests.get(url)
    geodat = json.loads(response.text)
    zipcode = address = None
    for component in geodat['results']:
        types  = component.get('types', None )
        if 'postal_code' in types:
            zipcode = component['address_components'][0]['long_name']
        if 'street_address' in types:
            address = component['formatted_address']
    return address, zipcode

# https://developers.google.com/maps/documentation/geocoding/
def geocode(addr):
    # Encode our dictionary of url parameters
    values = {'address' : addr, 'sensor':'false'}
    data = urllib.urlencode(values)
    # Set up our request
    url = root_url+data
    response = requests.get( url )
    # Get JSON data
    if response.ok:
        geodat = json.loads(response.text)
        location = walk( geodat, 'location')
        return location[1]

    return None

if __name__ == '__main__':
    reply = geocode( '280 Monroe Ave, Wyckoff NJ 07481')
    reply = reverse_geocode(reply['lat'],reply['lng'] )
    pass