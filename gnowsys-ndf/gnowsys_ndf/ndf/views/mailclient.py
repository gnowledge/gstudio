from django.core.mail import EmailMessage
from django.views.generic import TemplateView
from django.shortcuts import render
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.models import node_collection, triple_collection, gridfs_collection
from django.contrib.auth.models import User
from gnowsys_ndf.ndf.views.methods import get_drawers, get_execution_time
from gnowsys_ndf.ndf.views.methods import get_user_group, get_user_task, get_user_notification, get_user_activity, get_execution_time
from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_all_user_groups

#---------Django Mailbox imports----------------#
from django_mailbox.models import Mailbox

#---------python imports------------------------#
from imaplib import IMAP4
from gnowsys_ndf.ndf.views.file import save_file
from bson import json_util
from os import listdir
from os.path import isfile, join
from email.parser import Parser
import email.utils
import socket
import sqlite3
import os
import re
import shutil
import urllib2
import io
import mailbox
import datetime
import subprocess

#-----------------Dictionary of popular servers--------------#
server_dict = {
    "Gmail": "imap.gmail.com",
    "Yahoo_Mail": "imap.mail.yahoo.com",
    "Yahoo_Mail_Plus": "plus.imap.mail.yahoo.com",
    "AT&T": "imap.ntlworld.com",
    "Office365": "outlook.office365.com",
    "Outlook": "imap-mail.outlook.com",
    "AOL": "imap.aol.com",
    "Mail": "imap.mail.com",
    "Verizon": "incoming.verizon.net",
    "Bits_Pilani": "imap.gmail.com",
    "Rediffmail": "pop.rediffmail.com"
}

@login_required
def mailclient(request, group_id):
    '''
    This function fetches the mailboxes and the corresponding E-Mail IDs.
    The Mailbox.active_mailboxes.all() returns all mailboxes but given a 
    user has his/her own set of mailboxes , this is checked by mapping it
    through table 'user_mailboxes' which consists of the (user_id,mailbox_id)
    '''

    group_name, group_id = get_group_name_id(group_id)
    home_grp_id = node_collection.one({'name': "home"})

    mailbox_names = []
    try:
        # To set the relative path to 'example-sqlite3.db' file
        settings_dir1 = os.path.dirname(__file__)               # to find the parent folder of the current file
        settings_dir2 = os.path.dirname(settings_dir1)
        settings_dir3 = os.path.dirname(settings_dir2)
        path = os.path.abspath(os.path.dirname(settings_dir3))
        
        conn = sqlite3.connect(path + '/example-sqlite3.db')
        user_id = str(request.user.id)

        query = 'select mailbox_id from user_mailboxes where user_id=\''+user_id+'\''
        cursor = conn.execute(query)

        mailbox_ids=[]
        mailbox_emailids=[]
        all_mailboxes_in_db = Mailbox.active_mailboxes.all()
        for row in cursor:
            mailbox_ids.append(row[0])
        print "mbox ids", mailbox_ids        
        query = 'select name from django_mailbox_mailbox where id='
        for box_id in mailbox_ids:
            box_id = str(box_id)
            query_2 = query + box_id
            cursor = conn.execute(query_2)
            for row in cursor:
                mailbox_names.append(row[0])
                temp_box = Mailbox.active_mailboxes.get(id=box_id)
                temp_uri = temp_box.uri
                emailid = temp_uri.split("//")[1].split(":")[0].replace('%40','@')
                mailbox_emailids.append(emailid)

    # add exception
    except Exception as error:
        error_obj= str(error) + ", mailclient() fn"
        return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})
        #return HttpResponseRedirect(reverse('mailclient_error_display', args=(group_id,error_obj,)))

    #TODO: Handle the test case which requires the next two lines of code
    if group_id == home_grp_id['_id']:
        return render(request, 'ndf/oops.html')
    mailbox_data = []
    for i in range(len(mailbox_names)):
        temp = {}
        temp['name'] = mailbox_names[i]
        temp['emailid'] = mailbox_emailids[i]
        mailbox_data.append(temp)

    return render(request, 'ndf/mailclient.html', {
        'groupname': group_name,
        'groupid': group_id,
        'group_id': group_id,
        'mailbox_data': mailbox_data
    })
 
