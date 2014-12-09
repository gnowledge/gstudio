 # Django settings for gnowsys-ndf project.
from django.conf import global_settings
#from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
from django.utils.translation import ugettext
import os
DEBUG = True
# ALLOWED_HOSTS = ["127.0.0.1"]
TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG

LANGUAGES = (('en', 'English'),('hi', 'Hindi'))

# ('mr', 'Marathi'),('mun','Munda'),('mni','Manipuri'),('ori','Oriya'),('pi','Pali'),('raj','Rajasthani'),('lah','Lahnda'),('gu','Gujarati'),('ks','Kashmiri'), ('kok','Konkani'), ('kha','Khasi'), ('dra','Dravidian'), ('gon','Gondi'), ('bra','Braj'), ('mi','Malayalam'), ('mai','Maithili'), ('mag','Magahi'), ('lus','Lushai'), ('bh','Bihari'), ('kru','Kurukh'), ('awa','Awadhi'),('sa','Sanskrit'),('sat','Santali'), ('him','Himachali'), ('sd','Sindhi'), ('af', 'Afrikaans'), ('as','Assamese'),('ar', 'Arabic'), ('az', 'Azerbaijani'), ('bg', 'Bulgarian'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('br', 'Breton'), ('bs', 'Bosnian'), ('ca', 'Catalan'),('bho','Bhojpuri'), ('cs', 'Czech'), ('cy', 'Welsh'), ('da', 'Danish'), ('de', 'German'), ('el', 'Greek'), ('en-gb', 'British English'), ('eo', 'Esperanto'), ('es', 'Spanish'), ('es-ar', 'Argentinian Spanish'), ('es-mx', 'Mexican Spanish'), ('es-ni', 'Nicaraguan Spanish'), ('es-ve', 'Venezuelan Spanish'), ('et', 'Estonian'), ('eu', 'Basque'), ('fa', 'Persian'), ('fi', 'Finnish'), ('fr', 'French'), ('fy-nl', 'Frisian'), ('ga', 'Irish'), ('gl', 'Galician'), ('he', 'Hebrew'),('hr', 'Croatian'), ('hu', 'Hungarian'), ('ia', 'Interlingua'), ('id', 'Indonesian'), ('is', 'Icelandic'), ('it', 'Italian'), ('ja', 'Japanese'), ('ka', 'Georgian'), ('kk', 'Kazakh'), ('km', 'Khmer'), ('kn', 'Kannada'), ('ko', 'Korean'), ('lb', 'Luxembourgish'), ('lt', 'Lithuanian'), ('lv', 'Latvian'), ('mk', 'Macedonian'), ('ml', 'Malayalam'), ('mn', 'Mongolian'), ('my', 'Burmese'), ('nb', 'Norwegian Bokmal'), ('ne', 'Nepali'), ('nl', 'Dutch'), ('nn', 'Norwegian Nynorsk'), ('os', 'Ossetic'), ('pa', 'Punjabi'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('pt-br', 'Brazilian Portuguese'), ('ro', 'Romanian'), ('ru', 'Russian'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('sq', 'Albanian'), ('sr', 'Serbian'), ('sr-latn', 'Serbian Latin'), ('sv', 'Swedish'), ('sw', 'Swahili'), ('ta', 'Tamil'), ('te', 'Telugu'), ('th', 'Thai'), ('tr', 'Turkish'), ('tt', 'Tatar'), ('udm', 'Udmurt'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('vi', 'Vietnamese'), ('zh-cn', 'Simplified Chinese'), ('zh-tw', 'Traditional Chinese')) 

