from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.topics',
					   # url(r'^[/]$', 'themes', name='theme_page'),
					   url(r'^[/]$', 'themes', name='topics'),
                       url(r'^/all-themes$', 'list_themes', name='list_themes'),
                       url(r'^/(?P<app_id>[\w-]+)$', 'themes', name='theme_page'),
					   # url(r'^/(?P<app_Id>[\w-]+)/topic_details$', 'topic_detail_view', name='topic_details'),
                       url(r'^/delete-theme/(?P<theme_id>[\w-]+)/$', 'delete_theme', name='delete_theme'),
                       url(r'^/filter-resources/(?P<node_id>[^/]+)/', 'get_filtered_topic_resources', name='get_filtered_topic_resources'),
                       url(r'^/(?P<app_set_id>[\w-]+)/', 'theme_topic_create_edit', name='theme_topic_create'),
					)