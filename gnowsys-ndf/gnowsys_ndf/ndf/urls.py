
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

import views


urlpatterns = patterns('',
                       url(r'^$', views.homepage, name='homepage'),
                       url(r'^create_group/', views.create_group, name='create_group'),
                       url(r'^create_wiki/', views.create_wiki, name='create_wiki'),
                       url(r'^wikipage/', views.wikipage, name='wikipage'),
                       url(r'^delete/(?P<_id>[\w-]+)$', views.delete_node, name='delete_node'),
                       url(r'^uploadDoc/$', TemplateView.as_view(template_name='ndf/UploadDoc.html')),#Direct ot html template
                       url(r'^submitDoc/', views.submitDoc, name='submitDoc'),
                       url(r'^submit/', views.submitDoc, name='submitDoc')	
                       )
