''' -- imports from python libraries -- '''
# import os -- Keep such imports here

''' -- imports from installed packages -- '''
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.org2any import org2html
import re
######################################################################################################################################

db = get_database()

#######################################################################################################################################
#                                                                       C O M M O N   M E T H O D S   D E F I N E D   F O R   V I E W S
#######################################################################################################################################

def get_forum_repl_type(forrep_id):
  coln=db[GSystem.collection_name]
  forum_st = coln.GSystemType.one({'$and':[{'_type':'GSystemType'},{'name':GAPPS[5]}]})
  obj=coln.GSystem.one({'_id':ObjectId(forrep_id)})
  if obj:
    if forum_st._id in obj.member_of:
      return "Forum"
    else:    
      return "Reply"
  else:
    return "None"

def check_existing_group(groupname):
  col_Group = db[Group.collection_name]
  gpn=groupname
  colg = col_Group.Group.find({'_type': u'Group', "name":gpn})
  if colg.count() >= 1:
    return True
  else:
    return False

def get_drawers(group_name, nid=None, nlist=[], checked=None):
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
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$all':[gst_page_id]}, 'group_set': {'$all': [group_name]}})
        
      elif checked == "File":         
        drawer = collection.Node.find({'_type': u"File", 'group_set': {'$all': [group_name]}})
        
      elif checked == "Image":         
        drawer = collection.Node.find({'_type': u"File", 'mime_type': {'$exists': True, '$nin': [u'video']}, 'group_set': {'$all': [group_name]}})

      elif checked == "Video":         
        drawer = collection.Node.find({'_type': u"File", 'mime_type': u"video", 'group_set': {'$all': [group_name]}})

      elif checked == "Quiz":
        # For prior-node-list
        drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, 'group_set': {'$all': [group_name]}})

      elif checked == "QuizObj":
        # For collection-list
        gst_quiz_id = collection.Node.one({'_type': "GSystemType", 'name': "Quiz"})._id
        gst_quiz_item_id = collection.Node.one({'_type': "GSystemType", 'name': "QuizItem"})._id
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$in':[gst_quiz_id, gst_quiz_item_id]}, 'group_set': {'$all': [group_name]}})

      elif checked == "OnlyQuiz":
        gst_quiz_id = collection.Node.one({'_type': "GSystemType", 'name': "Quiz"})._id
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$all':[gst_quiz_id]}, 'group_set': {'$all': [group_name]}})

      elif checked == "QuizItem":
        gst_quiz_item_id = collection.Node.one({'_type': "GSystemType", 'name': "QuizItem"})._id
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$all':[gst_quiz_item_id]}, 'group_set': {'$all': [group_name]}})

      elif checked == "Group":
        drawer = collection.Node.find({'_type': u"Group"})

      elif checked == "Forum":
        gst_forum_id = collection.Node.one({'_type': "GSystemType", 'name': "Forum"})._id
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$all':[gst_forum_id]}, 'group_set': {'$all': [group_name]}})
      
      elif checked == "Module":
        gst_module_id = collection.Node.one({'_type': "GSystemType", 'name': "Module"})._id
        drawer = collection.Node.find({'_type': u"GSystem", 'member_of': {'$all':[gst_module_id]}, 'group_set': {'$all': [group_name]}})
    
        
    else:
      drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, 'group_set': {'$all': [group_name]}})   
           
    
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


def get_node_common_fields(request, node, group_name, node_type):
  """Updates the retrieved values of common fields from request into the given node.
  """
  
  gcollection = db[Node.collection_name]

  collection = None  

  name = request.POST.get('name')
  usrid = int(request.user.id)
  access_policy = request.POST.get("login-mode", '') 

  tags = request.POST.get('tags')
  prior_node_list = request.POST.get('prior_node_list','')
  collection_list = request.POST.get('collection_list','')
  module_list = request.POST.get('module_list','')
  content_org = request.POST.get('content_org')
  print module_list,"test"
  # --------------------------------------------------------------------------- For create only
  if not node.has_key('_id'):
    
    node.created_by = usrid
    #Adding the page for moderation
    col_Group = db[Group.collection_name]
    grname = re.split(r'[/=]', request.path)
    colg = col_Group.Group.one({'_type':u'Group','name':grname[1]+"Mod"})
    print "above block executed"
    if grname[1] in colg.group_set:
       print "if block executed"
       node.group_set.append(unicode(grname[1]+"Mod"))
    
    node.member_of.append(node_type._id)
  
    if access_policy == "PUBLIC":
      node.access_policy = unicode(access_policy)      
    else:
      node.access_policy = unicode(access_policy)    
          
    # End of if

  # --------------------------------------------------------------------------- For create/edit
  node.name = unicode(name)

  if access_policy == "PUBLIC":
      node.access_policy = u"PUBLIC"      
  else:
      node.access_policy = u"PRIVATE"    

  print node.access_policy
  print node.access_policy

  #node.modified_by.append(usrid)
  if usrid not in node.modified_by:
  #if usrid in node.modified_by:
    node.modified_by.insert(0,usrid)
  else:
    node.modified_by.remove(usrid)
    node.modified_by.insert(0,usrid)

  if group_name not in node.group_set:
    node.group_set.append(group_name)

  node.tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]

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


  