EXTRA_LANG_INFO = {
    'mr': {
        'bidi': True, # right-to-left
        'code': 'mr',
        'name': 'Marathi',
        'name_local': 'Marathi'
    },
    'mun': {
        'bidi': True, # right-to-left
        'code': 'mun',
        'name': 'Munda',
        'name_local': 'Munda'
    },

    'mni': {
        'bidi': True, # right-to-left
        'code': 'ug',
        'name': 'Manipuri',
        'name_local': 'Manipuri'
    },
    'ori': {
        'bidi': True, # right-to-left
        'code': 'ori',
        'name': 'Oriya',
        'name_local': 'Oriya'
    },
    'mr': {
        'bidi': True, # right-to-left
        'code': 'mr',
        'name': 'Marathi',
        'name_local': 'Marathi'
    },
    'pi': {
        'bidi': True, # right-to-left
        'code': 'pi',
        'name': 'Pali',
        'name_local': 'Pali'
    },
    'raj': {
        'bidi': True, # right-to-left
        'code': 'raj',
        'name': 'Rajasthani',
        'name_local': 'Rajasthani'
    },
    'sa': {
        'bidi': True, # right-to-left
        'code': 'sa',
        'name': 'Sanskrit',
        'name_local': 'Sanskrit'
    },

    'sat': {
        'bidi': True, # right-to-left
        'code': 'sat',
        'name': 'Santali',
        'name_local': 'Santali'
    },
    'sd': {
        'bidi': True, # right-to-left
        'code': 'sa',
        'name': 'Sindhi',
        'name_local': 'Sindhi'
    },
    'as': {
        'bidi': True, # right-to-left
        'code': 'as',
        'name': 'Assamese',
        'name_local': 'Assamese'
    },
    'awa': {
        'bidi': True, # right-to-left
        'code': 'awa',
        'name': 'Awadhi',
        'name_local': 'Awadhi'
    },
    'bho': {
        'bidi': True, # right-to-left
        'code': 'bho',
        'name': 'Bhojpuri',
        'name_local': 'Bhojpuri'
    },
    'bh': {
        'bidi': True, # right-to-left
        'code': 'bh',
        'name': 'Bihari',
        'name_local': 'Bihari'
    },
    'bra': {
        'bidi': True, # right-to-left
        'code': 'bho',
        'name': 'Braj',
        'name_local': 'Braj'
    },
    'gon': {
        'bidi': True, # right-to-left
        'code': 'gon',
        'name': 'Gondi',
        'name_local': 'Gondi'
    },
    'dra': {
        'bidi': True, # right-to-left
        'code': 'bho',
        'name': 'Dravidian',
        'name_local': 'Dravidian'
    },
    'gu': {
        'bidi': True, # right-to-left
        'code': 'gu',
        'name': 'Gujarati',
        'name_local': 'Gujarati'
    },
    'him': {
        'bidi': True, # right-to-left
        'code': 'him',
        'name': 'Himachali',
        'name_local': 'Himachali'
    },
    'ks': {
        'bidi': True, # right-to-left
        'code': 'ks',
        'name': 'Kashmiri',
        'name_local': 'Kashmiri'
    },
    'kha': {
        'bidi': True, # right-to-left
        'code': 'kha',
        'name': 'Khasi',
        'name_local': 'Khasi'
    },
    'kok': {
        'bidi': True, # right-to-left
        'code': 'kok',
        'name': 'Konkani',
        'name_local': 'Konkani'
    },
    'kru': {
        'bidi': True, # right-to-left
        'code': 'kru',
        'name': 'Kurukh',
        'name_local': 'Kurukh'
    },
    'lah': {
        'bidi': True, # right-to-left
        'code': 'lah',
        'name': 'Lahnda',
        'name_local': 'Lahnda'
    },
    'lus': {
        'bidi': True, # right-to-left
        'code': 'lus',
        'name': 'Lushai',
        'name_local': 'Lushai'
    },
    'mag': {
        'bidi': True, # right-to-left
        'code': 'mag',
        'name': 'Magahi',
        'name_local': 'Magahi'
    },
    'mai': {
        'bidi': True, # right-to-left
        'code': 'mai',
        'name': 'Maithili',
        'name_local': 'Maithili'
    },
    'mi': {
        'bidi': True, # right-to-left
        'code': 'mi',
        'name': 'Malayalam',
        'name_local': 'Malayalam'
    },
    
}
# Add custom languages not provided by Django
import django.conf.locale
LANG_INFO = dict(django.conf.locale.LANG_INFO.items() + EXTRA_LANG_INFO.items())
django.conf.locale.LANG_INFO = LANG_INFO

# Languages using BiDi (right-to-left) layout
#LANGUAGES_BIDI = global_settings.LANGUAGES_BIDI + ("mni",) 

# #SMTP setting for sending mail (Using python default SMTP server)
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
        'NAME': 'studio-dev',
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
LANGUAGE_CODE = 'de'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.

USE_I18N = True

# Setting system's default encoding to 'utf-8'
# By defalut, it's 'ascii'
# Comes handy while writing unicode text into a file
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


# Django-provide base translation in django/conf/locale.
LOCALE_PATHS = (os.path.join(os.path.dirname(__file__), '..','conf/locale/'),)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.middleware.activeuser_middleware.ActiveUserMiddleware',                 #for online_users
    # 'online_status.middleware.OnlineStatusMiddleware',                              #for online_users
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
     
# Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# AUTH_PROFILE_MODULE = 'gnowsys_ndf.ndf.models.UserProfile'

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
    'django.core.context_processors.static',
    #'django.core.context_processors.csrf',
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
    # 'gnowsys_ndf.mobwrite',	#textb
#    'south',			#textb
    # 'django_extensions',	#textb
    # 'reversion',		#textb
    # 'django.contrib.flatpages',	#textb
    # 'online_status',                       #for online_users     
#    'endless_pagination',
    'registration_email',
)

