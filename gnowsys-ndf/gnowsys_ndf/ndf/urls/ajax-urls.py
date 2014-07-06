from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import *


urlpatterns = patterns('gnowsys_ndf.ndf.views.ajax_views',                        
                       url(r'^collection/', 'select_drawer', name='select_drawer'),
                       url(r'^collectionNav/', 'collection_nav', name='collection_nav'),
                       url(r'^collectionView/', 'collection_view', name='collection_view'),
                       url(r'^shelf/', 'shelf', name='shelf'),
                       url(r'^add_subThemes/', 'add_sub_themes', name='add_sub_themes'),
                       url(r'^deleteThemes/', 'delete_themes', name='delete_themes'),
                       url(r'^add_Topics/', 'add_topics', name='add_topics'),
                       url(r'^get_tree_hierarchy/(?P<node_id>[\w-]+)$', 'get_tree_hierarchy', name='get_tree_hierarchy'),
                       url(r'^drawer/', 'drawer_widget', name='drawer_widget'),
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
                       url(r'^get_author_set_users/', 'get_author_set_users', name="get_author_set_users"),
                       url(r'^get_filterd_user_list/', 'get_filterd_user_list', name="get_filterd_user_list"),
                       url(r'^search_tasks/', 'search_tasks', name="search_tasks"),
                       url(r'^get_group_member_user/', 'get_group_member_user', name="get_group_member_user"),
                       url(r'^remove_user_from_author_set/', 'remove_user_from_author_set', name="remove_user_from_author_set"),
                       url(r'^get_data_for_user_drawer/', 'get_data_for_user_drawer', name='get_data_for_user_drawer'),
                       url(r'^get_data_for_batch_drawer/', 'get_data_for_batch_drawer', name='get_data_for_batch_drawer'),

                       url(r'^set_user_link/', 'set_user_link', name='set_user_link'),
                       
)
