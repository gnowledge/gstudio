''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
import datetime

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.views.generic import View
from django.core.cache import cache

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, GSTUDIO_GROUP_AGENCY_TYPES, GSTUDIO_NROER_MENU, GSTUDIO_NROER_MENU_MAPPINGS,GSTUDIO_FILE_UPLOAD_FORM, GSTUDIO_FILE_UPLOAD_POINTS, GSTUDIO_BUDDY_LOGIN
from gnowsys_ndf.settings import GSTUDIO_MODERATING_GROUP_ALTNAMES, GSTUDIO_PROGRAM_EVENT_MOD_GROUP_ALTNAMES, GSTUDIO_COURSE_EVENT_MOD_GROUP_ALTNAMES
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME
from gnowsys_ndf.ndf.models import NodeJSONEncoder, node_collection, triple_collection, Counter, counter_collection, Node
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.ndf.views.asset import *
from gnowsys_ndf.ndf.views.utils import add_to_list
# from gnowsys_ndf.ndf.models import GSystemType, GSystem, Group, Triple
# from gnowsys_ndf.ndf.models import c
from gnowsys_ndf.ndf.views.ajax_views import *
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_all_user_groups, get_sg_member_of, get_relation_value, get_attribute_value, check_is_gstaff # get_existing_groups
# from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.views.moderation import *
# from gnowsys_ndf.ndf.views.moderation import moderation_status, get_moderator_group_set, create_moderator_task
# ######################################################################################################################################

group_gst = node_collection.one({'_type': 'GSystemType', 'name': u'Group'})
gst_group = group_gst
app = gst_group

moderating_group_gst = node_collection.one({'_type': 'GSystemType', 'name': u'ModeratingGroup'})
programevent_group_gst = node_collection.one({'_type': 'GSystemType', 'name': u'ProgramEventGroup'})
courseevent_group_gst = node_collection.one({'_type': 'GSystemType', 'name': u'CourseEventGroup'})
announced_unit_gst = node_collection.one({'_type': 'GSystemType', 'name': u'announced_unit'})
partner_group_gst = node_collection.one({'_type': 'GSystemType', 'name': u'PartnerGroup'})

file_gst = node_collection.one({'_type': 'GSystemType', 'name': 'File'})
page_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Page'})
task_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Task'})

# ######################################################################################################################################
#      V I E W S   D E F I N E D   F O R   G A P P -- ' G R O U P '
# ######################################################################################################################################

