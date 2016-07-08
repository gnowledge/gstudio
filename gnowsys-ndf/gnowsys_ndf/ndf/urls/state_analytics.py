from django.conf.urls import patterns, url

from django.views.generic import TemplateView
from gnowsys_ndf.ndf.views import state_analytics

urlpatterns = patterns('gnowsys_ndf.ndf.views.state_analytics',
		url(r'^[/]$' ,'map_view',name='map_view'),
		url(r'^[/]update_organization/(?P<node_id>[\w-]+)$','add_organization',name='add_organization'),
		url(r'^[/]update_organization/$','add_organization',name='add_organization'),
		url(r'^[/]fetch_organization/$','fetch_organization',name='fetch_organization'),
		url(r'^[/]delete_organization/(?P<node_id>[\w-]+)$','delete_organization',name='delete_organization'),
	)