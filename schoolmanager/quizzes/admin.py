from django.contrib import admin
from schoolmanager.quizzes.models import *

class QuizSubmissionAdmin(admin.ModelAdmin):
	pass
admin.site.register(QuizSubmission, QuizSubmissionAdmin)