class CreateGroup(object):
    """
    Creates group.
    Instantiate group with request as argument
    """
    def __init__(self, request=HttpRequest()):
        super(CreateGroup, self).__init__()
        self.request = request
        self.moderated_groups_member_of = ['ProgramEventGroup',\
         'CourseEventGroup', 'PartnerGroup', 'ModeratingGroup']


    def is_group_exists(self, group_name):
        '''
        Checks if group with the given name exists.
        Returns Bool.
            - True: If group exists.
            - False: If group doesn't exists.
        '''

        # explicitely using "find_one" query
        group = node_collection.find_one({'_type': 'Group', 'name': unicode(group_name)})
        if group:
            return True

        else:
            return False


    def get_group_fields(self, group_name, **kwargs):
        '''
        function to fill the empty group object with values supplied.
        - group name is must and it's first argument.
        - group information may be sent either from "request" or from "kwargs".

        # If arg is kwargs, provide following dict as kwargs arg to this function.
        group_fields = {
          'altnames': '', 'group_type': '', 'edit_policy': '',
          'agency_type': '', 'moderation_level': '',
          ...., ...
        }

        # call in following way
        class_instance_var.get_group_fields(group_name, **group_fields)
        (NOTE: use ** before dict variables, in above case it's group_fields so it's: **group_fields)
        '''
        # getting the data into variables
        name = group_name

        # to check if existing group is getting edited
        node_id = kwargs.get('node_id', None)

        if kwargs.get('altnames', ''):
            altnames = kwargs.get('altnames', name)
        elif self.request:
            altnames = self.request.POST.get('altnames', name).strip()

        group_set = []
        if kwargs.get('group_set', ''):
            group_set = kwargs.get('group_set', [])
        else:
            group_set = self.request.POST.get('group_set', [])
        group_set = [group_set] if not isinstance(group_set, list) else group_set
        group_set = [ObjectId(g) for g in group_set]

        member_of = []
        if kwargs.get('member_of', ''):
            member_of = kwargs.get('member_of', [])
        else:
            member_of = self.request.POST.get('member_of', [])
        member_of = [member_of] if not isinstance(member_of, list) else member_of
        member_of = [ObjectId(m) for m in member_of]

        if kwargs.get('group_type', ''):
            group_type = kwargs.get('group_type', u'PUBLIC')
        elif self.request:
            group_type = self.request.POST.get('group_type', u'PUBLIC')

        if kwargs.get('access_policy', ''):
            access_policy = kwargs.get('access_policy', group_type)
        elif self.request:
            access_policy = self.request.POST.get('access_policy', group_type)

        if kwargs.get('edit_policy', ''):
            edit_policy = kwargs.get('edit_policy', u'EDITABLE_NON_MODERATED')
        elif self.request:
            edit_policy = self.request.POST.get('edit_policy', u'EDITABLE_NON_MODERATED')

        if kwargs.get('subscription_policy', ''):
            subscription_policy = kwargs.get('subscription_policy', u'OPEN')
        elif self.request:
            subscription_policy = self.request.POST.get('subscription_policy', u"OPEN")

        if kwargs.get('visibility_policy', ''):
            visibility_policy = kwargs.get('visibility_policy', u'ANNOUNCED')
        elif self.request:
            visibility_policy = self.request.POST.get('visibility_policy', u'ANNOUNCED')

        if kwargs.get('disclosure_policy', ''):
            disclosure_policy = kwargs.get('disclosure_policy', u'DISCLOSED_TO_MEM')
        elif self.request:
            disclosure_policy = self.request.POST.get('disclosure_policy', u'DISCLOSED_TO_MEM')

        if kwargs.get('encryption_policy', ''):
            encryption_policy = kwargs.get('encryption_policy', u'NOT_ENCRYPTED')
        elif self.request:
            encryption_policy = self.request.POST.get('encryption_policy', u'NOT_ENCRYPTED')

        if kwargs.get('agency_type', ''):
            agency_type = kwargs.get('agency_type', u'Other')
        elif self.request:
            agency_type = self.request.POST.get('agency_type', u'Other')

        if kwargs.get('content_org', ''):
            content_org = kwargs.get('content_org', u'')
        elif self.request:
            content_org = self.request.POST.get('content_org', u'')

        if kwargs.get('content', ''):
            content = kwargs.get('content', u'')
        elif self.request:
            content = self.request.POST.get('content', u'')

        # if not content or not content_org:
        #     content = content_org = u""

        if kwargs.get('language', ''):
            language = kwargs.get('language', '')
        elif self.request:
            language = self.request.POST.get('language', ('en', 'English'))

        # whenever we are passing int: 0, condition gets false
        # therefor casting to str
        if str(kwargs.get('moderation_level', '')):
            moderation_level = kwargs.get('moderation_level', '-1')
        elif self.request:
            moderation_level = self.request.POST.get('moderation_level', '-1')

        if node_id:
            # Existing group: if node_id exists means group already exists.
            # So fetch that group and use same object to override the fields.
            group_obj = node_collection.one({'_id': ObjectId(node_id)})
        else:
            # New group: instantiate empty group object
            group_obj = node_collection.collection.Group()

        # filling the values with variables in group object:
        group_obj.name = unicode(name)
        group_obj.altnames = unicode(altnames)

        for each_gset in group_set:
            if each_gset not in group_obj.group_set:
                group_obj.group_set.append(each_gset)

        for each_mof in member_of:
            if each_mof not in group_obj.member_of:
                group_obj.member_of.append(each_mof)

        # while doing append operation make sure to-be-append is not in the list
        if gst_group._id not in group_obj.member_of:
            group_obj.member_of.append(gst_group._id)

        if gst_group._id not in group_obj.type_of:
            group_obj.type_of.append(gst_group._id)

        # user related fields:
        user_id = int(self.request.user.id)
        group_obj.created_by = user_id
        group_obj.modified_by = user_id
        if user_id not in group_obj.author_set:
            group_obj.author_set.append(user_id)
        if user_id not in group_obj.contributors:
            group_obj.contributors.append(user_id)
        if user_id not in group_obj.group_admin:
            group_obj.group_admin.append(user_id)

        # group specific fields:
        group_obj.group_type = group_type
        group_obj.access_policy = access_policy
        group_obj.edit_policy = edit_policy
        group_obj.subscription_policy = subscription_policy
        group_obj.visibility_policy = visibility_policy
        group_obj.disclosure_policy = disclosure_policy
        group_obj.encryption_policy = encryption_policy
        group_obj.agency_type = agency_type

        if language:
            language_val = get_language_tuple(unicode(language))
            group_obj.language = language_val


        '''
        Use of content_org field is deprecated.
        Instead using value from content_org variable adding to content field
         -katkamrachana 28June2017

        #  org-content
        if group_obj.content_org != content_org:
            group_obj.content_org = content_org
            is_changed = True

            # Required to link temporary files with the current user who is:
            # usrname = self.request.user.username
            # filename = slugify(name) + "-" + slugify(usrname) + "-" + ObjectId().__str__()
            # group_obj.content = org2html(content_org, file_prefix=filename)
        if group_obj.content != content:
            group_obj.content = content
            is_changed = True
        '''
        if group_obj.content != content_org:
            group_obj.content = content_org

        # decision for adding moderation_level
        if group_obj.edit_policy == "EDITABLE_MODERATED":
            group_obj.moderation_level = int(moderation_level)
        else:
            group_obj.moderation_level = -1  # non-moderated group.

        # group's should not have draft stage. So publish them:
        group_obj.status = u"PUBLISHED"

        # returning basic fields filled group object
        return group_obj

    # --- END --- get_group_fields() ------


    def create_group(self, group_name, **kwargs):
        '''
        Creates group with given args.
        - Takes group name as compulsory argument.
        - Returns tuple containing: (True/False, sub_group_object/error)
        '''
        # for editing already existing group
        node_id = kwargs.get('node_id', None)
        # print "node_id : ", node_id

        # checking if group exists with same name
        if not self.is_group_exists(group_name) or node_id:

            # print "group_name : ", group_name
            group_obj = self.get_group_fields(group_name, **kwargs)

            try:
                group_obj.save()
            except Exception, e:
                return False, e

            # group created successfully
            return True, group_obj

        else:
            return False, 'Group with same name exists.'
    # --- END --- create_group() ---


    def get_group_edit_policy(self, group_id, group_obj=None):
        '''
        Returns "edit_policy" of the group.
        - Takes group_id as compulsory and only argument.
        - Returns: either "edit_policy" or boolian "False".
        '''

        if not group_obj and not isinstance(group_obj, Group):
            group_obj = node_collection.one({'_id': ObjectId(group_id)})

        if group_obj:
            return group_obj.edit_policy

        else:
          return False
    # --- END --- get_group_edit_policy() ------


    def get_group_type(self, group_id, group_obj=None):
        '''
        Returns "group_type" of the group.
        - Takes group_id as compulsory and only argument.
        - Returns: either "group_type" or boolian "False".
        '''

        if not group_obj and not isinstance(group_obj, Group):
            group_obj = node_collection.one({'_id': ObjectId(group_id)})

        if group_obj:
            return group_obj.group_type

        else:
            return False
    # --- END --- get_group_type() ------


    def get_all_subgroups_obj_list(self, group_id, group_obj=None):
        '''
        Returns mongokit (find) cursor of sub-group documents (only immediate first level) /
        which are in the post node of argument group_id else returns False.
        - Takes group_id as compulsory and only argument.
        '''

        if not group_obj and not isinstance(group_obj, Group):
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
        - Takes group_id as compulsory and only argument.
        '''

        sg_member_of_list = []
        # get all underlying groups
        all_sg = self.get_all_subgroups_obj_list(group_id)

        if all_sg:
            # getting parent's sub group's member_of in a list
            for each_sg in all_sg:
                sg_member_of_list += each_sg.member_of_names_list

        return sg_member_of_list
    # --- END --- get_all_subgroups_member_of_list() ------

    def set_logo(self, request, group_obj, logo_rt = "has_logo"):
        from gnowsys_ndf.ndf.views.file import save_file
        # adding thumbnail
        logo_img_node = None
        grel_id = None
        # logo_img_node_grel_id = get_relation_value(group_obj._id,unicode(logo_rt))
        grel_dict = get_relation_value(group_obj._id,unicode(logo_rt))
        is_cursor = grel_dict.get("cursor",False)
        if not is_cursor:
            logo_img_node = grel_dict.get("grel_node")
            grel_id = grel_dict.get("grel_id")
        # if logo_img_node_grel_id:
        #     logo_img_node = logo_img_node_grel_id[0]
        #     grel_id = logo_img_node_grel_id[1]
        f = request.FILES.get("filehive", "")
        # print "\nf is ",f

        if f:

            # if existing logo image is found
            if logo_img_node:
                # print "\nlogo_img_node--",logo_img_node
                # check whether it appears in any other node's grelation
                rel_obj = None
                rel_obj = triple_collection.find({"_type": "GRelation", 'subject': {'$ne': ObjectId(group_obj._id)}, 'right_subject': logo_img_node._id})
                file_cur = node_collection.find({'_type':"GSystem",'_id': {'$ne': logo_img_node._id}})
                # print "\nrel_obj--",rel_obj.count()
                # print "\nfile_cur.count()--",file_cur.count()
                if rel_obj.count() > 0 or file_cur.count() > 0:
                    # if found elsewhere too, delete it from current node's grelation ONLY
                    # print "\n Image exists for others"
                    if grel_id:
                        del_status, del_status_msg = delete_grelation(
                            node_id=ObjectId(grel_id),
                            deletion_type=1
                        )
                        # print del_status, "--", del_status_msg
                else:
                    # else delete the logo file
                    # print "\n delete node"
                    del_status, del_status_msg = delete_node(
                        node_id=logo_img_node._id,
                        deletion_type=1
                    )
                    print del_status, "--", del_status_msg

            from gnowsys_ndf.ndf.views.filehive import write_files
            is_user_gstaff = check_is_gstaff(group_obj._id, request.user)

            # gs_obj_list = write_files(request, group_id)
            fileobj_list = write_files(request, group_obj._id)
            # print "request&&&&&&&&&&&&&&&&&&&&&&",request
            fileobj_id = fileobj_list[0]['_id']
            # print "fileobj_id****************************",fileobj_list
            fileobj = node_collection.one({'_id': ObjectId(fileobj_id) })
            # print "fileobj_id-------------------",fileobj
            # fileobj,fs = save_file(f,f.name,request.user.id,group_obj._id, "", "", username=unicode(request.user.username), access_policy="PUBLIC", count=0, first_object="", oid=True)
            if fileobj:
                rt_has_logo = node_collection.one({'_type': "RelationType", 'name': unicode(logo_rt)})
                # print "\n creating GRelation has_logo\n"
                create_grelation(group_obj._id, rt_has_logo, ObjectId(fileobj._id))

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
        "parent_group_id" and "sub_group_name" and "sg_member_of" are compulsory args.
        '''

        # get basic fields filled group object
        group_obj = self.get_group_fields(sub_group_name, **kwargs)

        # if sg_member_of in ['ProgramEventGroup', 'CourseEventGroup', 'PartnerGroup', 'ModeratingGroup']:
        if sg_member_of in self.moderated_groups_member_of:
            # overriding member_of field of subgroup
            member_of_group = node_collection.one({'_type': u'GSystemType', 'name': unicode(sg_member_of)})
            group_obj.member_of = [ObjectId(member_of_group._id)]

            # for subgroup's of this types, group_type must be PRIVATE and EDITABLE_MODERATED
            group_obj.group_type = 'PRIVATE'
            group_obj.access_policy = u'PRIVATE'
            group_obj.edit_policy = 'EDITABLE_MODERATED'

        else:  # for normal sub-groups
            if not group_obj.group_type:
                # if group_type is not specified take it from parent:
                group_obj.group_type = self.get_group_type(parent_group_id)

            # if not group_obj.edit_policy:
            #     group_obj.edit_policy = self.get_group_edit_policy(parent_group_id)

        # check if group object's prior_node has _id of parent group, otherwise add one.
        if ObjectId(parent_group_id) not in group_obj.prior_node:
            group_obj.prior_node.append(ObjectId(parent_group_id))

        return group_obj


    def create_subgroup(self, parent_group_id, sub_group_name, sg_member_of, **kwargs):
        '''
        Creates sub-group with given args.
        Returns tuple containing True/False, sub_group_object/error.
        '''

        try:
            parent_group_id = ObjectId(parent_group_id)

        except:
            parent_group_name, parent_group_id = get_group_name_id(parent_group_id)

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
        Otherwise returns False.
        '''
        if sg_member_of == 'Group':
            # i.e: group is normal-sub-group.
            return True
        elif sg_member_of == 'subgroup':
            # i.e: group is normal-sub-group.
            return True

        # elif sg_member_of in ['ProgramEventGroup', 'CourseEventGroup', 'PartnerGroup', 'ModeratingGroup']:
        elif sg_member_of in self.moderated_groups_member_of:
            if self.get_group_edit_policy(parent_group_id) == 'EDITABLE_MODERATED':

                # if current sub-groups member_of is in parent's any one of the sub-group,
                # i.e: sub-group with current property exists in/for parent group.
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
        Returns sub-group-object having supplied particular member_of.
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

    def set_partnergroup(self, request, group_object):
        try:
            at_list = ['house_street','town_city','pin_code','email_id','alternate_number','mobile_number','website']
            partner_at_cur = node_collection.find({'_type':"AttributeType",'name':{'$in': at_list}})
            for each in partner_at_cur:
                each_name_val = self.request.POST.get(each.name,'')
                create_gattribute(group_object._id, each, each_name_val)
                group_object.reload()
            # print "\n\n group_object.attribute_set",group_object.attribute_set
            return True
        except Exception as e:
            return False

# --- END of class CreateSubGroup ---
# --------------------------------


class CreateModeratedGroup(CreateSubGroup):
    """
        Creates moderation group and it's sub-group/s.
        Instantiate with request.
    """
    def __init__(self, request):
        super(CreateSubGroup, self).__init__(request)
        self.request = request
        self.edit_policy = 'EDITABLE_MODERATED'
        # maintaining dict of group types and their corresponding sub-groups altnames.
        # referenced while creating new moderated sub-groups.
        self.altnames = {
            'ModeratingGroup': GSTUDIO_MODERATING_GROUP_ALTNAMES,
            'ProgramEventGroup': GSTUDIO_PROGRAM_EVENT_MOD_GROUP_ALTNAMES,
            'CourseEventGroup': GSTUDIO_COURSE_EVENT_MOD_GROUP_ALTNAMES
        }


    def create_edit_moderated_group(self, group_name, moderation_level=1,
             sg_member_of="ModeratingGroup", top_mod_groups_parent=None,
             perform_checks=True, **kwargs):
        '''
        Creates/Edits top level group as well as underlying sub-mod groups.
        - Takes group_name as compulsory argument and optional kwargs.
        - Returns tuple: (True/False, top_group_object/error)
        '''

        # retrieves node_id. means it's edit operation of existing group.
        node_id = kwargs.get('node_id', None)
        # print "\n\n top_mod_groups_parent",top_mod_groups_parent

        # checking if group exists with same name
        if not self.is_group_exists(group_name) or node_id:

            # values will be taken from POST form fields
            group_obj = self.get_group_fields(group_name, node_id=node_id)
            group_obj.save()
            if perform_checks:
                try:
                    if top_mod_groups_parent:
                        # check if group object's prior_node has _id of parent group,
                        # otherwise add one.
                        if ObjectId(top_mod_groups_parent) not in group_obj.prior_node:
                            group_obj.prior_node.append(ObjectId(top_mod_groups_parent))

                    group_obj.save()

                    if top_mod_groups_parent:
                        # equivalently, adding newly created top moderated group's _id
                        # in post node of it's immediate parent group
                        self.add_subgroup_to_parents_postnode(top_mod_groups_parent, group_obj._id, sg_member_of=sg_member_of)

                except Exception, e:
                    # if any errors return tuple with False and error
                    # print e
                    return False, e
                if node_id:
                    # i.e: Editing already existed group object.
                    # method modifies the underlying mod-sub-group structure and doesn't return anything.
                    self.check_reset_mod_group_hierarchy(sg_member_of=sg_member_of, top_group_obj=group_obj)

                else:
                    # i.e: New group is created and following code will create
                    # sub-mod-groups as per specified in the form.
                    parent_group_id = group_obj._id

                    for each_sg_iter in range(0, int(moderation_level)):

                        result = self.add_moderation_level(parent_group_id, sg_member_of=sg_member_of)

                        # result is tuple of (bool, newly-created-sub-group-obj)
                        if result[0]:
                            # overwritting parent's group_id with currently/newly-created group object
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
        - compulsory argument:
            - "_id/name" of parent
            - sub_group's "member_of": <str>.
        - increment_mod_level: If you want to add next moderation subgroup, despite of
                    moderation_level is 0.
                    In this case, if value is True,
                    moderation_level of all top hierarchy groups will be updated by 1.
        '''
        # getting group object
        parent_group_object = get_group_name_id(parent_group_id, get_obj=True)

        # pg: parent group
        pg_name = parent_group_object.name
        pg_moderation_level = parent_group_object.moderation_level
        # print pg_moderation_level, "===", pg_name

        # possible/next mod group name:
        # sg: sub group
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
                self.increment_hierarchy_mod_level(parent_group_id, sg_member_of)
                pg_moderation_level += 1

            try:
                result = self.get_top_group_of_hierarchy(parent_group_object._id)
                altnames_dict_index = -1
                if result:
                    top_group_obj = result[1]
                    top_group_moderation_level = top_group_obj.moderation_level
                    pg_name = top_group_obj.name
                    altnames_dict_index = top_group_moderation_level - pg_moderation_level
                sg_altnames = self.altnames[sg_member_of][altnames_dict_index] \
                                + u" of " + pg_name
                # print "=== in try", sg_altnames
            except Exception, e:
                # print e
                sg_altnames = sg_name
                # print "=== in Exception", sg_altnames

            # create new sub-group and append it to parent group:
            sub_group_result_tuple = self.create_subgroup(parent_group_id, sg_name, \
              sg_member_of, moderation_level=(pg_moderation_level-1), \
               altnames=sg_altnames)

            # print "\n=== sub_group_result_tuple", sub_group_result_tuple
            return sub_group_result_tuple


    def increment_hierarchy_mod_level(self, group_id, sg_member_of):
        '''
        Raises moderation_level by one of all the groups (right from top) in the hierarchy.
        Takes group_id as compulsory argument.
        Returns boolian True/False, depending on Success/Failure.
        '''

        try:
            group_id = ObjectId(group_id)
        except:
            group_name, group_id = get_group_name_id(group_id)

        # firstly getting all the sub-group-object list
        result = self.get_all_group_hierarchy(group_id, sg_member_of=sg_member_of)

        if result[0]:
            # get group's object's list into variables
            group_list = result[1]
            # flag
            is_updated = False

            for each_group in group_list:

                # change flag to True
                is_updated = True

                # adding +1 to existing moderation_level
                updated_moderation_level = each_group.moderation_level + 1

                node_collection.collection.update({'_id': each_group._id},
                            {'$set': {'moderation_level': updated_moderation_level } },
                            upsert=False, multi=False )

            if is_updated:
                return True

            else:
                return False

        # something went wrong to get group list
        else:
            return False


    def get_all_group_hierarchy(self, group_id, sg_member_of, top_group_obj=None, with_deleted=False):
        '''
        Provide _id of any of the group in the hierarchy and get list of all groups.
        Order will be from top to bottom.
        Arguments it takes:
            - "group_id": Takes _id of any of the group among hierarchy
            - "top_group_obj":  Takes object of top group (optional).
                                To be used in certain conditions.
            - "with_deleted":   Takes boolean value.
                                If it's True - returns all the groups irrespective of:
                                post_node and status field whether it's deleted or not.
                                To be used cautiously in certain conditions.
        e.g: [top_gr_obj, sub_gr_obj, sub_sub_gr_obj, ..., ...]
        NOTE: this function will return hierarchy of
        only groups with edit_policy: 'EDITABLE_MODERATED'
        '''
        # It will be good to go through proper flow.
        # Despite of either argument of top_group_obj is provided or not.
        # That's why using following step:
        result = self.get_top_group_of_hierarchy(group_id)
        # print "\n\n result",result

        if result[0]:
            # getting object of top group
            top_group = result[1]

        elif top_group_obj:
            # if top group is in args and result if negative.
            top_group = top_group_obj

        else:
            # fail to get top group
            return result

        # starting list with top-group's object:
        all_sub_group_list = [top_group]

        # taking top_group's object in group_obj. which will be used to start while loop
        group_obj = top_group

        # loop till overwritten group_obj exists and
        # if group_obj.post_node exists or with_deleted=True
        while group_obj and (group_obj.post_node or with_deleted):
            group_member_of_names_list = group_obj.member_of_names_list
            before_group_obj = group_obj

            # getting previous group objects name before it get's overwritten
            temp_group_obj_name = group_obj.name
            group_obj = self.get_particular_member_of_subgroup(group_obj._id, sg_member_of)
            # print "---===", group_obj

            # if in the case group_obj doesn't exists and with_deleted=True
            if with_deleted and not group_obj:

                try:
                    temp_group_name = unicode(group_obj_name + '_mod')
                except:
                    temp_group_name = unicode(temp_group_obj_name + '_mod')
                # firing named query here. with the rule of group names are unique and cannot be edited.
                group_obj = node_collection.one({'_type': u'Group',
                    'name': temp_group_name})

                # required to break the while loop along with with_deleted=True
                if not group_obj:
                    return True, all_sub_group_list

            # group object found with regular conditions
            if group_obj:
                group_obj_name = group_obj.name
                all_sub_group_list.append(group_obj)

            # group object not found with regular conditions and arg: with_deleted=False (default val)
            else:
                # return partially-completed/incompleted (at least with top-group-obj) group hierarchy list.
                return False, all_sub_group_list

        # while loop completed. now return computed list
        return True, all_sub_group_list

    def get_top_group_of_hierarchy(self, group_id):
        '''
        For getting top group object of hierarchy.
        Arguments:
        - group_id: _id of any of the group in the hierarchy.
        Returns top-group-object.
        '''
        curr_group_obj = node_collection.one({'_id': ObjectId(group_id)})

        # loop till there is no end of prior_node or till reaching at top group.
        while curr_group_obj and curr_group_obj.prior_node:

            temp_curr_group_obj = curr_group_obj

            # fetching object having curr_group_obj in it's prior_node:
            curr_group_obj = node_collection.one({'_id': curr_group_obj.prior_node[0]})

            # hierarchy does exists for 'EDITABLE_MODERATED' groups.
            # if edit_policy of fetched group object is not 'EDITABLE_MODERATED' return false.
            if curr_group_obj.edit_policy != 'EDITABLE_MODERATED':
                return True, temp_curr_group_obj
                # return False, "One of the group: " + str(curr_group_obj._id) + " is not with edit_policy: EDITABLE_MODERATED."

        # send overwritten/first curr_group_obj's "_id"
        return True, curr_group_obj


    def check_reset_mod_group_hierarchy(self, top_group_obj, sg_member_of):
        '''
        This is the method to reset/adjust all the group objects in the hierarchy,
        right from top group to last group.
        Method works-on/reset's/updates following fields of group object \
        according to top group object's fields:
            - moderation_level
            - post_node
            - status
            - altnames
            - member_of
        NOTE: "prior_node" is not updated or not taken into consideration.
              can be used in future/in-some-cases.
        Argument:
            - top_group_obj: Top group's object
        '''

        # instantiate variable group_moderation_level.
        # used for setting moderation_level of all groups
        group_moderation_level = 0

        # last sub-groups _id
        last_sg_id = top_group_obj._id

        # getting all the group hierarchy irrespective of
        # it's fields like post_node, moderation_level, status
        result = self.get_all_group_hierarchy(top_group_obj._id, \
            sg_member_of=sg_member_of, top_group_obj=top_group_obj, with_deleted=True)

        if result[0]:

            # getting all the group objects hierarchy in the list:
            all_sub_group_obj_list = result[1]
            # Zero index of all_sub_group_obj_list is top-group.

            # print [g.name for g in all_sub_group_obj_list]

            top_group_moderation_level = top_group_obj.moderation_level
            top_group_name = top_group_obj.name

            # overwritting group_moderation_level
            group_moderation_level = top_group_moderation_level

            # checking moderation_level hierarchy lists of:
            # - list created from iterating over all_sub_group_obj_list and
            # - list created from range starts from top_group_obj's moderation_level till 0.
            # if these both are same then there is no point in going ahead and do processing.
            # bacause there is no changes in the underlying heirarchy.
            # So return from here if both lists are equal.
            # ml: moderation_level
            if [ml.moderation_level for ml in all_sub_group_obj_list] == \
            [m for m in range(top_group_moderation_level, -1, -1)]:
                # print "=== return"
                return

            # looping through each group object of/in \
            # all_sub_group_obj_list with current iteration index:
            for index, each_sg in enumerate(all_sub_group_obj_list):
                # print "\n=== group_moderation_level : ", group_moderation_level
                # print each_sg.moderation_level, "=== each_sg name : ", each_sg.name

                # getting immediate parent group of current iterated group w.r.t. all_sub_group_obj_list
                # pg: parent group
                pg_obj = all_sub_group_obj_list[index - 1] if (index > 0) else top_group_obj
                pg_id = pg_obj._id
                pg_name = pg_obj.name

                # even we need to update altnames field \
                 # w.r.t. altnames dict (defined at class level variable)
                try:
                    sg_altnames = self.altnames[sg_member_of][index-1] \
                                    + u" of " + top_group_name
                except Exception, e:
                    # if not found in altnames dict (defined at class level variable)
                    sg_altnames = each_sg.name

                # do not update altnames field of top group w.r.t altnames dict and
                # keep Group gst's id in member_of of top-group's object:
                if each_sg._id == top_group_obj._id:
                    sg_altnames = each_sg.altnames
                    member_of_id = group_gst._id
                else:
                    if sg_member_of == "ModeratingGroup":
                        member_of_id = moderating_group_gst._id
                    elif sg_member_of == "ProgramEventGroup":
                        member_of_id = programevent_group_gst._id
                    elif sg_member_of == "CourseEventGroup":
                        member_of_id = courseevent_group_gst._id

                # print "=== altnames: ", sg_altnames

                if group_moderation_level > 0:
                    # print "=== level > 0", each_sg.name

                    node_collection.collection.update({'_id': each_sg._id},
                        {'$set': {
                            'altnames': sg_altnames,
                            'member_of': [member_of_id],
                            'moderation_level': group_moderation_level,
                            'status': u'PUBLISHED'
                            }
                        },
                        upsert=False, multi=False )

                    # except top-group, add current group's _id in top group's post_node
                    if pg_id != each_sg._id:
                        self.add_subgroup_to_parents_postnode(pg_id, each_sg._id, sg_member_of)

                    # one group/element of all_sub_group_obj_list is processed now \
                    # decrement group_moderation_level by 1:
                    group_moderation_level -= 1

                    # update last_sg variables:
                    last_sg_id = each_sg._id
                    last_sg_moderation_level = each_sg.moderation_level

                elif group_moderation_level == 0:
                    # only difference in above level>0 and this level==0 is:
                    #   last/leaf group-node (w.r.t. top_group_object.moderation_level) \
                    #   of hierarchy should not have post_node.

                    # print "=== level == 0", each_sg.name
                    node_collection.collection.update({'_id': each_sg._id},
                        {'$set': {
                            'altnames': sg_altnames,
                            'member_of': [member_of_id],
                            'moderation_level': group_moderation_level,
                            'status': u'PUBLISHED',
                            'post_node': []
                            }
                        },
                        upsert=False, multi=False )
                    # except top-group, add current group's _id in top group's post_node
                    if pg_id != each_sg._id:
                        self.add_subgroup_to_parents_postnode(pg_id, each_sg._id, sg_member_of)

                    # one group/element of all_sub_group_obj_list is processed now \
                    # decrement group_moderation_level by 1:
                    group_moderation_level -= 1

                    # update last_sg variables:
                    last_sg_id = each_sg._id
                    last_sg_moderation_level = each_sg.moderation_level

                elif group_moderation_level < 0:
                    # Now these/this are/is already created underlying moderated group's in the hierarchy.
                    # We do need to update following fields of this group object:
                    #     - moderation_level: -1
                    #     - status: u"DELETED"
                    #     - member_of: [<_id of Group gst>]
                    #     - post_node: []

                    # While doing above process, resources in these/this group need to be freed.
                    # So, fetching all the resources in this group and publishing them to top-group

                    # print "=== level < 0", each_sg.name

                    # getting all the resources (of type: File, Page, Task) under this group:
                    group_res_cur = node_collection.find({
                        'member_of': {'$in': [file_gst._id, page_gst._id, task_gst._id]},
                        'group_set': {'$in': [each_sg._id]} })

                    # iterating over each resource under this group:
                    for each_group_res in group_res_cur:

                        group_set = each_group_res.group_set

                        # removing current sub-groups _id from group_set:
                        if each_sg._id in group_set:
                            group_set.pop(group_set.index(each_sg._id))

                        # adding top-group's _id in group_set:
                        if top_group_obj._id not in group_set:
                            group_set.append(top_group_obj._id)

                        each_group_res.group_set = group_set
                        each_group_res.status = u'PUBLISHED'
                        each_group_res.save()

                    # updating current sub-group with above stated changes:
                    node_collection.collection.update({
                        '_id': each_sg._id},
                        {'$set': {
                            'member_of': [group_gst._id],
                            'status': u'DELETED',
                            'moderation_level': -1,
                            'post_node': []
                            }
                        }, upsert=False, multi=False )

                    # updating last_sg variables
                    last_sg_id = each_sg._id
                    last_sg_moderation_level = each_sg.moderation_level

        # print "out of for === group_moderation_level", group_moderation_level

        # despite of above looping and iterations, group_moderation_level is > 0 \
        # i.e: new moderated sub-group/s need to be created. (moderation level of parent group has raised).
        if group_moderation_level >= 0:

            # range(0, 0) will results: [] and range(0, 1) will results: [0]
            # hence, group_moderation_level is need to be increased by 1
            for each_sg_iter in range(0, group_moderation_level+1):

                # print each_sg_iter, " === each_sg_iter", last_sg_id
                result = self.add_moderation_level(last_sg_id, sg_member_of=sg_member_of)
                # result is tuple of (bool, newly-created-sub-group-obj)

                if result[0]:
                    last_sg_id = result[1]._id
                    # print " === new group created: ", result[0].name

                else:
                    # if result is False, means sub-group is not created.
                    # In this case, there is no point to go ahead and create subsequent sub-group.
                    break

