import time

import django.utils.simplejson as json

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.template import RequestContext
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Q
from django.utils.dateformat import format

from schoolmanager.utils import *

from schoolmanager.siteadmin.models import ExtendedUser
from schoolmanager.siteadmin.forms import *
from schoolmanager.siteadmin.utils import *

from schoolmanager.courses.models import *
from schoolmanager.courses.forms import *

from schoolmanager.assignments.models import *

def index(request):
	return render_with_context(request, "siteadmin/index.html")

def users(request):
	user_types = ("Administrators", "Instructors", "Students")
		
	form = UserCreationForm()

	return render_with_context(request, "siteadmin/users.html", { 'user_types': user_types, 'form': form })

def add_user(request):
	form = None
	if request.method == "POST":
		form = UserCreationForm(data=request.POST)
		if form.is_valid():
			user = form.save()
			user_data = { 'id': user.id, 'username': user.username, 'first_name': user.first_name, 'last_name': user.last_name }
			
			response_data = { 'success': True, 'user': user_data }
			return JsonResponse(response_data)
		else:
			return JsonResponse(form.compile_errors())
	else:
		return HttpResponse()

def delete_user(request):
	username = request.POST.get('username')
	
	deleted = True
	try:
		user = ExtendedUser.objects.get(username=username)
		user_data = user.to_dict()
		user.delete()
		#backend.delete(user)
	except User.DoesNotExist:
		deleted = False
		user_data = None
	
	return JsonResponse({ 'success': deleted, 'user': user_data })

def search_user(request):
	search_string = request.POST.get('search')
		
	users = []
	if search_string:
		users = ExtendedUser.objects.filter(Q(last_name__icontains=search_string)|Q(first_name__icontains=search_string)|Q(username__icontains=search_string))
		#backend.contains(search_string)
		
	user_data = { 'Administrators': [], 'Instructors': [], 'Students': [] }
	for user in users:
		type = get_user_type(user)
		user_list = user_data[type]
		user_list.append(user.to_dict())
	
	if not user_data['Administrators'] and not user_data['Instructors'] and not user_data['Students']:
		user_data = None
	
	response_data = { 'success': True, 'users': user_data }
	return JsonResponse(response_data)

def partial_user_list(request):
	letter = request.GET.get('letter')
		
	type = request.GET.get('type').lower()
	type_filter = None
	if type == "administrators":
		type_filter = Q(is_superuser=True)
	elif type == "instructors":
		type_filter = Q(is_staff=True)
	else:
		type_filter = Q(is_staff=False, is_superuser=False)
	
	users = ExtendedUser.objects.filter(type_filter, last_name__istartswith=letter).order_by("last_name", "first_name")
	#backend.startingwith(letter, type)
	
	user_data = []
	for user in users:
		user_data.append(user.to_dict())
		
	response_data = { 'success': True, 'users': user_data }
	return JsonResponse(response_data)

def view_user(request, user_id):
	user = get_object_or_404(User, id=user_id)
	#backend.get(username)
	
	user_courses = user.courses.select_related("term", "department").all().order_by("-term__start", "department__name", "number")
	course_terms = {}
	for course in user_courses:
		if not course.term.id in course_terms:
			term = course.term
			term.course_list = [course]
			course_terms.update({ term.id: term })
		else:
			term = course_terms[term.id]
			term.course_list.append(course)
			
	terms = Term.objects.exclude(end__lt=datetime.datetime.now()).exclude(id__in=[id for id, term in course_terms.items()])
	
	terms = list(terms) + course_terms.values()
	terms.sort(key=lambda term: term.start, reverse=True)
	
	departments = Department.objects.all().order_by("name")
	
	form = None
	if request.method == "POST":
		form = ChangeUserForm(instance=user, data=request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, "'%s' was updated successfully." % user.get_full_name())
	else:
		form = ChangeUserForm(instance=user)
	
	return render_with_context(request, "siteadmin/view_user.html", { 'vuser': user, 'departments': departments,
																	   'form': form, 'terms': terms })

def enroll_user_in_course(request, user_id):
	user = get_object_or_404(User, id=user_id)
	#backend.get(username)
	
	course_id = request.POST.get('course_id')
	
	enrolled = True
	try:
		course = Course.objects.get(id=course_id)
		user.courses.add(course)
		cache.delete("CurrentCourses-%d" % user.id)
	except Course.DoesNotExist:
		enrolled = False
		course = None
		
	if course:
		course_data = { 'id': course.id, 'name': course.shortname(), 'department': course.department.name }
	else:
		course_data = None
	
	return JsonResponse({ 'success': enrolled, 'course': course_data })

