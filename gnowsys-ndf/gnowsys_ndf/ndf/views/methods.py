''' -- imports from installed packages -- '''
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response, render
from django.http import HttpResponse
from django.template import RequestContext
from django.core.serializers.json import DjangoJSONEncoder
import mongokit 

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.mobwrite.models import TextObj
from gnowsys_ndf.ndf.models import HistoryManager

from gnowsys_ndf.ndf.management.commands.data_entry import create_gattribute

''' -- imports from python libraries -- '''
# import os -- Keep such imports here

import subprocess
import re
import ast
import string
import json
from datetime import datetime
######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]

history_manager = HistoryManager()
theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})

#######################################################################################################################################
#                                                                       C O M M O N   M E T H O D S   D E F I N E D   F O R   V I E W S
#######################################################################################################################################
coln=db[GSystem.collection_name]
grp_st=coln.Node.one({'$and':[{'_type':'GSystemType'},{'name':'Group'}]})
ins_objectid  = ObjectId()

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
  grp_obj=coln.Node.one({'_id':ObjectId(group_id)})
  auth_obj=coln.Node.one({'_id':ObjectId(user_id)})
  at_user_pref=collection.Node.one({'$and':[{'_type':'AttributeType'},{'name':'user_preference_off'}]})
  if at_user_pref:
    poss_attrs=auth_obj.get_possible_attributes(at_user_pref._id)
    if poss_attrs:
      list_at_pref=poss_attrs['user_preference_off']['object_value']
      if grp_obj in list_at_pref:
        return False
      else:
        return True

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

def get_drawers(group_id, nid=None, nlist=[], checked=None):
    """Get both drawers-list.
    """
    dict_drawer = {}
    dict1 = {}
    dict2 = []  # Changed from dictionary to list so that it's content are reflected in a sequential-order

    collection = db[Node.collection_name]
    
    theme_GST_id = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
    topic_GST_id = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})    
    theme_item_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'theme_item'})

    forum_GST_id = collection.Node.one({'_type': 'GSystemType', 'name': 'Forum'}, {'_id':1})
    reply_GST_id = collection.Node.one({'_type': 'GSystemType', 'name': 'Reply'}, {'_id':1})

    
    drawer = None    
    
    if checked:     
      if checked == "Page":
 
        gst_page_id = collection.Node.one({'_type': "GSystemType", 'name': "Page"})._id
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$all':[gst_page_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})
        
      elif checked == "File":         
        drawer = collection.Node.find({'_type': u"File", 'group_set': {'$all': [ObjectId(group_id)]}})
        
      elif checked == "Image":         
        gst_image_id = collection.Node.one({'_type': "GSystemType", 'name': "Image"})._id
        drawer = collection.Node.find({'_type': u"File", 'member_of': {'$in':[gst_image_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})
        

      elif checked == "Video":         
        gst_video_id = collection.Node.one({'_type': "GSystemType", 'name': "Video"})._id
        drawer = collection.Node.find({'_type': u"File", 'member_of': {'$in':[gst_video_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "Quiz":
        # For prior-node-list
        drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "QuizObj":
        # For collection-list
        gst_quiz_id = collection.Node.one({'_type': "GSystemType", 'name': "Quiz"})._id
        gst_quiz_item_id = collection.Node.one({'_type': "GSystemType", 'name': "QuizItem"})._id
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$in':[gst_quiz_id, gst_quiz_item_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "OnlyQuiz":
        gst_quiz_id = collection.Node.one({'_type': "GSystemType", 'name': "Quiz"})._id
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$all':[gst_quiz_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "QuizItem":
        gst_quiz_item_id = collection.Node.one({'_type': "GSystemType", 'name': "QuizItem"})._id
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$all':[gst_quiz_item_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "Group":
        drawer = collection.Node.find({'_type': u"Group"})

      elif checked == "Forum":
        gst_forum_id = collection.Node.one({'_type': "GSystemType", 'name': "Forum"})._id
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$all':[gst_forum_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "Module":
        gst_module_id = collection.Node.one({'_type': "GSystemType", 'name': "Module"})._id
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$all':[gst_module_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

      elif checked == "Pandora Video":
        gst_pandora_video_id = collection.Node.one({'_type': "GSystemType", 'name': "Pandora_video"})._id
        drawer = collection.Node.find({'_type': u"File", 'member_of': {'$all':[gst_pandora_video_id]}}).limit(50)

      elif checked == "Theme":
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$in':[theme_GST_id._id, topic_GST_id._id]}, 'group_set': {'$all': [ObjectId(group_id)]}}) 

      elif checked == "theme_item":
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$in':[theme_item_GST._id, topic_GST_id._id]}, 'group_set': {'$all': [ObjectId(group_id)]}}) 


      elif checked == "Topic":
        drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, 'member_of':{'$nin':[theme_GST_id._id, theme_item_GST._id, topic_GST_id._id]},'group_set': {'$all': [ObjectId(group_id)]}})   

    else:
      # For heterogeneous collection      
      if theme_GST_id or topic_GST_id or theme_item_GST or forum_GST_id or reply_GST_id:
        drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, 'member_of':{'$nin':[theme_GST_id._id,theme_item_GST._id, topic_GST_id._id, reply_GST_id._id, forum_GST_id._id]}, 'group_set': {'$all': [ObjectId(group_id)]}})   
      else:
        drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, 'group_set': {'$all': [ObjectId(group_id)]} })
           
    
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

    return dict_drawer

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
    filename = slugify(name) + "-" + usrname + "-"
    node.content = org2html(content_org, file_prefix=filename)