@login_required
@get_execution_time
def mailbox_create_edit(request, group_id):
    '''
    takes {
    request : HTTP request
    group_id : gstudio group id
    }
    returns {
                template which shows the create new mailbox form
    }

    This function creates a new Mailbox. First it renders the template which has the input form. When the form is submitted, this function
    is called again and the data is used to create a new mailbox. The email-id, password and the website on which the email-id is made 
    is verified and if the credentials are correct a new mailbox is saved in the database. Also the function adds the mailbox id, user_id
    record to another database to keep record of which user has which mailbox id.
    '''
    group_name, group_id = get_group_name_id(group_id)
    home_grp_id = node_collection.one({'name': "home"})

    if group_id == home_grp_id['_id']:
        return render(request, 'ndf/oops.html')
    template = "ndf/mailbox_create_edit.html"
    if request.method == "POST":  # create or edit
        # get all data from the form
        mailbox_name = request.POST.get("mailboxname", "")
        mailbox_name= mailbox_name.replace(" ","_")
        emailid = request.POST.get("emailid", "")
        pwd = request.POST.get("password", "")
        domain = request.POST.get("domain","")

        emailid_split = emailid.split('@')
        # make a mailbox from the above details
        newbox = Mailbox()

        #TODO: clean up mailbox_name since it will later go as part of url for :settings, edit and delete pages.
        characters_not_allowed= ['!','@',]
        newbox.name = mailbox_name
        webserver = server_dict[domain]

        try:
            uri = "imap+ssl://" + emailid_split[0] + "%40" + emailid_split[1] +  ":" + pwd + "@" + webserver + "?archive=" + mailbox_name.replace(" ","_")
            newbox.uri = uri
            print uri
        except IndexError: 
            print "Incorrect Email ID given!"
            error_obj= "Incorrect Email ID given!"
            return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})
            return HttpResponseRedirect(reverse('mailclient', args=(group_id,)))
        
        try:
            #may throw exception
            newbox.get_connection()
        except socket.gaierror :
            print "CONNECTION ERROR, COULDNT CONFIGURE MAILBOX WEBSERVER"
            error_obj= "CONNECTION ERROR, COULDNT CONFIGURE MAILBOX WEBSERVER"
            return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})
            
        except IMAP4.error:
            print "Either the emailid or password is incorrect or you have chosen the wrong account (domain)"
            error_obj= "Either the emailid or password is incorrect or you have chosen the wrong account (domain)"
            return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})
        
        #only on calling save() the mailbox is alotted an id
        newbox.save()

        try:
            settings_dir1 = os.path.dirname(__file__)
            settings_dir2 = os.path.dirname(settings_dir1)
            settings_dir3 = os.path.dirname(settings_dir2)
            path = os.path.abspath(os.path.dirname(settings_dir3))

            #may throw exception
            conn = sqlite3.connect(path + '/example-sqlite3.db')
            user_id = str(request.user.id)
            #query to insert (user.id,mailbox.id) pair in 'mapping' database
            query = 'insert into user_mailboxes values (?,?);'

            #may throw exception
            cursor = conn.execute(query, (request.user.id, newbox.id))            
            conn.commit()
            conn.close()
        except Exception as error:
            #Very imp: must delete the mailbox if this exception occurs
            #TODO: not only delete newbox but also remove entry from 'mapping' Database
            newbox.delete()
            print error
            error_obj= str(error) + ",mailbox_create_edit() fn, Mailbox created will be deleted"
            return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})
        
        
        return HttpResponseRedirect(reverse('mailclient', args=(group_id,)))
    else:
        title = "Add A New Mailbox"
        variable = RequestContext(request, {'title': title,
                                            'groupname': group_name,
                                            "group_id" : group_id,
                                            "groupid" : group_id,
                                            'server_dict' : server_dict 
                                            })
        return render_to_response(template, variable)





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

