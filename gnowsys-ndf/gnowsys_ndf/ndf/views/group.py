''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
# from django.template.defaultfilters import slugify
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import View

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, GSTUDIO_GROUP_AGENCY_TYPES, GSTUDIO_NROER_MENU, GSTUDIO_NROER_MENU_MAPPINGS

# from gnowsys_ndf.ndf.models import GSystemType, GSystem, Group, Triple
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_all_user_groups  # get_existing_groups
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.ndf.org2any import org2html

# ######################################################################################################################################

gst_group = node_collection.one({"_type": "GSystemType", 'name': u"Group"})
app = gst_group

# ######################################################################################################################################
#      V I E W S   D E F I N E D   F O R   G A P P -- ' G R O U P '
# ######################################################################################################################################

class CreateGroup(object):
    """
    Creates group.
    Instantiate group with request as argument
    """
    def __init__(self, request):
        super(CreateGroup, self).__init__()
        self.request = request


    def is_group_exists(self, arg_group_name):
        '''
        checks if group with the given name exists.
        Returns True: If group exists.
        '''
        name = arg_group_name
        group = node_collection.find_one({
                    '_type': 'Group',
                    'name': unicode(name)
                })
        if group:
            return True
        else:
            return False


    def get_group_fields(self, group_name, **kwargs):
        '''
        function to fill the empty group object with values supplied.
        group information may be sent either from "request" or from "kwargs".

        # If arg is kwargs, provide following dict as kwargs arg to this function.
        group_fields = {
          'altnames': '', 'group_type': '', 'edit_policy': '',
          'agency_type': '', 'moderation_level': ''
        }
        # call in following way
        class_instance_var.get_group_fields(group_name, **group_fields)
        '''

        # getting the data into variables
        name = group_name

        if kwargs.get('altnames', ''):
            altnames = kwargs.get('altnames', name) 
        else:
            altnames = self.request.POST.get('altnames', "").strip()

        if kwargs.get('group_type', ''):
            group_type = kwargs.get('group_type', '') 
        else:
            group_type = self.request.POST.get('group_type', '')

        if kwargs.get('access_policy', ''):
            access_policy = kwargs.get('access_policy', group_type) 
        else:
            access_policy = self.request.POST.get('access_policy', group_type)

        if kwargs.get('edit_policy', ''):
            edit_policy = kwargs.get('edit_policy', '') 
        else:
            edit_policy = self.request.POST.get('edit_policy', '')

        if kwargs.get('subscription_policy', ''):
            subscription_policy = kwargs.get('subscription_policy', 'OPEN') 
        else:
            subscription_policy = self.request.POST.get('subscription_policy', "OPEN")

        if kwargs.get('visibility_policy', ''):
            visibility_policy = kwargs.get('visibility_policy', 'ANNOUNCED') 
        else:
            visibility_policy = self.request.POST.get('visibility_policy', 'ANNOUNCED')

        if kwargs.get('disclosure_policy', ''):
            disclosure_policy = kwargs.get('disclosure_policy', 'DISCLOSED_TO_MEM') 
        else:
            disclosure_policy = self.request.POST.get('disclosure_policy', 'DISCLOSED_TO_MEM')

        if kwargs.get('encryption_policy', ''):
            encryption_policy = kwargs.get('encryption_policy', 'NOT_ENCRYPTED') 
        else:
            encryption_policy = self.request.POST.get('encryption_policy', 'NOT_ENCRYPTED')

        if kwargs.get('agency_type', ''):
            agency_type = kwargs.get('agency_type', 'Other') 
        else:
            agency_type = self.request.POST.get('agency_type', 'Other')

        if kwargs.get('content_org', ''):
            content_org = kwargs.get('content_org', '') 
        else:
            content_org = self.request.POST.get('content_org', '')

        # whenever we are passing int: 0, condition gets false
        # therefor casting to str
        if str(kwargs.get('moderation_level', '')):
            moderation_level = kwargs.get('moderation_level', '-1') 
        else:
            moderation_level = self.request.POST.get('moderation_level', '-1')

        # instantiated empty group object
        group_obj = node_collection.collection.Group()

        # filling the values with variables in empty group object
        group_obj.name = unicode(name)
        group_obj.altnames = unicode(altnames)
        group_obj.member_of.append(gst_group._id)
        group_obj.type_of.append(gst_group._id)
      
        user_id = int(self.request.user.id)
        group_obj.created_by = user_id
        group_obj.modified_by = user_id
        if user_id not in group_obj.author_set:
            group_obj.author_set.append(user_id)
        if user_id not in group_obj.contributors:
            group_obj.contributors.append(user_id)
        if user_id not in group_obj.group_admin:
            group_obj.group_admin.append(user_id)

        group_obj.group_type = group_type
        group_obj.access_policy = access_policy
        group_obj.edit_policy = edit_policy
        group_obj.subscription_policy = subscription_policy
        group_obj.visibility_policy = visibility_policy
        group_obj.disclosure_policy = disclosure_policy
        group_obj.encryption_policy = encryption_policy
        group_obj.agency_type = agency_type

        #  org-content
        if content_org:
            if group_obj.content_org != content_org:
                group_obj.content_org = content_org

                # Required to link temporary files with the current user who is
                # modifying this document
                usrname = self.request.user.username
                filename = slugify(name) + "-" + slugify(usrname) + "-" + ObjectId().__str__()
                group_obj.content = org2html(content_org, file_prefix=filename)
                is_changed = True

        # decision for adding moderation_level
        if group_obj.edit_policy == "EDITABLE_MODERATED":
            group_obj.moderation_level = int(moderation_level)
        else:
            group_obj.moderation_level = -1

        group_obj.status = u"PUBLISHED"

        # returning basic fields filled group object 
        return group_obj

    # --- END --- get_group_fields() ------


    def create_group(self, group_name, **kwargs):
        '''
        Creates group with given args.
        Returns tuple containing True/False, sub_group_object/error.
        '''

        # checking if group exists with same name
        if not self.is_group_exists(group_name):

            group_obj = self.get_group_fields(group_name, **kwargs)

            try:
                group_obj.save()
            except Exception, e:
                return False, e

            # group created successfully
            return True, group_obj

        else:
            return False, 'Group with same name exists.'

    # --- END --- create_group() ------


    def get_group_edit_policy(self, group_id):
        '''
        Returns "edit_policy" of the group.
        '''
        group_obj = node_collection.one({'_id': ObjectId(group_id)})
        if group_obj:
            return group_obj.edit_policy
        else:
          return False
    # --- END --- get_group_edit_policy() ------

    def get_group_type(self, group_id):
        '''
        Returns "group_type" of the group.
        '''
        group_obj = node_collection.one({'_id': ObjectId(group_id)})
        if group_obj:
            return group_obj.group_type
        else:
          return False
    # --- END --- get_group_type() ------

    def get_all_subgroups_obj_list(self, group_id):
        '''
        Returns mongokit (find) cursor of sub-group documents.
        '''
        group_obj = node_collection.one({'_id': ObjectId(group_id)})

        # check if group has post_node. Means it has sub-group/s
        if group_obj and group_obj.post_node:
            return node_collection.find({'_id': {'$in': group_obj.post_node} })
        else:
          return False
    # --- END --- get_all_subgroups_obj_list() ------

    def get_all_subgroups_member_of_list(self, group_id):
        '''
        Returns list of names of "member_of" of sub-groups.
        '''
        sg_member_of_list = []
        all_sg = self.get_all_subgroups_obj_list(group_id)

        if all_sg:
            # getting parent's sub group's member_of in a list
            for each_sg in all_sg:
                sg_member_of_list += each_sg.member_of_names_list

        return sg_member_of_list
    # --- END --- get_all_subgroups_member_of_list() ------

