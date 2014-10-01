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
import json

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import GSystemType, GSystem, Triple
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_existing_groups,get_all_user_groups
from gnowsys_ndf.ndf.views.methods import *


#######################################################################################################################################

from django.contrib.auth.models import User
db = get_database()
gst_collection = db[GSystemType.collection_name]
collection_tr = db[Triple.collection_name]
gst_group = gst_collection.GSystemType.one({'name': GAPPS[2]})
gs_collection = db[GSystem.collection_name]
collection = db[Node.collection_name]
get_all_usergroups=get_all_user_groups()
at_apps_list=collection.Node.one({'$and':[{'_type':'AttributeType'},{'name':'apps_list'}]})
ins_objectid  = ObjectId()
app=collection.Node.one({'name':u'Group','_type':'GSystemType'})



#######################################################################################################################################
#      V I E W S   D E F I N E D   F O R   G A P P -- ' G R O U P '
#######################################################################################################################################


def group(request, group_id, app_id=None):
  """Renders a list of all 'Group-type-GSystems' available within the database.
  """
  ins_objectid  = ObjectId()
  if ins_objectid.is_valid(group_id) is False :
    group_ins = collection.Node.find_one({'_type': "Group","name": group_id}) 
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) }) 
    if group_ins:
      group_id = str(group_ins._id)
    else :
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if auth :
        group_id = str(auth._id)	
  else :
  	pass

  group_nodes = []
  group_count = 0
  auth = collection.Node.one({'_type': u"Author", 'name': unicode(request.user.username)})

  if request.method == "POST":
    #Page search view
    title = gst_group.name
    
    search_field = request.POST['search_field']

    if auth:
      # Logged-In View
      cur_groups_user = collection.Node.find({'_type': "Group", 
                                       '_id': {'$nin': [ObjectId(group_id), auth._id]},
                                       '$or': [
                                          {'$and': [
                                            {'name': {'$regex': search_field, '$options': 'i'}},
                                            {'$or': [
                                              {'created_by': request.user.id}, 
                                              {'group_admin': request.user.id},
                                              {'author_set': request.user.id},
                                              {'group_type': 'PUBLIC'} 
                                              ]
                                            }                                  
                                          ]
                                          },
                                          {'$and': [
                                            {'tags': {'$regex':search_field, '$options': 'i'}},
                                            {'$or': [
                                              {'created_by': request.user.id}, 
                                              {'group_admin': request.user.id},
                                              {'author_set': request.user.id},
                                              {'group_type': 'PUBLIC'} 
                                              ]
                                            }                                  
                                          ]
                                          }, 
                                        ],
                                        'name': {'$nin': ["home"]},
                                   }).sort('last_update', -1)

      if cur_groups_user.count():
        for group in cur_groups_user:
          group_nodes.append(group)

      group_count = cur_groups_user.count()
        
    else:
      # Without Log-In View
      cur_public = collection.Node.find({'_type': "Group", 
                                       '_id': {'$nin': [ObjectId(group_id)]},
                                       '$or': [
                                          {'name': {'$regex': search_field, '$options': 'i'}}, 
                                          {'tags': {'$regex':search_field, '$options': 'i'}}
                                        ],
                                        'name': {'$nin': ["home"]},
                                        'group_type': "PUBLIC"
                                   }).sort('last_update', -1)
  
      if cur_public.count():
        for group in cur_public:
          group_nodes.append(group)
      
      group_count = cur_public.count()

    return render_to_response("ndf/group.html",
                              {'title': title,
                               'appId':app._id,
                               'searching': True, 'query': search_field,
                               'group_nodes': group_nodes, 'group_nodes_count': group_count,
                               'groupid':group_id, 'group_id':group_id
                              }, 
                              context_instance=RequestContext(request)
    )

  else:
    if auth:
      # Logged-In View
      cur_groups_user = collection.Node.find({'_type': "Group", 
                                              '_id': {'$nin': [ObjectId(group_id), auth._id]},
                                              'name': {'$nin': ["home"]},
                                              '$or': [{'created_by': request.user.id}, {'author_set': request.user.id}, {'group_admin': request.user.id}, {'group_type': 'PUBLIC'}]
                                          }).sort('last_update', -1)
      if cur_groups_user.count():
        for group in cur_groups_user:
          group_nodes.append(group)

      group_count = cur_groups_user.count()
        
    else:
      # Without Log-In View
      cur_public = collection.Node.find({'_type': "Group", 
                                         '_id': {'$nin': [ObjectId(group_id)]},
                                         'name': {'$nin': ["home"]},
                                         'group_type': "PUBLIC"
                                     }).sort('last_update', -1)
  
      if cur_public.count():
        for group in cur_public:
          group_nodes.append(group)
      
      group_count = cur_public.count()

    
    return render_to_response("ndf/group.html", 
                              {'group_nodes': group_nodes,
                               'appId':app._id,
                               'group_nodes_count': group_count,
                               'groupid': group_id, 'group_id': group_id
                              }, context_instance=RequestContext(request))


