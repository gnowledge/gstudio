''' -- imports from python libraries -- '''
import os
import ast
# from datetime import datetime
import datetime
import multiprocessing as mp

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response  # , render  uncomment when to use
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# from mongokit import paginator

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
''' -- imports from application folders/files -- '''
# from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.models import NodeJSONEncoder
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.organization import *
from gnowsys_ndf.ndf.views.course import *
from gnowsys_ndf.ndf.views.person import *
from gnowsys_ndf.ndf.views.enrollment import *
from gnowsys_ndf.ndf.views.methods import get_group_name_id, cast_to_data_type
from gnowsys_ndf.ndf.views.methods import get_execution_time


@login_required
@get_execution_time
def mis_detail(request, group_id, app_id=None, app_set_id=None, app_set_instance_id=None, app_name=None):
    """
    custom view for custom GAPPS
    """

    auth = None
    # if ObjectId.is_valid(group_id) is False :
    #   group_ins = node_collection.one({'_type': "Group","name": group_id})
    #   auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #   if group_ins:
    #     group_id = str(group_ins._id)
    #   else :
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if auth :
    #       group_id = str(auth._id)
    # else :
    #   pass
    group_name, group_id = get_group_name_id(group_id)
    app = None
    if app_id is None:
      app = node_collection.one({'_type': "GSystemType", 'name': app_name})
      if app:
        app_id = str(app._id)
    else:
      app = node_collection.one({'_id': ObjectId(app_id)})

    app_name = app.name

    app_collection_set = []
    atlist = []
    rtlist = []

    app_set = ""
    nodes = ""
    # nodes_dict = ""
    nodes_keys = []
    app_menu = ""
    app_set_template = ""
    app_set_instance_template = ""
    app_set_instance_name = ""
    app_set_name = ""
    title = ""
    tags = ""
    content = ""
    location = ""
    system = None
    system_id = ""
    system_type = ""
    system_mime_type = ""
    template = ""
    property_display_order = []
    events_arr = []
    university_wise_students_count = []

    template_prefix = "mis"

    if request.user.id:
      if auth is None:
        auth = node_collection.one({'_type': 'Author', 'created_by':int(request.user.id)})

      agency_type = auth.agency_type
      agency_type_node = node_collection.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
      if agency_type_node:
        #b=app_collection_set.append
        #for eachset in agency_type_node.collection_set:
        #  b(a({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))

        # loop replaced by a list comprehension
        app_collection_set=[node_collection.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}) for eachset in agency_type_node.collection_set]


    # for eachset in app.collection_set:
    #   app_collection_set.append(node_collection.one({"_id":eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))
      # app_set = node_collection.find_one({"_id":eachset})
      # app_collection_set.append({"id": str(app_set._id), "name": app_set.name, 'type_of'})

    if app_set_id:
      app_set = node_collection.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})

      view_file_extension = ".py"
      app_set_view_file_name = ""
      app_set_view_file_path = ""

      if app_set.type_of:
        app_set_type_of = node_collection.one({'_type': "GSystemType", '_id': ObjectId(app_set.type_of[0])}, {'name': 1})

        app_set_view_file_name = app_set_type_of.name.lower().replace(" ", "_")
        # print "\n app_set_view_file_name (type_of): ", app_set_view_file_name, "\n"

      else:
        app_set_view_file_name = app_set.name.lower().replace(" ", "_")
        # print "\n app_set_view_file_name: ", app_set_view_file_name, "\n"

      app_set_view_file_path = os.path.join(os.path.dirname(__file__), app_set_view_file_name + view_file_extension)
      # print "\n app_set_view_file_path: ", app_set_view_file_path, "\n"

      if os.path.exists(app_set_view_file_path):
        # print "\n Call this function...\n"
        if app_set_view_file_name == "course":
          app_set_view_file_name = "mis_course"
        return eval(app_set_view_file_name + "_detail")(request, group_id, app_id, app_set_id, app_set_instance_id, app_name)

      # print "\n Perform fallback code...\n"

      classtype = ""
      app_set_template = "yes"
      template = "ndf/"+template_prefix+"_list.html"

      systemtype = node_collection.find_one({"_id":ObjectId(app_set_id)})
      systemtype_name = systemtype.name
      title = systemtype_name

      if request.method=="POST":
        search = request.POST.get("search","")
        classtype = request.POST.get("class","")
        nodes = list(node_collection.find({'name':{'$regex':search, '$options': 'i'},'member_of': {'$all': [systemtype._id]}}, {'name': 1}).sort('name', 1))
      else :
        nodes = list(node_collection.find({'member_of': {'$all': [systemtype._id]},'group_set':{'$all': [ObjectId(group_id)]}}, {'name': 1}).sort('name', 1))

      nodes_keys = [('name', "Name")]
      # nodes_dict = []
      # for each in nodes:
      #   nodes_dict.append({"p_id":str(each._id), "name":each.name, "created_by":User.objects.get(id=each.created_by).username, "created_at":each.created_at})

    else :
      app_menu = "yes"
      template = "ndf/"+template_prefix+"_list.html"
      title = app_name

      university_gst = node_collection.one({'_type': "GSystemType", 'name': "University"})
      student_gst = node_collection.one({'_type': "GSystemType", 'name': "Student"})

      mis_admin = node_collection.one(
          {'_type': "Group", 'name': "MIS_admin"},
          {'_id': 1}
      )

      university_cur = node_collection.find(
        {'member_of': university_gst._id, 'group_set': mis_admin._id},
        {'name': 1, 'relation_set.affiliated_college': 1}
      ).sort('name', 1)

      for each_university in university_cur:
        affiliated_college_ids_list = []
        for rel in each_university.relation_set:
          if rel and "affiliated_college" in rel:
            affiliated_college_ids_list = rel["affiliated_college"]
            break

        students_cur = node_collection.find(
          {
            'member_of': student_gst._id,
            'relation_set.student_belongs_to_college': {'$in': affiliated_college_ids_list}
          }
        )

        # university_wise_students_count[each_university.name] = students_cur.count()
        university_wise_students_count.append((each_university.name, students_cur.count()))

    if app_set_instance_id :
        app_set_instance_template = "yes"
        template = "ndf/"+template_prefix+"_details.html"

        app_set_template = ""
        systemtype_attributetype_set = []
        systemtype_relationtype_set = []
        system = node_collection.find_one({"_id":ObjectId(app_set_instance_id)})
        systemtype = node_collection.find_one({"_id":ObjectId(app_set_id)})
        #for each in systemtype.attribute_type_set:
        #    systemtype_attributetype_set.append({"type":each.name,"type_id":str(each._id),"value":each.data_type})
        #loop replaced by a list comprehension
        systemtype_attributetype_set=[{"type":each.name,"type_id":str(each._id),"value":each.data_type} for each in systemtype.attribute_type_set]
        #for each in systemtype.relation_type_set:
        #    systemtype_relationtype_set.append({"rt_name":each.name,"type_id":str(each._id)})
        #loop replaced by a list comprehension
        systemtype_relationtype_set=[{"rt_name":each.name,"type_id":str(each._id)} for each in systemtype.relation_type_set]
        #temp. variables which stores the lookup for append method
        atlist_append_temp=atlist.append
        rtlist_append_temp=rtlist.append
        for eachatset in systemtype_attributetype_set :
            for eachattribute in triple_collection.find({"_type":"GAttribute", "subject":system._id, "attribute_type":ObjectId(eachatset["type_id"])}):
                atlist_append_temp({"type":eachatset["type"],"type_id":eachatset["type_id"],"value":eachattribute.object_value})
        for eachrtset in systemtype_relationtype_set :
            for eachrelation in triple_collection.find({"_type":"GRelation", "subject":system._id, "relation_type":ObjectId(eachrtset["type_id"])}):
                right_subject = node_collection.find_one({"_id":ObjectId(eachrelation.right_subject)})
                rtlist_append_temp({"type":eachrtset["rt_name"],"type_id":eachrtset["type_id"],"value_name": right_subject.name,"value_id":str(right_subject._id)})

        # To support consistent view

        property_order = system.property_order
        system.get_neighbourhood(systemtype._id)

        # array of dict for events ---------------------
        #a temp. variable which stores the lookup for append method
        events_arr_append_temp=events_arr.append
        # if system.has_key('organiser_of_event') and len(system.organiser_of_event): # gives list of events
        if 'organiser_of_event' in system and len(system.organiser_of_event): # gives list of events
            for event in system.organiser_of_event:
                event.get_neighbourhood(event.member_of)

                tempdict = {}
                tempdict['title'] = event.name

                if event.start_time:# and len(event.start_time) == 16:
                    # print "\n start_time: ", event.start_time, " -- ", event.start_time.strftime('%m/%d/%Y %H:%M')
                    # dt = datetime.datetime.strptime(event.start_time , '%m/%d/%Y %H:%M')
                    dt = event.start_time.strftime('%m/%d/%Y %H:%M')
                    tempdict['start'] = dt
                if event.end_time:# and len(event.end_time) == 16:
                    # print "\n end_time: ", event.end_time, " -- ", event.end_time.strftime('%m/%d/%Y %H:%M')
                    # dt = datetime.datetime.strptime(event.end_time , '%m/%d/%Y %H:%M')
                    dt = event.end_time.strftime('%m/%d/%Y %H:%M')
                    tempdict['end'] = dt
                tempdict['id'] = str(event._id)
                events_arr_append_temp(tempdict)

        # elif system.has_key('event_organised_by'): # gives list of colleges/host of events
        elif 'event_organised_by' in system:  # gives list of colleges/host of events

            for host in system.event_organised_by:
                host.get_neighbourhood(host.member_of)

                tempdict = {}
                tempdict['title'] = host.name

                if system.start_time:# and len(system.start_time) == 16:
                    # dt = datetime.datetime.strptime(system.start_time , '%m/%d/%Y %H:%M')
                    dt = event.start_time.strftime('%m/%d/%Y %H:%M')
                    tempdict['start'] = dt
                if system.end_time:# and len(system.start_time) == 16:
                    # dt = datetime.datetime.strptime(system.end_time , '%m/%d/%Y %H:%M')
                    dt = event.end_time.strftime('%m/%d/%Y %H:%M')
                    tempdict['end'] = dt

                tempdict['id'] = str(host._id)
                events_arr_append_temp(tempdict)

        # print json.dumps(events_arr)

        # END --- array of dict for events ---------------------
        #a temp. variable which stores the lookup for append method
        property_display_order_append_temp=property_display_order.append
        for tab_name, fields_order in property_order:
            display_fields = []
            #a temp. variable which stores the lookup for append method
            display_fields_append_temp=display_fields.append
            for field, altname in fields_order:
                if system.structure[field] == bool:
                    display_fields_append_temp((altname, ("Yes" if system[field] else "No")))

                elif not system[field]:
                    display_fields_append_temp((altname, system[field]))
                    continue

                elif system.structure[field] == datetime.datetime:
                    display_fields_append_temp((altname, system[field].date()))

                elif type(system.structure[field]) == list:
                    if system[field]:
                        if type(system.structure[field][0]) == ObjectId:
                            name_list = []
                            for right_sub_dict in system[field]:
                                name_list.append(right_sub_dict.name)
                            display_fields_append_temp((altname, ", ".join(name_list)))
                        elif system.structure[field][0] == datetime.datetime:
                            date_list = []
                            #for dt in system[field]:
                            #    date_list.append(dt.strftime("%d/%m/%Y"))
                            date_list=[dt.strftime("%d/%m/%Y") for dt in system[field]]
                            display_fields_append_temp((altname, ", ".join(date_list)))
                        else:
                            display_fields_append_temp((altname, ", ".join(system[field])))

                else:
                    display_fields_append_temp((altname, system[field]))

            property_display_order_append_temp((tab_name, display_fields))

        # End of code

        tags = ",".join(system.tags)
        content = system.content
        location = system.location
        app_set_name = systemtype.name
        system_id = system._id
        system_type = system._type

        # print "\n app_set_instance_name: ", app_set_instance_name
        # print "\n app_set_name: ", app_set_name

        if system_type == 'File':
            system_mime_type = system.mime_type

        app_set_instance_name = system.name
        title =  systemtype.name +"-" +system.name



    variable = RequestContext(request, {
                                        'group_id':group_id, 'groupid':group_id, 'app_name':app_name, 'app_id':app_id,
                                        "app_collection_set":app_collection_set, "app_set_id":app_set_id,
                                        "nodes":nodes, "nodes_keys": nodes_keys, "app_menu":app_menu, "app_set_template":app_set_template,
                                        "app_set_instance_template":app_set_instance_template, "app_set_name":app_set_name,
                                        "app_set_instance_name":app_set_instance_name, "title":title,
                                        "app_set_instance_atlist":atlist, "app_set_instance_rtlist":rtlist,
                                        'tags':tags, 'location':location, "content":content, "system_id":system_id,
                                        "system_type":system_type,"mime_type":system_mime_type, "app_set_instance_id":app_set_instance_id,
                                        "node":system, 'group_id':group_id, "property_display_order": property_display_order,
                                        "events_arr":events_arr, 'university_wise_students_count': university_wise_students_count
                                        })

    return render_to_response(template, variable)


