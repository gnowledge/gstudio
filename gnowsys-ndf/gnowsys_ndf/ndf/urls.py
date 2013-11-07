#from django.conf.urls.defaults import patterns, url, include
from django.conf.urls import patterns, url, include

import views


urlpatterns = patterns('',
                       url(r'^$', views.homepage, name='homepage'),
                       url(r'^create_wiki/', views.create_wiki, name='create_wiki'),
                       url(r'^wikipage/', views.wikipage, name='wikipage'),
                       url(r'^UserRegistration/', views.UserRegistration, name='UserRegistration'),
                       url(r'^Register/', views.Register, name='Register'),                       
                       url(r'^delete/(?P<_id>[\w-]+)$', views.delete_node, name='delete_node'),
                       )
