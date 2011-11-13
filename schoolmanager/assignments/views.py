from __future__ import with_statement

import os
import datetime
import time

from urllib import unquote
from decimal import *

import django.utils.simplejson as json

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotAllowed, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.core import serializers
from django.core.exceptions import MultipleObjectsReturned
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Q, F, Count
from django.db import IntegrityError
from django.utils.dateformat import format as date_format
from django.db import IntegrityError
from django.http import Http404
from django.forms.models import modelformset_factory

from schoolmanager.utils import *

from schoolmanager.courses.models import GradingScheme
from schoolmanager.courses.forms import GradingSchemeForm

from schoolmanager.assignments.models import *
from schoolmanager.assignments.forms import *
from schoolmanager.assignments.decorators import superuser_or_staff_required
from schoolmanager.assignments.utils import *

from schoolmanager.notifications.models import Notification

from schoolmanager.quizzes.models import OnlineQuiz, QuizSubmission

def all_assignments(request, course_name):	
	course = request.course
	
	assignments = QueryList(Assignment.objects.select_related("course", "course__department", "course__term").filter(course=course))
	
	group_objects = course.groups.all()
	
	groups = []
	for group in group_objects:
		group_assignments = assignments.filter(group_id=group.id)
		groups.append({ 'name': group.name, 'id': group.id, 'weight': group.weight, 'assignments': group_assignments })
	
	if request.user.is_staff:
		group_form = AssignmentGroupForm()
		
		blank_assignment_form = AssignmentForm(course=course, auto_id=False)
		
		grades = []
		submissions = QueryList(AssignmentSubmission.objects.select_related("assignment", "assignment_group") \
													.filter(assignment__course=course))
		grading = course.get_grading_scheme()
		for student in course.users.filter(is_staff=False, is_superuser=False):
			percentage = course.get_grade(student, submissions, group_objects)
			letter_grade = grading.grade_for_percent(percentage)
			
			grades.append({ "first_name": student.first_name, "last_name": student.last_name,
							"percentage": percentage, "letter_grade": letter_grade })
		
		grading_scale_form = None
		if request.method == "POST" and request.POST.get("form_name") == "scale":
			grading_scale_form = GradingSchemeForm(instance=grading, data=request.POST)
			if grading_scale_form.is_valid():
				grading_scale_form.save()
				messages.success(request, "Grading Scale changed successfully.")
		else:
			grading_scale_form = GradingSchemeForm(instance=grading)
				
		return render_with_context(request, "assignments/instructor/all_assignments.html", 
											{ 'groups': groups, 'group_form': group_form,
											  'blank_assignment_form': blank_assignment_form,
											   'grades': grades, 'scale_form': grading_scale_form })
									
	else:
		return render_with_context(request, "assignments/student/all_assignments2.html", { 'groups': groups })
		
def get_upcoming(request, course_name):
	assignments = request.course.assignments.select_related("course", "course__department", "course__term") \
											.filter(due_date__gte=datetime.datetime.now()).order_by("due_date")
	
	assignment_data = []
	for assignment in assignments:
		if assignment.is_viewable or request.user.is_superuser or request.user.is_staff:
			assignment.category = assignment.due_date_time_category()
		
			if request.user.is_staff or request.user.is_superuser:
				url = assignment.get_instructor_url()
			else:
				url = assignment.get_url()
		
			assignment_data.append({ 'id': assignment.id, 'due_date': assignment.get_time_category_display(), 
						'name': assignment.name, 'category': assignment.category, 'url': url })
	
	if not request.is_ajax():
		return render_to_response("courses/upcoming.html", { 'assignments': assignment_data })
	return JsonResponse(assignment_data)	

