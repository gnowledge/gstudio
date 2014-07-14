# imports from python libraries #######################################################################################################

import re

# imports from installed packages #####################################################################################################

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext


from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


from django_mongokit import get_database


from django.core.mail import send_mail


try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

# imports from application folders/files ##############################################################################################

from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.settings import *

#######################################################################################################################################

collection = get_database()[Node.collection_name]
group=''
class Midware(object):

	#This method is written to intercept the request sent while creating a new group or a new forum in a group or subscribing to or unsubscribing from a group and sending a mail to mailman server accordingly to create the mailing lists or subscribe or unsubscribe the users.

	def process_request(self,request):
		#print "opening the page %s " % request.path
		
		if re.search("^/[A-Za-z0-9]{24}/group/create_group",request.path):
			#print 'creating a GROUP'
			if request.method == 'POST':
			     body = "create list\n"
			     body += "Username:"+request.user.email+"\n"  
			     body += "Group:"+request.POST.get('groupname','')+"\n"
			     send_mail("creating a list",body, EMAIL_HOST_USER, [LOCAL_MAILMAN_USER], fail_silently=False)

		if re.search("^/[A-Za-z0-9]{24}/group/notify/join",request.path):
			#print 'joining a group'
			group = collection.Node.one({'_id': ObjectId(request.path.split('/')[1])})	
			body = 'join a group\n'
			body += "Username:"+request.user.email+"\n" 		      
			body +="Group:"+group['name']+"\n"
			send_mail("joining a group", body, EMAIL_HOST_USER, [LOCAL_MAILMAN_USER], fail_silently=False)

		if re.search("^/[A-Za-z0-9]{24}/group/notify/remove",request.path):
			#print 'unsubscribing from a group'
			group = collection.Node.one({'_id': ObjectId(request.path.split('/')[1])})	
			body = 'unsubscribe from a group\n'
			body += "Username:"+request.user.email+"\n" 		      
			body +="Group:"+group['name']+"\n"
			send_mail("unsubscribing from a group", body, EMAIL_HOST_USER, [LOCAL_MAILMAN_USER], fail_silently=False)
			    
		#if re.search("^/[A-Za-z0-9]{24}/forum/[A-Za-z0-9]{24}",request.path):
		if re.search("^/[A-Za-z0-9]+/forum/create",request.path):
			#print 'creating a forum in a group'
			if request.method == 'POST':
			     group = request.path.split('/')[1]
			     group_admin_id = collection.GSystem.one({"name":group,"_type":"Group"}).created_by
			     group_admin_address = User.objects.get(id = group_admin_id).email
			     body = "You have created a forum named "+ request.POST.get('forum_name','') +" in the group "+group+" on metastudio website. This group also has a mailman mailing list. Please contact the list admin of this list "+group_admin_address +" to add a new topic to the mailing lists."
			     send_mail("creating a topic", body, EMAIL_HOST_USER, [request.user.email], fail_silently=False)
		return None
