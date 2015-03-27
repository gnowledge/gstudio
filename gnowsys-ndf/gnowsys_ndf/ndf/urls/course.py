from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.course',
                        url(r'^[/]$', 'course', name='course'),
                      #  url(r'^/(?P<course_id>[\w-]+)$', 'course', name='course'),
                        url(r'^/create/$', 'create_edit', name='create_edit'),
                        url(r'^/edit/(?P<node_id>[\w-]+)$', 'create_edit', name='create_edit'),
                        url(r'^/structure/create/(?P<node_id>[\w-]+)$', 'create_course_struct', name='create_course_struct'),
                        url(r'^/change_node_name/$', 'change_node_name', name='change_node_name'),
                        url(r'^/course_sub_section_prop/$', 'course_sub_section_prop', name='course_sub_section_prop'),
                        url(r'^/change_order/$', 'change_order', name='change_order'),
                        url(r'^/create_cs/$', 'save_course_section', name='save_course_section'),
                        url(r'^/create_css/$', 'save_course_sub_section', name='save_course_sub_section'),
                        url(r'^/structure/units/$', 'add_units', name='add_units'),
						            url(r'^/course_detail/(?P<_id>[\w-]+)$', 'course_detail', name='course_detail'),
                        url(r'^/(?P<_id>[\w-]+)$', 'course_detail', name='course_detail'),
                       )
