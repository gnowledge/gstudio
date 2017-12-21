from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from gnowsys_ndf.ndf.views.html_diff import htmldiff
from gnowsys_ndf.ndf.views.methods import get_versioned_page, get_page, get_resource_type, diff_string,get_published_version_list
from gnowsys_ndf.ndf.views.methods import get_group_name_id
from gnowsys_ndf.ndf.views.methods import parse_data
try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId
from gnowsys_ndf.mobwrite.diff_match_patch import diff_match_patch
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.models import HistoryManager
history_manager = HistoryManager()


def version_node(request, group_id, node_id, version_no = None):
    """Renders either a single or compared version-view based on request.

    In single version-view, all information of the node for the given version-number 
    is provided.

    In compared version-view, comparitive information in tabular form about the node 
    for the given version-numbers is provided.
    """
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    d=diff_match_patch()    
    view = ""          # either single or compare
    selected_versions = {}
    node = node_collection.one({"_id": ObjectId(node_id)})
    node1 = node_collection.one({"_id": ObjectId(node_id)})
    fp = history_manager.get_file_path(node)
    listform = ['modified_by','created_by','last_update','name','content','contributors','rating','location','access_policy',
                'type_of','status','tags','language','member_of','url','created_at','author_set',
'group_set', 'collection_set','prior_node','attribute_set', 'relation_set']
    versions= get_published_version_list(request,node)
    
    if not version_no:
       if versions:
        version_no = versions.pop()
        versions.append(version_no)
       else:
        version_no = node.current_version  
        
    
    if request.method == "POST":
        view = "compare"

        version_1 = request.POST["version_1"]
        version_2 = request.POST["version_2"]
        #diff = get_html_diff(fp, version_1, version_2)
        selected_versions = {"1": version_1, "2": version_2}
        doc=history_manager.get_version_document(node,version_1)
        doc1=history_manager.get_version_document(node,version_2)     
        parse_data(doc)
        parse_data(doc1)
        for i in node1:
           try:
           
               s=htmldiff(str(doc[i]),str(doc1[i]),True)
               node1[i]=s
           except:
                node1[i]=node1[i]		       
        content = doc 
        content_1 = node1
        
        content['content'] = doc['content'].replace("&lt;","<").replace("&gt;",">").replace("&quot;","\"")
        content_1['content'] = content_1['content'].replace("insert:"," ").replace("delete:","").replace("<tt>","").replace("</tt>","")
        content_1['content'] = content_1['content'].replace("&lt;","<").replace("&gt;",">").replace("&quot;","\"")
        
        new_content = []
        new_content1= []
        
        for i in listform:
           new_content.append({i:str(content[i])})
           new_content1.append({i:content_1[i]})
        content =  new_content
        content_1 =  new_content1
    else:
        view = "single"
        data = None
        data = history_manager.get_version_document(node,version_no)
        parse_data(data)
        new_content = []
        selected_versions = {"1": version_no, "2": ""}
        for i in listform:
           new_content.append({i:str(data[i])})
        content =  new_content
        
        #content = data
        content_1="none"
    return render_to_response("ndf/version_page.html",
                              {'view': view,
                               'node': node,
                               'group_id':group_id,
                               'groupid':group_id,
                               'selected_versions': selected_versions,
                               'content': content,
                               'content1':content_1,
                               'publishedversions':versions
                               
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
      text = (data.replace("&", "&amp;").replace("&lt;", "<")
                 .replace("&gt;", ">").replace("\n", "<br>"))
      
      
      if op == DIFF_INSERT:
        html.append("<INS STYLE=background:#b3ffb3;> %s</INS>"
            % ( text))
      elif op == DIFF_DELETE:
        html.append("<DEL STYLE=background:#ffb3b3; >%s</DEL>"
            % ( text))
      elif op == DIFF_EQUAL:
        html.append("<SPAN >%s</SPAN>" % ( text))
      if op != DIFF_DELETE:
        i += len(data)
    return "".join(html)

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

def merge_doc(request,group_id,node_id,version_1,version_2):
     node = node_collection.one({'_id': ObjectId(node_id)})
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
     node.save(groupid=group_id)
     #update_mobwrite = update_mobwrite_content_org(node)
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
   node = node_collection.one({'_id': ObjectId(node_id)})
   group = node_collection.one({'_id': ObjectId(group_id)})
   doc=history_manager.get_version_document(node,version_1)
   
   for attr in node:
      if attr != '_type':
            try:
	    	node[attr] = doc[attr];
            except:
		node[attr] =node[attr]
   node.modified_by=request.user.id
   node.save(groupid=group_id)
   view ='revert'
   ver=history_manager.get_current_version(node)
   selected_versions=selected_versions = {"1": version_1, "2": ""}
   return render_to_response("ndf/version_page.html",
                               {'view': view,
                                'selected_versions': selected_versions, 
                                'node':node,
                                'groupid':group_id,
                                'group_id':group_id,
                                'content':node,
                                'ver':ver    
                           
                               },
                             
                              context_instance = RequestContext(request)
    )
