from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView
from gnowsys_ndf.ndf.views import *


urlpatterns = patterns('',
        url(r'^$', RedirectView.as_view(url='GSystem'), name='adminClass'),
        url(r'^edit','gnowsys_ndf.ndf.views.adminDashboard.adminDashboardEdit',name='adminDashboardEdit' ),
        url(r'^delete','gnowsys_ndf.ndf.views.adminDashboard.adminDashboardDelete',name='adminDashboardDelete' ),
	url(r'^(?P<class_name>[^/]+)','gnowsys_ndf.ndf.views.adminDashboard.adminDashboardClass',name='adminDashboardClass' ),

)
