import email
import imaplib
import os
import sys
import time
import user_authentications
import create_page
import send_page
import update_page

detach_dir = '.'
if 'attachments' not in os.listdir(detach_dir):
	os.mkdir('attachments')
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
	i=1
	s = 0
	e = 0
	username = ''
	group_name = ''
	activity = ''
	activity_name = ''
	
	while(i<=4):
		s = sub.find('[',e)+1
		e = sub.find(']',s)
		
		if(i==1):
			username = sub[s:e]
		elif(i==2):
			group_name = sub[s:e]
		elif(i==3):
			activity = sub[s:e]
		else:
			activity_name = sub[s:e]
		i = i+1
	
	return username,group_name,activity,activity_name

def parse_mail(email):
	s = email.find('<')+1
	e = email.find('>',s)
	return email[s:e]

class Email1:
	username = ''
	grp_name = ''
	activity = ''
	act_title = ''
	fromuser = ''
	Subject = ''
	Filename = None
	Body = ''
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
				self.username, self.grp_name, self.activity, self.act_title = parse_subject(self.Subject)
				
			for part in mail.walk():
				if part.get_content_type() == 'text/plain':
					self.Body = part.get_payload(decode=True)
					
			for part in mail.walk():
				if part.get_content_maintype() == 'multipart':
					continue
				if part.get('Content-Disposition') is None:
					continue
				self.Filename = part.get_filename()

				if bool(self.Filename):
					filePath = os.path.join(detach_dir, 'attachments', self.Filename)
					if not os.path.isfile(filePath):
						print "downloaded this",  self.Filename
						fp = open(filePath, 'wb')
						fp.write(part.get_payload(decode=True))
						fp.close()
					else:
						print "not downloaded " , self.Filename
	
			for OBJID in ['_id']:
				self.ObjectId = mail[OBJID]
				print self.ObjectId
		except:
			print 'Not able to download all attachments.'

	def return_from(self):
		return self.fromuser
	def return_username(self):
		return self.username
	def return_grp_name(self):
		return self.grp_name
	def return_activity(self):
		return self.activity
	def return_act_title(self):
		return self.act_title
	def return_body(self):
		return self.Body
	def return_id(self):
		return self.ObjectId
	def return_sub(self):
		return self.Subject

c = open_connection()
d = open_unseen(c)
print d
obj = Email1()
for msgId in d[0].split():
	obj.mail_extract(msgId, c)

	if(obj.return_id()):
		print 'here'
		update_page.update_page(name=obj.return_act_title(),content=obj.return_body(),
			id=obj.return_id(),sub=obj.return_sub(),sendMailTo=obj.return_from())

		send_page.send_page(to_user=obj.return_from(),page_name=obj.return_act_title(),
				page_content=obj.return_body(),subject=obj.return_sub(),id=obj.return_id())

	else:
		id,check,error=user_authentications.authenticate_user(user=obj.return_username(),
			group_name=obj.return_grp_name())
		print error
		if(check==True):
			p_id = create_page.create_page(name=obj.return_act_title(),content=obj.return_body(),
					created_by=id,group_name=obj.return_grp_name(),sendMailTo=obj.return_from(),
					subject=obj.return_sub())
			if(isinstance(p_id,str)):
				send_page.send_page(to_user=obj.return_from(),page_name=obj.return_act_title(),
					page_content=obj.return_body(),subject=obj.return_sub(),id=p_id)
			else:
				print p_id

close_connection(c)

	 



