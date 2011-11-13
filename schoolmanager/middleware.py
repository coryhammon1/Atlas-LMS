from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template import RequestContext, loader
from django.core.cache import cache
from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser

import traceback

from schoolmanager.settings import MEDIA_URL, LOGIN_URL, MIDDLEWARE_EXCLUDED_URLS

# Forces the user to be authenticated
class LoginRequiredMiddleware():
	def process_request(self, request):
		if request.path == LOGIN_URL:
			return None
				
		for url in MIDDLEWARE_EXCLUDED_URLS:
			if request.path.startswith(url):
				return None
	
		if request.user.is_authenticated():
			return None
		
		return HttpResponseRedirect(LOGIN_URL + "?next=%s" % request.path)
		
class Forbidden403Middleware():
	def process_response(self, request, response):
		if isinstance(response, HttpResponseForbidden):
			template = loader.get_template("403.html")
			return HttpResponseForbidden(template.render(RequestContext(request)))
		else:
			return response
			
class CacheAuthenticationMiddleware(object):
	def process_request(self, request):
		assert hasattr(request, 'session'), "Cache authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
				
		try:
			cache_key = "User-" + str(request.session["_auth_user_id"])
			request.__class__.user = cache.get(cache_key)
			if request.__class__.user == None:
				user = get_user(request)
				cache.set(cache_key, user, 5*60)
				request.__class__.user = user
				
		except KeyError:
			request.__class__.user = AnonymousUser()
			
		