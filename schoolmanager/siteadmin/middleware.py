from django.conf import settings
from django.http import HttpResponseRedirect

# Force user to be a superuser or staff
class AdminRequiredMiddleware():
	def process_request(self, request):
		if not request.path.startswith("/siteadmin/"):
			return None
	
		if request.path == settings.LOGIN_URL:
			return None
	
		if request.user.is_superuser or request.user.is_staff:
			return None
				
		return HttpResponseRedirect(settings.LOGIN_URL + "?next=%s" % request.path)