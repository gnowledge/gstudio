#from django.conf.urls.defaults import patterns, url
from django.conf.urls import patterns, url

import views


urlpatterns = patterns('',
        url(r'^$', views.homepage, name='homepage'),
		url(r'^wikipage/', views.wikipage, name='wikipage'),
		#url(r'^wiki_node/', views.wiki_node, name='wiki_node'),
        url(r'^users/', views.userspage, name='userspage'),
        url(r'^delete/(?P<_id>[\w-]+)$', views.delete_node, name='delete_node'),
)