def average_grades(request, course_name):
	assignments = request.course.assignments.all()
	scheme = request.course.get_grading_scheme()
	
	assignment_data = []
	
	for assignment in assignments:
		grade_data = {}
		
		#get student grade
		if not (request.user.is_superuser or request.user.is_staff):
			student_submission, created = assignment.submissions.get_or_create(user=request.user)
		
			student_grade = student_submission.get_grade()
			student_letter_grade = None
			if student_grade:
				student_grade *= 100
				student_letter_grade = scheme.grade_for_percent(student_grade)
			else:
				continue
			
			grade_data.update({ 'student': { 'grade': normalized_float(student_grade), 'letter_grade': student_letter_grade } })
		
		average = assignment.get_average_grade()
		average_letter_grade = None
		if average:
			average *= 100
			average_letter_grade = scheme.grade_for_percent(average)
		else:
			continue
		
		grade_data.update({ 'average': { 'grade': normalized_float(average), 'letter_grade': average_letter_grade } })
		grade_data.update({ 'name': assignment.name })
	
		assignment_data.append(grade_data)
	
	if request.is_ajax():
		return JsonResponse(assignment_data)
	return HttpResponse("<body>" + json.dumps(assignment_data) + "</body>")
																											
@user_passes_test(is_superuser_or_staff)
def instructor_add_group(request, course_name):
	form = None
	if request.method == "POST":
		form = AssignmentGroupForm(data=request.POST)
		if form.is_valid():
			new_group = form.save(commit=False)
			new_group.course = request.course
			new_group.save()
			
			form.cleaned_data.update({ 'id': int(new_group.id) })
			
			new_group_data = { 'success': True, 'group': form.cleaned_data }
			
			return JsonResponse(new_group_data)
		else:
			return JsonResponse(form.compile_errors())
	else:
		form = AssignmentGroupForm()
		return render_to_response("assignments/add_group_form.html", { 'form': form })		
	
@user_passes_test(is_superuser_or_staff)
def instructor_change_group_weight(request, course_name, group_id):
	group = get_object_or_404(AssignmentGroup, id=group_id)
	
	form = None
	if request.method == "POST":
		form = ChangeWeightForm(instance=group, data=request.POST)
		if form.is_valid():
			form.save()
			return JsonResponse({ 'success': True, 'weight': form.instance.weight })
		else:
			error = form.errors['weight'];
			return JsonResponse({ 'success': False, 'error': error })
	else:
		form = ChangeWeightForm(instance=group)
		
	return render_to_response("assignments/change_group_weight.html", { 'form': form })
		

@user_passes_test(is_superuser_or_staff)
def instructor_delete_group(request, course_name, group_id):
	group = get_object_or_404(AssignmentGroup, id=group_id)
		
	form = None
	if request.method == "POST":	
		form = TransferGroupAssignmentsForm(group=group, course=request.course, data=request.POST)
		if form.is_valid():
			transfer_group = form.cleaned_data.get('transfer_group')
			return_data = None
			if transfer_group: # transfer assignments to another group
				group.assignments.all().update(group=transfer_group)
				return_data = { 'success': True, 'transfer_id': transfer_group.id }
			else: # delete assignments and group
				group.assignments.all().delete()
				return_data = { 'success': True }
			group.delete()
			return JsonResponse(return_data)
		else:
			return JsonResponse({ 'success': False })
	else:
		form = TransferGroupAssignmentsForm(group=group, course=request.course)
	
	return render_to_response("assignments/transfer_group_assignments.html", { 'form': form })





"""Assignments"""

