# from django.views.generic import TemplateView
from django.shortcuts import render
import sqlite3
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

from django_mailbox.models import Mailbox
import socket

@login_required
def mailclient(request, group_id):
    group_name, group_id = get_group_name_id(group_id)
    home_grp_id = node_collection.one({'name': "home"})

    mailbox_names = []
    try:
        conn = sqlite3.connect('/home/akazuko/Developer/metastudio/gstudio/gnowsys-ndf/example-sqlite3.db')
        user_id = str(request.user.id)  
        query = 'select mailbox_id from user_mailboxes where user_id=\''+user_id+'\''
        cursor = conn.execute(query)

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

    # add exception
    except socket.gaierror:
        print "CONNECTION ERROR, COULDNT CONFIGURE MAILBOX WEBSERVER"

    # boxes = Mailbox.objects.all()

    # for box in boxes:
    #     mailbox_names.append(box.name)

    if group_id == home_grp_id['_id']:
        return render(request, 'ndf/oops.html')

    return render(request, 'ndf/mailclient.html', {
        'groupname': group_name,
        'groupid': group_id,
        'mailboxnames': mailbox_names,
        'mailboxids' : mailbox_ids
    })
 
#-----------------Dictionary of popular servers--------------#
server_dict = {
    "Gmail": "imap.gmail.com",
    "Yahoo Mail": "imap.mail.yahoo.com",
    "Yahoo Mail Plus": "plus.imap.mail.yahoo.com",
    "AT&T": "imap.ntlworld.com",
    "Office365": "outlook.office365.com",
    "Outlook": "imap-mail.outlook.com",
    "AOL": "imap.aol.com",
    "Mail": "imap.mail.com",
    "Verizon": "incoming.verizon.net",
    "Bits Pilani": "imap.gmail.com",
    "Rediffmail": "pop.rediffmail.com"
}

@login_required
@get_execution_time
def mailbox_create_edit(request, group_id):
    print "in second fn"
    group_name, group_id = get_group_name_id(group_id)
    home_grp_id = node_collection.one({'name': "home"})
 
    if group_id == home_grp_id['_id']:
        return render(request, 'ndf/oops.html')
    template = "ndf/mailbox_create_edit.html"
    if request.method == "POST":  # create or edit
        # get all data from the form
        mailbox_name = request.POST.get("mailboxname", "")
        emailid = request.POST.get("emailid", "")
        pwd = request.POST.get("password", "")
        domain = request.POST.get("domain", "")
        emailid_split= emailid.split('@')
 
        # make a mailbox from the above details
        newbox = Mailbox()
        newbox.name = mailbox_name
 
        # TODO: find the webserver address using user's choice as selected from
        # a drop down box
        webserver = server_dict[domain]
        uri = "imap+ssl://" + emailid_split[0] + "%40" + emailid_split[1] +  ":" + pwd + "@" + webserver + '?archive=' + mailbox_name
        newbox.uri = uri
        try:
            newbox.get_connection()
            newbox.save()
            conn = sqlite3.connect('/home/akazuko/Developer/metastudio/gstudio/gnowsys-ndf/example-sqlite3.db')
            user_id = str(request.user.id)
            query = 'insert into user_mailboxes values (?,?);'
            cursor = conn.execute(query, (request.user.id, newbox.id))
            conn.commit()
            conn.close()

        except socket.gaierror:
            print "CONNECTION ERROR, COULDNT CONFIGURE MAILBOX WEBSERVER"
        return HttpResponseRedirect(reverse('mailclient', args=(group_id,)))
 
    else:
        title = "Add A New Mailbox"
        variable = RequestContext(request, {'title': title,
                                            'groupname': group_name,
                                            'groupid': group_id,
                                            'server_dict' : server_dict
                                            })
        return render_to_response(template, variable)

def render_mailbox_pane(request,group_id):
    group_name, group_id = get_group_name_id(group_id)
    template = "ndf/mailcontent.html"

    if request.method=='POST' and request.is_ajax():
        variable = RequestContext(request, {
        'groupname': group_name,
        'groupid': group_id,
        'mailboxname': request.POST['mailBoxName'],
        'username' : request.POST['username']
        })
        return render_to_response(template,variable)