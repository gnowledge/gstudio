from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.discussion',
                        url(r'^/edit_comment/(?P<node_id>[\w-]+)$', 'edit_comment', name='edit_comment'),
					    url(r'^/(?P<node_id>[^/]+)/create_discussion$', 'create_discussion', name='create_discussion'),    
					    url(r'^/(?P<node_id>[^/]+)/discussion_reply$', 'discussion_reply', name='discussion_reply'),
					    url(r'^/(?P<node_id>[^/]+)/discussion_delete_reply$', 'discussion_delete_reply', name='discussion_delete_reply'),    
                        )