@user_passes_test(is_superuser_or_staff)
def instructor_view_assignment(request, course_name, assignment_id):
	try:
		assignment = request.assignment
	except AttributeError:
		assignment = get_object_or_404(Assignment, id=assignment_id)
	
	#delete notifications
	#request.user.notifications.filter(assignment=assignment, resource__isnull=True, is_new=True).update(is_new=False)
	
	form = None
	if request.method == "POST" and request.POST.get("submit_type") == "assignment":
		form = AssignmentForm(instance=assignment, course=request.course, data=request.POST)
		if form.is_valid() and form.has_changed():
			form.save()
			messages.success(request, "Assignment updated successfully.")
	else:
		form = AssignmentForm(instance=assignment, course=request.course)
	
	quiz = None
	grade_formset = None
	grade_form = None
	has_submitted_quiz = []
	submissions = assignment.get_submissions(request)
	if assignment.type == 's': #if assignment is submitted online						
		file_submissions = QueryList(
			AssignmentFileSubmission.objects.filter(assignment_submission__assignment=assignment)
		)
		
		for file in file_submissions:
			file._set_cached_course(request.course) #for performance
		
		for submission in submissions:
			submission.current_files = file_submissions.filter(assignment_submission_id=submission.id)
		
	elif assignment.type == 'c' or assignment.type == 'o': #if assignment is taken in class or taken online		
		if assignment.type == 'o': #if assignment is taken online
			quiz_submissions = QuizSubmission.objects.filter(submission__assignment=assignment)
			
			for quiz_submission in quiz_submissions:
				if quiz_submission.submission in submissions:
					has_submitted_quiz.append(quiz_submission.submission.id)
		
		
		def custom_field_callback(field):
			return field.formfield(required=False)
		
		AssignmentGradeFormset = modelformset_factory(AssignmentSubmission, fields=("score", "text"),
													   formfield_callback=custom_field_callback, extra=0)
		
		grade_queryset = assignment.submissions.select_related("user").order_by("user__last_name", "user__first_name")
		
		if request.method == "POST" and request.POST.get("submit_type") == "grades":
			grade_formset = AssignmentGradeFormset(queryset=grade_queryset, data=request.POST, auto_id=False)
			if grade_formset.is_valid():
				unsaved_submissions = grade_formset.save(commit=False)
				for submission in unsaved_submissions:
					submission.status = 1 #graded
					submission.save()
			
				if assignment.type == 'c':
					Notification.create_graded_assignments_notification(request.course, assignment, submissions)
				
				messages.success(request, "Students were graded successfully.")
		else:
			grade_formset = AssignmentGradeFormset(queryset=grade_queryset, auto_id=False)
			
			
	#resource form handling
	resource_form = None
	if request.method == "POST" and request.POST.get("submit_type") == "resource":
		resource_form = ResourceForm(assignment=assignment, data=request.POST, files=request.FILES, auto_id=False)
		if resource_form.is_valid():
			resource = resource_form.save(request.user.username)
			
			Notification.create_added_resource_notification(request.course, assignment, resource)
			
			messages.success(request, "Resource added successfully.")
			
			resource_form = ResourceForm(assignment=assignment, auto_id=False)
	else:
		resource_form = ResourceForm(assignment=assignment, auto_id=False)

	resources = assignment.resources.all()
													
	for resource in resources:
		resource._set_cached_course(request.course) #for performance

	return render_with_context(request, "assignments/instructor/view_assignment.html", 
						{ 'assignment': assignment, 'assignment_form': form, 
						'grade_formset': grade_formset, 'grade_form': grade_form, 
						'resource_form': resource_form, 'resources': resources,
						'submissions': submissions, 'has_submitted_quiz': has_submitted_quiz })


@user_passes_test(is_superuser_or_staff)
def instructor_add_assignment(request, course_name):
	form = None
	
	time.sleep(5)
	
	if request.method == "POST":
		form = AssignmentForm(course=request.course, data=request.POST)
		if form.is_valid():
			new_assignment = form.save(commit=False) # get new model instance from form
			new_assignment.course = request.course
			new_assignment.group_id = form.cleaned_data['group_id']
			new_assignment.save()
			
			form_data = form.cleaned_data
			form_data['due_date'] = str(form_data['due_date'])
			form_data['viewable_date'] = str(form_data['viewable_date'])
			form_data.update({ 'id': new_assignment.id })
			
			form_data = { 'success': True, 'assignment': form_data }
						
			Notification.create_added_assignment_student_notification(request.course, new_assignment)
			Notification.create_added_assignment_instructor_notification(request.course, request.user, new_assignment)
						
			return JsonResponse(form_data)
		else:
			return JsonResponse(form.compile_errors())
	else:
		form = AssignmentForm(course=request.course)
		
	return render_to_response('assignments/new_assignment_form.html', { 'form': form })

