import re
import datetime
import pickle

from urllib import unquote

from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from schoolmanager.courses.models import Course

# retrieves users's current courses
class CurrentCoursesMiddleware():
	def process_request(self, request):
		for excluded_url in settings.MIDDLEWARE_EXCLUDED_URLS:
			if request.path.startswith(excluded_url):
				return None
				
		courses = []
		if not request.user.is_anonymous():
			cache_key = "CurrentCourses-%d" % request.user.id
			courses = cache.get(cache_key)
			if courses == None:
				#courses within the current semester
				courses_query = request.user.courses.select_related() \
													.filter(term__start__lte=datetime.datetime.now(), term__end__gte=datetime.datetime.now()) \
													.order_by("department__name", "number", "section")
				
				courses = list(courses_query)
				cache.add(cache_key, courses) #hold for 5 minutes
			
		request.user.current_courses = courses
		request.course = None
				
		return None

# Only allows verified users to access course
class CourseAccessMiddleware():
	def process_request(self, request):
		if request.path.rfind("/courses/") == -1: #path does not direct to the courses app
			return None
		
		if request.path.startswith("/admin/"):
			return None
		
		if request.path.startswith("/siteadmin/"):
			return None
		
		#get course title
		expression = re.compile(r'/courses/(?P<course_identifier>\w*)/?') # match the course name
		match = expression.search(request.path)
		
		course_identifier = match.group("course_identifier")
					
		if course_identifier == "":
			return None
		
		expression = re.compile(r'(?P<department>[a-zA-Z]+)(?P<number>\d+)S(?P<section>\d*)(?P<term>[a-zA-Z]+)(?P<year>\d+)')
		match = expression.search(course_identifier)
		
		course_department = match.group("department")
		course_number = match.group("number")
		course_section = match.group("section")
		if course_section == "":
			course_section = None
		else:
			course_section = int(course_section)
		
		term_name = match.group("term")
		term_year = match.group("year")
		
		request.course = None
		
		try:
			for course in request.user.current_courses:
				if course.number == int(course_number) and course.section == course_section and course.department.name == course_department and course.term.name == term_name and course.term.start.year == int(term_year):
					request.course = course	
					break
								
		except Course.DoesNotExist:
			pass
		except AttributeError:
			pass
			
			
		if request.course == None: #if course is not in current courses
			#check all registered classes
			try:
				request.course = request.user.courses.get(number=course_number, section=course_section,
									department__name=course_department, term__name=term_name, term__start__year=term_year)
			except Course.DoesNotExist:
				pass
			
		
		if request.course: #course was found
			return None
		else:			#course was not found
			return HttpResponseForbidden()
	


	