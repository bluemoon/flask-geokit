from __future__ import absolute_import

from furl.furl import furl

import geohash
import urllib
import json
try:
    import memcache
    HAS_MEMCACHE = True
except:
    HAS_MEMCACHE = False
    
class Geokit(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self._yahoo_id = app.config.get('GEOKIT_YAHOO_ID')
        self._service  = app.config.get('GEOKIT_SERVICE', 'yahoo').lower()
        
    def geocode(self, location):
        if self._service == 'yahoo':
            return Yahoo(location, self._yahoo_id)
        
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
    
    def __init__(self, search_location, api_key):
        self.city = None
        self.state = None
        self.country = None
        self.error = -1
        self.error_msg = ''
        self.search_location = search_location
        self.api_key = api_key
        
        if HAS_MEMCACHE:
            self.mc = memcache.Client(['127.0.0.1:11211'], debug=0)
            
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
        request = json.load(request)
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
        if HAS_MEMCACHE:
            value = self.mc.get("YH_" + self.search_location)
            if value:
                return value
                
        f = furl('http://where.yahooapis.com/geocode?flags=JST&gflags=A')
        f.args['location'] = self.search_location
        f.args['appid'] = self.api_key
        request = self.fetch(f.url)
        request = json.load(request)
        self._request = request
        if HAS_MEMCACHE:
            self.mc.set("YH_" + self.search_location, request)