@user_passes_test(is_superuser_or_staff)
def instructor_transfer_assignment(request, course_name, assignment_id):
	transfered = True
	try:
		assignment = request.assignment
	except AttributeError:
		try:
			assignment = Assignment.objects.get(id=assignment_id)
		except Assignment.DoesNotExist:
			transfered = False
			assignment = None
	
	try:
		transfer_group = AssignmentGroup.objects.get(id=request.POST.get("transfer_id"))
	except AssignmentGroup.DoesNotExist:
		transfered = False
		transfer_group = None
	
	if transfered:
		assignment.group = transfer_group
		assignment.save()
	
	return JsonResponse({ 'success': transfered })

@user_passes_test(is_superuser_or_staff)
def instructor_delete_assignment(request, course_name, assignment_id):
	deleted = True
	try:
		assignment = request.assignment
	except AttributeError:
		try:
			assignment = Assignment.objects.get(id=assignment_id)
		except Assignment.DoesNotExist:
			assignment = None
	
	if assignment:
		# Manually delete all file submissions, because files on harddrive must be deleted as well
		for file_submission in AssignmentFileSubmission.objects.filter(assignment_submission__assignment=assignment):
			file_submission.delete()
		
		assignment.delete()
	else:
		deleted = False
	
	return JsonResponse({ 'success': deleted })
	
@user_passes_test(is_superuser_or_staff)
def instructor_grade_submission(request, course_name, assignment_id, submission_id):
	submission = get_object_or_404(AssignmentSubmission, id=submission_id)
	
	form = None
	if request.method == "POST":
		form = GradeAssignmentSubmissionForm(instance=submission, data=request.POST)
		if form.is_valid():
			graded_submission = form.save(commit=False)
			graded_submission.status = 1 #Graded
			graded_submission.save()
			
			Notification.create_graded_submission_notification(request.course, submission.assignment, graded_submission.user)
			
			graded_data = date_format(graded_submission.date, "D. N n, Y \\a\\t P")
			return JsonResponse({ 'success': True, 'score': graded_submission.score, 'date': graded_data })
		else:
			return JsonResponse(form.compile_errors())
	else:
		form = GradeAssignmentSubmissionForm(instance=submission)
		
	files = submission.files.all()
					
	return render_to_response("assignments/grade_submission_form.html",
								{ 'form': form, 'submission': submission, 'files': files })

@user_passes_test(is_superuser_or_staff)
def instructor_reset_submission(request, course_name, assignment_id, submission_id):
	deleted = True
	try:
		submission = AssignmentSubmission.objects.get(id=submission_id)
		submission.delete()
	except AssignmentSubmission.DoesNotExist:
		submission = None
		deleted = False
	
	return JsonResponse({ 'success': deleted })

@user_passes_test(is_superuser_or_staff)
def instructor_reset_all_submissions(request, course_name, assignment_id):
	deleted = True
	try:
		assignment = request.assignment
	except AttributeError:
		try:
			assignment = Assignment.objects.get(id=assignment_id)
		except Assignment.DoesNotExist:
			assignment = None
	
	if assignment:
		assignment.submissions.all().delete()
	else:
		messages.success(request, "Assignment was reset successfully")
	
	return HttpResponseRedirect("../../")


"""Resources"""

@user_passes_test(is_superuser_or_staff)
def instructor_delete_resource(request, course_name, assignment_id, resource_id):
	deleted = True
	try:
		resource = AssignmentResource.objects.get(id=resource_id)
		resource.delete()
	except AssignmentResource.DoesNotExist:
		resource = None
		deleted = False
	
	return JsonResponse({ 'success': deleted })
	
	
	
	
"""Student Views"""

