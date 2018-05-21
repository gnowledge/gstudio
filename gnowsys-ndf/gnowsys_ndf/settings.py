# Django settings for gnowsys-ndf project.

# imports from python libraries
import os
import djcelery

# imports from core django libraries
# from django.conf import global_settings
# from django.utils.translation import ugettext
# from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS

# imports from third-party app(s)

# from gnowsys_ndf.ndf.utils import (is_dir_exists, ensure_dir, get_current_dbs_path,
#     move_file_or_dirctory)

DEBUG = False
ALLOWED_HOSTS = ["*"]

TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG
BENCHMARK = "ON"
GSTUDIO_DEFAULT_GROUPS_LIST = ['home', 'Trash', 'desk', 'help', 'warehouse']
GROUP_SETTING_1 = {'edit_policy': 'NON_EDITABLE'}
GROUP_SETTING_2 = {'edit_policy': 'EDITABLE_NON_MODERATED'}

GSTUDIO_DEFAULT_FACTORY_GROUPS = {'home': GROUP_SETTING_1,
             'warehouse':GROUP_SETTING_2, 'Trash': GROUP_SETTING_1,
             'desk': GROUP_SETTING_2, 'help': GROUP_SETTING_2}

GSTUDIO_ALTERNATE_OPTS = ['Size', 'Format', 'Language','Content','Other']
GSTUDIO_ALTERNATE_FORMATS = {'image':['png','jpeg'],'video':['mkv','webm'],'audio':['mp3']}
GSTUDIO_ALTERNATE_SIZE = {'image':['100px','1048px'],'video':['144px','720px'],'audio':['128kbps']}
GSTUDIO_DEFAULT_GROUP = u'desk'
GSTUDIO_EDUCATIONAL_SUBJECTS_AS_GROUPS = False

LANGUAGES = (('en', 'English'), ('hi', 'Hindi'), ('te', 'Telugu'))
HEADER_LANGUAGES = (('en', 'English'), ('hi', u'\u0939\u093f\u0902\u0926\u0940'),('te', u'\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41'))
GSTUDIO_DEFAULT_LANGUAGE = ('en', 'English')
GSTUDIO_WORKSPACE_INSTANCE = False
GSTUDIO_IMPLICIT_ENROLL = False
OTHER_COMMON_LANGUAGES = [
    ('mr', 'Marathi'), ('mni','Manipuri'), ('ori','Oriya'),
    ('pi','Pali'), ('raj','Rajasthani'), ('gu','Gujarati'),
    ('ks','Kashmiri'), ('kok','Konkani'), ('kha','Khasi'),
    ('dra','Dravidian'), ('gon','Gondi'), ('bra','Braj'),
    ('mi','Malayalam'), ('mai','Maithili'), ('mag','Magahi'),
    ('lus','Lushai'), ('bho','Bhojpuri'), ('kru','Kurukh'),
    ('awa','Awadhi'), ('sa','Sanskrit'), ('sat','Santali'),
    ('him','Himachali'), ('sd','Sindhi'), ('as','Assamese'),
    ('ar', 'Arabic'), ('bn', 'Bengali'), ('ca', 'Catalan'),
    ('bho','Bhojpuri'), ('da', 'Danish'), ('de', 'German'),
    ('el', 'Greek'), ('en-gb', 'British English'), ('eo', 'Esperanto'),
    ('es', 'Spanish'), ('es-ar', 'Argentinian Spanish'),
    ('es-mx', 'Mexican Spanish'), ('es-ni', 'Nicaraguan Spanish'),
    ('es-ve', 'Venezuelan Spanish'), ('et', 'Estonian'),
    ('fa', 'Persian'), ('fi', 'Finnish'), ('fr', 'French'),
    ('ga', 'Irish'), ('he', 'Hebrew'), ('hu', 'Hungarian'),
    ('id', 'Indonesian'), ('is', 'Icelandic'), ('it', 'Italian'),
    ('ja', 'Japanese'), ('ka', 'Georgian'), ('kk', 'Kazakh'),
    ('km', 'Khmer'), ('kn', 'Kannada'), ('ko', 'Korean'),
    ('lb', 'Luxembourgish'), ('lt', 'Lithuanian'), ('lv', 'Latvian'),
    ('mk', 'Macedonian'), ('ml', 'Malayalam'), ('mn', 'Mongolian'),
    ('my', 'Burmese'), ('ne', 'Nepali'), ('nl', 'Dutch'),
    ('pa', 'Punjabi'), ('pl', 'Polish'), ('pt', 'Portuguese'),
    ('pt-br', 'Brazilian Portuguese'), ('ro', 'Romanian'), ('ru', 'Russian'),
    ('sk', 'Slovak'), ('sl', 'Slovenian'), ('sq', 'Albanian'), ('sr', 'Serbian'),
    ('sr-latn', 'Serbian Latin'), ('sv', 'Swedish'), ('sw', 'Swahili'),
    ('ta', 'Tamil'), ('te', 'Telugu'), ('th', 'Thai'), ('tr', 'Turkish'),
    ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('vi', 'Vietnamese'),
    ('zh-cn', 'Simplified Chinese'), ('zh-tw', 'Traditional Chinese')
]