def get_node_common_fields(request, node, group_id, node_type, coll_set=None):
  """Updates the retrieved values of common fields from request into the given node."""
  # print "\n Coming here...\n\n"

  gcollection = db[Node.collection_name]
  group_obj=gcollection.Node.one({'_id':ObjectId(group_id)})
  collection = None
  if coll_set:
      if "Theme" in coll_set.member_of_names_list:
        node_type = theme_GST
      else:
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
  prior_node_list = request.POST.get('prior_node_list','')
  collection_list = request.POST.get('collection_set_list','')
  module_list = request.POST.get('module_list','')
  map_geojson_data = request.POST.get('map-geojson-data')
  user_last_visited_location = request.POST.get('last_visited_location')

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

    if group_obj._id not in node.group_set:
      node.group_set.append(group_obj._id)

    if access_policy == "PUBLIC":
      node.access_policy = unicode(access_policy)
    else:
      node.access_policy = unicode(access_policy)

    node.status = "PUBLISHED"

    is_changed = True
          
    # End of if

  # --------------------------------------------------------------------------- For create/edit

  # -------------------------------------------------------------------------------- name
 
  if name:
    if node.name != name:
      node.name = name
      # print "\n Changed: name"
      is_changed = True
  
  if sub_theme_name:
    if node.name != sub_theme_name:
      node.name = sub_theme_name
      # print "\n Changed: sub-theme"
      is_changed = True
  
  if add_topic_name:
    if node.name != add_topic_name:
      node.name = add_topic_name
      # print "\n Changed: topic"
      is_changed = True

  # -------------------------------------------------------------------------------- language

  if language:
    node.language = unicode(language) 
  else:
    node.language = u"en"

  # -------------------------------------------------------------------------------- access_policy

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
  # -------------------------------------------------------------------------------- tags
  if tags:
    tags_list = []

    for tag in tags.split(","):
      tag = unicode(tag.strip())

      if tag:
        tags_list.append(tag)

    if set(node.tags) != set(tags_list):
      node.tags = tags_list
      # print "\n Changed: tags"
      is_changed = True

  # -------------------------------------------------------------------------------- prior_node

   
  # if prior_node_list != '':
  #   prior_node_list = prior_node_list.split(",")

  # i = 0
  # while (i < len(prior_node_list)):
  #   node_id = ObjectId(prior_node_list[i])
  #   if gcollection.Node.one({"_id": node_id}):
  #     node.prior_node.append(node_id)
    
  #   i = i+1
  #node.prior_node = []
  if prior_node_list != '':
    prior_node_list = [ObjectId(each.strip()) for each in prior_node_list.split(",")]

    if set(node.prior_node) != set(prior_node_list):
      i = 0
      while (i < len(prior_node_list)):
        node_id = ObjectId(prior_node_list[i])
        if gcollection.Node.one({"_id": node_id}):
          if node_id not in node.prior_node:
            node.prior_node.append(node_id)
        
        i = i+1
      # print "\n Changed: prior_node"
      is_changed = True
 
  # -------------------------------------------------------------------------------- collection

  # node.collection_set = []
  # if collection_list != '':
  #     collection_list = collection_list.split(",")

  # i = 0
  # while (i < len(collection_list)):
  #   node_id = ObjectId(collection_list[i])
    
  #   if gcollection.Node.one({"_id": node_id}):
  #     node.collection_set.append(node_id)
    
  #   i = i+1

  if collection_list != '':
    collection_list = [ObjectId(each.strip()) for each in collection_list.split(",")]

    if set(node.collection_set) != set(collection_list):
      i = 0
      node.collection_set = []

      # checking if each _id in collection_list is valid or not
      while (i < len(collection_list)):
        node_id = ObjectId(collection_list[i])
        
        if gcollection.Node.one({"_id": node_id}):
          if node_id not in node.collection_set:
            node.collection_set.append(node_id)
        
        i = i+1
      # print "\n Changed: collection_list"
      is_changed = True

     
  # -------------------------------------------------------------------------------- Module

  # node.collection_set = []
  # if module_list != '':
  #     collection_list = module_list.split(",")

  # i = 0
  # while (i < len(collection_list)):
  #   node_id = ObjectId(collection_list[i])
    
  #   if gcollection.Node.one({"_id": node_id}):
  #     node.collection_set.append(node_id)
    
  #   i = i+1

  if module_list != '':
    collection_list = [ObjectId(each.strip()) for each in module_list.split(",")]

    if set(node.collection_set) != set(collection_list):
      i = 0
      while (i < len(collection_list)):
        node_id = ObjectId(collection_list[i])
        
        if gcollection.Node.one({"_id": node_id}):
          if node_id not in node.collection_set:
            node.collection_set.append(node_id)
        
        i = i+1
      # print "\n Changed: module_list"
      is_changed = True
    
  # ------------------------------------------------------------------------------- org-content
  
  if content_org:
    if node.content_org != content_org:
      node.content_org = content_org
      
      # Required to link temporary files with the current user who is modifying this document
      usrname = request.user.username
      filename = slugify(name) + "-" + usrname + "-"
      node.content = org2html(content_org, file_prefix=filename)
      # print "\n Changed: content_org"
      is_changed = True

  # ----------------------------------------------------------------------------- visited_location in author class
  if node.location != map_geojson_data:
    node.location = map_geojson_data # Storing location data
    # print "\n Changed: map"
    is_changed = True
  
  if user_last_visited_location:
    user_last_visited_location = list(ast.literal_eval(user_last_visited_location))

    author = gcollection.Node.one({'_type': "GSystemType", 'name': "Author"})
    user_group_location = gcollection.Node.one({'_type': "Author", 'member_of': author._id, 'created_by': usrid, 'name': usrname})

    if user_group_location:
      if node._type == "Author" and user_group_location._id == node._id:
        if node['visited_location'] != user_last_visited_location:
          node['visited_location'] = user_last_visited_location
          # print "\n Changed: user location"
          is_changed = True

      else:
        user_group_location['visited_location'] = user_last_visited_location
        user_group_location.save()

  if is_changed:
    node.status = unicode("DRAFT")

    node.modified_by = usrid

    if usrid not in node.contributors:
      node.contributors.append(usrid)

  # print "\n Reached here ...\n\n"
  return is_changed
