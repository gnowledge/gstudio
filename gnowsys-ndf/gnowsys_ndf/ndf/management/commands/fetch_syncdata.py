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
import traceback
import filecmp
import tarfile

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
                                                if mail.subject.find('SYNC') != '-1': 
                                                    serverdir = process_mails(mail)
                                                #received_registries += serverdir
                                                if serverdir not in received_registries:         
                                                        received_registries.append(serverdir)                            
                                        result=chain_and_check_registry(received_registries)
                                        print result
                                        if result:
                                                server_sync(result)
                                                print "Data Inserted. Deleting Json Files"
                                                delete(result)      
                                else:
                                        print 'No new mails received'
                        metabox.delete()
                except Exception as error:
                        #delete temporary mailbox from database
                        metabox.delete()
                        print "The following error occured while fetching syncdata mails: "
                        print str(error)
                        traceback.print_exc()

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
        print filename
        #print 'output file name of decrypted attachment : \n %s' % op_file_name            
        #command = 'gpg --output ' + op_file_name + ' --decrypt ' + filename
        #std_out= subprocess.call([command],shell=True)
        list_of_decrypted_attachments.append(filename)
    return unpack_dir(list_of_decrypted_attachments,mail)

def unpack_dir(file_list,mail):
    # store this registry and data in different folder according to thei server name
    subject = mail.subject
    serverid = subject.split('_')[0]
    #strip anything before space
    serverid = serverid.split(' ')
    if len(serverid) > 1:
        serverid = serverid[1]
    else:
        print serverid
        serverid = serverid[0]
    if os.path.exists(serverid) == False:
        os.mkdir(serverid)
    manage_path = os.path.abspath(os.path.dirname(os.pardir))
    server_folder = os.path.join(manage_path,serverid+"/")
    #path_val = os.path.exists(serverdir)
    #if path_val == False:
    #    os.makedirs(serverdir)  
    #cp = "cp  -u " + str(file_list[0]) + " " + server_folder + "/"  
    #subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)    
    #os.popen(cp)
    #create zip patgh in server folder and dezip them 
    shutil.move(str(file_list[0]),server_folder)
    file_path = file_list[0]
    file_path = file_path.split('/')[-1:][0]
    zipfilepath =  os.path.join(server_folder,file_path)
    zipfilepath = os.path.abspath(zipfilepath)
    unzip(server_folder)
    return server_folder
    # unpack the file

def unzip(path):
    #unzip all the compressed files in a given directory 
    for dir,subdir,files in os.walk(path):
        for i in files:
            if '.gz' in i: 
                gz_path = os.path.join(dir,i)
                tar = tarfile.open(gz_path)    
                tar.extractall(path=path)
                tar.close()
                os.remove(gz_path)
    
'''
def fetch_registry(file_list,mail):
    #code written for fetchin packet information and data from the email as attachment
    registryfile = [i for i in file_list if i.find(".txt")!= -1]
    datafile = [ i for i in file_list if i.find(".json") != -1]
    # store this registry and data in different folder according to thei server name
    subject = mail.subject
    serverid = subject.split('_')[0]
    registryno = subject.split('_')[2]
    subject_split = subject.split('_')[-6:]
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
'''

def chain_and_check_registry(file_list):
    #file_list is list of servers from where files are recived
    all_file_path = []
    for i in file_list:
        #Get all the dir in the server folder
        dir_list = get_directories(i)
        #chain and check the sequence of th files
        file_list = chain_registries(dir_list,i)
        all_file_path += file_list
    return all_file_path

def get_directories(path):
    scanned_file = []    
    for dir_,_i,files in os.walk(path):
        if 'registries' not in dir_:
                scanned_file.append(dir_)
        for i in files:
            if '_sig' in i:
                path = os.path.join(dir_,i)
                decrypt_file(path)    
    return scanned_file 

def decrypt_file(filename):
    op_file_name = filename.split('_sig')[0]            
    print 'output file name of decrypted attachment : \n %s' % op_file_name            
    command = 'gpg --output ' + op_file_name + ' --decrypt ' + filename
    if not os.path.exists(op_file_name):
        std_out= subprocess.call([command],shell=True)   
    os.remove(filename)    
def chain_registries(dir_list,serverdir):
    create_stream = []
    streams = []
    continue_stream = True
    filepath_list = []
    temp_list = []
    readed = []
    if not os.path.exists(serverdir + "registries/"):
        os.mkdir(serverdir + "registries/")
    #method would chain the received registries
    #And store them to folder called registries
    #chaining which is incomplete wont be having their registry
    dir_list.remove(serverdir)
    sort_list = sorted(dir_list)
    for k,i in enumerate(sort_list):
        text = ""
        json = ""
        for files in os.listdir(i):
            if files.find(".txt") != -1:
               text = files
            if files.find(".json") != -1:
                json = files        
        filepath = os.path.join(i,text)
        current_file = open(filepath).readlines()
        if 'Start\n' in current_file or 'Start\r\n' in current_file or create_stream:
            create_stream.append(current_file[1])
            temp_list.append((os.path.join(i,json)))
            if readed and create_stream:
                if readed[2] == current_file[1]:
                    if  'End' in current_file:
                        filepath_list += temp_list
                        with open(serverdir + "registries/"+str("%06d" % k)+".txt",'w') as outfile:
                            for i in create_stream:
                                outfile.write(i)
                        create_stream = []
                        current_file = []
                        temp_list = []
                else:
                    #break the stream if chaining breaks
                    create_stream = []
                    current_file = []
                    temp_list = []    
        #condition when their exist only single file
        if ('Start\n' in current_file or 'Start\r\n' in current_file )and 'End' in current_file:
            with open(serverdir + "registries/"+str("%06d" % k)+".txt",'w') as outfile:
                for line in create_stream:
                    outfile.write(line)
            create_stream = []
            current_file = [] 
            temp_list = []            
            filepath_list.append((os.path.join(i,json)))
        if not create_stream:
             if 'Start\r\n' not in current_file:
                current_file = []           
        readed = current_file
    return filepath_list            
                            
def delete(file_list):
    #delete files which all are synced
    for  i in file_list:
        file_list = i.split("/")[0:-1]
        path = "/".join(file_list)
        print path
        shutil.rmtree(path)

def request_for_packet(packet_name):
    #print coming here
    mail = EmailMessage()
    # check the from address from which mail is coming 
    # and send a request to that mail servers to request the 
    # missing packet
    mail.to = ['example@example.com','example.upload@example.com']
    mail.subject = "Request" +"_" +str(packet_name)
    mail.send()     

        