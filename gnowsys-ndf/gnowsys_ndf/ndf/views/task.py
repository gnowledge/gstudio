from django.http import HttpResponseRedirect
#from django.http import HttpResponse
from django.shortcuts import render_to_response #render  uncomment when to use
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django_mongokit import get_database
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect,StreamingHttpResponse
from django.http import HttpResponse
from mongokit import paginator
from django.utils import simplejson
from online_status.utils import encode_json			
import datetime
import json
from gnowsys_ndf.ndf.models import NodeJSONEncoder
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.models import GSystemType, Node 
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, get_file_node, parse_template_data
from gnowsys_ndf.ndf.views.notify import set_notif_val
collection = get_database()[Node.collection_name]
sitename=Site.objects.all()
app = collection.Node.one({'_type': "GSystemType", 'name': 'Task'})

if sitename :
	sitename = sitename[0]
else : 
	sitename = ""


def task(request, group_name, task_id=None):
    """
    * Renders a list of all 'task' available within the database.
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

    GST_TASK = collection.Node.one({'_type': "GSystemType", 'name': 'Task'})
    title = "Task"
    TASK_inst = collection.GSystem.find({'member_of': {'$all': [GST_TASK._id]}, 'group_set': {'$all': [ObjectId(group_id)]}})
    template = "ndf/task.html"
    variable = RequestContext(request, {'title': title, 'appId':app._id, 'TASK_inst': TASK_inst, 'group_id': group_id, 'groupid': group_id, 'group_name':group_name })
    return render_to_response(template, variable)

def task_details(request, group_name, task_id):
    """
    * Renders a 'task' details.
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_name) is False :
      group_ins = collection.Node.find_one({'_type': "Group","name": group_name})
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
    elif ins_objectid.is_valid(group_name) is True :
      group_ins = collection.Node.find_one({'_type': "Group","_id":ObjectId(group_name)})
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })  
    if group_ins:
        group_id = str(group_ins._id)
    else :
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if auth :	
          group_id = str(auth._id)
        
    task_node = collection.Node.one({'_type': u'GSystem', '_id': ObjectId(task_id)})
    at_list = ["Status", "start_time", "Priority", "end_time", "Assignee", "Estimated_time","Upload_Task"]
    blank_dict = {}
    history = []
    subtask = []
    for each in at_list:
	attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':each})
        attr = collection.Node.find_one({"_type":"GAttribute", "subject":task_node._id, "attribute_type.$id":attributetype_key._id})
        if attr:
		blank_dict[each] = attr.object_value
    if task_node.prior_node :
	blank_dict['parent'] = collection.Node.one({'_id':task_node.prior_node[0]}).name 
    if task_node.post_node :
	for each_postnode in task_node.post_node:
		sys_each_postnode = collection.Node.find_one({'_id':each_postnode})
		sys_each_postnode_user = User.objects.get(id=sys_each_postnode.created_by)
		member_of_name = collection.Node.find_one({'_id':sys_each_postnode.member_of[0]}).name 
		if member_of_name == "Task" :
			subtask.append({'id':str(sys_each_postnode._id), 'name':sys_each_postnode.name, 'created_by':sys_each_postnode_user.username, 'created_at':sys_each_postnode.created_at})
		if member_of_name == "task_update_history":
			if sys_each_postnode.altnames == None:
				postnode_task = '[]'
			else :
				postnode_task = sys_each_postnode.altnames
			history.append({'id':str(sys_each_postnode._id), 'name':sys_each_postnode.name, 'created_by':sys_each_postnode_user.username, 'created_at':sys_each_postnode.created_at, 'altnames':eval(postnode_task), 'content':sys_each_postnode.content})
    if  task_node.collection_set:
		
	blank_dict['collection']='True'
    history.reverse()
    var = { 'title': task_node.name,'group_id': group_id, 'appId':app._id, 'groupid': group_id, 'group_name': group_name, 'node':task_node, 'history':history, 'subtask':subtask}
    var.update(blank_dict)
    variables = RequestContext(request, var)
    template = "ndf/task_details.html"
    return render_to_response(template, variables)

