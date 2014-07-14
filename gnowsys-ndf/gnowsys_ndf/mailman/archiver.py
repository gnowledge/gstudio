#imports from python packages

from email.message import Message
from email.parser import Parser
import re
import os
import datetime
import subprocess

#imports from django packages

from django.core.mail import send_mail
from django_mongokit import get_database
from django.contrib.auth.models import User

#imports from gstudio packages for database compatibility

from gnowsys_ndf.ndf.models import GSystem, Triple, Node
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.mailman import settings

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


#Open the input file containing all emails. Input file can be provided by changing the INPUT_FILE setting in the configuration file.

inputfile = open(settings.MAIL_SPOOL_FILE_PATH,'r+')
line = inputfile.readline()

#Create an email parser to parse messages from the plain text file and convert them into message objects.

mailparser = Parser()
messages = []			#list to store the message objects created
i = 0


#Establish connection with the database and get required collections. 
#Twist and Reply GSystemTypes are needed to create new GSystems for forum threads and replies.
#mm_id AttributeType is needed to create new mm_id GAttributes for each new GSystem.  

collection = get_database()[Node.collection_name]
twist_st = collection.Node.one({'$and':[{'_type':'GSystemType'},{'name':'Twist'}]})
reply_st = collection.Node.one({'$and':[{'_type':'GSystemType'},{'name':'Reply'}]})
mm_id_node = collection.Node.one({'$and':[{'_type':'AttributeType'},{'name':'mm_id'}]})


#Function to create new GAttributes

def create_gattribute(subject_id, attribute_type_node, object_value):
	try:
	           ga_node = collection.GAttribute()
	
	           ga_node.subject = subject_id
	           ga_node.attribute_type = attribute_type_node
	           ga_node.object_value = object_value
	            	
	           ga_node.status = u"PUBLISHED"
	           ga_node.save()
	           info_message = " GAttribute ("+ga_node.name+") created successfully.\n"

	except Exception as e:
	           error_message = "\n GAttributeCreateError: " + str(e) + "\n"
	           raise Exception(error_message)


#Function which processes message objects and performs required action.

def process(message):
	

#The function first processes the to-address of every mail and decides which task has to be performed:
#1. If the value of the to-address field is an email address of the type list@domainname.com, then a new thread/reply must be created.
#2. If the value of the to-address field is an email address of the type list-owner@domainname.com, then a person must be added/removed from the forum.

	to_address = message['X-Original-To']
	name = to_address[:to_address.index('@')]
	from_address = message['From']
	user_address = message['From'][:from_address.index('(')].replace(" ","")
	body = message.get_payload().rstrip("\n")
	subject = message['Subject']

	
	if re.search(r"^[A-Za-z0-9_.]+$",name):

		thread = subject[subject.index("]")+2:]
		topic = subject[subject.rindex("[")+1:subject.rindex("]")]
		

		group = collection.GSystem.one({'$and':[{'_type':'Group'},{'name':name}]})
		forum = collection.GSystem.one({'name':topic})
	
		
		#If the message has an "In-Reply-To" header, then it indicates that the message is a reply to a previous post.
		#If the message does not have an "In-Reply-To header, then it indicates that the message is a new post.
		#The function then performs the following checks:
		#1. If the ObjectId header is already present, then the reply has been created through the forum, and only needs to be assigned a Mailman ID. But if the ObjectId header is absent, then a new reply must be created and also assigned a Mailman ID.
		#2. If the user who has posted/replied is not found in the Metastudio database, it sends an intimation to the user with a request to join Metastudio
		#3. If the user who has posted/replied has a Metastudio account, but is not found in the group's author_set, it sends an intimation to the user with a request to join the group


		if message['In-Reply-To']:


			if message['ObjectId']:
				existing_reply = collection.Node.one({'$and':[{'_id':message['ObjectId']},{'member_of':reply_st._id}]})
				ga_node = collection.Triple.one({'_type': "GAttribute", 'subject': existing_reply._id, 'attribute_type': mm_id_node.get_dbref()})

   				if ga_node is None:

					create_gattribute(existing_reply._id, mm_id_node, unicode(message['Message-Id']))

			
			else:

				try:
					user = User.objects.get(email = user_address)
	
					if user.id in group.author_set or user.id == group.created_by:

						reply_content = ''
						lines = body.split('\n')
						for i in lines:
							if i.startswith('>') or re.search(r"^On\s[\w]{3},\s[\w]{3}\s[0-9]{1,2},\s[0-9]{4}\sat\s[0-9]{2}:[0-9]{2}\sPM", i):
								pass
							else:
								reply_content += i+" "
				
				
						parent_ga_node = collection.Triple.one({'_type':'GAttribute','object_value':message['In-Reply-To']})
						parent_thread_id = parent_ga_node.subject
						parent_thread = collection.Node.one({'_id':ObjectId(parent_thread_id)})
						print parent_thread
	
						new_reply = collection.GSystem()
						new_reply.prior_node.append(parent_thread._id)
						new_reply.member_of.append(reply_st._id)
	
						name = unicode("Reply of:"+str(parent_thread_id))
						new_reply.name = name
	
		
						if body:
		       	  				 new_reply.content_org = unicode(body)
		       	   				 filename = slugify(name) + "-" + user.username + "-"
		       	    				 new_reply.content = org2html(new_reply.content_org, file_prefix=filename)
				
						new_reply.created_by = user.id
						new_reply.modified_by = user.id
						if user.id not in new_reply.contributors:
							new_reply.contributors.append(user.id)
				
						new_reply.group_set.append(group._id)

						date_string = message['Date'][:message['Date'].index("+")]
						time = datetime.datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S ")
						new_thread.created_at = time

		
						new_reply.save()
	

		        			create_gattribute(new_reply._id, mm_id_node, unicode(message['Message-Id']))
	
		

					else:
						subject = 'Metastudio intimation'
						from_email = settings.METASTUDIO_SERVER_ADDRESS
						to = user_address
						text_content = 'You have replied to a mail in the '+name+' mailing list on mailman. This list also has a discussion forum on the metastudio website, but it seems that you are not added to the group on metastudio. Please visit the following link if you wish to join the group:\nhttp://www.metastudio.org/'+group.name+'/'
						send_mail(subject,text_content,from_email,[to])
						
	
				except User.DoesNotExist:
					subject = 'Metastudio intimation'
					from_email = settings.METASTUDIO_SERVER_ADDRESS
					to = user_address
					text_content = 'You have replied to a mail in the '+list_name+' mailing list on mailman. This list also has a discussion forum on the metastudio website, but it seems that you are registered on the metastudio website. Please visit the following link if you wish to create a Metastudio account:\nhttp://www.metastudio.org/accounts/register/'
					send_mail(subject,text_content,from_email,[to])
				