# ------ Some work for relational graph - (II) ------
def neighbourhood_nodes(page_node):

  collection = db[Node.collection_name]
        
  gs = collection.Node.find( {'$or':[{'_type':'GSystem'},{'_type':'File'}]}  )
  gs_cur = []

  for each in gs:
      gs_cur.append(each)

  gs.rewind()

  flag = False

  # Initiate and append this line compulsory for viewing node.
  graphData = '{"name":"'+ page_node.name +'", "degree":1, "children":['

  # Scan each document in cursor 'gs'
  for val in gs:
    
    # If vieving page _id exist in collection set of current document
    if page_node._id in val.collection_set:
      
      flag = True      
      # Start adding children 
      graphData += '{"name":"'+ val.name +'","degree" : 2'   #},'
      
      # If there is only one matching item in collection set
      if len(val.collection_set) == 1:
        graphData += '},'
        
      # If there is more than one _id in collection set, start adding children of children.
      elif len(val.collection_set) > 1:
        graphData += ', "children":['
        
        for each in val.collection_set:
          node_name = (filter( lambda x: x['_id'] == each, gs_cur ))[0].name
          
          # Escape name matching current page node name
          if(page_node._id == each):
            pass
          else:
            graphData += '{"name":"'+ node_name + '"},'

        graphData = graphData[:-1] + ']},'

  if flag:
    graphData = graphData[:-1] + ']}' 
  else:
    graphData += ']}' 

  return graphData
# ------ End of processing for graph ------



# ------ Some work for node graph - (II) ------
def graph_nodes(page_node):
  
  collection = db[Node.collection_name]
        
  def _get_node_info(node_id):
    node = collection.Node.one( {'$or':[{'_type':'GSystem'},{'_type':'File'}], '_id':node_id}  )
    return node.name

  # def _get_username(id_int):
    # return User.objects.get(id=id_int).username

  page_node_id = str(id(page_node._id))
  node_metadata ='{"screen_name":"' + page_node.name + '", "_id":"'+ page_node_id +'", "refType":"GSystem"}, '
  node_relations = ''
  exception_items = [
                      "name", "content", "_id", "login_required", "attribute_set",
                      "member_of", "status", "comment_enabled", "start_publication",
                      "_type", "modified_by", "created_by", "last_update", "url", "featured",
                      "created_at", "group_set", "type_of", "content_org", "author_set"
                    ]

  # username = User.objects.get(id=page_node.created_by).username

  i = 1
  for key, value in page_node.items():
    
    if key in exception_items:
      pass

    elif isinstance(value, list) and len(value):

      node_metadata +='{"screen_name":"' + key + '", "_id":"'+ str(i) +'_r"}, '
      node_relations += '{"type":"'+ key +'", "from":"'+ str(id(page_node._id)) +'", "to": "'+ str(i) +'_r"},'
      key_id = str(i)
      # i += 1
      
      # if key in ("modified_by", "author_set"):
      #   for each in value:
      #     node_metadata += '{"screen_name":"' + _get_username(each) + '", "_id":"'+ str(i) +'_n"},'
      #     node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(i) +'_n"},'
      #     i += 1

      # else:
      for each in value:
          if isinstance(each, ObjectId):
            node_name = _get_node_info(each)          
            node_metadata += '{"screen_name":"' + node_name + '", "_id":"'+ str(each) +'_n"},'
          
            node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(each) +'_n"},'
            i += 1
          else:
            node_metadata += '{"screen_name":"' + each + '", "_id":"'+ str(each) +'_n"},'
            node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(each) +'_n"},'
            i += 1
    
    else:
      node_metadata +='{"screen_name":"' + key + '", "_id":"'+ str(i) +'_r"},'
      node_relations += '{"type":"'+ key +'", "from":"'+ str(id(page_node._id)) +'", "to": "'+ str(i) +'_r"},'
      key_id = str(i)      

      if isinstance( value, list):
        for each in value:
          node_metadata += '{"screen_name":"' + each + '", "_id":"'+ str(i) +'_n"},'
          node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(i) +'_n"},'
          i += 1 
      
      else:
        node_metadata += '{"screen_name":"' + str(value) + '", "_id":"'+ str(i) +'_n"},'
        node_relations += '{"type":"'+ key +'", "from":"'+ str(i) +'_r", "to": "'+ str(i) +'_n"},'
        i += 1 
    # End of if - else
  # End of for loop

  node_metadata = node_metadata[:-1]
  node_relations = node_relations[:-1]

  node_graph_data = '{ "node_metadata": [' + node_metadata + '], "relations": [' + node_relations + '] }'

  return node_graph_data

# ------ End of processing for graph ------