def save_image(request, group_name, app_id=None, app_name=None, app_set_id=None, slug=None):
    if request.method == "POST" :
        group_object=collection.Group.one({'name':unicode(group_name), "_type": "Group"})
        for index, each in enumerate(request.FILES.getlist("doc[]", "")):

            title = each.name
            userid = request.POST.get("user", "")
            content_org = request.POST.get('content_org', '')
            tags = request.POST.get('tags', "")
            img_type = request.POST.get("type", "")
            language = request.POST.get("lan", "")
            usrname = request.user.username
            page_url = request.POST.get("page_url", "")
            access_policy = request.POST.get("login-mode", '') # To add access policy(public or private) to file object

            # for storing location in the file
            
            # location = []
            # location.append(json.loads(request.POST.get("location", "{}")))
            # obs_image = save_file(each,title,userid,group_id, content_org, tags, img_type, language, usrname, access_policy, oid=True, location=location)
            obs_image = save_file(each,title,userid,group_object._id, content_org, tags, img_type, language, usrname, access_policy, oid=True)
            # Sample output of (type tuple) obs_image: (ObjectId('5357634675daa23a7a5c2900'), 'True') 

            # if image sucessfully get uploaded then it's valid ObjectId
            
            if obs_image[0] and ObjectId.is_valid(obs_image[0]):
              return StreamingHttpResponse(str(obs_image[0]))
            
            else: # file is not uploaded sucessfully or uploaded with error
            	
            	return StreamingHttpResponse("UploadError")	

