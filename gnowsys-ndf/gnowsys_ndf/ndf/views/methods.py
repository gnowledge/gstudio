''' -- imports from installed packages -- '''
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response, render
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from mongokit import paginator
import mongokit 


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.mobwrite.models import TextObj
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.notification import models as notification

''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import subprocess
import re
import ast
import string
import json
from datetime import datetime


db = get_database()
collection = db[Node.collection_name]

history_manager = HistoryManager()
theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})


# C O M M O N   M E T H O D S   D E F I N E D   F O R   V I E W S

coln=db[GSystem.collection_name]
grp_st=coln.Node.one({'$and':[{'_type':'GSystemType'},{'name':'Group'}]})
ins_objectid  = ObjectId()

def check_delete(main):
  try:
    def check(*args, **kwargs):
      relns=""
      node_id=kwargs['node_id']
      ins_objectid  = ObjectId()
      if ins_objectid.is_valid(node_id) :
        node=collection.Node.one({'_id':ObjectId(node_id)})
        relns=node.get_possible_relations(node.member_of)
        attrbts=node.get_possible_attributes(node.member_of)
        return main(*args, **kwargs)
      else:
        print "Not a valid id"
    return check 
  except Exception as e:
    print "Error in check_delete "+str(e)

def get_all_resources_for_group(group_id):
  if ins_objectid.is_valid(group_id):
    obj_resources=coln.Node.find({'$and':[{'$or':[{'_type':'GSystem'},{'_type':'File'}]},{'group_set':{'$all':[ObjectId(group_id)]}},{'member_of':{'$nin':[grp_st._id]}}]})
    return obj_resources


def get_all_gapps():
  meta_type_gapp=coln.Node.one({'$and':[{'_type':'MetaType'},{'name':'GAPP'}]})
  all_gapps=coln.Node.find({'$and':[{'_type':'GSystemType'},{'member_of':{'$all':[meta_type_gapp._id]}}]})    
  return list(all_gapps)

#checks forum notification turn off for an author object
def forum_notification_status(group_id,user_id):
  try:
    grp_obj=coln.Node.one({'_id':ObjectId(group_id)})
    auth_obj=coln.Node.one({'_id':ObjectId(user_id)})
    at_user_pref=collection.Node.one({'$and':[{'_type':'AttributeType'},{'name':'user_preference_off'}]})
    list_at_pref=[]
    if at_user_pref:
      poss_attrs=auth_obj.get_possible_attributes(at_user_pref._id)
      if poss_attrs:
        if poss_attrs.has_key('user_preference_off'):
          list_at_pref=poss_attrs['user_preference_off']['object_value']
        if grp_obj in list_at_pref:
          return False
        else:
          return True
    return True
  except Exception as e:
    print "Exception in forum notification status check "+str(e)
def get_forum_repl_type(forrep_id):
  forum_st = coln.GSystemType.one({'$and':[{'_type':'GSystemType'},{'name':GAPPS[5]}]})
  obj=coln.GSystem.one({'_id':ObjectId(forrep_id)})
  if obj:
    if forum_st._id in obj.member_of:
      return "Forum"
    else:    
      return "Reply"
  else:
    return "None"

def check_existing_group(group_name):
  collection = db[Node.collection_name]
  if type(group_name) == 'unicode':
    colg = collection.Node.find({'_type': u'Group', "name": group_name})
    if colg.count()>0:
      return True
    if ins_objectid.is_valid(group_name):    #if group_name holds group_id
      colg = collection.Node.find({'_type': u'Group', "_id": ObjectId(group_name)})
    if colg.count()>0:
      return True
    else:
      colg = collection.Node.find({'_type': {'$in':['Group', 'Author']}, "_id": ObjectId(group_name)})
      if colg.count()>0:
        return True      
  else:
    if ins_objectid.is_valid(group_name):     #if group_name holds group_id
      colg = collection.Node.find({'_type': u'Group', "_id": ObjectId(group_name)})
      if colg.count()>0:
        return True
      colg = collection.Node.find({'_type': {'$in':['Group', 'Author']}, "_id": ObjectId(group_name)})
      if colg.count()>0:
        return True
    else:
      colg = collection.Node.find({'_type': {'$in':['Group', 'Author']}, "_id": group_name._id})
  if colg.count() >= 1:
    return True
  else:
    return False


def filter_drawer_nodes(nid, group_id=None):
  page_gst = collection.Node.one({'_type': 'GSystemType', 'name': 'Page'})
  file_gst = collection.Node.one({'_type': 'GSystemType', 'name': 'File'})
  Pandora_video_gst = collection.Node.one({'_type': 'GSystemType', 'name': 'Pandora_video'})
  quiz_gst = collection.Node.one({'_type': 'GSystemType', 'name': 'Quiz'})
  quizItem_gst = collection.Node.one({'_type': "GSystemType", 'name': "QuizItem"})
  query = None

  if group_id:
    query = {'_type': {'$in': ['GSystem', 'File']}, 'group_set': ObjectId(group_id), 
                'collection_set': {'$exists': True, '$not': {'$size': 0}, '$in':[ObjectId(nid)]},
                'member_of': {'$in': [page_gst._id,file_gst._id,Pandora_video_gst._id,quiz_gst._id,quizItem_gst._id] }
            }

  else:
    query = {'_type': {'$in': ['GSystem', 'File']},'collection_set': {'$exists': True, '$not': {'$size': 0}, '$in':[ObjectId(nid)]},
            'member_of': {'$in': [page_gst._id,file_gst._id,Pandora_video_gst._id,quiz_gst._id,quizItem_gst._id] }
            }                   

  nodes = collection.Node.find(query)

  # Remove parent nodes in which current node exists
  def filter_nodes(parents, group_id=None):  
    length = []
    if parents:
      length.extend(parents)

      inner_parents = []
      for each in parents:
        if group_id:
          query = {'_type': {'$in': ['GSystem', 'File']}, 'group_set': ObjectId(group_id), 
                    'collection_set': {'$exists': True, '$not': {'$size': 0}, '$in':[ObjectId(each)]},
                    'member_of': {'$in': [page_gst._id,file_gst._id,Pandora_video_gst._id,quiz_gst._id,quizItem_gst._id] }
                  }
        else:
          query = {'_type': {'$in': ['GSystem', 'File']},
                    'collection_set': {'$exists': True, '$not': {'$size': 0}, '$in':[ObjectId(each)]},
                    'member_of': {'$in': [page_gst._id,file_gst._id,Pandora_video_gst._id,quiz_gst._id,quizItem_gst._id] }
                  }

        nodes = collection.Node.find(query)
        if nodes.count() > 0:
          for k in nodes:
            inner_parents.append(k._id) 
   
      for each in inner_parents:
        if each not in parents:
          parents.append(each)

      if set(length) != set(parents):
        parents = filter_nodes(parents, group_id)
        return parents        
      else:
        return parents

  parents_list = []
  if nodes.count() > 0: 
    for each in nodes:
      parents_list.append(each._id)

    parents = filter_nodes(parents_list, group_id)    
    return parents 
  else:
    return parents_list



