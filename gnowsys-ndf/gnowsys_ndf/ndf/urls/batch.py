from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.batch',
                       url(r'^[/]$', 'batch', name='batch'),
                       url(r'^/edit/(?P<_id>[\w-]+)$', 'new_create_and_edit', name='edit'),
                       url(r'^/new_batch$', 'new_create_and_edit', name='new_batch'),
                       url(r'^/save_batch_stud$', 'save_students_for_batches', name='save_batch_stud'),
                       url(r'^/save_batch$', 'save_batch', name='save_batch'),
                       url(r'^/remove_stud_from_batch$', 'remove_stud_from_batch', name='remove_stud_from_batch'),
                       url(r'^/batch_detail$', 'batch_detail', name='batch_detail'),
                       url(r'^/detail/(?P<_id>[\w-]+)$', 'detail', name='detail'),
                       url(r'^/delete_batch/(?P<_id>[\w-]+)$', 'delete_batch', name='delete_batch'),
                       url(r'^/get_possible_batches/$', 'get_possible_batches', name='get_possible_batches'),
                       )

