from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage
import os
import urllib2
import requests
import shutil
from subprocess import call
from django.core.mail import EmailMessage
from imaplib import IMAP4
import subprocess
from django_mailbox.models import Mailbox
from gnowsys_ndf.settings import SYNCDATA_FETCHING_EMAIL_ID, SYNCDATA_FETCHING_EMAIL_ID_PASSWORD, SYNCDATA_FETCHING_IMAP_SERVER_ADDRESS
from gnowsys_ndf.ndf.views.mailclient import server_sync

def connected_to_internet(url='http://www.google.com/', timeout=2):
	try:
		urllib2.urlopen(url, timeout=timeout)
		return True
	except Exception as error:
		print 'Internet is not Available'
		print str(error)
		return False

class Command(BaseCommand):
	help = 'Function to fetch mails from the MailID specified in settings.py '

	def handle(self, *args, **kwargs):
		if connected_to_internet() is False:
			return None
		received_registries = []
		received_data = []	
		email = SYNCDATA_FETCHING_EMAIL_ID.replace('@','%40')
		metabox = Mailbox()
		metabox.name = 'Metabox'
		metabox.uri = 'imap+ssl://' + email + ':' + SYNCDATA_FETCHING_EMAIL_ID_PASSWORD + '@' + SYNCDATA_FETCHING_IMAP_SERVER_ADDRESS + '?archive=METABOX_SYNCDATA'
		
		try:
			metabox.get_connection()
		except IMAP4.error as error_obj:
			print "Syncdata emailid, password or imap server address improperly configured! Please check settings.py"
			print str(error_obj)
			return 'Syncdata emailid, password or imap server address improperly configured! Please check settings.py'
		except Exception as error_obj:
			print 'Some error occured while trying to establish connection with : %s for fetching syncdata', SYNCDATA_FETCHING_EMAIL_ID
			print str(error_obj)
			return str(error_obj)

		metabox.save()
		try:
			if connected_to_internet:
				syncdata_mails_list = metabox.get_new_mail()
				if syncdata_mails_list:
					for mail in syncdata_mails_list:
						text,data = process_mails(mail)
						received_registries += text
						received_data += data			
					chain_registry(received_registries)
					print received_data
					server_sync(received_data)		
				else:
					print 'No new mails received'
			metabox.delete()
		except Exception as error:
			#delete temporary mailbox from database
			metabox.delete()
			print "The following error occured while fetching syncdata mails: "
			print str(error)

def process_mails(mail):
	all_attachments = mail.attachments.all()
	all_attachments_path = []
	json_file_path = ''
	file_object_path = ''


	''' Code reads all the attachmnet of the single mail '''    
	''' Code to decrypt every attachment and create a list with the file paths of decrypted attachments'''
	list_of_decrypted_attachments = []
	for attachment in all_attachments:
		filename = attachment.document.path
		op_file_name = filename.split('_sig')[0]            
		print 'output file name of decrypted attachment : \n %s' % op_file_name            
		command = 'gpg --output ' + op_file_name + ' --decrypt ' + filename
		print "error point croseed"
		std_out= subprocess.call([command],shell=True)
		list_of_decrypted_attachments.append(op_file_name)
    	return fetch_registry(list_of_decrypted_attachments)    

def fetch_registry(file_list):
    registryfile = [i for i in file_list if i.find(".txt")!= -1]
    datafile = [ i for i in file_list if i.find(".json") != -1]
    print "the datafile",datafile
    return  registryfile,datafile   
def chain_registry(file_list):
	print file_list
        