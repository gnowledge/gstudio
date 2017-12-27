#------------------------------------------ Changing the website instances(Logo and database etc) -------------------------------------------------
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "14.139.123.3", "nroer.gov.in"]  
#ALLOWED_HOSTS = ["*"]  
#TEMPLATE_DEBUG78 = False                                                                                                                            

import os

# Authentication related and Error reporting emails
EMAIL_USE_TLS = ""
ACCOUNT_ACTIVATION_DAYS = 2
EMAIL_HOST = 'localhost'
#EMAIL_HOST = 'nroer.gov.in'
#DEFAULT_FROM_EMAIL = 'webmaster@nroer.metastudio.org'
#DEFAULT_FROM_EMAIL = 'webmaster-nroer@gnowledge.org'
DEFAULT_FROM_EMAIL = 'webmaster-nroer@gnowledge.org' #'webmaster@nroer.gov.in'
LOGIN_REDIRECT_URL = '/'
EMAIL_SUBJECT_PREFIX='[nroer-error-reporting]'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_PORT = "25"
ADMINS = (
    ('kedar', 'kedar2a@gmail.com'),
    ('mrunal', 'mrunal4888@gmail.com'),
    ('saurabh', 'saurabhbharswadkar7@gmail.com'),
    ('rachana', 'katkam.rachana@gmail.com'), 
    # ('nagarjuna','nagarjun@gnowledge.org'),            
)


#GSTUDIO_SITE_NAME = "clix"
#GSTUDIO_SITE_LANDING_TEMPLATE = "ndf/landing_page_clix.html"
# Mrunal : Added 25-04-2016

# GSTUDIO_SITE_NAME = "NROER"
# GSTUDIO_SITE_LANDING_TEMPLATE = "home"
# GSTUDIO_SITE_LOGO = "/static/ndf/css/themes/nroer/logo.png"
GSTUDIO_SITE_FAVICON = "/static/ndf/images/favicon/logo.png"
# GSTUDIO_SITE_HOME_PAGE = "/welcome"
#GSTUDIO_CAPTCHA_VISIBLE = True
# GSTUDIO_MY_GROUPS_IN_HEADER = False
# GSTUDIO_MY_COURSES_IN_HEADER = True
# GSTUDIO_SECOND_LEVEL_HEADER = True
# GSTUDIO_MY_DASHBOARD_IN_HEADER = True



# Deatils related to database
MEDIA_ROOT = '/data/media/'
GSTUDIO_DATA_ROOT = os.path.join('/data/')

GSTUDIO_LOGS_DIRNAME = 'gstudio-logs'
GSTUDIO_LOGS_DIR_PATH = os.path.join('/data/', GSTUDIO_LOGS_DIRNAME)

RCS_REPO_DIRNAME = "rcs-repo"
RCS_REPO_DIR = os.path.join('/data/', RCS_REPO_DIRNAME)

GSTUDIO_MAIL_DIRNAME = 'MailClient'
GSTUDIO_MAIL_DIR_PATH = os.path.join('/data/', GSTUDIO_MAIL_DIRNAME)

SQLITE3_DBNAME = 'example-sqlite3.db'    #'example-sqlite3.db'
SQLITE3_DB_PATH = os.path.join('/data/', SQLITE3_DBNAME)


#GSTUDIO_DATA_ROOT = '/data'
#SQLITE3_DBNAME = 'example-sqlite3.db'					# Used for sqlite3 db 
#RCS_REPO_DIRNAME = 'rcs-repo'

MONGODB_DBNAME = 'gstudio-mongodb'

DATABASES = {
    'default': {
    # We have 2 database (postgres and sqlite3) connection details here. Ensure the part of connection details of database not in use is commented.
        # 'ENGINE': 'django.db.backends.sqlite3',               # Used for sqlite3 db
        # 'NAME': SQLITE3_DB_PATH,        # Used for sqlite3 db
        'ENGINE': 'django.db.backends.postgresql_psycopg2',     # Used for postgres db
        'NAME': 'gstudio_psql',                     # Used for postgres db
        'USER': 'glab',                         # Used for postgres db
        'PASSWORD':'Gstudi02)1^',                       # Used for postgres db
        'HOST':'localhost',                     # Used for postgres db
        'PORT':''                               # Used for postgres db

    },
    'mongodb': {
        'ENGINE': 'django_mongokit.mongodb',                # Used for mongo db
        'NAME': MONGODB_DBNAME,                 # Used for mongo db
        'USER': '',                         # Used for mongo db
        'PASSWORD': '',                         # Used for mongo db
        'HOST': '',                             # Used for mongo db
        'PORT': '',                         # Used for mongo db
    },
}


RCS_REPO_DIR = os.path.join(GSTUDIO_DATA_ROOT, RCS_REPO_DIRNAME)

