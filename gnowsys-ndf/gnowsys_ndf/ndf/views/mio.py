import smtplib
import email
import os
import io
import time
import sys
import imaplib
import shutil
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.mime.message import MIMEMessage
import urllib
from HTMLParser import HTMLParser
from gnowsys_ndf.ndf.models import * 
from django.http import HttpRequest
from django.contrib.auth.models import User
from gnowsys_ndf.settings import GSTUDIO_LOGS_DIR_PATH
from gnowsys_ndf.ndf.views.filehive import *
from gnowsys_ndf.ndf.views.methods import create_grelation
from gnowsys_ndf.ndf.views.methods import get_group_name_id
from django.shortcuts import render
from django.conf import settings

error_message = {"Page name required":1,
				"Page Content required":2,
				"User details required":3,
				"already exists":4,
				"User does not exist":5,
				"User authenticated":6,
				"User not a member of this group":7,
				"Group does not exist":8}

#EXTRACTING EMAILID AND PASSWORD FROM THE SETTINGS.PY FILE
mio_from_email = ''
mio_from_password  = ''

if settings.GSTUDIO_MIO_FROM_EMAIL!='':
	mio_from_email = settings.GSTUDIO_MIO_FROM_EMAIL
else:
	mio_from_email = settings.DEFAULT_MIO_FROM_EMAIL
mio_from_password = settings.GSTUDIO_MIO_FROM_EMAIL_PASSWORD
#************************************************************

def create_page(**kwargs): 
	p = node_collection.collection.GSystem()

	if kwargs.has_key('group_name'):
		group_name = kwargs.get('group_name','home')
	else:
		group_name = 'home'
	group_name = unicode(group_name)

	if kwargs.has_key('name'):
		name = kwargs.get('name','')
	else:
		return error_message["Page name required"]
	name = unicode(name)

	if kwargs.has_key('content'):
		content = kwargs.get('content','')
	else:
		return error_message["Page Content required"]
	content = unicode(content)

	if kwargs.has_key('created_by'):
		created_by = kwargs.get('created_by','')
	else:
		return error_message["User details required"]

	m_id = kwargs.get('m_id','')

	gst_page = node_collection.one({'_type':u'GSystemType','name':u'Page'})
	gst_group = node_collection.one({'_type':u'Group','name':group_name})

	available_nodes = node_collection.find({'_type': u'GSystem', 'member_of': ObjectId(gst_page._id),
		'group_set': ObjectId(gst_group._id)})

	nodes_list = []
	for each in available_nodes:
		nodes_list.append(str((each.name).strip().lower()))

	if name in nodes_list:
		return error_message["already exists"]
	else:
		p.fill_gstystem_values(name = name,member_of=[gst_page._id],created_by = created_by,
			content = content,group_set=[gst_group._id])
		p.origin.append({'mio':m_id})
		try:
			p.save()
		except Exception as e:
			print "Exception in while creating page from mail:  " + str(e)
		return str(p._id);

def send_page(to_user,page_name,page_content,subject,m_id,ref):
        msg = MIMEMultipart('alternative')
        msg["Message-ID"] = email.utils.make_msgid()
        msg["In-Reply-To"] = m_id

        if(ref==None):
                msg["References"] = m_id
        else:
                msg["References"] = ref+"\n"+m_id

        msg['Subject'] = subject
        msg['From'] = mio_from_email
        msg['To'] = to_user
        
        context = {'pg_name': page_name,'pg_content': page_content}
    	Html = render(None, 'ndf/mio_index.html', context)
       	html = str(Html)
       	html = html.strip('Content-Type: text/html; charset=utf-8\n')	
        msg.attach(MIMEText(html, 'html'))
        smtpObj=smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(mio_from_email,mio_from_password)
        smtpObj.sendmail(mio_from_email,to_user,msg.as_string())
        smtpObj.quit()

def update_page(name,content,id,user_id):
	gst_page = node_collection.one({u'_id':ObjectId(id)})
	gst_page.name = unicode(name)
	gst_page.altnames = unicode(name)
	gst_page.content = unicode(content)
	gst_page.last_update = datetime.datetime.today()
	gst_page.modified_by = user_id

	try:
		gst_page.save()
	except Exception as e:
		print "Exception while updating page from mail:  " + str(e)

