from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.course',
                        url(r'^$', 'course', name='course'),
                      #  url(r'^/(?P<course_id>[\w-]+)$', 'course', name='course'),
                        url(r'^/create/$', 'create_edit', name='create_edit'),
                        url(r'^/edit/(?P<node_id>[\w-]+)$', 'create_edit', name='create_edit'),
			url(r'^/course_detail/(?P<_id>[\w-]+)$', 'course_detail', name='course_detail'),
                        url(r'^/(?P<_id>[\w-]+)$', 'course_detail', name='course_detail'),
                       )
