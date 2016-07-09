from gnowsys_ndf.ndf.models import *
import shutil
import email
import imaplib
import os
import sys
import time
import user_authentications
import create_page
import send_page
import update_page
import parse_html

detach_dir = '.'
if 'attachment' not in os.listdir(detach_dir):
	os.mkdir('attachment')
else:
	shutil.rmtree('/attachment')
	
print 'hi'
def open_connection():
	try:
		connection = imaplib.IMAP4_SSL('imap.gmail.com')
		typ, accountDetails = connection.login('ps.mio.bits@gmail.com', '1Guesswhat')
		return connection
	except:
		print 'Not able to sign in!'
		
def open_unseen(conn):
	try:
		conn.select('INBOX')
		typ, data = conn.search(None, 'UNSEEN')
		return data
	except:
		print 'Error searching Inbox.'


def close_connection(conn):
	try:
		conn.close()
	except:
		print "Couldn't close the Mailbox!"
	try:
		conn.logout()
	except:
		print "Couldn't logout of the account!"

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
				
				self.act_title , self.Body = parse_html.get_content(self.Body)

			#print "here 1"
			#print "1" + self.grp_name
			#print "2" + self.activity
			#print "3" + self.act_title
			#print "4" + self.fromuser
			#print "5" + self.Subject
			#print "7" + self.Body
			#print "8" + self.MessageId
			#print "9" + self.References
			#print self.ObjectId
			#print self.update
		except:
			print 'Not able to download all attachments.'

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

c = open_connection()
d = open_unseen(c)
print d
obj = Email1()
for msgId in d[0].split():
	obj.mail_extract(msgId, c)

	#if(obj.return_update()==False):
	#	id,check,error=user_authentications.authenticate_user(mail=obj.return_from(),group_name=obj.return_grp_name())
	#	print id,error
	#	if(check==True):
	#		p_id = create_page.create_page(name=obj.return_act_title(),content=obj.return_body(),
	#			created_by=id,group_name=obj.return_grp_name(),m_id=obj.return_MessageId())
	#		if(isinstance(p_id,str)):
	#			send_page.send_page(to_user=obj.return_from(),page_name=obj.return_act_title(),
	#				page_content=obj.return_body(),subject=obj.return_sub(),m_id=obj.return_MessageId(),ref=obj.return_Ref())
	#		else:
	#			print p_id
	#else:
	#	update_page.update_page(name=obj.return_act_title(),content=obj.return_body(),id=obj.return_ObjectId())
	#	send_page.send_page(to_user=obj.return_from(),page_name=obj.return_act_title(),
	#		page_content=obj.return_body(),subject=obj.return_sub(),m_id=obj.return_MessageId(),ref=obj.return_Ref())
close_connection(c)

	 



