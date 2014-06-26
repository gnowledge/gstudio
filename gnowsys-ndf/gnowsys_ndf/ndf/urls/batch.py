from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.batch',
                       url(r'^$', 'batch', name='batch'),
                       url(r'^/create$', 'create_and_edit', name='create'),
                       url(r'^/edit/(?P<_id>[\w-]+)$', 'create_and_edit', name='edit'),
                       url(r'^/create_new$', 'new_create_and_edit', name='create_new'),
                       #url(r'^/save$', 'save_and_update', name='save'),
                       url(r'^/save$', 'save', name='save'),
                       url(r'^/detail/(?P<_id>[\w-]+)$', 'detail', name='detail'),
                       )
