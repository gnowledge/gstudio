''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json

''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
# from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext

# from mongokit import paginator

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, get_page,get_node_metadata,get_execution_time

#######################################################################################################################################
history_manager = HistoryManager()
gapp_GST = node_collection.one({'_type': 'MetaType', 'name': 'GAPP'})
term_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Term', 'member_of': ObjectId(gapp_GST._id) })
topic_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})

if term_GST:	
	title = term_GST.altnames
@get_execution_time
def term(request, group_id, node_id=None):

	# ins_objectid  = ObjectId()
	# if ins_objectid.is_valid(group_id) is False :
	# 	group_ins = node_collection.find_one({'_type': "Group","name": group_id})
	# 	auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	# 	if group_ins:
	# 		group_id = str(group_ins._id)
	# 	else :
	# 		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	# 		if auth :
	# 			group_id = str(auth._id)
	# else :
	# 	pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
	

	if not node_id:
		# To list all term instances
	  	terms_list = node_collection.find({'_type':'GSystem','member_of': {'$all': [ObjectId(term_GST._id), ObjectId(topic_GST._id)]},
	  	 								   'group_set': ObjectId(group_id) 
	  	 								  }).sort('name', 1)

	  	
	  	terms = terms_list.count()

	 	return render_to_response("ndf/term.html",
	                               {'group_id': group_id,'groupid': group_id,
	                                'title':title, 'terms':terms
	                               },
	                              context_instance = RequestContext(request)
	    )

	else:
		topic = "Topic"
		node_obj = node_collection.one({'_id': ObjectId(node_id)})

		return render_to_response('ndf/topic_details.html',
									{ 'node': node_obj, 'title':title,
                                      'group_id': group_id,'topic':topic,
                                      'groupid':group_id,
									},
                                  	context_instance = RequestContext(request)
        )


@login_required
@get_execution_time
def create_edit_term(request, group_id, node_id=None):

    # ins_objectid = ObjectId()
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


    context_variables = { 'title': title,
                          'group_id': group_id,
                          'groupid': group_id
                      }
    
    # To list all term instances
    terms_list = node_collection.find({'_type': 'GSystem', 'member_of': {'$all': [ObjectId(term_GST._id), ObjectId(topic_GST._id)]},
                                       'group_set': ObjectId(group_id) 
                                   }).sort('name', 1)

    nodes_list = []
    for each in terms_list:
      nodes_list.append(str((each.name).strip().lower()))

    if node_id:
        term_node = node_collection.one({'_id': ObjectId(node_id)})
    else:
        term_node = node_collection.collection.GSystem()

    if request.method == "POST":
        
        # get_node_common_fields(request, page_node, group_id, gst_page)
        term_node.save(is_changed=get_node_common_fields(request, term_node, group_id, term_GST),groupid=group_id)

        get_node_metadata(request,term_node,term_GST)
	
        return HttpResponseRedirect(reverse('term_details', kwargs={'group_id': group_id, 'node_id': term_node._id }))

    else:
        if node_id:
            term_node,ver=get_page(request,term_node)
            term_node.get_neighbourhood(term_node.member_of)
            context_variables['node'] = term_node
            context_variables['groupid']=group_id
            context_variables['group_id']=group_id
            context_variables['nodes_list'] = json.dumps(nodes_list)
        else:
            context_variables['nodes_list'] = json.dumps(nodes_list)

        return render_to_response("ndf/term_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
                              	)

@login_required   
@get_execution_time 
def delete_term(request, group_id, node_id):
    """Change the status to Hidden.
    
    Just hide the term from users!
    """
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
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

    op = node_collection.collection.update({'_id': ObjectId(node_id)}, {'$set': {'status': u"HIDDEN"}})
    return HttpResponseRedirect(reverse('term', kwargs={'group_id': group_id}))
