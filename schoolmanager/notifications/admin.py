from django.contrib import admin

from schoolmanager.notifications.models import Notification

class NotificationAdmin(admin.ModelAdmin):
	pass
admin.site.register(Notification, NotificationAdmin)

