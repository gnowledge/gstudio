from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.forum',

                       url(r'^[/]$', 'forum', name='forum'),
                      # url(r'^/(?P<node_id>[\w-]+)$', 'forum', name='forum'),
                       url(r'^/create/$', 'create_forum', name='create_forum'),
					  # url(r'^/show/(?P<forum_id>[\w-]+)$', 'display_forum', name='show'),
                       url(r'^/edit_forum/(?P<forum_id>[\w-]+)$', 'edit_forum', name='edit_forum'),
                       url(r'^/edit_thread/(?P<forum_id>[\w-]+)/(?P<thread_id>[\w-]+)$', 'edit_thread', name='edit_thread'),

                       url(r'^/delete/(?P<node_id>[\w-]+)$', 'delete_forum', name='forum_delete'),
                       url(r'^/delete/thread/(?P<forum_id>[\w-]+)/(?P<node_id>[\w-]+)$', 'delete_thread', name='thread_delete'),
                       url(r'^/delete/reply/(?P<forum_id>[\w-]+)/(?P<thread_id>[\w-]+)/(?P<node_id>[\w-]+)$', 'delete_reply', name='reply_delete'),

                       url(r'^/(?P<forum_id>[\w-]+)$', 'display_forum', name='show'),
                       url(r'^/(?P<forum_id>[\w-]+)/thread/create/$', 'create_thread', name='create_thread'),###
                       url(r'^/thread/(?P<thread_id>[\w-]+)$', 'display_thread', name='thread'),
#                       url(r'^/(?P<forum_id>[\w-]+)/(?P<thread_id>[\w-]+)$', 'display_thread', name='thread'),
		       		   url(r'^/add_node/$','add_node',name="add_node"),
)

