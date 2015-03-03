from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.term',
					   url(r'^[/]$', 'term', name='term'),
					   url(r'^/(?P<node_id>[\w-]+)$', 'term', name='term_details'),
					   url(r'^/create/', 'create_edit_term', name='term_create_edit'),
                       url(r'^/edit/(?P<node_id>[\w-]+)$', 'create_edit_term', name='term_create_edit'),
                       url(r'^/delete/(?P<node_id>[\w-]+)$', 'delete_term', name='term_delete')
)