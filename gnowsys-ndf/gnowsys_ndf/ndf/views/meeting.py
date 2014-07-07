from django.http import HttpResponseRedirect
#from django.http import HttpResponse
from django.shortcuts import render_to_response,render #render  uncomment when to use
from django.template import RequestContext
from django.template import Context
from django.template.defaultfilters import slugify
from django.http import HttpResponseRedirect
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django_mongokit import get_database
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.utils import simplejson
from online_status.status import CACHE_USERS
from online_status.utils import encode_json
from gnowsys_ndf.ndf.models import Group
from django.http import HttpResponse
from gnowsys_ndf.ndf.views.methods import get_forum_repl_type,forum_notification_status
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import GSystemType, GSystem,Node
import datetime
from gnowsys_ndf.ndf.org2any import org2html
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.models import GSystemType, Node 
from gnowsys_ndf.ndf.views.methods import get_node_common_fields
from gnowsys_ndf.ndf.views.notify import set_notif_val

import unicodedata
db = get_database()
col_Group = db[Group.collection_name]
collection = get_database()[Node.collection_name]
sitename=Site.objects.all()
if sitename :
	sitename = sitename[0]
else : 
	sitename = ""


def meeting(request, group_name, meeting_id=None):
    """
    * Renders a list of all 'meeting' available within the database.
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_name) is False :
      group_ins = collection.Node.find_one({'_type': "Group","name": group_name})
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if group_ins:
        group_id = str(group_ins._id)
      else :
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if auth :
          group_id = str(auth._id)
    else :
        pass
    #print "\ngroup_id: ", group_id,"\n"

    online_users = cache.get(CACHE_USERS)                                         # ramk
    online_users = simplejson.dumps(online_users, default=encode_json)            # ramk
    print online_users
    GST_MEETING = collection.Node.one({'_type': "GSystemType", 'name': 'Meeting'})
    title = "Meeting"
    MEETING_inst = collection.GSystem.find({'member_of': {'$all': [GST_MEETING._id]}, 'group_set': {'$all': [ObjectId(group_id)]}})
    template = "ndf/meeting.html"
    variable = RequestContext(request, {'title': title, 'MEETING_inst': MEETING_inst, 'group_id': group_id, 'groupid': group_id, 'group_name':group_name,'meetingid': ins_objectid,'online_users':online_users})
    return render_to_response(template, variable)

def meeting_details(request, group_name, meeting_id):
    """
    * Renders a 'meeting' details.
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_name) is False :
      group_ins = collection.Node.find_one({'_type': "Group","name": group_name})
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if group_ins:
        group_id = str(group_ins._id)
      else :
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if auth :	
          group_id = str(auth._id)
    else :
        pass
    print meeting_id	
    meeting_node = collection.Node.one({'_type': u'GSystem', '_id': ObjectId(meeting_id)})
    at_list = ["start_time","start_time_2", "Priority", "Convener", "Estimated_time","invited","meeting_status"]
    blank_dict = {}
    history = []
    submeeting = []
    for each in at_list:
	attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':each})
        attr = collection.Node.find_one({"_type":"GAttribute", "subject":meeting_node._id, "attribute_type.$id":attributetype_key._id})
        if attr:
		blank_dict[each] = attr.object_value
    if meeting_node.prior_node :
	blank_dict['parent'] = collection.Node.one({'_id':meeting_node.prior_node[0]}).name 
    if meeting_node.post_node :
	for each_postnode in meeting_node.post_node:
		sys_each_postnode = collection.Node.find_one({'_id':each_postnode})
		sys_each_postnode_user = User.objects.get(id=sys_each_postnode.created_by)
		member_of_name = collection.Node.find_one({'_id':sys_each_postnode.member_of[0]}).name 
		if member_of_name == "Meeting" :
			submeeting.append({'id':str(sys_each_postnode._id), 'name':sys_each_postnode.name, 'created_by':sys_each_postnode_user.username, 'created_at':sys_each_postnode.created_at})
		if member_of_name == "meeting_update_history":
			if sys_each_postnode.altnames == None:
				postnode_meeting = '[]'
			else :
				postnode_meeting = sys_each_postnode.altnames
			history.append({'id':str(sys_each_postnode._id), 'name':sys_each_postnode.name, 'created_by':sys_each_postnode_user.username, 'created_at':sys_each_postnode.created_at, 'altnames':eval(postnode_meeting), 'content':sys_each_postnode.content})
    history.reverse()
    var = { 'title': meeting_node.name,'group_id': group_id, 'groupid': group_id, 'group_name': group_name, 'node':meeting_node, 'history':history, 'submeeting':submeeting }
    var.update(blank_dict)
    variables = RequestContext(request, var)
    template = "ndf/meeting_details.html"
    return render_to_response(template, variables)