# --- END of class CreateGroup ---
# --------------------------------


class CreateSubGroup(CreateGroup):
    """
        Create sub-group of any type
        (e.g: Moderated, Normal, programe_event, course_event)
        Instantiate group with request as argument
    """
    def __init__(self, request):
        super(CreateSubGroup, self).__init__(request)
        self.request = request

    
    def get_subgroup_fields(self, parent_group_id, sub_group_name, sg_member_of, **kwargs):
        '''
        Get empty group object filled with values supplied in arguments.
        "parent_group_id" and "sub_group_id" and "sg_member_of" are compulsory args.
        '''

        # get basic fields filled group object
        group_obj = self.get_group_fields(sub_group_name, **kwargs)

        if sg_member_of in ['ProgramEventGroup', 'CourseEventGroup', 'PartnerGroup', 'ModeratingGroup']:
            
            # overriding member_of field of subgroup
            member_of_group = node_collection.one({'_type': u'GSystemType', 'name': unicode(sg_member_of)})
            group_obj.member_of = [ObjectId(member_of_group._id)]

            # for subgroup's of this types, group_type must be PRIVATE and EDITABLE_MODERATED
            group_obj.group_type = 'PRIVATE'
            group_obj.access_policy = u'PRIVATE'
            group_obj.edit_policy = 'EDITABLE_MODERATED'

        else:  # for normal sub-groups
            if not group_obj.group_type:
                group_obj.group_type = self.get_group_type(parent_group_id)

            if not group_obj.edit_policy:
                group_obj.edit_policy = self.get_group_edit_policy(parent_group_id)

        # check if group object's prior_node has _id of parent group, otherwise add one.
        if ObjectId(parent_group_id) not in group_obj.prior_node:
            group_obj.prior_node.append(ObjectId(parent_group_id))

        return group_obj


    def create_subgroup(self, parent_group_id, sub_group_name, sg_member_of, **kwargs):
        '''
        Creates sub-group with given args.
        Returns tuple containing True/False, sub_group_object/error.
        '''
        # print "kwargs : ", kwargs

        try:
            parent_group_id = ObjectId(parent_group_id)

        except:
            parent_group_name, parent_group_id = get_group_name_id(group_id)
        # except:  # it's parent group's name (str). so dereference to get "_id"
        #     parent_group_obj = node_collection.one({"_type": {"$in": ["Group", "Author"] }, "name": unicode(parent_group_id)})
        #     # checking if group_obj is valid
        #     if parent_group_obj:
        #         parent_group_id = parent_group_obj._id

        # checking feasible conditions to add this sub-group
        if not self.check_subgroup_feasibility(parent_group_id, sg_member_of):
            return False, "It's not feasible to make sub-group with given values"

        if not self.is_group_exists(sub_group_name):

            # getting sub-group object filled with basic fields of (group + subgroup) levels
            group_obj = self.get_subgroup_fields(parent_group_id, sub_group_name, sg_member_of, **kwargs)

            try:
                group_obj.save()
            except Exception, e:
                # if any errors return tuple with False and error
                return False, e

            # after sub-group get created/saved successfully:
            self.add_subgroup_to_parents_postnode(parent_group_id, group_obj._id, sg_member_of)

            return True, group_obj
        
        else:
            return False, 'Group with same name exists.'


    def check_subgroup_feasibility(self, parent_group_id, sg_member_of):
        '''
        method to check feasibility of adding sub group to parent group 
        according to their following properties:
        - parent group's edit_policy
        - child group's member_of
        Returns True if it is OK to create sub-group with suplied fields.
        '''
        if sg_member_of == 'Group':
            return True

        elif sg_member_of in ['ProgramEventGroup', 'CourseEventGroup', 'PartnerGroup', 'ModeratingGroup']:
            if self.get_group_edit_policy(parent_group_id) == 'EDITABLE_MODERATED':
                
                # if current sub-groups member_of is in parent's any one of the sub-group,
                # means sub-group with current property exists in/for parent group.
                # And no sibling with these property can exists together (like normal sub-groups).

                if sg_member_of in self.get_all_subgroups_member_of_list(parent_group_id):
                    return False
                else:
                    return True
            else:
                return False


    def add_subgroup_to_parents_postnode(self, parent_group_id, sub_group_id, sg_member_of):
        '''
        Adding sub-group's _id in post_node of parent_group.
        '''

        # fetching parent group obj
        parent_group_object = node_collection.one({'_id': ObjectId(parent_group_id)})

        # adding sub group's id in post node of parent node
        if ObjectId(sub_group_id) not in parent_group_object.post_node:
            parent_group_object.post_node.append(ObjectId(sub_group_id))

            # adding normal sub-group to collection_set of parent group:
            if sg_member_of == 'Group':
                parent_group_object.collection_set.append(ObjectId(sub_group_id))

            parent_group_object.save()
            return True

        # sub-groups "_id" already exists in parent_group.
        return False


    def get_particular_member_of_subgroup(self, group_id, member_of):
        '''
        Returns sub-group having particular member_of.
        Else return False
        '''
        member_of = node_collection.one({'_type': 'GSystemType', 'name': unicode(member_of)})

        group_obj = node_collection.one({
                                        '_type': 'Group',
                                        'prior_node': {'$in': [ObjectId(group_id)]},
                                        'member_of': member_of._id
                                        })

        if group_obj:
            return group_obj
        else:
            return False

