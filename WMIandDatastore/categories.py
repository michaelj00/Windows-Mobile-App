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

class Categories(webapp2.RequestHandler):	
	'''
		This GET takes a kwarg of "name" and will search the datastore
			for a category with that name. If the category is found it will 
			return details of same. Which will later turn into the 
			businesses that recycle the category. 
	
		http://localhost:8080/v.1.0/categories/<category name>    ie. http://localhost:8080/v.1.0/categories/large_appliances
		
		curl request
			curl --request GET http://cs419recycle.appspot.com/v.1.0/categories/large_appliances
			
		Refactored by Peter Friedrichsen on 5.6.15
	'''
	def get(self, **kwargs):
	
		if "name" in kwargs:
			#name = kwargs['name']
			url_name = kwargs['name']
			replaced_name = url_name.replace("%F", "%2F")
			name = urllib.unquote(replaced_name)

			# Retrieve category from datastore
			q = db_models.recycle_category.query()
			q = q.filter(db_models.recycle_category.category_name == name)
			keys = q.fetch()
			
			# If category exists, find businesses that recycle it
			if (keys):
				category_key_get = db_models.recycle_category.query(db_models.recycle_category.category_name == name).fetch(1, keys_only=True)[0]
				category = category_key_get.get()
				
				q = db_models.business.query()
				q = q.filter(db_models.business.bus_categories == category_key_get)
				businesses = q.fetch()
				
					# If businesses found, print results in JSON format
				if businesses:
					response = { 'Business' : [x.bus_name for x in businesses], 'Items' : [item for item in category.items]}
					self.response.write(json.dumps(response))
					
					# If not, print error message
				else:
					response = { 'Business' : [], 'Items' : [item for item in category.items]}
					self.response.write(json.dumps(response))
					#self.response.write("No businesses accept that category")
					
		
			else:
					#	Protect where category does not exist in datastore
				self.response.write("That category was not found")
		else:
					#	If no category name was entered, list all categories
			q = db_models.recycle_category.query()
			keys = q.fetch()
			if keys:
				results = { 'Category' : [x.category_name for x in keys]}
				self.response.write(json.dumps(results))
			else:
				self.respone.write("Error: no categories available")