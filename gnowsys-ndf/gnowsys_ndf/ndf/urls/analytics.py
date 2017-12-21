from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import analytics


urlpatterns = patterns('gnowsys_ndf.ndf.views.analytics',  
    
    # URL for registering custom actions through AJAX
    url(r'^/custom_event/$', 'custom_events', name='register_custom_views'),
	
    # User Analytics URLS
	url(r'^[/]$', 'default_user', name='default_user'),                      
	url(r'^/list_activities[/]$', 'user_list_activities', name='user_list_activities'),
	url(r'^/summary[/]$', 'user_summary', name='user_summary'),
	url(r'^/list_activities/(?P<part>[^/]+)$', 'user_app_activities', name='user_app_activities'),
	#url(r'^/graphs[/]$', 'user_graphs', name='user_graphs'),
	
	# Group Analytics URLS

	url(r'^/group[/]$', 'default_group', name='default_group'),                      
	url(r'^/group/list_activities[/]$', 'group_list_activities', name='group_list_activities'),
	url(r'^/group/summary[/]$', 'group_summary', name='group_summary'),
	url(r'^/group/members[/]$', 'group_members', name='group_members'),
	url(r'^/group/member/(?P<user>[^/]+)$', 'group_member_info_details', name='group_member_info_details')


)