# --- END of class CreateSubGroup ---
# --------------------------------


class CreateModeratedGroup(CreateSubGroup):
    """
        Creates moderated sub-groups.
        Instantiate with request.
    """
    def __init__(self, request):
        super(CreateSubGroup, self).__init__(request)
        self.request = request
        self.edit_policy = 'EDITABLE_MODERATED'
        self.altnames = {
            'ModeratingGroup': [u'Clearing House', u'Curation House'],
            'ProgramEventGroup': [],
            'CourseEventGroup': []
        }

    def create_new_moderated_group(self, group_name, moderation_level=1, **kwargs):
        '''
        Creates top level group with given args.
        Returns tuple containing True/False, sub_group_object/error.
        '''

        if not self.is_group_exists(group_name):
            # values will be taken from POST form fields
            group_obj = self.get_group_fields(group_name)

            try:
                group_obj.save()
            except Exception, e:
                # if any errors return tuple with False and error
                print e
                return False, e

            # self.add_subgroup_to_parents_postnode(parent_group_id, group_obj._id, sg_member_of)
            parent_group_id = group_obj._id
            for each_sg_iter in range(0, int(moderation_level)):
                result = self.add_moderation_level(parent_group_id, 'ModeratingGroup')
                # result is tuple of (bool, newly-created-sub-group-obj)
                if result[0]:
                    parent_group_id = result[1]._id
                else:
                    # if result is False, means sub-group is not created.
                    # In this case, there is no point to go ahead and create subsequent sub-group.
                    break

            return True, group_obj
        
        else:
            return False, 'Group with same name exists.'


    def add_moderation_level(self, parent_group_id, sg_member_of, increment_mod_level=False):
        '''
        Adds the moderation sub group to parent group.
        - expects "_id/name" of parent and sub_group's "member_of".
        - increment_mod_level: If you want to add next moderation subgroup, despite of 
                    moderation_level is 0.
                    In this case, if value is True, 
                    moderation_level of all top hierarchy groups will be updated by 1.
        '''
        parent_group_object = get_group_name_id(parent_group_id, get_obj=True)

        # pg: parent group
        pg_name = parent_group_object.name
        pg_moderation_level = parent_group_object.moderation_level

        sg_name = pg_name + unicode('_mod')

        # no need to check following here, because it's being checked at sub-group creation time.
        # but keep this following code for future perspective.
        # 
        # if self.is_group_exists(sg_name):
        #     # checking for group with name exists
        #     return False, 'Group with name: ' + sg_name + ' exists.'

        # elif not self.check_subgroup_feasibility(sg_member_of):
        #     # checking if any of the sub-group has same member_of field.
        #     return False, 'Sub-Group with type of group' + sg_member_of + ' exists.'

        if (pg_moderation_level == 0) and not increment_mod_level:
            # if parent_group's moderation_level is reached to leaf; means to 0. Then return False

            return False, 'Parent group moderation level is: ' + pg_moderation_level \
             + '. So, further moderation group cannot be created!'

        elif (pg_moderation_level > 0) or increment_mod_level:
            # valid condition to create a sub group

            if (pg_moderation_level == 0) and increment_mod_level:
                # needs to increase moderation_level of all group hierarchy
                self.increment_hierarchy_mod_level(parent_group_id)
                pg_moderation_level += 1

            try:
                sg_altnames = self.altnames[sg_member_of][pg_moderation_level-1] \
                                + u" of " + pg_name
            except Exception, e:
                sg_altnames = sg_name

            # create new sub-group and append it to parent group:
            sub_group = self.create_subgroup(parent_group_id, sg_name, \
              sg_member_of, moderation_level=(pg_moderation_level-1), \
               altnames=sg_altnames)

            return sub_group


    def increment_hierarchy_mod_level(self, group_id):
        '''
        Raises moderation_level by one of all the groups in the hierarchy.
        '''

        try:
            group_id = ObjectId(group_id)

        except:
            group_name, group_id = get_group_name_id(group_id)

        result = self.get_all_group_hierarchy(group_id)

        if result[0]:
            group_list = result[1]
            is_updated = False

            for each_group in group_list:
                is_updated = True
                # adding +1 to existing moderation_level
                each_group.moderation_level += 1
                each_group.save()

            if is_updated:
                return True
            else:
                return False

        # something went wrong to get group list
        else:
            return False


    def get_all_group_hierarchy(self, group_id):
        '''
        Provide _id of any of the group and get list of all groups.
        Order will be from top to bottom.
        e.g: [top_gr_obj, sub_gr_obj, sub_sub_gr_obj, ..., ...]
        NOTE: this function will return hierarchy of 
        only groups with edit_policy: 'EDITABLE_MODERATED'
        '''
        top_group = self.get_top_group_of_hierarchy(group_id)

        if top_group[0]:
            # getting object of top group
            top_group = top_group[1]

        else:  # fail to get top group
            return top_group

        all_sub_group_list = [top_group]

        group_obj = top_group

        while group_obj and group_obj.post_node:
            group_obj = self.get_particular_member_of_subgroup(group_obj._id, 'ModeratingGroup')
            if group_obj:
                all_sub_group_list.append(group_obj)
            else:
                return False, [top_group]

        return True, all_sub_group_list


    def get_top_group_of_hierarchy(self, group_id):
        '''
        getting top group object of hierarchy.
        Returns mongokit object of top group.
        '''
        curr_group_obj = node_collection.one({'_id': ObjectId(group_id)})

        # loop till there is no end of prior_node or till reaching at top group.
        while curr_group_obj and curr_group_obj.prior_node:
            curr_group_obj = node_collection.one({'_id': curr_group_obj.prior_node[0]})

            if curr_group_obj.edit_policy != 'EDITABLE_MODERATED':
                return False, "One of the group: " + str(curr_group_obj._id) \
                 + " is not with edit_policy: EDITABLE_MODERATED."
            
        # send overwritten/first curr_group_obj's "_id"
        return True, curr_group_obj

