''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
from difflib import HtmlDiff

''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django_mongokit import get_database
from gnowsys_ndf.settings import LANGUAGES
from django.utils.translation import ugettext as _  

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import Node, GSystem, Triple
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.org2any import org2html

from gnowsys_ndf.ndf.views.methods import get_node_common_fields, get_translate_common_fields,get_page,get_resource_type,diff_string,get_node_metadata,create_grelation_list

from gnowsys_ndf.ndf.management.commands.data_entry import create_gattribute

from gnowsys_ndf.ndf.views.methods import get_versioned_page, get_page, get_resource_type, diff_string
from gnowsys_ndf.ndf.templatetags.ndf_tags import group_type_info

from gnowsys_ndf.mobwrite.diff_match_patch import diff_match_patch


#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]
collection_tr = db[Triple.collection_name]
gst_page = collection.Node.one({'_type': 'GSystemType', 'name': GAPPS[0]})
history_manager = HistoryManager()
rcs = RCS()
app=collection.Node.one({'name':u'Page','_type':'GSystemType'})

#######################################################################################################################################
# VIEWS DEFINED FOR GAPP -- 'PAGE'
#######################################################################################################################################

def page(request, group_id, app_id=None):
    """Renders a list of all 'Page-type-GSystems' available within the database.
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id}) 
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })

        if group_ins:
            group_id = str(group_ins._id)
          
            print group_id
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
           

            if auth :
                group_id = str(auth._id)
    else :
        pass
    if app_id is None:  
        app_ins = collection.Node.find_one({'_type':"GSystemType", "name":"Page"})
        if app_ins:
            app_id = str(app_ins._id)
        
    content=[]
    version=[]
    con=[]
    group_object=collection.Group.one({'_id':ObjectId(group_id)})

    # Code for user shelf
    shelves = []
    shelf_list = {}
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
    # End of user shelf

    if request.method == "POST":
    
      title = gst_page.name
      search_field = request.POST['search_field']
      page_nodes = collection.Node.find({
                                          'member_of': {'$all': [ObjectId(app_id)]},
                                          '$or': [
                                            {'$and': [
                                              {'name': {'$regex': search_field, '$options': 'i'}}, 
                                              {'$or': [
                                                {'access_policy': u"PUBLIC"},
                                                {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
                                                ]
                                              }
                                              ]
                                            },
                                            {'$and': [
                                              {'tags': {'$regex':search_field, '$options': 'i'}},
                                              {'$or': [
                                                {'access_policy': u"PUBLIC"},
                                                {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
                                                ]
                                              }
                                              ]
                                            }
                                          ], 
                                          'group_set': {'$all': [ObjectId(group_id)]},
                                          'status': {'$nin': ['HIDDEN']}
                                      }).sort('last_update', -1)
    
      return render_to_response("ndf/page_list.html",
                                {'title': title, 
                                 'appId':app._id,'shelf_list': shelf_list,'shelves': shelves,
                                 'searching': True, 'query': search_field,
                                 'page_nodes': page_nodes, 'groupid':group_id, 'group_id':group_id
                                }, 
                                context_instance=RequestContext(request)
      )

    elif gst_page._id == ObjectId(app_id):
        # Page list view 
        # code for moderated Groups
        # collection.Node.reload()
        group_type = collection.Node.one({'_id':ObjectId(group_id)})
        group_info=group_type_info(group_id)

        title = gst_page.name

        if  group_info == "Moderated":
          
          title = gst_page.name
          node=group_type.prior_node[0]
          page_nodes = collection.Node.find({'member_of': {'$all': [ObjectId(app_id)]},
                                             'group_set': {'$all': [ObjectId(node)]},
                                       }).sort('last_update', -1)

          return render_to_response("ndf/page_list.html",
                                    {'title': title, 
                                     'appId':app._id,'shelf_list': shelf_list,'shelves': shelves,
                                     'page_nodes': page_nodes, 'groupid':group_id, 'group_id':group_id
                                    }, 
                                    context_instance=RequestContext(request))
        
        elif group_info == "BaseModerated":
          #code for parent Groups
          node = collection.Node.find({'member_of': {'$all': [ObjectId(app_id)]}, 
                                       'group_set': {'$all': [ObjectId(group_id)]},                                           
                                       'status': {'$nin': ['HIDDEN']}
                                      }).sort('last_update', -1)

          if node is None:
            node = collection.Node.find({'member_of':ObjectId(app_id)})

          for nodes in node:
            node,ver=get_versioned_page(nodes) 
            content.append(node)  

                    
          # rcs content ends here
          
          return render_to_response("ndf/page_list.html",
                                    {'title': title, 
                                     'appId':app._id,
                                     'shelf_list': shelf_list,'shelves': shelves,
                                     'page_nodes':content,
                                     'groupid':group_id,
                                     'group_id':group_id
                                    }, 
                                    context_instance=RequestContext(request)
            )

        elif group_info == "PUBLIC" or group_info == "PRIVATE" or group_info is None:
          """
          Below query returns only those documents:
          (a) which are pages,
          (b) which belongs to given group,
          (c) which has status either as DRAFT or PUBLISHED, and 
          (d) which has access_policy either as PUBLIC or if PRIVATE then it's created_by must be the logged-in user
          """
          page_nodes = collection.Node.find({'member_of': {'$all': [ObjectId(app_id)]},
                                             'group_set': {'$all': [ObjectId(group_id)]},
                                             '$or': [
                                              {'access_policy': u"PUBLIC"},
                                              {'$and': [
                                                {'access_policy': u"PRIVATE"}, 
                                                {'created_by': request.user.id}
                                                ]
                                              }
                                             ],
                                             'status': {'$nin': ['HIDDEN']}
                                         }).sort('last_update', -1)

          # content =[]
          # for nodes in page_nodes:
        		# node,ver=get_page(request,nodes)
          #   if node != 'None':
          #     content.append(node)	

          return render_to_response("ndf/page_list.html",
                                    {'title': title,
                                     'appId':app._id,
                                     'shelf_list': shelf_list,'shelves': shelves,
                                     'page_nodes': page_nodes,
                                     'groupid':group_id,
                                     'group_id':group_id
                                    },
                                    context_instance=RequestContext(request))
        
    else:
        #Page Single instance view
        Group_node = collection.Node.one({"_id": ObjectId(group_id)})                
       
        if Group_node.prior_node: 
            page_node = collection.Node.one({"_id": ObjectId(app_id)})            
            
        else:
          node = collection.Node.one({"_id":ObjectId(app_id)})
          if Group_node.edit_policy == "EDITABLE_NON_MODERATED" or Group_node.edit_policy is None or Group_node.edit_policy == "NON_EDITABLE":
            page_node,ver=get_page(request,node)
          else:
            #else part is kept for time being until all the groups are implemented
            if node.status == u"DRAFT":
              page_node,ver=get_versioned_page(node)
            elif node.status == u"PUBLISHED":
              page_node = node

      
        # First time breadcrumbs_list created on click of page details
        breadcrumbs_list = []
        # Appends the elements in breadcrumbs_list first time the resource which is clicked
        breadcrumbs_list.append( (str(page_node._id), page_node.name) )

        
 
        annotations = json.dumps(page_node.annotations)
        page_node.get_neighbourhood(page_node.member_of)
        return render_to_response('ndf/page_details.html', 
                                  { 'node': page_node,
                                    'appId':app._id,
                                    'group_id': group_id,
                                    'shelf_list': shelf_list,
                                    'annotations': annotations,
                                    'shelves': shelves,
                                    'groupid':group_id,
                                    'breadcrumbs_list': breadcrumbs_list
                                  },
                                  context_instance = RequestContext(request)
        )        



@login_required
def create_edit_page(request, group_id, node_id=None):
    """Creates/Modifies details about the given quiz-item.
    """
    ins_objectid = ObjectId()
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

    context_variables = { 'title': gst_page.name,
                          'group_id': group_id,
                          'groupid': group_id
                      }
    
    available_nodes = collection.Node.find({'_type': u'GSystem', 'member_of': ObjectId(gst_page._id) })

    nodes_list = []
    for each in available_nodes:
      nodes_list.append(each.name)

    if node_id:
        page_node = collection.Node.one({'_type': u'GSystem', '_id': ObjectId(node_id)})
    else:
        page_node = collection.GSystem()
        

    if request.method == "POST":
        # get_node_common_fields(request, page_node, group_id, gst_page)
        page_node.save(is_changed=get_node_common_fields(request, page_node, group_id, gst_page))

        # To fill the metadata info while creating and editing page node
        metadata = request.POST.get("metadata_info", '') 
        if metadata:
          # Only while metadata editing
          if metadata == "metadata":
            if page_node:
              get_node_metadata(request,page_node)
        # End of filling metadata

        return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'app_id': page_node._id }))

    else:
        if node_id:

            page_node,ver=get_page(request,page_node)
            page_node.get_neighbourhood(page_node.member_of)
            context_variables['node'] = page_node
            context_variables['groupid']=group_id
            context_variables['group_id']=group_id
            context_variables['nodes_list'] = json.dumps(nodes_list)
        else:
            context_variables['nodes_list'] = json.dumps(nodes_list)

        return render_to_response("ndf/page_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
                              )


@login_required    
def delete_page(request, group_id, node_id):
    """Change the status to Hidden.
    
    Just hide the page from users!
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
    op = collection.update({'_id': ObjectId(node_id)}, {'$set': {'status': u"HIDDEN"}})
    return HttpResponseRedirect(reverse('page', kwargs={'group_id': group_id}))





