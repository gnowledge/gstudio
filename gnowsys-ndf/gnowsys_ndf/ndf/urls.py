#from django.conf.urls.defaults import patterns, url
from django.conf.urls import patterns, url
from django.views.generic import TemplateView
import views


urlpatterns = patterns('',
                       url(r'^$', views.homepage, name='homepage'),
                       url(r'^create_wiki/', views.create_wiki, name='create_wiki'),
                       url(r'^wikipage/', views.wikipage, name='wikipage'),
                       url(r'^UserRegistration/', views.UserRegistration, name='UserRegistration'),
                       url(r'^Register/', views.Register, name='Register'),
                       url(r'^Authentication/', views.Authentication, name='Authentication'),
                       url(r'^logout_view/', views.logout_view, name='logout_view'),
                       url(r'^delete/(?P<_id>[\w-]+)$', views.delete_node, name='delete_node'),
		       url(r'^uploadDoc/$', TemplateView.as_view(template_name='ndf/UploadDoc.html')),#Direct ot html template
		       url(r'^submitDoc/', views.submitDoc, name='submitDoc'),	
			url(r'^submit/', views.submitDoc, name='submitDoc')	
                       )
