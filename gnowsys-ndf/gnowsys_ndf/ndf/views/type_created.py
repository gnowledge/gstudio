''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect,HttpResponse,StreamingHttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

from gnowsys_ndf.settings import *
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *


def type_created(request,group_id):
    print "\n\n\n\n\n", "type_created" ,group_id , "\n\n\n\n\n\n\n\n"

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)


    option_list = []
    opt_list = []
    gst = node_collection.find({'_type':'GSystemType'})
    for e in gst :
        option_list.append(e.name)

    opt_list = node_collection.find({'_type':'GSystemType'})

    template = "ndf/type_created.html"
    variable = RequestContext(request, {'group_id':group_id,'groupid':group_id,'option_list':option_list,'opt_list':opt_list })

    return render_to_response(template,variable)












def default_template(request,group_id,node=None):

    # print "\n\n\n\n\n", "default_template","//////////////////",group_id , "\n\n\n\n\n\n\n\n"

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    gs = node_collection.find({'_type':'GSystem'})

    option_list=[]
    
    for e in gs :
        option_list.append(e.name)
        # opt_list.append(e)

    # class_name="GSystemType"
    # select = "Exam"
    # class_structure = eval(class_name).structure
    # print class_structure
    # gst = node_collection.find({'_type':'GSystemType'})

# notes: find out wt is gs structure and how saving can be done apply save button to the form and call ndf tag to pass the url

    new_instance_type = None

    gs = node_collection.find({'_type':'GSystem'})

    gs_sys2 = "GSystemType"
    class_structure =  eval(gs_sys2).structure
    print "gst\n", class_structure, "\n\n"
    
    gs_sys = "GSystem"
    gs_struc =  eval(gs_sys).structure
    print "gs_sys\n", gs_struc, "\n\n\n"
    
# For Display

    basic_list = ['name', 'altnames']

    if node :
        print "LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL"
        st_name = node
        # print st_name
        node_gs = node_collection.one({'$and':[{'_type': u'GSystemType'},{'name':st_name}]})
        # print node_gs

        node_gs_id = node_gs._id
        # print node_gs_id

        ats = node_gs.attribute_type_set
        # for e in ats:
            # print e._type,e.name,e.data_type,"\n\n"


        rts = node_gs.relation_type_set
        # for e in rts:
            # print e,"\n\n"
        
        # print rts



        # user_id = 1

        node = node_collection.find_one({'$and':[{'_type': u'GSystem'},{'name':st_name}]})
        
        gsys_node = node_collection.collection.GSystem()
        
        gsys_node.name = unicode(st_name)
        # print gsys_node.name        

        # gsys_node.created_by = user_id
        # gsys_node.modified_by = user_id
        # if user_id not in gsys_node.contributors:
          # gsys_node.contributors.append(user_id)

        # gs_city = node_collection.one({'_type':'GSystemType','name':'City'})
        # if gs_city:
          # gs_type_id = gs_city._id

        # if gs_type_id:
          # gsys_node.member_of.append(gs_type_id)
        
        if node_gs_id:
          gsys_node.member_of.append(node_gs_id)

        # if user_id not in gsys_node.contributors:
          # gsys_node.contributors.append(user_id)


        # gsys_node.save()

        # print gsys_node.member_of

        # gsys_node = node_collection.collection.GSystem()
        # gsys_node.name = unicode(st_name)

        pos_ats = gsys_node.get_possible_attributes(node_gs_id)

        # print pos_ats

        pos_rts = gsys_node.get_possible_relations(node_gs_id)

        # print pos_rts

        # DONOT DELETE THIS CODE -------------------------
        for key,value in pos_ats.iteritems():
            pos_ats[key].update({'value':None})

            print key ,"\n", pos_ats[key] , "\n\n\n"
            # print value['altnames'],value['_id']
        # for key,value in pos_rts.iteritems():
            # print value['altnames'],value['_id']
        # --------------------------------------------------






        # pos_ats = node.get_possible_attributes(node_gs._id)
        # print pos_ats , "??////////////////???/ \n\n\n\n"
        
    else:
        st_name = " "
        node_gs = node_collection.one({'$and':[{'_type': u'GSystemType'},{'name':st_name}]})
        ats = node_gs.attribute_type_set
        rts = node_gs.relation_type_set
        pos_ats = gsys_node.get_possible_attributes(node_gs_id)
        pos_rts = gsys_node.get_possible_relations(node_gs_id)



    print "\n\n\n\n\n\n\n"




    newdict = {}

    # if node_id:
    #     new_instance_type = node_collection.one({'_type': unicode(gs_sys), '_id': ObjectId(node_id)})
    # else:

    new_instance_type = eval("node_collection.collection"+"."+gs_sys)()



    # if request.method=="POST":
        # for key,value in class_structure.items():



    # If GET request ---------------------------------------------------------------------------------------
    # for key,value in class_structure.items():

            # newdict[key] = [value, new_instance_type[key]]

    # class_structure = newdict


























    template = "ndf/basic_temp.html"
    variable = RequestContext(request, {'group_id':group_id,'groupid':group_id ,'basic_list':basic_list, 'ats':ats , 'rts':rts , 'node_gs':node_gs ,'pos_ats':pos_ats , 'pos_rts':pos_rts ,'gs_struc':gs_struc  })

    return render_to_response(template,variable)