from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.course',
                        url(r'^[/]$', 'course', name='course'),

                        #  url(r'^/(?P<course_id>[\w-]+)$', 'course', name='course'),
                        url(r'^/create/$', 'create_edit', name='create_edit'),

                        url(r'^/ann_course/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)$', 'course_create_edit', name='ann_course_create_edit'),
                        url(r'^/edit/(?P<node_id>[\w-]+)$', 'create_edit', name='create_edit'),

                        url(r'^/course_detail/(?P<_id>[\w-]+)$', 'course_detail', name='course_detail'),
                        url(r'^/(?P<_id>[\w-]+)$', 'mis_course_detail', name='mis_course_detail'),

                        # Course structure set up urls
                        url(r'^/structure/create/(?P<node_id>[\w-]+)$', 'create_course_struct', name='create_course_struct'),
                        url(r'^/create_cs/$', 'save_course_section', name='save_course_section'),
                        url(r'^/create_css/$', 'save_course_sub_section', name='save_course_sub_section'),
                        url(r'^/course_sub_section_prop/$', 'course_sub_section_prop', name='course_sub_section_prop'),
                        url(r'^/resources/', 'get_resources', name='get_resources'),
                        url(r'^/add_units/', 'add_units', name='add_units'),
                        url(r'^/save_res/', 'save_resources', name='save_resources'),
                        url(r'^/create_edit_unit/', 'create_edit_unit', name='create_edit_unit'),
                        url(r'^/change_node_name/$', 'change_node_name', name='change_node_name'),
                        url(r'^/change_order/$', 'change_order', name='change_order'),
                        url(r'^/delete/$', 'delete_from_course_structure', name='delete_from_cs'),
                        url(r'^/enroll/$', 'enroll_generic', name='course_enroll'),
                       )
