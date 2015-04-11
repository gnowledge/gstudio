''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
# from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, GROUP_AGENCY_TYPES, GSTUDIO_NROER_MENU, GSTUDIO_NROER_MENU_MAPPINGS

# from gnowsys_ndf.ndf.models import GSystemType, GSystem, Group, Triple
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_all_user_groups  # get_existing_groups
from gnowsys_ndf.ndf.views.methods import *

# ######################################################################################################################################

gst_group = node_collection.one({"_type": "GSystemType", 'name': GAPPS[2]})
app = gst_group

# ######################################################################################################################################
#      V I E W S   D E F I N E D   F O R   G A P P -- ' G R O U P '
# ######################################################################################################################################


@get_execution_time
def group(request, group_id, app_id=None, agency_type=None):
  """Renders a list of all 'Group-type-GSystems' available within the database.
  """

  group_name, group_id = get_group_name_id(group_id)

  query_dict = {}
  if (app_id == "agency_type") and (agency_type in GROUP_AGENCY_TYPES):
    query_dict["agency_type"] = agency_type
  # print "=========", app_id, agency_type

  group_nodes = []
  group_count = 0
  auth = node_collection.one({'_type': u"Author", 'name': unicode(request.user.username)})

  if request.method == "POST":
    # Page search view
    title = gst_group.name
    
    search_field = request.POST['search_field']

    if auth:
      # Logged-In View
      cur_groups_user = node_collection.find({'_type': "Group", 
                                       '_id': {'$nin': [ObjectId(group_id), auth._id]},
                                       '$and': [query_dict],
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
      cur_public = node_collection.find({'_type': "Group", 
                                       '_id': {'$nin': [ObjectId(group_id)]},
                                       '$and': [query_dict],
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

  else: # for GET request

    if auth:
      # Logged-In View
      cur_groups_user = node_collection.find({'_type': "Group", 
                                              '$and': [query_dict],
                                              '_id': {'$nin': [ObjectId(group_id), auth._id]},
                                              'name': {'$nin': ["home"]},
                                              '$or': [
                                                      {'created_by': request.user.id},
                                                      {'author_set': request.user.id},
                                                      {'group_admin': request.user.id},
                                                      {'group_type': 'PUBLIC'}
                                                    ]
                                            }).sort('last_update', -1)
      # if cur_groups_user.count():
      #   for group in cur_groups_user:
      #     group_nodes.append(group)

      if cur_groups_user.count():
        group_nodes = cur_groups_user
        group_count = cur_groups_user.count()
        
    else:
      # Without Log-In View
      cur_public = node_collection.find({'_type': "Group", 
                                         '_id': {'$nin': [ObjectId(group_id)]},
                                         '$and': [query_dict],
                                         'name': {'$nin': ["home"]},
                                         'group_type': "PUBLIC"
                                     }).sort('last_update', -1)
  
      # if cur_public.count():
      #   for group in cur_public:
      #     group_nodes.append(group)
  
      if cur_public.count():
        group_nodes = cur_public
        group_count = cur_public.count()
    
    return render_to_response("ndf/group.html", 
                              {'group_nodes': group_nodes,
                               'appId':app._id,
                               'group_nodes_count': group_count,
                               'groupid': group_id, 'group_id': group_id
                              }, context_instance=RequestContext(request))


@login_required
@get_execution_time
def create_group(request,group_id):
  ins_objectid  = ObjectId()
  if ins_objectid.is_valid(group_id) is False :
    group_ins = node_collection.find_one({'_type': "Group","name": group_id}) 
    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) }) 
    if group_ins:
      group_id = str(group_ins._id)
    else:
      auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if auth:
        group_id = str(auth._id)	
  else :
  	pass

  if request.method == "POST":
    colg = node_collection.collection.Group()
    Mod_colg = node_collection.collection.Group()

    cname = request.POST.get('groupname', "").strip()
    colg.altnames = cname
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
    colg.agency_type=request.POST.get('agency_type', "")
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

    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) }) 

    has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })

    shelves = []
    shelf_list = {}
    
    if auth:
      shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type.$id': has_shelf_RT._id })

      if shelf:
        for each in shelf:
          shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)})           
          shelves.append(shelf_name)

          shelf_list[shelf_name.name] = []         
          for ID in shelf_name.collection_set:
            shelf_item = node_collection.one({'_id': ObjectId(ID) })
            shelf_list[shelf_name.name].append(shelf_item.name)
                  
      else:
        shelves = []

    return render_to_response("ndf/groupdashboard.html", {'groupobj': colg, 'appId': app._id, 'node': colg, 'user': request.user,
                                                         'groupid': colg._id, 'group_id': colg._id,
                                                         'shelf_list': shelf_list,'shelves': shelves
                                                        },context_instance=RequestContext(request))


  available_nodes = node_collection.find({'_type': u'Group', 'member_of': ObjectId(gst_group._id) })
  nodes_list = []
  for each in available_nodes:
      nodes_list.append(str((each.name).strip().lower()))

  return render_to_response("ndf/create_group.html", {'groupid': group_id, 'appId': app._id, 'group_id': group_id, 'nodes_list': nodes_list},RequestContext(request))


