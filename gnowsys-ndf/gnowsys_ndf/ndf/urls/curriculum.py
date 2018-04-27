from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.curriculum',
					   # url(r'^[/]$', 'themes', name='theme_page'),
					   url(r'^[/]$', 'curriculum', name='curriculum'),
                       url(r'^/all-themes$', 'list_themes', name='list_themes'),
                       url(r'^/curriculum-list$', 'curriculum_list', name='curriculum_list'),
                       url(r'^/create-edit-curriculum$', 'curriculum_create_edit', name='create_edit_curriculum'),
                       url(r'^/curriculum-detail/(?P<curriculum_id>[\w-]+)', 'curriculum_create_edit', name='curriculum_detail'),
                       url(r'^/topic-resources/(?P<curriculum_id>[\w-]+)/(?P<topic_id>[\w-]+)$', 'topic_resources', name='topic_resources'),
                       url(r'^/get_json_graph/', 'graph_node', name='get_json_graph'),
                       url(r'^/prerequisite/(?P<curriculum_id>[\w-]+)/(?P<topic_id>[\w-]+)$', 'get_prerequisite', name='get_prerequisite'),
                       url(r'^/(?P<app_id>[\w-]+)$', 'curriculum', name='theme_page'),
					   # url(r'^/(?P<app_Id>[\w-]+)/topic_details$', 'topic_detail_view', name='topic_details'),
                       url(r'^/delete-theme/(?P<theme_id>[\w-]+)/$', 'delete_theme', name='delete_theme'),
                       url(r'^/filter-resources/(?P<node_id>[^/]+)/', 'get_filtered_topic_resources', name='get_filtered_topic_resources'),
                       url(r'^/(?P<app_set_id>[\w-]+)/', 'theme_topic_create_edit', name='theme_topic_create'),
                       url(r'^graph/adminRenderGraphs/(?P<node_id>[^/]+)/fetch/(?P<graph_type>[^/]+)$', 'adminRenderGraphs', name='adminRenderGraphs'),
					)