@login_required
def create_edit_task(request, group_name, task_id=None,task=None,count=0):
  """Creates/Modifies details about the given Task.
  """
  edit_task_node = ""
  change_list = []
  parent_task_check = ""
  userlist = []
  
  ins_objectid  = ObjectId()
  if ins_objectid.is_valid(group_name) is False:
    group_ins = collection.Node.find_one({'_type': "Group","name": group_name})
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })

  elif ins_objectid.is_valid(group_name) is True:
    group_ins = collection.Node.find_one({'_type': "Group","_id": ObjectId(group_name)})
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })  

  if group_ins:
    group_id = str(group_ins._id)
  else:
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
    if auth:
      group_id = str(auth._id)

  blank_dict = {}

  if task_id:
    task_node = collection.Node.one({'_type': u'GSystem', '_id': ObjectId(task_id)})
    edit_task_node = task_node
    at_list = ["Status", "start_time", "Priority", "end_time", "Assignee", "Estimated_time","Upload_Task"]

  else:
    task_node = collection.GSystem()

  userlist=[] 	
  if request.method == "POST": # create or edit
    name = request.POST.get("name","")
    content_org = request.POST.get("content_org","")
    parent = request.POST.get("parent","")
    Status = request.POST.get("Status","")
    Start_date = request.POST.get("start_time", "")
    Priority = request.POST.get("Priority","")
    Due_date = request.POST.get("end_time", "")
    Assignee = request.POST.get("Assignee","")
    Estimated_time = request.POST.get("Estimated_time","")
    watchers = request.POST.get("watchers","")
    GST_TASK = collection.Node.one({'_type': "GSystemType", 'name': 'Task'})

    tag=""
    field_value=[]
    file_id=(request.POST.get("files"))
    file_name=(request.POST.get("files_name"))

    #if request.FILES.getlist('UploadTask'):
    #      	files=request.FILES.getlist('UploadTask')
    #      	print "the upload task values",files
    #      	field_value = save_file(a[0],a[0], request.user.id, group_id, content_org,tag,usrname=request.user.username,oid=True)

    if not task_id: # create
      get_node_common_fields(request, task_node, group_id, GST_TASK)
      if watchers:
        for each_watchers in watchers.split(','):
          bx=User.objects.get(username=each_watchers)
          task_node.author_set.append(bx.id)
          userlist.append(each_watchers)
        task_node.save()
  		
    if parent: # prior node saving
      if not task_id:		
        task_node.prior_node = [ObjectId(parent)]
        parent_object = collection.Node.find_one({'_id':ObjectId(parent)})
        parent_object.post_node = [task_node._id]
        parent_object.save()
      
      else: #update
        if not task_node.prior_node == [ObjectId(parent)]:
          parent_task_check = "yes"
          if not task_node.prior_node:
            task_node.prior_node = [ObjectId(parent)]
            changed_object = collection.Node.find_one({'_id':ObjectId(parent)})
            changed_object.post_node.append(task_node._id)
            changed_object.save()
            change_list.append('parent set to '+changed_object.name)

          else:
            parent_object = collection.Node.find_one({'_id':task_node.prior_node[0]})
            parent_object.post_node.remove(task_node._id)
            parent_object.save()
            task_node.prior_node = [ObjectId(parent)]
            changed_object = collection.Node.find_one({'_id':ObjectId(parent)})
            changed_object.post_node.append(task_node._id)
            changed_object.save()
            change_list.append('Parent changed from '+parent_object.name+' to '+changed_object.name) # updated details

    task_node.save()

    at_list = ["Status", "start_time", "Priority", "end_time", "Assignee", "Estimated_time", "Upload_Task"] # fields
  	
    if not task_id: # create
      for each in at_list:
        if request.POST.get(each,""):
          attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':each})
          newattribute = collection.GAttribute()
          newattribute.subject = task_node._id
          newattribute.attribute_type = attributetype_key
          if each == 'Assignee' and len(request.POST.getlist("Assignee",""))>1:
            if count == 0:
              newattribute.object_value = [request.user.username]
      
            else:
              assignee_list=[]
              assignee_list=(request.POST.getlist(each,""))
              # Code needs to be written for parsing content as I'm not sure 
              # which kind of value would come here
              newattribute.object_value = assignee_list[count]
    
          else:
            field_value = request.POST.get(each, "")

            date_format_string = ""
            if each in ["start_time", "end_time"]:
              date_format_string = "%d/%m/%Y"

            field_value = parse_template_data(eval(attributetype_key["data_type"]), field_value, date_format_string=date_format_string)
            newattribute.object_value = field_value
    
          newattribute.save()
    
      if request.FILES.getlist('UploadTask'):
        attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':'Upload_Task'})
        newattribute = collection.GAttribute()
        newattribute.subject = task_node._id
        newattribute.attribute_type = attributetype_key
        newattribute.object_value = file_id
        newattribute.save()

      if int(len(request.POST.getlist("Assignee","")))>1:
        if task is None:
          Task=collection.Node.find_one({"_id":ObjectId(task_node._id)})

        else:
          Task=collection.Node.find_one({"_id":ObjectId(task)})
          Task.collection_set.append(task_node._id)
        
        Task.save()

        if int(count) <int(len(request.POST.getlist("Assignee",""))-1):
          create_edit_task(request, group_name, task_id,Task._id,count=count+1)
      
      if count == 0:	
        request.POST.getlist("Assignee","").append(request.user.username)		
        for eachuser in (request.POST.getlist("Assignee","")):
          if eachuser != "":	
            activ="task reported"
            msg="Task '"+task_node.name+"' has been reported by "+request.user.username+"\n     - Status: "+request.POST.get('Status','')+"\n     - Assignee: "+request.POST.get('Assignee','')+"\n     -  Url: http://"+sitename.name+"/"+group_name.replace(" ","%20").encode('utf8')+"/task/"+str(task_node._id)+"/"
            bx=User.objects.get(username =eachuser)
            set_notif_val(request,group_id,msg,activ,bx)
  	
    else: #update
      for each in at_list:
        if request.POST.get(each, ""):
          attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':each})
          attr = collection.Node.find_one({"_type":"GAttribute", "subject":task_node._id, "attribute_type.$id":attributetype_key._id})
          if each == "Assignee":
            for i in request.POST.getlist(each, ""):
              if i != "":
                userlist.append(i)
            userlist.append(request.user.username)

          field_value = request.POST.get(each, "")

          date_format_string = ""
          if each in ["start_time", "end_time"]:
            date_format_string = "%d/%m/%Y"

          field_value = parse_template_data(eval(attributetype_key["data_type"]), field_value, date_format_string=date_format_string)

          if attr: # already attribute exist 
            if not attr.object_value == field_value:
              # change_list.append(each.encode('utf8')+' changed from '+attr.object_value.encode('utf8')+' to '+request.POST.get(each,"").encode('utf8')) # updated   details         
              change_list.append(each.encode('utf8')+' changed from '+str(attr.object_value)+' to '+str(field_value)) # updated 	details					
              attr.object_value = field_value
              attr.save()
          
          else:
            attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':each})
            newattribute = collection.GAttribute()
            newattribute.subject = task_node._id
            newattribute.attribute_type = attributetype_key
            # newattribute.object_value = request.POST.get(each,"")
            newattribute.object_value = field_value
            newattribute.save()
            # change_list.append(each.encode('utf8')+' set to '+request.POST.get(each,"").encode('utf8')) # updated details
            change_list.append(each.encode('utf8')+' set to '+str(field_value)) # updated details

        elif each == 'Upload_Task':
          attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':'Upload_Task'})
          attr = collection.Node.find_one({"_type":"GAttribute", "subject":task_node._id, "attribute_type.$id":attributetype_key._id})
          if attr:
            value=get_file_node(attr.object_value)
            change_list.append(' changed from '+str(value).strip('[]')+' to '+str(file_name))      
            attr.object_value=file_id
            attr.save()
      
          else:
            newattribute = collection.GAttribute()
            newattribute.subject = task_node._id
            newattribute.attribute_type = attributetype_key
            newattribute.object_value = file_id
            newattribute.save()
            change_list.append(each.encode('utf8')+' set to '+file_name.encode('utf8')) # updated details
      
      userobj = User.objects.get(id=task_node.created_by)
      userlist.append(userobj.username)
      
      for each_author in task_node.author_set:
        userlist.append(User.objects.get(id=each_author).username)
      
      for eachuser in list(set(userlist)):
        activ="task updated"
        msg="Task '"+task_node.name+"' has been updated by "+request.user.username+"\n     - Changes: "+ str(change_list).strip('[]')+"\n     - Status: "+request.POST.get('Status','')+"\n     - Assignee: "+request.POST.get('Assignee','')+"\n     -  Url: http://"+sitename.domain+"/"+group_name.replace(" ","%20").encode('utf8')+"/task/"+str(task_node._id)+"/"
        bx=User.objects.get(username =eachuser)
        set_notif_val(request,group_id,msg,activ,bx)

      if change_list or content_org:
        GST_task_update_history = collection.Node.one({'_type': "GSystemType", 'name': 'task_update_history'})
        update_node = collection.GSystem()
        get_node_common_fields(request, update_node, group_id, GST_task_update_history)
        if change_list:
          update_node.altnames = unicode(str(change_list))
        
        else:
          update_node.altnames = unicode('[]')

        update_node.prior_node = [task_node._id]		
        update_node.name = unicode(task_node.name+"-update_history")
        update_node.save()
        update_node.name = unicode(task_node.name+"-update_history-"+str(update_node._id))
        update_node.save()
        task_node.post_node.append(update_node._id)
        task_node.save()
        
        # patch
        GST_TASK = collection.Node.one({'_type': "GSystemType", 'name': 'Task'}) 			
        get_node_common_fields(request, task_node, group_id, GST_TASK)
        task_node.save()
        #End Patch        
      
    return HttpResponseRedirect(reverse('task_details', kwargs={'group_name': group_name, 'task_id': str(task_node._id) }))

  if task_id:
    for each in at_list:
      attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':each})
      attr = collection.Node.find_one({"_type":"GAttribute", "subject":task_node._id, "attribute_type.$id":attributetype_key._id})
      if attr:
        if each == "Upload_Task":
          file_list=[]
          new_list=[]
          files=str(attr.object_value).split(',')
          for i in files:
            files_name=str(i.strip('   [](\'u\'   '))
            new_list.append(files_name)
      
          ins_objectid  = ObjectId()
          for i in new_list:
            if  ins_objectid.is_valid(i) is False:
              filedoc=collection.Node.find({'_type':'File','name':unicode(i)})
          
            else:
              filedoc=collection.Node.find({'_type':'File','_id':ObjectId(i)})			
            
            if filedoc:
              for i in filedoc:
                file_list.append(i.name)
        
          blank_dict[each] = json.dumps(file_list)
          blank_dict['select'] = json.dumps(new_list)                

        else:          
          blank_dict[each] = attr.object_value
    
    if task_node.prior_node:
      pri_node = collection.Node.one({'_id':task_node.prior_node[0]})
      blank_dict['parent'] = pri_node.name 
      blank_dict['parent_id'] = str(pri_node._id)

  var = { 'title': 'Task','group_id': group_id, 'groupid': group_id,'appId':app._id, 'group_name': group_name, 'node':edit_task_node, 'task_id':task_id }
  var.update(blank_dict)
  context_variables = var

  return render_to_response("ndf/task_create_edit.html",
          context_variables,
          context_instance=RequestContext(request)
        )

