# Django settings for schoolmanager project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

PROJECT_DIRECTORY = './'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
	'default': {
		'NAME': PROJECT_DIRECTORY + '/database/database.db',
		'ENGINE': 'django.db.backends.sqlite3',
	}
}
"""
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'HOST': '127.0.0.1',
		'PORT': '8889',
		'NAME': 'schoolmanager',
		'USER': 'root',
		'PASSWORD': 'root'
	}
}
"""

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Phoenix'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = PROJECT_DIRECTORY + '/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'n@2dodpq1b7w*)8v^0-*78rn+k#_t4n%c==5--$jf+=b4l8s9r'

# List of callables that know how to import templates from various sources.

if DEBUG:
	TEMPLATE_LOADERS = (
		'django.template.loaders.filesystem.Loader',
		'django.template.loaders.app_directories.Loader',
	)
else:
	TEMPLATE_LOADERS = (
		('django.template.loaders.cached.Loader', (
			'django.template.loaders.filesystem.Loader',
			'django.template.loaders.app_directories.Loader',
		)),
	)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#	'middleware.CacheAuthenticationMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
#	'django.middleware.csrf.CsrfResponseMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'schoolmanager.profiling.middleware.ProfileMiddleware',
	'schoolmanager.middleware.Forbidden403Middleware',
	'schoolmanager.middleware.LoginRequiredMiddleware',
	'schoolmanager.siteadmin.middleware.AdminRequiredMiddleware',
	'schoolmanager.debug_toolbar.middleware.DebugToolbarMiddleware',
	'schoolmanager.courses.middleware.CurrentCoursesMiddleware',
	'schoolmanager.courses.middleware.CourseAccessMiddleware',
	'schoolmanager.assignments.middleware.CurrentAssignmentMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.contrib.auth.context_processors.auth',
	'django.core.context_processors.request',
	'django.contrib.messages.context_processors.messages',
)

ROOT_URLCONF = 'schoolmanager.urls'

TEMPLATE_DIRS = (
    PROJECT_DIRECTORY + '/templates/',
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.admin',
	'schoolmanager.django_evolution',
	'schoolmanager.debug_toolbar',
	'schoolmanager.notifications',
	'schoolmanager.bulletins',
	'schoolmanager.courses',
	'schoolmanager.assignments',
	'schoolmanager.quizzes',
	'schoolmanager.siteadmin',
)

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 2**10 #500 Kilobytes

MAX_UPLOAD_FILE_SIZE = 2.5 * 2**20 #2.5 megabytes
UPLOAD_DIR = PROJECT_DIRECTORY + "/uploads/"
UNSAFE_FILE_EXTENSIONS = (".exe", ".bat", ".scr")

CACHE_BACKEND = "locmem://"

APPEND_SLASH = True

INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}

MIDDLEWARE_EXCLUDED_URLS = ("/site_media", "/media", "/__debug__", "/reset_password", "/reset", "/favicon.ico")

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'atlaseduction@gmail.com'
EMAIL_HOST_PASSWORD = 'atlas1106'
EMAIL_PORT = 587


#USE_I18N = False
