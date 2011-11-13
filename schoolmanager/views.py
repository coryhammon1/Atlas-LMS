import os
import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import logout, login as old_login
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.core.cache import cache

from schoolmanager.utils import render_with_context

from schoolmanager.forms import UpdateUserForm
from schoolmanager.bulletins.models import BulletinBoard

def index(request):
	if request.user.is_superuser:
		return HttpResponseRedirect("/siteadmin/")

	notifications = None
	main_bulletin_board_id = None
	
	browser = request.META['HTTP_USER_AGENT']
	
	is_ie6 = False
	if browser.find("MSIE 6.0") >= 0:
		is_ie6 = True
	
	cache_key = "CheckFutureCourses-%d" % request.user.id
	checked = cache.get(cache_key)
	if checked is None:
		has_future_courses = request.user.courses.filter(term__start__gt=datetime.datetime.now()).exists()
		message = "You are enrolled in courses for future terms. Click 'All My Courses' on the right to view these courses."
		if has_future_courses:
			messages.success(request, message)
	
	return render_with_context(request, 'index.html', { 'is_ie6': is_ie6 })
	
def update_profile(request):
	if request.method == "POST" and request.POST.get("form_type") == "profile":
		profile_form = UpdateUserForm(instance=request.user, data=request.POST)
		if profile_form.is_valid():
			profile_form.save()
			messages.success(request, "Email was changed successfully.")
	else:
		profile_form = UpdateUserForm(instance=request.user)
		
	if request.method == "POST" and request.POST.get("form_type") == "password":
		password_form = PasswordChangeForm(user=request.user, data=request.POST)
		if password_form.is_valid():
			password_form.save()
			messages.success(request, "Password was changed successfully.")
	else:
		password_form = PasswordChangeForm(user=request.user)
		
	return render_with_context(request, "registration/update_profile.html", { 'profile_form': profile_form, 'password_form': password_form })
	
def reset_password(request):
	if request.method == "POST":
		form = PasswordResetForm(data=request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect("done/")
	else:
		form = PasswordResetForm()
	return render_with_context(request, "registration/reset_password.html", { 'form': form })
	