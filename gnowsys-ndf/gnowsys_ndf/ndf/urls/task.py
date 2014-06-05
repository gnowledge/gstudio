from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.task',
                       url(r'^$', 'task', name='task'),
                       url(r'^/create$', 'create_edit_task', name='task_create_edit'),
                       url(r'^/(?P<task_id>[\w-]+)/$', 'task_details', name='task_details'),
                       url(r'^/edit/(?P<task_id>[\w-]+)/$', 'create_edit_task', name='task_edit'),
                       )
