from django.conf.urls import patterns, url

# /(?P<file_path>[\w-]+)[/]

urlpatterns = patterns('gnowsys_ndf.ndf.views.file',
						url(r'^(?P<_id>[\w-]+)/(?:(?P<file_name>[^/]+))?$', 'readDoc', name='read_file'),
						url(r'^download/(?P<file_path>.*)$', 'read_attachment', name='read_attachment'),
)
