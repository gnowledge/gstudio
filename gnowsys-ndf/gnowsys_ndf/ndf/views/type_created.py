''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect,HttpResponse,StreamingHttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

from gnowsys_ndf.settings import GSYSTEM_LIST

from gnowsys_ndf.settings import *
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *

@login_required
def type_created(request,group_id):
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    opt_list = []
    gst = node_collection.find({'_type':'GSystemType'})
    group_name = 'home'
    for e in gst :
        op_demo = []
        op_demo = dict({'name':e.name, 'id':e._id })
        opt_list.append(op_demo)
    template = "ndf/type_created.html"
    variable = RequestContext(request, {'group_id':group_id,'groupid':group_id,'opt_list':opt_list, 'group_name_tag':group_name })
    return render_to_response(template,variable)

@login_required
def default_template(request,group_id,node=None,edit_node=None):
    
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    new_instance_type = None
    gs = node_collection.find({'_type':'GSystem'})
    gs_sys = "GSystem"
    gs_struc =  eval(gs_sys).structure
    # basic_list = { 'name':'Name' , 'altnames':'Alternate Name' }
    # basic_list = [{'name':'Name '} ,{'altnames':'Alternate Name '}]
    basic_list = GSYSTEM_LIST
    required_fields = eval(gs_sys).required_fields
    if node :
        st_id = node
        node_gs = node_collection.one({'_type': u'GSystemType','_id':ObjectId(st_id)})
        node_gs_id = node_gs._id
        ats = node_gs.attribute_type_set
        rts = node_gs.relation_type_set
                
        gsys_node = node_collection.collection.GSystem()
        if node_gs_id:
          gsys_node.member_of.append(node_gs_id)

        pos_ats = gsys_node.get_possible_attributes(node_gs_id)

        pos_rts = gsys_node.get_possible_relations(node_gs_id)

        # DONOT DELETE THIS CODE -------------------------
        # pos_rts_value = []
        # for key,value in pos_ats.iteritems():
            # pos_ats[key].update({'value':None})
        # for key,value in pos_rts.iteritems():
            # pos_rts_value = value['subject_or_object_type']
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
        pos_rts_temp_id = []

        for key,value in pos_rts.iteritems():
            pos_rts_temp_id.append(value['_id'])
        # Remove duplicity arising due to same subject and object type
        for e in pos_rts_temp_id:   
            if e not in pos_rts_id:
                pos_rts_id.append(e)
            
        final_pos_rts = []

        for e in pos_rts_id:
            if e not in rts_id:
                final_pos_rts.append(e)

        final_rts = []

        for e in final_pos_rts:
            fl_rts = node_collection.one({'_id':e})
            final_rts.append(fl_rts)

        # the final_rts list would have all the possible relationtype for the given GS.
        # the ones present in this list are not present in the RTs assosicated with the given GS

        f_rts_object_dict=[]
        rts_object_dict = []
        rts_obj= None
        rts_obj1= None
        rts_obj2= None
        k = None
        rts_name = None
        rts_alt = None
        rts_check = {}
        r_check = []
        rts_flag = False

        for e in rts:
            rts_name = e.name
            rts_alt = e.altnames
            rts_check_id = e._id
            r_oo = []
            rts_obj1 = e.object_type
            rts_obj2 = e.subject_type

            for each in rts_obj1:
                r_oo.append(each)
            for each in rts_obj2:
                r_oo.append(each)
            for each in r_oo:
                if each == node_gs_id:
                    r_oo.remove(each)
                    # rts_check = dict ({ 'rts_id' : rts_check_id })
                    # rts_flag = True
                    # r_check.append(rts_check)
            name_rst = []
            id_rst = []
            for each in r_oo:
                k = node_collection.one({'_id':ObjectId(each) })
                # name_rst.append(k.name) 
                # below code is to extract gs for each of them, the above would give gst
                id_rst.append(k._id)
            for v in id_rst:
                m = node_collection.find({'_type':'GSystem','member_of':ObjectId(v) })
                for c in m:
                    # print e.name
                    name_rst.append(c.name)

            rts_object_dict = dict({ 'name':rts_name, 'altnames':rts_alt, 'object_type':name_rst ,'rts_id' : rts_check_id  })
            f_rts_object_dict.append(rts_object_dict)

        # the code above returns a dict for the object display in template -- for rts

        f_pos_rts_object_dict=[]
        pos_rts_object_dict = []
        pos_rts_obj= None
        pos_rts_obj1= None
        pos_rts_obj2= None
        pos_k = None
        final_rts_name = None
        final_rts_alt = None
        rts_pos_check = {}
        r_pos_check = []
        rts_pos_flag = False

        for e in final_rts:
            final_rts_name = e.name
            final_rts_alt = e.altnames
            rts_check_pos_id = e._id
            pos_r = []
            pos_rts_obj1 = e.object_type
            pos_rts_obj2 = e.subject_type
            for e in pos_rts_obj1:
                pos_r.append(e)
            for e in pos_rts_obj2:
                pos_r.append(e)
            for each in pos_r:
                if each == node_gs_id:
                    rts_pos_check = dict ({ 'rts_id' : rts_check_pos_id })
                    rts_pos_flag = True
                    r_pos_check.append(rts_pos_check)
                    pos_r.remove(each)
            if rts_pos_flag:
                name_pos_rst = []
                id_pos_rst = []
                for each in pos_r:
                    k = node_collection.one({'_id':ObjectId(each) })
                    # name_pos_rst.append(k.name)
                    id_pos_rst.append(k._id)

                for v in id_pos_rst:
                    m = node_collection.find({'_type':'GSystem','member_of':ObjectId(v) })
                    for c in m:
                        name_pos_rst.append(c.name)
                
                pos_rts_object_dict = dict({'name':final_rts_name ,'altnames':final_rts_alt, 'object_type':name_pos_rst,'id':rts_check_pos_id })
                f_pos_rts_object_dict.append(pos_rts_object_dict)

        # the code above returns a dict for the object display in template -- for possible rts

    else:
        st_name = " "
        node_gs = node_collection.one({'$and':[{'_type': u'GSystemType'},{'name':st_name}]})
        ats = node_gs.attribute_type_set
        rts = node_gs.relation_type_set
        pos_ats = gsys_node.get_possible_attributes(node_gs_id)
        pos_rts = gsys_node.get_possible_relations(node_gs_id)

    # To check for duplicity in code, used to save below:
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

    if edit_node:
        new_instance_type = node_collection.one({'_type': u'GSystem' , '_id': ObjectId(edit_node)})
    else:
        new_instance_type = eval("node_collection.collection"+"."+gs_sys)()
    flag = False

    if request.method == "POST":
        # print request.POST
        flag = True
        for key,value in gs_struc.items():

            if key == "name":
                if request.POST.get(key,""):
                    # code below is to check whether the GSystem with same name exits or not, if it does further process would be aborted
                    key_name = unicode(request.POST.get(key,""))
                    search = node_collection.one({'_type':'GSystem','name':{'$regex': str(key_name), '$options': "i"},'member_of':ObjectId(node_gs_id) })
                    if search:
                        if not edit_node:
                            return StreamingHttpResponse(key_name+" already exits go back and use a different Name for the GSystem ")
                    else:
                        new_instance_type[key] = unicode(request.POST.get(key,""))

            if key == "altnames":
                if request.POST.get(key,""):
                    new_instance_type[key] = unicode(request.POST.get(key,""))

            if key == "attribute_set":
                ats_dict = []
                ats_dict2 =[]
                for e in key_ats:
                    print e ,"key"
                    if e in ("Location","location"):
                        for k in request.POST.get(e,"").split(","):
                            # print 'map-geojson-data'
                            qdict = request.POST
                            for lockey,locval in qdict.iteritems():
                                if lockey == 'map-geojson-data':
                                    ats_dict = dict({e:locval})
                                    ats_dict2.append(ats_dict)
                    else:
                        for k in request.POST.get(e,"").split(","):
                            # here e -- key name , k -- key value eg. e -- nussd_course_type, k -- General
                            ats_dict = dict({e:k})
                            ats_dict2.append(ats_dict)
                new_instance_type[key] = ats_dict2

            if key == "relation_set":
                rts_dict = []
                rts_dict2 = []
                for e in key_rts:
                    for k in request.POST.get(e,"").split(","):
                        # here e -- key name , k -- key value eg. e -- event_coordinator , k -- Person
                        rts_dict = dict({e:k})
                        rts_dict2.append(rts_dict)
                new_instance_type[key] = rts_dict2

        user_id = request.user.id
        if not new_instance_type.has_key('_id'):
            new_instance_type.created_by = user_id

        new_instance_type.modified_by = user_id
        new_instance_type.member_of.append(node_gs_id)

        if user_id not in new_instance_type.contributors:
            new_instance_type.contributors.append(user_id)

        new_instance_type.save()

        n_at = new_instance_type.attribute_set
        n_id = new_instance_type._id
        for e in n_at:
            for k,l in e.iteritems():
                gattr_create=None
                if l:
                    q = node_collection.one({'_type':'AttributeType','name':k})
                    try:
                        gattr_create=create_gattribute(new_instance_type._id,q,l)
                    except Exception as e:
                        print e

        n_rt = new_instance_type.relation_set
        n_rt_full = []
        for e in n_rt:
            for k,l in e.iteritems() :
                if l:
                    n_rt_full.append(e)

        for e in n_rt_full:
            for k,l in e.iteritems() :
                if l:
                    q1 = node_collection.one({'_type':'RelationType','name':k })
                    r1 = node_collection.one({'_type':'GSystem','name':l })
                    grel_create=None
                    if r1._id:
                        # print new_instance_type._id," \n", q1,"\n",  r1._id,">>>>from GRELATION\n\n\n\n\n\n\n"
                        try:
                            grel_create = create_grelation(new_instance_type._id,q1,r1._id)
                        except Exception as e :
                            print e 
                    # print grel_create , "GRELATION"
                    
        return HttpResponseRedirect("/admin/designer/GSystem")

    # If GET request ---------------------------------------------------------------------------------------
    for key,value in gs_struc.items():
        if key == "name":
            newdict[key] = ["unicode", new_instance_type[key]]

        if key == "altnames":
            newdict[key] = ["unicode", new_instance_type[key]]

        if key == "attribute_set":
            newdict[key] = ["dict", new_instance_type[key] ]

        if key == "relation_set":
            newdict[key] = ["dict", new_instance_type[key] ]

    gs_struc = newdict

    groupid = ""
    group_obj= node_collection.find({'$and':[{"_type":u'Group'},{"name":u'home'}]})
    if group_obj:
        groupid = str(group_obj[0]._id)
        group_name = group_obj[0].name

    template = "ndf/basic_temp.html"

    variable =  None
    class_structure_with_values = {}

    if edit_node:
        for key, value in gs_struc.items():
            class_structure_with_values[key] = [gs_struc[key][0], new_instance_type[key]]

        variable = RequestContext(request, {'group_id':group_id,'groupid':group_id ,'basic_list':basic_list,'required_fields': required_fields,
         'ats':ats , 'rts':rts , 'node_gs':node_gs , 'gs_struc':class_structure_with_values ,'final_ats':final_ats , 
         'f_rts_object_dict':f_rts_object_dict , 'f_pos_rts_object_dict':f_pos_rts_object_dict })

    else :
        variable = RequestContext(request, {'group_id':group_id,'groupid':group_id ,'basic_list':basic_list, 'required_fields': required_fields,
         'ats':ats , 'rts':rts , 'node_gs':node_gs , 'gs_struc':gs_struc ,'final_ats':final_ats , 
         'f_rts_object_dict':f_rts_object_dict , 'f_pos_rts_object_dict':f_pos_rts_object_dict })
            
    return render_to_response(template,variable)