# ============= END of def get_node_common_fields() ==============
  
  
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
     ''' function to filter between the page to be displyed to user 
           i.e which page to be shown to the user drafted or the published page
	if a user have some drafted content then he wouldbe shown his own drafted contents 
and if he has published his contents then he would be shown the current published contents


'''
     username =request.user
     # print node,"nodeeee"
     node1,ver1=get_versioned_page(node)
     node2,ver2=get_user_page(request,node)     
     
     if  ver2 != '1.1':                           
	    if node2 is not None:
		# print "direct"
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

  # print group_id

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


                      
"""
def get_node_metadata_fields(request, node, node_type):
	if(node.has_key('_id')):
  		for at in node_type.attribute_type_set:
			field_value=(request.POST.get(at.name,""))
	
			create_gattribute(node._id,at,field_value)
"""

def get_node_metadata(request,node,node_type):
	attribute_type_list = ["age_range","audience","timerequired","interactivitytype","basedonurl","educationaluse","textcomplexity","readinglevel","educationalsubject","educationallevel"]         
	if(node.has_key('_id')):
		for atname in attribute_type_list:
			field_value=unicode(request.POST.get(atname,""))
			at=collection.Node.one({"_type":"AttributeType","name":atname})	
			if(at!=None):
				create_gattribute(node._id,at,field_value)		
