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

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    new_instance_type = None

    gs = node_collection.find({'_type':'GSystem'})

    gs_sys2 = "GSystemType"
    class_structure =  eval(gs_sys2).structure
    # print "gst\n", class_structure, "\n\n"
    
    gs_sys = "GSystem"
    gs_struc =  eval(gs_sys).structure
    # print "gs_sys\n", gs_struc, "\n\n\n"
    
    # For Display
    # basic_list = ['name', 'altnames']
    basic_list = { 'name':'Name' , 'altnames':'Alternate Name' }

    if node :
        # print "LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL"
        st_name = node

        node_gs = node_collection.one({'$and':[{'_type': u'GSystemType'},{'name':st_name}]})

        node_gs_id = node_gs._id
        # print node_gs_id

        ats = node_gs.attribute_type_set
        
        rts = node_gs.relation_type_set
        
        gsys_node = node_collection.collection.GSystem()
        
        # gsys_node.name = unicode(st_name)
        # print gsys_node.name        
        
        if node_gs_id:
          gsys_node.member_of.append(node_gs_id)
        # print gsys_node.member_of,">>>member_of>>"

        pos_ats = gsys_node.get_possible_attributes(node_gs_id)

        pos_rts = gsys_node.get_possible_relations(node_gs_id)

        # DONOT DELETE THIS CODE -------------------------
        # pos_rts_value = []
        # for key,value in pos_ats.iteritems():
            # pos_ats[key].update({'value':None})

            # print key ,"\n", pos_ats[key] , "\n\n\n"
            # print value['altnames'],value['_id']
        # for key,value in pos_rts.iteritems():
            # print key ,"\n"
            # print value,"\n\n"

        # for key,value in pos_rts.iteritems():
            # pos_rts_value = value['subject_or_object_type']
            # print pos_rts_value
            # this has all the rightside gst of the relationtype

            # subject_or_object_type': [ObjectId('564c7451a78dd024cb05b7dd')
        # the below code is to get the union or intersection of the items 
        # ats_set = set(ats)
        # pos_ats_set = set(pos_ats)
        # print ats_set.intersection(pos_ats_set)
        # print ats_set.union(pos_ats_set)    


        # --------------------------------------------------
        # code to remove the extra fields from the possible values.

        # For AT
        ats_id = []

        for e in ats:
            ats_id.append(e._id)

        pos_ats_id = []

        for key,value in pos_ats.iteritems():
            pos_ats_id.append(value['_id'])

        final_pos_ats = []

        for e in pos_ats_id:
            if e not in ats_id:
                final_pos_ats.append(e)

        final_ats = []

        for e in final_pos_ats:
            fl_ats = node_collection.one({'_id':e})
            final_ats.append(fl_ats)

        # For RT 
        rts_id = []

        for e in rts:
            rts_id.append(e._id)

        pos_rts_id = []

        for key,value in pos_rts.iteritems():
            pos_rts_id.append(value['_id'])

        final_pos_rts = []

        for e in pos_rts_id:
            if e not in rts_id:
                final_pos_rts.append(e)

        final_rts = []

        for e in final_pos_rts:
            fl_rts = node_collection.one({'_id':e})
            final_rts.append(fl_rts)

        # the final_rts list would have all the possible relationtype for the given GS.
        # the ones preent in this list are not present in the RTs assosicated with the given GS

        f_rts_object_dict=[]
        rts_object_dict = []
        rts_obj= None
        k = None
        for e in rts:
            rts_obj = e.object_type
            name_rst = []
            id_rst = []
            for each in rts_obj:
                k = node_collection.one({'_id':ObjectId(each) })
                name_rst.append(k.name) 
                # below code is to extract gs for each of them, the above would give gst
                # id_rst.append(k._id)

                # for v in id_rst:
                #     m = node_collection.find({'_type':'GSystem','member_of':ObjectId(v) })
                #     for c in m:
                #         # print e.name
                #         name_rst.append(c.name)
            rts_object_dict = dict({ 'name':e.name, 'altnames':e.altnames, 'object_type':name_rst })
            f_rts_object_dict.append(rts_object_dict)
        # the code above returns a dict for the object display in template -- for rts


        f_pos_rts_object_dict=[]
        pos_rts_object_dict = []
        pos_rts_obj= None
        pos_k = None
        for e in final_rts:
            pos_rts_obj = e.object_type
            name_pos_rst = []
            id_pos_rst = []
            for each in pos_rts_obj:
                k = node_collection.one({'_id':ObjectId(each) })
                # print k.name,k._id        
                # name_pos_rst.append(k.name)
                id_pos_rst.append(k._id)

                for v in id_pos_rst:
                    m = node_collection.find({'_type':'GSystem','member_of':ObjectId(v) })
                    for c in m:
                        # print e.name
                        name_pos_rst.append(c.name)


            pos_rts_object_dict = dict({'name':e.name ,'altnames':e.altnames, 'object_type':name_pos_rst})
            f_pos_rts_object_dict.append(pos_rts_object_dict)
        # the code above returns a dict for the object display in template -- for possible rts

    else:
        st_name = " "
        node_gs = node_collection.one({'$and':[{'_type': u'GSystemType'},{'name':st_name}]})
        ats = node_gs.attribute_type_set
        rts = node_gs.relation_type_set
        pos_ats = gsys_node.get_possible_attributes(node_gs_id)
        pos_rts = gsys_node.get_possible_relations(node_gs_id)


    key_ats = []
    for e in ats:
        key_ats.append(e.name)

    for e in final_ats:
        key_ats.append(e.name)

    key_rts = []
    for e in rts:
        key_rts.append(e.name)

    for e in final_rts:
        key_rts.append(e.name)


    newdict = {}

    # if node_id:
    #     new_instance_type = node_collection.one({'_type': unicode(gs_sys), '_id': ObjectId(node_id)})
    # else:

    new_instance_type = eval("node_collection.collection"+"."+gs_sys)()

    if request.method == "POST":
        # print request.POST
        for key,value in gs_struc.items():
            # print key , value,"\n"

            if key == "name":
                # print "name"
                if request.POST.get(key,""):
                    new_instance_type[key] = unicode(request.POST.get(key,""))

            if key == "altnames":
                # print "altnames"
                if request.POST.get(key,""):
                    new_instance_type[key] = unicode(request.POST.get(key,""))

            if key == "attribute_set":
                # print "this attribute_set "
                ats_dict = []
                ats_dict2 =[]
                for e in key_ats:
                    # print e
                    for k in request.POST.get(e,"").split(","):
                        # print e,k ,"\n"
                        # here e -- key name , k -- key value eg. e -- nussd_course_type, k -- General
                        ats_dict = dict({e:k})
                        ats_dict2.append(ats_dict)
                    
                # print ats_dict2
                new_instance_type[key] = ats_dict2

            if key == "relation_set":
                # print "this relation_set "
                rts_dict = []
                rts_dict2 = []
                for e in key_rts:
                    for k in request.POST.get(e,"").split(","):
                        # print e,k ,"\n"
                        # here e -- key name , k -- key value eg. e -- event_coordinator , k -- Person
                        rts_dict = dict({e:k})
                        rts_dict2.append(rts_dict)

                # print rts_dict2
                new_instance_type[key] = rts_dict2


        # print request.user.id , ">>>>>>>>>>>>>>>>>>>" 

        user_id = request.user.id
        if not new_instance_type.has_key('_id'):
            new_instance_type.created_by = user_id

        new_instance_type.modified_by = user_id
        new_instance_type.member_of.append(node_gs_id)

        if user_id not in new_instance_type.contributors:
            new_instance_type.contributors.append(user_id)

        new_instance_type.save()

        # print new_instance_type
    # If GET request ---------------------------------------------------------------------------------------
    # for key,value in class_structure.items():

            # newdict[key] = [value, new_instance_type[key]]

    # class_structure = newdict


    template = "ndf/basic_temp.html"
    variable = RequestContext(request, {'group_id':group_id,'groupid':group_id ,'basic_list':basic_list,
     'ats':ats , 'rts':rts , 'node_gs':node_gs , 'gs_struc':gs_struc ,'final_ats':final_ats , 
     'f_rts_object_dict':f_rts_object_dict , 'f_pos_rts_object_dict':f_pos_rts_object_dict })

    return render_to_response(template,variable)