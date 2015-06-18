from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import analytics


urlpatterns = patterns('gnowsys_ndf.ndf.views.analytics',  
    url(r'^[/]$', 'default', name='default'),                      
    url(r'^/page_view/', 'page_view', name='page_view'),
)
