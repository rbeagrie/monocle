import os
import yaml

# Django settings for monocle project.

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

# Special Monocle Settings

PROJECT_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__),'..','..'))
MONOCLE_VERSION = '0.04'


MANAGERS = ADMINS

# get settings from db/settings.yaml (if any missing all will default)
# this allows customising the database and web server details after deployment
config = {}
try:
  config_file = os.path.join( PROJECT_PATH , 'settings.yaml' )
  if os.path.exists( config_file ):
    config = yaml.load( file( config_file, 'r' ))
except:
  pass

def get_config( config_yaml, index, default='' ):
  try:
    conf_setting = config_yaml[ index ]
    if conf_setting is None:
        conf_setting = ''
    return conf_setting
  except:
    return default

DEBUG = get_config( config, 'debug', True )
TEMPLATE_DEBUG = get_config( config, 'template_debug', DEBUG )
DATABASE_ENGINE = 'django.db.backends.%s' % get_config( config, 'database_engine', 'sqlite3' )
DATABASE_NAME = get_config( config, 'database_name', os.path.join(PROJECT_PATH,'monocle.db') )
DATABASE_USER = get_config( config, 'database_user', '' )
DATABASE_PASSWORD = get_config( config, 'database_password', '' )
DATABASE_HOST = get_config( config, 'database_host', '' )
DATABASE_PORT = get_config( config, 'database_port', '' )
TIME_ZONE = get_config( config, 'time_zone', 'Europe/London' )
LANGUAGE_CODE = get_config( config, 'language_code', 'en-uk' )
MONOCLE_IP = get_config( config, 'server_ip', '127.0.0.1')
MONOCLE_PORT = get_config( config, 'server_port', '8000')

DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE, 
        'NAME': DATABASE_NAME,                      
        'USER': DATABASE_USER,                      
        'PASSWORD': DATABASE_PASSWORD,                  
        'HOST': DATABASE_HOST,                      
        'PORT': DATABASE_PORT,                      
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-uk'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH,'temp')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH,'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Login URL for authentification
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'f-+2+ov04i0e2c615zba)k4ab87!%f8#l7c+=a1s*1)*1)or4w'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'monocle.urls'

TEMPLATE_CONTEXT_PROCESSORS = ('monocle.context_processors.header',
	'django.contrib.auth.context_processors.auth',
	'django.core.context_processors.static'
)

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'monocle.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	os.path.join(PROJECT_PATH,'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'gene',
	'list',
	'graph',
	'django_cpserver',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'gene.management.commands.import_cufflinks': {
            'handlers': ['console'],
            'level': 'INFO'
        }
    }
}
