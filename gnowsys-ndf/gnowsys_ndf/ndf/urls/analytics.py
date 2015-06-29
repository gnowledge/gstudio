from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import analytics


urlpatterns = patterns('gnowsys_ndf.ndf.views.analytics',  
    url(r'^[/]$', 'default', name='default'),                      
    url(r'^/page_view/', 'page_view', name='page_view'),
	url(r'^/list_activities/', 'list_activities', name='list_activities'),
	url(r'^/session_summary/', 'session_summary', name='session_summary'),
	url(r'^/group_analytics/', 'group_analytics', name='group_analytics'),

)
