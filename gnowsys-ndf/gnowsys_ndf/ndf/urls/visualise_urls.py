from django.conf.urls import patterns, url

from django.views.generic import TemplateView

urlpatterns = patterns('gnowsys_ndf.ndf.views.visualize',
                        url(r'^[/]$', 'graphs', name='visualize_home'),
#                        url(r'^/(?P<file_id>[\w-]+)$', 'file', name='file'),
                        # url(r'^graph_display/$', 'graph_display', name='graph_display'),
                       
)
