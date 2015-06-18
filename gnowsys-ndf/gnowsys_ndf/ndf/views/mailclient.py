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

    # add exception
    except Exception as error:
        error_obj= str(error) + ", mailclient() fn"
        return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})
        #return HttpResponseRedirect(reverse('mailclient_error_display', args=(group_id,error_obj,)))

    #TODO: Handle the test case which requires the next two lines of code
    if group_id == home_grp_id['_id']:
        return render(request, 'ndf/oops.html')

    return render(request, 'ndf/mailclient.html', {
        'groupname': group_name,
        'groupid': group_id,
        'group_id': group_id,
        'mailboxnames': mailbox_names,
        'mailboxids' : mailbox_ids
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
        mailbox_name= request.POST.get("mailbox_name","")
        user_id = request.POST.get("user_id","")
        mailbox_names = []
        if yes == "YES":
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
                error_obj= str(error) + ", mailbox_delete() fn"
                return render(request, 'ndf/mailclient_error.html', {'error_obj': error_obj,'groupid': group_id,'group_id': group_id})    

            mailbox_ids=[]
            for row in cursor:
                mailbox_ids.append(row[0])                  
            print mailbox_ids        
            query = 'select name from django_mailbox_mailbox where id='
            for box_id in mailbox_ids:
                box_id = str(box_id)
                query_2 = query + box_id
                cursor = conn.execute(query_2)
                for row in cursor:
                    mailbox_names.append(row[0])
                # edit mailbox with passed mailbox_id 
                box = None
                flag = 0
                boxes= Mailbox.active_mailboxes.all()
                for box in boxes:
                    if box.name == mailbox_name and box.id in mailbox_ids:
                        flag = 1
                        break

                if flag == 1:
                    #delete from out 'mapping' database (the database which tracks which user_id is asscociated with which mailbox_id )                    

                    # conn2 = sqlite3.connect(path + '/example-sqlite3.db')
                    query = 'delete from user_mailboxes where mailbox_id='+str(box.id)
                    cursor = conn.execute(query)
                    conn.commit()
                    #NOTE: we must delete the mailbox from our 'mapping' database first and then from django_mailbox database because 
                    # when you call the delete function of django_mailbox API on a mailbox object, the mailbox id is lost!
                    # And we need that id value to delete from our 'mapping' database. Hence order is important

                    #delete mailbox from django_mailbox's database
                    box.delete()
                    
                    # get it from the user
                    want_archive=None
                    if want_archive:
                        # change the mailbox folder from its existing location to the archives data folder
                        print 'PENDING!'
                    else:
                        # directly delete the folder from the system
                        print 'PENDING!'

                    print "%s Deleted from django_mailbox" % mailbox_name
                else:
                    print "Box not found > (fn: delete_mailbox)"
            conn.close()
            # conn2.close()
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
    return render_to_response(template,variable)