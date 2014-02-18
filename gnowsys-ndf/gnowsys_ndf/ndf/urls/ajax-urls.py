from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import *


urlpatterns = patterns('gnowsys_ndf.ndf.views.ajax_views',                        
                       url(r'^collection/', 'select_drawer', name='select_drawer'),
                       url(r'^change_group_settings/', 'change_group_settings', name='change_group_settings'),                 
                       url(r'^make_module/', 'make_module_set', name='make_module'),                 
                       url(r'^get_module_json/', 'get_module_json', name='get_module_json'),
                       url(r'^user_group/', 'user_group', name='user_group')                

)
