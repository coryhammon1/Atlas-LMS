from __future__ import division

from urllib import quote, unquote

import time
import datetime

import django.utils.simplejson as json

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.db.models import Q
from django.db import connection
from django.db import reset_queries
from django.forms.models import inlineformset_factory
from django import forms
from django.contrib import messages

from schoolmanager.utils import *

from schoolmanager.courses.models import *
from schoolmanager.courses.forms import COURSE_GRADE_LETTER_CHOICES, GradingSchemeForm, GradingForm

from schoolmanager.assignments.models import Assignment, AssignmentSubmission

from schoolmanager.bulletins.models import *
from schoolmanager.bulletins.forms import *

from schoolmanager.notifications.models import Notification

DATE_FORMAT = "%a. %b %d, %Y at %I:%M %p"

JS_DATE_FORMAT = "%c"

#helper
def render_with_context(request, template, context={}):
	return render_to_response(template, context, context_instance=RequestContext(request))

def index(request):
	courses = QueryList(request.user.courses.select_related("term", "department").all().order_by("name"))
	
	terms = list(courses.group_by("term"))
	for term in terms:
		term.course_list = term._object_list
	
	terms.sort(key=lambda term: term.start, reverse=True)
	
	terms_chunked = chunk_list(terms, 4)
	
	cache_key = "CheckFutureCourses-%d" % request.user.id
	checked = cache.add(cache_key, True, 60 * 60 * 24 * 5) #hold for 5 days
	
	return render_with_context(request, "courses/index.html", { 'courses': courses, 'terms_chunked': terms_chunked })

def view_course(request, course_name):	
	return render_with_context(request, "courses/view_course.html", { 'course': request.course })
	
def get_grade(request, course_name):
	percent = request.course.get_grade(request.user)
	
	grading = request.course.get_grading_scheme()
		
	letter_grade = grading.grade_for_percent(percent)
	
	percent = normalized_float(percent)
	
	if request.GET.get("not_ajax"):
		return HttpResponse("<body>Grade</body>")
	return JsonResponse({ 'percent': percent, 'letter_grade': letter_grade })

@user_passes_test(is_superuser_or_staff)
def print_grades(request, course_name):
	grading = request.course.get_grading_scheme()
	
	users = QueryList(request.course.users.all())
	
	students = users.filter(is_staff=False, is_superuser=False)
	instructors = users.exclude(is_staff=False, is_superuser=False)
	
	submissions = QueryList(AssignmentSubmission.objects.filter(assignment__course=request.course))
	
	for student in students:
		student.percent = request.course.get_grade(student, submissions)
		student.grade = grading.grade_for_percent(student.percent)
		
	return render_with_context(request, "courses/print_grades.html", { 'instructors': instructors, 'students': students,
	 																	'course': request.course })
		
		

@user_passes_test(is_superuser_or_staff)
def grades(request, course_name):
	grading = request.course.get_grading_scheme()
	
	grading_scale_form = None
	if request.method == "POST" and request.POST.get("form_name") == "scale":
		grading_scale_form = GradingSchemeForm(instance=grading, data=request.POST)
		if grading_scale_form.is_valid():
			grading_scale_form.save()
			messages.success(request, "Grading Scale changed successfully.")
	else:
		grading_scale_form = GradingSchemeForm(instance=grading)
		
				
	grading_form = None
	if request.method == "POST" and request.POST.get("form_name") == "grading":
		grading_form = GradingForm(request.course, data=request.POST)
		if grading_form.is_valid():
			grading_form.save()
			
			if not request.POST.get("print") is None:
				instructors = request.course.users.exclude(is_staff=False, is_superuser=False)
				students = []
				for field in grading_form:
					try:
						grade = grading_form.cleaned_data[field.name]
					except KeyError:
						grade = "F"

					students.append({ 'name': field.label, 'grade': grade, 'percent': field.percent })
				return render_with_context(request, "courses/print_grades.html", { 'instructors': instructors, 'students': students })
				
			messages.success(request, "Grades were submitted successfully")
	else:
		grading_form = GradingForm(request.course)
	
	return render_with_context(request, "courses/grades.html", { 'course': request.course, 'scale_form': grading_scale_form, 'grading_form': grading_form })

def get_stream(request, course_name):
	latest_date = datetime.datetime.now() - datetime.timedelta(weeks=4)
	
	recent_notifications = request.user.notifications.select_related("assignment", "assignment__user", "bulletin", "bulletin__user").filter(course=request.course, date__gte=latest_date).order_by("-date")[:10]
	
	stream_data = []
	for notification in recent_notifications:
		if notification.bulletin_id != None:
			try:
				bulletin = notification.bulletin
				
				#check if bulletin is already in stream
				bulletin_in_stream = False
				for data in stream_data:
					if data['type'] == "bulletin":
						if data['bulletin']['id'] == bulletin.id: #bulletin is in stream
							bulletin_in_stream = True
							break;
				
				if not bulletin_in_stream:
					stream_data.append({ 'type': "bulletin", 'bulletin': bulletin.get_data_with_comments() })
			except ObjectDoesNotExist:
				pass
		elif notification.assignment_id != None:
			if notification.assignment.is_viewable or request.user.is_superuser or request.user.is_staff:
				stream_data.append({ 'type': "assignment",
									 'text': notification.text,
									 'date': notification.date.strftime(DATE_FORMAT) })
	
	if not request.is_ajax():
		return render_to_response("courses/stream.html", { 'stream': stream_data })
	return JsonResponse(stream_data)
		
		
		
		