@login_required
def create_edit_meeting(request, group_name, meeting_id=None):
    """Creates/Modifies details about the given Meeting.
    """
    edit_meeting_node = ""
    change_list = []
    parent_meeting_check = ""
    userlist = []
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_name) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_name})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    blank_dict = {}
    if meeting_id:
        meeting_node = collection.Node.one({'_type': u'GSystem', '_id': ObjectId(meeting_id)})
	edit_meeting_node = meeting_node
	at_list = ["start_time","start_time_2", "Priority", "Convener", "Estimated_time","invited","meeting_status"]
    	
    else:
        meeting_node = collection.GSystem()

    if request.method == "POST": # create or edit
        name = request.POST.get("name","")
        content_org = request.POST.get("content_org","")
        parent = request.POST.get("parent","")
        start_time = request.POST.get("start_time","")#date
	start_time_2 = request.POST.get("start_time_2","")
        Priority = request.POST.get("Priority","")
	Convener = request.POST.get("Convener","")
        Estimated_time = request.POST.get("Estimated_time","")
	invited = request.POST.get("invited","")
	meeting_status=request.POST.get("meeting_status","0")
        GST_MEETING = collection.Node.one({'_type': "GSystemType", 'name': 'Meeting'})
	if not meeting_id: # create
        	get_node_common_fields(request, meeting_node, group_id, GST_MEETING)
		for each_invited in invited.split(','):
           		 print "\n\n :  ", each_invited
           		 bx=User.objects.get(username=each_invited)
	                 meeting_node.author_set.append(bx.id)
			 userlist.append(each_invited)
		meeting_node.save()

	
	if parent: # prior node saving
		if not meeting_id:		
			meeting_node.prior_node = [ObjectId(parent)]
			parent_object = collection.Node.find_one({'_id':ObjectId(parent)})
			parent_object.post_node = [meeting_node._id]
			parent_object.save()
		else : #update
			if not meeting_node.prior_node == [ObjectId(parent)] :
				parent_meeting_check = "yes"
				if not meeting_node.prior_node :
					meeting_node.prior_node = [ObjectId(parent)]
					changed_object = collection.Node.find_one({'_id':ObjectId(parent)})
					changed_object.post_node.append(meeting_node._id)
					changed_object.save()
					change_list.append('parent set to '+changed_object.name)
				else :
					parent_object = collection.Node.find_one({'_id':meeting_node.prior_node[0]})
					parent_object.post_node.remove(meeting_node._id)
					parent_object.save()
					meeting_node.prior_node = [ObjectId(parent)]
					changed_object = collection.Node.find_one({'_id':ObjectId(parent)})
					changed_object.post_node.append(meeting_node._id)
					changed_object.save()
					change_list.append('Parent changed from '+parent_object.name+' to '+changed_object.name) # updated details

	
        meeting_node.save()
	at_list = ["start_time","start_time_2", "Priority", "Convener", "Estimated_time","invited","meeting_status"] # fields
	if not meeting_id: # create
	    for each in at_list:
	         if request.POST.get(each,""):
			attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':each})
               		newattribute = collection.GAttribute()
                	newattribute.subject = meeting_node._id
                	newattribute.attribute_type = attributetype_key
                	newattribute.object_value = request.POST.get(each,"")
                	newattribute.save()
			if each == "Convener" :
				userlist.append(request.POST.get(each,""))
	    userlist.append(request.user.username)
	    for eachuser in list(set(userlist)):
		activ="meeting reported"
		msg="You have been invited to attend - Meeting '"+meeting_node.name+"' created by "+request.user.username+"\n     - Date: "+request.POST.get('start_time','')+"\n     - Time: "+request.POST.get('start_time_2','')+"\n     - Convener: "+request.POST.get('Convener','')+"\n     -  Url: http://"+sitename.name+"/"+group_name.encode('utf8')+"/meeting/"+str(meeting_node._id)+"/"
		bx=User.objects.get(username =eachuser)
	        set_notif_val(request,group_id,msg,activ,bx)
	else: #update
	    for each in at_list:
		if request.POST.get(each,""):
			attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':each})
        		attr = collection.Node.find_one({"_type":"GAttribute", "subject":meeting_node._id, "attribute_type.$id":attributetype_key._id})
			if each == "Convener" :
				userlist.append(request.POST.get(each,""))
			if attr : # already attribute exist 
				if not attr.object_value == request.POST.get(each,"") :	
					change_list.append(each.encode('utf8')+' changed from '+attr.object_value.encode('utf8')+' to '+request.POST.get(each,"").encode('utf8')) # updated details	  
					attr.object_value = request.POST.get(each,"")
					attr.save()
					
					
			else :
				attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':each})
               			newattribute = collection.GAttribute()
                		newattribute.subject = meeting_node._id
                		newattribute.attribute_type = attributetype_key
                		newattribute.object_value = request.POST.get(each,"")
                		newattribute.save()
				change_list.append(each.encode('utf8')+' set to '+request.POST.get(each,"").encode('utf8')) # updated details
	    userobj = User.objects.get(id=meeting_node.created_by)
	    userlist.append(userobj.username)
	    for each_author in meeting_node.author_set:
		userlist.append(User.objects.get(id=each_author).username)
       	    for eachuser in list(set(userlist)):
		activ="meeting updated"
		msg="Meeting '"+meeting_node.name+"' has been updated by "+request.user.username+"\n     - Changes: "+ str(change_list).strip('[]')+"\n     - Convener: "+request.POST.get('Convener','')+"\n     -  Url: http://"+sitename.domain+"/"+group_name.encode('utf8')+"/meeting/"+str(meeting_node._id)+"/"
		bx=User.objects.get(username =eachuser)
	        set_notif_val(request,group_id,msg,activ,bx)

	    if change_list or content_org :
		GST_meeting_update_history = collection.Node.one({'_type': "GSystemType", 'name': 'meeting_update_history'})
	        update_node = collection.GSystem()
		get_node_common_fields(request, update_node, group_id, GST_meeting_update_history)
		if change_list :
			update_node.altnames = unicode(str(change_list))
		else :
			update_node.altnames = unicode('[]')
		update_node.prior_node = [meeting_node._id]		
		update_node.save()
		update_node.name = unicode(meeting_node.name+"-update_history-"+str(update_node._id))
		update_node.save()
		meeting_node.post_node.append(update_node._id)
		meeting_node.save()			

        return HttpResponseRedirect(reverse('meeting_details', kwargs={'group_name': group_name, 'meeting_id': str(meeting_node._id) }))

    if meeting_id:
    	for each in at_list:
		attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':each})
        	attr = collection.Node.find_one({"_type":"GAttribute", "subject":meeting_node._id, "attribute_type.$id":attributetype_key._id})
        	if attr:
			blank_dict[each] = attr.object_value
	if meeting_node.prior_node :
		pri_node = collection.Node.one({'_id':meeting_node.prior_node[0]})
		blank_dict['parent'] = pri_node.name 
		blank_dict['parent_id'] = str(pri_node._id)

    var = { 'title': 'Meeting','group_id': group_id, 'groupid': group_id, 'group_name': group_name, 'node':edit_meeting_node, 'meeting_id':meeting_id }
    var.update(blank_dict)
    context_variables = var

    return render_to_response("ndf/meeting_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
                              )

    