"""			
def create_AttributeType(name, data_type, system_name, user_id):

	cursor = collection.Node.one({"name":unicode(name), "_type":u"AttributeType"})
	if (cursor != None):
		print "The AttributeType already exists."
	else:
		attribute_type = collection.AttributeType()
		attribute_type.name = unicode(name)
		attribute_type.data_type = data_type
		system_type = collection.Node.one({"name":system_name})
		attribute_type.subject_type.append(system_type._id)
		attribute_type.created_by = user_id
		attribute_type.modified_by = user_id
	        attribute_type.status=u"PUBLISHED"
		#factory_id = collection.Node.one({"name":u"factory_types"})._id
		#attribute_type.member_of.append(factory_id)
		attribute_type.save()
		system_type.attribute_type_set.append(attribute_type)
		system_type.save()

def create_RelationType(name,inverse_name,subject_type_name,object_type_name,user_id):

	cursor = collection.Node.one({"name":unicode(name)})
        if cursor!=None:
		print "The RelationType already exists."
	else:
		relation_type = collection.RelationType()
                relation_type.name = unicode(name)
                system_type = collection.Node.one({"name":unicode(subject_type_name)})
                relation_type.subject_type.append(system_type._id)
                relation_type.inverse_name = unicode(inverse_name)
		relation_type.created_by = user_id
                relation_type.modified_by = user_id
		relation_type.status=u"PUBLISHED"
		object_type = collection.Node.one({"name":unicode(object_type_name)})
		relation_type.object_type.append(ObjectId(object_type._id))
                relation_type.save()
		system_type.relation_type_set.append(relation_type)
		system_type.save()
"""

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

    for tab_name, list_field_id in demo['property_order']:
      list_field_set = []
      for field_id_or_name in list_field_id:
        if type(field_id_or_name) == ObjectId: #ObjectId.is_valid(field_id_or_name):
          # For attribute-field(s) and/or relation-field(s)
          
          field = collection.Node.one({'_id': ObjectId(field_id_or_name)}, {'_type': 1, 'subject_type': 1, 'object_type': 1, 'name': 1, 'altnames': 1, 'inverse_name': 1})
          # list_field_set.append([demo['member_of'], field, demo[field.name]])
          altnames = u""
          value = None
          data_type = None
          if field._type == RelationType or field._type == "RelationType":
            # For RelationTypes
            # print "\n field.altnames: ", field.altnames, "\n"
            # print "\n ", demo["member_of"], " === ", field.subject_type, "\n"
            if set(demo["member_of"]).issubset(field.subject_type):
              # It means we are dealing with normal relation & 
              data_type = demo.structure[field.name]
              value = demo[field.name]
              # print "\n field.altnames(inner 1 if): ", field.altnames, "\n"
              if field.altnames:
                if ";" in field.altnames:
                  # print "\n altnames: ", field.altnames
                  altnames = field.altnames.split(";")[0]
                else:
                  altnames = field.altnames

            elif set(demo["member_of"]).issubset(field.object_type):
              # It means we are dealing with inverse relation
              data_type = demo.structure[field.inverse_name]
              # print "\n field.altnames(else`): ", field.altnames, "\n"
              value = demo[field.inverse_name]
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
                  data_type = demo.structure[field.name]
                  # print "\n field.altnames(inner 2 if): ", field.altnames, "\n"
                  value = demo[field.name]
                  if field.altnames:
                    if ";" in field.altnames:
                      altnames = field.altnames.split(";")[0]
                    else:
                      altnames = field.altnames

                elif each in field.object_type:
                  data_type = demo.structure[field.inverse_name]
                  # print "\n field.altnames(inner 2_2 if): ", field.altnames, "\n"
                  value = demo[field.inverse_name]
                  if field.altnames:
                    if ";" in field.altnames:
                      altnames = field.altnames.split(";")[0]
                    else:
                      altnames = field.altnames


          else:
            # For AttributeTypes
            altnames = field.altnames
            data_type = demo.structure[field.name]
            value = demo[field.name]


          # print " field._id: ", field._id, " --  field.altnames: ", altnames

          list_field_set.append({ 'type': field._type, # It's only use on details-view template; overridden in ndf_tags html_widget()
                                  '_id': field._id, 
                                  'data_type': data_type,
                                  'name': field.name, 'altnames': altnames,
                                  'value': value
                                })

        else:
          # For node's base-field(s)

          base_field = {
            'name': {'name': "name", '_type': "BaseField", 'altnames': "Name", 'required': True},
            'content_org': {'name': "content_org", '_type': "BaseField", 'altnames': "Content", 'required': False},
            # 'featured': {'name': "featured", '_type': "BaseField", 'altnames': "Featured"},
            'location': {'name': "location", '_type': "BaseField", 'altnames': "Location", 'required': False},
            # 'status': {'name': "status", '_type': "BaseField", 'altnames': "Status", 'required': False},
            'tags': {'name': "tags", '_type': "BaseField", 'altnames': "Tags", 'required': False}
          }
          # list_field_set.append([demo['member_of'], base_field[field_id_or_name], demo[field_id_or_name]])
          list_field_set.append({ '_type': base_field[field_id_or_name]['_type'],
                                  'data_type': demo.structure[field_id_or_name],
                                  'name': field_id_or_name, 'altnames': base_field[field_id_or_name]['altnames'],
                                  'value': demo[field_id_or_name],
                                  'required': base_field[field_id_or_name]['required']
                                })

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
      # print " (if)--> ", field_data_type, (field_data_type == "datetime"), "\n"

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
        field_value = "???"

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

      # print "\n parsed field_value: ", field_value

    elif type(field_data_type) == list:

      if kwargs.has_key("field_instance"):
        if kwargs["field_instance"]["_type"] == RelationType or kwargs["field_instance"]["_type"] == "RelationType":
          # Write RT related code 
          if not field_value:
            return None

          # print "\n field_value (going herre): ", field_value
          field_value = collection.Node.one({'_id': ObjectId(field_value), 'member_of': {'$in': kwargs["field_instance"]["object_type"]}}, {'_id': 1})
          if field_value:
            field_value = field_value._id
            # print "\n field_value (innerobjectid): ", field_value, " -- ", type(field_value)
          else:
            error_message = "This ObjectId("+field_type+") doesn't exists"
            raise Exception(error_message)

      else:
        # Write code...
        if not field_value:
          return []

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

