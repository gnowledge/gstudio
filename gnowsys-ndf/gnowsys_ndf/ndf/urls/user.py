from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import *


urlpatterns = patterns('gnowsys_ndf.ndf.views.userDashboard',                       
                       url(r'^(?P<user>[\w-]+)/userDashboard', 'dashboard', name='userDashboard')
                       
)

