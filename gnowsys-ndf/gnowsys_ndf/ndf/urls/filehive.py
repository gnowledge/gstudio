from django.conf.urls import patterns, url

from django.views.generic import TemplateView

urlpatterns = patterns('gnowsys_ndf.ndf.views.filehive',
                        url(r'^[/]$', 'write_files', name='write_file'),
                        url(r'^/list/?$', 'read_file', name='read_file'),
                        url(r'^/upload_form/?$', 'upload_form', name='upload_form'),
            )