def remove_course_from_user(request, user_id):
	user = get_object_or_404(User, id=user_id)
	#backend.get(username)
	
	course_id = request.POST.get('course_id')
	
	removed = True
	try:
		course = user.courses.get(id=course_id)
		user.courses.remove(course)
		cache.delete("CurrentCourses-%d" % user.id)
	except Course.DoesNotExist:
		removed = False
		course = None
		
	if course:
		course_data = { 'id': course.id, 'name': course.shortname(), 'department': course.department.name }
	else:
		course_data = None
		
	return JsonResponse({ 'success': removed, 'course': course_data })

def add_term(request):
	form = None
	if request.method == "POST":
		form = TermForm(data=request.POST)
		if form.is_valid():
			term = form.save()
			
			term_data = { 'id': term.id }
			term_data.update({ 'start': format(term.start, "m/d/Y"), 'end': format(term.end, "m/d/Y") })	
			term_data.update({ 'name': term.__unicode__() })
			
			response_data = { 'success': True, 'term': term_data }
			return JsonResponse(response_data)
		else:
			return JsonResponse(form.compile_errors())
	else:
		form = TermForm()
		
	return render_with_context(request, "siteadmin/add_term.html", { 'form': form })

def delete_term(request):
	term_id = request.POST.get("id")
		
	deleted = True
	try:
		term = Term.objects.get(id=term_id)
		users = list(User.objects.filter(courses__term=term))
		term.delete()
						
		cache.delete_many(["PreviousCourseSelection-%d" % request.user.id] + ["CurrentCourses-%d" % user.id for user in users])
	except Term.DoesNotExist:
		deleted = False
	
	return JsonResponse({ 'success': deleted })

def change_term(request, term_id):
	term = get_object_or_404(Term, id=term_id)
	
	form = None
	if request.method == "POST":
		form = TermForm(data=request.POST, instance=term)
		if form.is_valid():
			term = form.save()
			term_data = { 'id': term.id, 'name': term.name,
						  'start': format(term.start, "m/d/Y"),
						  'end': format(term.end, "m/d/Y") }
			
			response_data = { 'success': True, 'term': term_data }
			return JsonResponse(response_data)
		else:
			return JsonResponse(form.compile_errors())
	else:
		form = TermForm(instance=term)
	
	return render_to_response("siteadmin/term_form.html", { 'form': form })

def add_department(request):
	form = None
	if request.method == "POST":
		form = DepartmentForm(data=request.POST)
		if form.is_valid():
			department = form.save()
						
			response_data = { 'success': True, 'department': department.to_dict() }
			return JsonResponse(response_data)
		else:
			return JsonResponse(form.compile_errors())
	
	return HttpResponse()

def change_department(request, department_id):
	department = get_object_or_404(Department, id=department_id)
	
	form = None
	if request.method == "POST":
		form = DepartmentForm(data=request.POST, instance=department)
		if form.is_valid():
			new_department = form.save()
			response_data = { 'success': True, 'department': new_department.to_dict() }
			return JsonResponse(response_data)
		else:
			return JsonResponse(form.compile_errors())
	else:
		return HttpResponse("")

def delete_department(request):
	department_id = request.POST.get("id")
	
	deleted = True
	try:
		department = Department.objects.get(id=department_id)
		users = list(User.objects.filter(courses__department=department))
		
		department.delete()
		
		cache.delete_many(["PreviousCourseSelection-%d" % request.user.id] + ["CurrentCourses-%d" % user.id for user in users])
		
	except Department.DoesNotExist:
		deleted = False
	
	return JsonResponse({ 'success': deleted })

def view_courses(request):
	terms = Term.objects.order_by("-start")
	departments = Department.objects.order_by("name")
	
	term_form = TermForm(auto_id=False)
	department_form = DepartmentForm()
	course_form = CourseForm()
	
	return render_with_context(request, "siteadmin/courses.html", { 'terms': terms, 'departments': departments,
																	'term_form': term_form,
																	'department_form': department_form,
																	'course_form': course_form })

