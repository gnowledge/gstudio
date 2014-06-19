''' -- imports from installed packages -- '''
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response, render
from django.template import RequestContext

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.mobwrite.models import TextObj
from gnowsys_ndf.ndf.models import HistoryManager

''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import subprocess
import re
import ast
import string
from datetime import datetime
######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]

history_manager = HistoryManager()
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
        theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})._id
        topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})._id
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$in':[theme_GST, topic_GST]}, 'group_set': {'$all': [ObjectId(group_id)]}}) 

    else:
      drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, 'group_set': {'$all': [ObjectId(group_id)]}})   

           
    
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

  

def get_node_common_fields(request, node, group_id, node_type):
  """Updates the retrieved values of common fields from request into the given node."""
  
  gcollection = db[Node.collection_name]
  group_obj=gcollection.Node.one({'_id':ObjectId(group_id)})
  collection = None

  name = request.POST.get('name')
  sub_theme_name = request.POST.get("sub_theme_name", '')
  add_topic_name = request.POST.get("add_topic_name", '')
  usrid = int(request.user.id)
  usrname = unicode(request.user.username)
  access_policy = request.POST.get("login-mode", '') 
  language= request.POST.get('lan')
  tags = request.POST.get('tags')
  prior_node_list = request.POST.get('prior_node_list','')
  collection_list = request.POST.get('collection_list','')
  module_list = request.POST.get('module_list','')
  content_org = request.POST.get('content_org')
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
          
    # End of if

  # --------------------------------------------------------------------------- For create/edit
  node.name = unicode(name)
  if sub_theme_name:
    node.name = unicode(sub_theme_name) 
  if add_topic_name:
    node.name = unicode(add_topic_name)

  node.status = unicode("DRAFT")
  if language:
    node.language = unicode(language) 
  else:
    node.language = u"en"
  node.location = map_geojson_data # Storing location data

  if access_policy:
    # Policy will be changed only by the creator of the resource
    # via access_policy(public/private) option on the template which is visible only to the creator
    if access_policy == "PUBLIC":
      node.access_policy = u"PUBLIC"
    else:
      node.access_policy = u"PRIVATE"
  else:
    node.access_policy = u"PUBLIC"

  node.modified_by = usrid

  if usrid not in node.contributors:
    node.contributors.append(usrid)

  # For displaying nodes in home group as well as in creator group.
  user_group_obj=gcollection.Node.one({'$and':[{'_type':ObjectId(group_id)},{'name':usrname}]})

  if group_obj._id not in node.group_set:
    node.group_set.append(group_obj._id)
  else:
    if user_group_obj:
      if user_group_obj._id not in node.group_set:
        node.group_set.append(user_group_obj._id)

  if tags:
    tags_list = []

    for tag in tags.split(","):
      tag = unicode(tag.strip())

      if tag:
        tags_list.append(tag)

    node.tags = tags_list

  # -------------------------------------------------------------------------------- prior_node

  node.prior_node = []
  if prior_node_list != '':
    prior_node_list = prior_node_list.split(",")

  i = 0
  while (i < len(prior_node_list)):
    node_id = ObjectId(prior_node_list[i])
    if gcollection.Node.one({"_id": node_id}):
      node.prior_node.append(node_id)
    
    i = i+1
 

  # -------------------------------------------------------------------------------- collection

  node.collection_set = []
  if collection_list != '':
      collection_list = collection_list.split(",")

  i = 0
  while (i < len(collection_list)):
    node_id = ObjectId(collection_list[i])
    
    if gcollection.Node.one({"_id": node_id}):
      node.collection_set.append(node_id)
    
    i = i+1
 
  # -------------------------------------------------------------------------------- Module

  node.collection_set = []
  if module_list != '':
      collection_list = module_list.split(",")

  i = 0
  while (i < len(collection_list)):
    node_id = ObjectId(collection_list[i])
    
    if gcollection.Node.one({"_id": node_id}):
      node.collection_set.append(node_id)
    
    i = i+1
 
    
  # ------------------------------------------------------------------------------- org-content
  if content_org:
    node.content_org = unicode(content_org)
    
    # Required to link temporary files with the current user who is modifying this document
    usrname = request.user.username
    filename = slugify(name) + "-" + usrname + "-"
    node.content = org2html(content_org, file_prefix=filename)

  # ----------------------------------------------------------------------------- visited_location in author class
  if user_last_visited_location:
    
    user_last_visited_location = list(ast.literal_eval(user_last_visited_location))

    author = gcollection.Node.one({'_type': "GSystemType", 'name': "Author"})
    user_group_location = gcollection.Node.one({'_type': "Author", 'member_of': author._id, 'created_by': usrid, 'name': usrname})

    if user_group_location:

      if node._type == "Author" and user_group_location._id == node._id:
        node['visited_location'] = user_last_visited_location

      else:
        user_group_location['visited_location'] = user_last_visited_location
        user_group_location.save()

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
          rev_no=rev_no.strip(' ')
       if line.find('status')!=-1:
          up_ind=line.find('status')
          if line.find(('PUBLISHED'),up_ind) !=-1:
               rev_no=rev_no.strip(' ')
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
     node1,ver1=get_versioned_page(node)
     node2,ver2=get_user_page(request,node)     
     
     if  ver2 != '1.1':                           
	    if node2 is not None:
		print "direct"
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

def parse_template_data(field_data_type, field_value, **kwargs):
  """
  Pareses the value fetched from request (GET/POST) object based on the data-type of the given field.

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
        field_value = str(field_value)

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
        field_value = bool(int(field_value))

      elif field_data_type == "ObjectId":
        field_value = ObjectId(field_value)

      else:
        error_message = "Unknown data-type ("+field_data_type+") found"
        raise Exception(error_message)

      # print "\n parsed field_value: ", field_value

    elif type(field_data_type) == list:
      # Write code...
      if not field_value:
        return []

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
      
    elif type(field_data_type) == dict:
      # Write code...
      if not field_value:
        return {}

    elif type(field_data_type) == mongokit.operators.IS:
      # Write code...
      if not field_value:
        return None

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


def create_grelation(subject_id, relation_type_node, right_subject_id):
  gr_node = None

  try:
    gr_node = collection.Triple.one({'_type': "GRelation", 
                                     'subject': subject_id, 
                                     'relation_type': relation_type_node.get_dbref(),
                                     'right_subject': right_subject_id
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
      info_message = " GRelation ("+gr_node.name+") already exists !\n"
      print "\n", info_message

    return gr_node

  except Exception as e:
      error_message = "\n GRelationCreateError: " + str(e) + "\n"
      raise Exception(error_message)