def create_group(request,group_id):
  ins_objectid  = ObjectId()
  if ins_objectid.is_valid(group_id) is False :
    group_ins = collection.Node.find_one({'_type': "Group","name": group_id}) 
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) }) 
    if group_ins:
      group_id = str(group_ins._id)
    else :
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if auth :
        group_id = str(auth._id)	
  else :
  	pass

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
    if usrid not in colg.author_set:
      colg.author_set.append(usrid)

    colg.modified_by = usrid
    if usrid not in colg.contributors:
      colg.contributors.append(usrid)

    colg.group_type = request.POST.get('group_type', "")        
    colg.edit_policy = request.POST.get('edit_policy', "")
    colg.subscription_policy = request.POST.get('subscription', "")
    colg.visibility_policy = request.POST.get('existance', 'ANNOUNCED')
    colg.disclosure_policy = request.POST.get('member', 'DISCLOSED_TO_MEM')
    colg.encryption_policy = request.POST.get('encryption', 'NOT_ENCRYPTED')
    colg.agency_type=request.POST.get('agency_type',"")
    colg.save()
    
    if colg.edit_policy == "EDITABLE_MODERATED":
      Mod_colg.altnames = cname + "Mod" 
      Mod_colg.name = cname + "Mod"     
      Mod_colg.group_type = "PRIVATE"

      Mod_colg.created_by = usrid
      if usrid not in Mod_colg.author_set:
        Mod_colg.author_set.append(usrid)

      Mod_colg.modified_by = usrid
      if usrid not in Mod_colg.contributors:
        Mod_colg.contributors.append(usrid)

      Mod_colg.prior_node.append(colg._id)
      Mod_colg.save() 

      colg.post_node.append(Mod_colg._id)
      colg.save()

    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) }) 

    has_shelf_RT = collection.Node.one({'_type': 'RelationType', 'name': u'has_shelf' })
    dbref_has_shelf = has_shelf_RT.get_dbref()

    shelves = []
    shelf_list = {}
    
    if auth:
      shelf = collection_tr.Triple.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': dbref_has_shelf })        

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

    return render_to_response("ndf/groupdashboard.html",{'groupobj':colg,'appId':app._id,'node':colg,'user':request.user,
                                                         'groupid':group_id,'group_id':group_id,
                                                         'shelf_list': shelf_list,'shelves': shelves
                                                        },context_instance=RequestContext(request))


  available_nodes = collection.Node.find({'_type': u'Group', 'member_of': ObjectId(gst_group._id) })

  nodes_list = []
  for each in available_nodes:
    nodes_list.append(each.name)

  return render_to_response("ndf/create_group.html", {'groupid':group_id,'appId':app._id,'group_id':group_id,'nodes_list': nodes_list},RequestContext(request))
    
# def home_dashboard(request):
#     try:
#         groupobj=gs_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
#     except Exception as e:
#         groupobj=""
#         pass
#     print "frhome--",groupobj
#     return render_to_response("ndf/groupdashboard.html",{'groupobj':groupobj,'user':request.user,'curgroup':groupobj},context_instance=RequestContext(request))


def populate_list_of_members():
	members = User.objects.all()
	memList = []
	for mem in members:
		memList.append(mem.username)	
	return memList

def populate_list_of_group_members(group_id):
    col = get_database()[Node.collection_name]
    try :
      try:
        author_list = col.Node.one({"_type":"Group", "_id":ObjectId(group_id)}, {"author_set":1, "_id":0})
      except:
        author_list = col.Node.find_one({"_type":"Group", "name":group_id}, {"author_set":1, "_id":0})
      
      memList = []

      for author in author_list.author_set:
          name_author = User.objects.get(pk=author)
          memList.append(name_author)
      
      print "members in group: ", memList
      return memList
    except:
        return []