# --- END of class CreateModeratedGroup ---
# -----------------------------------------



@get_execution_time
def group(request, group_id, app_id=None, agency_type=None):
  """Renders a list of all 'Group-type-GSystems' available within the database.
  """

  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)

  query_dict = {}
  if (app_id == "agency_type") and (agency_type in GSTUDIO_GROUP_AGENCY_TYPES):
    query_dict["agency_type"] = agency_type
  # print "=========", app_id, agency_type

  group_nodes = []
  group_count = 0
  auth = node_collection.one({'_type': u"Author", 'name': unicode(request.user.username)})

  if request.method == "POST":
    # Page search view
    title = gst_group.name
    
    search_field = request.POST['search_field']

    if auth:
      # Logged-In View
      cur_groups_user = node_collection.find({'_type': "Group", 
                                       '_id': {'$nin': [ObjectId(group_id), auth._id]},
                                       '$and': [query_dict],
                                       '$or': [
                                          {'$and': [
                                            {'name': {'$regex': search_field, '$options': 'i'}},
                                            {'$or': [
                                              {'created_by': request.user.id}, 
                                              {'group_admin': request.user.id},
                                              {'author_set': request.user.id},
                                              {'group_type': 'PUBLIC'} 
                                              ]
                                            }                                  
                                          ]
                                          },
                                          {'$and': [
                                            {'tags': {'$regex':search_field, '$options': 'i'}},
                                            {'$or': [
                                              {'created_by': request.user.id}, 
                                              {'group_admin': request.user.id},
                                              {'author_set': request.user.id},
                                              {'group_type': 'PUBLIC'} 
                                              ]
                                            }                                  
                                          ]
                                          }, 
                                        ],
                                        'name': {'$nin': ["home"]},
                                   }).sort('last_update', -1)

      if cur_groups_user.count():
        for group in cur_groups_user:
          group_nodes.append(group)

      group_count = cur_groups_user.count()
        
    else:
      # Without Log-In View
      cur_public = node_collection.find({'_type': "Group", 
                                       '_id': {'$nin': [ObjectId(group_id)]},
                                       '$and': [query_dict],
                                       '$or': [
                                          {'name': {'$regex': search_field, '$options': 'i'}}, 
                                          {'tags': {'$regex':search_field, '$options': 'i'}}
                                        ],
                                        'name': {'$nin': ["home"]},
                                        'group_type': "PUBLIC"
                                   }).sort('last_update', -1)
  
      if cur_public.count():
        for group in cur_public:
          group_nodes.append(group)
      
      group_count = cur_public.count()

    return render_to_response("ndf/group.html",
                              {'title': title,
                               'appId':app._id,
                               'searching': True, 'query': search_field,
                               'group_nodes': group_nodes, 'group_nodes_count': group_count,
                               'groupid':group_id, 'group_id':group_id
                              }, 
                              context_instance=RequestContext(request)
    )

  else: # for GET request

    if auth:
      # Logged-In View
      cur_groups_user = node_collection.find({'_type': "Group", 
                                              '$and': [query_dict],
                                              '_id': {'$nin': [ObjectId(group_id), auth._id]},
                                              'name': {'$nin': ["home"]},
                                              '$or': [
                                                      {'created_by': request.user.id},
                                                      {'author_set': request.user.id},
                                                      {'group_admin': request.user.id},
                                                      {'group_type': 'PUBLIC'}
                                                    ]
                                            }).sort('last_update', -1)
      # if cur_groups_user.count():
      #   for group in cur_groups_user:
      #     group_nodes.append(group)

      if cur_groups_user.count():
        group_nodes = cur_groups_user
        group_count = cur_groups_user.count()
        
    else:
      # Without Log-In View
      cur_public = node_collection.find({'_type': "Group", 
                                         '_id': {'$nin': [ObjectId(group_id)]},
                                         '$and': [query_dict],
                                         'name': {'$nin': ["home"]},
                                         'group_type': "PUBLIC"
                                     }).sort('last_update', -1)
  
      # if cur_public.count():
      #   for group in cur_public:
      #     group_nodes.append(group)
  
      if cur_public.count():
        group_nodes = cur_public
        group_count = cur_public.count()
    
    return render_to_response("ndf/group.html", 
                              {'group_nodes': group_nodes,
                               'appId':app._id,
                               'group_nodes_count': group_count,
                               'groupid': group_id, 'group_id': group_id
                              }, context_instance=RequestContext(request))



