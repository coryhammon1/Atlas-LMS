from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'views.index'),
	(r'^profile/$', 'views.update_profile'),
	
	(r'^reset_password/$', 'django.contrib.auth.views.password_reset',
		{ 'template_name': 'registration/reset_password.html' }),
	(r'^reset_password/done/$', 'django.contrib.auth.views.password_reset_done', 
		{ 'template_name': 'registration/password_reset_done.html' }),
	(r'^reset/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$', 'django.contrib.auth.views.password_reset_confirm',
		{ 'template_name': 'registration/password_reset_confirmation.html' }),
	(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete',
		{ 'template_name': 'registration/password_reset_complete.html' }),
	
	(r'^login/$', 'django.contrib.auth.views.login'),
	(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
	(r'^siteadmin', include('schoolmanager.siteadmin.urls')),
	(r'^admin/', include(admin.site.urls)),
	(r'^courses/(?P<course_name>\w+)/bulletins', include('schoolmanager.bulletins.urls')),
	(r'^courses/(?P<course_name>\w+)/assignments', include('schoolmanager.assignments.urls')),
	(r'^courses/', include('schoolmanager.courses.urls')),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^%s(?P<path>.*)$' % settings.MEDIA_URL, 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
		(r'^sentry/', include('sentry.urls')),
	)
