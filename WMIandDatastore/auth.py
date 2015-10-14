import webapp2
from webapp2_extras import sessions
import session_module
from google.appengine.ext import ndb
import db_models
import base
import os
import jinja2
import json

'''
	Group 1
	Michael Jones
	Peter Friedrichsen
	David Crisman
	
	Project CS419
'''

class Admin(base.MainPage):	
	
	def __init__(self, request, response):
		self.initialize(request, response)
		self.template_values = {}


	def render(self, page):
		base.MainPage.render(self, page, self.template_values)	

	def render2(self, page):
		self.template_values['Businesses'] = [{'bname':x.bus_name, 'bphone':x.bus_phone, 'bhours':x.bus_hours, 'bdays':x.bus_days, 'baddress':x.bus_address, 'burl':x.bus_url, 'bcats':x.bus_categories, 'key':x.key.urlsafe()} for x in db_models.business.query().fetch()]
		base.MainPage.render(self, page, self.template_values)
		
	def get(self):
		self.render('login.html')	

	def post(self):
		action = self.request.get('action')

		if action == 'add_user':
			user = db_models.login()
			uName = self.request.get('user_name')
			pWord = self.request.get('password')
			if uName:
				user.user_name = uName
			else:
				self.response.set_status(400, "Invalid POST Request.  Username is Required")
				self.response.write(self.response.status)
				return
			if pWord:
				user.password = pWord
			else:
				self.response.set_status(400, "Invalid POST Request.  Password is Required")
				self.response.write(self.response.status)
				return				
			user.put()
			u = user.to_dict()
			self.response.write(json.dumps(u))
		
		elif action == 'log_out':
			self.session.clear()
			self.template_values['message'] = 'Logged out'
			self.render('login.html')
			
		elif action == 'attempt_login':
			uName = self.request.get('user_name')
			pWord = self.request.get('password')
			valid = 0
			for u in db_models.login.query().fetch():
				if uName == u.user_name:
					if pWord == u.password:
						valid = 1

			if valid == 1:
				self.session['authorized'] = valid
				self.render('landing.html')
			else:
				self.template_values['error'] = 'User Name or Password is incorrect'
				self.render('login.html')
				
		elif action == 'reset_password':
			#email a new password to an admin email on file. Below is a temporary action
			self.render('login.html')

		else:
			self.template_values['error'] = 'Action ' + action + ' is unknown'
			self.render('login.html')