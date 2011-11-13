import re

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseForbidden

from schoolmanager.assignments.models import Assignment

def _get_assignment(assignment_id):
	try:
		assignment = Assignment.objects.select_related("user", "course", "course__term", "course__department").get(id=assignment_id)
	except Assignment.DoesNotExist:
		raise Http404
		
	return assignment

class CurrentAssignmentMiddleware():
	def process_view(self, request, view_func, view_args, view_kwargs):
		if view_kwargs.has_key('assignment_id'):			#instructor view
			assignment_id = view_kwargs['assignment_id']
			cache_key = "Assignment-%s" % assignment_id
			assignment = cache.get(cache_key)
			if assignment is None:
				assignment = _get_assignment(assignment_id)
				cache.add(cache_key, assignment)
				
			request.assignment = assignment
			
		elif view_kwargs.has_key('assignment_name'):		#student view
			assignment_name = view_kwargs['assignment_name']
			cache_key = "Course-%d-Assignment-%s" % (request.course.id, assignment_name)
			
			assignment_id = cache.get(cache_key)
			if assignment_id is None:
				assignment_name = assignment_name.replace("_", " ")
				try:
					assignment = Assignment.objects.select_related("user", "course", "course__term", "course__department").get(course=request.course, name=assignment_name)
				except Assignment.DoesNotExist:
					raise Http404
				cache.add(cache_key, str(assignment.id))
				
				id_cache_key = "Assignment-%d" % assignment.id
				
				cache.add(id_cache_key, assignment)
			else:
				id_cache_key = "Assignment-%s" % assignment_id
				assignment = cache.get(id_cache_key)
				if assignment is None:
					assignment = _get_assignment(assignment_id)
					cache.add(id_cache_key, assignment)
			
			if assignment.is_viewable or request.user.is_superuser or request.user.is_staff:
				request.assignment = assignment
			else:
				return HttpResponseForbidden()
			