def read_mails(path, _type, displayFrom):
    '''
    takes {
    path        :   path to the maildir folder,
    _type       :   0 for new mails , 1 for already read mails i.e. current mails,
    displayFrom :   the staring number like 1..20 or 21...40
    }
    returns {
                    set of emails
    }
    '''
    cur_path = path + '/cur'
    new_path = path + '/new'
    
    start = displayFrom
    end  = displayFrom + 20

    p = Parser()

    mails_list = []

    if _type == '0':
        all_unread_mails = sorted_ls(new_path)
        all_unread_mails.reverse()
        
        if end > len(all_unread_mails):
            end = len(all_unread_mails)

        required_mails = all_unread_mails[start:end]

        for temp_mail in required_mails:
            temp = {}
            temp_list = []
            msg = p.parse(open(join(new_path, temp_mail)))
            for key in msg.keys():
                if key == 'Attachments':
                    if msg[key] != '':
                        temp[key] = msg[key].split(';')
                    else:
                        temp[key] = []
                else:       
                    temp[key] = msg[key]
            
            for attachment_path in temp["Attachments"]:
                if attachment_path != '':
                    _name = attachment_path.split("/")[-1]
                    temp_list.append(_name)

            temp["attachment_filename"] = temp_list

            print temp["attachment_filename"], "<<< ATTACH"

            temp['text'] = msg.get_payload()
            temp['file_name'] = temp_mail
            mails_list.append(temp)
            
        return mails_list
    
    if _type == '1':
        all_unread_mails = sorted_ls(cur_path)
        all_unread_mails.reverse()
        
        if end > len(all_unread_mails):
            end = len(all_unread_mails)

        required_mails = all_unread_mails[start:end]

        for temp_mail in required_mails:
            temp = {}
            temp_list = []
            msg = p.parse(open(join(cur_path,temp_mail)))
            for key in msg.keys():
                if key == 'Attachments':
                    if msg[key] != '':
                        temp[key] = msg[key].split(';')
                    else:
                        temp[key] = []
                else:       
                    temp[key] = msg[key]

            for attachment_path in temp["Attachments"]:
                if attachment_path != '':
                    _name = attachment_path.split("/")[-1]
                    temp_list.append(_name)

            temp["attachment_filename"] = temp_list
            temp['text'] = msg.get_payload()
            mails_list.append(temp)

        return mails_list   


def store_mails(mails, path):
    '''
    takes {
        mails   :   The E-Mail message that needs to be stored as a file 
        path    :   The path where the file needs to be stored
    }
    
    Stores the mails in the Maildir format
    '''
    for mail in mails:
        from_addr = email.utils.formataddr(('Author', mail.from_address[0]))
        to_addr = email.utils.formataddr(('Recipient', mail.to_addresses[0]))
        now = datetime.datetime.now()
        cc_addr = None
        
        if len(mail.to_addresses) > 1:
            nameslist = mail.to_addresses[1:-1]     
            cc_list=""
            for names in nameslist:
                cc_list = cc_list + names + ';'
            
            cc_list = cc_list + mail.to_addresses[-1]
            cc_addr = email.utils.formataddr(('CC List', cc_list))

        mbox = mailbox.Maildir(path)
        mbox.lock()

        try:
            msg=mailbox.mboxMessage()
            unixform = mail.mailbox.name + ' ' + now.ctime()
            msg.set_unixfrom(unixform)
            msg['From'] = from_addr
            msg['To'] = to_addr
            if len(mail.to_addresses) > 1:
                msg['CC'] = cc_addr
            
            msg['Subject'] = mail.subject
            mail_data = mail.html
            mail_data = mail_data.replace('\r', '')
            msg.set_payload(mail_data)

            # To prepare a list of path of the attachments in comma-separated format
            if mail.attachments.count > 0:
                all_attachments = mail.attachments.all()
                all_attachments_path = ''
                for attachment in all_attachments:
                    all_attachments_path = all_attachments_path + attachment.document.path + ';'
                
                msg['Attachments'] = all_attachments_path

                

            mbox.add(msg)
            mbox.flush()

        except Exception as ex:
            print ex
            # redirect to the error-display page
        finally:
            mbox.unlock()
    return