# --- END of class CreateModeratedGroup ---
# -----------------------------------------



class CreateEventGroup(CreateModeratedGroup):
    """
        Creates moderated event sub-groups.
        Instantiate with request.
    """

    def __init__(self, request):
        super(CreateEventGroup, self).__init__(request)
        self.request = request

    def set_event_and_enrollment_dates(self, request, group_id, parent_group_obj):
        '''
        Sets Start-Date, End-Date, Start-Enroll-Date, End-Enroll-Date
        - Takes required dates from request object.
        - Returns tuple: (True/False, top_group_object/error)
        '''

        # retrieves node_id. means it's edit operation of existing group.
        # group_obj.prior_node.append(parent_group_obj._id)
        # group_obj.save()

        # if "ProgramEventGroup" not in group_obj.member_of_names_list:
        #     node_collection.collection.update({'_id': group_obj._id},
        #         {'$push': {'member_of': ObjectId(programevent_group_gst._id)}}, upsert=False, multi=False)
        #     group_obj.reload()
        try:
            group_obj = node_collection.one({'_id': ObjectId(group_id)})
            if parent_group_obj._id != group_obj._id:
                self.add_subgroup_to_parents_postnode(parent_group_obj._id, group_obj._id, "Event")
            start_date_val = self.request.POST.get('event_start_date','')
            if start_date_val:
                start_date_val = datetime.strptime(start_date_val, "%d/%m/%Y")
            end_date_val = self.request.POST.get('event_end_date','')
            if end_date_val:
                end_date_val = datetime.strptime(end_date_val, "%d/%m/%Y")

            start_enroll_val = self.request.POST.get('event_start_enroll_date','')
            if start_enroll_val:
                start_enroll_val = datetime.strptime(start_enroll_val, "%d/%m/%Y")

            end_enroll_val = self.request.POST.get('event_end_enroll_date','')
            if end_enroll_val:
                end_enroll_val = datetime.strptime(end_enroll_val, "%d/%m/%Y")

            start_date_AT = node_collection.one({'_type': "AttributeType", 'name': "start_time"})
            end_date_AT = node_collection.one({'_type': "AttributeType", 'name': "end_time"})

            start_enroll_AT = node_collection.one({'_type': "AttributeType", 'name': "start_enroll"})
            end_enroll_AT = node_collection.one({'_type': "AttributeType", 'name': "end_enroll"})

            create_gattribute(group_obj._id, start_date_AT, start_date_val)
            create_gattribute(group_obj._id, end_date_AT, end_date_val)
            create_gattribute(group_obj._id, start_enroll_AT, start_enroll_val)
            create_gattribute(group_obj._id, end_enroll_AT, end_enroll_val)

            return True, group_obj

        except Exception as e:
            # print "\n ", 'Cannot Set Dates to EventGroup.' + str(e)
            return False, 'Cannot Set Dates to EventGroup.' + str(e)


