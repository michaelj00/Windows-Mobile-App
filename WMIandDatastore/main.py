import webapp2
from webapp2_extras import sessions
import session_module
from google.appengine.api import oauth

'''
	Group 1
	Michael Jones
	Peter Friedrichsen
	David Crisman
	
	Project CS419
'''

app = webapp2.WSGIApplication([ ('/', 'auth.Admin'),], config = session_module.myconfig_dict, debug = True)
app.router.add(webapp2.Route(r'/v.1.0/categories', 'categories.Categories'))
app.router.add(webapp2.Route(r'/v.1.0/categories/<name:[^/]+>', 'categories.Categories'))
app.router.add(webapp2.Route(r'/v.1.0/business/<name:[^/]+>', 'business.Business'))
app.router.add(webapp2.Route(r'/v.1.0/business', 'business.Business'))
app.router.add(webapp2.Route(r'/v.1.0/auth', 'auth.Admin'))
app.router.add(webapp2.Route(r'/v.1.0/list_business', 'adminBus.Business'))
app.router.add(webapp2.Route(r'/v.1.0/list_business/<name:[^/]+>', 'adminBus.Business'))
app.router.add(webapp2.Route(r'/v.1.0/list_category', 'adminCat.Category'))
app.router.add(webapp2.Route(r'/v.1.0/list_category/<name:[^/]+>', 'adminCat.Category'))

