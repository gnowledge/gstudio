''' -- imports from python libraries -- '''
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django_mongokit import get_database
from django.contrib.auth.models import User

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import GSystemType, GSystem, Triple
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_existing_groups
from gnowsys_ndf.ndf.views.methods import *

#######################################################################################################################################

from django.contrib.auth.models import User
db = get_database()
gst_collection = db[GSystemType.collection_name]
collection_tr = db[Triple.collection_name]
gst_group = gst_collection.GSystemType.one({'name': GAPPS[2]})
gs_collection = db[GSystem.collection_name]
collection = db[Node.collection_name]

#######################################################################################################################################
#      V I E W S   D E F I N E D   F O R   G A P P -- ' G R O U P '
#######################################################################################################################################


def group(request, group_id,app_id):
    """Renders a list of all 'Group-type-GSystems' available within the database.
    """
    group_nodes = []
    excl_gr_nodes=[]
    col_Group = db[Group.collection_name]
    user_list=[]
    users=User.objects.all()
    for each in users:
        user_list.append(each.username)
    colg = col_Group.Group.find({'_type': u'Group'})
    colg.sort('name')
    gr = list(colg)
    for items in gr:
            group_nodes.append(items)
    group_nodes_count = len(group_nodes)
    colg = col_Group.Group.find({'$and':[{'_type': u'Group'},{'name':{'$nin':user_list}}]})
    colg.sort('name')
    gr = list(colg)
    for items in gr:
            excl_gr_nodes.append(items)
    return render_to_response("ndf/group.html", {'group_nodes': group_nodes, 'group_nodes_excluding_users':excl_gr_nodes,'group_nodes_count': group_nodes_count,'groupid': group_id,'group_id': group_id}, context_instance=RequestContext(request))
    



def create_group(request,group_id):
    if request.method == "POST":
        col_Group = db[Group.collection_name]
        colg = col_Group.Group()
        Mod_colg=col_Group.Group()

        cname=request.POST.get('groupname', "")
        colg.altnames=cname
        colg.name = unicode(cname)
        colg.member_of.append(gst_group._id)
        usrid = int(request.user.id)
        colg.created_by = usrid
        colg.modified_by = usrid
        
        if usrid not in colg.contributors:
            colg.contributors.append(usrid)

        colg.group_type = request.POST.get('group_type', "")        
        colg.edit_policy = request.POST.get('edit_policy', "")
        colg.subscription_policy = request.POST.get('subscription', "")
        colg.visibility_policy = request.POST.get('existance', "")
        colg.disclosure_policy = request.POST.get('member', "")
        colg.encryption_policy = request.POST.get('encryption', "")
        colg.save()
        
        if colg.edit_policy == "EDITABLE_MODERATED":
            Mod_colg.altnames = cname + "Mod" 
            Mod_colg.name = cname + "Mod"     
            Mod_colg.group_type = "PRIVATE"
            Mod_colg.created_by = usrid
            Mod_colg.modified_by = usrid
            if usrid not in Mod_colg.contributors:
                Mod_colg.contributors.append(usrid)
            Mod_colg.prior_node.append(colg._id)
            Mod_colg.save() 
            colg.post_node.append(Mod_colg._id)
            colg.save()

        auth = collection.Node.one({'_type': u'Group', 'name': unicode(request.user.username) }) 

        has_shelf_RT = collection.Node.one({'_type': 'RelationType', 'name': u'has_shelf' })
        dbref_has_shelf = has_shelf_RT.get_dbref()

        shelf = collection_tr.Triple.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': dbref_has_shelf })        
        shelves = []
        shelf_list = {}

        if shelf:
            for each in shelf:
                shelf_name = collection.Node.one({'_id': ObjectId(each.right_subject)})           
                shelves.append(shelf_name)

                shelf_list[shelf_name.name] = []         
                for ID in shelf_name.collection_set:
                    shelf_item = collection.Node.one({'_id': ObjectId(ID) })
                    shelf_list[shelf_name.name].append(shelf_item.name)
                    
        else:
            shelves = []

        return render_to_response("ndf/groupdashboard.html",{'groupobj':colg,'node':colg,'user':request.user,
                                                             'groupid':group_id,'group_id':group_id,
                                                             'shelf_list': shelf_list,'shelves': shelves
                                                            },context_instance=RequestContext(request))

    return render_to_response("ndf/create_group.html", {'groupid':group_id,'group_id':group_id},RequestContext(request))
    