def create_gattribute(subject_id, attribute_type_node, object_value):
  ga_node = None

  ga_node = collection.Triple.one({'_type': "GAttribute", 'subject': subject_id, 'attribute_type': attribute_type_node.get_dbref()})

  if ga_node is None:
    # Code for creation
    try:
      ga_node = collection.GAttribute()

      ga_node.subject = subject_id
      ga_node.attribute_type = attribute_type_node
      ga_node.object_value = object_value
      
      ga_node.status = u"PUBLISHED"
      ga_node.save()
      info_message = " GAttribute ("+ga_node.name+") created successfully.\n"
      print "\n ", info_message

    except Exception as e:
      error_message = "\n GAttributeCreateError: " + str(e) + "\n"
      raise Exception(error_message)

  else:
    # Code for updation
    is_ga_node_changed = False

    try:
      if type(ga_node.object_value) == list:
        if set(ga_node.object_value) != set(object_value):
          ga_node.object_value = object_value
          is_ga_node_changed = True

      elif type(ga_node.object_value) == dict:
        if cmp(ga_node.object_value, object_value) != 0:
          ga_node.object_value = object_value
          is_ga_node_changed = True

      else:
        if ga_node.object_value != object_value:
          ga_node.object_value = object_value
          is_ga_node_changed = True

      if is_ga_node_changed:
        ga_node.status = u"PUBLISHED"
        ga_node.save()
        info_message = " GAttribute ("+ga_node.name+") updated successfully.\n"
        print "\n", info_message

      else:
        info_message = " GAttribute ("+ga_node.name+") already exists (Nothing updated) !\n"
        print "\n", info_message

    except Exception as e:
      error_message = "\n GAttributeUpdateError: " + str(e) + "\n"
      raise Exception(error_message)

  return ga_node


