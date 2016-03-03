from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.discussion',
                        url(r'^[/]$', 'discussion', name='discussion'),
                        url(r'^/inline_edit_comment/(?P<node_id>[\w-]+)$', 'inline_edit_comment', name='inline_edit_comment'),
                        )