# def home_dashboard(request):
#     try:
#         groupobj=gs_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
#     except Exception as e:
#         groupobj=""
#         pass
#     print "frhome--",groupobj
#     return render_to_response("ndf/groupdashboard.html",{'groupobj':groupobj,'user':request.user,'curgroup':groupobj},context_instance=RequestContext(request))



def group_dashboard(request,group_id=None):
    try:
        groupobj="" 
        grpid=""
        shelf_list = {}
        shelves = []

        if group_id == None:
            groupobj=gs_collection.Node.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
            grpid=groupobj['_id']
        else:
            groupobj=gs_collection.Group.one({'_id':ObjectId(group_id)})
            grpid=groupobj['_id']

        auth = collection.Node.one({'_type': u'Group', 'name': unicode(request.user.username) }) 

        has_shelf_RT = collection.Node.one({'_type': 'RelationType', 'name': u'has_shelf' })
        dbref_has_shelf = has_shelf_RT.get_dbref()

        shelf = collection_tr.Triple.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': dbref_has_shelf })        
        shelf_list = {}

        if shelf:
            for each in shelf:
                shelf_name = collection.Node.one({'_id': ObjectId(each.right_subject)})           
                shelves.append(shelf_name)

                shelf_list[shelf_name.name] = []         
                for ID in shelf_name.collection_set:
                    shelf_item = collection.Node.one({'_id': ObjectId(ID) })
                    shelf_list[shelf_name.name].append(shelf_item.name)
                    
        else:
            shelves = []


    except Exception as e:
        groupobj=gs_collection.Node.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
        grpid=groupobj['_id']
        pass

    
    groupobj,ver=get_page(request,groupobj)    
    # First time breadcrumbs_list created on click of page details
    breadcrumbs_list = []
    # Appends the elements in breadcrumbs_list first time the resource which is clicked
    breadcrumbs_list.append( (str(groupobj._id), groupobj.name) )

    return render_to_response("ndf/groupdashboard.html",{'node': groupobj, 'groupid':grpid, 
                                                         'group_id':grpid, 'user':request.user, 
                                                         'shelf_list': shelf_list,
                                                         'shelves': shelves, 
                                                         'breadcrumbs_list': breadcrumbs_list
                                                        },context_instance=RequestContext(request)
                            )

@login_required
def edit_group(request,group_id):
    page_node = gs_collection.GSystem.one({"_id": ObjectId(group_id)})
    if request.method == "POST":
            get_node_common_fields(request, page_node, group_id, gst_group)
            if page_node.access_policy == "PUBLIC":
                page_node.group_type = "PUBLIC"
            if page_node.access_policy == "PRIVATE":
                
                page_node.group_type = "PRIVATE"
            page_node.save()
            group_id=page_node._id
            return HttpResponseRedirect(reverse('groupchange', kwargs={'group_id':group_id}))
    page_node,ver=get_page(request,page_node)
    return render_to_response("ndf/edit_group.html",
                                      { 'node': page_node,
                                        'groupid':group_id,
                                        'group_id':group_id
                                        },
                                      context_instance=RequestContext(request)
                                      )


def switch_group(request,group_id,node_id):
    try:
        node=collection.Node.one({"_id":ObjectId(node_id)})
        exstng_grps=node.group_set
        if request.method == "POST":
            node.group_set=[]
            new_grps = request.POST['new_grps']
            new_grps_list=new_grps.split(",")
            if new_grps_list:
                for each in new_grps_list:
                    if each:
                        node.group_set.append(ObjectId(each));
                node.save()
            return HttpResponse("Success")
        else:
            coll_obj_list = []
            data_list=[]
            user_id=request.user.id
            st = collection.Node.find({'$and':[{'_type':'Group'},{'author_set':{'$in':[user_id]}}]})
            for each in node.group_set:
                coll_obj_list.append(collection.Node.one({'_id':each}))
            data_list=set_drawer_widget(st,coll_obj_list)
            return HttpResponse(json.dumps(data_list))
     
    except Exception as e:
        print "Exception in switch_group"+str(e)
        return HttpResponse("Failure")
def publish_group(request,group_id,node):
  node=collection.Node.one({'_id':ObjectId(node)})
   
  page_node,v=get_page(request,node)
  
  node.content = page_node.content
  node.content_org=page_node.content_org
  node.status=unicode("PUBLISHED")
  node.modified_by = int(request.user.id)
  node.save() 
 
  return render_to_response("ndf/groupdashboard.html",
                                 { 'group_id':group_id,
                                   'node':node,
                                   'groupid':group_id
                                   
                                
                                 
                                 
                                 },
                                  context_instance=RequestContext(request)
                              )