@login_required    
def delete_meeting(request, group_name, _id):
    """This method will delete meeting object and its Attribute and Relation
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_name) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_name})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    pageurl = request.GET.get("next", "")
    try:
        node = collection.Node.one({'_id':ObjectId(_id)})
        if node:
            attributes = collection.Triple.find({'_type':'GAttribute','subject':node._id})
            relations = collection.Triple.find({'_type':'GRelation','subject':node._id})
            if attributes.count() > 0:
                for each in attributes:
                    collection.Triple.one({'_id':each['_id']}).delete()
                    
            if relations.count() > 0:
                for each in relations:
                    collection.Triple.one({'_id':each['_id']}).delete()
	    if len(node.post_node) > 0 :
		for each in node.post_node : 
		    sys_each_postnode = collection.Node.find_one({'_id':each})
		    member_of_name = collection.Node.find_one({'_id':sys_each_postnode.member_of[0]}).name 
		    if member_of_name == "Meeting" :
			sys_each_postnode.prior_node.remove(node._id)
			sys_each_postnode.save()
		    if member_of_name == "meeting_update_history":
			sys_each_postnode.delete()
            node.delete()
    except Exception as e:
        print "Exception:", e
    return HttpResponseRedirect(pageurl) 

def output(request, group_id, meetingid):                                                               #ramkarnani
    newmeetingid = meetingid
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False:
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else:
        group_ins = collection.Node.find_one({'_type': "Group","_id": ObjectId(group_id)})
        pass
            #template = "https://chatb/#"+meetingid
    
    return render_to_response("ndf/newmeeting.html",{'group_id': group_id,'groupid':group_id,'newmeetingid':newmeetingid},context_instance=RequestContext(request))



def dashb(request, group_id):
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False:
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else:
        group_ins = collection.Node.find_one({'_type': "Group","_id": ObjectId(group_id)})
        pass
    online_users = cache.get(CACHE_USERS)
    online_users = simplejson.dumps(online_users, default=encode_json)  
    #print "\n inside meeting \n"
    # print "\ngroup_id: ", group_id,"\n"
    
    

    return render_to_response("ndf/meeting.html",{'group_id': group_id,'groupid':group_id,'online_users':online_users,'meetingid':ins_objectid},context_instance=RequestContext(request))

#### Ajax would be called here to get refreshed list of online members
def get_online_users(request, group_id):                                                                        #ramkarnani
    """Json of online users, useful f.ex. for refreshing a online users list via an ajax call or something"""
    online_users = cache.get(CACHE_USERS)
    #print "hey \n"
    #print json.dumps(online_users, default=encode_json), "\n\n"
    #a = json.dumps(online_users, default=encode_json)
    #print type(a)
    return HttpResponse(simplejson.dumps(online_users, default=encode_json))

def invite_meeting(request, group_id, meetingid):                                                                  #ramkarnani
    try:
            # print "here in view"
            colg=col_Group.Group.one({'_id':ObjectId(group_id)})
            groupname=colg.name
            # print "\n\nPOST : ", request
            recipient = request.GET.get("usr","")
            recipient = unicodedata.normalize('NFKD', recipient).encode('ascii','ignore')
            #print type(recipient), recipient
            sender=request.user
            sending_user=User.objects.get(username=sender).id
            #print type (sitename), sitename
            activ="invitation to join in meeting"
            url_of_meeting = "http://" + str(sitename) + "/" + group_id + "/meeting/" + meetingid
            msg="'This is to inform you that " + str(sender) + " has invited you to the meeting of " +str(groupname)+" . Please click here " + url_of_meeting +"'"
            #print "\n\nmsg : ", msg

            ret=""
            
            bx=User.objects.get(username=recipient)
            ret = set_notif_val(request,group_id,msg,activ,bx)
            if bx.id not in colg.author_set:
                colg.author_set.append(bx.id)
                colg.save()
            if ret :
                return HttpResponse("success")

                   # msg_list=msg.split()
                   # newmeetingid=msg[16]

            else:
                return HttpResponse("failure")
    except Exception as e:
            print str(e)
            return HttpResponse(str(e))
