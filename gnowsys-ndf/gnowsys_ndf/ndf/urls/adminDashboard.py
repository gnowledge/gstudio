from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

urlpatterns = patterns('gnowsys_ndf.ndf.views.adminDashboard',
        url(r'^$', 'adminDashboardClass', name='adminClass'),
        url(r'^edit', 'adminDashboardEdit', name='adminDashboardEdit'),
        url(r'^delete', 'adminDashboardDelete', name='adminDashboardDelete'),
	url(r'^(?P<class_name>[^/]+)', 'adminDashboardClass', name='adminDashboardClass'),
)
