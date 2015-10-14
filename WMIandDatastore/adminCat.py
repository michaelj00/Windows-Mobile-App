import webapp2
from webapp2_extras import sessions
from google.appengine.ext import ndb
import db_models
import base
import os
import jinja2
import json
from urlparse import urlparse
import urllib
import urllib2
'''
	Group 1
	Michael Jones
	Peter Friedrichsen
	David Crisman
	
	Project CS419
'''
'''
	Changes Michael Jones
	line 33   url_name added to rCat class. 
	line 248 Categories declared before if. 
	line 61 get name un_url encoding. 
	lines 95-98 url_name added to page/356 added business list to add category page/358 add_category.html
'''
class rCat:
	name = 'nothing'
	items = []
	businesses = []
	url_name = 'nothing'

class Category(base.MainPage):	
	
	def __init__(self, request, response):
		self.initialize(request, response)
		self.template_values = {}


	def getBusinesses(self):

		businesses = []
		x = db_models.business.query().order(db_models.business.bus_name).fetch()
		for y in x:
			businesses.append(y.bus_name)
		businesses.sort()
		return businesses


	def render(self, page, variables):
		base.MainPage.render(self, page, variables)	
		
	def get(self, **kwargs):
		if self.session.get('authorized') != 1:
			self.template_values['error'] = "Please log in"
			self.render('login.html', self.template_values)
			return

		if "name" in kwargs:
			# If category name provided, return category information
			url_name = kwargs['name']
			
				#	un_urlencode the name sent in the string
			un_url = urllib.unquote_plus(url_name.encode('ascii')).decode('utf-8')
			
			q = db_models.recycle_category.query()
			q = q.filter(db_models.recycle_category.category_name == un_url)
			keys = q.fetch()

			if (keys):
				x = keys[0]
				items = []
				buss = []
				for b in x.bus_cat_link:
					something = b.get()
					buss.append(something.bus_name)
				for i in x.items:
					items.append(i)
				items.sort()
				self.template_values['MyItems'] = items
				self.template_values['MyBusinesses'] = buss
				self.template_values['Businesses'] = self.getBusinesses()
				self.template_values['Category'] = keys[0]
				self.render('edit_category.html', self.template_values)	
			else:
				self.template_values['error'] = "That category was not found"
			
		else: 
			k = db_models.recycle_category.query().order(db_models.recycle_category.category_name).fetch()
			Categories = []
			if (k):
				for l in k:
					buss = []
					cat = rCat()
					for m in l.bus_cat_link:
						something = m.get()
						buss.append(something.bus_name)
					new_urlname_string = l.category_name
					url_text = urllib.quote_plus(new_urlname_string.encode('utf-8'))
						#	Google App Engine does not like %2F encode it as %252F
					cat.url_name = url_text.replace('%2F', '%252F')
					cat.name = l.category_name
					cat.items = l.items
					cat.businesses = buss
					# = [{'name':l.category_name, 'items':l.items, 'businesses':buss}]
					Categories.append(cat)
					#self.response.write(cat.name, cat.items, cat.businesses)
			#Categories.items.sort()
			#self.response.write(Categories)
			self.template_values['Categories'] = Categories
			self.render('category.html', self.template_values)

	def post(self):
		if self.session.get('authorized') != 1:
			self.template_values['error'] = "Please log in"
			self.render('login.html', self.template_values)
			return
		
		action = self.request.get('action')
		if action == 'update_category':
			if self.request.get('category_name'):
				category_name = self.request.get('category_name')
				
				# Retrieve business entity
				q = db_models.recycle_category.query()
				q = q.filter(db_models.recycle_category.category_name == category_name)
				keys = q.fetch(keys_only=True)

				# If category exists, add new data, update database, and print success
				if (keys):
				
					category = keys[0].get()
					
					#Update the Items Array
					chosen_items = []
					for g in self.request.get_all('items'):
						chosen_items.append(g)
					chosen_items = self.request.get_all('items')
					category.items = chosen_items

					if self.request.get('new_item'):
						category.items.append(self.request.get('new_item'))
					category.items.sort()
					category.put()
					'''for i in category.items:
						if i not in chosen_items:
							category.items.remove(i)
							category.put()
						else:

							category.put()
					'''
					chosen_businesses = []
					chosen_businesses = self.request.get_all('businesses')

					#Prepare an array with all the businesses.  This will be used to create the complement of the selected businesses as well as to pass as a template value to the HTML file.
					
					all_bus = []
					p = db_models.business.query().fetch()
					for d in p:
						all_bus.append(d.bus_name) 

					#This will store the complement of the selected businesses.  We need this to make sure and remove any previous linked business-category pairs that are now 'unlinked.'
					remove_bus = []
					for c in all_bus:
						if c not in chosen_businesses:
							remove_bus.append(c)

					#Add the selected businesses to the database in both the business section and the category section.
					for b in chosen_businesses:
						bus_key_get = db_models.business.query(db_models.business.bus_name == b).get()
						bus_key = bus_key_get.key.id()

						category_key = category.key.id()

						bus_key_to_update = ndb.Key(db_models.business, "base-business", db_models.business, int(bus_key))
						category_key_to_update = ndb.Key(db_models.recycle_category, "base-category", db_models.recycle_category, int(category_key))

						if bus_key_to_update not in category.bus_cat_link:
							category.bus_cat_link.append(bus_key_to_update)
							category.put()
							bus_key_get.bus_categories.append(category_key_to_update)
							bus_key_get.put()

					for r in remove_bus:
						business_key_get = db_models.business.query(db_models.business.bus_name == r).fetch(1, keys_only=True)[0]
						business_to_remove = business_key_get.get()
						cat_key = keys[0]

						if cat_key in business_to_remove.bus_categories:
							business_to_remove.bus_categories.remove(cat_key)
							business_to_remove.put()
							category.bus_cat_link.remove(business_key_get)
							category.put()

					buss = []
					for b in category.bus_cat_link:
						something = b.get()
						buss.append(something.bus_name)
					self.template_values['MyItems'] = category.items
					self.template_values['MyBusinesses'] = buss
					self.template_values['Businesses'] = self.getBusinesses()
					self.template_values['special_message'] = "Update Successful"
					self.template_values['Category'] = category
					self.render('edit_category.html', self.template_values)

				# If category doesn't exist, print error and exit
				else:
					self.template_values['error'] = "Error: Category not found"
					
			else:
				self.response.write("You did not enter a Category name to update")
		
		elif action == 'delete_category':
			category_name = self.request.get('category_name')
			q = db_models.recycle_category.query()
			q = q.filter(db_models.recycle_category.category_name == category_name)
			keys = q.fetch()
			if (keys):
				self.template_values['Category'] = keys[0]
				self.render('delete_category.html', self.template_values)	
			else:
				self.template_values['error'] = "That business was not found"

		elif action == 'sure_delete':
			category_name = self.request.get('category_name')
									#	Make sure category exists in datastore.
			q = db_models.recycle_category.query()
			q = q.filter(db_models.recycle_category.category_name == category_name)
			keys = q.fetch(keys_only=True)
						
			# 	if exists start delete process
			if keys:

				#	Get the category key to delete
				cat_key_get = db_models.recycle_category.query(db_models.recycle_category.category_name == category_name).fetch(1, keys_only= True)[0]
									
				#	Search business where recycle_category is linked to it.
				q = db_models.business.query()
				q = q.filter(db_models.business.bus_categories == cat_key_get)
				result_of_fetch = q.fetch()
				
				#	For each item in the list remove the link to the business.
				for x in result_of_fetch:
					x.bus_categories.remove(cat_key_get)
					x.put()
				
				#self.response.write("Removed references to business in categories")
				
				#	Delete category from datastore
				category_key_get = db_models.recycle_category.query(db_models.recycle_category.category_name == category_name).get()
			
				category_key_get.key.delete()		
				self.template_values['special_message'] = category_name + " Deleted."
				k = db_models.recycle_category.query().order(db_models.recycle_category.category_name).fetch()
				Categories = []
				if (k):
					for l in k:
						buss = []
						cat = rCat()
						for m in l.bus_cat_link:
							something = m.get()
							buss.append(something.bus_name)
						new_urlname_string = l.category_name
						url_text = urllib.quote_plus(new_urlname_string.encode('utf-8'))
						#	Google App Engine does not like %2F encode it as %252F
						cat.url_name = url_text.replace('%2F', '%252F')
						cat.name = l.category_name
						cat.items = l.items
						cat.businesses = buss
						# = [{'name':l.category_name, 'items':l.items, 'businesses':buss}]
						Categories.append(cat)
					#self.response.write(cat.name, cat.items, cat.businesses)
					#Categories.items.sort()
					#self.response.write(Categories)
				self.template_values['Categories'] = Categories
				self.render('category.html', self.template_values)
				
				#	business did not exist									
			else:
				self.response.write("Business not found")
		
		elif action == 'add_page':
			self.template_values['Businesses'] = self.getBusinesses()
			self.render('add_category.html', self.template_values)
		
		elif action == 'log_out':
			self.session.clear()
			self.template_values['message'] = 'Logged out'
			self.render('login.html')
			
		elif action == 'add_category':
			if self.request.get('category_name'):
				category_name = self.request.get('category_name')
				
				# Retrieve business entity
				q = db_models.recycle_category.query()
				q = q.filter(db_models.recycle_category.category_name == category_name)
				keys = q.fetch(keys_only=True)

				if (keys):
					#	Item exists do not create a duplicate.
					self.template_values['error'] = "The Category already exists"
				else:
					#	Item does not exist. Add it.
					parent_key = ndb.Key(db_models.recycle_category, "base-category")
					new_category = db_models.recycle_category(parent = parent_key)
					new_category.category_name = category_name

					
					if self.request.get('new_item1'):
						new_category.items.append(self.request.get('new_item1'))
						
					if self.request.get('new_item2'):
						new_category.items.append(self.request.get('new_item2'))
						
					if self.request.get('new_item3'):
						new_category.items.append(self.request.get('new_item3'))
						
					if self.request.get('new_item4'):
						new_category.items.append(self.request.get('new_item4'))
							
					new_category.put()


					businesses = []
					businesses = self.request.get_all('businesses')
					#self.template_values['message'] = categories
					for b in businesses:
						bus_key_get = db_models.business.query(db_models.business.bus_name == b).get()
						bus_key = bus_key_get.key.id()

						category_key = new_category.key.id()

						bus_key_to_add = ndb.Key(db_models.business, "base-business", db_models.business, int(bus_key))
						category_key_to_add = ndb.Key(db_models.recycle_category, "base-category", db_models.recycle_category, int(category_key))

						if bus_key_to_add not in new_category.bus_cat_link:
							new_category.bus_cat_link.append(bus_key_to_add)
							new_category.put()
							bus_key_get.bus_categories.append(category_key_to_add)
							bus_key_get.put()						

					new_category.items.sort()					
					buss = []
					for b in new_category.bus_cat_link:
						something = b.get()
						buss.append(something.bus_name)
					self.template_values['MyItems'] = new_category.items
					self.template_values['MyBusinesses'] = buss
					self.template_values['Businesses'] = self.getBusinesses()
					self.template_values['special_message'] = "Added Successfully"
					self.template_values['Category'] = new_category
					self.render('edit_category.html', self.template_values)
					
			else:
				self.template_values['Businesses'] = self.getBusinesses()
				self.template_values['name_error'] = "Category Name is Required"
				self.render('add_category.html', self.template_values)

		else:
			self.template_values['error'] = 'Action ' + action + ' is unknown'
			k = db_models.recycle_category.query().order(db_models.recycle_category.category_name).fetch()
			Categories = []
			if (k):
				for l in k:
					buss = []
					cat = rCat()
					for m in l.bus_cat_link:
						something = m.get()
						buss.append(something.bus_name)
					new_urlname_string = l.category_name
					url_text = urllib.quote_plus(new_urlname_string.encode('utf-8'))
						#	Google App Engine does not like %2F encode it as %252F
					cat.url_name = url_text.replace('%2F', '%252F')
					cat.name = l.category_name
					cat.items = l.items
					cat.businesses = buss
					# = [{'name':l.category_name, 'items':l.items, 'businesses':buss}]
					Categories.append(cat)
					#self.response.write(cat.name, cat.items, cat.businesses)
			#Categories.items.sort()
			#self.response.write(Categories)
			self.template_values['Categories'] = Categories
			self.render('category.html', self.template_values)