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

    gst = node_collection.find({'_type':'GSystemType'})

    option_list=[]
    
    for e in gst :
        option_list.append(e.name)
        # opt_list.append(e)

    class_name="GSystemType"
    # select = "Exam"
    class_structure = eval(class_name).structure
    print class_structure


    gst = node_collection.find({'_type':'GSystemType'})
    gs = node_collection.find({'_type':'GSystem'})

    gs_sys = "GSystem"
    gs_struc =  eval(gs_sys).structure
    print "gs_sys\n",gs_struc,"\n\n\n"

    

# notes: fiind out wt is gs structure and how saving can be done apply save button to the form and call ndf tag to pass the url


    # gst_node

    basic_list = ['Name : ', 'Alternate Name : '];

    if node :
        print "LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL"
        st_name = node
        # print st_name
        node_gs = node_collection.one({'$and':[{'_type': u'GSystemType'},{'name':st_name}]})
        # print node_gs
        ats = node_gs.attribute_type_set
        # print ats
        rts = node_gs.relation_type_set
    else:
        st_name = "Exam"
        # print st_name
        node_gs = node_collection.one({'$and':[{'_type': u'GSystemType'},{'name':st_name}]})
        # print node_gs

        ats = node_gs.attribute_type_set

        rts = node_gs.relation_type_set



    print node,"\n\n\n\n\n\n\n"



    # gst_exam = node_collection.one({'_type': 'GSystemType', 'name':'Exam'})

















    template = "ndf/basic_temp.html"
    variable = RequestContext(request, {'group_id':group_id,'groupid':group_id ,'basic_list':basic_list, 'ats':ats , 'rts':rts , 'node_gs':node_gs  })

    return render_to_response(template,variable)