#				print(user_address+" posted to list "+group.name+" replied to thread: "+thread+" in forum "+forum.name+" message: "+body )
			
						
		if message['In-Reply-To'] is None:


			if message['ObjectId']:
				existing_thread = collection.Node.one({'$and':[{'_id':message['ObjectId']},{'member_of':twist_st._id}]})
				ga_node = collection.Triple.one({'_type': "GAttribute", 'subject': existing_thread._id, 'attribute_type': mm_id_node.get_dbref()})

   				if ga_node is None:
        			# Code for creation
	        			
					create_gattribute(existing_thread._id, mm_id_node, unicode(message['Message-Id']))
	
			else:

	
				try:
					user = User.objects.get(email = user_address)
	
					if user.id in group.author_set or user.id == group.created_by:

						new_thread = collection.GSystem()
						new_thread.name = unicode(thread)
						new_thread.prior_node.append(forum._id)
	
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

						date_string = message['Date'][:message['Date'].index("+")]
						time = datetime.datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S ")
						new_thread.created_at = time

	
						new_thread.save()

#					ga_node = collection.Triple.one({'_type': "GAttribute", 'subject': new_thread._id, 'attribute_type': mm_id_node.get_dbref()})

#    					if ga_node is None:
        					# Code for creation

	        				create_gattribute(new_thread._id, mm_id_node, unicode(message['Message-Id']))

		

					else:
						subject = 'Metastudio intimation'
						from_email = settings.METASTUDIO_SERVER_ADDRESS
						to = user_address
						text_content = 'You have posted to '+name+' mailing list on mailman. This list also has a discussion forum on the metastudio website, but it seems that you are not added to the group on metastudio. Please visit the following link if you wish to join the group:\nhttp://www.metastudio.org/'+group.name+'/'
						send_mail(subject,text_content,from_email,[to])
						
	
				except User.DoesNotExist:
					subject = 'Metastudio intimation'
					from_email = settings.METASTUDIO_SERVER_ADDRESS
					to = user_address
					text_content = 'You have posted to '+list_name+' mailing list on mailman. This list also has a discussion forum on the metastudio website, but it seems that you are registered on the metastudio website. Please visit the following link if you wish to create a Metastudio account:\nhttp://www.metastudio.org/accounts/register/'
					send_mail(subject,text_content,from_email,[to])

#			print new_thread

	return



#This extracts each message from input file as a string, parses it into a message object and passes it to the process() function

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
subprocess.call(["sudo","rm",settings.MAIL_SPOOL_FILE_PATH])