def upload(gp_name,filename,name,author,content):
	home_grp = node_collection.one({'_type': "Group", 'name':gp_name})
	file_gst = node_collection.one({'_type': "GSystemType", 'name': u'File'})

	each_img_name = filename
	each_img_name_wo_ext = each_img_name.split('.')[0]
	path = './attachment'

	try:
		file_obj_in_str = open(path+'/'+each_img_name,'r+')
		#file_obj_in_str = open('./attachment/helloworld.txt','r+')
	except Exception as e:
		print "can't open" + str(e)

	img_file = io.BytesIO(file_obj_in_str.read())
	img_file.seek(0)
	fh_obj = filehive_collection.collection.Filehive()
	filehive_obj_exists = fh_obj.check_if_file_exists(img_file)
	file_gs_obj = None

	if not filehive_obj_exists:
		file_gs_obj = node_collection.collection.GSystem()

		file_gs_obj.fill_gstystem_values(
										request=None,
										name=unicode(name),
										group_set=[home_grp._id],
										# language=language,
										uploaded_file=img_file,
										created_by=author,
										member_of=[file_gst._id],
										origin={'user-icon-list-path':str(path)},
										unique_gs_per_file=True,
										content_org=content
										)
		#print "\n\nGS obj id "+str(file_gs_obj._id)+"\n\n"
		try:
			# file_gs_obj.save(groupid=home_grp._id)
			file_gs_obj.save(groupid=home_grp._id)
		except Exception as e:
			print 'exception while saving', e
	else:
		print "file exists"
		return 0

	return 'done'

def authenticate_user(mail,group_name):
	id = -1
	try:
		id = User.objects.get(email=mail).id
	except:
		return id,False,error_message["User does not exist"]
	
	if node_collection.find({ '_type': 'Group', 'name': unicode(group_name)}).count() > 0:
		if node_collection.find({ '_type': 'Group', 'name': unicode(group_name), 'author_set': {'$in': [id]} }).count() > 0:
			return id,True,error_message["User authenticated"]
		else:
			return id,False,error_message["User not a member of this group"]
	else:
		return id,False,error_message["Group does not exist"]


class MyHTMLParser(HTMLParser):
    pg_content = ''
    pg_name = ''
    flag1 = 0
    flag2 = 0
    def handle_starttag(self, tag, attrs):
        if(('name', 'pg_name') in attrs):
            self.flag1 = 1
        if(('name', 'pg_content') in attrs):
            self.flag2 = 1
        
    def handle_endtag(self, tag):
        a = 0       
    
    def handle_data(self, data):
        if(self.flag1 == 1):
            self.pg_name = data
            self.flag1 = 0
        if(self.flag2 == 1):
            self.pg_content = data
            self.flag2 = 0

    def return_values(self):
        return self.pg_name ,self.pg_content

def get_content(html_body):
    parser = MyHTMLParser()
    parser.feed(html_body)
    pg_name , pg_content = parser.return_values()
    pg_content = pg_content.strip()
    pg_name = pg_name.strip()
    return pg_name,pg_content

#********************MAIL-CLIENT*******************************************************#

detach_dir = '.'
if 'attachment' not in os.listdir(detach_dir):
	os.mkdir('attachment')
	print "made"
else:
	shutil.rmtree('attachment')
	os.mkdir('attachment')
	print "new made"
	
print 'hi'
def open_connection():
	try:
		connection = imaplib.IMAP4_SSL('imap.gmail.com')
		typ, accountDetails = connection.login(mio_from_email , mio_from_password)
		return connection
	except Exception as e:
		print 'Not able to sign in!'+str(e)
		
def open_unseen(conn):
	try:
		conn.select('INBOX')
		typ, data = conn.search(None, 'UNSEEN')
		return data
	except Exception as e:
		print 'Error searching Inbox.'+str(e)


def close_connection(conn):
	try:
		conn.close()
	except Exception as e:
		print "Couldn't close the Mailbox!"+str(e)
	try:
		conn.logout()
	except Exception as e:
		print "Couldn't logout of the account!"+str(e)

def parse_subject(sub):
	#Formats for subject:
	#If no square brackets are there in the subject,it means that
	#User wants to create a 'Page in home group'
	#else subject format should be as follows:-  [Group-Name][Page/Forum] Page/Forum name
	
	i=1
	s = 0
	e = 0
	group_name = 'home'
	activity = 'Page'
	activity_name = ''
	ctr = 0;
	for index in range(len(sub)):
		if(sub[index]=='[' or sub[index]==']'):
			ctr = ctr+1
	if(ctr==0):
		ctr=0
	elif(ctr==4):
		ctr=2
	elif(ctr==6):
		ctr=3
	while(i<=ctr):
		s = sub.find('[',e)+1
		e = sub.find(']',s)
		
		if(i==1):
			group_name = sub[s:e]
		elif(i==2):
			activity = sub[s:e]
		i = i+1
		s = e+1

	activity_name = sub[s:len(sub)]
	activity_name = activity_name.strip()
	return group_name,activity,activity_name

