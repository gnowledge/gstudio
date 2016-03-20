from registration.signals import user_registered, user_activated
from django.dispatch import receiver
from gnowsys_ndf.ndf.models import *

@receiver(user_registered)
def user_registered_handler(sender, user, request, **kwargs):
    '''
    user_registered signal is received when a user registers on the platform.
    Creates node as:
    {'details_to_hold': {'node_type': 'Author', 'agency_type': 'Other',
     'userid': --, 'group_affiliation': ''}, '_type': u'node_holder',
     '_id': ObjectId('--')}

    '''
    # print "\n\n coming here----"
    tmp_hold = node_collection.collection.node_holder()
    dict_to_hold = {}
    dict_to_hold['node_type'] = 'Author'
    dict_to_hold['userid'] = user.id
    agency_type = request.POST.get("agency_type", "")
    if agency_type:
        dict_to_hold['agency_type'] = agency_type
    else:
        # Set default value for agency_type as "Other"
        dict_to_hold['agency_type'] = "Other"
    dict_to_hold['group_affiliation'] = request.POST.get("group_affiliation", "")
    tmp_hold.details_to_hold = dict_to_hold
    tmp_hold.save()
    # print "====",tmp_hold
    return

# FRAME CLASS DEFINITIONS
@receiver(user_activated)
def create_auth_grp(sender, user, request, **kwargs):
    '''
    user_activated signal is received when the registered user activates his/her account
    using email confirmation/verification link sent.
    '''
    # print "\n\n\n user", user.__dict__
    user_id = user.id
    auth = node_collection.one({'_type': u"Author", 'created_by': int(user_id)})
    # print "\n\n coming here user_activated----"

    # This will create user document in Author collection to behave user as a group.
    if auth is None:
        auth_gst = node_collection.one({'_type': u'GSystemType', 'name': u'Author'})
        auth = node_collection.collection.Author()
        # print "\n Creating new Author"
        auth.name = unicode(user.username)
        auth.email = unicode(user.email)
        auth.password = u""
        auth.member_of.append(auth_gst._id)
        auth.group_type = u"PUBLIC"
        auth.edit_policy = u"NON_EDITABLE"
        auth.subscription_policy = u"OPEN"
        auth.created_by = user_id
        auth.modified_by = user_id
        auth.contributors.append(user_id)
        auth.group_admin.append(user_id)
        auth.preferred_languages = {'primary': ('en', 'English')}

        # Get group_type and group_affiliation stored in node_holder for this author 
        try:
            temp_details = node_collection.one({'$and':[{'_type':'node_holder'},{'details_to_hold.node_type':'Author'},{'details_to_hold.userid':user_id}]})
            if temp_details:
                auth.agency_type = temp_details.details_to_hold['agency_type']
                auth.group_affiliation = temp_details.details_to_hold['group_affiliation']
        except e as Exception:
            print "Error in getting node_holder details for author " + str(e)
        auth_id = ObjectId()
        auth._id = auth_id
        auth.save(groupid=auth._id) 
        # print "\n\n auth===", auth

        # as on when user gets register on platform make user member of two groups:
        # 1: his/her own username group. 2: "home" group
        # adding user's id into author_set of "home" group.
        home_group_obj = node_collection.one({'_type': u"Group", 'name': unicode("home")})
        # being user is log-in for first time on site after registration,
        # directly add user's id into author_set of home group without anymore checking overhead.
        if user_id not in home_group_obj.author_set:
            # print "\n\n adding in home_group_obj"
            node_collection.collection.update({'_id': home_group_obj._id}, {'$push': {'author_set': user_id }}, upsert=False, multi=False)
            home_group_obj.reload()

        desk_group_obj = node_collection.one({'_type': u"Group", 'name': unicode("desk")})
        if desk_group_obj and user_id not in desk_group_obj.author_set:
            # print "\n\n adding in desk_group_obj"
            node_collection.collection.update({'_id': desk_group_obj._id}, {'$push': {'author_set': user_id }}, upsert=False, multi=False)
            desk_group_obj.reload()


