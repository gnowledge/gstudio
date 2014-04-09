''' -- imports from python libraries -- '''
# import os -- Keep such imports here

''' -- imports from installed packages -- '''
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.org2any import org2html

from gnowsys_ndf.ndf.models import HistoryManager
import subprocess
import re
import ast
import string
######################################################################################################################################

db = get_database()
history_manager = HistoryManager()
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

def check_existing_group(group_name):
  collection = db[Node.collection_name]

  if type(group_name) == 'unicode':
    colg = collection.Node.find({'_type': u'Group', "name": group_name})
  else:
    colg = collection.Node.find({'_type': u'Group', "_id": group_name._id})

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

def get_translate_common_fields(request, node, group_id, node_type, node_id):
  """ retrive & update the common fields required for translation of the node """

  gcollection = db[Node.collection_name]
  usrid = int(request.user.id)
  content_org = request.POST.get('content_org')
  name = request.POST.get('name')
  usrid = int(request.user.id)
  language= request.POST.get('lan')
  if not node.has_key('_id'):
    
    node.created_by = usrid
    node.member_of.append(node_type._id)

  node.name = unicode(name)
  node.language=unicode(language)

  node.modified_by = usrid

  if usrid not in node.contributors:
    node.contributors.append(usrid)

  group_obj=gcollection.Node.one({'_id':ObjectId(group_id)})
  if group_obj._id not in node.group_set:
    node.group_set.append(group_obj._id)

  if content_org:
    node.content_org = unicode(content_org)
    node.name=unicode(name)
    # Required to link temporary files with the current user who is modifying this document
    usrname = request.user.username
    filename = slugify(name) + "-" + usrname + "-"
    node.content = org2html(content_org, file_prefix=filename)

  

def get_node_common_fields(request, node, group_id, node_type):
  """Updates the retrieved values of common fields from request into the given node."""
  print"has come here"
  gcollection = db[Node.collection_name]
  group_obj=gcollection.Node.one({'_id':ObjectId(group_id)})
  collection = None

  name = request.POST.get('name')
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
  
  if map_geojson_data:
    map_geojson_data = map_geojson_data + ","
    map_geojson_data = list(ast.literal_eval(map_geojson_data))
  else:
    map_geojson_data = []
  
  # --------------------------------------------------------------------------- For create only
  if not node.has_key('_id'):
    
    node.created_by = usrid
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
  node.status = unicode("DRAFT")
  node.language = unicode(language) 
  node.location = map_geojson_data # Storing location data

  if access_policy:
    # Policy will be changed only by the creator of the resource
    # via access_policy(public/private) option on the template which is visible only to the creator
    if access_policy == "PUBLIC":
      node.access_policy = u"PUBLIC"
    else:
      node.access_policy = u"PRIVATE"

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



  
  
def get_versioned_page(node):
            content=[] 
       
            #check if same happens for multiple nodes
            i=node.current_version
          
            #get the particular document Document
                   
            doc=history_manager.get_version_document(node,i)

          
            #check for the published status for the particular version
          
            while (doc.status != "PUBLISHED"):
              currentRev = i

              splitVersion = currentRev.split('.')
              previousSubNumber = int(splitVersion[1]) - 1 

              if previousSubNumber <= 0:
               previousSubNumber = 1

              prev_ver=splitVersion[0] +"."+ str(previousSubNumber)
              i=prev_ver 

              doc=history_manager.get_version_document(node,i)
              if (i == '1.1'):
                  return (doc,i)
            return (doc,i)


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
          if line.find(str(request.user))!=-1:
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
		
                if node2.status == 'PUBLISHED':
			if float(ver2) > float(ver1):			
				return (node2,ver2)
			elif float(ver2) < float(ver1):
				return (node1,ver1)
			elif float(ver2) == float(ver1):
				return(node1,ver1)
		elif node2.status == 'DRAFT':
                       #========== conditions for Group===============#

                        if  node1.status == 'DRAFT' and node._type == "Group":
			    #check to perform if the person has recently joined the group
			    count=check_page_first_creation(request,node2)
                            if count == 1:
                                return (node1,ver1)
                            elif count == 2:
				return (node2,ver2)

                            
                        return (node2,ver2)  
	    else:
                        
			return(node1,ver1)		
	    
     else:
         
         if node._type == "GSystem" and node1.status == "DRAFT":
              if node1.created_by ==request.user.id:
                   return (node2,ver2)
              else:
		   return ('None','None')
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
      