def parse_mail(email):
	s = email.find('<')+1
	e = email.find('>',s)
	return email[s:e]

class Email1:
	grp_name = ''
	activity = ''
	act_title = ''
	fromuser = ''
	Subject = ''
	Filename = None
	Body = ''
	MessageId = ''
	References = None
	update = False
	ObjectId = None

	def mail_extract(self, msgId, conn):
		try:
			typ, messageParts = conn.fetch(msgId, '(RFC822)')
			if typ != 'OK':
				print 'Error fetching mail.'
				raise
			emailBody = messageParts[0][1]
			mail = email.message_from_string(emailBody)
			for header in ['from']:
				fromuser = mail[header]
				self.fromuser = parse_mail(fromuser)
			for header in ['subject']:
				self.Subject = mail[header]
				self.grp_name, self.activity, self.act_title = parse_subject(self.Subject)
				
			for part in mail.walk():
				if (part.get_content_type() == 'text/plain'):
					self.Body = part.get_payload(decode=True)
					
			for part in mail.walk():
				if part.get_content_maintype() == 'multipart':
					continue
				if part.get('Content-Disposition') is None:
					continue
				self.Filename = part.get_filename()

				if bool(self.Filename):
					filePath = os.path.join(detach_dir, 'attachment', self.Filename)
					if not os.path.isfile(filePath):
						print "downloaded this",  self.Filename
						fp = open(filePath, 'wb')
						fp.write(part.get_payload(decode=True))
						fp.close()
					else:
						print "not downloaded " , self.Filename

			for header in ['Message-ID']:
				self.MessageId = mail[header]

			for header in ['References']:
				self.References = mail[header]

			if(self.References!=None):
				self.update = True
				start = self.References.find('<',0)
				end = self.References.find('>',start)
				end = end+1
				m_id = self.References[start:end]
				gst_obj = node_collection.find({'_type':u'GSystem'})
				
				for i in range(gst_obj.count()):
					if({'mio': m_id} in gst_obj[i].origin):
						self.ObjectId = str(gst_obj[i]._id)

				for part in mail.walk():
					if (part.get_content_type() == 'text/plain' or part.get_content_type() == 'text/html'):
						self.Body = part.get_payload(decode=True)
				
				self.act_title , self.Body = get_content(self.Body)
		except Exception as e:
			print 'Not able to download all attachments.'+str(e)

	def return_from(self):
		return self.fromuser
	def return_grp_name(self):
		return self.grp_name
	def return_activity(self):
		return self.activity
	def return_act_title(self):
		return self.act_title
	def return_body(self):
		return self.Body
	def return_sub(self):
		return self.Subject
	def return_MessageId(self):
		return self.MessageId
	def return_Ref(self):
		return self.References
	def return_update(self):
		return self.update
	def return_ObjectId(self):
		return self.ObjectId
	def return_fileName(self):
		return self.Filename

connection_state = open_connection()
unread_inbox = open_unseen(connection_state)
print unread_inbox
obj = Email1()
for msgId in unread_inbox[0].split():
	obj.mail_extract(msgId, connection_state)

	id,check,error = authenticate_user(mail=obj.return_from(),group_name=obj.return_grp_name())
	print id,error
	if(obj.return_update()==False):
		if(check==True):
			if(obj.return_fileName()!=None):
				p_id = upload(gp_name=obj.return_grp_name(),
										filename=obj.return_fileName(),
										name=obj.return_act_title(),
										author=id,content=obj.return_body())
			else:	
				p_id = create_page(name=obj.return_act_title(),content=obj.return_body(),
					created_by=id,group_name=obj.return_grp_name(),m_id=obj.return_MessageId())
			
			if(isinstance(p_id,str)):
				send_page(to_user=obj.return_from(),page_name=obj.return_act_title(),
					page_content=obj.return_body(),subject=obj.return_sub(),m_id=obj.return_MessageId(),ref=obj.return_Ref())
			else:
				print p_id
	else:
		update_page(name=obj.return_act_title(),content=obj.return_body(),id=obj.return_ObjectId(),user_id=id)
		send_page(to_user=obj.return_from(),page_name=obj.return_act_title(),
			page_content=obj.return_body(),subject=obj.return_sub(),m_id=obj.return_MessageId(),ref=obj.return_Ref())
close_connection(connection_state)

#**************************************************************************************#
