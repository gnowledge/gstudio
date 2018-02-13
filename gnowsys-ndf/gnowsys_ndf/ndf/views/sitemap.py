# from django.contrib.sitemaps import Sitemap
import datetime
import json
from gnowsys_ndf.ndf.models import *
from django.shortcuts import render_to_response  # , render  uncomment when to use
from django.template import RequestContext

def sitemap(request):
    print "******************* Inseide sitemap mongokit.cursor.Cursor"
    all_groups = node_collection.find({"_type":"Group"})
    sitemap_structure = __get_sitemap_hierarchy(all_groups)
    return render_to_response("ndf/sitemap.html",
                                {"name":"name",'sitemap_structure':json.dumps(sitemap_structure,cls=NodeJSONEncoder)},
                                context_instance = RequestContext(request)
    )

def __get_sitemap_hierarchy(group_objects,lang="en"):
    '''
    ARGS: unit_group_obj
    Result will be of following form:
    {
        name: 'Lesson1',
        type: 'lesson',
        id: 'l1',
        activities: [
            {
                name: 'Activity 1',
                type: 'activity',
                id: 'a1'
            },
            {
                name: 'Activity 1',
                type: 'activity',
                id: 'a2'
            }
        ]
    }, {
        name: 'Lesson2',
        type: 'lesson',
        id: 'l2',
        activities: [
            {
                name: 'Activity 1',
                type: 'activity',
                id: 'a1'
            }
        ]
    }
    '''
    sitemap_structure = []
    for each in group_objects:
        group_dict ={}
        group = Node.get_node_by_id(each._id)
        if group:
            group_dict['label'] = group.altnames or group.name
            group_dict['type'] = 'unit-name'
            group_dict['id'] = str(group._id)
            group_dict['children'] = []
            if group.collection_set:
                for each_act in group.collection_set:
                    section_dict ={}
                    section = Node.get_node_by_id(each_act)
                    if section:
                        if section.collection_set:
                            section_dict['first_act']  = section.collection_set[0]     
                        section_dict['label'] = section.altnames or section.name
                        section_dict['type'] = 'activity-group'
                        section_dict['id'] = str(section._id)
                        section_dict['group_id'] = str(group._id)
                        group_dict['children'].append(section_dict)
            sitemap_structure.append(group_dict)
    return sitemap_structure