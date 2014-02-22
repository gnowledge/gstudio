from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView
from gnowsys_ndf.ndf.views import *


urlpatterns = patterns('',
        url(r'^$', RedirectView.as_view(url='GSystemType'), name='adminDesigner'),
	url(r'^(?P<class_name>[^/]+)$','gnowsys_ndf.ndf.views.adminDesignerDashboard.adminDesignerDashboardClass',name='adminDesignerDashboardClass' ),
	url(r'(?P<class_name>[^/]+)/create','gnowsys_ndf.ndf.views.adminDesignerDashboard.adminDesignerDashboardClassCreate',name='adminDesignerDashboardClassCreate' ),

)
