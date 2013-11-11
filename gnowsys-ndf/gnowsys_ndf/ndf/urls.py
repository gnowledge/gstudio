
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

import views


urlpatterns = patterns('',
                       url(r'^$', views.homepage, name='homepage'),
                       url(r'^create_wiki/', views.create_wiki, name='create_wiki'),
                       url(r'^wikipage/', views.wikipage, name='wikipage'),
                       url(r'^delete/(?P<_id>[\w-]+)$', views.delete_node, name='delete_node'),
<<<<<<< HEAD
		       url(r'^uploadDoc/$', TemplateView.as_view(template_name='ndf/UploadDoc.html')),#Direct ot html template
		       url(r'^submitDoc/', views.submitDoc, name='submitDoc'),	
		       url(r'^submit/', views.submitDoc, name='submitDoc'),
		       url(r'^documentList/', views.GetDoc, name='documentList'),
		       url(r'^readDoc/(?P<_id>[\w-]+)$', views.readDoc, name='read_file'),	
=======
                       url(r'^uploadDoc/$', TemplateView.as_view(template_name='ndf/UploadDoc.html')),#Direct ot html template
                       url(r'^submitDoc/', views.submitDoc, name='submitDoc'),
                       url(r'^submit/', views.submitDoc, name='submitDoc')	
>>>>>>> 4da6a7769d212d3b1b2af4e1ee8593b5d88c1543
                       )
