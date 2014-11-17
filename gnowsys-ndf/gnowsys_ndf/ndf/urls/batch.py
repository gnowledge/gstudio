from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.batch',
                       url(r'^$', 'batch', name='batch'),
                       url(r'^/edit/(?P<_id>[\w-]+)$', 'new_create_and_edit', name='edit'),
                       url(r'^/new_batch$', 'new_create_and_edit', name='new_batch'),
                       url(r'^/save_batch$', 'save_students_for_batches', name='save_batch'),
                       url(r'^/detail/(?P<_id>[\w-]+)$', 'detail', name='detail'),
                       )
