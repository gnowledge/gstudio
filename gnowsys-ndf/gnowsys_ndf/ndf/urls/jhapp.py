from django.conf.urls import patterns, url, include

from django.views.generic import TemplateView

urlpatterns = patterns('gnowsys_ndf.ndf.views.jhapp',
                       url(r'^[/]$', 'jhapp', name='jhapp'),
                       url(r'^/uploadjhapp/$', 'uploadjhapp', name='uploadjhapp'), 
                       url(r'^/savejhapp/', 'savejhapp', name='savejhapp'),                               
                       
)