@login_required
@get_execution_time
def create_group(request,group_id):

  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)

  if request.method == "POST":

    cname = request.POST.get('name', "").strip()
    edit_policy = request.POST.get('edit_policy', "")
    group_type = request.POST.get('group_type', "")
    moderation_level = request.POST.get('moderation_level', '1')

    if request.POST.get('edit_policy', "") == "EDITABLE_MODERATED":

        # instantiate moderated group
        mod_group = CreateModeratedGroup(request)

        # calling method to create new group
        result = mod_group.create_new_moderated_group(cname, moderation_level)
        
    else:

        # instantiate moderated group
        group = CreateGroup(request)

        # calling method to create new group
        result = group.create_group(cname)
        
    if result[0]:
        colg = result[1]

    # auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) }) 

    # has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })

    shelves = []
    shelf_list = {}
    
    # if auth:
    #   shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type.$id': has_shelf_RT._id })

    #   if shelf:
    #     for each in shelf:
    #       shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)})           
    #       shelves.append(shelf_name)

    #       shelf_list[shelf_name.name] = []         
    #       for ID in shelf_name.collection_set:
    #         shelf_item = node_collection.one({'_id': ObjectId(ID) })
    #         shelf_list[shelf_name.name].append(shelf_item.name)
                  
    #   else:
    #     shelves = []

    return render_to_response("ndf/groupdashboard.html", 
                                {'groupobj': colg, 'appId': app._id, 'node': colg,
                                  'user': request.user,
                                  'groupid': colg._id, 'group_id': colg._id,
                                  'shelf_list': shelf_list,'shelves': shelves
                                },context_instance=RequestContext(request))


  # for rendering empty form page:
  available_nodes = node_collection.find({'_type': u'Group'})
  nodes_list = []
  for each in available_nodes:
      nodes_list.append(str((each.name).strip().lower()))
  return render_to_response("ndf/create_group.html", {'groupid': group_id, 'appId': app._id, 'group_id': group_id, 'nodes_list': nodes_list},RequestContext(request))


# @get_execution_time
#def home_dashboard(request):
#     try:
#         groupobj=node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
#     except Exception as e:
#         groupobj=""
#         pass
#     print "frhome--",groupobj
#     return render_to_response("ndf/groupdashboard.html",{'groupobj':groupobj,'user':request.user,'curgroup':groupobj},context_instance=RequestContext(request))


@login_required
@get_execution_time
def populate_list_of_members():
	members = User.objects.all()
	memList = []
	for mem in members:
		memList.append(mem.username)	
	return memList


@login_required
@get_execution_time
def populate_list_of_group_members(group_id):
    try :
      try:
        author_list = node_collection.one({"_type":"Group", "_id":ObjectId(group_id)}, {"author_set":1, "_id":0})
      except:
        author_list = node_collection.find_one({"_type":"Group", "name":group_id}, {"author_set":1, "_id":0})
      
      memList = []

      for author in author_list.author_set:
          name_author = User.objects.get(pk=author)
          memList.append(name_author)
      return memList
    except:
        return []


