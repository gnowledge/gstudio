#------------------------------------------ Changing the website instances(Logo and database etc) -------------------------------------------------
DEBUG = True
# DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "*"]
# GSTUDIO_CLIX_LOGIN_TEMPLATE = 'clix_school'
import os
GSTUDIO_INSTITUTE_ID = 'mz1'
GSTUDIO_INSTITUTE_ID_SECONDARY = '0980KJH'
GSTUDIO_INSTITUTE_NAME = 'TEST SCHOOL'
# Authentication related and Error reporting emails
EMAIL_USE_TLS = ""
ACCOUNT_ACTIVATION_DAYS = 2
EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = 'webmaster@clix.ss.org'
LOGIN_REDIRECT_URL = '/'
EMAIL_SUBJECT_PREFIX='[clix-ss-error-reporting]'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_PORT = ""
ADMINS = ()
GSTUDIO_PRIMARY_COURSE_LANGUAGE = u'te'

# GSTUDIO_SOCIAL_SHARE_RESOURCE = True
GSTUDIO_SOCIAL_SHARE_RESOURCE = False
GSTUDIO_TWITTER_VIA = "atMetaStudio"
GSTUDIO_FACEBOOK_APP_ID = "146799965703412"


#*******MIO_SETTINGS*************
GSTUDIO_MIO_FROM_EMAIL = 'ps.mio.bits@gmail.com'
GSTUDIO_MIO_FROM_EMAIL_PASSWORD = '1Guesswhat'
#*********************************


# strength of a password
PASSWORD_MIN_LENGTH = 6
PASSWORD_COMPLEXITY = {  # You can ommit any or all of these for no limit for that particular set
    "LOWER": 1,       # Lowercase
#    "UPPER": 1,       # Uppercase
#    "DIGITS": 1,      # Digits
}

GSTUDIO_SITE_NAME = "NROER"
#GSTUDIO_SITE_NAME = "clix"
GSTUDIO_SITE_LANDING_TEMPLATE = "ndf/landing_page_nroer.html"
GSTUDIO_SITE_LOGO = "/static/ndf/css/themes/clix/logo.svg"
GSTUDIO_SITE_FAVICON = "/static/ndf/images/favicon/clix-favicon.png"
GSTUDIO_SITE_HOME_PAGE = "/welcome"
# GSTUDIO_DEFAULT_EXPLORE_URL = "explore_basecourses"

GSTUDIO_CAPTCHA_VISIBLE = False
GSTUDIO_MY_GROUPS_IN_HEADER = False
GSTUDIO_MY_COURSES_IN_HEADER = True
GSTUDIO_SECOND_LEVEL_HEADER = False
GSTUDIO_MY_DASHBOARD_IN_HEADER = True

# SESSION_COOKIE_AGE = 60
# SESSION_SAVE_EVERY_REQUEST = True
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True

GSTUDIO_BUDDY_LOGIN = True
# GSTUDIO_BUDDY_LOGIN = False
GSTUDIO_REGISTRATION = False
GSTUDIO_ELASTIC_SEARCH = True

# Deatils related to database
MEDIA_ROOT = '/data/media/'
GSTUDIO_OID_HELP = "593bddae7ab85b4693d45283"
GSTUDIO_DATA_ROOT = os.path.join('/data/')

GSTUDIO_LOGS_DIRNAME = 'gstudio-logs'
GSTUDIO_LOGS_DIR_PATH = os.path.join('/data/', GSTUDIO_LOGS_DIRNAME)

RCS_REPO_DIRNAME = 'rcs-repo'
RCS_REPO_DIR = os.path.join('/data/', RCS_REPO_DIRNAME)

GSTUDIO_MAIL_DIRNAME = 'MailClient'
GSTUDIO_MAIL_DIR_PATH = os.path.join('/data/', GSTUDIO_MAIL_DIRNAME)

