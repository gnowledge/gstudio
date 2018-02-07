from django.conf.urls import patterns, url
urlpatterns = patterns('gnowsys_ndf.ndf.views.Bib_App',
                       url(r'^[/]$', 'Bib_App', name='Bib_App'),
                       url(r'^[/]$', 'Bib_App', name='bib_app'),
                       url(r'^/create_entries$','create_entries',name='create_entries'),
                       url(r'^/view_entry/(?P<node_id>[\w-]+)$','view_entry',name='view_entry'),
                       url(r'^/view_entries/','view_entries',name='view_entries'),
                       url(r'^/view_sentry/(?P<node_id>[\w-]+)$','view_sentry',name='view_sentry'),
                       url(r'^/delete_entry/(?P<node_id>[\w-]+)$','delete_sentry',name='delete_sentry'),
                       url(r'^/edit_entry/(?P<node_id>[\w-]+)$','edit_entry',name='edit_entry')
                       )