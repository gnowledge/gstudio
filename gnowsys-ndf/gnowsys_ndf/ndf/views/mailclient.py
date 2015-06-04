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

from django_mailbox.models import Mailbox

@login_required
def mailclient(request, group_id):
    group_name, group_id = get_group_name_id(group_id)
    home_grp_id = node_collection.one({'name': "home"})

    boxes = Mailbox.objects.all()

    mailbox_names = []
    for box in boxes:
        mailbox_names.append(box.name)

    if group_id == home_grp_id['_id']:
        return render(request, 'ndf/oops.html')

    return render(request, 'ndf/mailclient.html', {
        'groupname': group_name,
        'groupid': group_id,
        'mailboxnames': mailbox_names
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
        emailid_split = emailid.split('@')
        domain = emailid_split.split('.')
 
        # make a mailbox from the above details
        newbox = Mailbox()
        newbox.name = mailbox_name
 
        # TODO: find the webserver address using user's choice as selected from
        # a drop down box
        webserver = server_dict["gmail"]
        uri = ""
        uri = "imap+ssl://" + emailid_split[0] + "%40" + emailid_split[1] +  ":" + pwd + "@" + webserver
        newbox.uri = uri
        try:
            newbox.get_connection()
            newbox.save()
        except socket.gaierror:
            print "CONNECTION ERROR, COULDNT CONFIGURE MAILBOX WEBSERVER"
        print mailbox_name
        print emailid
        print pwd
        print uri
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
        'mailboxname': request.POST['mailBoxName']
        })
        return render_to_response(template,variable)

