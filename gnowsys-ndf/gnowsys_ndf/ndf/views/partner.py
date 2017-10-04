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
from gnowsys_ndf.settings import GAPPS, GSTUDIO_GROUP_AGENCY_TYPES, GSTUDIO_NROER_MENU, GSTUDIO_NROER_MENU_MAPPINGS

# from gnowsys_ndf.ndf.models import GSystemType, GSystem, Group, Triple
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_existing_groups#, get_all_user_groups
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.ndf.views.notify import set_notif_val

# ######################################################################################################################################

gst_group = node_collection.one({"_type": "GSystemType", 'name': GAPPS[2]})
partner_group_gst = node_collection.one({"_type": "GSystemType", 'name': u'PartnerGroup'})
# get_all_usergroups=get_all_user_groups()
at_apps_list=node_collection.one({'$and':[{'_type':'AttributeType'},{'name':'apps_list'}]})
ins_objectid  = ObjectId()
app=gst_group

# ######################################################################################################################################
#      V I E W S   D E F I N E D   F O R   P A R T N E R '
# ######################################################################################################################################

@login_required
@get_execution_time
def create_partner(request,group_id):
  # ins_objectid  = ObjectId()
  # if ins_objectid.is_valid(group_id) is False :
  #   group_ins = node_collection.find_one({'_type': "Group","name": group_id})
  #   auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
  #   if group_ins:
  #     group_id = str(group_ins._id)
  #   else:
  #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
  #     if auth:
  #       group_id = str(auth._id)
  # else :
  # 	pass

  group_obj = get_group_name_id(group_id, get_obj=True)

  pg_gst = node_collection.one({'_type': "GSystemType", 'name': "PartnerGroup"})

  try:
    if request.method == "POST":
      colg = node_collection.collection.Group()
      street = request.POST.get('street', "")
      cname = request.POST.get('groupname', "").strip()
      colg.altnames = cname
      colg.name = unicode(cname)
      colg.member_of.append(gst_group._id)
      usrid = int(request.user.id)

      colg.created_by = usrid
      colg.author_set.append(usrid)

      colg.modified_by = usrid
      colg.contributors.append(usrid)

      #colg.group_type = request.POST.get('group_type', "")
      #colg.edit_policy = request.POST.get('edit_policy', "")
      #colg.subscription_policy = request.POST.get('subscription', "")
      colg.visibility_policy = request.POST.get('existance', 'ANNOUNCED')
      colg.disclosure_policy = request.POST.get('member', 'DISCLOSED_TO_MEM')
      colg.encryption_policy = request.POST.get('encryption', 'NOT_ENCRYPTED')
      colg.agency_type = "Partner"
      colg.save(groupid=group_id)
      # get alll attribute associated with partner
      attribute_set=colg.get_possible_attributes(colg.member_of).keys()
      activ="Request to become a partner"
      msg = colg.name+" is interested to became a partner on the platform "
      set_notif_val(request, colg._id, msg, activ, request.user)
      for each in attribute_set:

          if each !="apps_list":
              obj_val = request.POST.get(each, "").strip()
              att_type=node_collection.one({'_type':"AttributeType","name":each})
              # set  Attribute type values for partner
              create_gattribute(colg._id, att_type , object_value = obj_val)


      auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })

      # has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })

      # shelves = []
      # shelf_list = {}

      # if auth:
      #   shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': has_shelf_RT._id })

      #   if shelf:
      #     for each in shelf:
      #       shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)})
      #       shelves.append(shelf_name)

      #       shelf_list[shelf_name.name] = []
      #       for ID in shelf_name.collection_set:
      #         shelf_item = node_collection.one({'_id': ObjectId(ID) })
      #         shelf_list[shelf_name.name].append(shelf_item.name)

      #   else:
      #     shelves = []
      return render_to_response("ndf/groupdashboard.html", {'groupobj': colg, 'appId': app._id, 'node': colg, 'user': request.user,
                                                           'groupid': colg._id, 'group_id': colg._id,
                                                           # 'shelf_list': shelf_list,'shelves': shelves
                                                          },context_instance=RequestContext(request))

  except Exception as e:
    print "\n\n e",e
  available_nodes = node_collection.find({'_type': u'Group', 'member_of': ObjectId(gst_group._id) })
  nodes_list = []

  for each in available_nodes:
      nodes_list.append(str((each.name).strip().lower()))
  return render_to_response("ndf/create_partner.html", {'groupid': group_id, 'group_obj':group_obj,'appId': app._id, 'group_id': group_id, 'nodes_list': nodes_list},RequestContext(request))


