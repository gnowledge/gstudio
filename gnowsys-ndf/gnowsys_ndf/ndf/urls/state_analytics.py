from django.conf.urls import patterns, url

from django.views.generic import TemplateView
from gnowsys_ndf.ndf.views import state_analytics

urlpatterns = patterns('gnowsys_ndf.ndf.views.state_analytics',
		url(r'^$' ,'map_view',name='map_view'),
	)