def server_sync(mail):
    if 'SYNCDATA' in mail.subject:
        all_attachments = mail.attachments.all()
        all_attachments_path = []
                        
        json_file_path = ''
        file_object_path = ''

        

        ''' Code to decrypt every attachment and create a list with the file paths of decrypted attachments'''
        list_of_decrypted_attachments = []
        for attachment in all_attachments:
            filename = attachment.document.path
            op_file_name = filename.split('_sig')[0]
            command = 'gpg --output ' + op_file_name + ' --decrypt ' + filename
            subprocess.call([command],shell=True)
            list_of_decrypted_attachments.append(op_file_name)

        print '##**'*30
        print list_of_decrypted_attachments
        
        for file_path in list_of_decrypted_attachments:
            if file_path[-4:] == 'json':
                json_file_path = file_path
            else:
                file_object_path = file_path

        node_exists = False
        with open(json_file_path,'r') as json_file:
            json_data = json_file.read()
            json_data=json_data.replace('\\"','"').replace('\\\\"','\'').replace('\\\n','').replace('\\\\n','')
            json_data = json_util.loads(json_data[1:-1])
            # print json_data
                            
            cursor= None                            
            try:
                settings_dir1 = os.path.dirname(__file__)
                settings_dir2 = os.path.dirname(settings_dir1)
                settings_dir3 = os.path.dirname(settings_dir2)
                path = os.path.abspath(os.path.dirname(settings_dir3))
                #may throw error        
                conn = sqlite3.connect(path + '/example-sqlite3.db')
                user_id = json_data[u'created_by']
                query = 'select username from auth_user where id=\''+str(user_id)+'\''
                cursor = conn.execute(query)

            except Exception as error:
                print error
            
            username=None
            for row in cursor:
                username = row[0]    
            
            if file_object_path != '':
                ''' for the creation of the file object '''
                with open(file_object_path,'rb+') as to_be_saved_file:
                    req_groupid = None
                    for obj in json_data["group_set"]:
                        temp_obj = node_collection.one({"_id": obj, "_type" : "Group" })
                        if temp_obj is not None:
                            req_groupid = obj
                            break

                    to_be_saved_file = io.BytesIO(to_be_saved_file.read())
                    to_be_saved_file.name = json_data["name"]

                    node_id, is_video = save_file(to_be_saved_file, json_data["name"], json_data["created_by"], req_groupid, json_data["content_org"], json_data["tags"], json_data["mime_type"].split('/')[1], json_data["language"], username, json_data["access_policy"],server_sync=True,object_id=json_data["_id"],oid=True)

                    if type(node_id) == list:
                        node_id = node_id[1]
                                    
                    node_to_update = node_collection.one({ "_id": node_id })
                                    
                    temp_dict = {}
                    for key, values in json_data.items():
                        if key != 'fs_file_ids':
                            temp_dict[key] = values
                
                    node_to_update.update(temp_dict)
                    node_to_update.save()
                            
            else:
                # We need to check from the _type what we have that needs to be saved
                temp_node = node_collection.one({"_id" : json_data["_id"]})
                                
                if temp_node is not None:
                    temp_dict = {}
                    for key, values in json_data.items():
                        if key != u'fs_file_ids':
                            temp_dict[key] = values

                    temp_node.update(temp_dict)
                    temp_node.save()
                                
                else:
                    # for pages
                    temp_node = node_collection.collection.GSystem()
                                    
                    temp_dict = {}
                    ''' dictionary creation '''
                    for key, values in json_data.items():
                        temp_dict[key] = values

                    temp_node.update(temp_dict)
                    temp_node.save()

@get_execution_time
def get_mails_in_box(mailboxname, username, mail_type, displayFrom):
    '''
    takes{
        mailboxname :   The name of the mail-box whose mails need to be fetched
                        ( both new and old, depending upon the parameter mail_type)
        username    :   The user to whom mailbox must belong
        mail_type   :   0 for new mails , 1 for already read mails i.e. current mails
        displayFrom :   The staring number like 1..20 or 21...40
    }
    returns{
            List of all the mails in the range (displayFrom, displayFrom + 20) from the mailbox
            belonging to the user with the User-Name as username and Mail-Box name as mailboxname 
    }

    This function establishes the connection and fetches the mails from the corresponding imap server.
    During fetching it checks for the subject of the mail and then segregates mails either for local 
    storage or update the mongodb with the data received. The mails are stored in maildir format in the 
    'ndf/mailbox_data' folder.
    '''

    # To get the mail box instance based upon the unique name of the mailbox
    all_mail_boxes= Mailbox.objects.all()
    required_mailbox=None
    for box in all_mail_boxes:
        if box.name == mailboxname:
            required_mailbox=box
            break
    
    # To find the path to the mailbox_data folder where the mails are stored in the maildir format
    settings_dir = os.path.dirname(__file__)
    PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
    path = os.path.join(PROJECT_ROOT, 'mailbox_data/')
    path = path + username
    
    
    # Necessary for the storage of mails in maildir format : if not exists -> make the corresponding the directories
    if not os.path.exists(path):
        os.makedirs(path)
    
    path = path + '/' + mailboxname
    if not os.path.exists(path):
        os.makedirs(path)

    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(path + '/tmp'): 
        os.makedirs(path + '/tmp')
    if not os.path.exists(path + '/cur'):
        os.makedirs(path + '/cur')
    if not os.path.exists(path + '/new'):
        os.makedirs(path + '/new')

    displayFrom = int(displayFrom)

    if required_mailbox is not None:
        emails=[]

        if mail_type == '0':
            if displayFrom == 0:
                print 'FETCHING NEW MAILS'
                print required_mailbox
                all_mails=required_mailbox.get_new_mail()
                print 'FETCHING DONE'

                print len(all_mails)
                # To manage the mails that comes as a part of the server-sync technique
                for mail in all_mails:
                    server_sync(mail)

                # To read the mails from the directories
                print 'STORING NEW MAILS'
                store_mails(all_mails,path)
                print 'STORAGE DONE'
            
            print 'FETCHING FROM LOCAL STORAGE'
            all_mails = read_mails(path, mail_type, displayFrom)
            i=1
            for mail in all_mails:
                emails.append({'mail_id':i, 'mail_data':mail})
                i+=1

            print 'FETCHING DONE'
            return emails
        else:
            print 'FETCHING OLD MAILS'
            all_mails = read_mails(path, mail_type, displayFrom)
            i=1
            for mail in all_mails:
                emails.append({'mail_id':i, 'mail_data':mail})
                i+=1
            print 'FETCHING DONE'
            return emails
    else:
        print 'ERROR : NO SUCH MAILBOX'
        return None

