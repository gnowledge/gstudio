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
import os

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
						text,data,serverdir = process_mails(mail)
                                                #received_registries += serverdir
                                                if serverdir not in received_registries:         
                                                        received_registries.append(serverdir)                            
						received_data += data	
                                        result=check_and_chain_registry(received_registries)
                                        if result == True:
					   server_sync(received_data)
                                           delete(received_registries)		
				else:
					print 'No new mails received'
			metabox.delete()
		except Exception as error:
			#delete temporary mailbox from database
			metabox.delete()
			print "The following error occured while fetching syncdata mails: "
			print str(error)

def process_mails(mail):
    #place files in server related directory
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
		std_out= subprocess.call([command],shell=True)
		list_of_decrypted_attachments.append(op_file_name)
    	return fetch_registry(list_of_decrypted_attachments,mail)    

def fetch_registry(file_list,mail):
    registryfile = [i for i in file_list if i.find(".txt")!= -1]
    datafile = [ i for i in file_list if i.find(".json") != -1]
    # store this registry and data in different folder according to thei server name
    subject = mail.subject
    serverid = subject.split('_')[0]
    registryno = subject.split('_')[2]
    subject_split = subject.split('_')[-6:]
    print subject_split
    folder_name = "_".join(subject_split)
    if os.path.exists(serverid) == False:
        os.mkdir(serverid)
    #enter inside the directory
    manage_path = os.path.abspath(os.path.dirname(os.pardir))
    #directory path
    server_folder = os.path.join(manage_path,serverid+"/")
    serverdir = os.path.join(server_folder,str(folder_name)+"/")
    path_val = os.path.exists(serverdir)
    if path_val == False:
		os.makedirs(serverdir)
    cp = "cp  -u " + str(registryfile[0]) + " " + serverdir + "/"  
    subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
    cp = "cp  -u " + str(datafile[0]) + " " + serverdir + "/"  
    subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)	
    return  registryfile,datafile,server_folder

def check_and_chain_registry(file_list):
    #os.popen("grep -r 'view' *").read()
    #code considers that files are coming from single server only
    filepath = ""
    directories = []
    missing_data_files = []
    print file_list
    for i in file_list:
        for dir_,_i,files in os.walk(i):                
            for filename in files:
                if filename.find(".txt") != -1:
                   filepath = os.path.join(dir_,filename)
                   break
    #this line should look into individual servers                   
    directories += os.listdir(file_list[0])               
    registryopen = open(filepath)
    #file open
    directories = [(i.split('_')[-1]) for i in directories]
    print directories
    for i in  registryopen:
        line = i
        objectid =  line[line.find("_id")+4:line[line.find("_id")+4:].find(",")+line.find("_id")+4]
        objectid = objectid.strip('\'')
        if objectid in directories:
            print "do nothing match happend"
        else:
            print "didnot find the match"
            missing_data_files.append(objectid)
    registryopen.close()

    if missing_data_files:
        for i in missing_data_files:
            request_for_packet(i)           
        return False
    else:
        return True    

def delete(file_list):
    #delete files which all are synced
    for  i in file_list:
        shutil.rmtree(i)

def request_for_packet(packet_name):
    #print coming here
    mail = EmailMessage()
    # check the from address from which mail is coming 
    # and send a request to that mail servers to request the 
    # missing packet
    mail.to = ['mukesh_5501@yahoo.com','mrunal.upload@gmail.com']
    mail.subject = "Request" +"_" +str(packet_name)
    mail.send()     

        