# Implemented from http://www.thirumal.in/2012/04/sessions-in-google-app-engine-python.html
import webapp2
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

class BaseSessionHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)

        try:
            webapp2.RequestHandler.dispatch(self)
			
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()


