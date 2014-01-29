from django.conf.urls import patterns, url
from gnowsys_ndf.ndf.views import *

urlpatterns = patterns('gnowsys_ndf.ndf.views.course',
                        url(r'^(?P<course_id>[\w-]+)$', 'course', name='course'),
                       )