GSTUDIO_DEFAULT_GAPPS_LIST = [u"Page", u"Forum",u"E-Library"]
# GSTUDIO_DEFAULT_GAPPS_LIST = [ u"E-Library", u"Page", u"Forum"]

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
#STATIC_ROOT = os.path.join('/','home','glab','static')
#STATIC_ROOT = '/var/www/14.139.123.3:8101/static'   # Mrunal : Tue Jul 14 13:48:29 IST 2015 : Commented to change IP to name
#STATIC_ROOT = '/var/www/nroer.metastudio.org/static'
STATIC_ROOT = '/static/'

GSTUDIO_SITE_DEFAULT_LANGUAGE=u"('en', 'English')"

GSTUDIO_SITE_LOGO="/static/ndf/css/themes/nroer/logo.png" # usually appears on the top
GSTUDIO_ORG_LOGO="/static/ndf/css/themes/nroer/orglogo.svg" # can be placed in the footer
GSTUDIO_ORG_NAME='''<p>
<a href="https://github.com/gnowledge/ncert_nroer" target="_blank">Gnowsys-Studio</a>,<a href="http://www.hbcse.tifr.res.in" target="_blank">Homi Bhabha Centre for Science Education (HBCSE)</a>, <a href="http://www.tifr.res.in" target="_blank">Tata Institute of Fundamental Research (TIFR), India</a>.
</p>'''

GSTUDIO_COPYRIGHT="All material is licensed under a Creative Commons Attribution-Share Alike 3.0 Unported License unless mentioned otherwise."
GSTUDIO_GIT_REPO="https://github.com/gnowledge/gstudio"
#GSTUDIO_SITE_PRIVACY_POLICY="http://nroer.gov.in/home/page/55b8e5a381fccb25935dc495"
GSTUDIO_SITE_PRIVACY_POLICY="http://nroer.gov.in/home/page/5774fb2b16b51c03ba38f61c"
GSTUDIO_SITE_TERMS_OF_SERVICE="http://nroer.gov.in/home/page/58198aa216b51c01a6e3d651"

#GSTUDIO_SITE_ABOUT="http://nroer.gov.in/55ab34ff81fccb4f1d806025/page/55b8e42881fccb07c1cc66da"
GSTUDIO_SITE_ABOUT="http://nroer.gov.in/home/page/5774f5f316b51c03ba38f30d"
GSTUDIO_SITE_POWEREDBY="http://www.metastudio.org/gnowledge%20lab/"
# GSTUDIO_SITE_PARTNERS="http://nroer.metastudio.org/home/page/53fc615c81fccb2d7fc7da33"
GSTUDIO_SITE_PARTNERS = "http://nroer.gov.in/home/partner/Partners"
# GSTUDIO_SITE_GROUPS="http://nroer.metastudio.org/home/page/5400432381fccb6b4b19ab6a"
GSTUDIO_SITE_GROUPS = "http://nroer.gov.in/home/partner/Groups"
#GSTUDIO_SITE_CONTACT="http://nroer.gov.in/home/page/55b8e5e881fccb25935dc4d7"
GSTUDIO_SITE_CONTACT="http://nroer.gov.in/home/page/5774fd2d16b51c03ba38fa83"
GSTUDIO_SITE_CONTRIBUTE="http://nroer.gov.in/home/page/581998a316b51c01a86994de"
GSTUDIO_SITE_VIDEO='pandora'
GSTUDIO_SITE_LANDING_PAGE='home'
GSTUDIO_SITE_NAME = "NROER"
#GSTUDIO_SITE_LANDING_PAGE = "homepage"
GSTUDIO_SITE_HOME_PAGE = "/welcome"

WETUBE_USERNAME = "glab"
WETUBE_PASSWORD = "gl@b$@)we!ube"

GSTUDIO_FILE_UPLOAD_FORM = 'detail'

GSTUDIO_OID_TC = '55b8e55881fccb25935dc448'

GSTUDIO_OID_OER = '563f28d481fccb0fa7f3bc8f'
GSTUDIO_SITE_ISSUES_PAGE = "/home/page/5665aa9681fccb03424ffcda"
GSTUDIO_EBOOKS_HELP_TEXT = "/home/page/56701a8581fccb0343bf438b"

#Set False if you non't want any Social Networking share button
SOCIAL_SHARE_RESOURCE = True 

GSTUDIO_CAPTCHA_VISIBLE = True
GSTUDIO_MY_GROUPS_IN_HEADER = False
GSTUDIO_MY_COURSES_IN_HEADER = False
GSTUDIO_SECOND_LEVEL_HEADER = True
GSTUDIO_MY_DASHBOARD_IN_HEADER = False

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
        },
        'applogfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            #'filename': os.path.join(DJANGO_ROOT, 'survey.log'),
            'filename': 'gstudio.log',

            'maxBytes': 1024*1024*15, # 15MB
            'backupCount': 10,
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'gstudio': {
            'handlers': ['applogfile',],
            'level': 'DEBUG',
        },
    }
}

#--------------------------------------------- Replication -----------------------------------------------------

# # SMTP setting for sending mail (Using gmail SMTP server)
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'gnowledge.org'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'ssraj2pilot@gnowledge.org' # mrunal4888@
# EMAIL_HOST_PASSWORD = 'ssraj@234' 

# # The following variables are for email id and password for the email accoun
