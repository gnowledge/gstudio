import email
import imaplib
import os
import sys
import time
import user_authentications
import create_page

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






c = open_connection()
d = open_unseen(c)
print d
obj = Email1()
for msgId in d[0].split():
	obj.mail_extract(msgId, c)
	id,check=user_authentications.authenticate_user(user=obj.return_username(),
		group_name=obj.return_grp_name())
	
	if(check==True):
		create_page.create_page(name=obj.return_act_title(),content=obj.return_body(),
			created_by=id,group_name=obj.return_grp_name())

close_connection(c)

