from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import analytics


urlpatterns = patterns('gnowsys_ndf.ndf.views.analytics',  
    url(r'^[/]$', 'default', name='default'),                      
    
    # URL for registering custom actions through AJAX
    url(r'^/page_view/', 'page_view', name='page_view'),
	
    # User Analytics URLS
	url(r'^/list_activities/', 'user_list_activities', name='user_list_activities'),
	url(r'^/summary/', 'user_summary', name='user_summary'),
	
	# Group Analytics URLS
	url(r'^/(?P<group_id>[^/]+)/list_activities/', 'group_list_activities', name='group_list_activities'),
	url(r'^/(?P<group_id>[^/]+)/summary/', 'group_summary', name='group_summary'),
	url(r'^/(?P<group_id>[^/]+)/members/', 'group_members', name='group_members')

)
