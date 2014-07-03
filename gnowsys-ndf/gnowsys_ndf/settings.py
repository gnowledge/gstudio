 # Django settings for gnowsys-ndf project.

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG

# List of Indian Languages 
LANGUAGES = ['English','Hindi','Bengali','Telugu','Marathi','Tamil','Urdu','Gujarati','Kannada','Malayalam','Oriya','Punjabi','Assamese','Maithili','Santali','Kashmiri','Nepali','Gondi','Sindhi','Konkani']

#SMTP setting for sending mail (Using python default SMTP server)
EMAIL_USE_TLS = False
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'testing@example.com'

#SMTP setting for sending mail (Using gmail SMTP server)
#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'yourcompletegmailaddr'
#EMAIL_HOST_PASSWORD = 'yourpassword'

# strength of a password
PASSWORD_MIN_LENGTH = 8
PASSWORD_COMPLEXITY = { # You can ommit any or all of these for no limit for that particular set
    "UPPER": 1,       # Uppercase                 
    "LOWER": 1,       # Lowercase                                                                                                 
    "DIGITS": 1,      # Digits                                                                                                    
}

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'example-sqlite3.db',
    },
    'mongodb': {
        'ENGINE': 'django_mongokit.mongodb',
        'NAME': 'studio-dev1',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
USE_TZ = True
TIME_ZONE = 'Asia/Kolkata'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

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
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'ndf/static/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/static'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '7st0sdv&amp;7yw*eh)zmaz8#t48nr$&amp;ql#ow=$0l^#b_b&amp;$9c*$4c'

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
    #'django.middleware.activeuser_middleware.ActiveUserMiddleware',                 #for online_users
    'online_status.middleware.OnlineStatusMiddleware',                              #for online_users
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
     
# Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTH_PROFILE_MODULE = 'gnowsys_ndf.ndf.models.UserProfile'

ROOT_URLCONF = 'gnowsys_ndf.ndf.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'gnowsys_ndf.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
)

INSTALLED_APPS = (	
    'gnowsys_ndf.ndf',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',    
    'gnowsys_ndf.benchmarker',
    'registration',
    'djangoratings',
    'notification',
    'pagination',
    'gnowsys_ndf.mobwrite',	#textb
#    'south',			#textb
    'django_extensions',	#textb
    'reversion',		#textb
    'django.contrib.flatpages',	#textb
    'online_status',                       #for online_users     
)


ACCOUNT_ACTIVATION_DAYS = 2 # Two days for activation.

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
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
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LOGIN_REDIRECT_URL = "/"

# Absolute filesystem path to the project's base directory, 
# i.e. having settings.py file
# Example: "/.../project-name/app-name/"

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

META_TYPE = [u"GAPP",u"factory_types"]

#Default APPs inculde in beloow GAPPS list
<<<<<<< HEAD
GAPPS = [u"Page", u"File", u"Group", u"Image", u"Video", u"Forum", u"Quiz", u"Course", u"Module", u"Batch", u"Task", u"WikiData"]
=======

GAPPS = [u"Page", u"File", u"Group", u"Image", u"Video", u"Forum", u"Quiz", u"Course", u"Module", u"Batch", u"Task", u"WikiData"]

>>>>>>> aa314071f624dec1cd30b10a50a481fe8d24854f

#Visibility for 'Create Group'
CREATE_GROUP_VISIBILITY=True

EMACS_INIT_FILE_PATH = "~/.emacs"

###########################################################################

"""Settings for org-editor-content-to-html

Default settings required for uploading org-editor content into 
exported html form 
"""

from django.conf import settings

MARKUP_LANGUAGE = getattr(settings, 'GSTUDIO_MARKUP_LANGUAGE', 'html')

MARKDOWN_EXTENSIONS = getattr(settings, 'GSTUDIO_MARKDOWN_EXTENSIONS', '')

WYSIWYG_MARKUP_MAPPING = {
    'textile': 'markitup',
    'markdown': 'markitup',
    'restructuredtext': 'markitup',
    'html': 'tinymce' in settings.INSTALLED_APPS and 'tinymce' or 'wymeditor'}

WYSIWYG = getattr(settings, 'GSTUDIO_WYSIWYG',
                  WYSIWYG_MARKUP_MAPPING.get(MARKUP_LANGUAGE))

###########################################################################

"""Revision Control System (RCS) Configuration

It operates only on single files; and hence used in this project 
to keep track of history of each document belonging to different 
collections (models).

"""

# Indicates list of collection-names whose documents' history has to be 
# maintained.
VERSIONING_COLLECTIONS = ['AttributeTypes', 'RelationTypes', 
                          'GSystemTypes', 'GSystems']

# Absolute filesystem path to the directory that will hold all rcs-files 
# (history-files corresponding to every json-file created for each document)
RCS_REPO_DIR = os.path.join(PROJECT_ROOT, "ndf/static/rcs-repo")

# Indicates the "hash-level-number", i.e the number of sub-directories that 
# will be created for the corresponding document under it's 
# collection-directory; in order to store json-files in an effective manner
RCS_REPO_DIR_HASH_LEVEL = 3

try:
    from local_settings import *
    #print "Local settings applied"
except:
    #print "Default settings applied"
    pass

#textb
import warnings
warnings.filterwarnings(
        'error', r"DateTimeField received a naive datetime",
        RuntimeWarning, r'django\.db\.models\.fields')
#textb


########################################### for online_users_ramk

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#        'LOCATION': 'default-cache'
#    }
#}

#USER_ONLINE_TIMEOUT = 300

#USER_LASTSEEN_TIMEOUT = 60 * 60 * 24 * 7

USERS_ONLINE__TIME_IDLE = 300
USERS_ONLINE__TIME_OFFLINE = 10
#USERS_ONLINE__CACHE_PREFIX_USER
#USERS_ONLINE__CACHE_USERS

