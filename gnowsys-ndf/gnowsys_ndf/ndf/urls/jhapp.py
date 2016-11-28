from django.conf.urls import patterns, url, include

from django.views.generic import TemplateView

urlpatterns = patterns('gnowsys_ndf.ndf.views.jhapp',
                       url(r'^[/]$', 'jhapp', name='jhapp'),
                       # url(r'^/uploadDoc/$', 'uploadDoc', name='uploadDoc'), #Direct ot html template                               
                       
)

