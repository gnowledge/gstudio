from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.gcourse',
                        url(r'^[/]$', 'course', name='course'),

                        #  url(r'^/(?P<course_id>[\w-]+)$', 'course', name='course'),
                        url(r'^/create/$', 'create_edit', name='create_edit'),

                        url(r'^/ann_course/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)$', 'course_create_edit', name='ann_course_create_edit'),
                        url(r'^/edit/(?P<node_id>[\w-]+)$', 'create_edit', name='create_edit'),

                        url(r'^/course_detail/(?P<_id>[\w-]+)$', 'course_detail', name='course_detail'),
                        url(r'^/mis_course_detail/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/(?P<app_set_instance_id>[\w-]+)$', 'mis_course_detail', name='mis_course_detail'),  # mis_app_instance_detail

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
                        url(r'^/delete_from_structure/$', 'delete_from_course_structure', name='delete_from_cs'),
                        url(r'^/delete/(?P<node_id>[\w-]+)$', 'delete_course', name='del_course'),
                        url(r'^/remove/$', 'remove_resource_from_unit', name='remove_resource_from_unit'),
                        url(r'^/add_course_file/$', 'add_course_file', name='add_course_file'),
                        url(r'^/enroll_to_course/$', 'enroll_to_course', name='enroll_to_course'),
                        url(r'^/unsubscribe_from_group/$', 'unsubscribe_from_group', name='unsubscribe_from_group'),
                        url(r'^/set_release_date_css/$', 'set_release_date_css', name='set_release_date_css'),
                        url(r'^/summary/$', 'course_summary', name='course_summary'),
                        
                        # url(r'^/units/$', 'course_resource_detail', name='course_resource_detail'),
                        url(r'^/course_section/(?P<course_sub_section>[\w-]+)/(?P<course_unit>[\w-]+)/(?P<resource_id>[\w-]+)/$', 'course_resource_detail', name='course_resource_detail'),
                        url(r'^/dashboard/$', 'course_dashboard', name='course_dashboard'),
                        url(r'^/content/$', 'course_content', name='course_content'),
                        url(r'^/notebook/$', 'course_notebook', name='course_notebook'),
                        url(r'^/notebook/(?P<tab>[\w-]+)/(?P<node_id>[\w-]+)$', 'course_notebook', name='course_notebook_tab_note'),
                        url(r'^/notebook/(?P<node_id>[\w-]+)$', 'course_notebook', name='course_notebook_note'),
                        url(r'^/raw-material/$', 'course_raw_material', name='course_raw_material'),
                        url(r'^/raw-material/(?P<node_id>[\w-]+)$', 'course_raw_material', name='course_raw_material_detail'),
                        url(r'^/raw-material/page-no=(?P<page_no>\d+)/$', 'course_raw_material', name='course_raw_material_paged'),
                        url(r'^/gallery/$', 'course_gallery', name='course_gallery'),
                        url(r'^/gallery/(?P<node_id>[\w-]+)$', 'course_gallery', name='course_gallery_detail'),
                        url(r'^/gallery/page-no=(?P<page_no>\d+)/$', 'course_gallery', name='course_gallery_paged'),

                        url(r'^/filters/$', 'course_filters', name='course_filters'),
                        url(r'^/about/$', 'course_about', name='course_about'),
                        url(r'^/course_gallerymodal/$', 'course_gallerymodal', name='course_gallerymodal'),
                        url(r'^/course_note_page/$', 'course_note_page', name='course_note_page'),
                        url(r'^/inline_edit_res/$', 'inline_edit_res', name='inline_edit_res'),
                        url(r'^/course_analytics/(?P<user_id>[\w-]+)$', 'course_analytics', name='course_analytics'),
                        url(r'^build_progress_bar/(?P<node_id>[\w-]+)$', 'build_progress_bar', name='build_progress_bar'),
                        url(r'^/course_analytics_admin/$', 'course_analytics_admin', name='course_analytics_admin'),
                        url(r'^/get_resource_completion_status/$', 'get_resource_completion_status', name='get_resource_completion_status'),
                        url(r'^/manage_users/$', 'manage_users', name='manage_users'),
                        #Asset URLS
                        url(r'^/asset_list/$','assets', name='asset_list'),
                        url(r'^/asset_list/page-no=(?P<page_no>\d+)/$', 'assets', name='course_assets_paged'),
                        url(r'^/asset_detail/(?P<asset_id>[\w-]+)$', 'assets', name='asset_detail'),
                        url(r'^/asset_detail/(?P<asset_id>[\w-]+)/page-no=(?P<page_no>\d+)$', 'assets', name='asset_details_paged'),
                        url(r'^/asset_detail/(?P<asset_id>[\w-]+)/asset_content/(?P<asst_content_id>[\w-]+)$', 'assetcontent_detail', name='assetcontent_detail'),
                        url(r'^/asset_detail/(?P<asset_id>[\w-]+)/asset_content/(?P<asst_content_id>[\w-]+)/page-no=(?P<page_no>\d+)$', 'assetcontent_detail', name='assetcontent_detail_paged'),
                        
                        url(r'^/activity_player/(?P<lesson_id>[\w-]+)/(?P<activity_id>[\w-]+)/$', 'activity_player_detail', name='activity_player_detail'),
                        
                        url(r'^/activities/$', 'course_pages', name='course_pages'),
                        url(r'^/activities/page-no=(?P<page_no>\d+)/$', 'course_pages', name='course_pages_paged'),
                        url(r'^/activity/detail/(?P<page_id>[\w-]+)$', 'course_pages', name='view_course_page'),
                        url(r'^/activity/create$', 'create_edit_course_page', name='create_course_page'),
                        url(r'^/activity/create/(?P<page_type>[\w-]+)$', 'create_edit_course_page', name='create_course_page_info'),
                        url(r'^/activity/edit/(?P<page_id>[\w-]+)$', 'create_edit_course_page', name='edit_course_page'),


                        url(r'^/load_content_data/$', 'load_content_data', name='load_content_data'),
                        url(r'^/save_course_page/$', 'save_course_page', name='save_course_page'),
                        url(r'^/delete_activity_page/$', 'delete_activity_page', name='delete_activity_page'),
                        url(r'^/widget_page_create_edit/$', 'widget_page_create_edit', name='widget_page_create_edit'),
                        url(r'^/load_assessment_analytics/$', 'load_assessment_analytics', name='load_assessment_analytics'),
                        url(r'^/quiz_data/$', 'course_quiz_data', name='course_quiz_data'),
                        url(r'^/finish_lesson/(?P<node_id>[\w-]+)$', 'finish_lesson', name='finish_lesson'),
                       )
