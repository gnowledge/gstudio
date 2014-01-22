from django.conf.urls import patterns, url

from gnowsys_ndf.ndf.views import quiz

urlpatterns = patterns('gnowsys_ndf.ndf.views.quiz',
                       url(r'^(?P<app_id>[\w-]+)/list$', 'quiz', name='quiz'),
                       url(r'^create-question/', 'create_edit_quiz_item', name='quiz_item_create_edit'),
                       url(r'^create/', 'create_edit_quiz', name='quiz_create_edit'),
                       url(r'^(?P<app_id>[\w-]+)/details$', 'quiz', name='quiz_details'),
                       url(r'^(?P<node_id>[\w-]+)/edit-question$', 'create_edit_quiz_item', name='quiz_item_create_edit'),
                       url(r'^(?P<node_id>[\w-]+)/edit$', 'create_edit_quiz', name='quiz_create_edit'),
                       # url(r'^(?P<node_id>[\w-]+)/version/(?P<version_no>\d+\.\d+)$', 'version_node', name='node_version'),
)