@login_required
@get_execution_time
def render_mailbox_pane(request,group_id):
    '''
    This function sends the fecthed mails using 'get_mails_in_box' 
    function to the mailcontent template as a result of post request.
    '''

    group_name, group_id = get_group_name_id(group_id)
    template = "ndf/mailcontent.html"
    if request.method=='POST' and request.is_ajax():
        mails = get_mails_in_box(request.POST['mailBoxName'], request.POST['username'], request.POST['mail_type'], request.POST['startFrom'])
        variable = RequestContext(request, {
        'groupname': group_name,
        "group_id" : group_id,
        "groupid"  : group_id,
        "emails"   : mails 
        })
        return render_to_response(template,variable)


@login_required
@get_execution_time
def mailbox_edit(request, group_id,mailboxname):
    '''
    takes {
    request : HTTP request
    group_id : gstudio group id
    mailboxname: the name of the mailbox to be edited
    }
    returns {
                    template which shows the edit form
    }

    This function is used to edit the mailbox. The user has to change all properties: mailbox name, email-id, password and the account
    on which the id is made. The supplied credentials are checked and if it is verified the mailbox is edited or an appropriate error
    message is returned.
    '''
    group_name, group_id = get_group_name_id(group_id)
    home_grp_id = node_collection.one({'name': "home"})
    title = "Edit Mailbox"
    variable = RequestContext(request, {'title': title,
                                        'groupname': group_name,
                                        'groupid': group_id,
                                        'group_id': group_id,
                                        'server_dict' : server_dict,
                                        'mailboxname' : mailboxname,
                                            
                                        })
    template = "ndf/edit_mailbox.html"
    if request.method == "POST":  # create or edit
        # get all data from the form
        mailbox_name = request.POST.get("mailboxname", "")
        mailbox_name = mailbox_name.replace(" ","_")
        emailid = request.POST.get("emailid", "")
        pwd = request.POST.get("password", "")
        domain = request.POST.get("domain","")
        emailid_split = emailid.split('@')
        webserver = server_dict[domain]

        try:
            uri = "imap+ssl://" + emailid_split[0] + "%40" + emailid_split[1] +  ":" + pwd + "@" + webserver + "?archive=" + mailbox_name.replace(" ","_")
        except IndexError:
            error_obj= "Incorrect Email ID given!"
            return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})

        try: 
            newbox= Mailbox()
            newbox.uri = uri
            #may throw error
            newbox.get_connection()
        except socket.gaierror :
            print "CONNECTION ERROR, COULDNT CONFIGURE MAILBOX WEBSERVER"
            error_obj= "CONNECTION ERROR, COULDNT CONFIGURE MAILBOX WEBSERVER"
            return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})
            
        except IMAP4.error:
            print "Either the emailid or password is incorrect or you have chosen the wrong account (domain)"
            error_obj= "Either the emailid or password is incorrect or you have chosen the wrong account (domain)"
            return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})
            
        try:
            settings_dir1 = os.path.dirname(__file__)
            settings_dir2 = os.path.dirname(settings_dir1)
            settings_dir3 = os.path.dirname(settings_dir2)
            path = os.path.abspath(os.path.dirname(settings_dir3))
            #may throw error        
            conn = sqlite3.connect(path + '/example-sqlite3.db')
            user_id = str(request.user.id)
            query = 'select mailbox_id from user_mailboxes where user_id=\''+user_id+'\''
            cursor = conn.execute(query)

        except Exception as error:
            print error
            error_obj= str(error) + ", mailbox_edit() fn"
            return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})
            
        mailbox_ids=[]
        for row in cursor:
            mailbox_ids.append(row[0])

        # edit mailbox with passed mailbox_id 
        box = None
        flag = 0
        boxes= Mailbox.active_mailboxes.all()
        for box in boxes:
            if box.name == mailboxname and box.id in mailbox_ids:
                flag = 1
                break

        if flag == 1:
            box.name= mailbox_name
            box.uri=uri
            box.save()
        return HttpResponseRedirect(reverse('mailclient', args=(group_id,)))
    return render_to_response(template, variable)


