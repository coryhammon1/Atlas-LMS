from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core import serializers

#from notifications.helpers import get_new_notifications

def render_with_context(request, template, context={}):
	return render_to_response(template, context, context_instance=RequestContext(request))

def index(request):
	notifications = request.user.notification_set.all().order_by("-date")

	return render_with_context(request, "notifications/index.html", {"notifications": notifications})
									
def get_new_notifications(request):
	if request.is_ajax():
		#request.user.notification_set.create(text="New note")
		#request.user.notification_set.create(text="Note 2")
		
		new_notifications = request.user.notification_set.filter(is_new=True).order_by("-date")
	
		for notification in new_notifications:
			notification.is_new = False
			notification.save()

		new_notification_json = serializers.serialize("json", new_notifications, fields=("text",))

		return HttpResponse(new_notification_json, mimetype="application/json")
		
	return HttpResponseForbidden()