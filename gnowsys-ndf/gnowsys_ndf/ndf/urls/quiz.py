from django.conf.urls import patterns, url

from gnowsys_ndf.ndf.views import quiz

urlpatterns = patterns('gnowsys_ndf.ndf.views.quiz',
                       url(r'^(?P<app_id>[\w-]+)$', 'quiz', name='quiz'),
                       url(r'^question/create', 'create_edit_quiz_item', name='quiz_item_create_edit'),
                       url(r'^create/', 'create_edit_quiz', name='quiz_create_edit'),
                       url(r'^details/(?P<app_id>[\w-]+)$', 'quiz', name='quiz_details'),
                       url(r'^question/edit/(?P<node_id>[\w-]+)$', 'create_edit_quiz_item', name='quiz_item_create_edit'),
                       url(r'^edit/(?P<node_id>[\w-]+)$', 'create_edit_quiz', name='quiz_create_edit'),
                       # url(r'^(?P<node_id>[\w-]+)/version/(?P<version_no>\d+\.\d+)$', 'version_node', name='node_version'),
)