# --- END of class CreateEventGroup ---
# -----------------------------------------

class CreateProgramEventGroup(CreateEventGroup):
    """
        Creates ProgramEvent sub-groups.
        Instantiate with request.
    """

    def __init__(self, request):
        super(CreateProgramEventGroup, self).__init__(request)
        self.request = request

# --- END of class CreateProgramEventGroup ---
# -----------------------------------------

class CreateCourseEventGroup(CreateEventGroup):
    """
        Creates CourseEvent sub-groups.
        Instantiate with request.
    """
    def __init__(self, request):
        super(CreateCourseEventGroup, self).__init__(request)
        self.request = request
        self.user_id = request.user.id

        self.section_event_gst = node_collection.one({'_type': "GSystemType",
                                'name': "CourseSectionEvent"}, {"_id":1})
        self.subsection_event_gst = node_collection.one({'_type': "GSystemType",
                                'name': "CourseSubSectionEvent"}, {"_id":1})
        self.courseunit_event_gst = node_collection.one({'_type': "GSystemType",
                                'name': "CourseUnitEvent"}, {"_id": 1})

        self.base_unit_gst = node_collection.one({'_type': "GSystemType",
                                'name': "base_unit"}, {"_id": 1})
        self.announced_unit_gst = node_collection.one({'_type': "GSystemType",
                                'name': "announced_unit"}, {"_id": 1})
        self.lesson_gst = node_collection.one({'_type': "GSystemType",
                                'name': "lesson"}, {"_id": 1})

    def initialize_course_event_structure(self, request, group_obj, parent_group_obj):
        # After BaseCourseGroup impl, course_node_id is
        # same as group_id

        # course_node_id = request.POST.get('course_node_id', '')
        # if course_node_id:
        #     course_node = node_collection.one({'_id': ObjectId(course_node_id)})
        #     group_obj = node_collection.one({'_id': ObjectId(group_id)})
        #     if "Course" in course_node:
        #         rt_group_has_course_event = node_collection.one({'_type': "RelationType", 'name': "group_has_course_event"})
        #         create_grelation(group_obj._id, rt_group_has_course_event, course_node._id)
        #     self.ce_set_up(request, course_node, group_obj)
        self.ce_set_up(request, group_obj, parent_group_obj)

    def ce_set_up(self, request, new_course_obj, existing_course_obj):
        """
            Will build into Recursive function
            To fetch from Course'collection_set
            and build new GSystem for CourseEventGroup

            existing_course_obj is course existing_course_obj
            new_course_obj is CourseEvent existing_course_obj

        """
        try:
            if not new_course_obj.content:
                new_course_obj.content = existing_course_obj.content
                # No longer using field content_org
                # new_course_obj.content_org = existing_course_obj.content_org
                new_course_obj.save()

            self.update_raw_material_group_set(existing_course_obj, new_course_obj)
            self.call_setup(request, existing_course_obj, new_course_obj, new_course_obj)
            new_course_obj = get_all_iframes_of_unit(new_course_obj, request.META['HTTP_HOST'])
            return True

        except Exception as e:

            print e, "CourseEventGroup structure setup Error"

    def update_raw_material_group_set(self,old_group_obj, new_group_obj):
        # Fetch all files from Raw-Material using tag 'raw@material'
        # rm_files_cur = node_collection.find({'tags': 'raw@material', 'member_of': file_gst._id, 'group_set': old_group_obj._id})

        # June 17 2016. Importing files uploaded by user 'administrator' in old_group_obj
        # administrator_user = User.objects.get(username='administrator')
        # Commented fetching 'administrator_user '

        # raw_material_fetch_query = {'group_set': old_group_obj._id,
        #  '$or':[{'tags': 'raw@material'}, {'created_by': administrator_user.id}]}
        raw_material_fetch_query = {'group_set': old_group_obj._id,
         'tags': 'raw@material'}

        if "announced_unit" in new_group_obj.member_of_names_list:
            asset_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Asset'})
            raw_material_fetch_query.update({'member_of': asset_gst._id})
        else:
            raw_material_fetch_query.update({'member_of': file_gst._id})

        rm_files_cur = node_collection.find(raw_material_fetch_query)
        if rm_files_cur.count():
            for each_rm_file in rm_files_cur:
                each_rm_file.group_set.append(new_group_obj._id)
                if self.user_id not in each_rm_file.contributors:
                    each_rm_file.contributors.append(self.user_id)
                each_rm_file.modified_by = self.user_id
                each_rm_file.save(groupid=new_group_obj._id)


    def create_corresponding_gsystem(self,base_gsystem,gs_under_coll_set_of_obj, group_obj):
        '''
        Depricated this method. katkamrachana - 02June2017
        'replicate_resource' will be used for resources and hierarchy nodes.
        '''
        try:
            user_id = base_gsystem.created_by
            new_gsystem = create_clone(user_id, base_gsystem, group_obj._id)
            base_gsystem_mem_list = base_gsystem.member_of_names_list
            if any(base_gs_mem in ["CourseSection", "CourseSectionEvent"] for base_gs_mem in base_gsystem_mem_list):
                gst_node = self.section_event_gst
            if any(base_gs_mem in ["CourseSubSection", "CourseSubSectionEvent"] for base_gs_mem in base_gsystem_mem_list):
                gst_node = self.subsection_event_gst
            if any(base_gs_mem in ["CourseUnit", "CourseUnitEvent"] for base_gs_mem in base_gsystem_mem_list):
                gst_node = self.courseunit_event_gst
            if any(base_gs_mem in ["lesson"] for base_gs_mem in base_gsystem_mem_list):
                gst_node = self.lesson_gst

            # new_gsystem = node_collection.collection.GSystem()
            # new_gsystem.name = unicode(gs_name)
            # if gs_member_of == "CourseSection" or gs_member_of == "CourseSectionEvent":
            #     gst_node = self.section_event_gst
            # elif gs_member_of == "CourseSubSection" or gs_member_of == "CourseSubSectionEvent":
            #     gst_node = self.subsection_event_gst
            # elif gs_member_of == "CourseUnit" or gs_member_of == "CourseUnitEvent":
            #     gst_node = self.courseunit_event_gst
            # elif gs_member_of == "lesson" or gs_member_of == "lesson":
            #     gst_node = self.lesson_gst
            # new_gsystem.modified_by = int(self.user_id)
            # new_gsystem.save()
            new_gsystem.member_of.append(gst_node._id)
            new_gsystem.group_set.append(group_obj._id)
            gs_under_coll_set_of_obj.collection_set.append(new_gsystem._id)
            gs_under_coll_set_of_obj.save()
            new_gsystem.prior_node.append(gs_under_coll_set_of_obj._id)
            new_gsystem.save()
            return new_gsystem
        except Exception as e:
            # print e
            return False

    def call_setup(self, request, node, prior_node_obj, group_obj):
        if node.collection_set:
            try:
                for each_res in node.collection_set:
                    gst_node_id = None
                    each_res_node = node_collection.one({'_id': ObjectId(each_res)})
                    each_res_node_mem_list = each_res_node.member_of_names_list
                    if any(base_gs_mem in ["CourseSection", "CourseSectionEvent"] for base_gs_mem in each_res_node_mem_list):
                        gst_node_id = self.section_event_gst._id
                    if any(base_gs_mem in ["CourseSubSection", "CourseSubSectionEvent"] for base_gs_mem in each_res_node_mem_list):
                        gst_node_id = self.subsection_event_gst._id
                    if any(base_gs_mem in ["CourseUnit", "CourseUnitEvent"] for base_gs_mem in each_res_node_mem_list):
                        gst_node_id = self.courseunit_event_gst._id
                    if any(base_gs_mem in ["lesson"] for base_gs_mem in each_res_node_mem_list):
                        gst_node_id = self.lesson_gst._id

                    new_res = replicate_resource(request, each_res_node, 
                        group_obj._id, mem_of_node_id=gst_node_id)
                    # new_res = self.replicate_resource(request, each_res_node, group_obj)
                    prior_node_obj.collection_set.append(new_res._id)
                    new_res.prior_node.append(prior_node_obj._id)
                    new_res.save()
                    # below code changes the group_set of resources
                    # i.e cross-publication
                    # each_res_node.group_set.append(group_obj._id)
                    # prior_node_obj.collection_set.append(each_res_node._id)
                    # node.save()
                    prior_node_obj.save()
                    if each_res_node.collection_set:
                        self.call_setup(request, each_res_node, new_res, group_obj)
                    # else:
                    #     for each in node.collection_set:
                    #         each_node = node_collection.one({'_id': ObjectId(each)})
                    #         if each_node:
                    #             # name_arg = each_node.name
                    #             # member_of_name_str = each_node.member_of_names_list[0]
                    #             new_node = self.create_corresponding_gsystem(each_node, prior_node_obj, group_obj)
                    #             self.call_setup(request, each_node, new_node, group_obj)
            except Exception as call_set_err:
                print "\n !!!Error while creating Course Structure!!!", call_set_err
                pass


# --- END of class CreateCourseEventGroup ---
# -----------------------------------------