def get_drawers(group_id, nid=None, nlist=[], page_no=1, checked=None, **kwargs):
    """Get both drawers-list.
    """
    dict_drawer = {}
    dict1 = {}
    dict2 = []  # Changed from dictionary to list so that it's content are reflected in a sequential-order

    collection = db[Node.collection_name]

    drawer = None    

    if checked:
      filtering = filter_drawer_nodes(nid, group_id)

      if checked == "Page":
        gst_page_id = collection.Node.one({'_type': "GSystemType", 'name': "Page"})._id
        drawer = collection.Node.find({'_type': u"GSystem", '_id': {'$nin': filtering},'member_of': {'$all':[gst_page_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})
        
      elif checked == "File":         
        drawer = collection.Node.find({'_type': u"File", '_id': {'$nin': filtering},'group_set': {'$all': [ObjectId(group_id)]}})
        
      elif checked == "Image":
        gst_image_id = collection.Node.one({'_type': "GSystemType", 'name': "Image"})._id
        drawer = collection.Node.find({'_type': u"File", '_id': {'$nin': filtering},'member_of': {'$in':[gst_image_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "Video":         
        gst_video_id = collection.Node.one({'_type': "GSystemType", 'name': "Video"})._id
        drawer = collection.Node.find({'_type': u"File", '_id': {'$nin': filtering},'member_of': {'$in':[gst_video_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "Quiz":
        # For prior-node-list
        drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, '_id': {'$nin': filtering},'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "QuizObj" or checked == "assesses":
        # For collection-list
        gst_quiz_id = collection.Node.one({'_type': "GSystemType", 'name': "Quiz"})._id
        gst_quiz_item_id = collection.Node.one({'_type': "GSystemType", 'name': "QuizItem"})._id
        drawer = collection.Node.find({'_type': u"GSystem", '_id': {'$nin': filtering},'member_of': {'$in':[gst_quiz_id, gst_quiz_item_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "OnlyQuiz":
        gst_quiz_id = collection.Node.one({'_type': "GSystemType", 'name': "Quiz"})._id
        drawer = collection.Node.find({'_type': u"GSystem", '_id': {'$nin': filtering},'member_of': {'$all':[gst_quiz_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "QuizItem":
        gst_quiz_item_id = collection.Node.one({'_type': "GSystemType", 'name': "QuizItem"})._id
        drawer = collection.Node.find({'_type': u"GSystem", '_id': {'$nin': filtering},'member_of': {'$all':[gst_quiz_item_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "Group":
        drawer = collection.Node.find({'_type': u"Group", '_id': {'$nin': filtering} })

      elif checked == "Forum":
        gst_forum_id = collection.Node.one({'_type': "GSystemType", 'name': "Forum"})._id
        drawer = collection.Node.find({'_type': u"GSystem", '_id': {'$nin': filtering},'member_of': {'$all':[gst_forum_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "Module":
        gst_module_id = collection.Node.one({'_type': "GSystemType", 'name': "Module"})._id
        drawer = collection.Node.find({'_type': u"GSystem", '_id': {'$nin': filtering},'member_of': {'$all':[gst_module_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "Pandora Video":
        gst_pandora_video_id = collection.Node.one({'_type': "GSystemType", 'name': "Pandora_video"})._id
        drawer = collection.Node.find({'_type': u"File", '_id': {'$nin': filtering},'member_of': {'$all':[gst_pandora_video_id]}, 'group_set': {'$all': [ObjectId(group_id)]}}).limit(50)

      elif checked == "Theme":
        theme_GST_id = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
        topic_GST_id = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})    
        drawer = collection.Node.find({'_type': u"GSystem", '_id': {'$nin': filtering},'member_of': {'$in':[theme_GST_id._id, topic_GST_id._id]}, 'group_set': {'$all': [ObjectId(group_id)]}}) 

      elif checked == "theme_item":
        theme_item_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'theme_item'})
        topic_GST_id = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})    
        drawer = collection.Node.find({'_type': u"GSystem", '_id': {'$nin': filtering},'member_of': {'$in':[theme_item_GST._id, topic_GST_id._id]}, 'group_set': {'$all': [ObjectId(group_id)]}}) 

      elif checked == "Topic":
        drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, '_id': {'$nin': filtering},'member_of':{'$nin':[theme_GST_id._id, theme_item_GST._id, topic_GST_id._id]},'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "RelationType":
        # Special case used while dealing with RelationType widget
        if kwargs.has_key("left_drawer_content"):
          drawer = kwargs["left_drawer_content"]

    else:
      # For heterogeneous collection
      if checked == "RelationType":
        # Special case used while dealing with RelationType widget
        drawer = checked

      else:
        filtering = filter_drawer_nodes(nid, group_id)
        Page = collection.Node.one({'_type': 'GSystemType', 'name': 'Page'})
        File = collection.Node.one({'_type': 'GSystemType', 'name': 'File'})
        Quiz = collection.Node.one({'_type': "GSystemType", 'name': "Quiz"})
        drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, 
                                       '_id': {'$nin': filtering},'group_set': {'$all': [ObjectId(group_id)]}, 
                                       'member_of':{'$in':[Page._id,File._id,Quiz._id]}
                                      })

    if checked != "RelationType":
      paged_resources = paginator.Paginator(drawer, page_no, 10)
      drawer.rewind()
    

    if (nid is None) and (not nlist):
      for each in drawer:
        dict_drawer[each._id] = each

    elif (nid is None) and (nlist):
      for each in drawer:
        if each._id not in nlist:
          dict1[each._id] = each

      for oid in nlist:
        obj = collection.Node.one({'_id': oid})
        dict2.append(obj)

      dict_drawer['1'] = dict1
      dict_drawer['2'] = dict2
    
    else:
      for each in drawer:

        if each._id != nid:
          if each._id not in nlist:
            dict1[each._id] = each
          
      for oid in nlist: 
        obj = collection.Node.one({'_id': oid})
        dict2.append(obj)
      
      dict_drawer['1'] = dict1
      dict_drawer['2'] = dict2

    if checked == "RelationType":
      return dict_drawer

    else:

      return dict_drawer, paged_resources




# get type of resource
def get_resource_type(request,node_id):
  get_resource_type=collection.Node.one({'_id':ObjectId(node_id)})
  get_type=get_resource_type._type
  return get_type 
                          
def get_translate_common_fields(request,get_type,node, group_id, node_type, node_id):
  """ retrive & update the common fields required for translation of the node """

  gcollection = db[Node.collection_name]
  usrid = int(request.user.id)
  content_org = request.POST.get('content_org')
  tags = request.POST.get('tags')
  name = request.POST.get('name')
  tags = request.POST.get('tags')
  access_policy = request.POST.get('access_policy')
  usrid = int(request.user.id)
  language= request.POST.get('lan')
  if get_type == "File":
    get_parent_node=collection.Node.one({'_id':ObjectId(node_id)})
    get_mime_type=get_parent_node.mime_type
    get_fs_file_ids=get_parent_node.fs_file_ids
    node.mime_type=get_mime_type
    node.fs_file_ids=get_fs_file_ids
 
  if not node.has_key('_id'):
    node.created_by = usrid
    if get_type == "File":
        get_node_type = collection.Node.one({'name':get_type})
        node.member_of.append(get_node_type._id)
        if 'image' in get_mime_type:
          get_image_type = collection.Node.one({'name':'Image'})
          node.member_of.append(get_image_type._id)
        if 'video' in get_mime_type:
          get_video_type = collection.Node.one({'name':'Video'})
          node.member_of.append(get_video_type._id)
        
    else:
      node.member_of.append(node_type._id)
 
  node.name = unicode(name)
  node.language=unicode(language)
 
  node.modified_by = usrid
  if access_policy:
    node.access_policy = access_policy
 
  if usrid not in node.contributors:
    node.contributors.append(usrid)

  group_obj=gcollection.Node.one({'_id':ObjectId(group_id)})
  if group_obj._id not in node.group_set:
    node.group_set.append(group_obj._id)
  if tags:
    node.tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]

  if tags:
    node.tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]

  if content_org:
    node.content_org = unicode(content_org)
    node.name=unicode(name)
    # Required to link temporary files with the current user who is modifying this document
    usrname = request.user.username
    filename = slugify(name) + "-" + usrname + "-" + ObjectId().__str__()
    node.content = org2html(content_org, file_prefix=filename)



def get_node_common_fields(request, node, group_id, node_type, coll_set=None):
  """Updates the retrieved values of common fields from request into the given node."""

  gcollection = db[Node.collection_name]
  group_obj=gcollection.Node.one({'_id':ObjectId(group_id)})
  theme_item_GST = gcollection.Node.one({'_type': 'GSystemType', 'name': 'theme_item'})
  topic_GST = gcollection.Node.one({'_type': 'GSystemType', 'name':'Topic'})
  collection = None

  if coll_set:
      if "Theme" in coll_set.member_of_names_list:
        node_type = theme_GST
      if "theme_item" in coll_set.member_of_names_list:
        node_type = theme_item_GST
      if "Topic" in coll_set.member_of_names_list:
        node_type = topic_GST
                                
      name = request.POST.get('name_'+ str(coll_set._id),"")
      content_org = request.POST.get(str(coll_set._id),"")
      tags = request.POST.get('tags'+ str(coll_set._id),"")
     
  else:    
    name =request.POST.get('name','')
    content_org = request.POST.get('content_org')
    tags = request.POST.get('tags')

  language= request.POST.get('lan')
  sub_theme_name = request.POST.get("sub_theme_name", '')
  add_topic_name = request.POST.get("add_topic_name", '')
  is_changed = False
  sub_theme_name = unicode(request.POST.get("sub_theme_name", ''))
  add_topic_name = unicode(request.POST.get("add_topic_name", ''))
  usrid = int(request.user.id)
  usrname = unicode(request.user.username)
  access_policy = request.POST.get("login-mode", '')
  right_drawer_list = []
  checked = request.POST.get("checked", '') 
  check_collection = request.POST.get("check_collection", '') 
  if check_collection:
    if check_collection == "collection":
      right_drawer_list = request.POST.get('collection_list','')
    elif check_collection == "prior_node":    
      right_drawer_list = request.POST.get('prior_node_list','')
    elif check_collection == "teaches":    
      right_drawer_list = request.POST.get('teaches_list','')
    elif check_collection == "assesses":    
      right_drawer_list = request.POST.get('assesses_list','')
    elif check_collection == "module":    
      right_drawer_list = request.POST.get('module_list','')


  map_geojson_data = request.POST.get('map-geojson-data')
  user_last_visited_location = request.POST.get('last_visited_location')
  altnames = request.POST.get('altnames', '')
  featured = request.POST.get('featured', '')

  if map_geojson_data:
    map_geojson_data = map_geojson_data + ","
    map_geojson_data = list(ast.literal_eval(map_geojson_data))
  else:
    map_geojson_data = []
  
  # --------------------------------------------------------------------------- For create only
  if not node.has_key('_id'):
    
    node.created_by = usrid
    
    if node_type._id not in node.member_of:
      node.member_of.append(node_type._id)
      if node_type.name == "Term":
        node.member_of.append(topic_GST._id)
        
     
    if group_obj._id not in node.group_set:
      node.group_set.append(group_obj._id)

    if access_policy == "PUBLIC":
      node.access_policy = unicode(access_policy)
    else:
      node.access_policy = unicode(access_policy)

    node.status = "PUBLISHED"

    is_changed = True
          
    # End of if
    specific_url = set_all_urls(node.member_of)
    node.url = specific_url

  if name:
    if node.name != name:
      node.name = name
      is_changed = True
  
  if altnames or request.POST.has_key("altnames"):
    if node.altnames != altnames:
      node.altnames = altnames
      is_changed = True

  if (featured == True) or (featured == False) :
    if node.featured != featured:
      node.featured = featured
      is_changed = True

  if sub_theme_name:
    if node.name != sub_theme_name:
      node.name = sub_theme_name
      is_changed = True
  
  if add_topic_name:
    if node.name != add_topic_name:
      node.name = add_topic_name
      is_changed = True

  #  language
  if language:
      node.language = unicode(language) 
  else:
      node.language = u"en"

  #  access_policy

  if access_policy:
    # Policy will be changed only by the creator of the resource
    # via access_policy(public/private) option on the template which is visible only to the creator
    if access_policy == "PUBLIC" and node.access_policy != access_policy:
        node.access_policy = u"PUBLIC"
        # print "\n Changed: access_policy (pu 2 pr)"
        is_changed = True
    elif access_policy == "PRIVATE" and node.access_policy != access_policy:
        node.access_policy = u"PRIVATE"
        # print "\n Changed: access_policy (pr 2 pu)"
        is_changed = True
  else:
      node.access_policy = u"PUBLIC"

  # For displaying nodes in home group as well as in creator group.
  user_group_obj=gcollection.Node.one({'$and':[{'_type':ObjectId(group_id)},{'name':usrname}]})

  if group_obj._id not in node.group_set:
      node.group_set.append(group_obj._id)
  else:
      if user_group_obj:
          if user_group_obj._id not in node.group_set:
              node.group_set.append(user_group_obj._id)

  #  tags
  if tags:
    tags_list = []

    for tag in tags.split(","):
      tag = unicode(tag.strip())

      if tag:
        tags_list.append(tag)

    if set(node.tags) != set(tags_list):
      node.tags = tags_list
      is_changed = True

  #  Build collection, prior node, teaches and assesses lists
  if check_collection:
    changed = build_collection(node, check_collection, right_drawer_list, checked)  
    if changed == True:
      is_changed = True
    
  #  org-content
  if content_org:
    if node.content_org != content_org:
      node.content_org = content_org
      
      # Required to link temporary files with the current user who is modifying this document
      usrname = request.user.username
      filename = slugify(name) + "-" + usrname + "-" + ObjectId().__str__()
      node.content = org2html(content_org, file_prefix=filename)
      is_changed = True

  # visited_location in author class
  if node.location != map_geojson_data:
    node.location = map_geojson_data # Storing location data
    is_changed = True
  
  if user_last_visited_location:
    user_last_visited_location = list(ast.literal_eval(user_last_visited_location))

    author = gcollection.Node.one({'_type': "GSystemType", 'name': "Author"})
    user_group_location = gcollection.Node.one({'_type': "Author", 'member_of': author._id, 'created_by': usrid, 'name': usrname})

    if user_group_location:
      if node._type == "Author" and user_group_location._id == node._id:
        if node['visited_location'] != user_last_visited_location:
          node['visited_location'] = user_last_visited_location
          is_changed = True

      else:
        user_group_location['visited_location'] = user_last_visited_location
        user_group_location.save()

  if is_changed:
    node.status = unicode("DRAFT")

    node.modified_by = usrid

    if usrid not in node.contributors:
      node.contributors.append(usrid)
  return is_changed
# ============= END of def get_node_common_fields() ==============
  
def build_collection(node, check_collection, right_drawer_list, checked):  
  
  is_changed = False
  gcollection = db[Node.collection_name]

  if check_collection == "prior_node":
    if right_drawer_list != '':
      # prior_node_list = [ObjectId(each.strip()) for each in prior_node_list.split(",")]
      right_drawer_list = [ObjectId(each.strip()) for each in right_drawer_list.split(",")]

      if node.prior_node != right_drawer_list:
        i = 0
        node.prior_node=[]
        while (i < len(right_drawer_list)):
          node_id = ObjectId(right_drawer_list[i])
          node_obj = gcollection.Node.one({"_id": node_id})
          if node_obj:
            node.prior_node.append(node_id)
          
          i = i+1
        # print "\n Changed: prior_node"
        is_changed = True
    else:
      node.prior_node = []
      is_changed = True

  elif check_collection == "collection":
    #  collection
    if right_drawer_list != '':
      right_drawer_list = [ObjectId(each.strip()) for each in right_drawer_list.split(",")]

      nlist = node.collection_set

      # if set(node.collection_set) != set(right_drawer_list):
      if node.collection_set != right_drawer_list:
        i = 0          
        node.collection_set = []
        # checking if each _id in collection_list is valid or not
        while (i < len(right_drawer_list)):
          node_id = ObjectId(right_drawer_list[i])
          node_obj = gcollection.Node.one({"_id": node_id})
          if node_obj:
            if node_id not in nlist:
              nlist.append(node_id)  
            else:
              node.collection_set.append(node_id)  
              # After adding it to collection_set also make the 'node' as prior node for added collection element
              gcollection.update({'_id': ObjectId(node_id), 'prior_node': {'$nin':[node._id]} },{'$push': {'prior_node': ObjectId(node._id)}})
          
          i = i+1

        for each in nlist:
          if each not in node.collection_set:
            node.collection_set.append(each)
            # After adding it to collection_set also make the 'node' as prior node for added collection element
            gcollection.update({'_id': ObjectId(each), 'prior_node': {'$nin':[node._id]} },{'$push': {'prior_node': ObjectId(node._id)}})

        # For removing collection elements from heterogeneous collection drawer only
        if not checked: 
          if nlist:
            for each in nlist:
              if each not in right_drawer_list:
                node.collection_set.remove(each)
                # Also for removing prior node element after removing collection element
                gcollection.update({'_id': ObjectId(each), 'prior_node': {'$in':[node._id]} },{'$pull': {'prior_node': ObjectId(node._id)}})

        else:
          if nlist and checked:
            if checked == "QuizObj":
              quiz = gcollection.Node.one({'_type': 'GSystemType', 'name': "Quiz" })
              quizitem = gcollection.Node.one({'_type': 'GSystemType', 'name': "QuizItem" })
              for each in nlist:
                obj = gcollection.Node.one({'_id': ObjectId(each) })
                if quiz._id in obj.member_of or quizitem._id in obj.member_of:
                  if obj._id not in right_drawer_list:
                    node.collection_set.remove(obj._id)
                    # Also for removing prior node element after removing collection element
                    gcollection.update({'_id': ObjectId(each), 'prior_node': {'$in':[node._id]} },{'$pull': {'prior_node': ObjectId(node._id)}})

            elif checked == "Pandora Video":
              check = gcollection.Node.one({'_type': 'GSystemType', 'name': 'Pandora_video' })
              for each in nlist:
                obj = gcollection.Node.one({'_id': ObjectId(each) })
                if check._id == obj.member_of[0]:
                  if obj._id not in right_drawer_list:
                    node.collection_set.remove(obj._id)
                    gcollection.update({'_id': ObjectId(each), 'prior_node': {'$in':[node._id]} },{'$pull': {'prior_node': ObjectId(node._id)}})
            else:
              check = gcollection.Node.one({'_type': 'GSystemType', 'name': unicode(checked) })
              for each in nlist:
                obj = gcollection.Node.one({'_id': ObjectId(each) })
                if len(obj.member_of) < 2:
                  if check._id == obj.member_of[0]:
                    if obj._id not in right_drawer_list:
                      node.collection_set.remove(obj._id)
                      gcollection.update({'_id': ObjectId(each), 'prior_node': {'$in':[node._id]} },{'$pull': {'prior_node': ObjectId(node._id)}})
                else:
                  if check._id == obj.member_of[1]: 
                    if obj._id not in right_drawer_list:
                      node.collection_set.remove(obj._id)
                      gcollection.update({'_id': ObjectId(each), 'prior_node': {'$in':[node._id]} },{'$pull': {'prior_node': ObjectId(node._id)}})


        is_changed = True
      
    else:
      if node.collection_set and checked:
        if checked == "QuizObj":
          quiz = gcollection.Node.one({'_type': 'GSystemType', 'name': "Quiz" })
          quizitem = gcollection.Node.one({'_type': 'GSystemType', 'name': "QuizItem" })
          for each in node.collection_set:
            obj = gcollection.Node.one({'_id': ObjectId(each) })
            if quiz._id in obj.member_of or quizitem._id in obj.member_of:
              node.collection_set.remove(obj._id)
              gcollection.update({'_id': ObjectId(each), 'prior_node': {'$in':[node._id]} },{'$pull': {'prior_node': ObjectId(node._id)}})
        elif checked == "Pandora Video":
          check = gcollection.Node.one({'_type': 'GSystemType', 'name': 'Pandora_video' })
          for each in node.collection_set:
            obj = gcollection.Node.one({'_id': ObjectId(each) })
            if check._id == obj.member_of[0]:
              node.collection_set.remove(obj._id)
              gcollection.update({'_id': ObjectId(each), 'prior_node': {'$in':[node._id]} },{'$pull': {'prior_node': ObjectId(node._id)}})
        else:
          check = gcollection.Node.one({'_type': 'GSystemType', 'name': unicode(checked) })
          for each in node.collection_set:
            obj = gcollection.Node.one({'_id': ObjectId(each) })
            if len(obj.member_of) < 2:
              if check._id == obj.member_of[0]:
                node.collection_set.remove(obj._id)
                gcollection.update({'_id': ObjectId(each), 'prior_node': {'$in':[node._id]} },{'$pull': {'prior_node': ObjectId(node._id)}})
            else:
              if check._id == obj.member_of[1]: 
                node.collection_set.remove(obj._id)
                gcollection.update({'_id': ObjectId(each), 'prior_node': {'$in':[node._id]} },{'$pull': {'prior_node': ObjectId(node._id)}})

      else:
        node.collection_set = []
      
      is_changed = True

  elif check_collection == "teaches":
    # Teaches
    if right_drawer_list != '':

      right_drawer_list = [ObjectId(each.strip()) for each in right_drawer_list.split(",")]

      relationtype = gcollection.Node.one({"_type":"RelationType","name":"teaches"})
      list_grelations = gcollection.Node.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
      for relation in list_grelations:
        # nlist.append(ObjectId(relation.right_subject))
        relation.delete()

      if right_drawer_list:
        list_grelations.rewind()
        i = 0

        while (i < len(right_drawer_list)):
          node_id = ObjectId(right_drawer_list[i])
          node_obj = gcollection.Node.one({"_id": node_id})
          if node_obj:
            create_grelation(node._id,relationtype,node_id)
          i = i+1      
        
        # print "\n Changed: teaches_list"
        is_changed = True
    else:
      relationtype = gcollection.Node.one({"_type":"RelationType","name":"teaches"})
      list_grelations = gcollection.Node.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
      for relation in list_grelations:
        relation.delete()

      is_changed = True

  elif check_collection == "assesses":
    # Assesses
    if right_drawer_list != '':
      right_drawer_list = [ObjectId(each.strip()) for each in right_drawer_list.split(",")]

      relationtype = gcollection.Node.one({"_type":"RelationType","name":"assesses"})
      list_grelations = gcollection.Node.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
      for relation in list_grelations:
        relation.delete()

      if right_drawer_list:
        list_grelations.rewind()
        i = 0

        while (i < len(right_drawer_list)):
          node_id = ObjectId(right_drawer_list[i])
          node_obj = gcollection.Node.one({"_id": node_id})
          if node_obj:
            create_grelation(node._id,relationtype,node_id)            
          i = i+1      

        # print "\n Changed: teaches_list"
        is_changed = True
    else:
      relationtype = gcollection.Node.one({"_type":"RelationType","name":"assesses"})
      list_grelations = gcollection.Node.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
      for relation in list_grelations:
        relation.delete()
      
      is_changed = True

  # elif check_collection == "module":
    #  Module
    # if right_drawer_list != '':
    #   right_drawer_list = [ObjectId(each.strip()) for each in right_drawer_list.split(",")]

    #   if set(node.collection_set) != set(right_drawer_list):
    #     i = 0
    #     while (i < len(right_drawer_list)):
    #       node_id = ObjectId(right_drawer_list[i])
    #       node_obj = gcollection.Node.one({"_id": node_id})
    #       if node_obj:
    #         if node_id not in node.collection_set:
    #           node.collection_set.append(node_id)
          
    #       i = i+1
        # print "\n Changed: module_list"
        # is_changed = True
    # else:
      # node.module_set = []
      # is_changed = True
  if is_changed == True:
    return True
  else:
    return False

def get_versioned_page(node):
            
    rcs = RCS()
    fp = history_manager.get_file_path(node)
    cmd= 'rlog  %s' % \
  (fp)
    rev_no =""
    proc1=subprocess.Popen(cmd,shell=True,
        stdout=subprocess.PIPE)
    for line in iter(proc1.stdout.readline,b''):
       
      if line.find('revision')!=-1 and line.find('selected') == -1:
          rev_no=string.split(line,'revision')
          rev_no=rev_no[1].strip( '\t\n\r')
          rev_no=rev_no.split()[0]
      if line.find('status')!=-1:
          up_ind=line.find('status')
          if line.find(('PUBLISHED'),up_ind) !=-1:
	       rev_no=rev_no.split()[0]
               node=history_manager.get_version_document(node,rev_no)
               proc1.kill()
               return (node,rev_no)    
      if rev_no == '1.1':
           node=history_manager.get_version_document(node,'1.1')
           proc1.kill()
           return(node,'1.1')
        

def get_user_page(request,node):
    ''' function gives the last docment submited by the currently logged in user either it
	can be drafted or published
'''
    rcs = RCS()
    fp = history_manager.get_file_path(node)
    cmd= 'rlog  %s' % \
	(fp)
    rev_no =""
    proc1=subprocess.Popen(cmd,shell=True,
				stdout=subprocess.PIPE)
    for line in iter(proc1.stdout.readline,b''):
       
       if line.find('revision')!=-1 and line.find('selected') == -1:

          rev_no=string.split(line,'revision')
          rev_no=rev_no[1].strip( '\t\n\r')
          rev_no=rev_no.strip(' ')
       if line.find('updated')!=-1:
          up_ind=line.find('updated')
          if line.find(str(request.user),up_ind) !=-1:
               rev_no=rev_no.strip(' ')
               node=history_manager.get_version_document(node,rev_no)
               proc1.kill()
               return (node,rev_no)    
       if rev_no == '1.1':
           node=history_manager.get_version_document(node,'1.1')
           proc1.kill()
           return(node,'1.1')
                   
def get_page(request,node):
  ''' 
  function to filter between the page to be displyed to user 
  i.e which page to be shown to the user drafted or the published page
  if a user have some drafted content then he would be shown his own drafted contents 
  and if he has published his contents then he would be shown the current published contents
  '''
  username =request.user
  node1,ver1=get_versioned_page(node)
  node2,ver2=get_user_page(request,node)     
  
  if  ver2 != '1.1':                           
	    if node2 is not None:
                if node2.status == 'PUBLISHED':
                  
			if float(ver2) > float(ver1):			
				return (node2,ver2)
			elif float(ver2) < float(ver1):
				return (node1,ver1)
			elif float(ver2) == float(ver1):
				return(node1,ver1)
		elif node2.status == 'DRAFT':
                       #========== conditions for Group===============#

                        if   node._type == "Group":
			    
			    count=check_page_first_creation(request,node2)
                            if count == 1:
                                return (node1,ver1)
                            elif count == 2:
                               	return (node2,ver2)
                        
                        return (node2,ver2)  
	    else:
                        
			return(node1,ver1)		
	    
  else:
         
        # if node._type == "GSystem" and node1.status == "DRAFT":
        #     if node1.created_by ==request.user.id:
        #           return (node2,ver2)
        #      else:
	#	   return (node2,ver2)
         return (node1,ver1)
	 
def check_page_first_creation(request,node):
    ''' function to check wheather the editing is performed by the user very first time '''
    rcs = RCS()
    fp = history_manager.get_file_path(node)
    cmd= 'rlog  %s' % \
	(fp)
    rev_no =""
    count=0
    proc1=subprocess.Popen(cmd,shell=True,
				stdout=subprocess.PIPE)
    for line in iter(proc1.stdout.readline,b''):
         if line.find('updated')!=-1 or line.find('created')!=-1:
          if line.find(str(request.user))!=-1:
               count =count+1
               if count ==2:
                proc1.kill()
               	return (count)
    proc1.kill()
    if count == 1:
	return(count)     
      

def tag_info(request, group_id, tagname):
  '''
  Function to get all the resources related to tag
  '''


  return render_to_response("ndf/tag_browser.html", {'group_id': group_id, 'groupid': group_id }, context_instance=RequestContext(request))


#code for merging two text Documents
import difflib
def diff_string(original,revised):
        
        # build a list of sentences for each input string
        original_text = _split_with_maintain(original)
        new_text = _split_with_maintain(revised)
        a=original_text + new_text
        strings='\n'.join(a)
        #f=(strings.replace("*", ">").replace("-","="))
        #f=(f.replace("> 1 >",">").replace("= 1 =","="))

        
        return strings
STANDARD_REGEX = '[.!?]'
def _split_with_maintain(value, treat_trailing_spaces_as_sentence = True, split_char_regex = STANDARD_REGEX):
        result = []
        check = value
        
        # compile regex
        rx = re.compile(split_char_regex)
        
        # traverse the string
        while len(check) > 0:
            found  = rx.search(str(check))
            if found == None:
                result.append(check)
                break
            
            idx = found.start()
            result.append(str(check[:idx]))            # append the string
            result.append(str(check[idx:idx+1]))    # append the puncutation so changing ? to . doesn't invalidate the whole sentence
            check = check[idx + 1:]
            
            # group the trailing spaces if requested
            if treat_trailing_spaces_as_sentence:
                space_idx = 0
                while True:
                    if space_idx >= len(check):
                        break
                    if check[space_idx] != " ":
                        break
                    space_idx += 1
                
                if space_idx != 0:
                    result.append(check[0:space_idx])
            
                check = check[space_idx:]
            
        return result

def update_mobwrite_content_org(node_system):   
  '''
	on revert or merge of nodes,a content_org is synced to mobwrite object
	input : 
		node
  ''' 
  system = node_system
  filename = TextObj.safe_name(str(system._id))
  textobj = TextObj.objects.filter(filename=filename)
  content_org = system.content_org
  if textobj:
    textobj = TextObj.objects.get(filename=filename)
    textobj.text = content_org
    textobj.save()
  else:
    textobj = TextObj(filename=filename,text=content_org)
    textobj.save()
  return textobj


def get_node_metadata(request, node, **kwargs):
    '''
    Getting list of updated GSystems with kwargs arguments.
    Pass is_changed=True as last/fourth argument while calling this/get_node_metadata method.
    Example: 
      updated_ga_nodes = get_node_metadata(request, node_obj, GST_FILE_OBJ, is_changed=True)

    '''
    attribute_type_list = ["age_range", "audience", "timerequired",
                           "interactivitytype", "basedonurl", "educationaluse",
                           "textcomplexity", "readinglevel", "educationalsubject",
                           "educationallevel", "curricular", "educationalalignment",
                           "adaptation_of", "other_contributors", "creator", "source"
                          ]

    if kwargs.has_key("is_changed"):
        updated_ga_nodes = []

    if(node.has_key('_id')):

        for atname in attribute_type_list:

            field_value = unicode(request.POST.get(atname, ""))
            at = collection.Node.one({"_type": "AttributeType", "name": atname})	

            if at and field_value:

                if kwargs.has_key("is_changed"):
                    temp_res = create_gattribute(node._id, at, field_value, is_changed=True)
                    if temp_res["is_changed"]:  # if value is true
                        updated_ga_nodes.append(temp_res)
              
                else:
                    create_gattribute(node._id, at, field_value)
    
    if kwargs.has_key("is_changed"):
        return updated_ga_nodes


def create_grelation_list(subject_id, relation_type_name, right_subject_id_list):
# function to create grelations for new ones and delete old ones.
	relationtype = collection.Node.one({"_type":"RelationType","name":unicode(relation_type_name)})
	#list_current_grelations = collection.Node.find({"_type":"GRelation","subject":subject_id,"relation_type":relationtype})
	#removes all existing relations given subject and relation type and then creates again.
	collection.remove({"_type":"GRelation","subject":subject_id,"relation_type":relationtype.get_dbref()})

	
	
	for relation_id in right_subject_id_list:
	    
	    gr_node = collection.GRelation()
            gr_node.subject = ObjectId(subject_id)
            gr_node.relation_type = relationtype
            gr_node.right_subject = ObjectId(relation_id)
	    gr_node.status = u"PUBLISHED"
            gr_node.save()
		
def get_widget_built_up_data(at_rt_objectid_or_attr_name_list, node, type_of_set=[]):
  """
  Returns data in list of dictionary format which is required for building html widget.
  This data is used by html_widget template-tag.
  """
  if not isinstance(at_rt_objectid_or_attr_name_list, list):
    at_rt_objectid_or_attr_name_list = [at_rt_objectid_or_attr_name_list]

  if not type_of_set:
    node["property_order"] = []
    gst_nodes = collection.Node.find({'_type': "GSystemType", '_id': {'$in': node["member_of"]}}, {'type_of': 1, 'property_order': 1})
    for gst in gst_nodes:
      for type_of in gst["type_of"]:
        if type_of not in type_of_set:
          type_of_set.append(type_of)

      for po in gst["property_order"]:
        if po not in node["property_order"]:
          node["property_order"].append(po)

  BASE_FIELD_METADATA = {
    'name': {'name': "name", '_type': "BaseField", 'altnames': "Name", 'required': True},
    'content_org': {'name': "content_org", '_type': "BaseField", 'altnames': "Describe", 'required': False},
    # 'featured': {'name': "featured", '_type': "BaseField", 'altnames': "Featured"},
    'location': {'name': "location", '_type': "BaseField", 'altnames': "Location", 'required': False},
    'status': {'name': "status", '_type': "BaseField", 'altnames': "Status", 'required': False},
    'tags': {'name': "tags", '_type': "BaseField", 'altnames': "Tags", 'required': False}
  }

  widget_data_list = []
  for at_rt_objectid_or_attr_name in at_rt_objectid_or_attr_name_list:
    if type(at_rt_objectid_or_attr_name) == ObjectId: #ObjectId.is_valid(at_rt_objectid_or_attr_name):
      # For attribute-field(s) and/or relation-field(s)
      
      field = collection.Node.one({'_id': ObjectId(at_rt_objectid_or_attr_name)}, {'_type': 1, 'subject_type': 1, 'object_type': 1, 'name': 1, 'altnames': 1, 'inverse_name': 1})

      altnames = u""
      value = None
      data_type = None
      if field._type == RelationType or field._type == "RelationType":
        # For RelationTypes
        if set(node["member_of"]).issubset(field.subject_type):
          # It means we are dealing with normal relation & 
          data_type = node.structure[field.name]
          value = node[field.name]
          if field.altnames:
            if ";" in field.altnames:
              altnames = field.altnames.split(";")[0]
            else:
              altnames = field.altnames

        elif set(node["member_of"]).issubset(field.object_type):
          # It means we are dealing with inverse relation
          data_type = node.structure[field.inverse_name]
          value = node[field.inverse_name]
          if field.altnames:
            if ";" in field.altnames:
              altnames = field.altnames.split(";")[1]
            else:
              altnames = field.altnames

        elif type_of_set:
          # If current node's GST is not in subject_type
          # Search for that GST's type_of field value in subject_type
          for each in type_of_set:
            if each in field.subject_type:
              data_type = node.structure[field.name]
              value = node[field.name]
              if field.altnames:
                if ";" in field.altnames:
                  altnames = field.altnames.split(";")[0]
                else:
                  altnames = field.altnames

            elif each in field.object_type:
              data_type = node.structure[field.inverse_name]
              value = node[field.inverse_name]
              if field.altnames:
                if ";" in field.altnames:
                  altnames = field.altnames.split(";")[0]
                else:
                  altnames = field.altnames

      else:
        # For AttributeTypes
        altnames = field.altnames
        data_type = node.structure[field.name]
        value = node[field.name]

      widget_data_list.append({ '_type': field._type, # It's only use on details-view template; overridden in ndf_tags html_widget()
                              '_id': field._id, 
                              'data_type': data_type,
                              'name': field.name, 'altnames': altnames,
                              'value': value
                            })

    else:
      # For node's base-field(s)

      # widget_data_list.append([node['member_of'], BASE_FIELD_METADATA[at_rt_objectid_or_attr_name], node[at_rt_objectid_or_attr_name]])
      widget_data_list.append({ '_type': BASE_FIELD_METADATA[at_rt_objectid_or_attr_name]['_type'],
                              'data_type': node.structure[at_rt_objectid_or_attr_name],
                              'name': at_rt_objectid_or_attr_name, 'altnames': BASE_FIELD_METADATA[at_rt_objectid_or_attr_name]['altnames'],
                              'value': node[at_rt_objectid_or_attr_name],
                              'required': BASE_FIELD_METADATA[at_rt_objectid_or_attr_name]['required']
                            })

  return widget_data_list


def get_property_order_with_value(node):
  new_property_order = []
  demo = None

  if node.has_key('_id'):
    demo = collection.Node.one({'_id': node._id})

  else:
    demo = eval("collection"+"."+node['_type'])()
    demo["member_of"] = node["member_of"]

  if demo["_type"] not in ["MetaType", "GSystemType", "AttributeType", "RelationType"]:
    # If GSystems found, then only perform following statements
    
    demo["property_order"] = []
    type_of_set = []
    gst_nodes = collection.Node.find({'_type': "GSystemType", '_id': {'$in': demo["member_of"]}}, {'type_of': 1, 'property_order': 1})
    for gst in gst_nodes:
      for type_of in gst["type_of"]:
        if type_of not in type_of_set:
          type_of_set.append(type_of)

      for po in gst["property_order"]:
        if po not in demo["property_order"]:
          demo["property_order"].append(po)

    demo.get_neighbourhood(node["member_of"])

    for tab_name, list_field_id_or_name in demo['property_order']:
      list_field_set = get_widget_built_up_data(list_field_id_or_name, demo, type_of_set)
      new_property_order.append([tab_name, list_field_set])

    demo["property_order"] = new_property_order
  
  else:
    # Otherwise (if GSystemType found) depending upon whether type_of exists or not returns property_order.
    if not demo["property_order"] and demo.has_key("_id"):
      type_of_nodes = collection.Node.find({'_type': "GSystemType", '_id': {'$in': demo["type_of"]}}, {'property_order': 1})
      
      if type_of_nodes.count():
        demo["property_order"] = []
        for to in type_of_nodes:
          for po in to["property_order"]:
            demo["property_order"].append(po)

      collection.update({'_id': demo._id}, {'$set': {'property_order': demo["property_order"]}}, upsert=False, multi=False)

  new_property_order = demo['property_order']

  if demo.has_key('_id'):
    node = collection.Node.one({'_id': demo._id})

  else:
    node = eval("collection"+"."+demo['_type'])()
    node["member_of"] = demo["member_of"]
  
  node['property_order'] = new_property_order

  return node['property_order']


def parse_template_data(field_data_type, field_value, **kwargs):
  """
  Parses the value fetched from request (GET/POST) object based on the data-type of the given field.

  Arguments:
  field_data_type -- data-type of the field
  field_value -- value of the field retrieved from GET/POST object

  Returns:
  Parsed value based on the data-type of the field
  """

  '''
  kwargs_keys_list = [
                    "date_format_string",     # date-format in string representation
                    "field_instance"          # dict-object reperesenting AT/RT node
                  ]
  '''
  DATA_TYPE_STR_CHOICES = [
                          "unicode", "basestring",
                          "int", "float", "long",
                          "list", "dict",
                          "datetime",
                          "bool",
                          "ObjectId"
                        ]
  try:
    if type(field_data_type) == type:
      field_data_type = field_data_type.__name__

      if not field_value:
        if field_data_type == "dict":
          return {}

        elif field_data_type == "list":
          return []

        else:
          return None

      if field_data_type == "unicode":
        field_value = unicode(field_value)

      elif field_data_type == "basestring":
        field_value = field_value

      elif field_data_type == "int":
        field_value = int(field_value)

      elif field_data_type == "float":
        field_value = float(field_value)

      elif field_data_type == "long":
        field_value = long(field_value)

      elif field_data_type == "list":
        if ("[" in field_value) and ("]" in field_value):
          field_value = json.loads(field_value)

        else:
          lr = field_value.replace(" ,", ",")
          rr = lr.replace(", ", ",")
          field_value = rr.split(",")

      elif field_data_type == "dict":
        field_value = "???"

      elif field_data_type == "datetime":
        field_value = datetime.strptime(field_value, kwargs["date_format_string"])

      elif field_data_type == "bool":
        if field_value == "Yes" or field_value == "yes" or field_value == "1":
          if field_value == "1":
            field_value = bool(int(field_value))
          else:
            field_value = True
        
        elif field_value == "No" or field_value == "no" or field_value == "0":
          if field_value == "0":
            field_value = bool(int(field_value))
          else:
            field_value = False

      elif field_data_type == "ObjectId":
        field_value = ObjectId(field_value)

      else:
        error_message = "Unknown data-type ("+field_data_type+") found"
        raise Exception(error_message)

    elif type(field_data_type) == list:

      if kwargs.has_key("field_instance"):
        if kwargs["field_instance"]["_type"] == RelationType or kwargs["field_instance"]["_type"] == "RelationType":
          # Write RT related code 
          if not field_value:
            return None
          if field_value:
            field_value = ObjectId(field_value)

          else:
            error_message = "This ObjectId("+field_type+") doesn't exists"
            raise Exception(error_message)

      else:
        if not field_value:
          return []

        if ("[" in field_value) and ("]" in field_value):
          field_value = json.loads(field_value)

        else:
          lr = field_value.replace(" ,", ",")
          rr = lr.replace(", ", ",")
          field_value = rr.split(",")

        return field_value

    elif type(field_data_type) == dict:
      # Write code...
      if not field_value:
        return {}

    elif type(field_data_type) == mongokit.operators.IS:
      # Write code...
      if not field_value:
        return None

      field_value = unicode(field_value) if type(field_value) != unicode else field_value

    elif type(field_data_type) == mongokit.document.R:
      # Write code...
      if kwargs["field_instance"]["_type"] == AttributeType or kwargs["field_instance"]["_type"] == "AttributeType":
        # Write AT related code 
        if not field_value:
          if field_data_type == "dict":
            return {}

          elif field_data_type == "list":
            return []

          else:
            return None

      else:
        error_message = "Neither AttributeType nor RelationType found"
        raise Exception(error_message)

    else:
      error_message = "Unknown data-type found"
      raise Exception(error_message)

    return field_value
  
  except Exception as e:
    error_message = "\n TemplateDataParsingError: "+str(e)+" !!!\n"
    raise Exception(error_message)

def create_gattribute(subject_id, attribute_type_node, object_value, **kwargs):

  ga_node = None
  info_message = ""
  old_object_value = None

  ga_node = collection.Triple.one({'_type': "GAttribute", 'subject': subject_id, 'attribute_type.$id': attribute_type_node._id})
  if ga_node is None:
    # Code for creation
    try:
      ga_node = collection.GAttribute()

      ga_node.subject = subject_id
      ga_node.attribute_type = attribute_type_node

      if (not object_value) and type(object_value) != bool:
        object_value = u"None"
        ga_node.status = u"DELETED"

      else:
        ga_node.status = u"PUBLISHED"

      ga_node.object_value = object_value
      ga_node.save()

      if object_value == u"None":
        info_message = " GAttribute ("+ga_node.name+") created successfully with status as 'DELETED'!\n"

      else:
        info_message = " GAttribute ("+ga_node.name+") created successfully.\n"

        # Fetch corresponding document & append into it's attribute_set
        collection.update({'_id': subject_id}, 
                          {'$addToSet': {'attribute_set': {attribute_type_node.name: object_value}}}, 
                          upsert=False, multi=False
                        )

      is_ga_node_changed = True

    except Exception as e:
      error_message = "\n GAttributeCreateError: " + str(e) + "\n"
      raise Exception(error_message)

  else:
    # Code for updation
    is_ga_node_changed = False
    
    try:
      if (not object_value) and type(object_value) != bool:
        old_object_value = ga_node.object_value

        ga_node.status = u"DELETED"
        ga_node.save()
        info_message = " GAttribute ("+ga_node.name+") status updated from 'PUBLISHED' to 'DELETED' successfully.\n"

        # Fetch corresponding document & update it's attribute_set with proper value
        collection.update({'_id': subject_id, 'attribute_set.'+attribute_type_node.name: old_object_value}, 
                          {'$pull': {'attribute_set': {attribute_type_node.name: old_object_value}}}, 
                          upsert=False, multi=False)

      else:
        if type(ga_node.object_value) == list:
          if type(ga_node.object_value[0]) == dict:
            old_object_value = ga_node.object_value

            if len(old_object_value) != len(object_value):
              ga_node.object_value = object_value
              is_ga_node_changed = True

            else:
              pairs = zip(old_object_value, object_value)
              if any(x != y for x, y in pairs):
                ga_node.object_value = object_value
                is_ga_node_changed = True

          elif set(ga_node.object_value) != set(object_value):
            old_object_value = ga_node.object_value
            ga_node.object_value = object_value
            is_ga_node_changed = True

        elif type(ga_node.object_value) == dict:
          if cmp(ga_node.object_value, object_value) != 0:
            old_object_value = ga_node.object_value
            ga_node.object_value = object_value
            is_ga_node_changed = True

        else:
          if ga_node.object_value != object_value:
            old_object_value = ga_node.object_value
            ga_node.object_value = object_value
            is_ga_node_changed = True

        if is_ga_node_changed:
          if ga_node.status == u"DELETED":
            ga_node.status = u"PUBLISHED"
            ga_node.save()

            info_message = " GAttribute ("+ga_node.name+") status updated from 'DELETED' to 'PUBLISHED' successfully.\n"

            # Fetch corresponding document & append into it's attribute_set
            collection.update({'_id': subject_id}, 
                              {'$addToSet': {'attribute_set': {attribute_type_node.name: object_value}}}, 
                              upsert=False, multi=False)

          else:
            ga_node.status = u"PUBLISHED"
            ga_node.save()

            info_message = " GAttribute ("+ga_node.name+") updated successfully.\n"

            # Fetch corresponding document & update it's attribute_set with proper value
            collection.update({'_id': subject_id, 'attribute_set.'+attribute_type_node.name: old_object_value}, 
                              {'$set': {'attribute_set.$.'+attribute_type_node.name: ga_node.object_value}}, 
                              upsert=False, multi=False)
        else:
          info_message = " GAttribute ("+ga_node.name+") already exists (Nothing updated) !\n"

    except Exception as e:
      error_message = "\n GAttributeUpdateError: " + str(e) + "\n"
      raise Exception(error_message)

  # print "\n\t is_ga_node_changed: ", is_ga_node_changed
  if kwargs.has_key("is_changed"):
    ga_dict = {}
    ga_dict["is_changed"] = is_ga_node_changed
    ga_dict["node"] = ga_node
    ga_dict["before_obj_value"] = old_object_value
    return ga_dict
  else:
    return ga_node


def create_grelation(subject_id, relation_type_node, right_subject_id_or_list, **kwargs):
  """Creates single or multiple GRelation documents (instances) based on given 
  RelationType's cardinality (one-to-one / one-to-many).

  Arguments:
  subject_id -- ObjectId of the subject-node
  relation_type_node -- Document of the RelationType node (Embedded document)
  right_subject_id_or_list -- 
    - When one to one relationship: Single ObjectId of the right_subject node
    - When one to many relationship: List of ObjectId(s) of the right_subject node(s)

  Returns:
  - When one to one relationship: Created/Updated/Existed document.
  - When one to many relationship: Created/Updated/Existed list of documents.
  
  """
  gr_node = None
  multi_relations = False

  try:
    subject_id = ObjectId(subject_id)

    if relation_type_node["object_cardinality"]:
      # If object_cardinality value exists and greater than 1 (or eaqual to 100)
      # Then it signifies it's a one to many type of relationship
      # assign multi_relations = True
      if relation_type_node["object_cardinality"] > 1:
        multi_relations = True

        # Check whether right_subject_id_or_list is list or not
        # If not convert it to list
        if not isinstance(right_subject_id_or_list, list):
          right_subject_id_or_list = [right_subject_id_or_list]

        # Check whether all values of a list are of ObjectId data-type or not 
        # If not convert them to ObjectId
        for i, each in enumerate(right_subject_id_or_list):
          right_subject_id_or_list[i] = ObjectId(each)


    if multi_relations:
      # For dealing with multiple relations (one to many)

      # Iterate and find all relationships (including DELETED ones' also)
      nodes = collection.Triple.find({'_type': "GRelation", 
                                      'subject': subject_id, 
                                      'relation_type.$id': relation_type_node._id
                                    })

      gr_node_list = []

      for n in nodes:
        if n.right_subject in right_subject_id_or_list:
          if n.status != u"DELETED":
            # If match found with existing one's, then only remove that ObjectId from the given list of ObjectIds
            # Just to remove already existing entries (whose status is PUBLISHED)
            right_subject_id_or_list.remove(n.right_subject)
            gr_node_list.append(n)

            collection.update({'_id': subject_id, 'relation_set.'+relation_type_node.name: {'$exists': True}}, 
                              {'$addToSet': {'relation_set.$.'+relation_type_node.name: n.right_subject}}, 
                              upsert=False, multi=False
                            )

        else:
          # Case: When already existing entry doesn't exists in newly come list of right_subject(s)
          # So change their status from PUBLISHED to DELETED
          n.status = u"DELETED"
          n.save()
          info_message = " MultipleGRelation: GRelation ("+n.name+") status updated from 'PUBLISHED' to 'DELETED' successfully.\n"

          collection.update({'_id': subject_id, 'relation_set.'+relation_type_node.name: {'$exists': True}}, 
                            {'$pull': {'relation_set.$.'+relation_type_node.name: n.right_subject}}, 
                            upsert=False, multi=False
                          )

      if right_subject_id_or_list:
        # If still ObjectId list persists, it means either they are new ones' or from deleted ones'
        # For deleted one's, find them and modify their status to PUBLISHED
        # For newer one's, create them as new document
        for nid in right_subject_id_or_list:
          gr_node = collection.Triple.one({'_type': "GRelation", 
                                            'subject': subject_id, 
                                            'relation_type.$id': relation_type_node._id,
                                            'right_subject': nid
                                          })

          if gr_node is None:
            # New one found so create it
            gr_node = collection.GRelation()

            gr_node.subject = subject_id
            gr_node.relation_type = relation_type_node
            gr_node.right_subject = nid

            gr_node.status = u"PUBLISHED"
            gr_node.save()
            info_message = " MultipleGRelation: GRelation ("+gr_node.name+") created successfully.\n"

            left_subject = collection.Node.one({'_id': subject_id}, {'relation_set': 1})

            rel_exists = False
            for each_dict in left_subject.relation_set:
              if relation_type_node.name in each_dict:
                rel_exists = True
                break

            if not rel_exists:
              # Fetch corresponding document & append into it's relation_set
              collection.update({'_id': subject_id}, 
                                {'$addToSet': {'relation_set': {relation_type_node.name: [nid]}}}, 
                                upsert=False, multi=False
                              )
            else:
              collection.update({'_id': subject_id, 'relation_set.'+relation_type_node.name: {'$exists': True}}, 
                                {'$addToSet': {'relation_set.$.'+relation_type_node.name: nid}}, 
                                upsert=False, multi=False
                              )

            gr_node_list.append(gr_node)

          else:
            # Deleted one found so change it's status back to Published
            if gr_node.status == u'DELETED':
              gr_node.status = u"PUBLISHED"
              gr_node.save()

              info_message = " MultipleGRelation: GRelation ("+gr_node.name+") status updated from 'DELETED' to 'PUBLISHED' successfully.\n"

              collection.update({'_id': subject_id, 'relation_set.'+relation_type_node.name: {'$exists': True}}, 
                                {'$addToSet': {'relation_set.$.'+relation_type_node.name: gr_node.right_subject}}, 
                                upsert=False, multi=False
                              )

              gr_node_list.append(gr_node)

            else:
              error_message = " MultipleGRelation: Corrupt value found - GRelation ("+gr_node.name+")!!!\n"
              raise Exception(error_message)

      return gr_node_list

    else:
      # For dealing with single relation (one to one)
      gr_node = None

      if isinstance(right_subject_id_or_list, list):
        right_subject_id_or_list = ObjectId(right_subject_id_or_list[0])

      else:
        right_subject_id_or_list = ObjectId(right_subject_id_or_list)

      gr_node_cur = collection.Triple.find({'_type': "GRelation", 
                                            'subject': subject_id, 
                                            'relation_type.$id': relation_type_node._id
                                          })

      for node in gr_node_cur:
        if node.right_subject == right_subject_id_or_list:
          # If match found, it means it could be either DELETED one or PUBLISHED one

          if node.status == u"DELETED":
            # If deleted, change it's status back to Published from Deleted
            node.status = u"PUBLISHED"
            node.save()
            info_message = " SingleGRelation: GRelation ("+node.name+") status updated from 'DELETED' to 'PUBLISHED' successfully.\n"

            collection.update(
              {'_id': subject_id, 'relation_set.'+relation_type_node.name: {'$exists': True}}, 
              {'$addToSet': {'relation_set.$.'+relation_type_node.name: node.right_subject}}, 
              upsert=False, multi=False
            )

          elif node.status == u"PUBLISHED":
            collection.update(
              {'_id': subject_id, 'relation_set.'+relation_type_node.name: {'$exists': True}}, 
              {'$addToSet': {'relation_set.$.'+relation_type_node.name: node.right_subject}}, 
              upsert=False, multi=False
            )
            info_message = " SingleGRelation: GRelation ("+node.name+") already exists !\n"

          # Set gr_node value as matched value, so that no need to create new one
          node.reload()
          gr_node = node

        else:
          # If match not found and if it's PUBLISHED one, modify it to DELETED
          if node.status == u'PUBLISHED':
            node.status = u"DELETED"
            node.save()

            collection.update({'_id': subject_id, 'relation_set.'+relation_type_node.name: {'$exists': True}}, 
                              {'$pull': {'relation_set.$.'+relation_type_node.name: node.right_subject}}, 
                              upsert=False, multi=False
                            )
            info_message = " SingleGRelation: GRelation ("+node.name+") status updated from 'DELETED' to 'PUBLISHED' successfully.\n"
          
          elif node.status == u'DELETED':
            collection.update({'_id': subject_id, 'relation_set.'+relation_type_node.name: {'$exists': True}}, 
                              {'$pull': {'relation_set.$.'+relation_type_node.name: node.right_subject}}, 
                              upsert=False, multi=False
                            )
            info_message = " SingleGRelation: GRelation ("+node.name+") status updated from 'DELETED' to 'PUBLISHED' successfully.\n"

      if gr_node is None:
        # Code for creation
        gr_node = collection.GRelation()

        gr_node.subject = subject_id
        gr_node.relation_type = relation_type_node
        gr_node.right_subject = right_subject_id_or_list

        gr_node.status = u"PUBLISHED"
        
        gr_node.save()
        info_message = " GRelation ("+gr_node.name+") created successfully.\n"

        left_subject = collection.Node.one({'_id': subject_id}, {'relation_set': 1})

        rel_exists = False
        for each_dict in left_subject.relation_set:
          if relation_type_node.name in each_dict:
            rel_exists = True
            break

        if not rel_exists:
          # Fetch corresponding document & append into it's relation_set
          collection.update({'_id': subject_id}, 
                            {'$addToSet': {'relation_set': {relation_type_node.name: [right_subject_id_or_list]}}}, 
                            upsert=False, multi=False
                          )

        else:
          collection.update({'_id': subject_id, 'relation_set.'+relation_type_node.name: {'$exists': True}}, 
                            {'$addToSet': {'relation_set.$.'+relation_type_node.name: right_subject_id_or_list}}, 
                            upsert=False, multi=False
                          )

      return gr_node

  except Exception as e:
      error_message = "\n GRelationError: " + str(e) + "\n"
      raise Exception(error_message)

      

      
###############################################      ###############################################
def set_all_urls(member_of):
	Gapp_obj = collection.Node.one({"_type":"MetaType", "name":"GAPP"})
	factory_obj = collection.Node.one({"_type":"MetaType", "name":"factory_types"})

	url = ""	
	gsType = member_of[0]
	gsType_obj = collection.Node.one({"_id":ObjectId(gsType)})
	
	if Gapp_obj._id in gsType_obj.member_of:
		if gsType_obj.name == u"Quiz":
		    url = u"quiz/details"
		else:
		    url = gsType_obj.name.lower()
	elif factory_obj._id in gsType_obj.member_of:
		if gsType_obj.name == u"QuizItem":
		    url = u"quiz/details"
		elif gsType_obj.name == u"Twist":
		    url = u"forum/thread"
		else:
		    url = gsType_obj.name.lower()
	else:
		url = u"None"
	return url
###############################################	###############################################    


# Method to create discussion thread for File and Page.
@login_required
def create_discussion(request, group_id, node_id):
  '''
  Method to create discussion thread for File and Page.
  '''

  try:

    twist_st = collection.Node.one({'_type':'GSystemType', 'name':'Twist'})

    node = collection.Node.one({'_id': ObjectId(node_id)})

    # group = collection.Group.one({'_id':ObjectId(group_id)})

    thread = collection.Node.one({ "_type": "GSystem", "name": node.name, "member_of": ObjectId(twist_st._id), "prior_node": ObjectId(node_id) })
    
    if not thread:
      
      # retriving RelationType
      # relation_type = collection.Node.one({ "_type": "RelationType", "name": u"has_thread", "inverse_name": u"thread_of" })
      
      # Creating thread with the name of node
      thread_obj = collection.GSystem()

      thread_obj.name = unicode(node.name)
      thread_obj.status = u"PUBLISHED"

      thread_obj.created_by = int(request.user.id)
      thread_obj.modified_by = int(request.user.id)
      thread_obj.contributors.append(int(request.user.id))

      thread_obj.member_of.append(ObjectId(twist_st._id))
      thread_obj.prior_node.append(ObjectId(node_id))
      thread_obj.group_set.append(ObjectId(group_id))
      
      thread_obj.save()

      # creating GRelation
      # create_grelation(node_id, relation_type, twist_st)
      response_data = [ "thread-created", str(thread_obj._id) ]

      return HttpResponse(json.dumps(response_data))

    else:
      response_data =  [ "Thread-exist", str(thread._id) ]
      return HttpResponse(json.dumps(response_data))
  
  except Exception as e:
    
    error_message = "\n DiscussionThreadCreateError: " + str(e) + "\n"
    raise Exception(error_message)
    # return HttpResponse("server-error")


# to add discussion replies
def discussion_reply(request, group_id):

  try:

    prior_node = request.POST.get("prior_node_id", "")
    content_org = request.POST.get("reply_text_content", "") # reply content

    # process and save node if it reply has content  
    if content_org:
  
      user_id = int(request.user.id)
      user_name = unicode(request.user.username)

      # auth = collection.Node.one({'_type': 'Author', 'name': user_name })
      reply_st = collection.Node.one({ '_type':'GSystemType', 'name':'Reply'})
      
      # creating empty GST and saving it
      reply_obj = collection.GSystem()

      reply_obj.name = unicode("Reply of:" + str(prior_node))
      reply_obj.status = u"PUBLISHED"

      reply_obj.created_by = user_id
      reply_obj.modified_by = user_id
      reply_obj.contributors.append(user_id)

      reply_obj.member_of.append(ObjectId(reply_st._id))
      reply_obj.prior_node.append(ObjectId(prior_node))
      reply_obj.group_set.append(ObjectId(group_id))
  
      reply_obj.content_org = unicode(content_org)
      filename = slugify(unicode("Reply of:" + str(prior_node))) + "-" + user_name + "-"
      reply_obj.content = org2html(content_org, file_prefix=filename)
  
      # saving the reply obj
      reply_obj.save()

      formated_time = reply_obj.created_at.strftime("%B %d, %Y, %I:%M %p")
      
      # ["status_info", "reply_id", "prior_node", "html_content", "org_content", "user_id", "user_name", "created_at" ]
      reply = json.dumps( [ "reply_saved", str(reply_obj._id), str(reply_obj.prior_node[0]), reply_obj.content, reply_obj.content_org, user_id, user_name, formated_time], cls=DjangoJSONEncoder )

      return HttpResponse( reply )

    else: # no reply content

      return HttpResponse(json.dumps(["no_content"]))      

  except Exception as e:
    
    error_message = "\n DiscussionReplyCreateError: " + str(e) + "\n"
    raise Exception(error_message)

    return HttpResponse(json.dumps(["Server Error"]))


def discussion_delete_reply(request, group_id):

    nodes_to_delete = json.loads(request.POST.get("nodes_to_delete", "[]"))
    
    reply_st = collection.Node.one({ '_type':'GSystemType', 'name':'Reply'})

    deleted_replies = []
    
    for each_reply in nodes_to_delete:
        temp_reply = collection.Node.one({"_id": ObjectId(each_reply)})
        
        if temp_reply:
            deleted_replies.append(temp_reply._id.__str__())
            temp_reply.delete()
        
    return HttpResponse(json.dumps(deleted_replies))


def get_user_group(userObject):
  '''
  methods for getting user's belongs to group.
  input (userObject) is user object
  output list of dict, dict contain groupname, access, group_type, created_at and created_by
  '''
  blank_list = []
  cur_groups_user = collection.Node.find({'_type': "Group", 
                                          '$or': [
                                            {'created_by': userObject.id}, 
                                            {'group_admin': userObject.id},
                                            {'author_set': userObject.id},
                                          ]
                                        }).sort('last_update', -1)
  for eachgroup in cur_groups_user :
    access = ""
    if eachgroup.created_by == userObject.id:
      access = "owner"
    elif userObject.id in eachgroup.group_admin :
      access = "admin"
    elif userObject.id in eachgroup.author_set :
      access = "member"
    else :
      access = "member"
    user = User.objects.get(id=eachgroup.created_by)
    blank_list.append({'id':str(eachgroup._id), 'name':eachgroup.name, 'access':access, 'group_type':eachgroup.group_type, 'created_at':eachgroup.created_at, 'created_by':user.username})
  return blank_list
  
def get_user_task(userObject):
  '''
  methods for getting user's assigned task.
  input (userObject) is user object
  output list of dict, dict contain taskname, status, due_time, created_at and created_by, group_name
  '''
  blank_list = []
  attributetype_assignee = collection.Node.find_one({"_type":'AttributeType', 'name':'Assignee'})
  attributetype_status = collection.Node.find_one({"_type":'AttributeType', 'name':'Status'})
  attributetype_end_time = collection.Node.find_one({"_type":'AttributeType', 'name':'end_time'})
  attr_assignee = collection.Node.find({"_type":"GAttribute", "attribute_type.$id":attributetype_assignee._id, "object_value":userObject.username})
  for attr in attr_assignee :
    blankdict = {}
    task_node = collection.Node.find_one({'_id':attr.subject})
    attr_status = collection.Node.find_one({"_type":"GAttribute", "attribute_type.$id":attributetype_status._id, "subject":task_node._id})
    attr_end_time = collection.Node.find_one({"_type":"GAttribute", "attribute_type.$id":attributetype_end_time._id, "subject":task_node._id})
    if attr_status.object_value is not "closed":
      group = collection.Node.find_one({"_id":task_node.group_set[0]})
      user = User.objects.get(id=task_node.created_by)
      blankdict.update({'name':task_node.name, 'created_at':task_node.created_at, 'created_by':user.username, 'group_name':group.name, 'id':str(task_node._id)})
      if attr_status:
        blankdict.update({'status':attr_status.object_value})
      if attr_end_time:
        blankdict.update({'due_time':attr_end_time.object_value})
      blank_list.append(blankdict)
  return blank_list

def get_user_notification(userObject):
  '''
  methods for getting user's notification.
  input (userObject) is user object
  output list of dict, dict contain notice label, notice display
  '''
  blank_list = []
  notification_object = notification.NoticeSetting.objects.filter(user_id=userObject.id)
  for each in notification_object.reverse():
    ntid = each.notice_type_id
    ntype = notification.NoticeType.objects.get(id=ntid)
    label = ntype.label.split("-")[0]
    blank_list.append({'label':label, 'display': ntype.display})
  blank_list.reverse()
  return blank_list

def get_user_activity(userObject):
  '''
  methods for getting user's activity.
  input (userObject) is user object
  output list of dict, dict 
  '''
  blank_list = []
  activity = ""
  activity_user = collection.Node.find({'$and':[{'$or':[{'_type':'GSystem'},{'_type':'Group'},{'_type':'File'}]}, 
                                                 {'$or':[{'created_by':userObject.id}, {'modified_by':userObject.id}]}] }).sort('last_update', -1).limit(10)
  for each in activity_user:
    if each.created_by == each.modified_by :
      if each.last_update == each.created_at:
        activity =  'created'
      else :
        activity =  'modified'
    else :
      activity =  'created'
    if each._type == 'Group':
      blank_list.append({'id':str(each._id), 'name':each.name, 'date':each.last_update, 'activity': activity, 'type': each._type})
    else :
      member_of = collection.Node.find_one({"_id":each.member_of[0]})
      blank_list.append({'id':str(each._id), 'name':each.name, 'date':each.last_update, 'activity': activity, 'type': each._type, 'group_id':str(each.group_set[0]), 'member_of':member_of.name.lower()})
  return blank_list

def get_file_node(file_name=""):
  file_list=[]
  new=[]
  a=str(file_name).split(',')
  for i in a:
        k=str(i.strip('   [](\'u\'   '))
        new.append(k)
	col_Group = db[Node.collection_name]
	ins_objectid  = ObjectId()
  for i in new:
          if  ins_objectid.is_valid(i) is False:
		  filedoc=collection.Node.find({'_type':'File','name':unicode(i)})
	  else:
		  filedoc=collection.Node.find({'_type':'File','_id':ObjectId(i)})			
          if filedoc:
             for i in filedoc:
		            file_list.append(i.name)	
  return file_list	

def create_task(task_dict, task_type_creation="single"):
    """Creates task with required attribute(s) and relation(s).

    task_dict
    - Required keys: _id[optional], name, group_set, created_by, modified_by, contributors, content_org,
        created_by_name, Status, Priority, start_time, end_time, Assignee, has_type

    task_type_creation
    - Valid input values: "single", "multiple", "group"
    """
    # Fetch Task GSystemType document
    task_gst = collection.Node.one(
        {'_type': "GSystemType", 'name': "Task"}
    )

    # List of keys of "task_dict" dictionary
    task_dict_keys = task_dict.keys()

    if task_dict.has_key("_id"):
      task_node = collection.Node.one({'_id': task_dict["_id"]})
    else:
      task_node = collection.GSystem()
      task_node["member_of"] = [task_gst._id]

    # Store built in variables of task node
    # Iterate task_node using it's keys
    for key in task_node:
        if key in ["Status", "Priority", "start_time", "end_time", "Assignee"]:
            # Required because these values might come as key in node's document
            continue

        if key in task_dict_keys:
            if key == "content_org":
                #  org-content
                task_node[key] = task_dict[key]

                # Required to link temporary files with the current user who is modifying this document
                filename = slugify(task_dict["name"]) + "-" + task_dict["created_by_name"] + "-" + ObjectId().__str__()
                task_dict_keys.remove("created_by_name")
                task_node.content = org2html(task_dict[key], file_prefix=filename)

            else:
                task_node[key] = task_dict[key]

            task_dict_keys.remove(key)

    # Save task_node with built-in variables as required for creating GAttribute(s)/GRelation(s)
    task_node.status = u"PUBLISHED"
    task_node.save()

    # Create GAttribute(s)/GRelation(s)
    for attr_or_rel_name in task_dict_keys:
        attr_or_rel_node = collection.Node.one(
            {'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': unicode(attr_or_rel_name)}
        )

        if attr_or_rel_node:
            if attr_or_rel_node._type == "AttributeType":
                ga_node = create_gattribute(task_node._id, attr_or_rel_node, task_dict[attr_or_rel_name])
            
            elif attr_or_rel_node._type == "RelationType":
                gr_node = create_grelation(task_node._id, attr_or_rel_node, task_dict[attr_or_rel_name])

            task_node.reload()

        else:
            raise Exception("\n No AttributeType/RelationType exists with given name("+attr_or_rel_name+") !!!")

    # If given task is a group task (create a task for each Assignee from the list)
    # Iterate Assignee list & create separate tasks for each Assignee 
    # with same set of attribute(s)/relation(s)
    if task_type_creation == "group":
        mutiple_assignee = task_dict["Assignee"]
        collection_set = []
        for each in mutiple_assignee:
            task_dict["Assignee"] = [each]
            task_sub_node = create_task(task_dict)
            collection_set.append(task_sub_node._id)

        collection.update({'_id': task_node._id}, {'$set': {'collection_set': collection_set}}, upsert=False, multi=False)

    else:
        # Send notification for each each Assignee of the task
        # Only be done in case when task_type_creation is not group, 
        # i.e. either single or multiple
        if not task_dict.has_key("_id"):
          site = Site.objects.get(pk=1)
          site = site.name.__str__()

          from_user = task_node.user_details_dict["created_by"]  # creator of task

          group_name = collection.Node.one(
              {'_type': {'$in': ["Group", "Author"]}, '_id': task_node.group_set[0]},
              {'name': 1}
          ).name

          url_link = "http://" + site + "/" + group_name.replace(" ","%20").encode('utf8') + "/task/" + str(task_node._id)

          to_user_list = []
          for index, user_id in enumerate(task_dict["Assignee"]):
              user_obj = User.objects.get(id=user_id)
              task_dict["Assignee"][index] = user_obj.username
              if user_obj not in to_user_list:
                  to_user_list.append(user_obj)

          msg = "Task '" + task_node.name + "' has been reported by " + from_user + \
              "\n     - Status: " + task_dict["Status"] + \
              "\n     - Priority: " + task_dict["Priority"] + \
              "\n     - Assignee: " + ", ".join(task_dict["Assignee"]) +  \
              "\n     - For more details, please click here: " + url_link

          activity = "reported task"
          render_label = render_to_string(
              "notification/label.html",
              {
                  "sender": from_user,
                  "activity": activity,
                  "conjunction": "-",
                  "link": url_link
              }
          )
          notification.create_notice_type(render_label, msg, "notification")
          notification.send(to_user_list, render_label, {"from_user": from_user})

    return task_node
