from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

urlpatterns = patterns('gnowsys_ndf.ndf.views.adminDesignerDashboard',
                       url(r'^$', 'adminDesignerDashboardClass', name='adminDesigner'),
                       url(r'^(?P<class_name>[^/]+)$', 'adminDesignerDashboardClass', name='adminDesignerDashboardClass'),
                       url(r'(?P<class_name>[^/]+)/create/', 'adminDesignerDashboardClassCreate', name='adminDesignerDashboardClassCreate'),
                       url(r'(?P<class_name>[^/]+)/edit/(?P<node_id>[\w-]+)$', 'adminDesignerDashboardClassCreate', name='adminDesignerDashboardClassEdit'),
)