EXTRA_LANG_INFO = {
    'mr': {
        'bidi': True,  # right-to-left
        'code': 'mr',
        'name': 'Marathi',
        'name_local': 'Marathi'
    },
    'mun': {
        'bidi': True,  # right-to-left
        'code': 'mun',
        'name': 'Munda',
        'name_local': 'Munda'
    },

    'mni': {
        'bidi': True,  # right-to-left
        'code': 'ug',
        'name': 'Manipuri',
        'name_local': 'Manipuri'
    },
    'ori': {
        'bidi': True,  # right-to-left
        'code': 'ori',
        'name': 'Oriya',
        'name_local': 'Oriya'
    },
    'mr': {
        'bidi': True,  # right-to-left
        'code': 'mr',
        'name': 'Marathi',
        'name_local': 'Marathi'
    },
    'pi': {
        'bidi': True,  # right-to-left
        'code': 'pi',
        'name': 'Pali',
        'name_local': 'Pali'
    },
    'raj': {
        'bidi': True,  # right-to-left
        'code': 'raj',
        'name': 'Rajasthani',
        'name_local': 'Rajasthani'
    },
    'sa': {
        'bidi': True,  # right-to-left
        'code': 'sa',
        'name': 'Sanskrit',
        'name_local': 'Sanskrit'
    },

    'sat': {
        'bidi': True,  # right-to-left
        'code': 'sat',
        'name': 'Santali',
        'name_local': 'Santali'
    },
    'sd': {
        'bidi': True,  # right-to-left
        'code': 'sa',
        'name': 'Sindhi',
        'name_local': 'Sindhi'
    },
    'as': {
        'bidi': True,  # right-to-left
        'code': 'as',
        'name': 'Assamese',
        'name_local': 'Assamese'
    },
    'awa': {
        'bidi': True,  # right-to-left
        'code': 'awa',
        'name': 'Awadhi',
        'name_local': 'Awadhi'
    },
    'bho': {
        'bidi': True,  # right-to-left
        'code': 'bho',
        'name': 'Bhojpuri',
        'name_local': 'Bhojpuri'
    },
    'bh': {
        'bidi': True,  # right-to-left
        'code': 'bh',
        'name': 'Bihari',
        'name_local': 'Bihari'
    },
    'bra': {
        'bidi': True,  # right-to-left
        'code': 'bho',
        'name': 'Braj',
        'name_local': 'Braj'
    },
    'gon': {
        'bidi': True,  # right-to-left
        'code': 'gon',
        'name': 'Gondi',
        'name_local': 'Gondi'
    },
    'dra': {
        'bidi': True,  # right-to-left
        'code': 'bho',
        'name': 'Dravidian',
        'name_local': 'Dravidian'
    },
    'gu': {
        'bidi': True,  # right-to-left
        'code': 'gu',
        'name': 'Gujarati',
        'name_local': 'Gujarati'
    },
    'him': {
        'bidi': True,  # right-to-left
        'code': 'him',
        'name': 'Himachali',
        'name_local': 'Himachali'
    },
    'ks': {
        'bidi': True,  # right-to-left
        'code': 'ks',
        'name': 'Kashmiri',
        'name_local': 'Kashmiri'
    },
    'kha': {
        'bidi': True,  # right-to-left
        'code': 'kha',
        'name': 'Khasi',
        'name_local': 'Khasi'
    },
    'kok': {
        'bidi': True,  # right-to-left
        'code': 'kok',
        'name': 'Konkani',
        'name_local': 'Konkani'
    },
    'kru': {
        'bidi': True,  # right-to-left
        'code': 'kru',
        'name': 'Kurukh',
        'name_local': 'Kurukh'
    },
    'lah': {
        'bidi': True,  # right-to-left
        'code': 'lah',
        'name': 'Lahnda',
        'name_local': 'Lahnda'
    },
    'lus': {
        'bidi': True,  # right-to-left
        'code': 'lus',
        'name': 'Lushai',
        'name_local': 'Lushai'
    },
    'mag': {
        'bidi': True,  # right-to-left
        'code': 'mag',
        'name': 'Magahi',
        'name_local': 'Magahi'
    },
    'mai': {
        'bidi': True,  # right-to-left
        'code': 'mai',
        'name': 'Maithili',
        'name_local': 'Maithili'
    },
    'mi': {
        'bidi': True,  # right-to-left
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
# LANGUAGES_BIDI = global_settings.LANGUAGES_BIDI + ("mni",)


# --- mailclient app and Replication ---
#
# GSTUDIO_SYNC_SND=True/False
# GSTUDIO_SYNC_RCV=True/False
#
# Following has to be done for using the Replication features
# Override following variables in local_settings file:
#
# SMTP setting for sending mail (Using python default SMTP server)
EMAIL_USE_TLS = False
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'testing@example.com'
#
# SMTP setting for sending mail (e.g: gmail SMTP server)
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'yourcompletegmailaddr'
# EMAIL_HOST_PASSWORD = 'yourpassword'
#
# The following email id and password for the email account will be used for sending/receiving SYNCDATA
SYNCDATA_KEY_PUB = ""
SYNCDATA_FROM_EMAIL_ID = ""
#
SYNCDATA_SENDING_EMAIL_ID = ""
SYNCDATA_FETCHING_EMAIL_ID = ''
#
SYNCDATA_FETCHING_EMAIL_ID_PASSWORD = ''
SYNCDATA_FETCHING_IMAP_SERVER_ADDRESS = ''
#
# This is the duration (in secs) at which send_syncdata and fetch_syncdata scripts will be run
SYNCDATA_DURATION = 60
#
# Mail Chunk Size in MB
TARSIZE = 1000
#
# --- END of mailclient app and Replication ---


# Use following if you want people to have to log in every time they open a browser.
# It clears the session on browser close (but chrome may behave to prevent sessions from expiring on browser close)
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# strength of a password
PASSWORD_MIN_LENGTH = 8
PASSWORD_COMPLEXITY = {  # You can ommit any or all of these for no limit for that particular set
    "UPPER": 1,       # Uppercase
    "LOWER": 1,       # Lowercase
    "DIGITS": 1,      # Digits
}

# Absolute filesystem path to the project's base directory,
# i.e. having settings.py file
# Example: "/.../project-name/app-name/"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Absolute filesystem path to the project's data directory,
# i.e. common place to store all database(s)
# Example: "/home/<user-name>/data/"
# Don't edit this below path
GSTUDIO_DATA_ROOT = os.path.join(os.path.expanduser("~/"), 'gstudio_data')

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Don't edit default database's NAME attribute
# If overridden in local settings file, then
# follow the same pattern and edit only the database-name
SQLITE3_DBNAME = 'example-sqlite3.db'
SQLITE3_DB_PATH = os.path.join(GSTUDIO_DATA_ROOT, SQLITE3_DBNAME)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': SQLITE3_DB_PATH,
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
# MEDIA_ROOT = 'gnowsys_ndf/ndf/static/'
MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ndf/static/media')

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
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '7st0sdv&amp;7yw*eh)zmaz8#t48nr$&amp;ql#ow=$0l^#b_b&amp;$9c*$4c'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #  'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.middleware.activeuser_middleware.ActiveUserMiddleware',                 #for online_users
    # 'online_status.middleware.OnlineStatusMiddleware',                              #for online_users
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',

    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # gstudio custom middleware(s):
    'gnowsys_ndf.ndf.middleware.SetData.UserDetails',
    'gnowsys_ndf.ndf.middleware.SetData.Author',
    'gnowsys_ndf.ndf.middleware.SetData.AdditionalDetails',
    # 'gnowsys_ndf.ndf.middleware.Buddy.BuddySession',
    'gnowsys_ndf.ndf.middleware.UserRestrictMiddleware.UserRestrictionMiddleware',

    # for profiling methods:
    # 'gnowsys_ndf.ndf.middleware.ProfileMiddleware.ProfileMiddleware',
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
    'django.core.context_processors.media',
    # 'django.core.context_processors.csrf',
)


djcelery.setup_loader()
# # CELERY_RESULT_BACKEND = "mongodb"
CELERY_RESULT_BACKEND = "djcelery.backends.database:DatabaseBackend"
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

CELERY_TASK_SERIALIZER = "json"
CELERY_IMPORTS = ("gnowsys_ndf.ndf.views.tasks")
# # BROKER_URL = 'mongodb://localhost:27017/' + DATABASES['mongodb']['NAME']
BROKER_URL = 'amqp://'

INSTALLED_APPS = (
    'gnowsys_ndf.ndf',
    # 'dlkit',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration',
    'notification',
    'pagination',
    'captcha',
    # 'gnowsys_ndf.benchmarker',
    # 'django.contrib.flatpages',   #textb
    # 'django_extensions',          #textb
    # 'djangoratings',
    # 'gnowsys_ndf.mobwrite',       #textb
    # 'south',                      #textb
    # 'reversion',                  #textb
    # 'online_status',              #for online_users
    # 'endless_pagination',
    # 'jsonrpc',
    'registration_email',
    'memcache_admin',
    'django_mailbox',
    'djcelery',
    #'dlkit',
    #'dlkit_runtime'
)

AUTHENTICATION_BACKENDS = (
    'registration_email.auth.EmailBackend',
)

ACCOUNT_ACTIVATION_DAYS = 2  # Two days for activation.

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

# Binary - Only meant for RelationType's document to represent
# Binary relationship, especially defined to differentiate
# from other relationship(s), i.e. Triadic, etc.
# Example (Binary): A >> son-of >> [B]
# Example (Triadic): A >> teaches-course-in-college >> [Course, College]
META_TYPE = [
    u"GAPP", u"factory_types", u"Mapping_relations", u"Binary", u"Triadic"
]

GSTUDIO_GROUP_AGENCY_TYPES = [
    "Other", "Partner", "GovernmentAgency", "NGO", "College", "University",
    "School", "Institution", "Project", "SpecialInterestGroup"
]
GSTUDIO_GROUP_AGENCY_TYPES_DEFAULT = 'Other'

GSTUDIO_AUTHOR_AGENCY_TYPES = [
    "Student", "Teacher", "Teacher Educator", "Faculty", "Researcher", "Other"
]

# Varible to toggle the visibility of author_agency_type field of Author
# class in User-registration template (shown as Occupation)
GSTUDIO_REGISTRATION_AUTHOR_AGENCY_TYPE = True

# Varible to toggle the visibility of group_affiliation field of Author
# class in User-registration template (shown as Organization)
GSTUDIO_REGISTRATION_AFFILIATION = True

# Built-in GAPPS list
# ONLY TO BE EDITED - in case of adding new built-in GAPPS
GAPPS = [
    u"Page", u"File", u"Group", u"Image", u"Video", u"Forum", u"Quiz",
    u"Course", u"Module", u"Batch", u"Task", u"WikiData", u"Topics",
    u"E-Library", u"Meeting", u"Bib_App", u"Observation", u"Event", u"E-Book"
]

# This holds the list of stable GAPPS
# ONLY TO BE EDITED in local_settings file
# In order to edit (redorderig purpose or adding new ones) this list,
# please make use of local_settings file
GSTUDIO_WORKING_GAPPS = [
    u"Page", u"File", u"E-Library", u"Forum", u"Task", u"Topics",
    u"Course", u"Observation", u"Event", u"Quiz"
]

GSTUDIO_REGISTRATION = True

GSTUDIO_SECOND_LEVEL_HEADER = True
GSTUDIO_MY_GROUPS_IN_HEADER = True
GSTUDIO_MY_COURSES_IN_HEADER = False
GSTUDIO_MY_DASHBOARD_IN_HEADER = False
GSTUDIO_DEFAULT_EXPLORE_URL = "explore_courses"
 #GSTUDIO_DEFAULT_EXPLORE_URL it defines url which will be loaded when user clicks on explore button
 # e.g explore_courses will go to explore/courses url. likewise options are explore_groups and explore_basecourses
GSTUDIO_REPLICATION_GROUPS = [
    u"Author", u"home"
]

# This is to be used for listing default GAPPS on gapps-menubar/gapps-iconbar
# if not set by specific group
# DON'T EDIT this variable here.
# ONLY TO BE EDITED in local_settings file
GSTUDIO_DEFAULT_GAPPS_LIST = []
GSTUDIO_USER_GAPPS_LIST = ['Page', 'File', 'Task', 'Course', 'Event', 'Quiz']

# Defined all site specific variables
GSTUDIO_ORG_NAME = '''<p>
A project of <a href="http://lab.gnowledge.org/" target="_blank">{% trans "Gnowledge Lab" %}</a> at the <a href="http://www.hbcse.tifr.res.in" target="_blank">Homi Bhabha Centre for Science Education (HBCSE)</a>, <a href="http://www.tifr.res.in" target="_blank">Tata Institute of Fundamental Research (TIFR), India</a>.
</p>'''
GSTUDIO_SITE_FAVICON = "/static/ndf/images/favicon/logo.png"
GSTUDIO_SITE_LOGO = "/static/ndf/css/themes/metastudio/logo.svg"
GSTUDIO_SITE_SECONDARY_LOGO = "/static/ndf/css/themes/metastudio/logo.svg"
GSTUDIO_GIT_REPO = "https://github.com/gnowledge/gstudio"
GSTUDIO_SITE_PRIVACY_POLICY = ""
GSTUDIO_SITE_TERMS_OF_SERVICE = ""
GSTUDIO_SITE_DEFAULT_LANGUAGE = u"en"
GSTUDIO_SITE_ABOUT = ""
GSTUDIO_SITE_POWEREDBY = ""
GSTUDIO_SITE_CONTACT = ""
GSTUDIO_SITE_PARTNERS = ""
GSTUDIO_SITE_GROUPS = ""
GSTUDIO_ORG_LOGO = ""
GSTUDIO_SITE_ORG = ""
GSTUDIO_SITE_CONTRIBUTE = ""
GSTUDIO_SITE_VIDEO = "pandora_and_local"  # possible values are 'local','pandora' and 'pandora_and_local'
GSTUDIO_SITE_LANDING_PAGE = "home"  # possible values are 'home' and 'udashboard'
GSTUDIO_SITE_LANDING_TEMPLATE = ""  # possible value is template name.
GSTUDIO_SITE_HOME_PAGE = None  # it is url rendered on template. e.g: "/welcome". Default is: "/home"
GSTUDIO_SITE_NAME = "metaStudio"  # holds the name of site. e.g: "NROER, "tiss" etc. (Override it in local_settings)
GSTUDIO_SITE_ISSUES_PAGE = ""
GSTUDIO_EBOOKS_HELP_TEXT = "" #ebook help text page  url(page:"how to read ebooks")
GSTUDIO_SUPPORTED_JHAPPS = ['Jsmol','Police Squad','OpenStoryTool','BioMechanics', 'TurtleBlocks']
GSTUDIO_EDIT_LMS_COURSE_STRUCTURE = False
# terms & conditions
GSTUDIO_OID_TC = None
GSTUDIO_OID_HELP = ""
# GSTUDIO_SITE_EDITOR = "orgitdown"  #possible values are 'aloha'and 'orgitdown'
# Visibility for 'Create Group'
CREATE_GROUP_VISIBILITY = True
GSTUDIO_DEFAULT_SYSTEM_TYPES_LIST = []
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
RCS_REPO_DIRNAME = "rcs-repo"
RCS_REPO_DIR = os.path.join(GSTUDIO_DATA_ROOT, RCS_REPO_DIRNAME)

GSTUDIO_LOGS_DIRNAME = 'gstudio-logs'
GSTUDIO_LOGS_DIR_PATH = os.path.join(GSTUDIO_DATA_ROOT, GSTUDIO_LOGS_DIRNAME)

GSTUDIO_EPUBS_LOC_NAME = 'gstudio-epubs'
GSTUDIO_EPUBS_LOC_PATH = os.path.join(GSTUDIO_DATA_ROOT, GSTUDIO_EPUBS_LOC_NAME)

GSTUDIO_MAIL_DIRNAME = 'MailClient'
GSTUDIO_MAIL_DIR_PATH = os.path.join(GSTUDIO_DATA_ROOT, GSTUDIO_MAIL_DIRNAME)

# Indicates the "hash-level-number", i.e the number of sub-directories that
# will be created for the corresponding document under it's
# collection-directory; in order to store json-files in an effective manner
RCS_REPO_DIR_HASH_LEVEL = 3

GSTUDIO_RESOURCES_EDUCATIONAL_USE = ["Images", "Audios", "Videos", "Interactives", "Documents", "eBooks", "Maps", "Events", "Publications"]

GSTUDIO_RESOURCES_INTERACTIVITY_TYPE = ["Active", "Expositive", "Mixed"]

GSTUDIO_RESOURCES_EDUCATIONAL_ALIGNMENT = ["NCF", "State", "All"]

GSTUDIO_RESOURCES_EDUCATIONAL_LEVEL = ["Primary", "Upper Primary", "Secondary", "Senior Secondary", "Tertiary"]

GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT = ["Language", "Mathematics", "Environmental Studies", "Science", "Chemistry", "Physics", "Biology", "Social Science", "History", "Geography", "Political Science", "Economics", "Sociology", "Psychology", "Commerce", "Business Studies", "Accountancy", "Art", "Education"]

GSTUDIO_RESOURCES_CURRICULAR = ["True", "False"]

GSTUDIO_RESOURCES_AUDIENCE = ["Teachers", "Students", "Teacher educators"]

GSTUDIO_RESOURCES_TEXT_COMPLEXITY = ["Easy", "Moderately Easy", "Intermediate", "Moderately Hard", "Hard"]

GSTUDIO_RESOURCES_LANGUAGES = ["English", "Gujarati", "Hindi", "Manipuri", "Marathi", "Mizo", "Telugu"]

GSTUDIO_RESOURCES_AGE_RANGE = ["5-10", "11-20", "21-30", "31-40", "41 and above"]

GSTUDIO_RESOURCES_TIME_REQUIRED = ["0-2M", "2-5M", "5-15M", "15-45M"]

GSTUDIO_RESOURCES_AGE_RANGE = ["5-10", "11-20", "21-30", "31-40", "41 and above"]

GSTUDIO_RESOURCES_READING_LEVEL = ["Primary", "Upper Primary", "Secondary", "Senior Secondary", "Tertiary"]

GSTUDIO_TASK_TYPES = ["Bug", "Feature", "Support", "UI Feature", "Moderation", "Other"]

GSTUDIO_NROER_MENU = [{"Repository": []}, {"Partners": ["States", "Institutions", "Individuals"]}, {"Groups":["Teachers", "Interest Groups", "Schools"]}]

GSTUDIO_NROER_GAPPS = [{"Themes": "topics"}, {"eLibrary": "e-library"}, {"eBooks": "e-book"}, {"eCourses": "course"}, {"Events": "program"}]

GSTUDIO_NROER_MENU_MAPPINGS = {
            "States": "State Partners", "Institutions": "Institutional Partners", "Individuals": "Individual Partners",
            "Teachers": "Teachers", "Interest Groups": "Interest Groups", "Schools": "Schools"
            }

GSTUDIO_FILTERS = {
            "File": ['educationallevel', 'audience', 'language', 'educationalsubject', 'source'],
            "E-Library": ['educationallevel', 'audience', 'language', 'educationalsubject', 'source'],
            "E-Book": ['educationallevel', 'audience', 'language', 'educationalsubject'],
            "Topics": ['educationallevel', 'audience', 'language', 'educationalsubject', 'educationaluse']
            }

GSTUDIO_COURSE_FILTERS_KEYS = ["created_by", "tags"]

GSTUDIO_RESOURCES_CREATION_RATING = 5

GSTUDIO_RESOURCES_REGISTRATION_RATING = 5

GSTUDIO_RESOURCES_REPLY_RATING = 2

# the level of moderation means level of sub mode group hierarchy
GSTUDIO_GROUP_MODERATION_LEVEL = 1

# allowed moderation levels
GSTUDIO_ALLOWED_GROUP_MODERATION_LEVELS = [1, 2, 3]

GSTUDIO_COPYRIGHT = ["CC BY-SA", "CC BY", "CC BY-NC-SA", "CC BY-NC-ND", "CC BY-ND", "PUBLIC-DOMAIN", "FDL (FREE DOCUMENTATION LICENSE)", "NCERT License", "OTHERS"]

GSTUDIO_DEFAULT_COPYRIGHT = 'CC-BY-SA 4.0 unported'

GSTUDIO_DEFAULT_LICENSE = 'HBCSE'

GSTUDIO_FILE_UPLOAD_FORM = 'simple'  # possible values are 'simple' or 'detail'

GSTUDIO_MODERATING_GROUP_ALTNAMES = ['Clearing House', 'Curation House']

GSTUDIO_COURSE_EVENT_MOD_GROUP_ALTNAMES = ['Screening House', 'Selection House']

GSTUDIO_PROGRAM_EVENT_MOD_GROUP_ALTNAMES = ['Screening House', 'Selection House']

GSTUDIO_DOC_FOOTER_TEXT = "gStudio, Gnowledge Lab"

GSTUDIO_HELP_TIP = {
   "name":"Title of the object",
   "altnames":"Alternate title",
   "language":"Language of the title",
   "subject_type":"The system types that can hold this property",
   "data_type":"Data Type",
   "applicable_node_type":"Applicable Node Type",
   "member_of":"Member of MetaType ",
   "verbose_name":"Verbose Name",
   "null":"Value can be null",
   "blank":"Value can be blank",
   "max_digits":"Maximum length of digits applicable if the data type is any type of numbers ",
   "decimal_places":" Number of decimal places if the data type is float",
   # "auto_now":"The value is automatically filled by the computer",
   "auto_now_add":"Auto now would insert time only if the auto now field is true",
   "path":"Path",
   "verify_exist":"Verify Exist",
   "status":"Status",
   "content_org":"Description",
   "validators":"Regular Expressions required for Validation",
   "help_text":"The help text to be displayed on the Tooltip for GSystem ",
   "prior_node":"This node depends on",
   "featured":"Featured",
   "created_at":"Time of creation",
   "start_publication":"Published from the date",
   "tags":"Tags are keywords",
   "url":"URL",
   "last_update":"The time of modification ",
   "login_required":"Login required",
   "meta_type_set":"N/A",
   "attribute_type_set":"N/A",
   "relation_type_set":"N/A",
   "type_of":"Sub Attribute type of"
 }

GSYSTEMTYPE_DEFINITIONLIST = [
   {
      "name":"Name "
   },
   {
      "altnames":"Alternate Name "
   },
   {
      "language":"Language "
   },
   {
      "status":"Status "
   },
   {
      "member_of":"Member of MetaType "
   },
   {
      "meta_type_set":"Select the MetaType "
   },
   {
      "attribute_type_set":"Select the AttributeType "
   },
   {
      "relation_type_set":"Select the RelationType "
   },
   {
      "type_of":"Type Of "
   }
]

ATTRIBUTETYPE_DEFINITIONLIST = [
   {
      "name":"Name "
   },
   {
      "altnames":"Alternate Name "
   },
   {
      "language":"Language "
   },
   {
      "subject_type":"Subject Type "
   },
   {
      "data_type":"Data Type "
   },
   {
      "member_of":"Member of MetaType "
   },
   {
      "verbose_name":"Verbose Name "
   },
   {
      "null":"Null "
   },
   {
      "blank":"Blank "
   },
   {
      "help_text":"Help Text "
   },
   {
      "max_digits":"Maximum Digits "
   },
   {
      "decimal_places":"Decimal Places "
   },
   # {
      # "auto_now":"Auto Now "
   # },
   {
      "auto_now_add":"Auto Now Add "
   },
   {
      "path":"Path "
   },
   {
      "verify_exist":"Verify Existence "
   },
   {
      "validators":"Validators"
   },
   {
      "status":"Status "
   }
]

RELATIONTYPE_DEFINITIONLIST = [
   {
      "name":"Name "
   },
   {
      "inverse_name":"Inverse Name "
   },
   {
      "altnames":"Alternate Name "
   },
   {
      "language":"Language "
   },
   {
      "subject_type":"Subject Type "
   },
   {
      "object_type":"Object Type "
   },
   {
      "subject_cardinality":"Subject Cardinality "
   },
   {
      "object_cardinality":"Object Cardinality "
   },
   {
      "subject_applicable_nodetype":"Subject Applicable Node Type "
   },
   {
      "object_applicable_nodetype":"Object Applicable Node Type "
   },
   {
      "is_symmetric":"Is Symmetric "
   },
   {
      "is_reflexive":"Is Reflexive "
   },
   {
      "is_transitive":"Is Transitive "
   },
   {
      "status":"Status "
   },
   {
      "member_of":"Member of MetaType "
   }
]

CONTENTLIST = [{'content_org':'content organization' }]

DEPENDENCYLIST = [{'prior_node':'Prior Node ' }]

OPTIONLIST = [
   {
      "featured":"Featured "
   },
   {
      "created_at":"Created At "
   },
   {
      "start_publication":"Start Publication "
   },
   {
      "tags":"Tags "
   },
   {
      "url":"URL "
   },
   {
      "last_update":"Last Update "
   },
   {
      "login_required":"Login Required "
   }
]

GSYSTEM_LIST = [{'name':'Name '} ,{'altnames':'Alternate Name '}]

GSTUDIO_INTERACTION_TYPES = ['Comment', 'Discuss', 'Reply', 'Post', 'Submit', 'Voice-Response', 'Answer', 'Feedback']
DEFAULT_DISCUSSION_LABEL = 'Feedback'
# #textb
# import warnings
# warnings.filterwarnings(
#         'error', r"DateTimeField received a naive datetime",
#         RuntimeWarning, r'django\.db\.models\.fields')
# #textb

# cache implementation with memcached and python-memcached binding:
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 300,  #  60 * 5 = 300 seconds or 5 minutes
    }
}