@login_required
@get_execution_time
def mailbox_delete(request, group_id,mailboxname):
    '''
    takes {
        request : HTTP request
        group_id : gstudio group id
        mailboxname: the name of the mailbox to be deleted
    }
    returns {
                    template which shows the delete options page
    }

    This function is used to delete the mailbox. The user is directed to a confirmation page. If the user also selects to save the
    mails before deleting the mailbox, the function moves the mails into archive folder. Otherwise the function deletes the mails 
    and the mailbox from the database if the user confirms deletion.
    '''
    group_name, group_id = get_group_name_id(group_id)
    title = "Delete Mailbox"
    variable = RequestContext(request, {'title': title,
                                        'groupname': group_name,
                                        "group_id" : group_id,
                                        "groupid" : group_id,
                                        'mailboxname' : mailboxname,
                                        })
    template = "ndf/delete_mailbox.html"
    if request.method == "POST":  # create or edit
        yes = request.POST.get("save-yes",None)
        no = request.POST.get("save-no",None)
        save_mails = request.POST.get("mails_save_option",None)
        mailbox_name= request.POST.get("mailbox_name","")
        user_id = request.POST.get("user_id","")
        mailbox_names = []

        if save_mails == "YES" and yes == "YES":
            mails_path_dir1 = os.path.dirname(__file__)
            mails_path_dir2 = os.path.dirname(mails_path_dir1)
            src = str(mails_path_dir2) + "/mailbox_data/" + str(request.user.username) + "/" + mailboxname
            dst = str(mails_path_dir2) + "/mailbox_data" + "/Archived_Mails/" + str(request.user.username) + "/" + mailboxname 
            print '*'*30
            print src
            print dst
            try:
                shutil.move(src,dst)
            except Exception as error:
                print error
                error_obj= str(error) + ", mailbox_delete() fn"
                return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})    
            
        elif save_mails== "NO" and yes =="YES":
            mails_path_dir1 = os.path.dirname(__file__)
            mails_path_dir2 = os.path.dirname(mails_path_dir1)
            src = str(mails_path_dir2) + "/mailbox_data/" + str(request.user.username) + "/" + mailboxname
                       
            print '*'*30
            print src
            try:
                shutil.rmtree(src)
            except Exception as error:
                print error
                error_obj= str(error) + ", mailbox_delete() fn"
                return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})    

        if yes == "YES":
            
            settings_dir1 = os.path.dirname(__file__)
            settings_dir2 = os.path.dirname(settings_dir1)
            settings_dir3 = os.path.dirname(settings_dir2)
            path = os.path.abspath(os.path.dirname(settings_dir3))
            conn = None
            try:
                conn = sqlite3.connect(path + '/example-sqlite3.db')
                query = 'select mailbox_id from user_mailboxes where user_id=\''+user_id+'\''
                cursor = conn.execute(query)
            except Exception as error:
                print error
                error_obj= str(error) + ", mailbox_delete() fn"
                return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})    

            mailbox_ids=[]
            for row in cursor:
                mailbox_ids.append(row[0])                  
            print mailbox_ids        
            box = None
            flag = 0
            boxes= Mailbox.active_mailboxes.all()
            for box in boxes:
                if box.name == mailbox_name and box.id in mailbox_ids:
                    flag = 1
                    break

            if flag == 1:
                #delete from our 'mapping' database (the database which tracks which user_id is asscociated with which mailbox_id )                    

                # conn2 = sqlite3.connect(path + '/example-sqlite3.db')
                query = 'delete from user_mailboxes where mailbox_id='+str(box.id)
                cursor = conn.execute(query)
                conn.commit()

                #NOTE: we must delete the mailbox from our 'mapping' database first and then from django_mailbox database because 
                # when you call the delete function of django_mailbox API on a mailbox object, the mailbox id is lost!
                # And we need that id value to delete from our 'mapping' database. Hence order is important

                #delete mailbox from django_mailbox's database
                box.delete()
                print "%s Deleted from django_mailbox" % mailbox_name
            else:
                print "Box not found > (fn: delete_mailbox)"
            conn.close()

        return HttpResponseRedirect(reverse('mailclient', args=(group_id,)))
    return render_to_response(template, variable)

