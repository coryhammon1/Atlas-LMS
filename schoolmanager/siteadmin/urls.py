from django.conf.urls.defaults import *

urlpatterns = patterns('schoolmanager.siteadmin.views',
	(r'^/$', 'index'),
	
	(r'^/users/$', 'users'),
	(r'^/users/add/$', 'add_user'),
	(r'^/users/delete/$', 'delete_user'),
	(r'^/users/partial/$', 'partial_user_list'),
	(r'^/users/search/$', 'search_user'),
	(r'^/users/(?P<user_id>\d+)/$', 'view_user'),
	(r'^/users/(?P<user_id>\d+)/enroll/$', 'enroll_user_in_course'),
	(r'^/users/(?P<user_id>\d+)/remove/$', 'remove_course_from_user'),
	
	(r'^/terms/add/$', 'add_term'),
	(r'^/terms/delete/$', 'delete_term'),
	(r'^/terms/(?P<term_id>\d+)/change/', 'change_term'),
	(r'^/departments/add/$', 'add_department'),
	(r'^/departments/delete/$', 'delete_department'),
	(r'^/departments/(?P<department_id>\d+)/change/$', 'change_department'),
	(r'^/courses/$', 'view_courses'),
	(r'^/courses/add/$', 'add_course'),
	(r'^/courses/delete/$', 'delete_course'),
	(r'^/courses/partial/$', 'partial_course_list'),
	(r'^/courses/(?P<course_id>\d+)/$', 'view_course'),
	(r'^/courses/(?P<course_id>\d+)/add_user/$', 'add_user_to_course'),
	(r'^/courses/(?P<course_id>\d+)/remove_user/$', 'remove_user_from_course'),
	(r'^/courses/(?P<course_id>\d+)/print_grades/$', 'print_course_grades'),
)