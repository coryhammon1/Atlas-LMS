try:
	from functools import update_wrapper, wraps
except ImportError:
	from django.utils.functional import update_wrapper, wraps
	
from django.http import HttpResponseForbidden

# Required the user to be a superuser or staff
def superuser_or_staff_required(function=None):
	def decorator(view_func):
		def _wrapped_view(request, *args, **kwargs):
			if request.is_superuser or request.is_staff:
				return view_func(request, *args, **kwargs)
			return HttpResponseForbidden()
		return wraps(view_func)(_wrapped_view)
	return decorator