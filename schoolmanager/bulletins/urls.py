from django.conf.urls.defaults import *

urlpatterns = patterns('schoolmanager.bulletins.views',
	(r'^/$', 'get_bulletin_board'),
	(r'^/add/$', 'add_bulletin'),
	(r'^/(?P<bulletin_id>\d+)/delete/$', 'delete_bulletin'),
	(r'^/comments/add/$', 'add_comment'),
	(r'^/comments/(?P<comment_id>\d+)/delete/$', 'delete_comment')
)