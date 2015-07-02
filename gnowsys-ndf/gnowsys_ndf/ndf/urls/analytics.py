from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import analytics


urlpatterns = patterns('gnowsys_ndf.ndf.views.analytics',  
    url(r'^[/]$', 'default', name='default'),                      
    url(r'^/page_view/', 'page_view', name='page_view'),
	url(r'^/list_activities/', 'list_activities', name='list_activities'),
	url(r'^/session_summary/', 'session_summary', name='session_summary'),
	url(r'^/(?P<group_id>[^/]+)/list_activities/', 'group_list_activities', name='group_list_activities'),
	url(r'^/(?P<group_id>[^/]+)/group_summary/', 'group_summary', name='group_summary')
	

)