@login_required
@get_execution_time
def mis_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
    """
    create new instance of app_set of apps view for custom GAPPS
    """
    auth = None
    group_name, group_id = get_group_name_id(group_id)
    # if ObjectId.is_valid(group_id) is False :
    #   group_ins = node_collection.one({'_type': "Group","name": group_id})
    #   auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #   if group_ins:
    #     group_id = str(group_ins._id)
    #   else :
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if auth :
    #       group_id = str(auth._id)
    # else :
    #   pass

    app = None
    if app_id is None:
      app = node_collection.one({'_type': "GSystemType", 'name': app_name})
      if app:
        app_id = str(app._id)
    else:
      app = node_collection.one({'_id': ObjectId(app_id)})

    app_name = app.name

    # app_name = "mis"
    app_collection_set = []
    # app = node_collection.find_one({"_id":ObjectId(app_id)})
    app_set = ""
    app_set_instance_name = ""
    nodes = ""
    systemtype = ""
    title = ""
    tags = ""
    location=""
    content_org = ""
    system_id = ""
    system_type = ""
    system_mime_type = ""
    systemtype_name = ""
    systemtype_attributetype_set = []
    systemtype_relationtype_set = []
    title = ""
    file_st_ids = []
    app_type_of_id = ""
    File = 'False'
    obj_id_ins = ObjectId()

    template_prefix = "mis"

    user_id = int(request.user.id)  # getting django user id
    user_name = unicode(request.user.username)  # getting django user name

    if request.user.id:
      if auth is None:
        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username)})
      agency_type = auth.agency_type
      agency_type_node = node_collection.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
      if agency_type_node:
      # for eachset in agency_type_node.collection_set:
     #  app_collection_set.append(node_collection.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))

        #loop replaced by a list comprehension
        app_collection_set=[node_collection.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}) for eachset in agency_type_node.collection_set]
    # for eachset in app.collection_set:
    #   app_collection_set.append(node_collection.one({"_id":eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))
      # app_set = node_collection.find_one({"_id":eachset})
      # app_collection_set.append({"id": str(app_set._id), "name": app_set.name, 'type_of'})

    if app_set_id:
        app_set = node_collection.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})

        view_file_extension = ".py"
        app_set_view_file_name = ""
        app_set_view_file_path = ""

        if app_set.type_of:
            app_set_type_of = node_collection.one({'_type': "GSystemType", '_id': ObjectId(app_set.type_of[0])}, {'name': 1})

            app_set_view_file_name = app_set_type_of.name.lower().replace(" ", "_")
            # print "\n app_set_view_file_name (type_of): ", app_set_view_file_name, "\n"

        else:
            app_set_view_file_name = app_set.name.lower().replace(" ", "_")
            # print "\n app_set_view_file_name: ", app_set_view_file_name, "\n"

        app_set_view_file_path = os.path.join(os.path.dirname(__file__), app_set_view_file_name + view_file_extension)
        # print "\n app_set_view_file_path: ", app_set_view_file_path, "\n"

        if os.path.exists(app_set_view_file_path):
            # print "\n Call this function...\n"
            return eval(app_set_view_file_name + "_create_edit")(request, group_id, app_id, app_set_id, app_set_instance_id, app_name)


        # print "\n Perform fallback code...\n"

        systemtype = node_collection.find_one({"_id":ObjectId(app_set_id)})
        systemtype_name = systemtype.name
        title = systemtype_name + " - new"
       # for each in systemtype.attribute_type_set:
        #    systemtype_attributetype_set.append({"type":each.name,"type_id":str(each._id),"value":each.data_type, 'sub_values': each.complex_data_type, 'altnames': each.altnames})

        #loop replaced by a list comprehension
        systemtype_attributetype_set=[{"type":each.name,"type_id":str(each._id),"value":each.data_type, 'sub_values': each.complex_data_type, 'altnames': each.altnames} for each in systemtype.attribute_type_set]

        #a temp. variable which stores the lookup for append method
        sys_type_relation_set_append= systemtype_relationtype_set.append
        for eachrt in systemtype.relation_type_set:
            # object_type = [ {"name":rtot.name, "id":str(rtot._id)} for rtot in node_collection.find({'member_of': {'$all': [ node_collection.find_one({"_id":eachrt.object_type[0]})._id]}}) ]
            object_type_cur = node_collection.find({'member_of': {'$in': eachrt.object_type}})
            object_type = []
           # for each in object_type_cur:
           #   object_type.append({"name":each.name, "id":str(each._id)})
            object_type=[{"name":each.name, "id":str(each._id)} for each in object_type_cur]
            sys_type_relation_set_append({"rt_name": eachrt.name, "type_id": str(eachrt._id), "object_type": object_type})

    request_at_dict = {}
    request_rt_dict = {}

    files_sts = ['File','Image','Video']
    if app_set_id:
        app = node_collection.one({'_id':ObjectId(app_set_id)})
        for each in files_sts:
            node_id = node_collection.one({'name':each,'_type':'GSystemType'})._id
            if node_id in app.type_of:
                File = 'True'

    if app_set_instance_id : # at and rt set editing instance
        system = node_collection.find_one({"_id":ObjectId(app_set_instance_id)})
        #Function used by Processes implemented below
        def multi_(lst):
            for eachatset in lst:
                eachattribute=triple_collection.find_one({"_type":"GAttribute", "subject":system._id, "attribute_type":ObjectId(eachatset["type_id"])})
                if eachattribute :
                    eachatset['database_value'] = eachattribute.object_value
                    eachatset['database_id'] = str(eachattribute._id)
                else :
                    eachatset['database_value'] = ""
                    eachatset['database_id'] = ""
        #this empty list will have the Process objects as its elements
        processes=[]
        #returns no of cores in the cpu
        x=mp.cpu_count()
        n1=len(systemtype_attributetype_set)
        #divides the list into those many parts
        n2=n1/x
         #Process object is created.The list after being partioned is also given as an argument.
        for i in range(x):
            processes.append(mp.Process(target=multi_,args=(systemtype_attributetype_set[i*n2:(i+1)*n2],)))
        for i in range(x):
            processes[i].start()#each Process started
        for i in range(x):
            processes[i].join()#each Process converges

        #Function used by Processes implemented below
        def multi_2(lst):
            for eachrtset in lst:

                eachrelation = triple_collection.find_one({"_type":"GRelation", "subject":system._id, "relation_type":ObjectId(eachrtset["type_id"])})
                if eachrelation:
                    right_subject = node_collection.find_one({"_id":ObjectId(eachrelation.right_subject)})
                    eachrtset['database_id'] = str(eachrelation._id)
                    eachrtset["database_value"] = right_subject.name
                    eachrtset["database_value_id"] = str(right_subject._id)
                else :
                    eachrtset['database_id'] = ""
                    eachrtset["database_value"] = ""
                    eachrtset["database_value_id"] = ""
        #this empty list will have the Process objects as its elements
        processes2=[]
        n1=len(systemtype_relationtype_set)
        #divides the list into those many parts
        n2=n1/x
        #Process object is created.The list after being partioned is also given as an argument.
        for i in range(x):
            processes2.append(mp.Process(target=multi_2,args=(systemtype_relationtype_set[i*n2:(i+1)*n2],)))
        for i in range(x):
            processes2[i].start()#each Process started
        for i in range(x):
            processes2[i].join()#each Process converges


        tags = ",".join(system.tags)
        content_org = system.content_org
        location = system.location
        system_id = system._id
        system_type = system._type
        if system_type == 'File':
            system_mime_type = system.mime_type
        app_set_instance_name = system.name
        title =  system.name+"-"+"edit"

    if request.method=="POST": # post methods
        tags = request.POST.get("tags","")
        content_org = unicode(request.POST.get("content_org",""))
        name = request.POST.get("name","")
        map_geojson_data = request.POST.get('map-geojson-data') # getting markers
        user_last_visited_location = request.POST.get('last_visited_location') # getting last visited location by user
        file1 = request.FILES.get('file', '')
        #Function used by Processes implemented below
        def multi_3(lst):
            for each in lst:
                if request.POST.get(each["type_id"],"") :
                    request_at_dict[each["type_id"]] = request.POST.get(each["type_id"],"")
        #this empty list will have the Process objects as its elements
        processes3=[]
        n1=len(systemtype_attributetype_set)
        #divides the list into those many parts
        n2=n1/x
        #Process object is created.The list after being partioned is also given as an argument.
        for i in range(x):
            processes3.append(mp.Process(target=multi_3,args=(systemtype_attributetype_set[i*n2:(i+1)*n2],)))
        for i in range(x):
            processes3[i].start()#each Process started
        for i in range(x):
            processes3[i].join()#each Process converges
        #Function used by Processes implemented below
        def multi_4(lst):
            for eachrtset in lst:
                if request.POST.get(eachrtset["type_id"],""):
                    request_rt_dict[eachrtset["type_id"]] = request.POST.get(eachrtset["type_id"],"")
        #this empty list will have the Process objects as its elements
        processes4=[]
        n1=len(systemtype_relationtype_set)
        #divides the list into those many parts
        n2=n1/x
        #Process object is created.The list after being partioned is also given as an argument.
        for i in range(x):
            processes4.append(mp.Process(target=multi_4,args=(systemtype_relationtype_set[i*n2:(i+1)*n2],)))
        for i in range(x):
            processes4[i].start()#each Process started
        for i in range(x):
            processes4[i].join()  #each Process converges

        if File == 'True':
            if file1:
                f = save_file(file1, name, request.user.id, group_id, content_org, tags)
                if obj_id_ins.is_valid(f):
                    newgsystem = node_collection.one({'_id':f})
                else:
                    template = "ndf/mis_list.html"
                    variable = RequestContext(request, {'group_id':group_id, 'groupid':group_id, 'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set, "app_set_id":app_set_id, "nodes":nodes, "systemtype_attributetype_set":systemtype_attributetype_set, "systemtype_relationtype_set":systemtype_relationtype_set, "create_new":"yes", "app_set_name":systemtype_name, 'title':title, 'File':File, 'already_uploaded_file':f})
                    return render_to_response(template, variable)
            else:
                newgsystem = node_collection.collection.File()
        else:
            newgsystem = node_collection.collection.GSystem()
        if app_set_instance_id:
            newgsystem = node_collection.find_one({"_id": ObjectId(app_set_instance_id)})

        newgsystem.name = name
        newgsystem.member_of = [ObjectId(app_set_id)]

        if not app_set_instance_id:
            newgsystem.created_by = request.user.id

        newgsystem.modified_by = request.user.id
        newgsystem.status = u"PUBLISHED"

        newgsystem.group_set.append(ObjectId(group_id))

        if tags:
            newgsystem.tags = tags.split(",")

        if content_org:
            usrname = request.user.username
            filename = slugify(newgsystem.name) + "-" + usrname
            # newgsystem.content = org2html(content_org, file_prefix=filename)
            newgsystem.content = content_org
            newgsystem.content_org = content_org

        # check if map markers data exist in proper format then add it into newgsystem
        if map_geojson_data:
            map_geojson_data = map_geojson_data + ","
            map_geojson_data = list(ast.literal_eval(map_geojson_data))
            newgsystem.location = map_geojson_data
            location = map_geojson_data
        else:
            map_geojson_data = []
            location = []
            newgsystem.location = map_geojson_data

        # check if user_group_location exist in proper format then add it into newgsystem
        if user_last_visited_location:

            user_last_visited_location = list(ast.literal_eval(user_last_visited_location))

            author = node_collection.one({'_type': "GSystemType", 'name': "Author"})
            user_group_location = node_collection.one({'_type': "Author", 'member_of': author._id, 'created_by': user_id, 'name': user_name})

            if user_group_location:
                user_group_location['visited_location'] = user_last_visited_location
                user_group_location.save(groupid=group_id)

        newgsystem.save(groupid=group_id)

        if not app_set_instance_id:
            #Function used by Processes implemented below
            def multi_5(lst):
                for key,value in lst:
                    attributetype_key = node_collection.find_one({"_id":ObjectId(key)})
                    ga_node = create_gattribute(newgsystem._id, attributetype_key, value)
            #this empty list will have the Process objects as its elements
            processes5=[]
            lst11=request_at_dict.items()
            n1=len(lst11)
            #divides the list into those many parts
            n2=n1/x
            #Process object is created.The list after being partioned is also given as an argument.
            for i in range(x):
                processes5.append(mp.Process(target=multi_5,args=(lst11[i*n2:(i+1)*n2],)))
            for i in range(x):
                processes5[i].start()#each Process started
            for i in range(x):
                processes5[i].join()#each Process converges
            """
             for key, value in request_rt_dict.items():
                if key:
                    relationtype_key = node_collection.find_one({"_id": ObjectId(key)})
                if value:
                    right_subject = node_collection.find_one({"_id": ObjectId(value)})
                    gr_node = create_grelation(newgsystem._id, relationtype_key, right_subject._id)
                    # newrelation = triple_collection.collection.GRelation()
                    # newrelation.subject = newgsystem._id
                    # newrelation.relation_type = relationtype_key
                    # newrelation.right_subject = right_subject._id
                    # newrelation.save()
            """
            def multi_6(lst):#Function used by Processes implemented below
                for key,value in lst:
                    if key:
                        relationtype_key = node_collection.find_one({"_id": ObjectId(key)})
                    if value:
                        right_subject = node_collection.find_one({"_id": ObjectId(value)})
                        gr_node = create_grelation(newgsystem._id, relationtype_key, right_subject._id)

            #this empty list will have the Process objects as its elements
            processes6=[]
            lst12=request_rt_dict.items()
            n1=len(lst12)
            #divides the list into those many parts
            n2=n1/x
            #Process object is created.The list after being partioned is also given as an argument.
            for i in range(x):
                processes6.append(mp.Process(target=multi_6,args=(lst12[i*n2:(i+1)*n2],)))
            for i in range(x):
                processes6[i].start()#each Process started
            for i in range(x):
                processes6[i].join()#each Process converges


        if app_set_instance_id:
            # editing instance
            """
            for each in systemtype_attributetype_set:
                if each["database_id"]:
                    attribute_instance = triple_collection.find_one({"_id": ObjectId(each['database_id'])})
                    attribute_instance.object_value = request.POST.get(each["database_id"],"")
                    # attribute_instance.save()
                    ga_node = create_gattribute(attribute_instance.subject, attribute_instance.attribute_type, attribute_instance.object_value)
                else:
                    if request.POST.get(each["type_id"], ""):
                        attributetype_key = node_collection.find_one({"_id":ObjectId(each["type_id"])})
                        # newattribute = triple_collection.collection.GAttribute()
                        # newattribute.subject = newgsystem._id
                        # newattribute.attribute_type = attributetype_key
                        # newattribute.object_value = request.POST.get(each["type_id"],"")
                        # newattribute.save()
                        ga_node = create_gattribute(newgsystem._id, attributetype_key, request.POST.get(each["type_id"],""))
            """
            def multi_7(lst):#Function used by Processes implemented below
                for each in lst:
                    if each["database_id"]:
                        attribute_instance = triple_collection.find_one({"_id": ObjectId(each['database_id'])})
                        attribute_instance.object_value = request.POST.get(each["database_id"],"")
                        # attribute_instance.save()
                        ga_node = create_gattribute(attribute_instance.subject, attribute_instance.attribute_type, attribute_instance.object_value)
                    else:
                        if request.POST.get(each["type_id"], ""):
                            attributetype_key = node_collection.find_one({"_id":ObjectId(each["type_id"])})
                            # newattribute = triple_collection.collection.GAttribute()
                            # newattribute.subject = newgsystem._id
                            # newattribute.attribute_type = attributetype_key
                            # newattribute.object_value = request.POST.get(each["type_id"],"")
                            # newattribute.save()
                            ga_node = create_gattribute(newgsystem._id, attributetype_key, request.POST.get(each["type_id"],""))
            #this empty list will have the Process objects as its elements
            processes7=[]
            n1=len(systemtype_attributetype_set)
            #divides the list into those many parts
            n2=n1/x
            #Process object is created.The list after being partioned is also given as an argument.
            for i in range(x):
                processes7.append(mp.Process(target=multi_7,args=(systemtype_attributetype_set[i*n2:(i+1)*n2],)))
            for i in range(x):
                processes7[i].start()#each Process started
            for i in range(x):
                processes7[i].join()#each Process converges


            """
            for eachrt in systemtype_relationtype_set:
                if eachrt["database_id"]:
                    relation_instance = triple_collection.find_one({"_id":ObjectId(eachrt['database_id'])})
                    relation_instance.right_subject = ObjectId(request.POST.get(eachrt["database_id"],""))
                    # relation_instance.save()
                    gr_node = create_grelation(relation_instance.subject, relation_instance.relation_type, relation_instance.right_subject)
                else :
                    if request.POST.get(eachrt["type_id"],""):
                        relationtype_key = node_collection.find_one({"_id":ObjectId(eachrt["type_id"])})
                        right_subject = node_collection.find_one({"_id":ObjectId(request.POST.get(eachrt["type_id"],""))})
                        gr_node = create_grelation(newgsystem._id, relationtype_key, right_subject._id)
                        # newrelation = triple_collection.collection.GRelation()
                        # newrelation.subject = newgsystem._id
                        # newrelation.relation_type = relationtype_key
                        # newrelation.right_subject = right_subject._id
                        # newrelation.save()
            """
            def multi_8(lst):#Function used by Processes implemented below
                for eachrt in lst:
                    if eachrt["database_id"]:
                        relation_instance = triple_collection.find_one({"_id":ObjectId(eachrt['database_id'])})
                        relation_instance.right_subject = ObjectId(request.POST.get(eachrt["database_id"],""))
                    # relation_instance.save()
                        gr_node = create_grelation(relation_instance.subject, relation_instance.relation_type, relation_instance.right_subject)
                    else :
                        if request.POST.get(eachrt["type_id"],""):
                            relationtype_key = node_collection.find_one({"_id":ObjectId(eachrt["type_id"])})
                            right_subject = node_collection.find_one({"_id":ObjectId(request.POST.get(eachrt["type_id"],""))})
                            gr_node = create_grelation(newgsystem._id, relationtype_key, right_subject._id)

            #this empty list will have the Process objects as its elements
            processes8=[]
            n1=len(systemtype_relationtype_set)
            #divides the list into those many parts
            n2=n1/x
            #Process object is created.The list after being partioned is also given as an argument.
            for i in range(x):
                processes8.append(mp.Process(target=multi_4,args=(systemtype_relationtype_set[i*n2:(i+1)*n2],)))
            for i in range(x):
                processes8[i].start()#each Process started
            for i in range(x):
                processes8[i].join() #each Process converges
        return HttpResponseRedirect(reverse(app_name.lower()+":"+template_prefix+'_app_detail', kwargs={'group_id': group_id, "app_id":app_id, "app_set_id":app_set_id}))

    template = "ndf/"+template_prefix+"_create_edit.html"
    variable = RequestContext(request, {'group_id':group_id, 'groupid':group_id, 'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set, "app_set_id":app_set_id, "nodes":nodes, "systemtype_attributetype_set":systemtype_attributetype_set, "systemtype_relationtype_set":systemtype_relationtype_set, "create_new":"yes", "app_set_name":systemtype_name, 'title':title, 'File':File, 'tags':tags, "content_org":content_org, "system_id":system_id,"system_type":system_type,"mime_type":system_mime_type, "app_set_instance_name":app_set_instance_name, "app_set_instance_id":app_set_instance_id, 'location':location})
    return render_to_response(template, variable)


@login_required
@get_execution_time
def mis_enroll(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
    """
    Redirects to student_enroll function of person-view.
    """
    if app_set_id:
        app_set = node_collection.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})

        view_file_extension = ".py"
        app_set_view_file_name = ""
        app_set_view_file_path = ""

        if app_set.type_of:
            app_set_type_of = node_collection.one({'_type': "GSystemType", '_id': ObjectId(app_set.type_of[0])}, {'name': 1})
            app_set_view_file_name = app_set_type_of.name.lower().replace(" ", "_")

        else:
            app_set_view_file_name = app_set.name.lower().replace(" ", "_")

        app_set_view_file_path = os.path.join(os.path.dirname(__file__), app_set_view_file_name + view_file_extension)

        if os.path.exists(app_set_view_file_path):
            return eval(app_set_view_file_name + "_enroll")(request, group_id, app_id, app_set_id, app_set_instance_id, app_name)


    template = "ndf/student_enroll.html"
    variable = RequestContext(request, {'groupid': group_id,
                                        'title':title,
                                        'app_id':app_id, 'app_name': app_name,
                                        'app_collection_set': app_collection_set, 'app_set_id': app_set_id
                                        # 'nodes':nodes,
                                        })
    return render_to_response(template, variable)


@login_required
@get_execution_time
def get_mis_reports(request, group_id, **kwargs):
    title = "Reports"
    group_name, group_id = get_group_name_id(group_id)
    states = []
    selected_filters = 0
    # states -- [first-element: subject (State's ObjectId),
    #            second-element: manipulated-name-value (State's name)]
    query = {}
    response_dict = {}

    state_gst = node_collection.one({'_type': "GSystemType", 'name': "State"})
    mis_admin_grp = node_collection.one({'_type': "Group", 'name': "MIS_admin"})
    state_cur = node_collection.find({'member_of': state_gst._id,
                                      'group_set': mis_admin_grp._id},{'name':1,'_id':1})

    if request.is_ajax() and request.method == "POST":
        state_id = university_id = college_id = None
        end_date = start_date = None
        gst_node = state_node = univ_node = college_node = None
        univ_ids = []
        return_data_set = []
        rec = None
        colg_cur = None
        data_for_report1 = {}
        data_dict = request.POST.get("data_set", "")
        gst_name = request.POST.get("gst_name", "")
        if gst_name == "Event":
            gst_name = "Classroom Session"
        ac_year = request.POST.get("academic_year", "")
        if ac_year:
            if ac_year != "ALL":
                academic_year = ac_year
                date_gte = datetime.datetime.strptime("1/1/" + academic_year, "%d/%m/%Y")
                date_lte = datetime.datetime.strptime("31/12/" + academic_year, "%d/%m/%Y")
                query.update({'attribute_set.registration_date': {'$gte': date_gte, '$lte': date_lte}})

        gst_node = node_collection.one({'_type': 'GSystemType', 'name': unicode(gst_name)})
        # print "gst_node", gst_node.name
        query.update({'member_of': gst_node._id})
        data_dict = json.loads(data_dict)
        univ_gst = node_collection.one({'_type': "GSystemType", 'name': "University"})
        colg_gst = node_collection.one({'_type': "GSystemType", 'name': "College"})
        if "state" in data_dict:
            if data_dict["state"]:
                state_id = data_dict['state']
                if state_id != "ALL":
                    state_node = node_collection.one({'_id': ObjectId(state_id)})
        if "university" in data_dict:
            if data_dict["university"]:
                university_id = data_dict['university']
                if university_id != "ALL":
                    univ_node = node_collection.one({'_id': ObjectId(university_id)})
        if "college" in data_dict:
            if data_dict["college"]:
                college_id = data_dict['college']
                if college_id != "ALL":
                    college_node = node_collection.one({'_id': ObjectId(college_id)})
        if "start_date" in data_dict:
            start_date = data_dict['start_date']
        if "end_date" in data_dict:
            end_date = data_dict['end_date']

        if start_date and end_date:

            start_date = datetime.datetime.strptime(start_date,"%d/%m/%Y")
            end_date = datetime.datetime.strptime(end_date,"%d/%m/%Y")
            query.update({'attribute_set.start_time': {'$gte': start_date}})
            query.update({'attribute_set.end_time': {'$lte': end_date}})
        if state_id and not university_id and not college_id:
            selected_filters = 1
        elif state_id and university_id and not college_id:
            selected_filters = 2
        elif state_id and university_id and college_id:
            selected_filters = 3

        # print "\nselected_filters\n", selected_filters
        if selected_filters == 1:
            if state_id == "ALL":
                state_id_list = []
                for each in state_cur:
                    state_id_list.append(each._id)
                if gst_node.name == "Student":
                    query.update({'relation_set.person_belongs_to_state': {'$in':state_id_list}})
                university_cur = node_collection.find({'member_of': univ_gst._id,
                      'relation_set.organization_belongs_to_state': {'$in':state_id_list},
                      'group_set': mis_admin_grp._id})
            else:
                if gst_node.name == "Student":
                    query.update({'relation_set.person_belongs_to_state': ObjectId(state_id)})

                university_cur = node_collection.find({'member_of': univ_gst._id,
                  'relation_set.organization_belongs_to_state': ObjectId(state_id),
                  'group_set': mis_admin_grp._id})

            for each in university_cur:
                univ_ids.append(each._id)
            colg_cur = node_collection.find({'member_of': colg_gst._id,
                        'relation_set.college_affiliated_to': {'$in': univ_ids},
                        'group_set': mis_admin_grp._id})

        elif selected_filters == 2:
            if state_id == "ALL":
                state_id_list = []
                for each in state_cur:
                    state_id_list.append(each._id)
                if gst_node.name == "Student":
                    query.update({'relation_set.person_belongs_to_state': {'$in':state_id_list}})
                university_cur = node_collection.find({'member_of': univ_gst._id,
                      'relation_set.organization_belongs_to_state': {'$in':state_id_list},
                      'group_set': mis_admin_grp._id})
            else:
                if gst_node.name == "Student":
                    query.update({'relation_set.person_belongs_to_state': ObjectId(state_id)})

                university_cur = node_collection.find({'member_of': univ_gst._id,
                  'relation_set.organization_belongs_to_state': ObjectId(state_id),
                  'group_set': mis_admin_grp._id})

            if university_id == "ALL":
                univ_id_list = []
                for each in university_cur:
                    univ_id_list.append(each._id)
                if gst_node.name == "Student":
                    query.update({'relation_set.student_belongs_to_university': {'$in': univ_id_list}})
                colg_cur = node_collection.find({'member_of': colg_gst._id,
                  'relation_set.college_affiliated_to': {'$in': univ_id_list},
                  'group_set': mis_admin_grp._id})
            else:
                if gst_node.name == "Student":
                    query.update({'relation_set.student_belongs_to_university': ObjectId(university_id)})

                colg_cur = node_collection.find({'member_of': colg_gst._id,
                  'relation_set.college_affiliated_to': ObjectId(university_id),
                  'group_set': mis_admin_grp._id})

        elif selected_filters == 3:
            if state_id == "ALL":
                state_id_list = []
                for each in state_cur:
                    state_id_list.append(each._id)
                if gst_node.name == "Student":
                    query.update({'relation_set.person_belongs_to_state': {'$in': state_id_list}})
                university_cur = node_collection.find({
                      'member_of': univ_gst._id,
                      'relation_set.organization_belongs_to_state': {'$in': state_id_list},
                      'group_set': mis_admin_grp._id})
            else:
                if gst_node.name == "Student":
                    query.update({'relation_set.person_belongs_to_state': ObjectId(state_id)})

                university_cur = node_collection.find({'member_of': univ_gst._id,
                  'relation_set.organization_belongs_to_state': ObjectId(state_id),
                  'group_set': mis_admin_grp._id})

            if university_id == "ALL":
                univ_id_list = []
                for each in university_cur:
                    univ_id_list.append(each._id)
                # query.update({'relation_set.person_belongs_to_state': {'$in':state_id_list}})
                if gst_node.name == "Student":
                    query.update({'relation_set.student_belongs_to_university': {'$in': univ_id_list}})
                colg_cur = node_collection.find({'member_of': colg_gst._id,
                      'relation_set.college_affiliated_to': {'$in': univ_id_list},
                      'group_set': mis_admin_grp._id})
            else:
                # query.update({'relation_set.person_belongs_to_state': ObjectId(state_id)})
                if gst_node.name == "Student":
                    query.update({'relation_set.student_belongs_to_university': ObjectId(university_id)})

                colg_cur = node_collection.find({'member_of': colg_gst._id,
                  'relation_set.college_affiliated_to': ObjectId(university_id),
                  'group_set': mis_admin_grp._id})

            colg_id_list = []
            if college_node:
                colg_cur = node_collection.find({'_id': ObjectId(college_id)})
            for each in colg_cur:
                colg_id_list.append(each._id)
            colg_cur.rewind()
        # print "\n gst_name", gst_node.name
        vt_colg_ids = []
        if gst_node.name == "Voluntary Teacher":
            if colg_cur:
                for each in colg_cur:
                    list_of_colg_id = [each._id]
                    query.update({'relation_set.trainer_teaches_course_in_college': {"$elemMatch":{"$elemMatch":{"$in": list_of_colg_id}}}})
                    n = node_collection.find(query)
                    if n:
                        # for eachvt in n:
                        #     if eachvt.relation_set:
                        #         for rel in eachvt.relation_set:
                        #             if rel and 'trainer_teaches_course_in_college' in rel:
                        #                 old_dictcc = rel['trainer_teaches_course_in_college']
                        #                 for cc_dict in old_dictcc:
                        #                     for colg_course in cc_dict:
                        #                         n = node_collection.one({'_id': ObjectId(colg_course)})
                        #                         if 'College' in n.member_of_names_list:
                        #                             if n._id == each._id:
                        #                                 vt_colg_ids.append(each._id)
                        vt_colg_ids.append(each._id)
                    # del query['relation_set.trainer_teaches_course_in_college']
            if vt_colg_ids:
                colg_cur = node_collection.find({'_id': {'$in': vt_colg_ids}})
                del query['relation_set.trainer_teaches_course_in_college']
            else:
                colg_cur.rewind()

        if colg_cur:
            for each in colg_cur:
                if gst_node.name == "Student":
                    query.update({'relation_set.student_belongs_to_college': each._id})
                if gst_node.name == "Voluntary Teacher":
                    list_of_colg_id = [ObjectId(each._id)]
                    query.update({'relation_set.trainer_teaches_course_in_college': {"$elemMatch":{"$elemMatch":{"$in": list_of_colg_id}}}})

                if each.relation_set:
                    # print "\n\n each/relation_set",each.relation_set
                    for each_rel in each.relation_set:
                        if gst_node.name == "Classroom Session":
                            if each_rel and "has_group" in each_rel:
                                colg_group_node_id = each_rel["has_group"][0]
                                query.update({'group_set': ObjectId(colg_group_node_id)})
                        if each_rel and "college_affiliated_to" in each_rel:
                            univname = each_rel["college_affiliated_to"]
                        if each_rel and "organization_belongs_to_state" in each_rel:
                            statename = each_rel["organization_belongs_to_state"]
                        colgname = each._id

                # print "\n\nquery", query
                rec = node_collection.collection.aggregate([
                                          {
                                            '$match': query
                                          },
                                          {'$group':
                                            {
                                              '_id': {'State': statename,
                                              'University': univname,
                                              'College': each._id,
                                              },
                                              'total_students': {'$sum': 1}
                                            }
                                          }
                ])

                resultset = rec['result']
                # print "\n\n resultset", resultset
                if resultset:
                    for each in resultset:
                        each['query'] = str(query)
                        if each["_id"]:
                            if each['_id']['State']:
                                # each["state"] = each['_id']['State']
                                state_node = node_collection.one({'_id': ObjectId(each['_id']['State'][0])})
                                each["state"] = state_node.name
                            if each['_id']['University']:
                                univ_node = node_collection.one({'_id': ObjectId(each['_id']['University'][0])})
                                each["university"] = univ_node.name
                                # data_for_report1["university_id"] = str(univ_node._id)
                            if each['_id']['College']:
                                colg_node = node_collection.one({'_id': ObjectId(each['_id']['College'])})
                                each["college"] = colg_node.name
                                # data_for_report1["college_id"] = str(colg_node._id)
                            del each['_id']
                            try:
                                l = each['total_students']
                            except:
                                del each['total_students']

                        return_data_set.append(each)
                # print "\n return_data_set", return_data_set
            column_headers = [
                        ("state", "State"),
                        ("university", "University"),
                        ("college", "College"),
            ]

            if gst_node.name == "Student":
                column_headers.append(('total_students',"Total Students"))
            elif gst_node.name == "Classroom Session":
                column_headers.append(('total_students',"Total Events"))
            elif gst_node.name == "Voluntary Teacher":
                column_headers.append(('total_students',"Total VTs"))

            response_dict["column_headers"] = column_headers
            response_dict["success"] = True
            response_dict["return_data_set"] = return_data_set
            # response_dict["data_for_report1"] = json.dumps(data_for_report1)
        return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

    else:

        # Fetching all states belonging to given state in sorted order by name
        if state_cur.count():
            for d in state_cur:
                states.append([str(d._id), str(d.name)])

        return render_to_response("ndf/mis_report.html",
                                {'title': title,
                                'group_id': group_id,
                                'groupid': group_id,
                                'states_list': json.dumps(states)
                                },
                                context_instance=RequestContext(request)
                                )


