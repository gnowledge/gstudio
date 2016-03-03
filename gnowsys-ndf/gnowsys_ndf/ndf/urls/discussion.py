from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.discussion',
                        url(r'^[/]$', 'discussion', name='discussion'),
                        url(r'^/edit_comment/(?P<node_id>[\w-]+)$', 'edit_comment', name='edit_comment'),
                        )