class GroupCreateEditHandler(View):
    """
    Class to handle create/edit group requests.
    This class should handle all the types ofgroup create/edit requests.
    Currently it supports the functionality for following types of groups:
        - Normal Groups
        - Moderating Groups
        - Pending:
            -- Sub Groups
            -- CourseEvent Group
            -- ProgramEvent Group
    """

    @method_decorator(login_required)
    @method_decorator(staff_required)
    @method_decorator(get_execution_time)
    def get(self, request, group_id, action):
        """
        Catering GET request of group's create/edit.
        Render's to create_group template.
        """
        try:
            group_id = ObjectId(group_id)
        except:
            group_name, group_id = get_group_name_id(group_id)
        group_obj = None
        nodes_list = []
        logo_img_node = None
        parent_obj_partner = None
        subgroup_flag = request.GET.get('subgroup','')
        node_edit_flag = request.GET.get('node_edit',False)
        if not isinstance(node_edit_flag, bool):
            node_edit_flag = eval(node_edit_flag)
        # print "\n node_edit_flag ==== ",type(node_edit_flag)
        partnergroup_flag = request.GET.get('partnergroup','')
        if partnergroup_flag:
            partnergroup_flag = eval(partnergroup_flag)

        if action == "edit":  # to edit existing group

            group_obj = get_group_name_id(group_id, get_obj=True)
            if partnergroup_flag:
                parent_id = group_obj.prior_node[0]
                parent_obj_partner = get_group_name_id(parent_id, get_obj=True)
                # print "\n\n parent_group_obj", parent_obj_partner

            # as group edit will not have provision to change name field.
            # there is no need to send nodes_list while group edit.

        elif action == "create":  # to create new group

            available_nodes = node_collection.find({'_type': u'Group'}, {'name': 1, '_id': 0})
            # making list of group names (to check uniqueness of the group):
            nodes_list = [str(g_obj.name.strip().lower()) for g_obj in available_nodes]
            if partnergroup_flag:
                parent_obj_partner = get_group_name_id(group_id, get_obj=True)

            # print nodes_list
        # why following logic exists? Do we need so?
        # if group_obj.status == u"DRAFT":
        #     group_obj, ver = get_page(request, group_obj)
        #     group_obj.get_neighbourhood(group_obj.member_of)

        title = action + ' Group'

        # In the case of need old group edit interface (node_edit_base.html), we can simply replace:
        # "ndf/create_group.html" with "ndf/edit_group.html"
        template = "ndf/create_group.html"
        if node_edit_flag:
            # Coming for page-edit interface (Collection, Metadata, Help)
            template = "ndf/edit_group.html"
        if subgroup_flag:
            subgroup_flag = eval(subgroup_flag)
        if partnergroup_flag:
            template = "ndf/create_partner.html"
            if group_obj:
                # logo_img_node, grel_id = get_relation_value(group_obj._id,'has_profile_pic')
                grel_dict = get_relation_value(group_obj._id, "has_profile_pic")
                is_cursor = grel_dict.get("cursor",False)
                if not is_cursor:
                    logo_img_node = grel_dict.get("grel_node")
                    grel_id = grel_dict.get("grel_id")

                group_obj.get_neighbourhood(group_obj.member_of)

        # print "\n\ngroup_obj",group_obj.name,"----",group_obj.relation_set
        return render_to_response(template,
                                    {
                                        'node': group_obj, 'title': title,
                                        'nodes_list': nodes_list,
                                        'groupid': group_id, 'group_id': group_id,
                                        'subgroup_flag':subgroup_flag,
                                        'parent_obj_partner':parent_obj_partner,
                                        'partnergroup_flag':partnergroup_flag,
                                        'logo_img_node': logo_img_node
                                        # 'appId':app._id, # 'is_auth_node':is_auth_node
                                      }, context_instance=RequestContext(request))
    # --- END of get() ---

    @method_decorator(login_required)
    @method_decorator(staff_required)
    @method_decorator(get_execution_time)
    def post(self, request, group_id, action):
        '''
        To handle post request of group form.
        To save edited or newly-created group's data.
        '''
        # getting group's object:
        group_obj = get_group_name_id(group_id, get_obj=True)

        # getting field values from form:
        group_name = request.POST.get('name', '').strip()  # hidden-form-field
        node_id = request.POST.get('node_id', '').strip()  # hidden-form-field
        edit_policy = request.POST.get('edit_policy', '')
        group_page_edit = request.POST.get('group_page_edit', False)
        if not isinstance(group_page_edit, bool):
            group_page_edit = eval(group_page_edit)

        subgroup_flag = request.POST.get('subgroup', '')
        partnergroup_flag = request.POST.get('partnergroup_flag', '')
        url_name = 'groupchange'

        # raise Exception(partnergroup_flag)
        if subgroup_flag:
            subgroup_flag = eval(subgroup_flag)
            parent_group_id = group_id
        else:
            parent_group_id = None

        if partnergroup_flag:
            partnergroup_flag = eval(partnergroup_flag)
        # check if group's editing policy is already 'EDITABLE_MODERATED' or
        # it was not and now it's changed to 'EDITABLE_MODERATED' or vice-versa.
        if (edit_policy == "EDITABLE_MODERATED") or (group_obj.edit_policy == "EDITABLE_MODERATED"):

            moderation_level = request.POST.get('moderation_level', '')
            # print "~~~~~~~ ", moderation_level

            # instantiate moderated group
            mod_group = CreateModeratedGroup(request)

            # calling method to create new group
            result = mod_group.create_edit_moderated_group(group_name, moderation_level, "ModeratingGroup", top_mod_groups_parent=parent_group_id, node_id=node_id)

            # print "=== result: ", result

        elif subgroup_flag:
            sub_group = CreateSubGroup(request)
            result = sub_group.create_subgroup(parent_group_id, group_name, "subgroup")
        else:
            # instantiate regular group
            group = CreateGroup(request)

            # calling method to create new group
            result = group.create_group(group_name, node_id=node_id)

        # print result[0], "\n=== result : "
        if result[0]:
            # operation success: redirect to group-detail page
            group_obj = result[1]
            group_name = group_obj.name
            # url_name = 'groupchange'
            if group_page_edit:
                is_node_changed=get_node_common_fields(request, group_obj, group_id, gst_group)
                group_obj.save(is_changed=is_node_changed)
                group_obj.save()

            elif not partnergroup_flag:
                if request.POST.get('apps_to_set', ''):
                    app_selection(request, group_obj._id)

            else:
                group_obj.member_of = [partner_group_gst._id]
                group_obj.save()
                partner_grp_result = sub_group.set_partnergroup(request, group_obj)
                sub_group.set_logo(request, group_obj, logo_rt = "has_profile_pic")
        else:
            if not partnergroup_flag:
                # operation fail: redirect to group-listing
                group_name = 'home'
                url_name = 'group'
            else:
                partner_grp_result = sub_group.set_partnergroup(request, group_obj)
                sub_group.set_logo(request, group_obj, logo_rt = "has_profile_pic")
                # print "-------------------------------------------------",group_obj
        return HttpResponseRedirect( reverse( url_name, kwargs={'group_id': group_name} ) )
# ===END of class EditGroup() ===
# -----------------------------------------

class EventGroupCreateEditHandler(View):
    """
    Class to handle create/edit group requests.
    Currently it supports the functionality for following types of groups:
        - CourseEvent Group
        - ProgramEvent Group
    """
    @method_decorator(login_required)
    @method_decorator(staff_required)
    @method_decorator(get_execution_time)
    def get(self, request, group_id, action, sg_type):
        """
        Catering GET request of group's create/edit.
        Render's to create_group template.
        """
        try:
            group_id = ObjectId(group_id)
        except:
            group_name, group_id = get_group_name_id(group_id)
        # course_node_id = request.GET.get('cnode_id', '')
        group_obj = None
        nodes_list = []
        spl_group_type = sg_type
        logo_img_node = None
        gst_module_name, gst_module_id = GSystemType.get_gst_name_id('Module')
        modules = GSystem.query_list('home', 'Module', request.user.id)
        # spl_group_type = request.GET.get('sg_type','')
        # print "\n\n spl_group_type", spl_group_type
        title = action + ' ' + spl_group_type
        context_variables = {
            'title': title, 'modules': modules,
            'spl_group_type': spl_group_type,
            'groupid': group_id, 'group_id': group_id,
            'nodes_list': nodes_list
          }

        if action == "edit":  # to edit existing group

            group_obj = get_group_name_id(group_id, get_obj=True)
            grel_id = None

            # logo_img_node_grel_id = get_relation_value(group_obj._id,'has_profile_pic')
            # if logo_img_node_grel_id:
            #     logo_img_node = logo_img_node_grel_id[0]
            #     grel_id = logo_img_node_grel_id[1]

            grel_dict = get_relation_value(group_obj._id, "has_profile_pic")
            is_cursor = grel_dict.get("cursor",False)
            if not is_cursor:
                logo_img_node = grel_dict.get("grel_node")
                grel_id = grel_dict.get("grel_id")

            # get all modules which are parent's of this unit/group
            parent_modules = node_collection.find({
                    '_type': 'GSystem',
                    'member_of': gst_module_id,
                    'collection_set': {'$in': [group_id]}
                })
            context_variables.update({'module_val_list': [str(pm._id) for pm in parent_modules],
                'node': group_obj, 'logo_img_node':logo_img_node})

            # as group edit will not have provision to change name field.
            # there is no need to send nodes_list while group edit.

        elif action == "create":  # to create new group

            available_nodes = node_collection.find({'_type': u'Group'}, {'name': 1, '_id': 0})

            # making list of group names (to check uniqueness of the group):
            nodes_list = [str(g_obj.name.strip().lower()) for g_obj in available_nodes]

            context_variables.update({'nodes_list': nodes_list})

        # In the case of need, we can simply replace:
        # "ndf/create_group.html" with "ndf/edit_group.html"
        return render_to_response("ndf/create_event_group.html",RequestContext(request, context_variables))
    # --- END of get() ---

    @method_decorator(login_required)
    @method_decorator(staff_required)
    @method_decorator(get_execution_time)
    def post(self, request, group_id, action, sg_type):
        '''
        To handle post request of group form.
        To save edited or newly-created group's data.
        '''
        parent_group_obj = get_group_name_id(group_id, get_obj=True)

        # getting field values from form:
        group_name = request.POST.get('name', '').strip()  # hidden-form-field
        node_id = request.POST.get('node_id', '').strip()  # hidden-form-field
        edit_policy = request.POST.get('edit_policy', '')
        # course_node_id = request.POST.get('course_node_id', '')
        # check if group's editing policy is already 'EDITABLE_MODERATED' or
        # it was not and now it's changed to 'EDITABLE_MODERATED' or vice-versa.
        # import ipdb; ipdb.set_trace()
        if (edit_policy == "EDITABLE_MODERATED") or (parent_group_obj.edit_policy == "EDITABLE_MODERATED"):

            moderation_level = request.POST.get('moderation_level', '')
            # instantiate moderated group
            if sg_type == "ProgramEventGroup":
                mod_group = CreateProgramEventGroup(request)
            elif sg_type == "CourseEventGroup":
                moderation_level = -1
                mod_group = CreateCourseEventGroup(request)

            # calling method to create new group
            result = mod_group.create_edit_moderated_group(group_name, moderation_level, sg_type, node_id=node_id, perform_checks=False)
        if result[0]:
            # operation success: create ATs
            group_obj = result[1]
            group_obj.fill_node_values(request)
            language = request.POST.get('language', ('en', 'English'))
            if language:
                language_val = get_language_tuple(unicode(language))
                group_obj.language = language_val

            date_result = mod_group.set_event_and_enrollment_dates(request, group_obj._id, parent_group_obj)
            if sg_type == "CourseEventGroup":
                if ("base_unit" in parent_group_obj.member_of_names_list or 
                    "announced_unit" in parent_group_obj.member_of_names_list):
                    group_obj.member_of = [ObjectId(announced_unit_gst._id)]
                else:
                    group_obj.member_of = [ObjectId(courseevent_group_gst._id)]
                # group_obj.language = parent_group_obj.language
                if parent_group_obj.project_config:
                    group_obj.project_config = parent_group_obj.project_config
                group_obj.save()
                # modules
                module_val = request.POST.getlist('module', [])
                if module_val:
                    update_unit_in_modules(module_val, group_obj._id)

                if node_id:
                    return HttpResponseRedirect(reverse('groupchange',
                     kwargs={'group_id': group_name}))
            # to make PE/CE as sub groups of the grp from which it is created.
            # parent_group_obj.post_node.append(group_obj._id)
            # group_obj.prior_node.append(parent_group_obj._id)
            # group_obj.save()
            # parent_group_obj.save()
            if not node_id:
                if date_result[0]:
                    # Successfully had set dates to EventGroup
                    if sg_type == "CourseEventGroup":
                        mod_group.initialize_course_event_structure(request, group_obj, parent_group_obj)
                        # creating a new counter document for a user for a given course for the purpose of analytics

                        # counter_obj = Counter.get_counter_obj(userid, group_id)
                        # print "===========================", counter_obj

                        # auth_obj= node_collection.one({'_type':'Author','created_by':request.user.id})

                        # counter_obj = counter_collection.collection.Counter()
                        # counter_obj.fill_counter_values(
                        #                                 user_id=request.user.id,
                        #                                 auth_id=auth_obj._id,
                        #                                 group_id=group_obj._id,
                        #                                 is_group_member=True
                        #                             )
                        # counter_obj.save()

                    # elif sg_type == "ProgramEventGroup":
                        # mod_group.set_logo(request,group_obj,logo_rt = "has_logo")
                    # mod_group.set_logo(request,group_obj,logo_rt = "has_profile_pic")
                    mod_group.set_logo(request,group_obj,logo_rt = "has_banner_pic")
                    group_name = group_obj.name
                    if "announced_unit" in group_obj.member_of_names_list:
                        # check if base_unit is assigned to any module
                        gst_module_name, gst_module_id = GSystemType.get_gst_name_id('Module')
                        parent_modules = node_collection.find({
                            '_type': 'GSystem',
                            'member_of': gst_module_id,
                            'collection_set': {'$in': [parent_group_obj._id]}
                        })
                        for each_parent_module in parent_modules:
                            each_parent_module.collection_set.append(group_obj._id)
                            each_parent_module.save()
                        # check if base_unit has attr assigned
                        # Add attr  educationallevel_val and educationalsubject
                        educationalsubject_val = get_attribute_value(parent_group_obj._id,"educationalsubject")
                        educationallevel_val = get_attribute_value(parent_group_obj._id,"educationallevel")
                        # print "\n educationalsubject_val: ", educationalsubject_val
                        # print "\n educationallevel_val: ", educationallevel_val
                        if educationalsubject_val:
                            educationalsubject_at = node_collection.one({
                                '_type': 'AttributeType',
                                'name': "educationalsubject"
                            })
                            create_gattribute(group_obj._id, educationalsubject_at, unicode(educationalsubject_val))
                        if educationallevel_val:
                            educationallevel_at = node_collection.one({
                                '_type': 'AttributeType',
                                'name': "educationallevel"
                            })
                            create_gattribute(group_obj._id, educationallevel_at, unicode(educationallevel_val))
                        group_obj.reload()
                    url_name = 'groupchange'
                else:
                    # operation fail: redirect to group-listing
                    group_name = 'home'
                    url_name = 'group'
        else:
            # operation fail: redirect to group-listing
            group_name = 'home'
            url_name = 'group'
        return HttpResponseRedirect(reverse(url_name, kwargs={'group_id': group_name}))

