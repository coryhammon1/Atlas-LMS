from django.conf.urls.defaults import *

urlpatterns = patterns('schoolmanager.notifications.views',
   (r'^/$', 'index'),
   (r'^/get_new/$', 'get_new_notifications'),
)