SQLITE3_DBNAME = 'example-sqlite3.db'                                       # Used for sqlite3 db
SQLITE3_DB_PATH = os.path.join('/data/', SQLITE3_DBNAME)                    # Used for sqlite3 db

MONGODB_DBNAME = 'gstudio-mongodb'

DATABASES = {
    'default': {
    # We have 2 database (postgres and sqlite3) connection details here. Ensure the part of connection details of database not in use is commented.
        # 'ENGINE': 'django.db.backends.sqlite3',				# Used for sqlite3 db
        # 'NAME': SQLITE3_DB_PATH,        # Used for sqlite3 db
        'ENGINE': 'django.db.backends.postgresql_psycopg2',     # Used for postgres db
        'NAME': 'gstudio_psql',                     # Used for postgres db
        'USER': 'glab',                         # Used for postgres db
        'PASSWORD':'Gstudi02)1^',                       # Used for postgres db
        'HOST':'localhost',                     # Used for postgres db
        'PORT':''                               # Used for postgres db

    },
    'mongodb': {
        'ENGINE': 'django_mongokit.mongodb',				# Used for mongo db
        'NAME': MONGODB_DBNAME,					# Used for mongo db
        'USER': '',							# Used for mongo db
        'PASSWORD': '',							# Used for mongo db
        'HOST': '', 							# Used for mongo db
        'PORT': '',							# Used for mongo db
    },
}

from gnowsys_ndf.settings import MIDDLEWARE_CLASSES
MIDDLEWARE_CLASSES += ('gnowsys_ndf.ndf.middleware.ProfileMiddleware.ProfileMiddleware',)

GSTUDIO_DOCUMENT_MAPPING = '/data'
# from gnowsys_ndf.settings import INSTALLED_APPS
# INSTALLED_APPS += (
#     'django_extensions',
#     'devserver',
#     )
 
# DEVSERVER_MODULES = (
#     'devserver.modules.sql.SQLRealTimeModule',
#     'devserver.modules.sql.SQLSummaryModule',
#     'devserver.modules.profile.ProfileSummaryModule',

#     # Modules not enabled by default
#     'devserver.modules.ajax.AjaxDumpModule',
#     'devserver.modules.profile.MemoryUseModule',
#     'devserver.modules.cache.CacheSummaryModule',
#     'devserver.modules.profile.LineProfilerModule',
# )
# DEVSERVER_AUTO_PROFILE = True

#--------------------------------------------- Replication -----------------------------------------------------

# SMTP setting for sending mail (Using gmail SMTP server)
#EMAIL_USE_TLS = True
#EMAIL_HOST = 'your_email_id'
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'your_email_id' # mrunal4888@
#EMAIL_HOST_PASSWORD = 'your_password'

# The following variables are for email id and password for the email account which will be used for receiving SYNCDATA mails
#SYNCDATA_FETCHING_EMAIL_ID = 'your_email_id'
#SYNCDATA_FETCHING_EMAIL_ID_PASSWORD = 'your_password'
#SYNCDATA_FETCHING_IMAP_SERVER_ADDRESS = 'imap_address_of_server'

# Mailing-list ID (ie to this id syncdata mails will be sent)
#SYNCDATA_SENDING_EMAIL_ID = (
#    'mailing_list_emil_id',
#) # Mailing list

#While sending syncdata mails the from field of the mail is set by this variable
#SYNCDATA_FROM_EMAIL_ID ='Display_name <your_email_id>'
# sample:  'Gstudio <t.metastudio@gmail.com>'

# This is the duration (in secs) at which send_syncdata and fetch_syncdata scripts will be run
# SYNCDATA_DURATION = 60

#SIGNING KEY Pub. Fill the pub of the key with which to sign syncdata mails here
#SYNCDATA_KEY_PUB = 'gpg_public_key'


# ----------------------------------------------------------------------------
# following has to be at last
# just put every thing above it

try:
    from server_settings import *
    # print "Server settings applied"
except:
    # print "Default settings applied"
    pass

# ========= nothing to be added below this line ===========
