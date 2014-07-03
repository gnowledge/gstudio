#imports from python packages

from email.message import Message
from email.parser import Parser
import re
import os

#imports from django packages

from django.core.mail import EmailMultiAlternatives
from django_mongokit import get_database
from django.contrib.auth.models import User

#imports from gstudio packages for database compatibility

from gnowsys_ndf.ndf.models import GSystem, Triple, Node
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.ndf.org2any import org2html

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


#open input file

inputfile = open('./gnowsys_ndf/mailman/try3.txt','r+')
line = inputfile.readline()

#create email parser and a list to store message objects

mailparser = Parser()
messages = []
i = 0

#establish connection with the database and get required collections

collection = get_database()[Node.collection_name]
twist_st = collection.Node.one({'$and':[{'_type':'GSystemType'},{'name':'Twist'}]})


#function which processes message objects and performs required action

def process(message):
	"This function processes the to address of every mail and decides what action is to be performed"

	to_address = message['X-Original-To']
	name = to_address[:to_address.index('@')]
	from_address = message['From']
	user_address = message['From'][:from_address.index('(')].replace(" ","")
	body = message.get_payload().rstrip("\n")

	
	if re.search(r"^[A-Za-z0-9_.]+$",name):

		subject = message['Subject']
		thread = subject[subject.index("]")+2:]
		topic = subject[subject.index("[")+1:subject.index("]")]
		

		group = collection.GSystem.one({'$and':[{'_type':'Group'},{'name':name}]})
		forum = collection.GSystem.one({'name':topic})
	
		
		if re.search(r"Re:",subject):
			
			reply_content = ''
			lines = body.split('\n')
			for i in lines:
				if i.startswith('>'):
					pass
				else:
					reply_content += i+" "
			
			
			parent_thread = collection.GSystem.one({'$and':[{'name':thread},{'prior_node':forum._id}]})
			print parent_thread

			new_reply = collection.GSystem()
			new_reply.prior_node.append(parent_thread._id)

			user = User.objects.get(email = user_address)
#
#			if body:
#          			 new_thread.content_org = unicode(body)
#           			 filename = slugify(thread) + "-" + user.username + "-"
#            			 new_thread.content = org2html(new_thread.content_org, file_prefix=filename)
#
#			new_thread.created_by = user.id
#			new_thread.modified_by = user.id
#			if user.id not in new_thread.contributors:
#				new_thread.contributors.append(user.id)
#
#			new_thread.member_of.append(twist_st._id)
#			new_thread.group_set.append(group._id)

#			new_thread.save()
			
			print(user_address+" posted to list "+group.name+" replied to thread: "+thread+" in forum "+forum.name+" message: "+body )
			
						
		else:

			new_thread = collection.GSystem()
			new_thread.name = unicode(thread)
			new_thread.prior_node.append(forum._id)

			try:
				user = User.objects.get(email = user_address)

				if body:
        	  			 new_thread.content_org = unicode(body)
        	   			 filename = slugify(thread) + "-" + user.username + "-"
        	    			 new_thread.content = org2html(new_thread.content_org, file_prefix=filename)
	
				new_thread.created_by = user.id
				new_thread.modified_by = user.id
				if user.id not in new_thread.contributors:
					new_thread.contributors.append(user.id)
	
				new_thread.member_of.append(twist_st._id)
				new_thread.group_set.append(group._id)
	
				new_thread.save()

			except User.DoesNotExist:
				pass

#			print new_thread


	
	if re.search(r"^[A-Za-z0-9_.]+-owner$",name):	


		if re.search(r'^[A-Za-z0-9_.]+@[A-Za-z0-9.]+.[A-Za-z]{1,4} has been successfully subscribed to',body):
			try:
				user_address = body.split(" ")[0]
				list_name = body.split(" ")[6]
				group = collection.Group.one({'$and':[{'name':list_name},{'_type':'Group'}]})
				user = User.objects.get(email = user_address)
		
				if not ((user.id in group.author_set) or (user.id == group.created_by )):
					group.author_set.append(user.id)
					group.modified_by = user.id
					group.status = u'PUBLISHED'
					group.save()
	
			except User.DoesNotExist:
	
				subject = 'Metastudio intimation'
				from_email = 'mailmantrial@gmail.com'
				to = user_address
				text_content = 'You have joined '+list_name+' mailing list on mailman. This list also has a discussion forum on the metastudio website, but you cannot access the forum until you are registered on the website. Please visit the following link if you wish to create a Metastudio account:\n'
				print text_content
				html_content = '<html><body><a href = "http://127.0.0.1:8000/accounts/register/">'
				message = EmailMultiAlternatives(subject, text_content, from_email, [to])
				message.attach_alternative(html_content, "text/html")
				print message.body
				message.send()
	
		if re.search(r'^[A-Za-z0-9_.]+@[A-Za-z0-9.]+.[A-Za-z]{1,4} has been removed from',body):
			try:
				user_address = body.split(" ")[0]
				list_name = body.split(" ")[5]
				group = collection.Group.one({'$and':[{'name':list_name},{'_type':'Group'}]})
				user = User.objects.get(email = user_address)
	
				group.author_set.remove(user.id)
				group.modified_by = user.id
				group.status = u'PUBLISHED'
				group.save()
	
			except User.DoesNotExist:
				pass
	
	
			#print(user_address+" contacted admin of list "+list_name)
	
	
	return



#this extracts each message from input file and passes it to the process function

for next in inputfile:
	end = re.search(r"^From\s[A-Za-z0-9_.]+@[A-Za-z0-9.]+.[A-Za-z]{1,4}\s\s[A-Za-z]{3}\s[A-Za-z]{3}\s[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\s[0-9]{4}$",next)
	if end:
		messages.append(mailparser.parsestr(line))
		process(messages[i])
		i += 1
		line = next
	else:
		line += next

messages.append(mailparser.parsestr(line))
process(messages[i])

inputfile.close()
#os.remove('try2')
