import webapp2
from webapp2_extras import sessions
import session_module
from google.appengine.ext import ndb
import db_models
import base
import os
import jinja2
import json
from urlparse import urlparse
import urllib

'''
	Group 1
	Michael Jones
	Peter Friedrichsen
	David Crisman
	
	Project CS419
'''
'''
	Changes Michael 6/7/2015
	line 50 un_urlencoding string
	line 67 added urlencoded string url_bname
	line 152, 155 removed elses that resulted in failed geolocation
	line 355, 360 removed elses that resulted in failed geolocation
	line 358, 361 removed elses that resulted in failed geolocation \ line 428 added business list to add_business page
'''

class Business(base.MainPage):	
	
	def __init__(self, request, response):
		self.initialize(request, response)
		self.template_values = {}


	def render(self, page, variables):
		base.MainPage.render(self, page, variables)	
		
	def get(self, **kwargs):
		if self.session.get('authorized') != 1:
			self.template_values['error'] = "Please log in"
			self.render('login.html', self.template_values)
			return
	
		if "name" in kwargs:
				# If business name provided, return business information
			name = kwargs['name']
				#	UnUrl ecode the business name for comparison to the data base. 
			un_url = urllib.unquote_plus(name.encode('ascii')).decode('utf-8')
			
			q = db_models.business.query()
			q = q.filter(db_models.business.bus_name == un_url)
			keys = q.fetch()

			if (keys):
				x = keys[0]
				cats = []
				for c in x.bus_categories:
					something = c.get()
					cats.append(something.category_name)
				self.template_values['MyCats'] = cats
				self.template_values['Cats'] = [{'name':x.category_name} for x in db_models.recycle_category.query().order(db_models.recycle_category.category_name).fetch()]
				self.template_values['Business'] = keys[0]
				self.render('edit_business.html', self.template_values)	
			else:
				self.template_values['error'] = "That business was not found"
			
		else: 
			self.template_values['Businesses'] = [{'url_bname': (urllib.quote_plus(x.bus_name).replace('%2F', '%252F')), 'bname':x.bus_name, 'bphone':x.bus_phone, 'bhours':x.bus_hours, 'bdays':x.bus_days, 'baddress':x.bus_address, 'burl':x.bus_url, 'bcats':x.bus_categories, 'key':x.key.urlsafe()} for x in db_models.business.query().order(db_models.business.bus_name).fetch()]
			self.render('business.html', self.template_values)

	def post(self):
		if self.session.get('authorized') != 1:
			self.template_values['error'] = "Please log in"
			self.render('login.html', self.template_values)
			return
	
		action = self.request.get('action')
		if action == 'update_business':
			if self.request.get('bus_name'):
				bus_name = self.request.get('bus_name')
				
				# Retrieve business entity
				q = db_models.business.query()
				q = q.filter(db_models.business.bus_name == bus_name)
				keys = q.fetch(keys_only=True)

				# If business exists, add new data, update database, and print success
				if keys:
				
					business = keys[0].get()
					
					#This will be an array of the categories that were selected.
					chosen_categories = []
					chosen_categories = self.request.get_all('categories')

					#Input the updated values									
					if self.request.get('bus_phone'):
						business.bus_phone = self.request.get('bus_phone')
					else:
						business.bus_phone = ""	
					if self.request.get('bus_hours'):
						business.bus_hours = self.request.get('bus_hours')
					else:
						business.bus_hours = ""							
					if self.request.get('bus_days'):
						business.bus_days = self.request.get('bus_days')
					else:
						business.bus_days = ""							
					if self.request.get('bus_address'):
						business_address = self.request.get('bus_address')
						
						
						#		First let's see if address was changed. Geocoding does not need to be done unless it is changed.
						#		Get address in datastore for business
						bus_key_get = db_models.business.query(db_models.business.bus_name == bus_name).fetch(1, keys_only=True)[0]
						business_address_to_verify = bus_key_get.get()
						database_address = business_address_to_verify.bus_address
						
							#	if the address do not match we will modify in the database
							#	including geocode
						if database_address != business_address:
							#	setup business address for Google Geocoding request. " " must be "+"
							url_address = urllib.quote_plus(business_address)
							#	Create url string
							url_http_string = "https://maps.googleapis.com/maps/api/geocode/json?address="
							google_API_key = "&key=AIzaSyAnYYjW2ezjaQnSIyyVtEcC4sgmCTRr1l4"
							combined_url_string = url_http_string + url_address + google_API_key

							#	Make Google geocode request
							result = json.load(urllib.urlopen(combined_url_string))
							
							#	If correct Google should have only returned one item. Count to verify
							count = 0
							for s in result['results']:
								count = count + 1
						
							#	Only one result was returned from Google 
							#	lat and long and address it to the database 
							if count == 1:
								#	Parse the string to get lat and long out. 
								bus_lat = json.dumps([s['geometry']['location']['lat'] for s in result['results']], indent=2)
								bus_long = json.dumps([s['geometry']['location']['lng'] for s in result['results']], indent=2)
								#	Remove the []'s and " "
								formatted_bus_lat = bus_lat.translate(None,"[] ")
								formatted_bus_long = bus_long.translate(None,"[] ")
							
								#	Commit business address to datastore. 
								business.bus_address = business_address
								business.bus_lat = formatted_bus_lat
								business.bus_long = formatted_bus_long
							else:
								self.template_values['Geo_error'] = "Geocoding returned multiple addresses. Please manually verify"
								business.bus_address = business_address
					else:
						business.bus_address = ""								
					if self.request.get('bus_lat'):
						business.bus_lat = self.request.get('bus_lat')

					if self.request.get('bus_long'):
						business.bus_long = self.request.get('bus_long')

					if self.request.get('bus_url'):
						business_url_test = self.request.get('bus_url')
						parsed_url = urlparse(business_url_test)
						if ((parsed_url.scheme == "http") or (parsed_url.scheme == "https")) and (parsed_url.netloc != ""):
							business.bus_url = business_url_test
						elif ((business_url_test == "n/a") or (business_url_test == " ") or (business_url_test == "")):
							business.bus_url = business_url_test
						else:
							business.bus_url = business_url_test
							self.template_values['url_error'] = "If changing the URL, please include http://"
							self.template_values['MyCats'] = chosen_categories
							self.template_values['Cats'] = [{'name':x.category_name} for x in db_models.recycle_category.query().order(db_models.recycle_category.category_name).fetch()]
							self.template_values['Business'] = business
							self.render('edit_business.html', self.template_values)
							return
					else:
						business.bus_url = ""	
					#Prepare an array with all the categories.  This will be used to create the complement of the selected categories as well as to pass as a template value to the HTML file.
					
					all_cats = []
					p = db_models.recycle_category.query().fetch()
					for a in p:
						all_cats.append(a.category_name) 


					#This will store the complement of the selected categories.  We need this to make sure and remove any previous linked business-category pairs that are now 'unlinked.'
					remove_cats = []
					for c in all_cats:
						if c not in chosen_categories:
							remove_cats.append(c)

					#Add the selected categories to the database in both the business section and the category section.
					for b in chosen_categories:
						category_key_get = db_models.recycle_category.query(db_models.recycle_category.category_name == b).get()
						category_key = category_key_get.key.id()

						bus_key = business.key.id()
						bus_key_to_update = ndb.Key(db_models.business, "base-business", db_models.business, int(bus_key))
						category_key_to_update = ndb.Key(db_models.recycle_category, "base-category", db_models.recycle_category, int(category_key))

						if bus_key_to_update not in category_key_get.bus_cat_link:
							category_key_get.bus_cat_link.append(bus_key_to_update)
							category_key_get.put()
							business.bus_categories.append(category_key_to_update)
							business.put()

					for r in remove_cats:
						category_key_get = db_models.recycle_category.query(db_models.recycle_category.category_name == r).fetch(1, keys_only=True)[0]
						category_to_remove = category_key_get.get()

						bus_key = keys[0]

						if bus_key in category_to_remove.bus_cat_link:
							category_to_remove.bus_cat_link.remove(bus_key)
							category_to_remove.put()
							business.bus_categories.remove(category_key_get)
							business.put()

					business.put()
					cats = []
					for c in business.bus_categories:
						something = c.get()
						cats.append(something.category_name)
					self.template_values['MyCats'] = chosen_categories
					self.template_values['Cats'] = [{'name':x.category_name} for x in db_models.recycle_category.query().order(db_models.recycle_category.category_name).fetch()]
					self.template_values['special_message'] = "Update Successful"
					self.template_values['Business'] = business
					self.render('edit_business.html', self.template_values)  

				# If business doesn't exist, print error and exit
				else:
					self.template_values['error'] = "Error: business not found"
					
			else:
				self.response.write("You did not enter a business name to update")
		
		elif action == 'delete_business':
			bus_name = self.request.get('bus_name')
			q = db_models.business.query()
			q = q.filter(db_models.business.bus_name == bus_name)
			keys = q.fetch()
			if (keys):
				self.template_values['Business'] = keys[0]
				self.render('delete_business.html', self.template_values)	
			else:
				self.template_values['error'] = "That business was not found"

		elif action == 'log_out':
			self.session.clear()
			self.template_values['message'] = 'Logged out'
			self.render('login.html')
				
		elif action == 'sure_delete':
			bus_name = self.request.get('bus_name')
									#	Make sure business exists in datastore.
			q = db_models.business.query()
			q = q.filter(db_models.business.bus_name == bus_name)
			keys = q.fetch(keys_only = True)
						
						# 	if exists start delete process
			if keys:

						#	Get the business key to delete
				bus_key_get = db_models.business.query(db_models.business.bus_name == bus_name).fetch(1, keys_only= True)[0]
									
						#	Search recycle_category where business is linked to it.
				q = db_models.recycle_category.query()
				q = q.filter(db_models.recycle_category.bus_cat_link == bus_key_get)
				result_of_fetch = q.fetch()
				
						#	For each item in the list remove the link to the business.
				for x in result_of_fetch:
					x.bus_cat_link.remove(bus_key_get)
					x.put()
				
				#self.response.write("Removed references to business in items")
				
						#	Delete business from datastore
				business_key_get = db_models.business.query(db_models.business.bus_name == bus_name).get()
			
				business_key_get.key.delete()		
				self.template_values['special_message'] = bus_name + " Deleted."
				self.template_values['Businesses'] = [{'url_bname': (urllib.quote_plus(x.bus_name).replace('%2F', '%252F')),'bname':x.bus_name, 'bphone':x.bus_phone, 'bhours':x.bus_hours, 'bdays':x.bus_days, 'baddress':x.bus_address, 'burl':x.bus_url, 'bcats':x.bus_categories, 'key':x.key.urlsafe()} for x in db_models.business.query().order(db_models.business.bus_name).fetch()]
				self.render('business.html', self.template_values)
				
				#	business did not exist									
			else:
				self.response.write("Business not found")
		
		elif action == 'add_page':
			self.template_values['Cats'] = [{'name':x.category_name} for x in db_models.recycle_category.query().order(db_models.recycle_category.category_name).fetch()]
			self.render('add_business.html', self.template_values)

		elif action == 'add_business':
			if self.request.get('bus_name'):
				bus_name = self.request.get('bus_name')
				
				# Retrieve business entity
				q = db_models.business.query()
				q = q.filter(db_models.business.bus_name == bus_name)
				keys = q.fetch(keys_only=True)
				if (keys):
									#	Item exists do not create a duplicate.
					self.template_values['error'] = "The Business already exists"
					self.render('add_business.html', self.template_values)
				else:
									#	Item does not exist. Add it.
					parent_key = ndb.Key(db_models.business, "base-business")
					new_bus = db_models.business(parent=parent_key)
					new_bus.bus_name = bus_name
				# If business exists, add new data, update database, and print success

					if self.request.get('bus_phone'):
						new_bus.bus_phone = self.request.get('bus_phone')
					else:
						new_bus.bus_phone = ""

					if self.request.get('bus_hours'):
						new_bus.bus_hours = self.request.get('bus_hours')
					else:
						new_bus.bus_hours = ""

					if self.request.get('bus_days'):
						new_bus.bus_days = self.request.get('bus_days')
					else:
						new_bus.bus_days = ""

					if self.request.get('bus_address'):
						business_address = self.request.get('bus_address')
						
						#	setup business address for Google Geocoding request. " " must be "+"
						url_address = urllib.quote_plus(business_address)
						#	Create url string
						url_http_string = "https://maps.googleapis.com/maps/api/geocode/json?address="
						google_API_key = "&key=AIzaSyAnYYjW2ezjaQnSIyyVtEcC4sgmCTRr1l4"
						combined_url_string = url_http_string + url_address + google_API_key

						#	Make Google geocode request
						result = json.load(urllib.urlopen(combined_url_string))
							
						#	If correct Google should have only returned one item. Count to verify
						count = 0
						for s in result['results']:
							count = count + 1
						
						#	Only one result was returned from Google 
						#	lat and long and address it to the database 
						if count == 1:
							#	Parse the string to get lat and long out. 
							bus_lat = json.dumps([s['geometry']['location']['lat'] for s in result['results']], indent=2)
							bus_long = json.dumps([s['geometry']['location']['lng'] for s in result['results']], indent=2)
							#	Remove the []'s and " "
							formatted_bus_lat = bus_lat.translate(None,"[] ")
							formatted_bus_long = bus_long.translate(None,"[] ")
						
							#	Commit business address to datastore. 
							new_bus.bus_address = business_address
							new_bus.bus_lat = formatted_bus_lat
							new_bus.bus_long = formatted_bus_long
						else:
							self.template_values['Geo_error'] = "Geocoding returned multiple addresses. Please manually verify"
							new_bus.bus_address = business_address
					else:
						new_bus.bus_address = ""

					if self.request.get('bus_lat'):
						new_bus.bus_lat = self.request.get('bus_lat')

					if self.request.get('bus_long'):
						new_bus.bus_long = self.request.get('bus_long')
					
					categories = []
					categories = self.request.get_all('categories')

					if self.request.get('bus_url'):
						business_url_test = self.request.get('bus_url')
						parsed_url = urlparse(business_url_test)
						if ((parsed_url.scheme == "http") or (parsed_url.scheme == "https")) and (parsed_url.netloc != ""):
							new_bus.bus_url = business_url_test
						elif ((business_url_test == "n/a") or (business_url_test == " ") or (business_url_test == "")):
							new_bus.bus_url = business_url_test
						else:
							new_bus.bus_url = business_url_test
							self.template_values['url_error'] = "If entering a URL, please include http://"
							self.template_values['MyCats'] = categories
							self.template_values['Cats'] = [{'name':x.category_name} for x in db_models.recycle_category.query().order(db_models.recycle_category.category_name).fetch()]
							self.template_values['Business'] = new_bus
							self.render('add_business.html', self.template_values)
							return

					else:
						new_bus.bus_url = ""	
					new_bus.put()


					
					#self.template_values['message'] = categories
					for b in categories:
						category_key_get = db_models.recycle_category.query(db_models.recycle_category.category_name == b).get()
						category_key = category_key_get.key.id()

						bus_key = new_bus.key.id()
						bus_key_to_add = ndb.Key(db_models.business, "base-business", db_models.business, int(bus_key))
						category_key_to_add = ndb.Key(db_models.recycle_category, "base-category", db_models.recycle_category, int(category_key))

						if bus_key_to_add not in category_key_get.bus_cat_link:
							category_key_get.bus_cat_link.append(bus_key_to_add)
							category_key_get.put()
							new_bus.bus_categories.append(category_key_to_add)
							new_bus.put()


					self.template_values['MyCats'] = categories
					self.template_values['Cats'] = [{'name':x.category_name} for x in db_models.recycle_category.query().order(db_models.recycle_category.category_name).fetch()]
					self.template_values['special_message'] = "Successfully Added Business"
					self.template_values['Business'] = new_bus
					self.render('edit_business.html', self.template_values)
					
			else:
				self.template_values['Cats'] = [{'name':x.category_name} for x in db_models.recycle_category.query().order(db_models.recycle_category.category_name).fetch()]
				self.template_values['name_error'] = "Business Name is Required"
				self.render('add_business.html', self.template_values)

		else:
			self.template_values['error'] = 'Action ' + action + ' is unknown'
			self.template_values['Businesses'] = [{'url_bname': (urllib.quote_plus(x.bus_name).replace('%2F', '%252F')),'bname':x.bus_name, 'bphone':x.bus_phone, 'bhours':x.bus_hours, 'bdays':x.bus_days, 'baddress':x.bus_address, 'burl':x.bus_url, 'bcats':x.bus_categories, 'key':x.key.urlsafe()} for x in db_models.business.query().order(db_models.business.bus_name).fetch()]
			self.render('business.html', self.template_values)