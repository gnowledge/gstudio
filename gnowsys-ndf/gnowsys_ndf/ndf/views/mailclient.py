# from django.views.generic import TemplateView
from django.shortcuts import render
# from gnowsys_ndf.settings import META_TYPE, GAPPS, GSTUDIO_SITE_DEFAULT_LANGUAGE, GSTUDIO_SITE_NAME
# from gnowsys_ndf.settings import GSTUDIO_RESOURCES_CREATION_RATING,
# GSTUDIO_RESOURCES_REGISTRATION_RATING, GSTUDIO_RESOURCES_REPLY_RATING

from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.models import node_collection, triple_collection, gridfs_collection
# from gnowsys_ndf.ndf.models import *
from django.contrib.auth.models import User

from gnowsys_ndf.ndf.views.methods import get_drawers, get_execution_time
# from gnowsys_ndf.ndf.views.methods import create_grelation, create_gattribute
from gnowsys_ndf.ndf.views.methods import get_user_group, get_user_task, get_user_notification, get_user_activity, get_execution_time

from gnowsys_ndf.ndf.views.file import *
# from gnowsys_ndf.ndf.views.forum import *
from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget
# from gnowsys_ndf.notification import models as notification
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_all_user_groups

#---------Django Mailbox imports----------------#
from django_mailbox.models import Mailbox
import socket
from imaplib import IMAP4
import sqlite3
import os
import re
import shutil
from django.core.mail import EmailMessage
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
    group_name, group_id = get_group_name_id(group_id)
    home_grp_id = node_collection.one({'name': "home"})

    mailbox_names = []
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

def render_mailbox_pane(request,group_id):
    group_name, group_id = get_group_name_id(group_id)
    template = "ndf/mailcontent.html"
    if request.method=='POST' and request.is_ajax():
        variable = RequestContext(request, {
        'groupname': group_name,
        "group_id" : group_id,
        "groupid" : group_id,
        'mailboxname': request.POST['mailBoxName'],
        'username' : request.POST['username'],
        'mail_type' : request.POST['mail_type'],
        'displayFrom' : request.POST['startFrom']
        })
        return render_to_response(template,variable)


@login_required
@get_execution_time
def mailbox_edit(request, group_id,mailboxname):
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
            pass
            #mail.send()
        except Exception as error:
                print error
                error_obj= str(error) + ", compose_mail() fn"
                return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})    

        return HttpResponseRedirect(reverse('mailclient', args=(group_id,)))

    return render_to_response(template,variable)

def update_mail_status(request,group_id):
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