def create_grelation(subject_id, relation_type_node, right_subject_id, **kwargs):
  """
  Creates a GRelation document (instance).

  Arguments:
  subject_id -- ObjectId of the subject-node
  relation_type_node -- Document of the RelationType node (Embedded document)
  right_subject_id -- ObjectId of the right_subject node

  Returns:
  Created GRelation document.
  """
  gr_node = None
  multi_relations = False

  try:
    if kwargs.has_key("multi"):
      multi_relations = kwargs["multi"]

    subject_id = ObjectId(subject_id)
    right_subject_id = ObjectId(right_subject_id)

    if multi_relations:
      # For dealing with multiple relations

      # Iterate and find all relationships (including DELETED ones' also)
      nodes = collection.Triple.find({'_type': "GRelation", 
                                      'subject': subject_id, 
                                      'relation_type': relation_type_node.get_dbref()
                                    })

      for n in nodes:
        if n.right_subject in right_subject_id:
          if n.status != u"DELETED":
            # If match found with existing one's, then only remove that ObjectId from the given list of ObjectIds
            right_subject_id.remove(n.right_subject)

      if right_subject_id:
        # If still ObjectId list persists, it means either they are new ones' or they are from deleted ones'
        for nid in right_subject_id:
          gr_node = collection.Triple.one({'_type': "GRelation", 
                                            'subject': subject_id, 
                                            'relation_type': relation_type_node.get_dbref(),
                                            'right_subject': nid
                                          })

          if gr_node is None:
            # New one found so create it
            gr_node = collection.GRelation()

            gr_node.subject = subject_id
            gr_node.relation_type = relation_type_node
            gr_node.right_subject = right_subject_id

            gr_node.status = u"PUBLISHED"
            gr_node.save()

          else:
            # Deleted one found so change it's status back to Published
            if gr_node.status == u'DELETED':
              collection.update({'_id': gr_node._id}, {'$set': {'status': u"PUBLISHED"}}, upsert=False, multi=False)

          info_message = " GRelation ("+gr_node.name+") created successfully.\n"
          print "\n", info_message

    else:
      # For dealing with single relation
      gr_node = collection.Triple.one({'_type': "GRelation", 
                                       'subject': subject_id, 
                                       'relation_type': relation_type_node.get_dbref()
                                      })

      if gr_node is None:
        # Code for creation
        gr_node = collection.GRelation()

        gr_node.subject = subject_id
        gr_node.relation_type = relation_type_node
        gr_node.right_subject = right_subject_id

        gr_node.status = u"PUBLISHED"
        
        gr_node.save()
        info_message = " GRelation ("+gr_node.name+") created successfully.\n"
        print "\n", info_message

      else:
        if gr_node.right_subject != right_subject_id:
          collection.update({'_id': gr_node._id}, {'$set': {'right_subject': right_subject_id}}, upsert=False, multi=False)

        elif gr_node.right_subject == right_subject_id and gr_node.status == u"DELETED":
          collection.update({'_id': gr_node._id}, {'$set': {'status': u"PUBLISHED"}}, upsert=False, multi=False)

        else:
          info_message = " GRelation ("+gr_node.name+") already exists !\n"
          print "\n", info_message

    return gr_node

  except Exception as e:
      error_message = "\n GRelationCreateError: " + str(e) + "\n"
      raise Exception(error_message)

# Method to create discussion thread for File and Page.
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
      # print "\n\n====", reply

      return HttpResponse( reply )

    else: # no reply content

      return HttpResponse(json.dumps(["no_content"]))      

  except Exception as e:
    
    error_message = "\n DiscussionReplyCreateError: " + str(e) + "\n"
    raise Exception(error_message)

    return HttpResponse(json.dumps(["Server Error"]))