def student_view_assignment(request, course_name, assignment_name):
	try:
		assignment = request.assignment
	except AttributeError:
		assignment_name = assignment_name.replace("_", " ")
		assignment = get_object_or_404(Assignment, name=assignment_name, course=request.course)
	
	#request.user.notifications.filter(assignment=assignment, resource__isnull=True, is_new=True).update(is_new=False)
	
	resources = assignment.resources.all()
	
	"""
	for resource in resources:
		resource.notification_count = resource.get_notification_count(request.user)
	"""
	try:
		submission = request.user.submissions.select_related("assignment").get(assignment=assignment)
	except AssignmentSubmission.DoesNotExist:
		if request.user.is_superuser or request.user.is_staff:
			submission = AssignmentSubmission(assignment=assignment, user=request.user)
		else:
			submission = request.user.submissions.create(assignment=assignment)
		
	
	quiz = None
	quiz_submission = None
	if assignment.type == 'o':
		quiz, created = OnlineQuiz.objects.get_or_create(assignment=assignment)
		quiz_submission, created = QuizSubmission.objects.get_or_create(quiz=quiz, submission=submission)
		quiz_submission._set_cached_quiz(quiz)
		
	try:
		scheme = request.course.get_grading_scheme()
		submission.grade = scheme.grade_for_percent(100 * submission.get_grade())
	except:
		pass
	
	due_date_expired = assignment.due_date < datetime.datetime.now()
	
	submission_errors = {}
	if request.method == "POST":
		if assignment.type == 's' and not due_date_expired:
			
			submission_errors = save_files_for_submission(request.FILES.items(), submission)
			submission.text = request.POST['submission-text']
		
			if submission_errors == {}:
				submission.status = 0 #submitted status
				messages.success(request, "Your response was submitted successfully.")
		
			if not (request.user.is_superuser or request.user.is_staff):
				submission.save()
			
			Notification.create_submitted_assignment_notification(request.course, request.user, assignment)
		
	files = submission.files.all()
	for file in files:
		file._set_cached_course(request.course) #for performance
		
	return render_with_context(request, "assignments/student/view_assignment.html",
						{ 'assignment': assignment, 'submission': submission, 'files': files, 
						'errors': submission_errors, 'due_date_expired': due_date_expired,
						'resources': resources, 'MAX_UPLOAD_FILE_SIZE': settings.MAX_UPLOAD_FILE_SIZE,
						'quiz': quiz, 'quiz_submission': quiz_submission })	
			
def student_delete_file_submission(request, course_name, file_id):
	deleted = True
	try:
		file_submission = AssignmentFileSubmission.objects.get(id=file_id)
		file_name = file_submission.__unicode__()
		file_submission.delete()
	except AssignmentFileSubmission.DoesNotExist:
		deleted = False
		file_name = ""
	
	return JsonResponse({ 'success': deleted, 'file': file_name })

def get_file_submission(request, course_name, file_id):
	file_submission = get_object_or_404(AssignmentFileSubmission, id=file_id)
	if not (request.user.is_superuser or request.user.is_staff):
		if file_submission.assignment_submission.user != request.user:
			raise Http404
	
	if settings.DEBUG:
		uploaded_file = get_uploaded_file(file_submission.file)
	
		response = HttpResponse(uploaded_file, mimetype=file_submission.content_type)
		response['Content-Disposition'] = "attachment; filename=%s" % file_submission.__unicode__()
	else:		
		response = HttpResponse(mimetype=file_submission.content_type)
		response['Content-Disposition'] = "attachment; filename=%s" % file_submission.__unicode__()
		response['X-Accel-Redirect'] = "/uploads/%s" % file_submission.file

	return response
	
def get_resource(request, course_name, resource_id):
	resource = get_object_or_404(AssignmentResource, id=resource_id)
	
	#request.user.notifications.filter(resource=resource, is_new=True).update(is_new=False)
	
	if resource.type == 'u': #if resource is url
		return HttpResponseRedirect(resource.get_url())
	else:		# resource is file	
	
		if settings.DEBUG:
			uploaded_file = get_uploaded_file(resource.file)
			
			response = HttpResponse(uploaded_file, mimetype=resource.content_type)
			response['Content-Disposition'] = "attachment; filename=%s" % resource.name
		else:
			response = HttpResponse(mimetype=resource.content_type)
			response['Content-Disposition'] = "attachment; filename=%s" % resource.name
			response['X-Accel-Redirect'] = "/uploads/%s" % resource.file
		
		return response







				