# ===END of class EventGroupCreateEditHandler() ===
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
        #loop replaced by a list comprehension
        group_nodes=[group for group in cur_groups_user]

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
        #loop replaced by a list comprehension
        group_nodes=[group for group in cur_public]
      group_count = cur_public.count()

    return render_to_response("ndf/group.html",
                              {'title': title,
                               'appId':app._id, 'app_gst': group_gst,
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
                               'appId':app._id, 'app_gst': group_gst,
                               'group_nodes_count': group_count,
                               'groupid': group_id, 'group_id': group_id
                              }, context_instance=RequestContext(request))


# @login_required
# @get_execution_time
# def create_group(request, group_id):

#   try:
#       group_id = ObjectId(group_id)
#   except:
#       group_name, group_id = get_group_name_id(group_id)

#   if request.method == "POST":

#     cname = request.POST.get('name', "").strip()
#     edit_policy = request.POST.get('edit_policy', "")
#     group_type = request.POST.get('group_type', "")
#     moderation_level = request.POST.get('moderation_level', '1')

#     if request.POST.get('edit_policy', "") == "EDITABLE_MODERATED":

#         # instantiate moderated group
#         mod_group = CreateModeratedGroup(request)

#         # calling method to create new group
#         result = mod_group.create_edit_moderated_group(cname, moderation_level)

#     else:

#         # instantiate moderated group
#         group = CreateGroup(request)

#         # calling method to create new group
#         result = group.create_group(cname)

#     if result[0]:
#         colg = result[1]

#     # auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })

#     # has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })

#     shelves = []
#     shelf_list = {}

#     # if auth:
#     #   shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': has_shelf_RT._id })

#     #   if shelf:
#     #     for each in shelf:
#     #       shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)})
#     #       shelves.append(shelf_name)

#     #       shelf_list[shelf_name.name] = []
#     #       for ID in shelf_name.collection_set:
#     #         shelf_item = node_collection.one({'_id': ObjectId(ID) })
#     #         shelf_list[shelf_name.name].append(shelf_item.name)

#     #   else:
#     #     shelves = []

#     return render_to_response("ndf/groupdashboard.html",
#                                 {'groupobj': colg, 'appId': app._id, 'node': colg,
#                                   'user': request.user,
#                                   'groupid': colg._id, 'group_id': colg._id,
#                                   'shelf_list': shelf_list,'shelves': shelves
#                                 },context_instance=RequestContext(request))