def group_dashboard(request,group_id=None):

  if ins_objectid.is_valid(group_id) is False :
    group_ins = collection.Node.find_one({'_type': "Group","name": group_id}) 
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
    if group_ins:
	    group_id = str(group_ins._id)
    else :
	    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
	    if auth :
	    	group_id = str(auth._id)	
  else :
  	pass

  try:
    groupobj="" 
    grpid=""
    shelf_list = {}
    shelves = []
    alternate_template = ""

    if group_id == None:
      groupobj=gs_collection.Node.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
      grpid=groupobj['_id']
    else:
      groupobj=gs_collection.Group.one({'_id':ObjectId(group_id)})
      grpid=groupobj['_id']

    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) }) 

    if auth:
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

  # Call to get_neighbourhood() is required for setting-up property_order_list
  groupobj.get_neighbourhood(groupobj.member_of)

  property_order_list = []
  if groupobj.has_key("group_of"):
    if groupobj['group_of']:
      college = collection.Node.one({'_type': "GSystemType", 'name': "College"}, {'_id': 1})

      if college:
        if college._id in groupobj['group_of'][0]['member_of']:
          alternate_template = "ndf/college_group_details.html"

      property_order_list = get_property_order_with_value(groupobj['group_of'][0])

  # First time breadcrumbs_list created on click of page details
  breadcrumbs_list = []
  # Appends the elements in breadcrumbs_list first time the resource which is clicked
  breadcrumbs_list.append( (str(groupobj._id), groupobj.name) )
  annotations = json.dumps(groupobj.annotations)

  default_template = "ndf/groupdashboard.html"
  return render_to_response([alternate_template, default_template] ,{'node': groupobj, 'groupid':grpid, 
                                                       'group_id':grpid, 'user':request.user, 
                                                       'shelf_list': shelf_list,
                                                       'appId':app._id,
                                                       'annotations' : annotations,
                                                       'shelves': shelves, 
                                                       'breadcrumbs_list': breadcrumbs_list
                                                      },context_instance=RequestContext(request)
                          )


@login_required
def edit_group(request,group_id):
  ins_objectid  = ObjectId()
  if ins_objectid.is_valid(group_id) is False :
    group_ins = collection.Node.find_one({'_type': "Group","name": group_id}) 
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
    if group_ins:
      group_id = str(group_ins._id)
    else:
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if auth :
        group_id = str(auth._id)

  else:
    pass

  page_node = gs_collection.GSystem.one({"_id": ObjectId(group_id)})
  if request.method == "POST":
    is_node_changed=get_node_common_fields(request, page_node, group_id, gst_group)
    
    if page_node.access_policy == "PUBLIC":
      page_node.group_type = "PUBLIC"

    if page_node.access_policy == "PRIVATE":
      page_node.group_type = "PRIVATE"
    page_node.save(is_changed=is_node_changed)
    page_node.save()
    group_id=page_node._id
    page_node.get_neighbourhood(page_node.member_of)
    return HttpResponseRedirect(reverse('groupchange', kwargs={'group_id':group_id}))

  else:
    if page_node.status == u"DRAFT":
      page_node, ver = get_page(request, page_node)
      page_node.get_neighbourhood(page_node.member_of) 
  return render_to_response("ndf/edit_group.html",
                                    { 'node': page_node,
                                      'appId':app._id,
                                      'groupid':group_id,
                                      'group_id':group_id
                                      },
                                    context_instance=RequestContext(request)
                                    )

def app_selection(request,group_id):
  ins_objectid  = ObjectId()
  if ins_objectid.is_valid(group_id) is False :
    group_ins = collection.Node.find_one({'_type': "Group","name": group_id}) 
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) }) 
    if group_ins:
      group_id = str(group_ins._id)
    else :
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if auth :
      	group_id = str(auth._id)	
  else :
  	pass

  try:
    grp=collection.Node.one({"_id":ObjectId(group_id)})
    if request.method == "POST":
      lst=[]
      apps_to_set = request.POST['apps_to_set']
      apps_list=apps_to_set.split(",")
      if apps_list:
        for each in apps_list:
          if each:
            obj=collection.Node.one({'_id':ObjectId(each)})
            lst.append(obj);
        gattribute=collection.Node.one({'$and':[{'_type':'GAttribute'},{'attribute_type.$id':at_apps_list._id},{'subject':grp._id}]})
        if gattribute:
          gattribute.delete()
        if lst:
          create_attribute=collection.GAttribute()
          create_attribute.attribute_type=at_apps_list
          create_attribute.subject=grp._id
          create_attribute.object_value=lst
          create_attribute.save()            
      return HttpResponse("Success")

    else:
      list_apps=[]

      if not at_apps_list:
        return HttpResponse("Failure")
      poss_atts=grp.get_possible_attributes(at_apps_list._id)

      if poss_atts:
        list_apps=poss_atts['apps_list']['object_value']
      st = get_all_gapps()
      # print "inapp_list view",st,list_apps
      data_list=set_drawer_widget(st,list_apps)
      return HttpResponse(json.dumps(data_list))

  except Exception as e:
    print "Error in app_selection "+str(e)
     

