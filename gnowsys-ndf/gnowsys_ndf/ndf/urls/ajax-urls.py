from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import *


urlpatterns = patterns('gnowsys_ndf.ndf.views.ajax_views',                        
                       url(r'^collection/', 'select_drawer', name='select_drawer'),
                       url(r'^collectionNav/', 'collection_nav', name='collection_nav'),
                       url(r'^collectionView/', 'collection_view', name='collection_view'),
                       url(r'^shelf/', 'shelf', name='shelf'),
                       url(r'^add_subThemes/', 'add_sub_themes', name='add_sub_themes'),
                       url(r'^add_ThemeItems', 'add_theme_item', name='add_theme_item'),
                       url(r'^add_pages/', 'add_page', name='add_page'),
                       url(r'^add_files/', 'add_file', name='add_file'),
                       url(r'^deleteThemes/', 'delete_themes', name='delete_themes'),
                       url(r'^add_Topics/', 'add_topics', name='add_topics'),
                       url(r'^get_tree_hierarchy/(?P<node_id>[\w-]+)$', 'get_tree_hierarchy', name='get_tree_hierarchy'),
                       url(r'^get_collection/(?P<node_id>[\w-]+)$', 'get_collection', name='get_collection'),
                       url(r'^drawer/', 'drawer_widget', name='drawer_widget'),
                       url(r'^search/', 'search_drawer', name='search_drawer'),
                       url(r'^terms/', 'terms_list', name='terms_list'),
                       url(r'^change_group_settings/', 'change_group_settings', name='change_group_settings'),                 
                       url(r'^make_module/', 'make_module_set', name='make_module'),                 
                       url(r'^get_module_json/', 'get_module_json', name='get_module_json'),
                       url(r'^get_graph_json/', 'graph_nodes', name='get_graph_json'),
                       url(r'^get_data_for_drawer/', 'get_data_for_drawer', name='get_data_for_drawer'),
                       url(r'^get_data_for_drawer_of_attributetype_set/', 'get_data_for_drawer_of_attributetype_set', name='get_data_for_drawer_of_attributetype_set'),
                       url(r'^get_data_for_drawer_of_relationtype_set/', 'get_data_for_drawer_of_relationtype_set', name='get_data_for_drawer_of_relationtype_set'),                
                       url(r'^deletionInstances/', 'deletion_instances', name='deletion_instances'),
                       url(r'^get_visited_location/', 'get_visited_location', name='get_visited_location'),
                       url(r'^get_online_editing_user/', 'get_online_editing_user', name="get_online_editing_user"),
                       url(r'^view_articles/', 'view_articles', name="view_articles"),
                       url(r'^get_author_set_users/', 'get_author_set_users', name="get_author_set_users"),
                       url(r'^get_filterd_user_list/', 'get_filterd_user_list', name="get_filterd_user_list"),
                       url(r'^search_tasks/', 'search_tasks', name="search_tasks"),
                       url(r'^get_group_member_user/', 'get_group_member_user', name="get_group_member_user"),
                       url(r'^remove_user_from_author_set/', 'remove_user_from_author_set', name="remove_user_from_author_set"),
                       url(r'^get_data_for_user_drawer/', 'get_data_for_user_drawer', name='get_data_for_user_drawer'),
                       url(r'^get_data_for_batch_drawer/', 'get_data_for_batch_drawer', name='get_data_for_batch_drawer'),

                       # Ajax-urls required for MIS --------------------------------
                       
                       url(r'^get_students_for_batches/', 'get_students_for_batches', name='get_students_for_batches'),
                       url(r'^get_anncourses_allstudents/', 'get_anncourses_allstudents', name='get_anncourses_allstudents'),
                       url(r'^get_courses/', 'get_courses', name='get_courses'),
                       
                       url(r'^get_enroll_duration_of_ac/', 'get_enroll_duration_of_ac', name='get_enroll_duration_of_ac'),
                       url(r'^get_announced_courses_with_ctype/', 'get_announced_courses_with_ctype', name='get_announced_courses_with_ctype'),
                       url(r'^get_colleges/', 'get_colleges', name='get_colleges'),
                       url(r'^get_districts/', 'get_districts', name='get_districts'),
                       url(r'^get_affiliated_colleges/', 'get_affiliated_colleges', name='get_affiliated_colleges'),
                       url(r'^get_students/', 'get_students', name='get_students'),
                       url(r'^get_enrolled_students_count/', 'get_enrolled_students_count', name='get_enrolled_students_count'),
                       
                       url(r'^get_college_wise_students_data/', 'get_college_wise_students_data', name='get_college_wise_students_data'),
                       url(r'^set_user_link/', 'set_user_link', name='set_user_link'),
                       url(r'^set_enrollment_code/', 'set_enrollment_code', name='set_enrollment_code'),
                       url(r'^get_students_assignments/', 'get_students_assignments', name='get_students_assignments'),
                       url(r'^get_course_details_for_trainer/', 'get_course_details_for_trainer', name='get_course_details_for_trainer'),
                       # ===========================================================
                       
                       url(r'^edit_task_title/', 'edit_task_title', name='edit_task_title'),
                       url(r'^events/', 'get_data_for_event_task', name='get_data_for_event_task'),
                       url(r'^edit_task_content/', 'edit_task_content', name='edit_task_content'),
                       url(r'^insert_picture/', 'insert_picture', name="insert_picture"),
)