# @get_execution_time
#def home_dashboard(request):
#     try:
#         groupobj=node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
#     except Exception as e:
#         groupobj=""
#         pass
#     print "frhome--",groupobj
#     return render_to_response("ndf/groupdashboard.html",{'groupobj':groupobj,'user':request.user,'curgroup':groupobj},context_instance=RequestContext(request))


@login_required
@get_execution_time
def populate_list_of_members():
	members = User.objects.all()
	memList = []
	for mem in members:
		memList.append(mem.username)	
	return memList


@login_required
@get_execution_time
def populate_list_of_group_members(group_id):
    try :
      try:
        author_list = node_collection.one({"_type":"Group", "_id":ObjectId(group_id)}, {"author_set":1, "_id":0})
      except:
        author_list = node_collection.find_one({"_type":"Group", "name":group_id}, {"author_set":1, "_id":0})
      
      memList = []

      for author in author_list.author_set:
          name_author = User.objects.get(pk=author)
          memList.append(name_author)
      return memList
    except:
        return []


@get_execution_time
def group_dashboard(request, group_id=None):
  # # print "reahcing"
  # if ins_objectid.is_valid(group_id) is False :
  #   group_ins = node_collection.find_one({'_type': "Group","name": group_id})
  #   auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
  #   if group_ins:
	 #    group_id = str(group_ins._id)
  #   else :
	 #    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	 #    if auth :
	 #    	group_id = str(auth._id)	
  # else :
  # 	pass

  try:
    group_obj = "" 
    shelf_list = {}
    shelves = []
    alternate_template = ""
    profile_pic_image = None

    group_obj = get_group_name_id(group_id, get_obj=True)

    if not group_obj:
      group_obj=node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
      group_id=group_obj['_id']
    else:
      # group_obj=node_collection.one({'_id':ObjectId(group_id)})
      group_id = group_obj._id

      # getting the profile pic File object
      for each in group_obj.relation_set:
          if "has_profile_pic" in each:
              profile_pic_image = node_collection.one(
                  {'_type': "File", '_id': each["has_profile_pic"][0]}
              )
              break

    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) }) 

    if auth:

      has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })

      shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type.$id': has_shelf_RT._id })        
      shelf_list = {}

      if shelf:
        for each in shelf:
          shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)})           
          shelves.append(shelf_name)

          shelf_list[shelf_name.name] = []
          for ID in shelf_name.collection_set:
            shelf_item = node_collection.one({'_id': ObjectId(ID) })
            shelf_list[shelf_name.name].append(shelf_item.name)
              
      else:
          shelves = []

  except Exception as e:
    group_obj=node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
    group_id=group_obj['_id']
    pass

  # Call to get_neighbourhood() is required for setting-up property_order_list
  group_obj.get_neighbourhood(group_obj.member_of)

  property_order_list = []
  if "group_of" in group_obj:
    if group_obj['group_of']:
      college = node_collection.one({'_type': "GSystemType", 'name': "College"}, {'_id': 1})

      if college:
        if college._id in group_obj['group_of'][0]['member_of']:
          alternate_template = "ndf/college_group_details.html"

      property_order_list = get_property_order_with_value(group_obj['group_of'][0])

  annotations = json.dumps(group_obj.annotations)
  
  default_template = "ndf/groupdashboard.html"
  return render_to_response([alternate_template,default_template] ,{'node': group_obj, 'groupid':group_id, 
                                                       'group_id':group_id, 'user':request.user, 
                                                       'shelf_list': shelf_list,
                                                       'appId':app._id,
                                                       'annotations' : annotations, 'shelves': shelves,
                                                       'prof_pic_obj': profile_pic_image
                                                      },context_instance=RequestContext(request)
                          )


