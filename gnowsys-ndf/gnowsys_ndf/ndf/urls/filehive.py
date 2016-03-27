from django.conf.urls import patterns, url

from django.views.generic import TemplateView

urlpatterns = patterns('gnowsys_ndf.ndf.views.filehive',
                        url(r'^[/]$', 'write_file', name='write_file'),
            )
