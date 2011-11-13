from django.conf.urls.defaults import *

urlpatterns = patterns('schoolmanager.courses.views',
	(r'^$', 'index'),
    (r'^(?P<course_name>\w+)/$', 'view_course'),
	(r'^(?P<course_name>\w+)/stream/$', 'get_stream'),
	(r'^(?P<course_name>\w+)/grade/$', 'get_grade'),
	(r'^(?P<course_name>\w+)/grades/$', 'grades'),
	(r'^(?P<course_name>\w+)/print_grades/$', 'print_grades')
)