@login_required    
def task_collection(request,group_name,task_id=None,each_page=1):
    ins_objectid  = ObjectId()
    choice=0
    
    task=[]
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
    collection_task=[]
    node = collection.Node.one({'_id':ObjectId(task_id)})
    attr_value = {}
    at_list = ["Status", "start_time", "Priority", "end_time", "Assignee", "Estimated_time"]	
    for each in node.collection_set:
        attr_value = {}
    	new = collection.Node.one({'_id':ObjectId(each)})
    	for attrvalue in at_list:
		attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':attrvalue})
		attr = collection.Node.find_one({"_type":"GAttribute", "subject":new._id, "attribute_type.$id":attributetype_key._id})
		if attr:
			attr_value.update({attrvalue:attr.object_value})
		else:
			attr_value.update({attrvalue:"--"})
	attr_value.update({'id':each})
	attr_value.update({'Name':new.name})
	 
	         
	collection_task.append(dict(attr_value))
    paged_resources = Paginator(collection_task,10)
    files_list = []
    for each_resource in (paged_resources.page(each_page)).object_list:
		files_list.append(each_resource)
    			
    template = "ndf/task_list_view.html"
    variable = RequestContext(request, {'TASK_inst':files_list,'group_name':group_name,"page_info":paged_resources,'page_no':each_page, 
                                        'group_id': group_id, 'groupid': group_id,'choice':choice,'status':'None','task':task_id})
    return render_to_response(template, variable)                                     	