@get_execution_time
def group_dashboard(request, group_id=None):
  # # print "reahcing"
  # if ins_objectid.is_valid(group_id) is False :
  #   group_ins = node_collection.find_one({'_type': "Group","name": group_id})
  #   auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
  #   if group_ins:
	 #    group_id = str(group_ins._id)
  #   else :
	 #    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	 #    if auth :
	 #    	group_id = str(auth._id)	
  # else :
  # 	pass

  try:
    group_obj = "" 
    shelf_list = {}
    shelves = []
    alternate_template = ""
    profile_pic_image = None

    group_obj = get_group_name_id(group_id, get_obj=True)

    if not group_obj:
      group_obj=node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
      group_id=group_obj['_id']
    else:
      # group_obj=node_collection.one({'_id':ObjectId(group_id)})
      group_id = group_obj._id

      # getting the profile pic File object
      for each in group_obj.relation_set:
          if "has_profile_pic" in each:
              profile_pic_image = node_collection.one(
                  {'_type': "File", '_id': each["has_profile_pic"][0]}
              )
              break

    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) }) 

    if auth:

      has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })

      shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type.$id': has_shelf_RT._id })        
      shelf_list = {}

      if shelf:
        for each in shelf:
          shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)})           
          shelves.append(shelf_name)

          shelf_list[shelf_name.name] = []
          for ID in shelf_name.collection_set:
            shelf_item = node_collection.one({'_id': ObjectId(ID) })
            shelf_list[shelf_name.name].append(shelf_item.name)
              
      else:
          shelves = []

  except Exception as e:
    group_obj=node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
    group_id=group_obj['_id']
    pass

  # Call to get_neighbourhood() is required for setting-up property_order_list
  group_obj.get_neighbourhood(group_obj.member_of)

  property_order_list = []
  if "group_of" in group_obj:
    if group_obj['group_of']:
      college = node_collection.one({'_type': "GSystemType", 'name': "College"}, {'_id': 1})

      if college:
        if college._id in group_obj['group_of'][0]['member_of']:
          alternate_template = "ndf/college_group_details.html"

      property_order_list = get_property_order_with_value(group_obj['group_of'][0])

  annotations = json.dumps(group_obj.annotations)
  
  default_template = "ndf/groupdashboard.html"
  return render_to_response([alternate_template,default_template] ,{'node': group_obj, 'groupid':group_id, 
                                                       'group_id':group_id, 'user':request.user, 
                                                       'shelf_list': shelf_list,
                                                       'appId':app._id,
                                                       'annotations' : annotations, 'shelves': shelves,
                                                       'prof_pic_obj': profile_pic_image
                                                      },context_instance=RequestContext(request)
                          )


# @login_required
# @get_execution_time
# def edit_group(request, group_id):
  
#   # page_node = node_collection.one({"_id": ObjectId(group_id)})
#   # title = gst_group.name
#   # if request.method == "POST":
#   #   is_node_changed=get_node_common_fields(request, page_node, group_id, gst_group)
    
#   #   if page_node.access_policy == "PUBLIC":
#   #     page_node.group_type = "PUBLIC"

#   #   if page_node.access_policy == "PRIVATE":
#   #     page_node.group_type = "PRIVATE"
#     # page_node.save(is_changed=is_node_changed)
#     # page_node.save()
#   #   group_id=page_node._id
#   #   page_node.get_neighbourhood(page_node.member_of)
#   #   return HttpResponseRedirect(reverse('groupchange', kwargs={'group_id':group_id}))

#   # else:
#   #   if page_node.status == u"DRAFT":
#   #     page_node, ver = get_page(request, page_node)
#   #     page_node.get_neighbourhood(page_node.member_of) 

#   # available_nodes = node_collection.find({'_type': u'Group', 'member_of': ObjectId(gst_group._id) })
#   # nodes_list = []
#   # for each in available_nodes:
#   #     nodes_list.append(str((each.name).strip().lower()))

#   # return render_to_response("ndf/edit_group.html",
#   #                                   { 'node': page_node,'title':title,
#   #                                     'appId':app._id,
#   #                                     'groupid':group_id,
#   #                                     'nodes_list': nodes_list,
#   #                                     'group_id':group_id,
#   #                                     'is_auth_node':is_auth_node
#   #                                     },
#   #                                   context_instance=RequestContext(request)
#   #                                   )
    
#     group_obj = get_group_name_id(group_id, get_obj=True)

#     if request.method == "POST":
#         is_node_changed = get_node_common_fields(request, group_obj, group_id, gst_group)
#         # print "=== ", is_node_changed

#         if group_obj.access_policy == "PUBLIC":
#             group_obj.group_type = "PUBLIC"

#         elif group_obj.access_policy == "PRIVATE":
#             group_obj.group_type = "PRIVATE"

#         group_obj.save(is_changed=is_node_changed)

#         group_obj.get_neighbourhood(group_obj.member_of)

#         return HttpResponseRedirect(reverse('groupchange', kwargs={'group_id':group_obj._id}))

#     elif request.method == "GET":
#         if group_obj.status == u"DRAFT":
#             group_obj, ver = get_page(request, group_obj)
#             group_obj.get_neighbourhood(group_obj.member_of) 

#         available_nodes = node_collection.find({'_type': u'Group', '_id': {'$nin': [group_obj._id]}}, {'name': 1, '_id': 0})
#         nodes_list = [str(g_obj.name.strip().lower()) for g_obj in available_nodes]
#         # print nodes_list

#         return render_to_response("ndf/create_group.html",
#                                         {   
#                                         'node': group_obj,
#                                         'title': 'Group',
#                                         # 'appId':app._id,
#                                         'groupid':group_id,
#                                         'group_id':group_id,
#                                         'nodes_list': nodes_list,
#                                         # 'is_auth_node':is_auth_node
#                                       },
#                                     context_instance=RequestContext(request)
#                                     )