AUTHENTICATION_BACKENDS=(
'registration_email.auth.EmailBackend',
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

META_TYPE = [u"GAPP",u"factory_types",u"Mapping_relations"]

GROUP_AGENCY_TYPES=["Partner","GovernmentAgency","NGO","College","University","School","Institution","Project","SpecialInterestGroup"]

AUTHOR_AGENCY_TYPES=["Student","Teacher","TeacherTrainer","Faculty","Researcher","Others"]

# Built-in GAPPS list 
# DON'T EDIT THIS LIST - for listing purpose on gapps-menubar/gapps-iconbar, instead make use of below one in local_setting file
# ONLY TO BE EDITED - in case of adding new built-in GAPPS
GAPPS = [u"Page", u"File", u"Group", u"Image", u"Video", u"Forum", u"Quiz", u"Course", u"Module", u"Batch", u"Task", u"WikiData", u"Topics", u"E-Library", u"Meeting",u"Bib_App", u"Observation",u"Event"]

# This is to be used for listing default GAPPS on gapps-menubar/gapps-iconbar
# DON'T EDIT this variable here.
# ONLY TO BE EDITED in local_settings file
DEFAULT_GAPPS_LIST = []

# Defined all site specific variables
GSTUDIO_ORG_NAME='''<p>
A project of <a href="http://lab.gnowledge.org/" target="_blank">{% trans "Gnowledge Lab" %}</a> at the <a href="http://www.hbcse.tifr.res.in" target="_blank">Homi Bhabha Centre for Science Education (HBCSE)</a>, <a href="http://www.tifr.res.in" target="_blank">Tata Institute of Fundamental Research (TIFR), India</a>.
</p>'''

GSTUDIO_SITE_LOGO="/static/ndf/css/themes/metastudio/logo.svg"
GSTUDIO_COPYRIGHT=""
GSTUDIO_GIT_REPO="https://github.com/gnowledge/gstudio"
GSTUDIO_SITE_PRIVACY_POLICY=""
GSTUDIO_SITE_TERMS_OF_SERVICE=""
GSTUDIO_SITE_DEFAULT_LANGUAGE=u"en"
GSTUDIO_SITE_ABOUT=""
GSTUDIO_SITE_POWEREDBY=""
GSTUDIO_SITE_CONTACT=""
GSTUDIO_SITE_PARTNERS=""
GSTUDIO_SITE_GROUPS=""
GSTUDIO_ORG_LOGO=""
GSTUDIO_SITE_ORG=""
GSTUDIO_SITE_CONTRIBUTE=""
GSTUDIO_SITE_VIDEO="pandora"  #possible values are 'local','pandora' and 'pandora_and_local'
GSTUDIO_SITE_LANDING_PAGE="udashboard"  #possible values are 'home' and 'udashboard'
#GSTUDIO_SITE_EDITOR = "orgitdown"  #possible values are 'aloha'and 'orgitdown'
# Visibility for 'Create Group'
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
RCS_REPO_DIR = os.path.join(PROJECT_ROOT, "ndf/rcs-repo")


# Indicates the "hash-level-number", i.e the number of sub-directories that 
# will be created for the corresponding document under it's 
# collection-directory; in order to store json-files in an effective manner
RCS_REPO_DIR_HASH_LEVEL = 3



GSTUDIO_RESOURCES_EDUCATIONAL_USE = [ "Images", "Audios", "Videos", "Interactives", "Documents", "Maps", "Events", "Publications"]

GSTUDIO_RESOURCES_INTERACTIVITY_TYPE = [ "Active", "Expositive", "Mixed" ]

GSTUDIO_RESOURCES_EDUCATIONAL_ALIGNMENT = [ "NCF", "State", "All" ]

GSTUDIO_RESOURCES_EDUCATIONAL_LEVEL = [ "Primary", "Upper Primary", "Secondary", "Senior Secondary", "Tertiary", "Primary and Upper Primary", "Primary, Upper Primary and Secondary", "Primary, Upper Primary, Secondary and Senior Secondary", "Secondary and Senior Secondary", "Upper Primary, Secondary and Senior Secondary", "Upper Primary and Secondary", "Upper Primary and Senior Secondary" ]

GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT = [ "Language", "Mathematics", "Environmental Studies", "Science", "Chemistry", "Physics", "Biology", "Social Science", "History", "Geography", "Political Science", "Economics", "Sociology", "Psychology", "Commerce", "Business Studies", "Accountancy" ]

GSTUDIO_RESOURCES_CURRICULAR = [ "True", "False" ]

GSTUDIO_RESOURCES_AUDIENCE = [ "Teachers", "Students", "Teacher educators", "Teachers and Students", "Teachers, Students and Teacher educators" ]

GSTUDIO_RESOURCES_TEXT_COMPLEXITY = [ "Easy", "Moderately Easy", "Intermediate", "Moderately Hard", "Hard" ]

GSTUDIO_RESOURCES_LANGUAGES = [ "English","Gujarati" ,"Hindi" ,"Manipuri" ,"Marathi" ,"Mizo" ,"Telugu" ]

GSTUDIO_RESOURCES_AGE_RANGE = [ "5-10","11-20", "21-30", "31-40", "41 and above" ] 

GSTUDIO_RESOURCES_TIME_REQUIRED = [ "0-2M","2-5M", "5-15M", "15-45M" ]

GSTUDIO_RESOURCES_AGE_RANGE = [ "5-10","11-20", "21-30", "31-40", "41 and above" ] 

GSTUDIO_RESOURCES_READING_LEVEL = [  ] 

GSTUDIO_TASK_TYPES = ["Bug", "Feature", "Support", "UI Feature", "Other"]


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

# USERS_ONLINE__TIME_IDLE = 300
# USERS_ONLINE__TIME_OFFLINE = 10
#USERS_ONLINE__CACHE_PREFIX_USER
#USERS_ONLINE__CACHE_USERS
