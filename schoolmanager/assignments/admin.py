from django.contrib import admin
from schoolmanager.assignments.models import *

class AssignmentAdmin(admin.ModelAdmin):
	pass
admin.site.register(Assignment, AssignmentAdmin)

class AssignmentGroupAdmin(admin.ModelAdmin):
	pass
admin.site.register(AssignmentGroup, AssignmentGroupAdmin)

class AssignmentSubmissionAdmin(admin.ModelAdmin):
	pass
admin.site.register(AssignmentSubmission, AssignmentSubmissionAdmin)

class AssignmentFileSubmissionAdmin(admin.ModelAdmin):
	pass
admin.site.register(AssignmentFileSubmission, AssignmentFileSubmissionAdmin)

class AssignmentResourceAdmin(admin.ModelAdmin):
	pass
admin.site.register(AssignmentResource, AssignmentResourceAdmin)