# @get_execution_time    
# @login_required
class EditGroup(View):
    """
    Class to handle create/edit group requests.
    """

    @method_decorator(login_required)
    @method_decorator(get_execution_time)
    def get(self, request, group_id):
        """
        Catering GET request of rendering group create/edit form.
        """

        group_obj = get_group_name_id(group_id, get_obj=True)

        if group_obj.status == u"DRAFT":
            group_obj, ver = get_page(request, group_obj)
            group_obj.get_neighbourhood(group_obj.member_of) 

        available_nodes = node_collection.find({'_type': u'Group','_id': {'$nin': [group_obj._id]}},
            {'name': 1, '_id': 0})
        nodes_list = [str(g_obj.name.strip().lower()) for g_obj in available_nodes]
        # print nodes_list

        # if in the case we can replace "ndf/create_group.html" with "ndf/edit_group.html"
        return render_to_response("ndf/create_group.html",
                                        {   
                                        'node': group_obj,
                                        'title': 'Group', # 'appId':app._id,
                                        'groupid': group_id, 'group_id': group_id,
                                        'nodes_list': nodes_list,
                                        # 'is_auth_node':is_auth_node
                                      },
                                    context_instance=RequestContext(request)
                                    )

    def post(self, request, group_id):
        '''
        To handle post request of group form.
        To save edited or newly-created group's data. 
        '''
        group_obj = get_group_name_id(group_id, get_obj=True)

        is_node_changed = get_node_common_fields(request, group_obj, group_id, gst_group)
        # print "=== ", is_node_changed

        if group_obj.access_policy == "PUBLIC":
            group_obj.group_type = "PUBLIC"

        elif group_obj.access_policy == "PRIVATE":
            group_obj.group_type = "PRIVATE"

        group_obj.status = u"PUBLISHED"
        group_obj.save(is_changed=is_node_changed)

        group_obj.get_neighbourhood(group_obj.member_of)

        return HttpResponseRedirect(reverse('groupchange', kwargs={'group_id':group_obj._id}))

# ===END of class EditGroup() ===
    
        
@login_required
@get_execution_time
def app_selection(request, group_id):
    if ObjectId.is_valid(group_id) is False:
        group_ins = node_collection.find_one({
            '_type': "Group", "name": group_id
        })
        auth = node_collection.one({
            '_type': 'Author', 'name': unicode(request.user.username)
        })
        if group_ins:
            group_id = str(group_ins._id)
        else:
            auth = collection.Node.one({
                '_type': 'Author', 'name': unicode(request.user.username)
            })
            if auth:
                group_id = str(auth._id)
    else:
        pass

    try:
        grp = node_collection.one({
            "_id": ObjectId(group_id)
        }, {
            "name": 1, "attribute_set.apps_list": 1
        })
        if request.method == "POST":
            apps_to_set = request.POST['apps_to_set']
            apps_to_set = json.loads(apps_to_set)

            apps_to_set = [
                ObjectId(app_id) for app_id in apps_to_set if app_id
            ]

            apps_list = []
            apps_list_append = apps_list.append
            for each in apps_to_set:
                apps_list_append(
                    node_collection.find_one({
                        "_id": each
                    })
                )

            at_apps_list = node_collection.one({
                '_type': 'AttributeType', 'name': 'apps_list'
            })
            ga_node = create_gattribute(grp._id, at_apps_list, apps_list)
            return HttpResponse("Apps list updated successfully.")

        else:
            list_apps = []

            for attr in grp.attribute_set:
                if attr and "apps_list" in attr:
                    list_apps = attr["apps_list"]
                    break

            st = get_gapps(already_selected_gapps=list_apps)

            data_list = set_drawer_widget(st, list_apps)
            return HttpResponse(json.dumps(data_list))

    except Exception as e:
        print "Error in app_selection " + str(e)


@get_execution_time
def switch_group(request,group_id,node_id):
  ins_objectid = ObjectId()
  if ins_objectid.is_valid(group_id) is False:
    group_ins = node_collection.find_one({'_type': "Group","name": group_id}) 
    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) }) 
    if group_ins:
      group_id = str(group_ins._id)
    else:
      auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if auth:
      	group_id = str(auth._id)
  else :
  	pass

  try:
    node = node_collection.one({"_id": ObjectId(node_id)})
    existing_grps = node.group_set
    if request.method == "POST":
      new_grps_list = request.POST.getlist("new_groups_list[]", "")
      resource_exists = False
      resource_exists_in_grps = []
      response_dict = {'success': False, 'message': ""}

      new_grps_list_distinct = [ObjectId(item) for item in new_grps_list if ObjectId(item) not in existing_grps]
      if new_grps_list_distinct:
        for each_new_grp in new_grps_list_distinct:
          if each_new_grp:
            grp = node_collection.find({'name': node.name, "group_set": ObjectId(each_new_grp), "member_of":ObjectId(node.member_of[0])})
            if grp.count() > 0:
              resource_exists = True
              resource_exists_in_grps.append(unicode(each_new_grp))

        response_dict["resource_exists_in_grps"] = resource_exists_in_grps

      if not resource_exists:
        new_grps_list_all = [ObjectId(item) for item in new_grps_list]
        node_collection.collection.update({'_id': node._id}, {'$set': {'group_set': new_grps_list_all}}, upsert=False, multi=False)
        node.reload()
        response_dict["success"] = True
        response_dict["message"] = "Published to selected groups"
      else:
        response_dict["success"] = False
        response_dict["message"] = node.member_of_names_list[0] + " with name " + node.name + \
                " already exists. Hence Cannot Publish to selected groups."
        response_dict["message"] = node.member_of_names_list[0] + " with name " + node.name + \
                " already exists in selected group(s). " + \
                "Hence cannot be cross published now." + \
                " For publishing, you can rename this " + node.member_of_names_list[0] + " and try again."
      # print response_dict
      return HttpResponse(json.dumps(response_dict))

    else:
      coll_obj_list = []
      data_list = []
      user_id = request.user.id
      all_user_groups = []
      for each in get_all_user_groups():
        all_user_groups.append(each.name)
      st = node_collection.find({'$and': [{'_type': 'Group'}, {'author_set': {'$in':[user_id]}},{'name':{'$nin':all_user_groups}}]})
      for each in node.group_set:
        coll_obj_list.append(node_collection.one({'_id': each}))
      data_list = set_drawer_widget(st, coll_obj_list)
      return HttpResponse(json.dumps(data_list))
   
  except Exception as e:
    print "Exception in switch_group"+str(e)
    return HttpResponse("Failure")