#   # for rendering empty form page:
#   available_nodes = node_collection.find({'_type': u'Group'})
#   nodes_list = []
#   for each in available_nodes:
#       nodes_list.append(str((each.name).strip().lower()))
#   return render_to_response("ndf/create_group.html", {'groupid': group_id, 'appId': app._id, 'group_id': group_id, 'nodes_list': nodes_list},RequestContext(request))


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

  try:
    group_obj = ""
    # shelf_list = {}
    # shelves = []
    alternate_template = ""
    profile_pic_image = None
    list_of_unit_events = []
    all_blogs = None
    blog_pages = None
    user_blogs = None
    subgroups_cur = None
    old_profile_pics = []
    selected = request.GET.get('selected','')
    group_obj = get_group_name_id(group_id, get_obj=True)
    try:
        if 'tab_name' in group_obj.project_config and group_obj.project_config['tab_name'].lower() == "questions":
            if "announced_unit" in group_obj.member_of_names_list:
                if group_obj.collection_set:
                    lesson_id = group_obj.collection_set[0]
                    lesson_node = node_collection.one({'_id': ObjectId(lesson_id)})
                    activity_id = lesson_node.collection_set[0]
                return HttpResponseRedirect(reverse('activity_player_detail', kwargs={'group_id': group_id,
                    'lesson_id': lesson_id, 'activity_id': activity_id}))
    except Exception as e:
        pass

    if ("base_unit" in group_obj.member_of_names_list or
        "CourseEventGroup" in group_obj.member_of_names_list or
        "BaseCourseGroup" in group_obj.member_of_names_list or 
        "announced_unit" in group_obj.member_of_names_list):
        return HttpResponseRedirect(reverse('course_content', kwargs={'group_id': group_id}))

    if group_obj and group_obj.post_node:
        # subgroups_cur = node_collection.find({'_id': {'$in': group_obj.post_node}, 'edit_policy': {'$ne': "EDITABLE_MODERATED"},
        # now we are showing moderating group too:
        subgroups_cur = node_collection.find({
                '_type': u'Group',
                '_id': {'$in': group_obj.post_node},
                # 'member_of': {'$in': [group_gst._id]}, #Listing all types of sub groups
                '$or': [
                            {'created_by': request.user.id},
                            {'group_admin': request.user.id},
                            {'author_set': request.user.id},
                            {'group_type': 'PUBLIC'}
                        ]
                }).sort("last_update",-1)



    if not group_obj:
      group_obj=node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
      group_id=group_obj['_id']
    else:
      # group_obj=node_collection.one({'_id':ObjectId(group_id)})
      group_id = group_obj._id

      # getting the profile pic File object
      # profile_pic_image, grelation_node = get_relation_value(group_obj._id,"has_profile_pic")
      # profile_pic_image = get_relation_value(group_obj._id,"has_profile_pic")
      # if profile_pic_image:
      #   profile_pic_image =  profile_pic_image[0]

      grel_dict = get_relation_value(group_obj._id, "has_profile_pic")
      is_cursor = grel_dict.get("cursor",False)
      if not is_cursor:
          profile_pic_image = grel_dict.get("grel_node")
          # grel_id = grel_dict.get("grel_id")


      # for each in group_obj.relation_set:
      #     if "has_profile_pic" in each:
      #         profile_pic_image = node_collection.one(
      #             {'_type': "File", '_id': each["has_profile_pic"][0]}
      #         )
      #         break
    '''
    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })

    if auth:

      has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })

      shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': has_shelf_RT._id })
      shelf_list = {}

      if shelf:
        #a temp. variable which stores the lookup for append method
        shelves_append_temp=shelves.append
        for each in shelf:
          shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)})
          shelves_append_temp(shelf_name)

          shelf_list[shelf_name.name] = []
          #a temp. variable which stores the lookup for append method
          shelf_lst_shelfname_append=shelf_list[shelf_name.name].append
          for ID in shelf_name.collection_set:
            shelf_item = node_collection.one({'_id': ObjectId(ID) })
            shelf_lst_shelfname_append(shelf_item.name)

      else:
          shelves = []
    '''
  except Exception as e:
    print "\nError: ", e
    group_obj=node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
    group_id=group_obj['_id']
    pass

  # profile_pic_image, grelation_node = get_relation_value(group_obj._id,"has_profile_pic")
  # profile_pic_image = get_relation_value(group_obj._id,"has_profile_pic")
  # if profile_pic_image:
  #   profile_pic_image = profile_pic_image[0]
  grel_dict = get_relation_value(group_obj._id, "has_profile_pic")
  is_cursor = grel_dict.get("cursor",False)
  if not is_cursor:
      profile_pic_image = grel_dict.get("grel_node")
      # grel_id = grel_dict.get("grel_id")

  has_profile_pic_rt = node_collection.one({'_type': 'RelationType', 'name': unicode('has_profile_pic') })
  all_old_prof_pics = triple_collection.find({'_type': "GRelation", "subject": group_obj._id, 'relation_type': has_profile_pic_rt._id, 'status': u"DELETED"})
  if all_old_prof_pics:
    for each_grel in all_old_prof_pics:
      n = node_collection.one({'_id': ObjectId(each_grel.right_subject)})
      old_profile_pics.append(n)

  # Call to get_neighbourhood() is required for setting-up property_order_list
  # group_obj.get_neighbourhood(group_obj.member_of)
  course_structure_exists = False
  files_cur = None
  parent_groupid_of_pe = None
  list_of_sg_member_of = get_sg_member_of(group_obj._id)
  # print "\n\n list_of_sg_member_of", list_of_sg_member_of
  files_cur = None
  allow_to_join = ""
  sg_type = None
  course_collection_data = []
  if  u"ProgramEventGroup" in list_of_sg_member_of and u"ProgramEventGroup" not in group_obj.member_of_names_list:
      sg_type = "ProgramEventGroup"
      # files_cur = node_collection.find({'group_set': ObjectId(group_obj._id), '_type': "File"})
      parent_groupid_of_pe = node_collection.find_one({'_type':"Group","post_node": group_obj._id})
      if parent_groupid_of_pe:
        parent_groupid_of_pe = parent_groupid_of_pe._id

      alternate_template = "ndf/gprogram_event_group.html"
  if "CourseEventGroup" in group_obj.member_of_names_list:
      sg_type = "CourseEventGroup"
      alternate_template = "ndf/gcourse_event_group.html"
      # course_collection_data = get_collection(request,group_obj._id,group_obj._id)
      # course_collection_data = json.loads(course_collection_data.content)
  if 'Group' in group_obj.member_of_names_list:
    alternate_template = "ndf/lms.html"
  # The line below is commented in order to:
  #     Fetch files_cur - resources under moderation in groupdahsboard.html
  # if  u"ProgramEventGroup" not in group_obj.member_of_names_list:
  if "CourseEventGroup" in group_obj.member_of_names_list or u"ProgramEventGroup" in list_of_sg_member_of and u"ProgramEventGroup" not in group_obj.member_of_names_list:
      page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
      blogpage_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"})
      # files_cur = node_collection.find({'group_set': ObjectId(group_obj._id), '_type': "File"}).sort("last_update",-1)
      if group_obj.collection_set:
          course_structure_exists = True
      if request.user.id:
          all_blogs = node_collection.find({
                'member_of':page_gst._id,
                'type_of': blogpage_gst._id,
                'group_set': group_obj._id
            }).sort('created_at', -1)
          if all_blogs:
              blog_pages = all_blogs.clone()
              blog_pages = blog_pages.where("this.created_by!=" + str(request.user.id))
              user_blogs = all_blogs.where("this.created_by==" + str(request.user.id))
      start_enrollment_date = get_attribute_value(group_obj._id,"start_enroll")
      # if 'start_enroll' in group_obj:
      #     if group_obj.start_enroll:
      #         start_enrollment_date = group_obj.start_enroll
      #         # print "\n\nstart_enrollment_date", start_enrollment_dates
      if start_enrollment_date:
        start_enrollment_date = start_enrollment_date.date()
        curr_date_time = datetime.now().date()
        if start_enrollment_date > curr_date_time:
            allow_to_join = "Forthcoming"
        else:
            allow_to_join = "Open"

      last_enrollment_date = get_attribute_value(group_obj._id,"end_enroll")
      # if 'end_enroll' in group_obj:
      #     if group_obj.end_enroll:
      #         last_enrollment_date = group_obj.end_enroll
      if last_enrollment_date:
        last_enrollment_date = last_enrollment_date.date()
        curr_date_time = datetime.now().date()
        if last_enrollment_date < curr_date_time:
            allow_to_join = "Closed"
        else:
            allow_to_join = "Open"
  if group_obj.edit_policy == "EDITABLE_MODERATED":# and group_obj._type != "Group":
      files_cur = node_collection.find({'group_set': ObjectId(group_obj._id), '_type': {'$in': ["File","GSystem"]}})
  '''
  property_order_list = []
  if "group_of" in group_obj:
    if group_obj['group_of']:
      college = node_collection.one({'_type': "GSystemType", 'name': "College"}, {'_id': 1})

      if college:
        if college._id in group_obj['group_of'][0]['member_of']:
          alternate_template = "ndf/college_group_details.html"

      property_order_list = get_property_order_with_value(group_obj['group_of'][0])

  annotations = json.dumps(group_obj.annotations)
  '''
  default_template = "ndf/groupdashboard.html"
  # print "\n\n blog_pages.count------",blog_pages
  if alternate_template:
    return HttpResponseRedirect( reverse('course_content', kwargs={"group_id": group_id}) )
  else:
    return render_to_response([alternate_template,default_template] ,{'node': group_obj, 'groupid':group_id,
                                                       'group_id':group_id, 'user':request.user,
                                                       # 'shelf_list': shelf_list,
                                                       'list_of_unit_events': list_of_unit_events,
                                                       'blog_pages':blog_pages,
                                                       'user_blogs': user_blogs,
                                                       'selected': selected,
                                                       'files_cur': files_cur,
                                                       'sg_type': sg_type,
                                                       'course_collection_data':course_collection_data,
                                                       'parent_groupid_of_pe':parent_groupid_of_pe,
                                                       'course_structure_exists':course_structure_exists,
                                                       'allow_to_join': allow_to_join,
                                                       'appId':app._id, 'app_gst': group_gst,
                                                       'subgroups_cur':subgroups_cur,
                                                       # 'annotations' : annotations, 'shelves': shelves,
                                                       'prof_pic_obj': profile_pic_image,
                                                       'old_profile_pics':old_profile_pics,
                                                       'group_obj': group_obj,
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


@login_required
@get_execution_time
def app_selection(request, group_id):
    from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget

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
  from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget

  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)

  try:
    node = node_collection.one({"_id": ObjectId(node_id)})
    existing_grps = node.group_set

    if request.method == "POST":

      new_grps_list = request.POST.getlist("new_groups_list[]", "")
      resource_exists = False
      resource_exists_in_grps = []
      response_dict = {'success': False, 'message': ''}
      #a temp. variable which stores the lookup for append method
      resource_exists_in_grps_append_temp = resource_exists_in_grps.append
      new_grps_list_distinct = [ObjectId(item) for item in new_grps_list if ObjectId(item) not in existing_grps]
      # print "\nnew_grps_list_distinct",new_grps_list_distinct
      if new_grps_list_distinct:
        for each_new_grp in new_grps_list_distinct:
          if each_new_grp:
            grp = node_collection.find({'name': node.name, "group_set": ObjectId(each_new_grp), "member_of":ObjectId(node.member_of[0])})
            if grp.count() > 0:
              resource_exists = True
              resource_exists_in_grps_append_temp(unicode(each_new_grp))

        response_dict["resource_exists_in_grps"] = resource_exists_in_grps

      if not resource_exists:
        # new_grps_list_all = [ObjectId(item) for item in new_grps_list]

        new_grps_list_all = []

        for each_group_id in new_grps_list:
            each_group_obj = node_collection.one({'_id': ObjectId(each_group_id)})

            if each_group_obj.moderation_level > -1:
                # means group is moderated one.
                each_result_dict = moderation_status(request, each_group_obj._id, node._id, get_only_response_dict=True)
                if each_result_dict['is_under_moderation']:
                    # means, this node already exists in one of -
                    # - the underlying mod group of this (each_group_obj).
                    pass
                else:
                    each_group_set = get_moderator_group_set(existing_grps, each_group_id, get_details=False)
                    merge_group_set = set(each_group_set + new_grps_list_all)
                    new_grps_list_all = list(merge_group_set)
                    t = create_moderator_task(request, node.group_set[-1], node._id,on_upload=True)

            else:
                if each_group_id not in new_grps_list_all:
                    new_grps_list_all.append(ObjectId(each_group_id))


        node.group_set = list(set(new_grps_list_all))
        node.save()
        # node_collection.collection.update({'_id': node._id}, {'$set': {'group_set': new_grps_list_all}}, upsert=False, multi=False)
        # node.reload()
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
      # for each in get_all_user_groups():
      #   all_user_groups.append(each.name)
      #loop replaced by a list comprehension
      top_partners_list = ["State Partners", "Individual Partners", "Institutional Partners"]
      all_user_groups = [each.name for each in get_all_user_groups()]
      if not request.user.is_superuser:
          all_user_groups.append('home')
          # exclude home group in listing if not SU
      all_user_groups.append('Trash')
      all_user_groups.extend(top_partners_list)

      st = node_collection.find({
            '$and': [
                        {'_type': 'Group'},
                        {'$or':[
                                {'author_set': {'$in':[user_id]}},
                                {'group_admin': {'$in':[user_id]}}
                            ]
                        },
                        {'name':{'$nin':all_user_groups}},
                        {'member_of': {'$in': [group_gst._id]}},
                        {'status': u'PUBLISHED'}
                      # ,{'edit_policy': {'$ne': "EDITABLE_MODERATED"}}
                    ]
                }).sort('name',-1)
      # st = node_collection.find({'$and': [{'_type': 'Group'}, {'author_set': {'$in':[user_id]}},
      #                                     {'name':{'$nin':all_user_groups}},
      #                                     {'edit_policy': {'$ne': "EDITABLE_MODERATED"}}
      #                                    ]
      #                           })
      # for each in node.group_set:
      #   coll_obj_list.append(node_collection.one({'_id': each}))
      #loop replaced by a list comprehension

      # coll_obj_list=[node_collection.one({'_id': each}) for each in node.group_set ]



      for each_coll_obj_id in node.group_set:
        each_coll_obj = node_collection.one({'_id': ObjectId(each_coll_obj_id)})
        if each_coll_obj and moderating_group_gst._id not in each_coll_obj.member_of:
            coll_obj_list.append(each_coll_obj)
        elif each_coll_obj:

            try:
                mod_group_instance = CreateModeratedGroup(request)
                is_top_group, top_group_obj = mod_group_instance.get_top_group_of_hierarchy(each_coll_obj_id)
                coll_obj_list.append(top_group_obj)
            except Exception as d:
                print d

      data_list = set_drawer_widget(st, coll_obj_list, 'moderation_level')
      # print "\n\n data_list",data_list
      return HttpResponse(json.dumps(data_list))

  except Exception as e:
    print "Exception in switch_group: "+str(e)
    return HttpResponse("Failure")


@login_required
@get_execution_time
def cross_publish(request, group_id):
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    gstaff_access = check_is_gstaff(group_id,request.user)
    if request.method == "GET":
        query = {'_type': 'Group', 'status': u'PUBLISHED',
                '$or': [
                            {'access_policy': u"PUBLIC"},
                            {'$and': [
                                    {'access_policy': u"PRIVATE"},
                                    {'created_by': request.user.id}
                                ]
                            }
                        ],
                }

        if gstaff_access:
            query.update({'group_type': {'$in': [u'PUBLIC', u'PRIVATE']}})
        else:
            query.update({'name': {'$nin': GSTUDIO_DEFAULT_GROUPS_LIST},
                        'group_type': u'PUBLIC'})
        group_cur = node_collection.find(query,{ '_id': 1, 'name':1, 'altnames':1}).sort('last_update', -1)
        response_dict = {'groups_cur': group_cur}
        return HttpResponse(json.dumps(list(group_cur), cls=NodeJSONEncoder))
    elif request.method == "POST":
        success_flag = True
        target_group_ids = request.POST.getlist("group_ids[]", None)

        # print "\ntarget_group_ids:", target_group_ids
        if target_group_ids:
            try:
                target_group_ids = map(ObjectId, list(set(target_group_ids)))
                node_id = request.POST.get("node_id", None)
                # remove_from_curr_grp_flag = eval((request.POST.get("remove_from_curr_grp_flag", "False")).title())
                publish_children = eval(request.POST.get("publishChildren", False))
                node_obj = Node.get_node_by_id(node_id)
                if publish_children:
                    # Exclusive action for Asset
                    if u"Asset" in node_obj.member_of_names_list:
                        asset_content_tr = node_obj.get_relation("has_assetcontent")
                        child_ids = [each_tr.right_subject for each_tr in asset_content_tr]
                    else:
                        child_ids = node_obj.collection_set
                    child_cur =  node_collection.find({'_id': {'$in': child_ids}})
                    for each_child in child_cur:
                        # each_child.group_set = add_to_list(each_child.group_set, target_group_ids)
                        each_child.group_set = target_group_ids
                        each_child.save()
                    # if remove_from_curr_grp_flag:
                    #     for each_child in child_cur:
                    #         # each_child.group_set = add_to_list(each_child.group_set, target_group_ids)
                    #         each_child.group_set = filter(lambda x: x != group_id, target_group_ids)
                    #         each_child.save()
                    # else:
                    #     for each_child in child_cur:
                    #         # each_child.group_set = add_to_list(each_child.group_set, target_group_ids)
                    #         each_child.group_set = target_group_ids
                    #         each_child.save()
                # node_obj.group_set = add_to_list(node_obj.group_set, target_group_ids)
                node_obj.group_set = target_group_ids
                # if remove_from_curr_grp_flag:
                #     node_obj.group_set = filter(lambda x: x != group_id, target_group_ids)
                # else:
                #     node_obj.group_set = target_group_ids
                node_obj.save()
            except Exception as e:
                print "\nError occurred in Cross-Publish", e
                success_flag = False
                pass

        return HttpResponse(json.dumps(target_group_ids, cls=NodeJSONEncoder))



@login_required
@get_execution_time
def publish_group(request,group_id,node):

    group_obj = get_group_name_id(group_id, get_obj=True)
    profile_pic_image = None

    if group_obj:
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
    node.save(groupid=group_id)

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
          colg.save(groupid=group_id)
          #save subgroup_id in the collection_set of parent group
          group_ins.collection_set.append(colg._id)
          #group_ins.post_node.append(colg._id)
          group_ins.save(groupid=group_id)

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
              Mod_colg.save(groupid=group_id)

              colg.post_node.append(Mod_colg._id)
              colg.save(groupid=group_id)
          auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
          has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })
          shelves = []
          shelf_list = {}

          if auth:
              shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': has_shelf_RT._id })

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



