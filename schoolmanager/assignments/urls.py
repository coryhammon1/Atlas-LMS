from django.conf.urls.defaults import *

urlpatterns = patterns('schoolmanager.assignments.views',
	(r'^/$', 'all_assignments'),
	(r'^/upcoming/$', 'get_upcoming'),
	(r'^/average/$', 'average_grades'),
	
	(r'^/groups/add/$', 'instructor_add_group'),
	(r'^/groups/(?P<group_id>\d+)/delete/$', 'instructor_delete_group'),
	(r'^/groups/(?P<group_id>\d+)/change/$', 'instructor_change_group_weight'),
	(r'^/add/$', 'instructor_add_assignment'),
	
	(r'^/(?P<assignment_id>\d+)/$', 'instructor_view_assignment'),
	(r'^/(?P<assignment_id>\d+)/delete/$', 'instructor_delete_assignment'),
	(r'^/(?P<assignment_id>\d+)/transfer/$', 'instructor_transfer_assignment'),
	
	(r'^/(?P<assignment_id>\d+)/submissions/(?P<submission_id>\d+)/grade/$', 'instructor_grade_submission'),
	(r'^/(?P<assignment_id>\d+)/submissions/(?P<submission_id>\d+)/reset/$', 'instructor_reset_submission'),
	(r'^/(?P<assignment_id>\d+)/submissions/reset/', 'instructor_reset_all_submissions'),
	
	(r'^/(?P<assignment_id>\d+)/resources/(?P<resource_id>\d+)/delete/$', 'instructor_delete_resource'),
	
	(r'^/(?P<assignment_name>\w+)/$', 'student_view_assignment'),
	
	(r'^/files/(?P<file_id>\d+)/$', 'get_file_submission'),
	(r'^/files/(?P<file_id>\d+)/delete/$', 'student_delete_file_submission'),
	
	(r'^/\w+/resources/(?P<resource_id>\d+)/$', 'get_resource'),
)

urlpatterns += patterns('schoolmanager.quizzes.views',
	(r'^/(?P<assignment_id>\d+)/quiz/questions/add/$', 'instructor_add_question'),
	(r'^/(?P<assignment_id>\d+)/quiz/questions/(?P<question_id>\d+)/update/$', 'instructor_update_question'),
	(r'^/(?P<assignment_id>\d+)/quiz/questions/(?P<question_id>\d+)/delete/$', 'instructor_delete_question'),
	(r'^/(?P<assignment_id>\d+)/quiz/questions/(?P<question_id>\d+)/choices/update/$', 'instructor_update_choices'),
	(r'^/(?P<assignment_id>\d+)/quiz/(?P<student_id>\d+)/results/$', 'instructor_view_results'),
	(r'^/(?P<assignment_id>\d+)/quiz/$', 'instructor_view_quiz'),
	
	(r'^/(?P<assignment_name>\w+)/quiz/results/$', 'student_view_results'),
	(r'^/(?P<assignment_name>\w+)/quiz/$', 'student_take_quiz'),
)