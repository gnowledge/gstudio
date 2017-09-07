from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.discussion',
                        url(r'^/edit_comment/(?P<node_id>[\w-]+)$', 'edit_comment', name='edit_comment'),
					    url(r'^/(?P<node_id>[^/]+)/create_discussion$', 'create_discussion', name='create_discussion'),
					    url(r'^/(?P<node_id>[^/]+)/discussion_reply$', 'discussion_reply', name='discussion_reply'),
					    url(r'^/(?P<node_id>[^/]+)/discussion_delete_reply$', 'discussion_delete_reply', name='discussion_delete_reply'),
					    url(r'^/get_thread_comments_count/(?P<thread_node_id>[\w-]+)$', 'get_thread_comments_count', name='get_thread_comments_count'),
						url(r'^/replies/(?P<user_name_or_id>[\w-]+)$', 'get_user_replies', name='get_user_replies'),
                        )
