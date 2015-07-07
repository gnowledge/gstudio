from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage
import os
import requests
import shutil
from subprocess import call
from django.core.mail import EmailMessage
from imaplib import IMAP4
from django_mailbox.models import Mailbox
from gnowsys_ndf.settings import SYNCDATA_FETCHING_EMAIL_ID, SYNCDATA_FETCHING_EMAIL_ID_PASSWORD, SYNCDATA_FETCHING_IMAP_SERVER_ADDRESS
from gnowsys_ndf.ndf.views.mailclient import server_sync

def connected_to_internet(url='http://www.google.com/', timeout=2):
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
    	print "Error occurred in : ", str(__file__)
        print("No internet connection available.")
    return False

class Command(BaseCommand):
	help = 'Function to fetch mails from the MailID specified in settings.py '

	def handle(self, *args, **kwargs):
		if connected_to_internet() is False:
			return None

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
						print '**'*30; print mail; print ''
						server_sync(mail)
				else:
					print 'No new syncdata mails received'
			metabox.delete()
		except Exception as error:
			#delete temporary mailbox from database
			metabox.delete()
			print "The following error occured while fetching syncdata mails: "
			print str(error)						