''' -- imports from installed packages -- '''
import json

from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template import Context
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

######################

from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import simplejson
from online_status.status import CACHE_USERS
from online_status.utils import encode_json
from gnowsys_ndf.ndf.models import Group




from django_mongokit import get_database
from gnowsys_ndf.ndf.views.methods import get_forum_repl_type,forum_notification_status
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import GSystemType, GSystem,Node
from gnowsys_ndf.ndf.views.notify import set_notif_val
import datetime
from gnowsys_ndf.ndf.org2any import org2html
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
import unicodedata

db = get_database()
col_Group = db[Group.collection_name]
sitename=Site.objects.all()[0]

##################
collection = get_database()[Node.collection_name]
##################

def output(request, group_id, meetingid):                                                               #ramkarnani
	newmeetingid = meetingid
	ins_objectid  = ObjectId()
        if ins_objectid.is_valid(group_id) is False:
            group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if group_ins:
                group_id = str(group_ins._id)
            else :
                auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
                if auth :
                    group_id = str(auth._id)
        else:
            group_ins = collection.Node.find_one({'_type': "Group","_id": ObjectId(group_id)})
            pass
            #template = "https://chatb/#"+meetingid
	
	return render_to_response("ndf/newmeeting.html",{'group_id': group_id,'groupid':group_id,'newmeetingid':newmeetingid},context_instance=RequestContext(request))



def dashb(request, group_id):                                                                           #ramkarnani
    """Renders a list of all 'Page-type-GSystems' available within the database.
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False:
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else:
        group_ins = collection.Node.find_one({'_type': "Group","_id": ObjectId(group_id)})
        pass
    online_users = cache.get(CACHE_USERS)
    online_users = simplejson.dumps(online_users, default=encode_json)	
    #print "\n inside meeting \n"
    # print "\ngroup_id: ", group_id,"\n"
    
    

    return render_to_response("ndf/meeting.html",{'group_id': group_id,'groupid':group_id,'online_users':online_users,'meetingid':ins_objectid},context_instance=RequestContext(request))

#### Ajax would be called here to get refreshed list of online members
def get_online_users(request, group_id):                                                                        #ramkarnani
	"""Json of online users, useful f.ex. for refreshing a online users list via an ajax call or something"""
	online_users = cache.get(CACHE_USERS)
	#print "hey \n"
	#print json.dumps(online_users, default=encode_json), "\n\n"
	#a = json.dumps(online_users, default=encode_json)
	#print type(a)
	return HttpResponse(simplejson.dumps(online_users, default=encode_json))

def invite_meeting(request, group_id, meetingid):                                                                  #ramkarnani
	try:
            # print "here in view"
            colg=col_Group.Group.one({'_id':ObjectId(group_id)})
            groupname=colg.name
            # print "\n\nPOST : ", request
            recipient = request.GET.get("usr","")
            recipient = unicodedata.normalize('NFKD', recipient).encode('ascii','ignore')
            #print type(recipient), recipient
            sender=request.user
            sending_user=User.objects.get(username=sender).id
            #print type (sitename), sitename
            activ="invitation to join in meeting"
            url_of_meeting = "http://" + str(sitename) + "/" + group_id + "/meeting/" + meetingid
            msg="'This is to inform you that " + str(sender) + " has invited you to the meeting of " +str(groupname)+" . Please click here " + url_of_meeting +"'"
            #print "\n\nmsg : ", msg

            ret=""
            
            bx=User.objects.get(username=recipient)
            ret = set_notif_val(request,group_id,msg,activ,bx)
            if bx.id not in colg.author_set:
                colg.author_set.append(bx.id)
                colg.save()
            if ret :
                return HttpResponse("success")

                   # msg_list=msg.split()
                   # newmeetingid=msg[16]

            else:
                return HttpResponse("failure")
	except Exception as e:
            print str(e)
            return HttpResponse(str(e))