def delete_task(request, group_name, _id):
    """This method will delete task object and its Attribute and Relation
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
		    if member_of_name == "Task" :
			sys_each_postnode.prior_node.remove(node._id)
			sys_each_postnode.save()
		    if member_of_name == "task_update_history":
			sys_each_postnode.delete()
            node.delete()
    except Exception as e:
        print "Exception:", e

    return HttpResponseRedirect(reverse('task', kwargs={'group_name': group_name }))

def check_filter(request,group_name,choice=1,status='New',each_page=1):
    at_list = ["Status", "start_time", "Priority", "end_time", "Assignee", "Estimated_time"]
    blank_dict = {}
    history = []
    subtask = []
    group_name=group_name
    ins_objectid  = ObjectId()
    task=[]
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
    #section to get the Tasks 
    group=collection.Node.find_one({'_id':ObjectId(group_id)})
    GST_TASK = collection.Node.one({'_type': "GSystemType", 'name': 'Task'})
    attributetype_key1 = collection.Node.find_one({"_type":'AttributeType', 'name':'Assignee'})
    
    Completed_Status_List=['Resolved','Closed']
    title = "Task"
    TASK_inst = collection.GSystem.find({'member_of': {'$all': [GST_TASK._id]}, 'group_set': {'$all': [ObjectId(group_id)]}})
    task_list=[]
    message="" 	
    send="This group doesn't have any files"
    #Task Completed
    sub_task_name=[] 
    for each in TASK_inst:
	  if (each.collection_set):
            sub_task_name.append(each.name)
    TASK_inst.rewind()

    
    #every one see only task created by them and assigned to them 
    #only group owner can see all the task	
    for each in TASK_inst:
         attr_value={}
         for attrvalue in at_list:
		attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':attrvalue})
		attr = collection.Node.find_one({"_type":"GAttribute", "subject":each._id, "attribute_type.$id":attributetype_key._id})
		attr1 = collection.Node.find_one({"_type":"GAttribute","subject":each._id, "attribute_type.$id":attributetype_key1._id,"object_value":request.user.username})
		if attr:
			attr_value.update({attrvalue:attr.object_value})
		else:
			attr_value.update({attrvalue:"--"})
	 attr_value.update({'id':each._id})
	 if each.created_by == request.user.id:
	        attr_value.update({'owner':'owner'})
	 else:       
	        attr_value.update({'owner':'assignee'})
	 attr_value.update({'Name':each.name})
	 attr_value.update({'collection':each.collection_set})
	 if attr1 or each.created_by == request.user.id or group.created_by == request.user.id :
	    if ((each.name in sub_task_name and (not each.collection_set) == False) or each.name not in sub_task_name or attr1):    	
	        if int(choice) == int(1):
		         task_list.append(dict(attr_value))
	        if int(choice) == int(2):
                        message="No Completed Task"
	        	if attr_value['Status'] in Completed_Status_List:
		        		task_list.append(dict(attr_value))
	        if int(choice) == int(3):
                        message="No Task Created"
		        auth1 = collection.Node.one({'_type': 'Author', 'created_by': each.created_by })   
		        if auth:    		
		        	if auth.name == auth1.name:
		        		task_list.append(dict(attr_value))
	        if int(choice) == int(4):
		        message="Nothing Assigned"
		        attr1 = collection.Node.find_one({"_type":"GAttribute","subject":each._id, "attribute_type.$id":attributetype_key1._id,"object_value":request.user.username})
		        if attr1:
		        	task_list.append(dict(attr_value))
	        if int(choice) == int(5):
                        message="No Pending Task"  
		
		        if attr_value['Status'] not in Completed_Status_List: 
		        			if attr_value['Status'] != 'Rejected':
		        				if attr_value['end_time'] != "--" :
							
                                                                if (attr_value['end_time'] > unicode(datetime.date.today())) is False:
		        						task_list.append(dict(attr_value))
		        				else:
                                                                task_list.append(dict(attr_value)) 
	        if int(choice) == int(6):
                        message="No"+" "+status+" "+"Task"
		        if attr_value['Status'] == status:
		        			task_list.append(dict(attr_value))
    		
     
    		 
    
        
    paged_resources = Paginator(task_list,10)
    files_list = []
    for each_resource in (paged_resources.page(each_page)).object_list:
		files_list.append(each_resource)
    
    count_list=[]
    #count_list.append(TASK_inst.count())			 			
    TASK_inst.rewind()
    count=len(task_list)	
    	
    template = "ndf/task_list_view.html"
    variable = RequestContext(request, {'TASK_inst':files_list,'group_name':group_name, 'appId':app._id, 'group_id': group_id, 'groupid': group_id,'send':message,'count':count,'TASK_obj':TASK_inst,"page_info":paged_resources,'page_no':each_page,'choice':choice,'status':status})
    return render_to_response(template, variable)
    #return HttpResponse(json.dumps(self_task,cls=NodeJSONEncoder))
