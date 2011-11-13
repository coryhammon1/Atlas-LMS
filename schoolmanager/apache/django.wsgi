import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'schoolmanager.settings'

sys.path.append("/users/public/schoolmanager")

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()