@login_required
@get_execution_time
def edit_group(request, group_id):
  ins_objectid  = ObjectId()
  is_auth_node = False
  if ins_objectid.is_valid(group_id) is False :
    group_ins = node_collection.find_one({'_type': "Group","name": group_id}) 
    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    if group_ins:
      group_id = str(group_ins._id)
    else:
      auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if auth :
        group_id = str(auth._id)
        is_auth_node = True

  else:
    pass
  page_node = node_collection.one({"_id": ObjectId(group_id)})
  title = gst_group.name
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

  available_nodes = node_collection.find({'_type': u'Group', 'member_of': ObjectId(gst_group._id) })
  nodes_list = []
  for each in available_nodes:
      nodes_list.append(str((each.name).strip().lower()))

  return render_to_response("ndf/edit_group.html",
                                    { 'node': page_node,'title':title,
                                      'appId':app._id,
                                      'groupid':group_id,
                                      'nodes_list': nodes_list,
                                      'group_id':group_id,
                                      'is_auth_node':is_auth_node
                                      },
                                    context_instance=RequestContext(request)
                                    )


@login_required
@get_execution_time
def app_selection(request, group_id):
    if ObjectId.is_valid(group_id) is False:
        group_ins = node_collection.find_one({
            '_type': "Group", "name": group_id
        })
        auth = node_collection.one({
            '_type': 'Author', 'name': unicode(request.user.username)
        })
        if group_ins:
            group_id = str(group_ins._id)
        else:
            auth = collection.Node.one({
                '_type': 'Author', 'name': unicode(request.user.username)
            })
            if auth:
                group_id = str(auth._id)
    else:
        pass

    try:
        grp = node_collection.one({
            "_id": ObjectId(group_id)
        }, {
            "name": 1, "attribute_set.apps_list": 1
        })
        if request.method == "POST":
            apps_to_set = request.POST['apps_to_set']
            apps_to_set = json.loads(apps_to_set)

            apps_to_set = [
                ObjectId(app_id) for app_id in apps_to_set if app_id
            ]

            apps_list = []
            apps_list_append = apps_list.append
            for each in apps_to_set:
                apps_list_append(
                    node_collection.find_one({
                        "_id": each
                    })
                )

            at_apps_list = node_collection.one({
                '_type': 'AttributeType', 'name': 'apps_list'
            })
            ga_node = create_gattribute(grp._id, at_apps_list, apps_list)
            return HttpResponse("Apps list updated successfully.")

        else:
            list_apps = []

            for attr in grp.attribute_set:
                if attr and "apps_list" in attr:
                    list_apps = attr["apps_list"]
                    break

            st = get_gapps(already_selected_gapps=list_apps)

            data_list = set_drawer_widget(st, list_apps)
            return HttpResponse(json.dumps(data_list))

    except Exception as e:
        print "Error in app_selection " + str(e)


@get_execution_time
def switch_group(request,group_id,node_id):
  ins_objectid = ObjectId()
  if ins_objectid.is_valid(group_id) is False:
    group_ins = node_collection.find_one({'_type': "Group","name": group_id}) 
    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) }) 
    if group_ins:
      group_id = str(group_ins._id)
    else:
      auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if auth:
      	group_id = str(auth._id)
  else :
  	pass

  try:
    node = node_collection.one({"_id": ObjectId(node_id)})
    existing_grps = node.group_set
    if request.method == "POST":
      new_grps_list = request.POST.getlist("new_groups_list[]", "")
      resource_exists = False
      resource_exists_in_grps = []
      response_dict = {'success': False, 'message': ""}

      new_grps_list_distinct = [ObjectId(item) for item in new_grps_list if ObjectId(item) not in existing_grps]
      if new_grps_list_distinct:
        for each_new_grp in new_grps_list_distinct:
          if each_new_grp:
            grp = node_collection.find({'name': node.name, "group_set": ObjectId(each_new_grp), "member_of":ObjectId(node.member_of[0])})
            if grp.count() > 0:
              resource_exists = True
              resource_exists_in_grps.append(unicode(each_new_grp))

        response_dict["resource_exists_in_grps"] = resource_exists_in_grps

      if not resource_exists:
        new_grps_list_all = [ObjectId(item) for item in new_grps_list]
        node_collection.collection.update({'_id': node._id}, {'$set': {'group_set': new_grps_list_all}}, upsert=False, multi=False)
        node.reload()
        response_dict["success"] = True
        response_dict["message"] = "Published to selected groups"
      else:
        response_dict["success"] = False
        response_dict["message"] = node.member_of_names_list[0] + " with name " + node.name + \
                " already exists. Hence Cannot Publish to selected groups."
        response_dict["message"] = node.member_of_names_list[0] + " with name " + node.name + \
                " already exists in selected group(s). " + \
                "Hence cannot be cross published now." + \
                " For publishing, you can rename this " + node.member_of_names_list[0] + " and try again."
      # print response_dict
      return HttpResponse(json.dumps(response_dict))

    else:
      coll_obj_list = []
      data_list = []
      user_id = request.user.id
      all_user_groups = []
      for each in get_all_user_groups():
        all_user_groups.append(each.name)
      st = node_collection.find({'$and': [{'_type': 'Group'}, {'author_set': {'$in':[user_id]}},{'name':{'$nin':all_user_groups}}]})
      for each in node.group_set:
        coll_obj_list.append(node_collection.one({'_id': each}))
      data_list = set_drawer_widget(st, coll_obj_list)
      return HttpResponse(json.dumps(data_list))
   
  except Exception as e:
    print "Exception in switch_group"+str(e)
    return HttpResponse("Failure")


