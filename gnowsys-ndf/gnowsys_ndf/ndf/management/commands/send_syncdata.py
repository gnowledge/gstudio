from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage
import os
import requests
import shutil
from subprocess import call
from django.core.mail import EmailMessage

def sorted_ls(path):
    '''
    takes {
        path : Path to the folder location
    }
    returns {
        list of file-names sorted based on time
    }
    '''
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))

def connected_to_internet(url='http://www.google.com/', timeout=5):
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
    	print "Error occurred in : ", str(__file__)
        print("No internet connection available.")
    return False

class Command(BaseCommand):
	help = 'Will call the script to send the captured json and data files.'

	def handle(self, *args, **kwargs):
		if connected_to_internet() is False:
			return None

		syncdata_folder_path = os.path.dirname(__file__).split('/management')[0] + '/syncdata'
		list_of_syncdata_folders = []
		sent_folder_path = os.path.dirname(__file__).split('/management')[0] + '/sent_syncdata_files'

		if not os.path.exists(sent_folder_path):
			os.makedirs(sent_folder_path)

		try:
			# we take list of directories sorted by 'last modified time' so that changes captured first are sent first
			list_of_syncdata_folders = sorted_ls(syncdata_folder_path)
			print list_of_syncdata_folders
		except Exception as error:
			print 'File name and location is: ', str(__file__)
			print 'Error is : ', error

		for folder_name in list_of_syncdata_folders:
			print '**'*30
			path = syncdata_folder_path + '/' + folder_name
			list_of_syncdata_files = os.listdir(path)
			if connected_to_internet() is True:
				mail = EmailMessage()
				tstamp = folder_name
				mail.subject= "SYNCDATA_"+tstamp

				for filename in list_of_syncdata_files:
					file_path = path + '/' + filename
					mail.attach_file(file_path)
					print file_path

				mail.from_email = "Gstudio <t.metastudio@gmail.com>"
				mail.to = ['djangotest94@gmail.com']
				mail.send()
				shutil.move(path,sent_folder_path)

		# for filename in list_of_syncdata_files:
		# 	if connected_to_internet() is True:
		# 		mail = EmailMessage()
		# 		tstamp = filename[0:19]
		# 		mail.subject= "SYNCDATA_"+tstamp
		# 		file_path = syncdata_folder_path + "/" + filename
		# 		mail.attach_file(file_path)
		# 		mail.from_email = "Gstudio <t.metastudio@gmail.com>"
		# 		mail.to = ['djangotest94@gmail.com']
		# 		mail.send()
		# 		print file_path + '----------sent'
		# 		print '**'*30
		# 		shutil.move(file_path,sent_folder_path)
		# 	else:
		# 		print "syncdata_sending_stopped"



		# command = 'bash'+ ' ' + path1 + ' ' + path2
		# call([command],shell=True)
