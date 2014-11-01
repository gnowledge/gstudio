from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.batch',
                       url(r'^$', 'batch', name='batch'),
                       url(r'^/create$', 'create_and_edit', name='create'),
                       url(r'^/edit/(?P<_id>[\w-]+)$', 'new_create_and_edit', name='edit'),
                       url(r'^/batch_create_criteria$', 'batch_create_criteria', name='batch_create_criteria'),
                       url(r'^/new_create_and_edit$', 'new_create_and_edit', name='new_create_and_edit'),
                       url(r'^/save_students_for_batches$', 'save_students_for_batches', name='save_students_for_batches'),
                       #url(r'^/save$', 'save_and_update', name='save'),
                       url(r'^/save$', 'save', name='save'),
                       url(r'^/detail/(?P<_id>[\w-]+)$', 'detail', name='detail'),
                       )