@login_required
@get_execution_time
def publish_group(request,group_id,node):
  # ins_objectid  = ObjectId()
  # if ins_objectid.is_valid(group_id) is False :
  #   group_ins = node_collection.find_one({'_type': "Group","name": group_id})
  #   auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
  #   if group_ins:
	 #    group_id = str(group_ins._id)
  #   else:
	 #    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	 #    if auth :
	 #    	group_id = str(auth._id)	
  # else :
  # 	pass

    group_obj = get_group_name_id(group_id, get_obj=True)
    profile_pic_image = None

    if group_obj:
      # group_obj=node_collection.one({'_id':ObjectId(group_id)})
      group_id = group_obj._id

      # getting the profile pic File object
      for each in group_obj.relation_set:

          if "has_profile_pic" in each:
              profile_pic_image = node_collection.one( {'_type': "File", '_id': each["has_profile_pic"][0]} )
              break

    node=node_collection.one({'_id':ObjectId(node)})
     
    page_node,v=get_page(request,node)
    
    node.content = page_node.content
    node.content_org=page_node.content_org
    node.status=unicode("PUBLISHED")
    node.modified_by = int(request.user.id)
    node.save() 
   
    return render_to_response("ndf/groupdashboard.html",
                                   { 'group_id':group_id, 'groupid':group_id,
                                   'node':node, 'appId':app._id,                                   
                                   'prof_pic_obj': profile_pic_image
                                 },
                                  context_instance=RequestContext(request)
                              )


@login_required
@get_execution_time
def create_sub_group(request,group_id):
  try:
      ins_objectid  = ObjectId()
      grpname=""
      if ins_objectid.is_valid(group_id) is False :
          group_ins = node_collection.find_one({'_type': "Group","name": group_id}) 
          auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
          if group_ins:
              grpname=group_ins.name 
              group_id = str(group_ins._id)
          else :
              auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
              if auth :
                  group_id = str(auth._id)
                  grpname=auth.name	
      else :
          group_ins = node_collection.find_one({'_type': "Group","_id": ObjectId(group_id)})
          if group_ins:
              grpname=group_ins.name
              pass
          else:
              group_ins = node_collection.find_one({'_type': "Author","_id": ObjectId(group_id)})
              if group_ins:
                  grpname=group_ins.name
                  pass

      if request.method == "POST":
          colg = node_collection.collection.Group()
          Mod_colg=node_collection.collection.Group()
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
          #save subgroup_id in the collection_set of parent group 
          group_ins.collection_set.append(colg._id)
          #group_ins.post_node.append(colg._id)
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
          auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) }) 
          has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })
          shelves = []
          shelf_list = {}
    
          if auth:
              shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type.$id': has_shelf_RT._id })        

              if shelf:
                  for each in shelf:
                      shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)})
                      shelves.append(shelf_name)
                      shelf_list[shelf_name.name] = []
                      for ID in shelf_name.collection_set:
                          shelf_item = node_collection.one({'_id': ObjectId(ID) })
                          shelf_list[shelf_name.name].append(shelf_item.name)
                  
              else:
                  shelves = []

          return render_to_response("ndf/groupdashboard.html",{'groupobj':colg,'appId':app._id,'node':colg,'user':request.user,
                                                         'groupid':colg._id,'group_id':colg._id,
                                                         'shelf_list': shelf_list,'shelves': shelves
                                                        },context_instance=RequestContext(request))
      available_nodes = node_collection.find({'_type': u'Group', 'member_of': ObjectId(gst_group._id) })
      nodes_list = []
      for each in available_nodes:
          nodes_list.append(str((each.name).strip().lower()))

      return render_to_response("ndf/create_sub_group.html", {'groupid':group_id,'maingroup':grpname,'group_id':group_id,'nodes_list': nodes_list},RequestContext(request))
  except Exception as e:
      print "Exception in create subgroup "+str(e)