@login_required
@get_execution_time
def publish_group(request,group_id,node):
  # ins_objectid  = ObjectId()
  # if ins_objectid.is_valid(group_id) is False :
  #   group_ins = node_collection.find_one({'_type': "Group","name": group_id})
  #   auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
  #   if group_ins:
	 #    group_id = str(group_ins._id)
  #   else:
	 #    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	 #    if auth :
	 #    	group_id = str(auth._id)	
  # else :
  # 	pass

    group_obj = get_group_name_id(group_id, get_obj=True)
    profile_pic_image = None

    if group_obj:
      # group_obj=node_collection.one({'_id':ObjectId(group_id)})
      group_id = group_obj._id

      # getting the profile pic File object
      for each in group_obj.relation_set:

          if "has_profile_pic" in each:
              profile_pic_image = node_collection.one( {'_type': "File", '_id': each["has_profile_pic"][0]} )
              break

    node=node_collection.one({'_id':ObjectId(node)})
     
    page_node,v=get_page(request,node)
    
    node.content = page_node.content
    node.content_org=page_node.content_org
    node.status=unicode("PUBLISHED")
    node.modified_by = int(request.user.id)
    node.save() 
   
    return render_to_response("ndf/groupdashboard.html",
                                   { 'group_id':group_id, 'groupid':group_id,
                                   'node':node, 'appId':app._id,                                   
                                   'prof_pic_obj': profile_pic_image
                                 },
                                  context_instance=RequestContext(request)
                              )


@login_required
@get_execution_time
def create_sub_group(request,group_id):
  try:
      ins_objectid  = ObjectId()
      grpname=""
      if ins_objectid.is_valid(group_id) is False :
          group_ins = node_collection.find_one({'_type': "Group","name": group_id}) 
          auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
          if group_ins:
              grpname=group_ins.name 
              group_id = str(group_ins._id)
          else :
              auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
              if auth :
                  group_id = str(auth._id)
                  grpname=auth.name	
      else :
          group_ins = node_collection.find_one({'_type': "Group","_id": ObjectId(group_id)})
          if group_ins:
              grpname=group_ins.name
              pass
          else:
              group_ins = node_collection.find_one({'_type': "Author","_id": ObjectId(group_id)})
              if group_ins:
                  grpname=group_ins.name
                  pass

      if request.method == "POST":
          colg = node_collection.collection.Group()
          Mod_colg=node_collection.collection.Group()
          cname=request.POST.get('name', "")
          colg.altnames=cname
          colg.name = unicode(cname)
          colg.member_of.append(gst_group._id)
          usrid = int(request.user.id)
          colg.created_by = usrid
          if usrid not in colg.author_set:
              colg.author_set.append(usrid)
          colg.modified_by = usrid
          if usrid not in colg.contributors:
              colg.contributors.append(usrid)
          colg.group_type = request.POST.get('group_type', "")
          colg.edit_policy = request.POST.get('edit_policy', "")
          colg.subscription_policy = request.POST.get('subscription', "OPEN")
          colg.visibility_policy = request.POST.get('existance', "ANNOUNCED")
          colg.disclosure_policy = request.POST.get('member', "DISCLOSED_TO_MEM")
          colg.encryption_policy = request.POST.get('encryption', "NOT_ENCRYPTED")
          colg.agency_type=request.POST.get('agency_type',"")
          if group_id:
              colg.prior_node.append(group_ins._id)
          colg.save()
          #save subgroup_id in the collection_set of parent group 
          group_ins.collection_set.append(colg._id)
          #group_ins.post_node.append(colg._id)
          group_ins.save()
    
          if colg.edit_policy == "EDITABLE_MODERATED":
              Mod_colg.altnames = cname + "Mod" 
              Mod_colg.name = cname + "Mod"     
              Mod_colg.group_type = "PRIVATE"
              Mod_colg.created_by = usrid
              if usrid not in Mod_colg.author_set:
                  Mod_colg.author_set.append(usrid)
              Mod_colg.modified_by = usrid
              if usrid not in Mod_colg.contributors:
                  Mod_colg.contributors.append(usrid)
              Mod_colg.prior_node.append(colg._id)
              Mod_colg.save() 

              colg.post_node.append(Mod_colg._id)
              colg.save()
          auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) }) 
          has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })
          shelves = []
          shelf_list = {}
    
          if auth:
              shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type.$id': has_shelf_RT._id })        

              if shelf:
                  for each in shelf:
                      shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)})
                      shelves.append(shelf_name)
                      shelf_list[shelf_name.name] = []
                      for ID in shelf_name.collection_set:
                          shelf_item = node_collection.one({'_id': ObjectId(ID) })
                          shelf_list[shelf_name.name].append(shelf_item.name)
                  
              else:
                  shelves = []

          return render_to_response("ndf/groupdashboard.html",{'groupobj':colg,'appId':app._id,'node':colg,'user':request.user,
                                                         'groupid':colg._id,'group_id':colg._id,
                                                         'shelf_list': shelf_list,'shelves': shelves
                                                        },context_instance=RequestContext(request))
      available_nodes = node_collection.find({'_type': u'Group', 'member_of': ObjectId(gst_group._id) })
      nodes_list = []
      for each in available_nodes:
          nodes_list.append(str((each.name).strip().lower()))

      return render_to_response("ndf/create_sub_group.html", {'groupid':group_id,'maingroup':grpname,'group_id':group_id,'nodes_list': nodes_list},RequestContext(request))
  except Exception as e:
      print "Exception in create subgroup "+str(e)
