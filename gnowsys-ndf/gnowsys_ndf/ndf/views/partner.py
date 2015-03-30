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
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_existing_groups, get_all_user_groups
from gnowsys_ndf.ndf.views.methods import *

# ######################################################################################################################################

gst_group = node_collection.one({"_type": "GSystemType", 'name': GAPPS[2]})
get_all_usergroups=get_all_user_groups()
at_apps_list=node_collection.one({'$and':[{'_type':'AttributeType'},{'name':'apps_list'}]})
ins_objectid  = ObjectId()
app=gst_group

# ######################################################################################################################################
#      V I E W S   D E F I N E D   F O R   P A R T N E R '
# ######################################################################################################################################

@login_required
@get_execution_time
def create_partner(request,group_id):
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
    colg.agency_type = "Partner"
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
  return render_to_response("ndf/create_partner.html", {'groupid': group_id, 'appId': app._id, 'group_id': group_id, 'nodes_list': nodes_list},RequestContext(request))
    

@get_execution_time
def nroer_groups(request, group_id, groups_category):
    group_name, group_id = get_group_name_id(group_id)

    mapping = GSTUDIO_NROER_MENU_MAPPINGS

    # loop over nroer menu except "Repository" 
    for each_item in GSTUDIO_NROER_MENU[1:]:
        temp_key_name = each_item.keys()[0]
        if temp_key_name == groups_category:
            groups_names_list = each_item.get(groups_category, [])
            
            # mapping for the text names in list
            groups_names_list = [mapping.get(i) for i in groups_names_list]
            break

    group_nodes = node_collection.find({ '_type': "Group", 
                                        '_id': {'$nin': [ObjectId(group_id)]},
                                        'name': {'$nin': ["home"], '$in': groups_names_list},
                                        'group_type': "PUBLIC"
                                     })#.sort('last_update', -1)
    
    group_nodes_count = group_nodes.count() if group_nodes else 0
    is_partner = True
    return render_to_response("ndf/partner.html", 
                          {'group_nodes': group_nodes,
                           'is_partner':is_partner,
                           'group_nodes_count': group_nodes_count,
                           'groupid': group_id, 'group_id': group_id
                          }, context_instance=RequestContext(request))