def add_course(request):
	form = None
	if request.method == "POST":
		form = CourseForm(data=request.POST)
		if form.is_valid():
			course = form.save()
			
			#add default groups
			course.groups.create(name="Homework")
			course.groups.create(name="Tests")
			course.groups.create(name="Quizzes")
			
			course_data = { 'id': course.id, 'name': course.shortname(), 'number': course.number }
			
			response_data = { 'success': True, 'course': course_data }
			return JsonResponse(response_data)
		else:
			return JsonResponse(form.compile_errors())
	else:
		return HttpResponse()
	
def view_course(request, course_id):
	try:
		course = Course.objects.select_related("department", "term", "grades").get(id=course_id)
	except Course.DoesNotExist:
		raise Http404
	
	course_users = QueryList(course.users.all().order_by("is_staff", "last_name", "first_name"))
	
	course.students = course_users.filter(is_staff=False, is_superuser=False)
	course.instructors = course_users.exclude(is_staff=False)
	
	submissions = QueryList(AssignmentSubmission.objects.filter(assignment__course=course))
	scheme = course.get_grading_scheme()
	
	for student in course.students:
		student.grade = scheme.grade_for_percent(course.get_grade(student, submissions))
	
	form = None
	if request.method == "POST":
		form = UpdateCourseForm(instance=course, data=request.POST)
		print form.is_valid()
		if form.is_valid():
			form.save()
						
			#nuke caches of users in this course
			cache.delete_many(["CurrentCourses-%d" % user.id for user in course_users])
			
			messages.success(request, "'%s' was updated successfully." % course.shortname())
						
			if request.user in course_users:
				return HttpResponseRedirect(".")
	else:
		form = UpdateCourseForm(instance=course)
	
	return render_with_context(request, "siteadmin/course.html", { 'course': course, 'form': form })

def delete_course(request):
	course_id = request.POST.get('id')
		
	deleted = True
	try:
		course = Course.objects.get(id=course_id)
		course_users = course.users.all()
		
		cache.delete_many(["CurrentCourses-%d" % user.id for user in course_users])
		
		course.delete()
	except Course.DoesNotExist:
		deleted = False
	
	return JsonResponse({ 'success': deleted })

def add_user_to_course(request, course_id):
	course = get_object_or_404(Course, id=course_id)
	
	username = request.POST.get('username')
	
	added = True
	try:
		user = ExtendedUser.objects.get(username=username)
		course.users.add(user)
		
		cache.delete("CurrentCourses-%d" % user.id)
	except User.DoesNotExist:
		added = False
		user = None
		
	if user:
		user_data = user.to_dict()
	else:
		user_data = None
	
	return JsonResponse({ 'success': added, 'user': user_data })

def remove_user_from_course(request, course_id):
	course = get_object_or_404(Course, id=course_id)
	
	username = request.POST.get('username')
	
	removed = True
	try:
		user = course.users.get(username=username)
		course.users.remove(user)
		
		cache.delete("CurrentCourses-%d" % user.id)
	except User.DoesNotExist:
		removed = False
		user = None
		
	if user:
		user_data = { 'id': user.id, 'last_name': user.last_name,
					  'first_name': user.first_name,
					  'username': user.username }
	else:
		user_data = None
		
	return JsonResponse({ 'success': removed, 'user': user_data })

def print_course_grades(request, course_id):	
	try:
		course = Course.objects.select_related("department", "term", "grades").get(id=course_id)
	except Course.DoesNotExist:
		raise Http404
	
	grading = course.get_grading_scheme()
	
	users = QueryList(course.users.all())
	
	students = users.filter(is_staff=False, is_superuser=False)
	instructors = users.exclude(is_staff=False, is_superuser=False)
	
	submissions = QueryList(AssignmentSubmission.objects.select_related("assignment").filter(assignment__course=course))
	
	for student in students:
		student.percent = course.get_grade(student, submissions)
		student.grade = grading.grade_for_percent(student.percent)
		
	return render_with_context(request, "courses/print_grades.html", { 'course': course, 'instructors': instructors,
																	   'students': students })

def partial_course_list(request):
	term = request.GET.get('term')
	department = request.GET.get('department')
	
	if term:
		term_name = term[:2]
		term_year = term[2:]
	else:
		term_name = None
		term_year = None
	
	courses = []
	for course in Course.objects.select_related("department").filter(department__name=department, term__name=term_name, term__start__year=term_year).order_by("department__name", "term__start", "number"):
		courses.append({ 'id': course.id, 'name': course.shortname() })
	
	response_data = { 'success': True, 'courses': courses }
	return JsonResponse(response_data)