@login_required
@get_execution_time
def upload_using_save_file(request,group_id):
    from gnowsys_ndf.ndf.views.file import save_file
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    group_obj = node_collection.one({'_id': ObjectId(group_id)})
    title = request.POST.get('context_name','')
    sel_topic = request.POST.get('topic_list','')
    
    usrid = request.user.id
    name  = request.POST.get('name')
    # print "\n\n\nusrid",usrid
    # # url_name = "/"+str(group_id)
    # for key,value in request.FILES.items():
    #     fname=unicode(value.__dict__['_name'])
    #     # print "key=",key,"value=",value,"fname=",fname
    #     fileobj,fs = save_file(value,fname,usrid,group_id, "", "", username=unicode(request.user.username), access_policy=group_obj.access_policy, count=0, first_object="", oid=True)
    #     file_obj = node_collection.find_one({'_id': ObjectId(fileobj)})
    #     if file_obj:
    #         #set interaction-settings
    #         discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
    #         create_gattribute(file_obj._id, discussion_enable_at, True)
    #         return_status = create_thread_for_node(request,group_obj._id, file_obj)

    #     # if file_obj:
    #     #     url_name = "/"+str(group_id)+"/#gallery-tab"

    from gnowsys_ndf.ndf.views.filehive import write_files
    is_user_gstaff = check_is_gstaff(group_obj._id, request.user)
    content_org = request.POST.get('content_org', '')
    uploaded_files = request.FILES.getlist('filehive', [])
    # gs_obj_list = write_files(request, group_id)
    # fileobj_list = write_files(request, group_id)
    # fileobj_id = fileobj_list[0]['_id']
    fileobj_list = write_files(request, group_id,unique_gs_per_file=False)
    # fileobj_list = write_files(request, group_id)
    fileobj_id = fileobj_list[0]['_id']
    file_node = node_collection.one({'_id': ObjectId(fileobj_id) })

    # if GSTUDIO_FILE_UPLOAD_FORM == 'detail' and GSTUDIO_SITE_NAME == "NROER" and title != "raw material" and title != "gallery":
    if GSTUDIO_FILE_UPLOAD_FORM == 'detail' and title != "raw material" and title != "gallery":
        if request.POST:
            # mtitle = request.POST.get("docTitle", "")
            # userid = request.POST.get("user", "")
            language = request.POST.get("lan", "")
            # img_type = request.POST.get("type", "")
            # topic_file = request.POST.get("type", "")
            # doc = request.POST.get("doc", "")
            usrname = request.user.username
            page_url = request.POST.get("page_url", "")
            access_policy = request.POST.get("login-mode", '') # To add access policy(public or private) to file object
            tags = request.POST.get('tags', "")
            copyright = request.POST.get("Copyright", "")
            source = request.POST.get("Source", "")
            Audience = request.POST.getlist("audience", "")
            fileType = request.POST.get("FileType", "")
            Based_url = request.POST.get("based_url", "")
            co_contributors = request.POST.get("co_contributors", "")
            map_geojson_data = request.POST.get('map-geojson-data')
            subject = request.POST.get("Subject", "")
            level = request.POST.getlist("Level", "")
            content_org = request.POST.get('content_org', '')

            subject = '' if (subject=='< Not Sure >') else subject
            level = '' if (level=='< Not Sure >') else level

            if content_org:
                file_node.content_org = content_org

            if map_geojson_data:
                map_geojson_data = map_geojson_data + ","
                map_geojson_data = list(ast.literal_eval(map_geojson_data))
            else:
                map_geojson_data = []

            file_node.legal['copyright'] = unicode(copyright)

            file_node.location = map_geojson_data
            # file_node.save(groupid=group_id)
            if language:
                # fileobj.language = unicode(language)
                file_node.language = get_language_tuple(language)
            file_node.created_by = int(usrid)

            file_node.modified_by = int(usrid)
            if source:
                # create gattribute for file with source value
                source_AT = node_collection.one({'_type':'AttributeType','name':'source'})
                src = create_gattribute(ObjectId(file_node._id), source_AT, source)

            if Audience:
              # create gattribute for file with Audience value
                audience_AT = node_collection.one({'_type':'AttributeType','name':'audience'})
                aud = create_gattribute(file_node._id, audience_AT, Audience)

            if fileType:
              # create gattribute for file with 'educationaluse' value
                educationaluse_AT = node_collection.one({'_type':'AttributeType', 'name': 'educationaluse'})
                FType = create_gattribute(file_node._id, educationaluse_AT, fileType)

            if subject:
                # create gattribute for file with 'educationaluse' value
                subject_AT = node_collection.one({'_type':'AttributeType', 'name': 'educationalsubject'})
                sub = create_gattribute(file_node._id, subject_AT, subject)

            if level:
              # create gattribute for file with 'educationaluse' value
                educationallevel_AT = node_collection.one({'_type':'AttributeType', 'name': 'educationallevel'})
                edu_level = create_gattribute(file_node._id, educationallevel_AT, level)
            if Based_url:
              # create gattribute for file with 'educationaluse' value
                basedonurl_AT = node_collection.one({'_type':'AttributeType', 'name': 'basedonurl'})
                basedUrl = create_gattribute(file_node._id, basedonurl_AT, Based_url)

            if co_contributors:
              # create gattribute for file with 'co_contributors' value
                co_contributors_AT = node_collection.one({'_type':'AttributeType', 'name': 'co_contributors'})
                co_contributors = create_gattribute(file_node._id, co_contributors_AT, co_contributors)
            if content_org:
                    file_node.content_org = unicode(content_org)
                    # Required to link temporary files with the current user who is modifying this document
                    filename_content = slugify(title) + "-" + usrname + "-"
                    file_node.content = content_org
            if tags:
                # print "\n\n tags",tags
                if not type(tags) is list:
                    tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]
                file_node.tags = tags
            # rt_has_asset_content = node_collection.one({'_type': 'RelationType','name': 'has_assetcontent'})
            # gr = create_grelation(ObjectId('58a3dd4cc6bd690400016ae5'), rt_has_asset_content, ObjectId(file_node._id))
            # print gr
            # # asset_node = create_asset(file_node.name,group_id,file_node.created_by,request)
            # # print "++++++++++++++++++++++++++++++++++++++++",asset_node._id
            # asset_content_node = create_assetcontent(ObjectId('58a3dd4cc6bd690400016ae5'),file_node.name,group_id,file_node.created_by)
            # print "---------------------------------------",asset_content_node
            rt_teaches = node_collection.one({'_type': "RelationType", 'name': unicode("teaches")})
            create_grelation(file_node._id,rt_teaches,ObjectId(sel_topic))
            file_node.save(groupid=group_id,validate=False)

            return HttpResponseRedirect( reverse('file_detail', kwargs={"group_id": group_id,'_id':file_node._id}) )
    # print "\n\nretirn gs_obj_list",gs_obj_list
    # gs_obj_id = gs_obj_list[0]['_id']
    # print "\n\n\ngs_obj_id: ",gs_obj_id

    discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
    for each_gs_file in fileobj_list:
        #set interaction-settings
        each_gs_file.status = u"PUBLISHED"
        if usrid not in each_gs_file.contributors:
            each_gs_file.contributors.append(usrid)

        if title == "raw material" or (title == "gallery" and is_user_gstaff):
            if u'raw@material' not in each_gs_file.tags:
                each_gs_file.tags.append(u'raw@material')

        group_object = node_collection.one({'_id': ObjectId(group_id)})
        if (group_object.edit_policy == "EDITABLE_MODERATED") and (group_object.moderation_level > 0):
            from gnowsys_ndf.ndf.views.moderation import get_moderator_group_set
            # print "\n\n\n\ninside editable moderated block"
            each_gs_file.group_set = get_moderator_group_set(each_gs_file.group_set, group_object._id)
            # print "\n\n\npage_node._id",page_node._id
            each_gs_file.status = u'MODERATION'
            # print "\n\n\n page_node.status",page_node.status
        each_gs_file.save()
        create_gattribute(each_gs_file._id, discussion_enable_at, True)
        return_status = create_thread_for_node(request,group_obj._id, each_gs_file)

    if (title == "gallery") or (title == "raw material"):

        active_user_ids_list = [request.user.id]
        if GSTUDIO_BUDDY_LOGIN:
            active_user_ids_list += Buddy.get_buddy_userids_list_within_datetime(request.user.id, datetime.now())
            # removing redundancy of user ids:
            active_user_ids_list = dict.fromkeys(active_user_ids_list).keys()

        counter_objs_cur = Counter.get_counter_objs_cur(active_user_ids_list, group_id)
        # counter_obj = Counter.get_counter_obj(request.user.id, group_id)
        for each_counter_obj in counter_objs_cur:
            each_counter_obj['file']['created'] += len(fileobj_list)
            each_counter_obj['group_points'] += (len(fileobj_list) * GSTUDIO_FILE_UPLOAD_POINTS)
            each_counter_obj.last_update = datetime.now()
            each_counter_obj.save()

    if title == "gallery" and not is_user_gstaff:
        return HttpResponseRedirect(reverse('course_gallery', kwargs={'group_id': group_id}))
    elif title == "raw material" or (title == "gallery" and is_user_gstaff):
        return HttpResponseRedirect(reverse('course_raw_material', kwargs={'group_id': group_id}))
    else:
        return HttpResponseRedirect( reverse('file_detail', kwargs={"group_id": group_id,'_id':fileobj_id}))
    # return HttpResponseRedirect(url_name)



@get_execution_time
def notification_details(request,group_id):
    from gnowsys_ndf.ndf.views.utils import get_dict_from_list_of_dicts
    group_name, group_id = get_group_name_id(group_id)
    group_obj = node_collection.find({'group_set':ObjectId(group_id)}).sort('last_update', -1)
    files_list = []
    user_activity = []
    user_activity_append_temp=user_activity.append
    files_list_append_temp=files_list.append
    for each in group_obj:
      if each.created_by == each.modified_by :
        if each.last_update == each.created_at:
          if each.if_file.mime_type:
            activity =  'created in asset'
          else:
            activity =  'created ' + each.name 
              
        else:
          rel_set_dict = get_dict_from_list_of_dicts(each.relation_set)
          if each.if_file.mime_type and 'assetcontent_of' in rel_set_dict:
            node_obj = Node.get_node_by_id(each.relation_set[0]['assetcontent_of'][0])
            if node_obj:
                activity =  'uploaded ' + each.name +  ' in ' + node_obj.name
          elif 'Asset' in each.member_of_names_list and 'asset@gallery' in each.tags:
            activity =  'Modified Folder ' + each.name
          elif 'Asset' in each.member_of_names_list and 'raw@material' in each.tags:
            activity =  'Modified Resource ' + each.name
          elif 'Asset' in each.member_of_names_list:
            activity =  'Modified Asset ' + each.name
          else:
            activity =  'Modified ' + each.name

      else:
        activity =  'created ' + each.name
      if each._type == 'Group':
        user_activity_append_temp(each)
      each.update({'activity':activity})
      files_list_append_temp(each)
    

    return render_to_response('ndf/notification_detail.html',
                                { 
                                  'group_id': group_id,
                                  'groupid':group_id,
                                  'activity_list' : files_list
                                },
                                context_instance = RequestContext(request)
                            )