def partner_list(request, group_id):

    group_obj = get_group_name_id(group_id, get_obj=True)
    app_gst = node_collection.one({'_type': 'GSystemType', 'name': 'PartnerGroup'})
    group_nodes = None
    collection_set = []
    # groups_category = None
    if group_obj:
        group_id = group_obj._id
        group_name = group_obj.name
        groups_category = group_obj.agency_type
        # groups_category = "Partner" if groups_category == "Partner" else "Group"

        group_obj = node_collection.one({'_id': ObjectId(group_id)})
        # if group_obj:
        #     for each in group_obj.collection_set:
        #         node = node_collection.one({'_id': each})
        #         collection_set.append(node)

        group_nodes = node_collection.find({'_id': {'$in':group_obj.post_node}}).sort("last_update",-1)
    # print GSTUDIO_NROER_MENU_MAPPINGS.get(group_name, None)
    # print GSTUDIO_NROER_MENU
    return render_to_response("ndf/partner_list.html",
                          {'group_nodes': group_nodes,
                           # "groups_category": groups_category,
                           'group_obj':group_obj,
                           'groupid': group_id, 'group_id': group_id, "app_gst": partner_group_gst,
                          }, context_instance=RequestContext(request))


@get_execution_time
def nroer_groups(request, group_id, groups_category):
    group_name, group_id = get_group_name_id(group_id)

    mapping = GSTUDIO_NROER_MENU_MAPPINGS

    groups_names_list = []
    # loop over nroer menu except "Repository"
    for each_item in GSTUDIO_NROER_MENU[1:]:
        temp_key_name = each_item.keys()[0]
        if temp_key_name == groups_category:
            groups_names_list = each_item.get(groups_category, [])
            # mapping for the text names in list
            groups_names_list = [mapping.get(i) for i in groups_names_list]
            break
    # print "\n\ngroups_names_list",groups_names_list
    group_nodes = []
    '''
    For displaying Partners and Groups in same order
     as defined in settings GSTUDIO_NROER_MENU_MAPPINGS
    '''
    for eachgroup in groups_names_list:
        grp_node = node_collection.one({'_type': "Group", 'name': unicode(eachgroup)})
        group_nodes.append(grp_node)

    # group_nodes = node_collection.find({ '_type': "Group",
    #                                     '_id': {'$nin': [ObjectId(group_id)]},

    #                                     'name': {'$nin': ["home"], '$in': groups_names_list},
    #                                     'group_type': "PUBLIC"
    #                                  }).sort('created_at', -1)

    if groups_category == "Partners":
        app_gst = node_collection.one({'_type': 'GSystemType', 'name': 'PartnerGroup'})

    elif groups_category == "Groups":
        app_gst = gst_group

    # print "=============", app_gst
    # group_nodes_count = group_nodes.count() if group_nodes else 0
    return render_to_response("ndf/partner.html",
                          {'group_nodes': group_nodes, "groups_category": groups_category,
                           #'group_nodes_count': group_nodes_count,
                          'app_gst': app_gst,
                           'groupid': group_id, 'group_id': group_id,

                          }, context_instance=RequestContext(request))


def partner_showcase(request, group_id):

    group_name, group_id = get_group_name_id(group_id)

    all_source = node_collection.find({'attribute_set.source': {'$exists': True, '$ne': ''} }).distinct('attribute_set.source')

    partner_group = node_collection.one({'_type': 'GSystemType', 'name': 'PartnerGroup'})

    source_partners = node_collection.find({'_type': 'Group', 'member_of': {'$in': [partner_group._id]}, 'name': {'$in': all_source} }).sort('name',1)

    return render_to_response('ndf/partner_showcase.html',
                            {
                              'group_id': group_id, 'groupid': group_id,
                              'source_partners': source_partners
                            }, context_instance=RequestContext(request)
                          )
