import webapp2
from google.appengine.ext import ndb
import db_models
import json
import urllib
'''
	Group 1
	Michael Jones
	Peter Friedrichsen
	David Crisman
	
	Project CS419
'''

class Business(webapp2.RequestHandler):	
	''' 
		curl --request GET http://cs419recycle.appspot.com/v.1.0/business/<name>
		
		Refactored by Peter Friedrichsen on 5.6.15
	'''

	def get(self, **kwargs):
				
		if "name" in kwargs:
				# If business name provided, return business information
			url_name = kwargs['name']
			replaced_name = url_name.replace("%F", "%2F")
			name = urllib.unquote(replaced_name)
			
			q = db_models.business.query()
			q = q.filter(db_models.business.bus_name == name)
			keys = q.fetch()
			if (keys):
				result =  keys[0].to_dict()
				self.response.write(json.dumps(result))
			else:
				self.response.write("That business was not found")
			
		else:
				# If no business name was provided, list all business names
			q = db_models.business.query()
			keys = q.fetch()
			if keys:
				results = { 'Business' : [x.bus_name for x in keys]}
				self.response.write(json.dumps(results))
			else:
				self.response.write("Error: no businesses available")