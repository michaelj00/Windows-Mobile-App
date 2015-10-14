from google.appengine.ext import ndb
'''
	Group 1
	Michael Jones
	Peter Friedrichsen
	David Crisman
	
	Project CS419
'''

class Model(ndb.Model):
	def to_dict(self):
		d= super(Model, self).to_dict()
		d['key'] = self.key.id()
		return d

class recycle_category(Model):
	category_name = ndb.StringProperty(required = True)
	bus_cat_link = ndb.KeyProperty(repeated = True)
	items = ndb.StringProperty(repeated=True)
	
	def to_dict(self):
		d = super(recycle_category, self).to_dict()
		d['bus_cat_link'] = [m.id() for m in d['bus_cat_link']]
		return d
	
class business(Model):
	bus_name = ndb.StringProperty(required = True)
	bus_phone = ndb.StringProperty(required = False)
	bus_hours = ndb.StringProperty(required = False)
	bus_days = ndb.StringProperty(required = False) 
		#if we do day of week = Sunday, Monday, Tuesday as a list. 
	bus_address = ndb.StringProperty(required = False)
	bus_url = ndb.StringProperty(required = False)
	bus_categories = ndb.KeyProperty(repeated = True)
	bus_lat = ndb.StringProperty(required = False)
	bus_long = ndb.StringProperty(required = False)
	
	def to_dict(self):
		d = super(business, self).to_dict()
		d['bus_categories'] = [m.id() for m in d['bus_categories']]
		return d

class login(Model):
	user_name = ndb.StringProperty(required = True)
	password = ndb.StringProperty(required = True)