from furl.furl import furl

import urllib
import cjson

def get_geocode(location):
    '''Helper function for Geocode classes'''
    coded = Yahoo(location)
    if coded.error != -1:
        return None
    else:
        return coded
    

class Base(object):
    '''Geocoding abstraction
    
    The city is in long form
    The state is in short form
    The country is in short form
    
    Usage:
    >>> g = GeocodeGoogle('Spokane')
    >>> g.city
    ... Spokane
    >>> g = GeocodeGoogle('7208 N. Crestline, Spokane, Washington')
    >>> g.city
    ... Spokane
    >>> g.state
    ... WA
    '''
    
    def __init__(self, search_location):
        self.city = None
        self.state = None
        self.country = None
        self.error = -1
        self.error_msg = ''
        self.search_location = search_location
        self.build_url()
        self.parse()
        
    @property
    def formatted_location(self):
        return '{0}, {1}, {2}'.format(self.city, self.state, self.country)
    
    def fetch(self, url):
        '''Either get from the cache or actually fetch it.
        We're not really using this yet :)
        '''
        request = urllib.urlopen(url)
        return request
    
    def parse(self):
        raise NotImplementedError
    
    def build_url(self):
        raise NotImplementedError


class Google(Base):
    def parse(self):
        self._json = self._request['results'][0]['address_components']
        for element in self._json:
            location_type = element['types']
            if 'administrative_area_level_2' in location_type:
                # This is what google calls a `city`
                self.city = element['long_name']
            if 'administrative_area_level_1' in location_type:
                # This is what google calls a `state`
                self.state = element['long_name']
            if 'country' in location_type:
                # This is a `country`
                self.country = element['short_name']
            if 'locality' in location_type:
                self.locality = element['long_name']
            if 'street_number' in location_type:
                self.street_number = element['short_name']
            if 'route' in location_type:
                self.road = element['long_name']
                            
    def build_url(self):
        api_url = furl(MAPS_API_GEOCODE)
        api_url.args['address'] = self.search_location
        api_url.args['sensor'] = False
        request = self.fetch(api_url.url)
        request = cjson.load(request)
        self._request = request


class Yahoo(Base):
    def parse(self):
        result_set = self._request['ResultSet']
        if result_set['Found'] == 0:
            self.error_msg = result_set['ErrorMessage']
            self.error = result_set['Error']
            return

        # Get only the first one
        results = result_set['Results'][-1]
        if 'city' in results:
            self.city = results['city']
        if 'countrycode' in results:
            self.country = results['countrycode']
        if 'state' in results:
            self.state = results['state']
        if 'longitude' in results:
            self.longitude = float(results['longitude'])
        if 'latitude' in results:
            self.latitude = float(results['latitude'])
        
        self.geohash = geohash.encode(self.latitude, self.longitude, precision=6)
        
    def build_url(self):
        f = furl('http://where.yahooapis.com/geocode?flags=JST&gflags=A')
        f.args['location'] = self.search_location
        f.args['appid'] = YAHOO_ID
        request = self.fetch(f.url)
        request = cjson.load(request)
        self._request = request