# Captcha settings
CAPTCHA_CHALLENGE_FUNCT =  'captcha.helpers.random_char_challenge'
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_arcs','captcha.helpers.noise_dots',)

GSTUDIO_HELP_SIDEBAR = False
GSTUDIO_SOCIAL_SHARE_RESOURCE = False
GSTUDIO_TWITTER_VIA = "atMetaStudio"
GSTUDIO_CAPTCHA_VISIBLE = False
GSTUDIO_FACEBOOK_APP_ID = ""
# the no of cards/objects/instances to be render of app (listing view).
GSTUDIO_NO_OF_OBJS_PP = 24
GSTUDIO_FILE_UPLOAD_POINTS = 25
GSTUDIO_NOTE_CREATE_POINTS = 30
GSTUDIO_QUIZ_CORRECT_POINTS = 5
GSTUDIO_COMMENT_POINTS = 5
GSTUDIO_ENABLE_USER_DASHBOARD = True
GSTUDIO_PRIMARY_COURSE_LANGUAGE = u'en'

# --- BUDDY Module configurations ---
#
GSTUDIO_BUDDY_LOGIN = False
GSTUDIO_USERNAME_SELECTION_WIDGET = False
GSTUDIO_INSTITUTE_ID = ''
GSTUDIO_INSTITUTE_ID_SECONDARY = ''
GSTUDIO_INSTITUTE_NAME = ''
#
# --- End of BUDDY Module ---


# # textb
# import warnings
# warnings.filterwarnings(
#         'error', r"DateTimeField received a naive datetime",
#         RuntimeWarning, r'django\.db\.models\.fields')
# # textb


# --- meeting gapp ---
#
# for online_users_ramk:
#
# USER_ONLINE_TIMEOUT = 300
# USER_LASTSEEN_TIMEOUT = 60 * 60 * 24 * 7
# USERS_ONLINE__TIME_IDLE = 300
# USERS_ONLINE__TIME_OFFLINE = 10
# USERS_ONLINE__CACHE_PREFIX_USER
# USERS_ONLINE__CACHE_USERS
#
# --- END of meeting gapp ---




# ----------------------------------------------------------------------------
# following has to be at last
# just put every thing above it

try:
    from local_settings import *
    # print "Local settings applied"
except:
    # print "Default settings applied"
    pass

# ========= nothing to be added below this line ===========