def switch_group(request,group_id,node_id):
  ins_objectid  = ObjectId()
  if ins_objectid.is_valid(group_id) is False :
    group_ins = collection.Node.find_one({'_type': "Group","name": group_id}) 
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) }) 
    if group_ins:
      group_id = str(group_ins._id)
    else :
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if auth :
      	group_id = str(auth._id)	
  else :
  	pass

  try:
    node=collection.Node.one({"_id":ObjectId(node_id)})
    exstng_grps=node.group_set
    if request.method == "POST":     
      node.group_set=[] # Remove all existing groups and add new ones 
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
      all_user_groups=[]
      for each in get_all_user_groups():
        all_user_groups.append(each.name)
      st = collection.Node.find({'$and':[{'_type':'Group'},{'author_set':{'$in':[user_id]}},{'name':{'$nin':all_user_groups}}]})
      for each in node.group_set:
        coll_obj_list.append(collection.Node.one({'_id':each}))
      data_list=set_drawer_widget(st,coll_obj_list)
      return HttpResponse(json.dumps(data_list))
   
  except Exception as e:
    print "Exception in switch_group"+str(e)
    return HttpResponse("Failure")


def publish_group(request,group_id,node):
  ins_objectid  = ObjectId()
  if ins_objectid.is_valid(group_id) is False :
    group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
    if group_ins:
	    group_id = str(group_ins._id)
    else:
	    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
	    if auth :
	    	group_id = str(auth._id)	
  else :
  	pass

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
                                   'appId':app._id,
                                   'groupid':group_id
                                 },
                                  context_instance=RequestContext(request)
                              )


def create_sub_group(request,group_id):
  try:
      ins_objectid  = ObjectId()
      grpname=""
      if ins_objectid.is_valid(group_id) is False :
          group_ins = collection.Node.find_one({'_type': "Group","name": group_id}) 
          auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
          if group_ins:
              grpname=group_ins.name 
              group_id = str(group_ins._id)
          else :
              auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
              if auth :
                  group_id = str(auth._id)
                  grpname=auth.name	
      else :
          group_ins = collection.Node.find_one({'_type': "Group","_id": ObjectId(group_id)})
          if group_ins:
              grpname=group_ins.name
              pass
          else:
              group_ins = collection.Node.find_one({'_type': "Author","_id": ObjectId(group_id)})
              if group_ins:
                  grpname=group_ins.name
                  pass

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
          if usrid not in colg.author_set:
              colg.author_set.append(usrid)
          colg.modified_by = usrid
          if usrid not in colg.contributors:
              colg.contributors.append(usrid)
          colg.group_type = request.POST.get('group_type', "")        
          colg.edit_policy = request.POST.get('edit_policy', "")
          colg.subscription_policy = request.POST.get('subscription', "")
          colg.visibility_policy = request.POST.get('existance', "ANNOUNCED")
          colg.disclosure_policy = request.POST.get('member', "DISCLOSED_TO_MEM")
          colg.encryption_policy = request.POST.get('encryption', "NOT_ENCRYPTED")
          colg.agency_type=request.POST.get('agency_type',"")
          if group_id:
              colg.prior_node.append(group_ins._id)
          colg.save()
          #save subgroup_id in post_node of parent group 
          group_ins.post_node.append(colg._id)
          group_ins.save()
    
          if colg.edit_policy == "EDITABLE_MODERATED":
              Mod_colg.altnames = cname + "Mod" 
              Mod_colg.name = cname + "Mod"     
              Mod_colg.group_type = "PRIVATE"
              Mod_colg.created_by = usrid
              if usrid not in Mod_colg.author_set:
                  Mod_colg.author_set.append(usrid)
              Mod_colg.modified_by = usrid
              if usrid not in Mod_colg.contributors:
                  Mod_colg.contributors.append(usrid)
              Mod_colg.prior_node.append(colg._id)
              Mod_colg.save() 

              colg.post_node.append(Mod_colg._id)
              colg.save()
          auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) }) 
          has_shelf_RT = collection.Node.one({'_type': 'RelationType', 'name': u'has_shelf' })
          dbref_has_shelf = has_shelf_RT.get_dbref()
          shelves = []
          shelf_list = {}
    
          if auth:
              shelf = collection_tr.Triple.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': dbref_has_shelf })        

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

          return render_to_response("ndf/groupdashboard.html",{'groupobj':colg,'appId':app._id,'node':colg,'user':request.user,
                                                         'groupid':group_id,'group_id':group_id,
                                                         'shelf_list': shelf_list,'shelves': shelves
                                                        },context_instance=RequestContext(request))
      available_nodes = collection.Node.find({'_type': u'Group', 'member_of': ObjectId(gst_group._id) })
      nodes_list = []
      for each in available_nodes:
          nodes_list.append(each.name)
      return render_to_response("ndf/create_sub_group.html", {'groupid':group_id,'maingroup':grpname,'group_id':group_id,'nodes_list': nodes_list},RequestContext(request))
  except Exception as e:
      print "Exception in create subgroup "+str(e)
