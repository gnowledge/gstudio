''' -- imports from python libraries -- '''
# import os -- Keep such imports here

''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.generic import RedirectView
from gnowsys_ndf.ndf.views.methods import get_execution_time
from gnowsys_ndf.ndf.views.analytics import *

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, GSTUDIO_SITE_LANDING_PAGE, GSTUDIO_SITE_NAME, GSTUDIO_SITE_LANDING_TEMPLATE
from gnowsys_ndf.ndf.models import GSystemType, Node
from gnowsys_ndf.ndf.models import node_collection

###################################################
#   V I E W S   D E F I N E D   F O R   H O M E   #
###################################################

@get_execution_time
def homepage(request, group_id):
    
    if request.user.is_authenticated():
        # auth_gst = node_collection.one({'_type': u'GSystemType', 'name': u'Author'})
        # if auth_obj:
        #     auth_type = auth_obj._id
        auth = node_collection.one({'_type': u"Author", 'created_by': int(request.user.id)})

        # This will create user document in Author collection to behave user as a group.
        '''
        The code below is commented whose purpose was to create Author
        group on first-time login.
        This functionality is implemented by using django-registration
        signal 'user_activated'. (See 'def create_auth_grp' in signals.py)
        
        if auth is None:
            auth = node_collection.collection.Author()
            auth.name = unicode(request.user)
            auth.email = unicode(request.user.email)
            auth.password = u""
            # auth.member_of.append(auth_type)
            auth.member_of.append(auth_gst._id)
            auth.group_type = u"PUBLIC"
            auth.edit_policy = u"NON_EDITABLE"
            auth.subscription_policy = u"OPEN"
            user_id = int(request.user.pk)
            auth.created_by = user_id
            auth.modified_by = user_id
            if user_id not in auth.contributors:
                auth.contributors.append(user_id)
            # Get group_type and group_affiliation stored in node_holder for this author 
            try:
                temp_details = node_collection.one({'$and':[{'_type':'node_holder'},{'details_to_hold.node_type':'Author'},{'details_to_hold.userid':user_id}]})
                if temp_details:
                    auth.agency_type = temp_details.details_to_hold['agency_type']
                    auth.group_affiliation = temp_details.details_to_hold['group_affiliation']
            except e as Exception:
                print "error in getting node_holder details for an author"+str(e)
            auth.save(groupid=group_id)

            # as on when user gets register on platform make user member of two groups:
            # 1: his/her own username group. 2: "home" group
            # adding user's id into author_set of "home" group.
            home_group_obj = node_collection.one({'_type': u"Group", 'name': unicode("home")})
            # being user is log-in for first time on site after registration,
            # directly add user's id into author_set of home group without anymore checking overhead.
            home_group_obj.author_set.append(request.user.id)
            home_group_obj.save(groupid=group_id)
        '''

        if GSTUDIO_SITE_LANDING_PAGE == "home":
            return HttpResponseRedirect( reverse('landing_page') )

        else:
            return HttpResponseRedirect( reverse('dashboard', kwargs={"group_id": request.user.id}) )

    else:
        if GSTUDIO_SITE_LANDING_PAGE == "home":
            return HttpResponseRedirect( reverse('landing_page') )

        else:
            return HttpResponseRedirect( reverse('groupchange', kwargs={"group_id": group_id}) )

@get_execution_time
def landing_page(request):
    '''
    Method to render landing page after checking variables in local_settings/settings file.
    '''
    if (GSTUDIO_SITE_LANDING_PAGE == "home") and (GSTUDIO_SITE_NAME == "NROER"):
        return render_to_response(
                                "ndf/landing_page_nroer.html",
                                {
                                    "group_id": "home", 'groupid':"home",
                                    'landing_page': 'landing_page'
                                },
                                context_instance=RequestContext(request)
                            )

    elif GSTUDIO_SITE_LANDING_TEMPLATE:
        if GSTUDIO_SITE_NAME == "clix":
            if request.META['QUERY_STRING']  == "True":
                return render_to_response(
                                        GSTUDIO_SITE_LANDING_TEMPLATE,
                                        {
                                            "group_id": "home", 'groupid':"home",
                                            'title': 'CLIx'
                                        },
                                        context_instance=RequestContext(request)
                                    )
            elif request.user.id:
                return HttpResponseRedirect( reverse('my_desk', kwargs={"group_id": request.user.id}) )        
            else:
        
                return render_to_response(
                                        GSTUDIO_SITE_LANDING_TEMPLATE,
                                        {
                                            "group_id": "home", 'groupid':"home",
                                            'title': 'CLIx'
                                        },
                                        context_instance=RequestContext(request)
                                    )
    else:
        return HttpResponseRedirect( reverse('groupchange', kwargs={"group_id": "home"}) )


# This class overrides the django's default RedirectView class and allows us to redirect it into user group after user logsin   
# class HomeRedirectView(RedirectView):
#     pattern_name = 'home'

#     def get_redirect_url(self, *args, **kwargs):
#       if self.request.user.is_authenticated():
#             auth_obj = node_collection.one({'_type': u'GSystemType', 'name': u'Author'})
#             if auth_obj:
#                 auth_type = auth_obj._id
#             auth = ""
#             auth = node_collection.one({'_type': u"Author", 'name': unicode(self.request.user)})
#             # This will create user document in Author collection to behave user as a group.

#             if auth is None:
#                 auth = node_collection.collection.Author()

#                 auth.name = unicode(self.request.user)
#                 auth.email = unicode(self.request.user.email)
#                 auth.password = u""
#                 auth.member_of.append(auth_type)
#                 auth.group_type = u"PUBLIC"
#                 auth.edit_policy = u"NON_EDITABLE"
#                 auth.subscription_policy = u"OPEN"
#                 user_id = int(self.request.user.pk)
#                 auth.created_by = user_id
#                 auth.modified_by = user_id
#                 if user_id not in auth.contributors:
#                     auth.contributors.append(user_id)
#                 # Get group_type and group_affiliation stored in node_holder for this author 
#                 try:
#                     temp_details = node_collection.one({'_type': 'node_holder', 'details_to_hold.node_type': 'Author', 'details_to_hold.userid': user_id})
#                     if temp_details:
#                         auth.agency_type=temp_details.details_to_hold['agency_type']
#                         auth.group_affiliation=temp_details.details_to_hold['group_affiliation']
#                 except e as Exception:
#                     print "error in getting node_holder details for an author"+str(e)
#                 auth.save()
                
#             # This will return a string in url as username and allows us to redirect into user group as soon as user logsin.
#             #return "/{0}/".format(auth.pk)
#             if GSTUDIO_SITE_LANDING_PAGE == 'home':
#                 #return "/home/dashboard/group"
#                 return "/home/"
#             else:    
#                 return "/{0}/dashboard".format(self.request.user.id)     
#         else:
#             # If user is not loggedin it will redirect to home as our base group.
#             #return "/home/dashboard/group"
#             return "/home/"

@get_execution_time
def help_page_view(request,page_name):
    # page_obj = Node.get_node_by_id(page_id)
    help_grp = node_collection.one({'$and':[{'_type': u'Group'}, {'name': u'help'}]})
    
    page_obj = node_collection.one({"name":unicode(page_name),"group_set":ObjectId(help_grp._id)})
    return render_to_response(
                                        "ndf/help_page.html",
                                        {
                                            "group_id": page_obj._id,
                                            'title': 'Help Page',
                                            'page_obj':page_obj
                                        },
                                        context_instance=RequestContext(request)
                                    )
