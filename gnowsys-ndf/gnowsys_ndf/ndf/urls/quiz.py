from django.conf.urls import patterns, url

from gnowsys_ndf.ndf.views import quiz

urlpatterns = patterns('gnowsys_ndf.ndf.views.quiz',
                       url(r'^(?P<app_id>[\w-]+)/list$', 'quiz', name='quiz'),
                       url(r'^create/', 'create_quiz_item', name='quiz_item_create'),
                       # url(r'^create/', 'create_page', name='page_create'),
                       # url(r'^(?P<app_id>[\w-]+)/details$', 'page', name='page_details'),
                       # url(r'^(?P<node_id>[\w-]+)/edit$', 'edit_page', name='page_edit'),
                       # url(r'^(?P<node_id>[\w-]+)/version/(?P<version_no>\d+\.\d+)$', 'version_node', name='node_version'),
)