@get_execution_time
def mailclient_error_display(request, group_id, error_obj):
    '''
    takes {
        request : HTTP request
        group_id : gstudio group id
        error_obj: a string describing the error
    }
    returns {
            template which displays the error message
    }

    Function renders a template which displays the error string passed
    '''
    template = "ndf/mailclient_error.html"
    group_name, group_id = get_group_name_id(group_id)
    title = "Error Page"
    # print error_obj
    context_dict = { "title" : title,
                    "group_name" : group_name,
                    "group_id" : group_id,
                    "groupid" : group_id
                    }
    variable = RequestContext(request,context_dict)
    return render_to_response(template,variable)

@login_required
@get_execution_time
def mailbox_settings(request, group_id,mailboxname):    
    '''
    takes {
        request : HTTP request
        group_id : gstudio group id
        mailboxname: the name of the mailbox for which settings have to be changed
    }
    returns {
                    template which shows the settings page
    }

    Function directs user to settings page.
    '''
    template = "ndf/mailclient_settings.html"
    group_name, group_id = get_group_name_id(group_id)
    title = "Settings Page"
    
    context_dict = { "title" : title,
                    "group_name" : group_name,
                    "group_id" : group_id,
                    "groupid" : group_id,
                    "mailbox_name" : mailboxname
                    }
    variable = RequestContext(request,context_dict)
    return render_to_response(template,variable)    

@login_required
@get_execution_time
def compose_mail(request, group_id,mailboxname):    
    '''
        takes {
        request : HTTP request
        group_id : gstudio group id
        mailboxname: the name of the mailbox via which new mail has to be sent
    }
    returns {
        template which shows the email message form or error page
    }

    The function renders the form to create a new email and then processes it when the form is submitted (user hits 'send'). The 'to',
    'cc', 'bcc', subject and body are processed and attached to django_mailbo's EmailMessage class object(email object). Files added 
    as 'attachments' are read and attached to the email object and the mail is sent.

    '''
    template = "ndf/compose_mail.html"
    group_name, group_id = get_group_name_id(group_id)
    title = "New Mail"

    context_dict = { "title" : title,
                    "group_name" : group_name,
                    "group_id" : group_id,
                    "groupid" : group_id,
                    "mailbox_name" : mailboxname
                    }
    variable = RequestContext(request,context_dict)

    if request.method == "POST":
        user_id = request.POST.get("user_id","")
        to = request.POST.get("to_addrs", "")
        subject = request.POST.get("subject", "")
        body = request.POST.get("body_editor", "")
        sum_size = 0
        files_list = request.FILES.getlist('attached_files')

        # if files_list is not None:
        #     for f in files_list:
        #         sum_size = sum_size+f.size
        #     print sum_size
        #     print (sum_size/(1024.0*1024.0))
        #     if (sum_size/(1024.0*1024.0)) > 25:
        #         error_obj= "Attachment Size is %dMB. It exceeds maximum allowed size : 25MB. Please go back and \"re-select\"  attachments. Press the 'back' button on your browser. Your data will still be there." % (sum_size/(1024.0*1024.0))
        #         return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})

        to=to.replace(" ","")
        to_list=to.split(";")

        cc = request.POST.get("cc_addrs", "")
        if cc:
            cc=cc.replace(" ","")
            cc_list=cc.split(";")
        
        bcc = request.POST.get("bcc_addrs", "")
        if bcc:
            bcc=bcc.replace(" ","")
            bcc_list=bcc.split(";")

        mail = EmailMessage()
        mail.to = to_list
        if cc:
            mail.cc = cc_list
        if bcc:
            mail.bcc = bcc_list

        #TODO: extract email id from db using mailbox name and user id
        mail.from_email = "MetaStudio <abtiwari94@gmail.com>"
        mail.subject= subject
        mail.content_subtype = "html"
        mail.body = body 
        for f in files_list:        
            print '-'*30
            print f.name
            print f.size
            print f.content_type
            #TODO
            print f.multiple_chunks(1024)
            print '-'*30
            mail.attach(f.name,f.read(),f.content_type)
        print body
        try:
            mail.send()
        except Exception as error:
                print error
                error_obj= str(error) + ", compose_mail() fn"
                return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})    

        return HttpResponseRedirect(reverse('mailclient', args=(group_id,)))

    return render_to_response(template,variable)

