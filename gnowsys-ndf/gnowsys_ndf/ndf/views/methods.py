''' -- imports from python libraries -- '''
# import os -- Keep such imports here

''' -- imports from installed packages -- '''
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.org2any import org2html

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
    if obj.member_of in forum_st.name:
          if obj.member_of in "Forum":
             return "Forum"
          else:    
             return "Reply"
    else:
          return "None"
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
    dict2 = {}

    gst_collection = db[GSystemType.collection_name]
    gs_collection = db[GSystem.collection_name]
    
    drawer = None    
    
    if checked:     
      if checked == "Page":
        # drawer = gs_collection.GSystem.find({'_type': u"GSystem", 'gsystem_type': {'$all': [ObjectId(gst_page._id)]}, 'group_set': {'$all': [group_name]}})
        drawer = gs_collection.GSystem.find({'_type': u"GSystem", 'member_of': {'$all':[u'Page']}, 'group_set': {'$all': [group_name]}})
        
      elif checked == "File":         
        drawer = gs_collection.GSystem.find({'_type': u"File", 'group_set': {'$all': [group_name]}})
        # drawer = gs_collection.GSystem.find({'_type': u"File"})
        
      elif checked == "Image":         
        drawer = gs_collection.GSystem.find({'_type': u"File", 'mime_type': {'$exists': True, '$nin': [u'video']}, 'group_set': {'$all': [group_name]}})
        # drawer = gs_collection.GSystem.find({'_type': u"File", 'mime_type': u"image/jpeg", 'group_set': {'$all': [group_name]}})
        # drawer = gs_collection.GSystem.find({'_type': u"File", 'mime_type': u"image/jpeg"})

      elif checked == "Video":         
        drawer = gs_collection.GSystem.find({'_type': u"File", 'mime_type': u"video", 'group_set': {'$all': [group_name]}})
        # drawer = gs_collection.GSystem.find({'_type': u"File", 'mime_type': u"video"})

      elif checked == "Quiz":
        drawer = gs_collection.GSystem.find({'_type': {'$in' : [u"GSystem", u"File"]}, 'group_set': {'$all': [group_name]}})

      elif checked == "QuizItem":
        drawer = gs_collection.GSystem.find({'_type': u"GSystem", 'member_of': {'$all':[u'QuizItem']}, 'group_set': {'$all': [group_name]}})

    else:
      drawer = gs_collection.GSystem.find({'_type': {'$in' : [u"GSystem", u"File"]}, 'group_set': {'$all': [group_name]}})   


    if (nid is None) and (not nlist):
      for each in drawer:                      
        
        dict_drawer[each._id] = each

    elif (nid is None) and (nlist):
      for each in drawer:
        if each._id not in nlist:          
            
          dict1[each._id] = each

      for oid in nlist: 
        obj = gs_collection.GSystem.one({'_id': oid})        
                 
        dict2[oid] = obj

      dict_drawer['1'] = dict1
      dict_drawer['2'] = dict2
        
    else:
      for each in drawer:
        if each._id != nid:          
          if each._id not in nlist:  
            
            dict1[each._id] = each
          
          else: 
                
            dict2[each._id] = each
      
      dict_drawer['1'] = dict1
      dict_drawer['2'] = dict2

    return dict_drawer


    '''if (nid is None) and (not nlist):
      for each in drawer:   
        user = User.objects.get(pk=each.created_by).username 
        content = each.content_org        
        if content != None:
            content = content[:100] 
        else: 
            content = u"No description !"
            
        #dict_drawer[each._id] = [each.name, user, each.created_at, content]
        dict_drawer[each._id] = each

    elif (nid is None) and (nlist):
      for each in drawer:
        if each._id not in nlist:
          user = User.objects.get(pk=each.created_by).username
          content = each.content_org        
          if content != None:
            content = content[:100] 
          else: 
            content = u"No description."
            
          dict1[each._id] = [each.name, user, each.created_at, content]

      for oid in nlist: 
        obj = gs_collection.GSystem.one({'_id': oid})
        user = User.objects.get(pk=obj.created_by).username
        content = obj.content_org        
        if content != None:
            content = content[:100] 
        else: 
            content = u"No description."
                 
        dict2[oid] = [obj.name, user, obj.created_at, content]

      dict_drawer['1'] = dict1
      dict_drawer['2'] = dict2
        
    else:
      for each in drawer:
        if each._id != nid:
          user = User.objects.get(pk=each.created_by).username
          content = each.content_org  
          if each._id not in nlist:                    
            if content != None:
                content = content[:100] 
            else: 
                content = u"No description."
            
            dict1[each._id] = [each.name, user, each.created_at, content]
          
          else:            
            if content != None:
                content = content[:100] 
            else: 
                content = u"No description."
                
            dict2[each._id] = [each.name, user, each.created_at, content]
      
      dict_drawer['1'] = dict1
      dict_drawer['2'] = dict2

    return dict_drawer'''


def get_node_common_fields(request, node, group_name, node_type):
  """Updates the retrieved values of common fields from request into the given node.
  """
  gs_collection = db[GSystem.collection_name]

  collection = None
  private = None

  name = request.POST.get('name')
  usrid = int(request.user.id)
  private = request.POST.get("private_cb", '')
  tags = request.POST.get('tags')
  prior_node_list = request.POST['prior_node_list']
  collection_list = request.POST['collection_list']
  content_org = request.POST.get('content_org')

  # --------------------------------------------------------------------------- For create only
  if not node.has_key('_id'):
    
    node.created_by = usrid
    node.member_of.append(node_type.name)
    node.gsystem_type.append(node_type._id)
  
    if private:
      private = True
    else:
      private = False

    # End of if

  # --------------------------------------------------------------------------- For create/edit
  node.name = unicode(name)

  if usrid not in node.modified_by:
    node.modified_by.append(usrid)

  if group_name not in node.group_set:
    node.group_set.append(group_name)

  node.tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]

  # -------------------------------------------------------------------------------- prior_node
  node.prior_node = []
  if prior_node_list != '':
    prior_node_list = prior_node_list.split(",")
  
  i = 0
  while (i < len(prior_node_list)):
    pn_name = prior_node_list[i]    
    pn_name = pn_name.replace("'", "")        
    objs = gs_collection.GSystem.one({'_type': {'$in' : [u"GSystem", u"File"]}, 'name': pn_name})       
    node.prior_node.append(objs._id)    
    i = i+1

  # -------------------------------------------------------------------------------- collection
  node.collection_set = []
  if collection_list != '':
      collection_list = collection_list.split(",")

  i = 0                    
  while (i < len(collection_list)):                    
    c_name = collection_list[i]    
    c_name = c_name.replace("'", "")
    #print c_name
    objs = gs_collection.GSystem.one({'_type': {'$in' : [u"GSystem", u"File"]}, 'name': c_name})
    #print objs
    node.collection_set.append(objs._id)
    i = i+1
      
  # ------------------------------------------------------------------------------- org-content
  if content_org:
    node.content_org = unicode(content_org)
    
    # Required to link temporary files with the current user who is modifying this document
    usrname = request.user.username
    filename = slugify(name) + "-" + usrname + "-"
    node.content = org2html(content_org, file_prefix=filename)



# ------ Some work for graph ------
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