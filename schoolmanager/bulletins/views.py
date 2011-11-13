import datetime

import django.utils.simplejson as json

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_list_or_404, render_to_response, get_object_or_404

from schoolmanager.utils import JsonResponse

from schoolmanager.bulletins.models import *
from schoolmanager.bulletins.forms import *

from schoolmanager.notifications.models import Notification

def get_bulletin_board(request, course_name):
	bulletin_board = None
	try:
		bulletin_board = request.course.bulletin_board
	except BulletinBoard.DoesNotExist:
		bulletin_board = BulletinBoard.objects.create(course=request.course)
	
	request.user.notifications.filter(course=request.course, bulletin__isnull=False).update(is_new=False)
	
	if not request.is_ajax():
		return render_to_response("courses/bulletin_board.html", { 'bulletin_board': bulletin_board.to_json() })
	return JsonResponse(bulletin_board.to_json())

def add_bulletin(request, course_name):
	form = None
	if request.method == "POST":
		form = BulletinForm(data=request.POST)
		if form.is_valid():
			bulletin = form.save(commit=False)
			bulletin.user = request.user
			
			bulletin_board, created = BulletinBoard.objects.get_or_create(course=request.course)
			
			bulletin.board = bulletin_board
			bulletin.save()
			
			Notification.create_added_bulletin_notification(request.course, bulletin)
			
			return JsonResponse({ 'success': True, 'bulletin': bulletin.get_data() })
		else:
			return JsonResponse(form.compile_errors())
	else:
		form = BulletinForm()
	
	return render_to_response("courses/bulletins/add_bulletin_form.html", { 'form': form })

def delete_bulletin(request, course_name, bulletin_id):

	deleted = True
	try:
		bulletin = Bulletin.objects.get(id=bulletin_id)
		
		#must be either the bulletin's owner or instructor to delete bulletin
		if bulletin.user != request.user and not (request.user.is_superuser or request.user.is_staff):
			return HttpResponseForbidden()
		
		bulletin.delete()
	except Bulletin.DoesNotExist:
		bulletin = None
		deleted = False
	
	return JsonResponse({ 'success': deleted, 'bulletin_id': bulletin.id })
	
def add_comment(request, course_name):
	form = None
	if request.method == "POST":
		form = CommentForm(data=request.POST)
		if form.is_valid() and request.POST.get('bulletin_id'):
			comment = form.save(commit=False)
			comment.bulletin = Bulletin.objects.get(id=request.POST.get('bulletin_id'))
			comment.user = request.user
			comment.date = datetime.datetime.now()
			comment.save()
			
			#add notification
			Notification.create_added_comment_notification(request.course, comment.bulletin, comment)
			
			return JsonResponse({ 'success': True, 'comment': comment.get_data() })
		else:
			return JsonResponse({ 'success': False, 'error': "* This field is required." })
	else:
		form = CommentForm()
		
	return render_to_response("courses/bulletins/add_comment_form.html", {'form': form})
	
def delete_comment(request, course_name, comment_id):
	try:
		comment = BulletinComment.objects.get(id=comment_id)
		
		#must be either the bulletin's owner or instructor to delete bulletin
		if comment.user != request.user and not (request.user.is_superuser or request.user.is_staff):
			return HttpResponseForbidden()
		
		comment.delete()
	except BulletinComment.DoesNotExist:
		comment = None
		deleted = False
	
	return JsonResponse({ 'success': True, 'comment_id': comment.id })


