import webapp2
import os
import jinja2
from webapp2_extras import sessions

'''
	Group 1
	Michael Jones
	Peter Friedrichsen
	David Crisman
	
	Project CS419
'''

myconfig_dict = {}
myconfig_dict['webapp2_extras.sessions'] = {
    'secret_key': 'michael-david-peter-are-all-awesome',
}

class MainPage(webapp2.RequestHandler):
	
	@webapp2.cached_property
	def jinja2(self):
		#Read about these properties at http://jinja.pocoo.org/docs/dev/api/
		return jinja2.Environment(
		loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
		extensions = ['jinja2.ext.autoescape'],
		autoescape = True
		)
		
	def render(self, template, template_variables={}):
		template = self.jinja2.get_template(template)
		self.response.write(template.render(template_variables))

	def dispatch(self):
		self.session_store = sessions.get_store(request = self.request)
		
		try:
			webapp2.RequestHandler.dispatch(self)
			
		finally:
			self.session_store.save_sessions(self.response)
			
	@webapp2.cached_property
	def session(self):
		return self.session_store.get_session()