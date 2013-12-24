from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import *



urlpatterns = patterns('gnowsys_ndf.ndf.views.ajax-views',                        
                       url(r'^collection/', 'select_drawer', name='select_drawer'),                        
)