def version_node(request, group_id, node_id, version_no):
    """Renders either a single or compared version-view based on request.

    In single version-view, all information of the node for the given version-number 
    is provided.

    In compared version-view, comparitive information in tabular form about the node 
    for the given version-numbers is provided.
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

    d=diff_match_patch()

    view = ""          # either single or compare
    selected_versions = {}
    node = collection.Node.one({"_id": ObjectId(node_id)})
    node1 = collection.Node.one({"_id": ObjectId(node_id)})
    fp = history_manager.get_file_path(node)

    if request.method == "POST":
        view = "compare"

        version_1 = request.POST["version_1"]
        version_2 = request.POST["version_2"]
        diff = get_html_diff(fp, version_1, version_2)
	selected_versions = {"1": version_1, "2": version_2}
   	doc=history_manager.get_version_document(node,version_1)
	doc1=history_manager.get_version_document(node,version_2)     
        
        for i in node1:
	   try:
    
    	       s=d.diff_compute(str(doc[i]),str(doc1[i]),True)
               l=diff_prettyHtml(s)
	       node1[i]=l
           except:
                node1[i]=node1[i]		       
           
        
    
        content = node1
        content_1=doc
        
        
	
    else:
        view = "single"

        # Retrieve rcs-file for a given version-number
        rcs.checkout((fp, version_no))

        # Copy content from rcs-version-file
        data = None
        with open(fp, 'r') as sf:
            data = sf.read()

        # Used json.loads(x) -- to covert string to dictionary object
        # If want to use key from this converted dictionay, use array notation because dot notation doesn't works!
        data = json.loads(data)

        # Remove retrieved rcs-file belonging to the given version-number
        rcs.checkin(fp)

        selected_versions = {"1": version_no, "2": ""}
        content = data
        content_1='none'
    return render_to_response("ndf/version_page.html",
                              {'view': view,
                               'node': node,
                               'appId':app._id,
                               'group_id':group_id,
                               'groupid':group_id,
                               'selected_versions': selected_versions,
                               'content': content,
                               'content1':content_1,
                               
                              },
                              context_instance = RequestContext(request)
    )        


def diff_prettyHtml(diffs):
    """Convert a diff array into a pretty HTML report.

    Args:
      diffs: Array of diff tuples.

    Returns:
      HTML representation.
    """
    html = []
    DIFF_DELETE = -1
    DIFF_INSERT = 1
    DIFF_EQUAL = 0
    i = 0
    for (op, data) in diffs:
      text = (data.replace("&", "&amp;").replace("<", "&lt;")
                 .replace(">", "&gt;").replace("\n", "<BR>"))
      if op == DIFF_INSERT:
        html.append("<INS STYLE=\"background:#b3ffb3;\" TITLE=\"i=%i\">%s</INS>"
            % (i, text))
      elif op == DIFF_DELETE:
        html.append("<DEL STYLE=\"background:#ffb3b3;\" TITLE=\"i=%i\">%s</DEL>"
            % (i, text))
      elif op == DIFF_EQUAL:
        html.append("<SPAN TITLE=\"i=%i\">%s</SPAN>" % (i, text))
      if op != DIFF_DELETE:
        i += len(data)
    return "".join(html)


def translate_node(request,group_id,node_id=None):
    """ translate the node content"""
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

    context_variables = { 'title': gst_page.name,
                          'group_id': group_id,
                          'groupid': group_id
                      }
    if request.method == "POST":
        get_type=get_resource_type(request, node_id)
        page_node = eval("collection"+"."+ get_type)()
        get_translate_common_fields(request, get_type,page_node, group_id, gst_page,node_id)
        page_node.save()
        # add triple to the GRelation 
        # then append this ObjectId of GRelation instance in respective subject and object Nodes' relation_set field.
        relation_type=collection.Node.one({'$and':[{'name':'translation_of'},{'_type':'RelationType'}]})
        grelation=collection.GRelation()
        grelation.relation_type=relation_type
        grelation.subject=ObjectId(node_id)
        grelation.right_subject=page_node._id
        grelation.name=u""
        grelation.save()
        return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'app_id': page_node._id}))
        
    node = collection.Node.one({"_id": ObjectId(node_id)})
        
    fp = history_manager.get_file_path(node)
    # Retrieve rcs-file for a given version-number
    rcs.checkout(fp)
   
    # Copy content from rcs-version-file
    data = None
    with open(fp, 'r') as sf:
        data = sf.read()
       
        # Used json.loads(x) -- to covert string to dictionary object
        # If want to use key from this converted dictionay, use array notation because dot notation doesn't works!
        data = json.loads(data)

        # Remove retrieved rcs-file belonging to the given version-number
        rcs.checkin(fp)

        content = data
        node_details=[]
        for k,v in content.items():
            
            node_name = content['name']
            node_content_org=content['content_org']
            node_tags=content['tags']
            
        return render_to_response("ndf/translation_page.html",
                               {'content': content,
                                'appId':app._id,
                                'node':node,
                                'node_name':node_name,
                                'groupid':group_id,
                                'group_id':group_id
                                      },
                             
                              context_instance = RequestContext(request)
    )        


#######################################################################################################################################
#                                                                                                     H E L P E R  -  F U N C T I O N S
#######################################################################################################################################

def get_html_diff(versionfile, fromfile="", tofile=""):

    if versionfile != "":
        if fromfile == "":
            fromfile = rcs.head(versionfile)

        if tofile == "":
            tofile = rcs.head(versionfile)

        # fromfile ----------------------------------------------------------

        # Retrieve rcs-file for a given version-number (here, version-number <--> fromfile)
        rcs.checkout((versionfile, fromfile))

        # Copy content from rcs-version-file
        fromlines = None
        with open(versionfile, 'r') as ff:
            fromlines = ff.readlines()

        # Remove retrieved rcs-file belonging to the given version-number
        rcs.checkin(versionfile)

        # tofile ------------------------------------------------------------

        # Retrieve rcs-file for a given version-number (here, version-number <--> tofile)
        rcs.checkout((versionfile, tofile))

        # Copy content from rcs-version-file
        tolines = None
        with open(versionfile, 'r') as tf:
            tolines = tf.readlines()

        # Remove retrieved rcs-file belonging to the given version-number
        rcs.checkin(versionfile)
        #---------------------------------------------
        
        fromfile = "Version #" + fromfile
        tofile = "Version #" + tofile
       
        
        return HtmlDiff(wrapcolumn=60).make_file(fromlines, tolines, fromfile, tofile)
        #return gh
    else:
        print "\n Please pass a valid rcs-version-file!!!\n"
        #TODO: Throw an error indicating the above message!
        return ""
        
def publish_page(request,group_id,node):
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

    node=collection.Node.one({'_id':ObjectId(node)})
    group=collection.Node.one({'_id':ObjectId(group_id)})
    if group.post_node:
        node.status=unicode("PUBLISHED")
        node.save('UnderModeration')
    else:
        page_node,v=get_page(request,node)
        node.content = unicode(page_node.content)
        node.content_org = unicode(page_node.content_org)
        node.status = unicode("PUBLISHED")
        node.modified_by = int(request.user.id)
        node.save() 
    #no need to use this section as seprate view is created for group publish
    #if node._type == 'Group':
    # return HttpResponseRedirect(reverse('groupchange', kwargs={'group_id': group_id}))    

    return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'app_id': node._id}))


def merge_doc(request,group_id,node_id,version_1,version_2):
     node=collection.Node.one({'_id':ObjectId(node_id)})
     doc=history_manager.get_version_document(node,version_1)
     doc2=history_manager.get_version_document(node,version_2)
     a=doc.content_org
     b=doc2.content_org
     c=doc.content
     d=doc2.content   
     con2=diff_string(a,b)
     con3=diff_string(c,d)
     doc2.update(doc)
     for attr in node:
       if attr != '_type':
        try:
		node[attr] = doc2[attr];
        except:
		node[attr]=node[attr]
     doc2.content_org=con2
     doc2.content=con3
     node.content_org=doc2.content_org
     node.content=doc2.content
     node.modified_by=request.user.id
     node.save()
     update_mobwrite = update_mobwrite_content_org(node)
     ver=history_manager.get_current_version(node)
     view='merge'
     
     return render_to_response("ndf/version_page.html",
                               {'view': view,
                                'appId':app._id,
                                'version_no':version_1,
                                'node':node,
                                'groupid':group_id,
                                'group_id':group_id,
                                'content':node,
                                'ver':ver
                               },
                             
                              context_instance = RequestContext(request)
    )        

  
  
def revert_doc(request,group_id,node_id,version_1):
   node=collection.Node.one({'_id':ObjectId(node_id)})
   group=collection.Node.one({'_id':ObjectId(group_id)})
   doc=history_manager.get_version_document(node,version_1)
   
   print node
   
   for attr in node:
      if attr != '_type':
            try:
	    	node[attr] = doc[attr];
            except:
		node[attr] =node[attr]
   node.modified_by=request.user.id
   node.save()
   update_mobwrite = update_mobwrite_content_org(node)
   view ='revert'
   ver=history_manager.get_current_version(node)
   selected_versions=selected_versions = {"1": version_1, "2": ""}
   
   return render_to_response("ndf/version_page.html",
                               {'view': view,
                                'appId':app._id,
                                'selected_versions': selected_versions, 
                                'node':node,
                                'groupid':group_id,
                                'group_id':group_id,
                                'content':node,
                                'ver':ver    
                           
                               },
                             
                              context_instance = RequestContext(request)
    )
			  
