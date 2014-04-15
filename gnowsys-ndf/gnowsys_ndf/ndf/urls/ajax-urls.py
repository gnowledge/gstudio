from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import *


urlpatterns = patterns('gnowsys_ndf.ndf.views.ajax_views',                        
                       url(r'^collection/', 'select_drawer', name='select_drawer'),
                       url(r'^collectionNav/', 'collection_nav', name='collection_nav'),
                       url(r'^collectionView/', 'collection_view', name='collection_view'),
                       url(r'^shelf/', 'shelf', name='shelf'),
                       url(r'^change_group_settings/', 'change_group_settings', name='change_group_settings'),                 
                       url(r'^make_module/', 'make_module_set', name='make_module'),                 
                       url(r'^get_module_json/', 'get_module_json', name='get_module_json'),
                       url(r'^get_graph_json/', 'graph_nodes', name='get_graph_json'),
                       url(r'^get_data_for_drawer/', 'get_data_for_drawer', name='get_data_for_drawer'),
                       url(r'^get_data_for_drawer_of_attributetype_set/', 'get_data_for_drawer_of_attributetype_set', name='get_data_for_drawer_of_attributetype_set'),
                       url(r'^get_data_for_drawer_of_relationtype_set/', 'get_data_for_drawer_of_relationtype_set', name='get_data_for_drawer_of_relationtype_set'),                
                       url(r'^deletionInstances/', 'deletion_instances', name='deletion_instances'),
                       url(r'^get_visited_location/', 'get_visited_location', name='get_visited_location')

)
