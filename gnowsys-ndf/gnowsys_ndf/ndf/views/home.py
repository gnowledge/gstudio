''' -- imports from python libraries -- '''
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.views.generic import RedirectView

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import GSystemType,Node

#######################################################################################################################################
#                                                                                           V I E W S   D E F I N E D   F O R   H O M E
#######################################################################################################################################


def homepage(request):	

	return render_to_response("ndf/base.html",context_instance=RequestContext(request))



# This class overrides the django's default RedirectView class and allows us to redirect it into user group after user logsin   
class HomeRedirectView(RedirectView):
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):

    	if self.request.user.is_authenticated():
            collection = get_database()[Node.collection_name]
            auth_obj = collection.GSystemType.one({'_type': u'GSystemType', 'name': u'Author'})
            if auth_obj:
                auth_type = auth_obj._id
            auth = ""
            auth = collection.Group.one({'_type': u"Author", 'name': unicode(self.request.user)})            
            # This will create user document in Author collection to behave user as a group.
            
            if auth is None:
                auth = collection.Author()
                
                auth.name = unicode(self.request.user)      
                auth.password = u""
                auth.member_of.append(auth_type)
                auth.group_type = u"PUBLIC"
                auth.edit_policy = u"NON_EDITABLE"
                auth.subscription_policy = u"OPEN"
                user_id = int(self.request.user.pk)
                auth.created_by = user_id
                auth.modified_by = user_id
                if user_id not in auth.contributors:
                    auth.contributors.append(user_id)
                # Get group_type and group_affiliation stored in node_holder for this author 
                temp_details=collection.Node.one({'$and':[{'_type':'node_holder'},{'details_to_hold.node_type':'Author'},{'details_to_hold.userid':user_id}]})
                if temp_details:
                    auth.agency_type=temp_details.details_to_hold['agency_type']
                    auth.group_affiliation=temp_details.details_to_hold['group_affiliation']
                auth.save()
                
            # This will return a string in url as username and allows us to redirect into user group as soon as user logsin.
            #return "/{0}/".format(auth.pk)
        return "/home/"     
        #else:
            # If user is not loggedin it will redirect to home as our base group.
        #    return "/home/"		

    