def update_mail_status(request,group_id):
    '''
    takes {
        request : HTTP request
        group_id : gstudio group id
    }
    returns {
        template or error page
    }

    This fucntion moves the mail-file stored on server from new folder
    to cur folder after the user has read the mail
    '''
    group_name, group_id = get_group_name_id(group_id)
    template = "ndf/mailstatuschange.html"
    if request.method=='POST' and request.is_ajax():
        variable = RequestContext(request, {
        'groupname': group_name,
        "group_id" : group_id,
        "groupid" : group_id,
        'mailboxname': request.POST['mailBoxName'],
        'username' : request.POST['username'],
        'mail_type' : request.POST['mail_type'],
        'filename' : request.POST['file_name']
        })
        return render_to_response(template,variable)

# The mailBox-name must not be repeated for an individual user but other users can share the same mailBox-name
def unique_mailbox_name(request,group_id):
    '''
    takes {
        request : HTTP request
        group_id : gstudio group id
    }
    returns {
        template or error page
    }
    To check whether the mailbox name is unique for a user.
    Different users can still have two separate mailboxes with same names.
    '''
    
    group_name, group_id = get_group_name_id(group_id)
    template = "ndf/mail_condition_check.html"
    if request.method == 'POST' and request.is_ajax():

        success = True

        mail_box_name = request.POST['name_data']
        user_id = str(request.user.id)

        settings_dir1 = os.path.dirname(__file__)
        settings_dir2 = os.path.dirname(settings_dir1)
        settings_dir3 = os.path.dirname(settings_dir2)
        path = os.path.abspath(os.path.dirname(settings_dir3))
                
        try:
            conn = sqlite3.connect(path + '/example-sqlite3.db')
            query = 'select mailbox_id from user_mailboxes where user_id=\''+user_id+'\''
            cursor = conn.execute(query)
        except Exception as error:
            print error
            error_obj= str(error) + ", unique_mailbox_name fn"
            return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})

        mailbox_ids=[]
        for row in cursor:
            mailbox_ids.append(row[0])


        try:
            query = 'select id from django_mailbox_mailbox where name=\''+mail_box_name+'\''
            cursor = conn.execute(query)
        except Exception as error:
            print error
            error_obj= str(error) + ", unique_mailbox_name fn"
            return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})

        mailbox_ids_existing=[]
        for row in cursor:
            mailbox_ids_existing.append(row[0])

        for _id in mailbox_ids_existing:
            if _id in mailbox_ids:
                success = False
                break

        message = ''
        if not success:
            message = 'You already have a mailbox with this name!'
        variable = RequestContext(request, {
                'groupname': group_name,
                "group_id" : group_id,
                "groupid" : group_id,
                'display_message': message,
                'csrf_token' : request.POST['csrfmiddlewaretoken'],
                'success' : success,
        })
        return render_to_response(template,variable)

# The ID is unique to the individual user hence must not be repeated in the mailBox-data
def unique_mailbox_id(request,group_id):
    '''
    takes {
        request : HTTP request
        group_id : gstudio group id
    }
    returns {
        template or error page
    }
    The Email-ID has to be unique. No other user can use the ID that is already in use.
    '''
    group_name, group_id = get_group_name_id(group_id)
    template = "ndf/mail_condition_check.html"
    if request.method == 'POST' and request.is_ajax():

        success = True

        email_id_data = request.POST['email_data']
        user_id = str(request.user.id)

        settings_dir1 = os.path.dirname(__file__)
        settings_dir2 = os.path.dirname(settings_dir1)
        settings_dir3 = os.path.dirname(settings_dir2)
        path = os.path.abspath(os.path.dirname(settings_dir3))
                
        try:
            conn = sqlite3.connect(path + '/example-sqlite3.db')
            query = 'select mailbox_id from user_mailboxes where user_id=\''+user_id+'\''
            cursor = conn.execute(query)
        except Exception as error:
            print error
            error_obj= str(error) + ", unique_mailbox_id fn"
            return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})

        mailbox_ids=[]
        for row in cursor:
            mailbox_ids.append(row[0])


        try:
            query = 'select uri from django_mailbox_mailbox'
            cursor = conn.execute(query)
        except Exception as error:
            print error
            error_obj= str(error) + ", unique_mailbox_name fn"
            return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})

        all_email_id=[]
        for row in cursor:
            a = row[0].split('//')[1].split(":")[0].replace('%40','@')
            all_email_id.append(a)

        if email_id_data in all_email_id:
            success = False

        message = ''
        if not success:
            message = 'This Email-ID already in use'

        variable = RequestContext(request, {
                'groupname': group_name,
                "group_id" : group_id,
                "groupid" : group_id,
                'display_message': message,
                'csrf_token' : request.POST['csrfmiddlewaretoken'],
                'success' : success,
        })
        return render_to_response(template,variable)
