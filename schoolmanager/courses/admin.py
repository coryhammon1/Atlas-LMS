from django.contrib import admin

from schoolmanager.courses.models import *

class CourseAdmin(admin.ModelAdmin):
	pass
admin.site.register(Course, CourseAdmin)

class TermAdmin(admin.ModelAdmin):
	pass
admin.site.register(Term, TermAdmin)

class DepartmentAdmin(admin.ModelAdmin):
	pass
admin.site.register(Department, DepartmentAdmin)

class GradingSchemeAdmin(admin.ModelAdmin):
	pass
admin.site.register(GradingScheme, GradingSchemeAdmin)