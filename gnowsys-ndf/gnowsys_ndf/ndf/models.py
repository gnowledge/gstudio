# imports from python libraries
import os
import hashlib
import datetime
import json
import magic
import mimetypes

from itertools import chain     # Using from_iterable()
from hashfs import HashFS       # content-addressable file management system
from StringIO import StringIO
from PIL import Image
from django.utils import timezone

# imports from installed packages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.sessions.models import Session
from django.db import models
from django.http import HttpRequest

from django_mongokit import connection
from django_mongokit import get_database
from django_mongokit.document import DjangoDocument
from django.core.files.images import get_image_dimensions

from mongokit import IS
from mongokit import OR
from mongokit import INDEX_ASCENDING, INDEX_DESCENDING

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


# imports from application folders/files
from gnowsys_ndf.settings import RCS_REPO_DIR, MEDIA_ROOT
from gnowsys_ndf.settings import RCS_REPO_DIR_HASH_LEVEL
from gnowsys_ndf.settings import MARKUP_LANGUAGE
from gnowsys_ndf.settings import MARKDOWN_EXTENSIONS
from gnowsys_ndf.settings import GSTUDIO_GROUP_AGENCY_TYPES, GSTUDIO_AUTHOR_AGENCY_TYPES
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_LICENSE
from gnowsys_ndf.settings import META_TYPE
from gnowsys_ndf.ndf.rcslib import RCS
from registration.signals import user_registered


NODE_TYPE_CHOICES = (
    ('Nodes'),
    ('Attribute Types'),
    ('Attributes'),
    ('Relation Types'),
    ('Relations'),
    ('GSystem Types'),
    ('GSystems'),
    ('Node Specification'),
    ('Attribute Specification'),
    ('Relation Specification'),
    ('Intersection'),
    ('Complement'),
    ('Union'),
    ('Process Types'),
    ('Process')
)

TYPES_OF_GROUP = (
    ('PUBLIC'),
    ('PRIVATE'),
    ('ANONYMOUS')
)

EDIT_POLICY = (
    ('EDITABLE_NON_MODERATED'),
    ('EDITABLE_MODERATED'),
    ('NON_EDITABLE')
)

SUBSCRIPTION_POLICY = (
    ('OPEN'),
    ('BY_REQUEST'),
    ('BY_INVITATION'),
)

EXISTANCE_POLICY = (
    ('ANNOUNCED'),
    ('NOT_ANNOUNCED')
)

LIST_MEMBER_POLICY = (
    ('DISCLOSED_TO_MEM'),
    ('NOT_DISCLOSED_TO_MEM')
)

ENCRYPTION_POLICY = (
    ('ENCRYPTED'),
    ('NOT_ENCRYPTED')
)

DATA_TYPE_CHOICES = (
    "None",
    "bool",
    "basestring",
    "unicode",
    "int",
    "float",
    "long",
    "datetime.datetime",
    "list",
    "dict",
    "ObjectId",
    "IS()"
)

my_doc_requirement = u'storing_orignal_doc'
reduced_doc_requirement = u'storing_reduced_doc'
to_reduce_doc_requirement = u'storing_to_be_reduced_doc'
indexed_word_list_requirement = u'storing_indexed_words'

# CUSTOM DATA-TYPE DEFINITIONS
STATUS_CHOICES_TU = IS(u'DRAFT', u'HIDDEN', u'PUBLISHED', u'DELETED', u'MODERATION')
STATUS_CHOICES = tuple(str(qtc) for qtc in STATUS_CHOICES_TU)

QUIZ_TYPE_CHOICES_TU = IS(u'Short-Response', u'Single-Choice', u'Multiple-Choice')
QUIZ_TYPE_CHOICES = tuple(str(qtc) for qtc in QUIZ_TYPE_CHOICES_TU)

# Designate a root folder for HashFS. If the folder does not exists already, it will be created.
# Set the `depth` to the number of subfolders the file's hash should be split when saving.
# Set the `width` to the desired width of each subfolder.
gfs = HashFS(MEDIA_ROOT, depth=3, width=1, algorithm='sha256')
# gfs: gstudio file system


@connection.register
class Node(DjangoDocument):
    '''Everything is a Node.  Other classes should inherit this Node class.

    According to the specification of GNOWSYS, all nodes, including
    types, metatypes and members of types, edges of nodes, should all
    be Nodes.

    Member of this class must belong to one of the NODE_TYPE_CHOICES.

    Some in-built Edge names (Relation types) are defined in this
    class: type_of, member_of, prior_node, post_node, collection_set,
    group_set.

    type_of is used to express generalization of Node. And member_of
    to express its type. This type_of should not be confused with
    _type.  The latter expresses the Python classes defined in this
    program that the object inherits.  The former (type_of) is about
    the data the application represents.

    _type is useful in seggregating the nodes from the mongodb
    collection, where all nodes are stored.

    prior_node is to express that the current node depends in some way
    to another node/s.  post_node is seldom used.  Currently we use it
    to define sub-Group, and to set replies to a post in the Forum App.

    Nodes are publisehed in one group or another, or in more than one
    group. The groups in which a node is publisehed is expressed in
    group_set.

    '''
    objects = models.Manager()

    collection_name = 'Nodes'
    structure = {
        '_type': unicode, # check required: required field, Possible
                          # values are to be taken only from the list
                          # NODE_TYPE_CHOICES
        'name': unicode,
        'altnames': unicode,
        'plural': unicode,
        'prior_node': [ObjectId],
        'post_node': [ObjectId],

        # 'language': unicode,  # previously it was unicode.
        'language': (basestring, basestring),  # Tuple are converted into a simple list
                                               # ref: https://github.com/namlook/mongokit/wiki/Structure#tuples

        'type_of': [ObjectId], # check required: only ObjectIDs of GSystemType
        'member_of': [ObjectId], # check required: only ObjectIDs of
                                 # GSystemType for GSystems, or only
                                 # ObjectIDs of MetaTypes for
                                 # GSystemTypes
        'access_policy': unicode, # check required: only possible
                                  # values are Public or Private.  Why
                                  # is this unicode?

      	'created_at': datetime.datetime,
        'created_by': int, # test required: only ids of Users

        'last_update': datetime.datetime,
        'modified_by': int, # test required: only ids of Users

        'contributors': [int], # test required: set of all ids of
                               # Users of created_by and modified_by
                               # fields
        'location': [dict], # check required: this dict should be a
                            # valid GeoJason format
        'content': unicode,
        'content_org': unicode,

        'group_set': [ObjectId], # check required: should not be
                                 # empty. For type nodes it should be
                                 # set to a Factory Group called
                                 # Administration
        'collection_set': [ObjectId],  # check required: to exclude
                                       # parent nodes as children, use
                                       # MPTT logic
        'property_order': [],  # Determines the order & grouping in
                               # which attribute(s)/relation(s) are
                               # displayed in the form

        'start_publication': datetime.datetime,
        'tags': [unicode],
        'featured': bool,
        'url': unicode,
        'comment_enabled': bool,
      	'login_required': bool,
      	# 'password': basestring,

        'status': STATUS_CHOICES_TU,
        'rating':[{'score':int,
                  'user_id':int,
                  'ip_address':basestring}],
        'snapshot':dict
    }

    indexes = [
        {
            # 1: Compound index
            'fields': [
                ('_type', INDEX_ASCENDING), ('name', INDEX_ASCENDING)
            ]
        }, {
            # 2: Compound index
            'fields': [
                ('_type', INDEX_ASCENDING), ('created_by', INDEX_ASCENDING)
            ]
        }, {
            # 3: Single index
            'fields': [
                ('group_set', INDEX_ASCENDING)
            ]
        }, {
            # 4: Single index
            'fields': [
                ('member_of', INDEX_ASCENDING)
            ]
        }, {
            # 5: Single index
            'fields': [
                ('name', INDEX_ASCENDING)
            ]
        }, {
            # 6: Compound index
            'fields': [
                ('created_by', INDEX_ASCENDING), ('status', INDEX_ASCENDING), \
                ('access_policy', INDEX_ASCENDING), ('last_update' , INDEX_DESCENDING)
            ]
        }, {
            # 7: Compound index
            'fields': [
                ('created_by', INDEX_ASCENDING), ('status', INDEX_ASCENDING), \
                ('access_policy', INDEX_ASCENDING), ('created_at' , INDEX_DESCENDING)
            ]
        }, {
            # 8: Compound index
            'fields': [
                ('created_by', INDEX_ASCENDING), ('last_update' , INDEX_DESCENDING)
            ]
        }, {
            # 9: Compound index
            'fields': [
                ('status', INDEX_ASCENDING), ('last_update' , INDEX_DESCENDING)
            ]
        },
    ]

    required_fields = ['name', '_type'] # 'group_set' to be included
                                        # here after the default
                                        # 'Administration' group is
                                        # ready.
    default_values = {
                        'created_at': datetime.datetime.now,
                        'status': u'DRAFT',
                        'language': ('en', 'English')
                    }
    use_dot_notation = True


    def fill_node_values(self, request=HttpRequest(), **kwargs):

        # 'name': unicode,
        if kwargs.has_key('name'):
            name = kwargs.get('name', '')
        else:
            name = request.POST.get('name', '').strip()
        self.name = unicode(name)

        # 'altnames': unicode,
        if kwargs.has_key('altnames'):
            altnames = kwargs.get('altnames', name)
        else:
            altnames = request.POST.get('altnames', name).strip()
        self.altnames = unicode(altnames)

        # 'plural': unicode,
        if kwargs.has_key('plural'):
            plural = kwargs.get('plural', None)
        else:
            plural = request.POST.get('plural', None)
        self.plural = unicode(plural)

        # 'prior_node': [ObjectId],
        if kwargs.has_key('prior_node'):
            prior_node = kwargs.get('prior_node', [])
        else:
            prior_node = request.POST.get('prior_node', [])
        self.prior_node = prior_node
        if prior_node and not isinstance(prior_node, list):
            self.prior_node = [ObjectId(each) for each in prior_node]

        # 'post_node': [ObjectId]
        if kwargs.has_key('post_node'):
            post_node = kwargs.get('post_node', [])
        else:
            post_node = request.POST.get('post_node', [])
        self.post_node = post_node
        if post_node and not isinstance(post_node, list):
            self.post_node = [ObjectId(each) for each in post_node]

        # 'language': (basestring, basestring)
        if kwargs.has_key('language'):
            language = kwargs.get('language', ('en', 'English'))
        else:
            language = request.POST.get('language', ('en', 'English'))
        self.language = language

        # 'type_of': [ObjectId]
        if kwargs.has_key('type_of'):
            type_of = kwargs.get('type_of', [])
        else:
            type_of = request.POST.get('type_of', [])
        self.type_of = type_of
        if type_of and not isinstance(type_of, list):
            self.type_of = [ObjectId(each) for each in type_of]

        # 'member_of': [ObjectId]
        if kwargs.has_key('member_of'):
            member_of = kwargs.get('member_of', [])
        else:
            member_of = request.POST.get('member_of', [])
        self.member_of = [ObjectId(member_of)] if member_of else member_of
        # if member_of and not isinstance(member_of, list):
        #     self.member_of = [ObjectId(each) for each in member_of]

        # 'access_policy': unicode
        if kwargs.has_key('access_policy'):
            access_policy = kwargs.get('access_policy', u'PUBLIC')
        else:
            access_policy = request.POST.get('access_policy', u'PUBLIC')
        self.access_policy = unicode(access_policy)

        # 'created_at': datetime.datetime
        #   - this will be system generated (while instantiation time), always.

        # 'last_update': datetime.datetime,
        #   - this will be system generated (from save method), always.

        # 'created_by': int
        if not self.created_by:
            if kwargs.has_key('created_by'):
                created_by = kwargs.get('created_by', '')
            elif request:
                created_by = request.user.id
            self.created_by = int(created_by) if created_by else 0

        # 'modified_by': int, # test required: only ids of Users
        if kwargs.has_key('modified_by'):
            modified_by = kwargs.get('modified_by', None)
        elif request:
            if hasattr(request, 'user'):
                modified_by = request.user.id
            elif kwargs.has_key('created_by'):
                modified_by = created_by
        self.modified_by = int(modified_by) if modified_by else 0

        # 'contributors': [int]
        if kwargs.has_key('contributors'):
            contributors = kwargs.get('contributors', [])
        else:
            contributors = request.POST.get('contributors', [])
        self.contributors = contributors
        if contributors and not isinstance(contributors, list):
            self.contributors = [int(each) for each in contributors]

        # 'location': [dict]
        if kwargs.has_key('location'):
            location = kwargs.get('location', [])
        else:
            location = request.POST.get('location', [])
        self.location = list(location) if not isinstance(location, list) else location

        # 'content': unicode
        if kwargs.has_key('content'):
            content = kwargs.get('content', '')
        else:
            content = request.POST.get('content', '')
        self.content = unicode(content)

        # 'content_org': unicode
        if kwargs.has_key('content_org'):
            content_org = kwargs.get('content_org', '')
        else:
            content_org = request.POST.get('content_org', '')
        self.content_org = unicode(content_org)

        # 'group_set': [ObjectId]
        if kwargs.has_key('group_set'):
            group_set = kwargs.get('group_set', [])
        else:
            group_set = request.POST.get('group_set', [])
        self.group_set = group_set
        if group_set and not isinstance(group_set, list):
            self.group_set = [ObjectId(each) for each in group_set]

        # 'collection_set': [ObjectId]
        if kwargs.has_key('collection_set'):
            collection_set = kwargs.get('collection_set', [])
        else:
            collection_set = request.POST.get('collection_set', [])
        self.collection_set = collection_set
        if collection_set and not isinstance(collection_set, list):
            self.collection_set = [ObjectId(each) for each in collection_set]

        # 'property_order': []
        if kwargs.has_key('property_order'):
            property_order = kwargs.get('property_order', [])
        else:
            property_order = request.POST.get('property_order', [])
        self.property_order = list(property_order) if not isinstance(property_order, list) else property_order

        # 'start_publication': datetime.datetime,
        if kwargs.has_key('start_publication'):
            start_publication = kwargs.get('start_publication', None)
        else:
            start_publication = request.POST.get('start_publication', None)
        self.start_publication = start_publication
        # self.start_publication = datetime.datetime(start_publication) if not isinstance(start_publication, datetime.datetime) else start_publication

        # 'tags': [unicode],
        if kwargs.has_key('tags'):
            tags = kwargs.get('tags', [])
        else:
            tags = request.POST.get('tags', [])
        self.tags = tags if tags else []
        if tags and not isinstance(tags, list):
            self.tags = [unicode(each.strip()) for each in tags.split(',')]

        # 'featured': bool,
        if kwargs.has_key('featured'):
            featured = kwargs.get('featured', None)
        else:
            featured = request.POST.get('featured', None)
        self.featured = bool(featured)

        # 'url': unicode,
        if kwargs.has_key('url'):
            url = kwargs.get('url', None)
        else:
            url = request.POST.get('url', None)
        self.url = unicode(url)

        # 'comment_enabled': bool,
        if kwargs.has_key('comment_enabled'):
            comment_enabled = kwargs.get('comment_enabled', None)
        else:
            comment_enabled = request.POST.get('comment_enabled', None)
        self.comment_enabled = bool(comment_enabled)

        # 'login_required': bool,
        if kwargs.has_key('login_required'):
            login_required = kwargs.get('login_required', None)
        else:
            login_required = request.POST.get('login_required', None)
        self.login_required = bool(login_required)

        # 'status': STATUS_CHOICES_TU,
        if kwargs.has_key('status'):
            status = kwargs.get('status', u'DRAFT')
        else:
            status = request.POST.get('status', u'DRAFT')
        self.status = unicode(status)

        # 'rating':[{'score':int, 'user_id':int, 'ip_address':basestring}],
        #       - mostly, it's on detail view and by AJAX and not in/within forms.

        # 'snapshot':dict
        #       - needs to think on this.

        return self


    ########## Setter(@x.setter) & Getter(@property) ##########
    @property
    def user_details_dict(self):
        """Retrieves names of created-by & modified-by users from the given
        node, and appends those to 'user_details' dict-variable

        """
        user_details = {}
        if self.created_by:
            user_details['created_by'] = User.objects.get(pk=self.created_by).username

        contributor_names = []
        for each_pk in self.contributors:
            contributor_names.append(User.objects.get(pk=each_pk).username)
        user_details['contributors'] = contributor_names

        if self.modified_by:
            user_details['modified_by'] = User.objects.get(pk=self.modified_by).username

        return user_details

    @property
    def member_of_names_list(self):
        """Returns a list having names of each member (GSystemType, i.e Page,
        File, etc.), built from 'member_of' field (list of ObjectIds)

        """
        member_of_names = []

        if self.member_of:
            for each_member_id in self.member_of:
                if type(each_member_id) == ObjectId:
                    _id = each_member_id
                else:
                    _id = each_member_id['$oid']
                if _id:
                    mem = node_collection.one({'_id': ObjectId(_id)})
                    if mem:
                        member_of_names.append(mem.name)
        else:
            if "gsystem_type" in self:
                for each_member_id in self.gsystem_type:
                    if type(each_member_id) == ObjectId:
                        _id = each_member_id
                    else:
                        _id = each_member_id['$oid']
                    if _id:
                        mem = node_collection.one({'_id': ObjectId(_id)})
                        if mem:
                            member_of_names.append(mem.name)
        return member_of_names

    @property
    def prior_node_dict(self):
        """Returns a dictionary consisting of key-value pair as
        ObjectId-Document pair respectively for prior_node objects of
        the given node.

        """

        obj_dict = {}
        i = 0
        for each_id in self.prior_node:
            i = i + 1

            if each_id != self._id:
                node_collection_object = node_collection.one({"_id": ObjectId(each_id)})
                dict_key = i
                dict_value = node_collection_object

                obj_dict[dict_key] = dict_value

        return obj_dict

    @property
    def collection_dict(self):
        """Returns a dictionary consisting of key-value pair as
        ObjectId-Document pair respectively for collection_set objects
        of the given node.

        """

        obj_dict = {}

        i = 0;
        for each_id in self.collection_set:
            i = i + 1

            if each_id != self._id:
                node_collection_object = node_collection.one({"_id": ObjectId(each_id)})
                dict_key = i
                dict_value = node_collection_object

                obj_dict[dict_key] = dict_value

        return obj_dict

    @property
    def html_content(self):
        """Returns the content in proper html-format.

        """
        if MARKUP_LANGUAGE == 'markdown':
            return markdown(self.content, MARKDOWN_EXTENSIONS)
        elif MARKUP_LANGUAGE == 'textile':
            return textile(self.content)
        elif MARKUP_LANGUAGE == 'restructuredtext':
            return restructuredtext(self.content)
        return self.content

    @property
    def current_version(self):
        history_manager = HistoryManager()
        return history_manager.get_current_version(self)

    @property
    def version_dict(self):
        """Returns a dictionary containing list of revision numbers of the
        given node.

        Example:
        {
         "1": "1.1",
         "2": "1.2",
         "3": "1.3",
        }

        """
        history_manager = HistoryManager()
        return history_manager.get_version_dict(self)


    ########## Built-in Functions (Overridden) ##########

    def __unicode__(self):
        return self._id

    def identity(self):
        return self.__unicode__()

    def save(self, *args, **kwargs):
	if "is_changed" in kwargs:
            if not kwargs["is_changed"]:
                #print "\n ", self.name, "(", self._id, ") -- Nothing has changed !\n\n"
                return

        is_new = False

        if not "_id" in self:
            is_new = True               # It's a new document, hence yet no ID!"

            # On save, set "created_at" to current date
            self.created_at = datetime.datetime.today()

        self.last_update = datetime.datetime.today()

        # Check the fields which are not present in the class
        # structure, whether do they exists in their GSystemType's
        # "attribute_type_set"; If exists, add them to the document
        # Otherwise, throw an error -- " Illegal access: Invalid field
        # found!!! "

        try:

            invalid_struct_fields = list(set(self.structure.keys()) - set(self.keys()))
            # print '\n invalid_struct_fields: ',invalid_struct_fields
            if invalid_struct_fields:
                for each_invalid_field in invalid_struct_fields:
                    if each_invalid_field in self.structure:
                        print "=== removed from structure", each_invalid_field, ' : ', self.structure.pop(each_invalid_field)


            keys_list = self.structure.keys()
            keys_list.append('_id')
            invalid_struct_fields_list = list(set(self.keys()) - set(keys_list))
            # print '\n invalid_struct_fields_list: ',invalid_struct_fields_list
            if invalid_struct_fields_list:
                for each_invalid_field in invalid_struct_fields_list:
                    if each_invalid_field in self:
                        print "=== removed ", each_invalid_field, ' : ', self.pop(each_invalid_field)

        except Exception, e:
            print e
            pass

        invalid_fields = []

        for key, value in self.iteritems():
            if key == '_id':
                continue

            if not (key in self.structure):
                field_found = False
                for gst_id in self.member_of:
                    attribute_set_list = node_collection.one({'_id': gst_id}).attribute_type_set

                    for attribute in attribute_set_list:
                        if key == attribute['name']:
                            field_found = True

                            # TODO: Check whether type of "value"
                            # matches with that of
                            # "attribute['data_type']" Don't continue
                            # searching from list of remaining
                            # attributes
                            break

                    if field_found:
                        # Don't continue searching from list of
                        # remaining gsystem-types
                        break

                if not field_found:
                    invalid_fields.append(key)
                    print "\n Invalid field(", key, ") found!!!\n"
                    # Throw an error: " Illegal access: Invalid field
                    # found!!! "

        # print "== invalid_fields : ", invalid_fields
        try:
            self_keys = self.keys()
            if invalid_fields:
                for each_invalid_field in invalid_fields:
                    if each_invalid_field in self_keys:
                        self.pop(each_invalid_field)
        except Exception, e:
            print "\nError while processing invalid fields: ", e
            pass

        super(Node, self).save(*args, **kwargs)

    	#This is the save method of the node class.It is still not
    	#known on which objects is this save method applicable We
    	#still do not know if this save method is called for the
    	#classes which extend the Node Class or for every class There
    	#is a very high probability that it is called for classes
    	#which extend the Node Class only The classes which we have
    	#i.e. the MyReduce() and ToReduce() class do not extend from
    	#the node class Hence calling the save method on those objects
    	#should not create a recursive function

    	#If it is a new document then Make a new object of ToReduce
    	#class and the id of this document to that object else Check
    	#whether there is already an object of ToReduce() with the id
    	#of this object.  If there is an object present pass else add
    	#that object I have not applied the above algorithm

   	#Instead what I have done is that I have searched the
   	#ToReduce() collection class and searched whether the ID of
   	#this document is present or not.  If the id is not present
   	#then add that id.If it is present then do not add that id

   	old_doc = node_collection.collection.ToReduceDocs.find_one({'required_for':to_reduce_doc_requirement,'doc_id':self._id})

    		#print "~~~~~~~~~~~~~~~~~~~~It is not present in the ToReduce() class collection.Message Coming from save() method ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",self._id
    	if  not old_doc:


    		z = node_collection.collection.ToReduceDocs()
    		z.doc_id = self._id
    		z.required_for = to_reduce_doc_requirement
    		z.save()

    	#If you create/edit anything then this code shall add it in the URL

        history_manager = HistoryManager()
        rcs_obj = RCS()
	if is_new:
            # Create history-version-file
            try:
                if history_manager.create_or_replace_json_file(self):
                    fp = history_manager.get_file_path(self)
                    user = User.objects.get(pk=self.created_by).username
                    message = "This document (" + self.name + ") is created by " + user + " on " + self.created_at.strftime("%d %B %Y")
                    rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")
            except Exception as err:
                print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be created!!!\n"
                node_collection.collection.remove({'_id': self._id})
                raise RuntimeError(err)

        else:
            # Update history-version-file
            fp = history_manager.get_file_path(self)

            try:
                rcs_obj.checkout(fp)
            except Exception as err:
                try:
                    if history_manager.create_or_replace_json_file(self):
                        fp = history_manager.get_file_path(self)
                        user = User.objects.get(pk=self.created_by).username
                        message = "This document (" + self.name + ") is re-created by " + user + " on " + self.created_at.strftime("%d %B %Y")
                        rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

                except Exception as err:
                    print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be re-created!!!\n"
                    node_collection.collection.remove({'_id': self._id})
                    raise RuntimeError(err)

            try:
                if history_manager.create_or_replace_json_file(self):
                    user = User.objects.get(pk=self.modified_by).username
                    message = "This document (" + self.name + ") is lastly updated by " + user + " status:" + self.status + " on " + self.last_update.strftime("%d %B %Y")
                    rcs_obj.checkin(fp, 1, message.encode('utf-8'))

            except Exception as err:
                print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be updated!!!\n"
                raise RuntimeError(err)
	#gets the last version no.
        rcsno = history_manager.get_current_version(self)
	#update the snapshot feild
	if kwargs.get('groupid'):
		node_collection.collection.update({'_id':self._id}, {'$set': {'snapshot'+"."+str(kwargs['groupid']):rcsno }}, upsert=False, multi=True)

    # User-Defined Functions
    def get_possible_attributes(self, gsystem_type_id_or_list):
        """Returns user-defined attribute(s) of given node which belongs to
        either given single/list of GType(s).

        Keyword arguments: gsystem_type_id_or_list -- Single/List of
        ObjectId(s) of GSystemTypes' to which the given node (self)
        belongs

        If node (self) has '_id' -- Node is created; indicating
        possible attributes needs to be searched under GAttribute
        collection & return value of those attributes (previously
        existing) as part of the list along with attribute-data_type

        Else -- Node needs to be created; indicating possible
        attributes needs to be searched under AttributeType collection
        & return default value 'None' of those attributes as part of
        the list along with attribute-data_type

        Returns: Dictionary that holds follwoing details:- Key -- Name
        of the attribute Value, which inturn is a dictionary that
        holds key and values as shown below:

        { 'attribute-type-name': { 'altnames': Value of AttributeType
        node's altnames field, 'data_type': Value of AttributeType
        node's data_type field, 'object_value': Value of GAttribute
        node's object_value field } }

        """

        gsystem_type_list = []
        possible_attributes = {}

        # Converts to list, if passed parameter is only single ObjectId
        if not isinstance(gsystem_type_id_or_list, list):
            gsystem_type_list = [gsystem_type_id_or_list]
        else:
            gsystem_type_list = gsystem_type_id_or_list

        # Code for finding out attributes associated with each gsystem_type_id in the list
        for gsystem_type_id in gsystem_type_list:

            # Converts string representaion of ObjectId to it's corresponding ObjectId type, if found
            if not isinstance(gsystem_type_id, ObjectId):
                if ObjectId.is_valid(gsystem_type_id):
                    gsystem_type_id = ObjectId(gsystem_type_id)
                else:
                    error_message = "\n ObjectIdError: Invalid ObjectId (" + str(gsystem_type_id) + ") found while finding attributes !!!\n"
                    raise Exception(error_message)

            # Case [A]: While editing GSystem
            # Checking in Gattribute collection - to collect user-defined attributes' values, if already set!
            if "_id" in self:
                # If - node has key '_id'
                attributes = triple_collection.find({'_type': "GAttribute", 'subject': self._id})
                for attr_obj in attributes:
                    # attr_obj is of type - GAttribute [subject (node._id), attribute_type (AttributeType), object_value (value of attribute)]
                    # Must convert attr_obj.attribute_type [dictionary] to node_collection(attr_obj.attribute_type) [document-object]
                    AttributeType.append_attribute(node_collection.collection.AttributeType(attr_obj.attribute_type), possible_attributes, attr_obj.object_value)

            # Case [B]: While creating GSystem / if new attributes get added
            # Again checking in AttributeType collection - because to collect newly added user-defined attributes, if any!
            attributes = node_collection.find({'_type': 'AttributeType', 'subject_type': gsystem_type_id})
            for attr_type in attributes:
                # Here attr_type is of type -- AttributeType
                AttributeType.append_attribute(attr_type, possible_attributes)

            # type_of check for current GSystemType to which the node belongs to
            gsystem_type_node = node_collection.one({'_id': gsystem_type_id}, {'name': 1, 'type_of': 1})
            if gsystem_type_node.type_of:
                attributes = node_collection.find({'_type': 'AttributeType', 'subject_type': {'$in': gsystem_type_node.type_of}})
                for attr_type in attributes:
                    # Here attr_type is of type -- AttributeType
                    AttributeType.append_attribute(attr_type, possible_attributes)

        return possible_attributes


    def get_possible_relations(self, gsystem_type_id_or_list):
        """Returns relation(s) of given node which belongs to either given
        single/list of GType(s).

        Keyword arguments: gsystem_type_id_or_list -- Single/List of
        ObjectId(s) of GTypes' to which the given node (self) belongs

        If node (self) has '_id' -- Node is created; indicating
        possible relations need to be searched under GRelation
        collection & return value of those relations (previously
        existing) as part of the dict along with relation-type details
        ('object_type' and 'inverse_name')

        Else -- Node needs to be created; indicating possible
        relations need to be searched under RelationType collection &
        return default value 'None' for those relations as part of the
        dict along with relation-type details ('object_type' and
        'inverse_name')

        Returns: Dictionary that holds details as follows:- Key --
        Name of the relation Value -- It's again a dictionary that
        holds key and values as shown below:

        { // If inverse_relation - False 'relation-type-name': {
        'altnames': Value of RelationType node's altnames field [0th
        index-element], 'subject_or_object_type': Value of
        RelationType node's object_type field, 'inverse_name': Value
        of RelationType node's inverse_name field,
        'subject_or_right_subject_list': List of Value(s) of GRelation
        node's right_subject field }

          // If inverse_relation - True 'relation-type-name': {
          'altnames': Value of RelationType node's altnames field [1st
          index-element], 'subject_or_object_type': Value of
          RelationType node's subject_type field, 'inverse_name':
          Value of RelationType node's name field,
          'subject_or_right_subject_list': List of Value(s) of
          GRelation node's subject field } }

        """
        gsystem_type_list = []
        possible_relations = {}

        # Converts to list, if passed parameter is only single ObjectId
        if not isinstance(gsystem_type_id_or_list, list):
            gsystem_type_list = [gsystem_type_id_or_list]
        else:
            gsystem_type_list = gsystem_type_id_or_list

        # Code for finding out relations associated with each gsystem_type_id in the list
        for gsystem_type_id in gsystem_type_list:

            # Converts string representaion of ObjectId to it's corresponding ObjectId type, if found
            if not isinstance(gsystem_type_id, ObjectId):
                if ObjectId.is_valid(gsystem_type_id):
                    gsystem_type_id = ObjectId(gsystem_type_id)
                else:
                    error_message = "\n ObjectIdError: Invalid ObjectId (" + gsystem_type_id + ") found while finding relations !!!\n"
                    raise Exception(error_message)

            # Relation
            inverse_relation = False
            # Case - While editing GSystem Checking in GRelation
            # collection - to collect relations' values, if already
            # set!
            if "_id" in self:
                # If - node has key '_id'
                relations = triple_collection.find({'_type': "GRelation", 'subject': self._id, 'status': u"PUBLISHED"})
                for rel_obj in relations:
                    # rel_obj is of type - GRelation
                    # [subject(node._id), relation_type(RelationType),
                    # right_subject(value of related object)] Must
                    # convert rel_obj.relation_type [dictionary] to
                    # collection.Node(rel_obj.relation_type)
                    # [document-object]
                    RelationType.append_relation(
                        node_collection.collection.RelationType(rel_obj.relation_type),
                        possible_relations, inverse_relation, rel_obj.right_subject
                    )

            # Case - While creating GSystem / if new relations get
            # added Checking in RelationType collection - because to
            # collect newly added user-defined relations, if any!
            relations = node_collection.find({'_type': 'RelationType', 'subject_type': gsystem_type_id})
            for rel_type in relations:
                # Here rel_type is of type -- RelationType
                RelationType.append_relation(rel_type, possible_relations, inverse_relation)

            # type_of check for current GSystemType to which the node
            # belongs to
            gsystem_type_node = node_collection.one({'_id': gsystem_type_id}, {'name': 1, 'type_of': 1})
            if gsystem_type_node.type_of:
                relations = node_collection.find({'_type': 'RelationType', 'subject_type': {'$in': gsystem_type_node.type_of}})
                for rel_type in relations:
                    # Here rel_type is of type -- RelationType
                    RelationType.append_relation(rel_type, possible_relations, inverse_relation)

            # Inverse-Relation
            inverse_relation = True
            # Case - While editing GSystem Checking in GRelation
            # collection - to collect inverse-relations' values, if
            # already set!
            if "_id" in self:
                # If - node has key '_id'
                relations = triple_collection.find({'_type': "GRelation", 'right_subject': self._id, 'status': u"PUBLISHED"})
                for rel_obj in relations:
                    # rel_obj is of type - GRelation
                    # [subject(node._id), relation_type(RelationType),
                    # right_subject(value of related object)] Must
                    # convert rel_obj.relation_type [dictionary] to
                    # collection.Node(rel_obj.relation_type)
                    # [document-object]

                    if META_TYPE[4] in rel_obj.relation_type.member_of_names_list:
                        # We are not handling inverse relation processing for
                        # Triadic relationship(s)
                        continue

                    RelationType.append_relation(
                        node_collection.collection.RelationType(rel_obj.relation_type),
                        possible_relations, inverse_relation, rel_obj.subject
                    )

            # Case - While creating GSystem / if new relations get
            # added Checking in RelationType collection - because to
            # collect newly added user-defined relations, if any!
            relations = node_collection.find({'_type': 'RelationType', 'object_type': gsystem_type_id})
            for rel_type in relations:
                # Here rel_type is of type -- RelationType
                RelationType.append_relation(rel_type, possible_relations, inverse_relation)

            # type_of check for current GSystemType to which the node
            # belongs to
            gsystem_type_node = node_collection.one({'_id': gsystem_type_id}, {'name': 1, 'type_of': 1})
            if gsystem_type_node.type_of:
                relations = node_collection.find({'_type': 'RelationType', 'object_type': {'$in': gsystem_type_node.type_of}})
                for rel_type in relations:
                    # Here rel_type is of type -- RelationType
                    RelationType.append_relation(rel_type, possible_relations, inverse_relation)

        return possible_relations

    def get_neighbourhood(self, member_of):
        """Attaches attributes and relations of the node to itself;
        i.e. key's types to it's structure and key's values to itself
        """

        attributes = self.get_possible_attributes(member_of)
        for key, value in attributes.iteritems():
            self.structure[key] = value['data_type']
            self[key] = value['object_value']

        relations = self.get_possible_relations(member_of)
        for key, value in relations.iteritems():
            self.structure[key] = value['subject_or_object_type']
            self[key] = value['subject_or_right_subject_list']


@connection.register
class AttributeType(Node):
    '''To define reusable properties that can be set as possible
    attributes to a GSystemType. A set of possible properties defines
    a GSystemType.

    '''

    structure = {
	'data_type': basestring, # check required: only of the DATA_TYPE_CHOICES
        'complex_data_type': [unicode], # can be a list or a dictionary
        'subject_type': [ObjectId], # check required: only one of Type
                                    # Nodes. GSystems cannot be set as
                                    # subject_types
	'applicable_node_type': [basestring],	# can be one or more
                                                # than one of
                                                # NODE_TYPE_CHOICES

	'verbose_name': basestring,
	'null': bool,
	'blank': bool,
	'help_text': unicode,
	'max_digits': int, # applicable if the datatype is a number
	'decimal_places': int, # applicable if the datatype is a float
	'auto_now': bool,
	'auto_now_add': bool,
	'upload_to': unicode,
	'path': unicode,
	'verify_exist': bool,
	'min_length': int,
	'required': bool,
	'label': unicode,
	'unique': bool,
	'validators': list,
	'default': unicode,
	'editable': bool
    }

    required_fields = ['data_type', 'subject_type']
    use_dot_notation = True

    ##########  User-Defined Functions ##########

    @staticmethod
    def append_attribute(attr_id_or_node, attr_dict, attr_value=None, inner_attr_dict=None):
        if isinstance(attr_id_or_node, unicode):
            # Convert unicode representation of ObjectId into it's
            # corresponding ObjectId type Then fetch
            # attribute-type-node from AttributeType collection of
            # respective ObjectId
            if ObjectId.is_valid(attr_id_or_node):
                attr_id_or_node = node_collection.one({'_type': 'AttributeType', '_id': ObjectId(attr_id_or_node)})
            else:
                print "\n Invalid ObjectId: ", attr_id_or_node, " is not a valid ObjectId!!!\n"
                # Throw indicating the same

        if not attr_id_or_node.complex_data_type:
            # Code for simple data-type Simple data-types: int, float,
            # ObjectId, list, dict, basestring, unicode
            if inner_attr_dict is not None:
                # If inner_attr_dict exists It means node should ne
                # added to this inner_attr_dict and not to attr_dict
                if not (attr_id_or_node.name in inner_attr_dict):
                    # If inner_attr_dict[attr_id_or_node.name] key
                    # doesn't exists, then only add it!
                    if attr_value is None:
                        inner_attr_dict[attr_id_or_node.name] = {
                            'altnames': attr_id_or_node.altnames, '_id': attr_id_or_node._id,
                            'data_type': eval(attr_id_or_node.data_type),
                            'object_value': attr_value
                        }
                    else:
                        inner_attr_dict[attr_id_or_node.name] = {
                            'altnames': attr_id_or_node.altnames, '_id': attr_id_or_node._id,
                            'data_type': eval(attr_id_or_node.data_type),
                            'object_value': attr_value[attr_id_or_node.name]
                        }

                if attr_id_or_node.name in attr_dict:
                    # If this attribute-node exists in outer
                    # attr_dict, then remove it
                    del attr_dict[attr_id_or_node.name]

            else:
                # If inner_attr_dict is None
                if not (attr_id_or_node.name in attr_dict):
                    # If attr_dict[attr_id_or_node.name] key doesn't
                    # exists, then only add it!
                    attr_dict[attr_id_or_node.name] = {
                        'altnames': attr_id_or_node.altnames, '_id': attr_id_or_node._id,
                        'data_type': eval(attr_id_or_node.data_type),
                        'object_value': attr_value
                    }

        else:
            # Code for complex data-type
            # Complex data-types: [...], {...}
            if attr_id_or_node.data_type == "dict":
                if not (attr_id_or_node.name in attr_dict):
                    inner_attr_dict = {}

                    for c_attr_id in attr_id_or_node.complex_data_type:
                        # NOTE: Here c_attr_id is in unicode format
                        # Hence, this function first converts attr_id
                        # to ObjectId format if unicode found
                        AttributeType.append_attribute(c_attr_id, attr_dict, attr_value, inner_attr_dict)

                    attr_dict[attr_id_or_node.name] = inner_attr_dict

                else:
                    for remove_attr_name in attr_dict[attr_id_or_node.name].iterkeys():
                        if remove_attr_name in attr_dict:
                            # If this attribute-node exists in outer
                            # attr_dict, then remove it
                            del attr_dict[remove_attr_name]

            elif attr_id_or_node.data_type == "list":
                if len(attr_id_or_node.complex_data_type) == 1:
                    # Represents list of simple data-types
                    # Ex: [int], [ObjectId], etc.
                    dt = unicode("[" + attr_id_or_node.complex_data_type[0] + "]")
                    if not (attr_id_or_node.name in attr_dict):
                        # If attr_dict[attr_id_or_node.name] key
                        # doesn't exists, then only add it!
                        attr_dict[attr_id_or_node.name] = {
                            'altnames': attr_id_or_node.altnames, '_id': attr_id_or_node._id,
                            'data_type': eval(dt),
                            'object_value': attr_value
                        }

                else:
                    # Represents list of complex data-types Ex:
                    # [{...}]
                    for c_attr_id in attr_id_or_node.complex_data_type:
                        if not ObjectId.is_valid(c_attr_id):
                            # If basic data-type values are found,
                            # pass the iteration
                            continue

                        # If unicode representation of ObjectId is
                        # found
                        AttributeType.append_attribute(c_attr_id, attr_dict, attr_value)

            elif attr_id_or_node.data_type == "IS()":
                # Below code does little formatting, for example:
                # data_type: "IS()" complex_value: [u"ab", u"cd"] dt:
                # "IS(u'ab', u'cd')"
                dt = "IS("
                for v in attr_id_or_node.complex_data_type:
                    dt = dt + "u'" + v + "'" + ", "
                dt = dt[:(dt.rfind(", "))] + ")"

                if not (attr_id_or_node.name in attr_dict):
                    # If attr_dict[attr_id_or_node.name] key doesn't
                    # exists, then only add it!
                    attr_dict[attr_id_or_node.name] = {
                        'altnames': attr_id_or_node.altnames, '_id': attr_id_or_node._id,
                        'data_type': eval(dt),
                        'object_value': attr_value
                    }


@connection.register
class RelationType(Node):
    structure = {
        'inverse_name': unicode,
        'subject_type': [ObjectId],  # ObjectId's of Any Class
        'object_type': [OR(ObjectId, list)],  # ObjectId's of Any Class
        'subject_cardinality': int,
        'object_cardinality': int,
        'subject_applicable_nodetype': basestring,  # NODE_TYPE_CHOICES [default (GST)]
        'object_applicable_nodetype': basestring,
        'slug': basestring,
        'is_symmetric': bool,
        'is_reflexive': bool,
        'is_transitive': bool
    }

    required_fields = ['inverse_name', 'subject_type', 'object_type']
    use_dot_notation = True

    # User-Defined Functions ##########
    @staticmethod
    def append_relation(
        rel_type_node, rel_dict, inverse_relation, left_or_right_subject=None
    ):
        """Appends details of a relation in format described below.

        Keyword arguments:
        rel_type_node -- Document of RelationType
        node rel_dict -- Dictionary to which relation-details are
        appended inverse_relation -- Boolean variable that indicates
        whether appending an relation or inverse-relation
        left_or_right_subject -- Actual value of related-subjects
        (only if provided, otherwise by default it's None)

        Returns: Dictionary that holds details as follows: Key -- Name
        of the relation Value -- It's again a dictionary that holds
        key and values as shown below: { // If inverse_relation -
        False 'relation-type-name': { 'altnames': Value of
        RelationType node's altnames field [0th index-element],
        'subject_or_object_type': Value of RelationType node's
        object_type field, 'inverse_name': Value of RelationType
        node's inverse_name field, 'subject_or_right_subject_list':
        List of Value(s) of GRelation node's right_subject field }

          // If inverse_relation - True 'relation-type-name': {
          'altnames': Value of RelationType node's altnames field [1st
          index-element], 'subject_or_object_type': Value of
          RelationType node's subject_type field, 'inverse_name':
          Value of RelationType node's name field,
          'subject_or_right_subject_list': List of Value(s) of
          GRelation node's subject field } }
        """

        left_or_right_subject_node = None

        if left_or_right_subject:
            if META_TYPE[3] in rel_type_node.member_of_names_list:
                # If Binary relationship found
                left_or_right_subject_node = node_collection.one({
                    '_id': left_or_right_subject
                })
            else:
                left_or_right_subject_node = []
                for each in left_or_right_subject:
                    each_node = node_collection.one({
                        '_id': each
                    })
                    left_or_right_subject_node.append(each_node)

            if not left_or_right_subject_node:
                error_message = "\n AppendRelationError: Right subject with " \
                    + "this ObjectId(" + str(left_or_right_subject) + ") " \
                    + "doesn't exists !!!"
                raise Exception(error_message)

        rel_name = ""
        opp_rel_name = ""
        alt_names = ""
        subject_or_object_type = None

        if inverse_relation:
            # inverse_relation = True
            # Means looking from object type
            # relation-type's name & inverse-name will be swapped
            rel_name = rel_type_node.inverse_name
            opp_rel_name = rel_type_node.name

            if rel_type_node.altnames:
                if ";" in rel_type_node.altnames:
                    alt_names = rel_type_node.altnames.split(";")[1]
            else:
                alt_names = u""

            subject_or_object_type = rel_type_node.subject_type

        else:
            # inverse_relation = False
            # Means looking from subject type
            # relation-type's name & inverse-name will be as it is
            rel_name = rel_type_node.name
            opp_rel_name = rel_type_node.inverse_name
            if rel_type_node.altnames:
                if ";" in rel_type_node.altnames:
                    alt_names = rel_type_node.altnames.split(";")[0]
            else:
                alt_names = u""

            subject_or_object_type = rel_type_node.object_type

        if not (rel_name in rel_dict):
            subject_or_right_subject_list = [left_or_right_subject_node] if left_or_right_subject_node else []

            rel_dict[rel_name] = {
                'altnames': alt_names,
                'subject_or_object_type': subject_or_object_type,
                'inverse_name': opp_rel_name,
                'subject_or_right_subject_list': subject_or_right_subject_list
            }

        else:
            subject_or_right_subject_list = rel_dict[rel_name]["subject_or_right_subject_list"] if rel_dict[rel_name]["subject_or_right_subject_list"] else []
            if left_or_right_subject_node:
                if not (left_or_right_subject_node in subject_or_right_subject_list):
                    subject_or_right_subject_list.append(left_or_right_subject_node)
                    rel_dict[rel_name]["subject_or_right_subject_list"] = subject_or_right_subject_list

        rel_dict[rel_name]["_id"] = rel_type_node._id
        return rel_dict


@connection.register
class MetaType(Node):
    """MetaType class: Its members are any of GSystemType, AttributeType,
    RelationType, ProcessType.

    It is used to express the NodeTypes that are part of an
    Application developed using GNOWSYS-Studio. E.g, a GSystemType
    'Page' or 'File' become applications by expressing them as members
    of a MetaType, 'GAPP'.

    """

    structure = {
        'description': basestring,    # Description (name)
        'attribute_type_set': [AttributeType],  # Embed list of Attribute Type Class as Documents
        'relation_type_set': [RelationType],    # Holds list of Relation Types
        'parent': ObjectId                      # Foreign key to self
    }
    use_dot_notation = True


class ProcessType(Node):
    """A kind of nodetype for defining processes or events or temporal
    objects involving change.

    """

    structure = {
        'changing_attributetype_set': [AttributeType],  # List of Attribute Types
        'changing_relationtype_set': [RelationType]    # List of Relation Types
    }
    use_dot_notation = True

# user should have a list of groups attributeType added should
# automatically be added to the attribute_type_set of GSystemType
@connection.register
class GSystemType(Node):
    """Class to generalize GSystems
    """

    structure = {
        'meta_type_set': [MetaType],            # List of Metatypes
        'attribute_type_set': [AttributeType],  # Embed list of Attribute Type Class as Documents
        'relation_type_set': [RelationType],    # Holds list of Relation Types
        'process_type_set': [ProcessType],      # List of Process Types
        'property_order': []                    # List of user-defined attributes in template-view order
    }

    use_dot_notation = True
    use_autorefs = True                         # To support Embedding of Documents


@connection.register
class GSystem(Node):
    """GSystemType instance
    """

    # static vars:
    image_sizes_name = ['original', 'mid', 'thumbnail']
    image_sizes = {'mid': (500, 300), 'thumbnail': (128, 128)}
    sys_gen_image_prefix = 'gstudio-'

    structure = {
        'attribute_set': [dict],    # ObjectIds of GAttributes
        'relation_set': [dict],     # ObjectIds of GRelations
        'module_set': [dict],       # Holds the ObjectId & SnapshotID (version_number)
                                        # of collection elements
                                        # along with their sub-collection elemnts too
        'if_file': {
                        'mime_type': basestring,
                        'original': {'id': ObjectId, 'relurl': basestring},
                        'mid': {'id': ObjectId, 'relurl': basestring},
                        'thumbnail': {'id': ObjectId, 'relurl': basestring}
                    },
        'author_set': [int],        # List of Authors
        'annotations': [dict],      # List of json files for annotations on the page
        'license': basestring,      # contains license/s in string format
        'origin': []                # e.g:
                                        # [
                                        #   {"csv-import": <fn name>},
                                        #   {"sync_source": "<system-pub-key>"}
                                        # ]
    }

    use_dot_notation = True

    # default_values = "CC-BY-SA 4.0 unported"
    default_values = {
                        'license': GSTUDIO_DEFAULT_LICENSE
                    }

    def fill_gstystem_values(self,
                            request=None,
                            attribute_set=[],
                            relation_set=[],
                            author_set=[],
                            license=GSTUDIO_DEFAULT_LICENSE,
                            origin=[],
                            uploaded_file=None,
                            **kwargs):

        existing_file_gs = None
        existing_file_gs_if_file = None

        if uploaded_file:

            fh_obj = filehive_collection.collection.Filehive()
            existing_fh_obj = fh_obj.check_if_file_exists(uploaded_file)

            if existing_fh_obj:
                existing_file_gs = node_collection.find_one({
                                    '_type': 'GSystem',
                                    'if_file.original.id': existing_fh_obj._id
                                })

            if kwargs.has_key('unique_gs_per_file') and kwargs['unique_gs_per_file']:

                if existing_file_gs:
                    return existing_file_gs

        self.fill_node_values(request, **kwargs)

        user_id = self.created_by

        # generating '_id':
        if not self.has_key('_id'):
            self['_id'] = ObjectId()

        # origin:
        if kwargs.has_key('origin'):
            self['origin'] = kwargs.get('origin', '')
        # else:  # rarely/no origin field value will be sent via form/request.
        #     self['origin'] = request.POST.get('origin', '').strip()

        if existing_file_gs:

            existing_file_gs_if_file = existing_file_gs.if_file

            def __check_if_file(d):
                for k, v in d.iteritems():
                    if isinstance(v, dict):
                        __check_if_file(v)
                    else:
                        # print "{0} : {1}".format(k, v)
                        if not v:
                            existing_file_gs_if_file = None

        if uploaded_file and existing_file_gs_if_file:
            self['if_file'] = existing_file_gs_if_file

        elif uploaded_file and not existing_file_gs:

            original_filehive_obj   = filehive_collection.collection.Filehive()
            original_file           = uploaded_file

            mime_type = original_filehive_obj.get_file_mimetype(original_file)
            file_name = original_filehive_obj.get_file_name(original_file)
            original_file_extension = original_filehive_obj.get_file_extension(file_name, mime_type)

            file_exists, original_filehive_obj = original_filehive_obj.save_file_in_filehive(
                file_blob=original_file,
                file_name=file_name,
                first_uploader=user_id,
                first_parent=self._id,
                mime_type=mime_type,
                file_extension=original_file_extension,
                if_image_size_name='original',
                get_obj=True,
                get_file_exists=True
                )

            mime_type = original_filehive_obj.mime_type

            # print "original_filehive_obj: ", original_filehive_obj
            if original_filehive_obj:

                self.if_file.mime_type       = mime_type
                self.if_file.original.id    = original_filehive_obj._id
                self.if_file.original.relurl = original_filehive_obj.relurl

                if 'image' in original_filehive_obj.mime_type.lower():

                    for each_image_size in self.image_sizes_name[1:]:

                        parent_id = self.if_file[self.image_sizes_name[self.image_sizes_name.index(each_image_size) - 1]]['id']

                        each_image_size_filename =  self.sys_gen_image_prefix \
                                                    + each_image_size \
                                                    + '-' \
                                                    + original_filehive_obj.filename

                        each_image_size_filehive_obj = filehive_collection.collection.Filehive()
                        each_image_size_file, dimension = each_image_size_filehive_obj.convert_image_to_size(files=original_file,
                                                  file_name=each_image_size_filename,
                                                  file_extension=original_file_extension,
                                                  file_size=self.image_sizes[each_image_size])

                        if each_image_size_file:
                            each_image_size_id_url = each_image_size_filehive_obj.save_file_in_filehive(
                                file_blob=each_image_size_file,
                                file_name=each_image_size_filename,
                                first_uploader=user_id,
                                first_parent=parent_id,
                                mime_type=mime_type,
                                file_extension=original_file_extension,
                                if_image_size_name=each_image_size,
                                if_image_dimensions=dimension)

                            # print "each_image_size_id_url : ",each_image_size_id_url
                            self.if_file[each_image_size]['id']    = each_image_size_id_url['id']
                            self.if_file[each_image_size]['relurl'] = each_image_size_id_url['relurl']

        return self

    def get_gsystem_mime_type(self):

        if hasattr(self, 'mime_type') and self.mime_type:
            mime_type = self.mime_type
        elif self.if_file.mime_type:
            mime_type = self.if_file.mime_type
        else:
            mime_type = ''

        return mime_type


    def get_file(self, md5_or_relurl=None):

        file_blob = None

        try:
            if md5_or_relurl:
                file_blob = gfs.open(md5_or_relurl)
        except Exception, e:
                print "File '", md5_or_relurl, "' not found: ", e

        return file_blob



@connection.register
class Filehive(DjangoDocument):
    """
    Filehive class to hold any resource in file system.
    """

    objects = models.Manager()
    collection_name = 'Filehives'

    structure = {
        '_type': unicode,
        'md5': basestring,
        'relurl': basestring,
        'mime_type': basestring,             # Holds the type of file
        'length': float,
        'filename': unicode,
        'first_uploader': int,
        'first_parent': ObjectId,
        'uploaded_at': datetime.datetime,
        'if_image_size_name': basestring,
        'if_image_dimensions': basestring,
        }

    indexes = [
        {
            # 12: Single index
            'fields': [
                ('mime_type', INDEX_ASCENDING)
            ]
        }
    ]

    use_dot_notation = True
    required_fields = ['md5', 'mime_type']
    default_values = {
                        'uploaded_at': datetime.datetime.now
                    }


    def __unicode__(self):
        return self._id


    def identity(self):
        return self.__unicode__()


    def get_file_md5(self, file_blob):
        file_md5 = gfs.computehash(file_blob)
        return file_md5


    def get_filehive_obj_from_file_blob(self, file_blob):
        file_md5 = self.get_file_md5(file_blob)
        return filehive_collection.find_one({'md5': str(file_md5)})


    def check_if_file_exists(self, file_blob):
        file_md5 = self.get_file_md5(file_blob)
        return filehive_collection.find_one({'md5': file_md5})


    def _put_file(self, file_blob, file_extension):
        '''
        - Put's file under specified root.
        - After saving file blob or if file already exists,
            returns it's relative path.
        '''

        file_hash = gfs.computehash(file_blob)

        if gfs.exists(file_hash):
            # file with same hash already exists in file system.
            hash_addr_obj = gfs.get(file_hash)
        else:
            hash_addr_obj = gfs.put(file_blob, file_extension)

        return hash_addr_obj


    def save_file_in_filehive(self,
                              file_blob,
                              first_uploader,
                              first_parent,
                              file_name='',
                              mime_type=None,
                              file_extension='',
                              if_image_size_name='',
                              if_image_dimensions=None,
                              **kwargs):

        # file_hash = gfs.computehash(file_blob)

        # to check if file is new-fresh-file or old-existing-file
        file_exists = True

        file_metadata_dict = self.get_file_metadata(file_blob, mime_type, file_extension, file_name, if_image_dimensions)

        # file_blob.seek(0)
        addr_obj = self._put_file(file_blob, file_metadata_dict['file_extension'])
        # print "addr_obj : ", addr_obj

        md5 = str(addr_obj.id)
        filehive_obj = filehive_collection.find_one({'md5': md5})
        # print filehive_obj

        id_url_dict = {'id': None, 'relurl': ''}

        if not filehive_obj:

            # file is new and it doesn't exists
            file_exists = False

            # instantiating empty instance
            # filehive_obj = filehive_collection.collection.Filehive()
            filehive_obj = self

            filehive_obj.md5                 = str(md5)
            filehive_obj.relurl              = str(addr_obj.relpath)
            filehive_obj.mime_type           = str(file_metadata_dict['file_mime_type'])
            filehive_obj.length              = float(file_metadata_dict['file_size'])
            filehive_obj.filename            = unicode(file_metadata_dict['file_name'])
            filehive_obj.first_uploader      = int(first_uploader)
            filehive_obj.first_parent        = ObjectId(first_parent)
            filehive_obj.if_image_size_name  = str(if_image_size_name)
            filehive_obj.if_image_dimensions = str(file_metadata_dict['image_dimension'])

            filehive_obj.save()
            # print "filehive_obj : ", filehive_obj

        id_url_dict['id']     = filehive_obj._id
        id_url_dict['relurl'] = filehive_obj.relurl

        if kwargs.has_key('get_obj') and kwargs['get_obj']:
            result = filehive_obj
        else:
            result = id_url_dict

        if kwargs.has_key('get_file_exists') and kwargs['get_file_exists']:
            return (file_exists, result)

        return result


    @staticmethod
    def delete_file_from_filehive(filehive_id, filehive_relurl):

        filehive_obj    = filehive_collection.one({'_id': ObjectId(filehive_id)})
        if filehive_obj:
            file_md5        = str(filehive_obj.md5)
            filehive_obj_id = str(filehive_obj._id)

            print "\nDeleted filehive object having '_id': ", filehive_obj_id," from Filehive collection."
            filehive_obj.delete()

            if gfs.delete(file_md5):
                print "\nDeleted physical file having 'md5': ", file_md5
                return True

        if gfs.delete(filehive_relurl):
            print "\nDeleted physical file having 'relurl': ", filehive_relurl
            return True

        return False


    # -- file helper methods --
    def get_file_metadata(self,
                          file_blob,
                          mime_type=None,
                          file_extension='',
                          file_name='',
                          image_dimensions=None):

        # as file_blob is mostly uploaded file, using some of django's
        # <django.core.files.uploadedfile> class's built in properties.
        file_metadata_dict = {
            'file_name': '',
            'file_size': 0,
            'file_mime_type': '',
            'file_extension': '',
            'image_dimension': None
        }

        file_name = file_name if file_name else file_blob.name if hasattr(file_blob, 'name') else ''
        file_metadata_dict['file_name'] = file_name

        file_mime_type = mime_type if mime_type else self.get_file_mimetype(file_blob)
        file_metadata_dict['file_mime_type'] = file_mime_type

        if file_extension:
            file_metadata_dict['file_extension'] = file_extension
        else:
            file_extension = self.get_file_extension(file_name, file_mime_type)

        try:
            if hasattr(file_blob, 'size'):
                file_size = file_blob.size
            else:
                file_blob.seek(0, os.SEEK_END)
                file_size = file_blob.tell()
                file_blob.seek(0)
        except Exception, e:
            print "Exception in calculating file_size: ", e
            file_size = 0

        file_metadata_dict['file_size'] = file_size

        # get_image_dimensions: Returns the (width, height) of an image
        image_dimension_str = ''
        image_dimension_tuple = None
        if image_dimensions:
            image_dimension_tuple = image_dimensions
        else:
            try:
                image_dimension_tuple = get_image_dimensions(file_blob)
            except Exception, e:
                print "Exception in calculating file dimensions: ", e
                pass

        if image_dimension_tuple:
            image_dimension_str = str(image_dimension_tuple[0])
            image_dimension_str += ' X '
            image_dimension_str += str(image_dimension_tuple[1])
        file_metadata_dict['image_dimension'] = image_dimension_str

        # print "\nfile_metadata_dict : ", file_metadata_dict
        return file_metadata_dict


    def get_file_mimetype(self, file_blob):

        file_mime_type = ''
        file_content_type = file_blob.content_type if hasattr(file_blob, 'content_type') else None

        if file_content_type and file_content_type != 'application/octet-stream':
            file_mime_type = file_blob.content_type
        else:
            file_blob.seek(0)
            file_mime_type = magic.from_buffer(file_blob.read(), mime=True)
            file_blob.seek(0)

        return file_mime_type


    def get_file_name(self, file_blob):

        file_name = file_blob.name if hasattr(file_blob, 'name') else ''
        return file_name


    def get_file_extension(self, file_name, file_mime_type):
        # if uploaded file is of mimetype: 'text/plain':
        #     - use extension of original file if provided.
        #     - if extension is not provided, use '.txt' as extension.
        file_extension = ''

        poss_ext = '.'
        poss_ext += file_name.split('.')[-1]

        # possible extension from file name
        # get all possible extensions as a list
        # e.g for text/plain:
        # ['.ksh', '.pl', '.bat', '.h', '.c', '.txt', '.asc', '.text', '.pot', '.brf', '.srt']
        all_poss_ext = mimetypes.guess_all_extensions(file_mime_type)

        if poss_ext in all_poss_ext:
            file_extension = poss_ext

        elif file_mime_type == 'text/plain':
            file_extension = '.txt'

        elif poss_ext == '.ggb':
            file_extension = '.ggb'

        else:
            file_extension = mimetypes.guess_extension(file_mime_type)

        return file_extension


    def convert_image_to_size(self, files, file_name='', file_extension='', file_size=()):
        """
        convert image into mid size image w.r.t. max width of 500
        """
        try:

            files.seek(0)
            mid_size_img = StringIO()
            size = file_size if file_size else (500, 300)
            file_name = file_name if file_name else files.name if hasattr(files, 'name') else ''

            try:
                img = Image.open(StringIO(files.read()))
            except Exception, e:
                print "Exception in opening file with PIL.Image.Open(): ", e
                return None, None

            size_to_comp = size[0]
            if (img.size > size) or (img.size[0] >= size_to_comp):
                # both width and height are more than width:500 and height:300
                # or
                # width is more than width:500
                factor = img.size[0]/size_to_comp
                img = img.resize((size_to_comp, int(img.size[1] / factor)), Image.ANTIALIAS)

            elif (img.size <= size) or (img.size[0] <= size_to_comp):
                img = img.resize(img.size, Image.ANTIALIAS)

            if 'jpg' in file_extension or 'jpeg' in file_extension:
                extension = 'JPEG'
            elif 'png' in file_extension:
                extension = 'PNG'
            elif 'gif' in file_extension:
                extension = 'GIF'
            elif 'svg' in file_extension:
                extension = 'SVG'
            else:
                extension = ''

            if extension:
                img.save(mid_size_img, extension)
            else:
                img.save(mid_size_img, "JPEG")

            img_size = img.size if img else None
            mid_size_img.name = file_name
            mid_size_img.seek(0)

            return mid_size_img, img_size

        except Exception, e:
            print "Exception in converting image to mid size: ", e
            return None


    def save(self, *args, **kwargs):

        is_new = False if ('_id' in self) else True

        if is_new:
            self.uploaded_at = datetime.datetime.now()

        super(Filehive, self).save(*args, **kwargs)

        # storing Filehive JSON in RSC system:
        history_manager = HistoryManager()
        rcs_obj = RCS()

        if is_new:

            # Create history-version-file
            if history_manager.create_or_replace_json_file(self):
                fp = history_manager.get_file_path(self)
                message = "This document (" + str(self.md5) + ") is created on " + self.uploaded_at.strftime("%d %B %Y")
                rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

        else:
            # Update history-version-file
            fp = history_manager.get_file_path(self)

            try:
                rcs_obj.checkout(fp)

            except Exception as err:
                try:
                    if history_manager.create_or_replace_json_file(self):
                        fp = history_manager.get_file_path(self)
                        message = "This document (" + str(self.md5) + ") is re-created on " + datetime.uploaded_at.strftime("%d %B %Y")
                        rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

                except Exception as err:
                    print "\n DocumentError: This document (", self._id, ":", str(self.md5), ") can't be re-created!!!\n"
                    node_collection.collection.remove({'_id': self._id})
                    raise RuntimeError(err)

            try:
                if history_manager.create_or_replace_json_file(self):
                    message = "This document (" + str(self.md5) + ") is lastly updated on " + datetime.datetime.now().strftime("%d %B %Y")
                    rcs_obj.checkin(fp, 1, message.encode('utf-8'))

            except Exception as err:
                print "\n DocumentError: This document (", self._id, ":", str(self.md5), ") can't be updated!!!\n"
                raise RuntimeError(err)

        # --- END of storing Filehive JSON in RSC system ---


@connection.register
class File(GSystem):
    """File class to hold any resource
    """

    structure = {
        'mime_type': basestring,             # Holds the type of file
        'fs_file_ids': [ObjectId],           # Holds the List of  ids of file stored in gridfs
                                             # order is [original, thumbnail, mid]
        'file_size': {
            'size': float,
            'unit': unicode
        }  # dict used to hold file size in int and unit palace in term of KB,MB,GB
    }

    indexes = [
        {
            # 12: Single index
            'fields': [
                ('mime_type', INDEX_ASCENDING)
            ]
        }
    ]

    gridfs = {
        'containers': ['files']
    }

    use_dot_notation = True


@connection.register
class Group(GSystem):
    """Group class to create collection (group) of members
    """

    structure = {
        'group_type': basestring,            # Types of groups - Anonymous, public or private
        'edit_policy': basestring,           # Editing policy of the group - non editable,editable moderated or editable non-moderated
        'subscription_policy': basestring,   # Subscription policy to this group - open, by invitation, by request
        'visibility_policy': basestring,     # Existance of the group - announced or not announced
        'disclosure_policy': basestring,     # Members of this group - disclosed or not
        'encryption_policy': basestring,     # Encryption - yes or no
        'agency_type': basestring,           # A choice field such as Pratner,Govt.Agency, NGO etc.

        'group_admin': [int],		     # ObjectId of Author class
        'moderation_level': int              # range from 0 till any integer level
    }

    use_dot_notation = True

    default_values = {'moderation_level': -1}

    validators = {
        'group_type': lambda x: x in TYPES_OF_GROUP,
        'edit_policy': lambda x: x in EDIT_POLICY,
        'subscription_policy': lambda x: x in SUBSCRIPTION_POLICY,
        'visibility_policy': lambda x: x in EXISTANCE_POLICY,
        'disclosure_policy': lambda x: x in LIST_MEMBER_POLICY,
        'encryption_policy': lambda x: x in ENCRYPTION_POLICY,
        'agency_type': lambda x: x in GSTUDIO_GROUP_AGENCY_TYPES,
        # 'name': lambda x: x not in \
        # [ group_obj['name'] for group_obj in \
        # node_collection.find({'_type': 'Group'}, {'name': 1, '_id': 0})]
    }

    def is_gstaff(self, user):
        """
        Checks whether given user belongs to GStaff.
        GStaff includes only the following users of a group:
          1) Super-user (Django's superuser)
          2) Creator of the group (created_by field)
          3) Admin-user of the group (group_admin field)
        Other memebrs (author_set field) doesn't belongs to GStaff.

        Arguments:
        self -- Node of the currently selected group
        user -- User object taken from request object

        Returns:
        True -- If user is one of them, from the above specified list of categories.
        False -- If above criteria is not met (doesn't belongs to any of the category, mentioned above)!
        """

        if (user.is_superuser) or (user.id == self.created_by) or (user.id in self.group_admin):
            return True

        else:
            return False


@connection.register
class Author(Group):
    """Author class to store django user instances
    """
    structure = {
        'email': unicode,
        'password': unicode,
        'visited_location': [],
        'preferred_languages': dict,          # preferred languages for users like preferred lang. , fall back lang. etc.
        'group_affiliation': basestring,
	'language_proficiency':list,
	'subject_proficiency':list
    }

    use_dot_notation = True

    validators = {
        'agency_type': lambda x: x in GSTUDIO_AUTHOR_AGENCY_TYPES         # agency_type inherited from Group class
    }

    required_fields = ['name']

    def __init__(self, *args, **kwargs):
        super(Author, self).__init__(*args, **kwargs)

    def __eq__(self, other_user):
        # found that otherwise millisecond differences in created_at is compared
        try:
            other_id = other_user['_id']
        except (AttributeError, TypeError):
            return False

        return self['_id'] == other_id

    @property
    def id(self):
        return self.name

    def password_crypt(self, password):
        password_salt = str(len(password))
        crypt = hashlib.sha1(password[::-1].upper() + password_salt).hexdigest()
        PASSWORD = unicode(crypt, 'utf-8')
        return PASSWORD

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    @staticmethod
    def get_user_id_list_from_author_oid_list(author_oids_list=[]):
        all_authors_cur = node_collection.find({'_id': {'$in': [ObjectId(a) for a in author_oids_list]} },
                                                {'_id': 0, 'created_by': 1} )
        return [user['created_by'] for user in all_authors_cur]

    @staticmethod
    def get_author_oid_list_from_user_id_list(user_ids_list=[], list_of_str_oids=False):
        all_authors_cur = node_collection.find(
                                        {
                                            '_type': 'Author',
                                            'created_by': {'$in': [int(uid) for uid in user_ids_list]}
                                        },
                                        {'_id': 1}
                                    )
        if list_of_str_oids:
            return [str(user['_id']) for user in all_authors_cur]
        else:
            return [user['_id'] for user in all_authors_cur]


    @staticmethod
    def create_author(user_id_or_obj, agency_type='Student', **kwargs):

        user_obj = None

        if isinstance(user_id_or_obj, int):
            user_obj = User.objects.filter(id=user_id_or_obj)
            if len(user_obj) > 0:
                user_obj = user_obj[0]

        elif isinstance(user_id_or_obj, User):
            user_obj = user_id_or_obj

        if not user_obj:
            raise Exception("\nUser with provided user-id/user-obj does NOT exists!!")

        auth = node_collection.find_one({'_type': u"Author", 'created_by': int(user_obj.id)})

        if auth:
            return auth

        auth_gst = node_collection.one({'_type': u'GSystemType', 'name': u'Author'})

        print "\n Creating new Author obj for user id (django): ", user_obj.id
        auth = node_collection.collection.Author()
        auth.name = unicode(user_obj.username)
        auth.email = unicode(user_obj.email)
        auth.password = u""
        auth.member_of.append(auth_gst._id)
        auth.group_type = u"PUBLIC"
        auth.edit_policy = u"NON_EDITABLE"
        auth.subscription_policy = u"OPEN"
        auth.created_by = user_obj.id
        auth.modified_by = user_obj.id
        auth.contributors.append(user_obj.id)
        auth.group_admin.append(user_obj.id)
        auth.preferred_languages = {'primary': ('en', 'English')}

        auth.agency_type = "Student"
        auth_id = ObjectId()
        auth['_id'] = auth_id
        auth.save(groupid=auth_id)

        home_group_obj = node_collection.one({'_type': u"Group", 'name': unicode("home")})
        if user_obj.id not in home_group_obj.author_set:
            node_collection.collection.update({'_id': home_group_obj._id}, {'$push': {'author_set': user_obj.id }}, upsert=False, multi=False)
            home_group_obj.reload()

        desk_group_obj = node_collection.one({'_type': u"Group", 'name': unicode("desk")})
        if desk_group_obj and user_obj.id not in desk_group_obj.author_set:
            node_collection.collection.update({'_id': desk_group_obj._id}, {'$push': {'author_set': user_obj.id }}, upsert=False, multi=False)
            desk_group_obj.reload()

        return auth


#  HELPER -- CLASS DEFINITIONS
class HistoryManager():
    """Handles history management for documents of a collection
    using Revision Control System (RCS).
    """

    objects = models.Manager()

    __RCS_REPO_DIR = RCS_REPO_DIR

    def __init__(self):
        pass

    def check_dir_path(self, dir_path):
        """Checks whether path exists; and if not it creates that path.

        Arguments:
        (1) dir_path -- a string value representing an absolute path

        Returns: Nothing
        """
        dir_exists = os.path.isdir(dir_path)

        if not dir_exists:
            os.makedirs(dir_path)

    def get_current_version(self, document_object):
        """Returns the current version/revision number of the given document instance.
        """
        fp = self.get_file_path(document_object)
        rcs = RCS()
        return rcs.head(fp)

    def get_version_dict(self, document_object):
        """Returns a dictionary containing list of revision numbers.

        Example:
        {
         "1": "1.1",
         "2": "1.2",
         "3": "1.3",
        }
        """
        fp = self.get_file_path(document_object)

        rcs = RCS()
        # current_rev = rcs.head(fp)          # Say, 1.4
        total_no_of_rev = int(rcs.info(fp)["total revisions"])         # Say, 4

        version_dict = {}
        for i, j in zip(range(total_no_of_rev), reversed(range(total_no_of_rev))):
            version_dict[(j + 1)] = rcs.calculateVersionNumber(fp, (i))

        return version_dict

    def get_file_path(self, document_object):
        """Returns absolute filesystem path for a json-file.

        This path is combination of :-
        (a) collection_directory_path: path to the collection-directory
        to which the given instance belongs
        (b) hashed_directory_structure: path built from object id based
        on the set hashed-directory-level
        (c) file_name: '.json' extension concatenated with object id of
        the given instance

        Arguments:
        (1) document_object -- an instance of a collection

        Returns: a string representing json-file's path
        """
        file_name = (document_object._id.__str__() + '.json')

        collection_dir = \
            (os.path.join(self.__RCS_REPO_DIR, \
                              document_object.collection_name))

        # Example:
        # if -- file_name := "523f59685a409213818e3ec6.json"
        # then -- collection_hash_dirs := "6/c/3/8/
        # -- from last (2^0)pos/(2^1)pos/(2^2)pos/(2^3)pos/../(2^n)pos"
        # here n := hash_level_num
        collection_hash_dirs = ""
        for pos in range(0, RCS_REPO_DIR_HASH_LEVEL):
            collection_hash_dirs += \
                (document_object._id.__str__()[-2**pos] + "/")

        file_path = \
            os.path.join(collection_dir, \
                             (collection_hash_dirs + file_name))

        return file_path

    def create_rcs_repo_collections(self, *versioning_collections):
        """Creates Revision Control System (RCS) repository.

        After creating rcs-repo, it also creates sub-directories
        for each collection inside it.

        Arguments:
        (1) versioning_collections -- a list representing collection-names

        Returns: Nothing
        """
        try:
            self.check_dir_path(self.__RCS_REPO_DIR)
        except OSError as ose:
            print("\n\n RCS repository not created!!!\n {0}: {1}\n"\
                      .format(ose.errno, ose.strerror))
        else:
            print("\n\n RCS repository created @ following path:\n {0}\n"\
                      .format(self.__RCS_REPO_DIR))

        # for collection in versioning_collections:
        #     rcs_repo_collection = os.path.join(self.__RCS_REPO_DIR, \
        #                                            collection)
        #     try:
        #         os.makedirs(rcs_repo_collection)
        #     except OSError as ose:
        #         print(" {0} collection-directory under RCS repository "\
        #                   "not created!!!\n Error #{1}: {2}\n"\
        #                   .format(collection, ose.errno, ose.strerror))
        #     else:
        #         print(" {0} collection-directory under RCS repository "\
        #                   "created @ following path:\n {1}\n"\
        #                   .format(collection, rcs_repo_collection))

    def create_or_replace_json_file(self, document_object=None):
        """Creates/Overwrites a json-file for passed document object in
        its respective hashed-directory structure.

        Arguments:
        (1) document_object -- an instance of document of a collection

        Returns: A boolean value indicating whether created successfully
        (a) True - if created
        (b) False - Otherwise
        """

        collection_tuple = (MetaType, GSystemType, GSystem, AttributeType, GAttribute, RelationType, GRelation, Filehive, Buddy)
        file_res = False    # True, if no error/exception occurred

        if document_object is not None and \
                isinstance(document_object, collection_tuple):

            file_path = self.get_file_path(document_object)

            json_data = document_object.to_json_type()
            #------------------------------------------------------------------
            # Creating/Overwriting data into json-file and rcs-file
            #------------------------------------------------------------------

            # file_mode as w:-
            #    Opens a file for writing only.
            #    Overwrites the file if the file exists.
            #    If the file does not exist, creates a new file for writing.
            file_mode = 'w'
            rcs_file = None

            try:
                self.check_dir_path(os.path.dirname(file_path))

                rcs_file = open(file_path, file_mode)
            except OSError as ose:
                print("\n\n Json-File not created: Hashed directory "\
                          "structure doesn't exists!!!")
                print("\n {0}: {1}\n".format(ose.errno, ose.strerror))
            except IOError as ioe:
                print(" " + str(ioe))
                print("\n\n Please refer following command from "\
                          "\"Get Started\" file:\n"\
                          "\tpython manage.py initrcsrepo\n")
            except Exception as e:
                print(" Unexpected error : " + str(e))
            else:
                rcs_file.write(json.dumps(json_data,
                                          sort_keys=True,
                                          indent=4,
                                          separators=(',', ': '),
                                          cls=NodeJSONEncoder
                                          )
                               )

                # TODO: Commit modifications done to the file into
                # it's rcs-version-file

                file_res = True
            finally:
                if rcs_file is not None:
                    rcs_file.close()

        else:
            # TODO: Throw/raise error having following message!
            # if document_object is None or
            # !isinstance(document_object, collection_tuple)

            msg = " Following instance is either invalid or " \
            + "not matching given instances-type list " + str(collection_tuple) + ":-" \
            + "\n\tObjectId: " + document_object._id.__str__() \
            + "\n\t    Type: " + document_object._type \
            + "\n\t    Name: " + document_object.get('name', '')
            raise RuntimeError(msg)

        return file_res

    def get_version_document(self, document_object, version_no=""):
        """Returns an object representing mongodb document instance of a given version number.
        """
        if version_no == "":
            version_no = self.get_current_version(document_object)

        fp = self.get_file_path(document_object)
        rcs = RCS()
        rcs.checkout((fp, version_no))

        json_data = ""
        with open(fp, 'r') as version_file:
            json_data = version_file.read()

	# assigning None value to key, which is not present in json_data compare to Node class keys
	null = 0
	import json
	json_dict = json.loads(json_data)
	json_node_keys = document_object.keys()
	json_dict_keys = json_dict.keys()
	diff_keys = list(set(json_node_keys)-set(json_dict_keys))
	if diff_keys:
		for each in diff_keys:
			json_dict[each]=None
	json_data = json.dumps(json_dict)

        # Converts the json-formatted data into python-specific format
        doc_obj = node_collection.from_json(json_data)

        rcs.checkin(fp)

        # Below Code temporary resolves the problem of '$oid' This
        # problem occurs when we convert mongodb's document into
        # json-format using mongokit's to_json_type() function - It
        # converts ObjectId() type into corresponding format
        # "{u'$oid': u'24-digit-hexstring'}" But actual problem comes
        # into picture when we have a field whose data-type is "list
        # of ObjectIds" In case of '_id' field (automatically created
        # by mongodb), mongokit handles this conversion and does so
        # But not in case of "list of ObjectIds", it still remains in
        # above given format and causes problem

        for k, v in doc_obj.iteritems():
            oid_list_str = ""
            oid_ObjectId_list = []
            if v and type(v) == list:
                oid_list_str = v.__str__()
                try:
                    if '$oid' in oid_list_str: #v.__str__():

                        for oid_dict in v:
                            oid_ObjectId = ObjectId(oid_dict['$oid'])
                            oid_ObjectId_list.append(oid_ObjectId)

                        doc_obj[k] = oid_ObjectId_list

                except Exception as e:
                    print "\n Exception for document's ("+doc_obj.name+") key ("+k+") -- ", str(e), "\n"

        return doc_obj

class NodeJSONEncoder(json.JSONEncoder):
  def default(self, o):
    if isinstance(o, ObjectId):
      return str(o)

    if isinstance(o, datetime.datetime):
      return o.strftime("%d/%m/%Y %H:%M:%S")

    return json.JSONEncoder.default(self, o)


class ActiveUsers(object):
    """docstring for ActiveUsers"""

    @staticmethod
    def get_active_id_session_keys():
        # Query all non-expired sessions
        # use timezone.now() instead of datetime.now() in latest versions of Django
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        # uid_list = []
        # uid_list_append = uid_list.append
        # session_key_list = []
        userid_session_key_dict = {}

        # Build a list of user ids from that query
        for session in sessions:
            data = session.get_decoded()
            user_id = data.get('_auth_user_id', 0)
            # if user_id:
            # uid_list_append(user_id)
            # session_key_list.append(session.session_key)
            userid_session_key_dict[user_id] = session.session_key

        return userid_session_key_dict

        # # Query all logged in users based on id list
        # if list_of_ids:
        #     return User.objects.filter(id__in=uid_list).values_list('id', flat=True)
        # else:
        #     return User.objects.filter(id__in=uid_list)


# class DjangoActiveUsersGroup(object):
#     """docstring for DjangoActiveUsersGroup"""

#     django_active_users_group_name = 'active_loggedin_and_buddy_users'

#     try:
#         active_loggedin_and_buddy_users_group = DjangoGroup.objects.get_or_create(name=django_active_users_group_name)[0]
#     except Exception, e:
#         print e
#         pass

#     # def __init__(self):
#     #     super(DjangoActiveUsersGroup, self).__init__()

#     @classmethod
#     def addto_user_set(cls, user_id=0):
#         cls.active_loggedin_and_buddy_users_group.user_set.add(user_id)
#         return cls.active_loggedin_and_buddy_users_group.user_set.all()

#     @classmethod
#     def removefrom_user_set(cls, user_id=0):
#         cls.active_loggedin_and_buddy_users_group.user_set.remove(user_id)
#         return cls.active_loggedin_and_buddy_users_group.user_set.all()

#     @classmethod
#     def update_user_set(cls, add=[], remove=[]):
#         # print "add : ", add
#         # print "remove : ", remove
#         for each_userid_toadd in add:
#             cls.addto_user_set(each_userid_toadd)

#         for each_userid_toremove in remove:
#             cls.removefrom_user_set(each_userid_toremove)

#         return cls.active_loggedin_and_buddy_users_group.user_set.all()

#     @classmethod
#     def get_all_user_set_objects_list(cls):
#         return cls.active_loggedin_and_buddy_users_group.user_set.all()

#     @classmethod
#     def get_all_user_set_ids_list(cls):
#         return cls.active_loggedin_and_buddy_users_group.user_set.values_list('id', flat=True)




# Benchmarking Class Defination
@connection.register
class Benchmark(DjangoDocument):

  objects = models.Manager()

  collection_name = 'Benchmarks'

  structure = {
    '_type':unicode,
    'name': unicode,
    'time_taken':unicode,
    'parameters':unicode,
    'size_of_parameters':unicode,
    'function_output_length':unicode,
    'calling_url':unicode,
    'last_update': datetime.datetime,
    'action' : basestring,
    'user' : basestring,
    'session_key' : basestring,
    'group' : basestring,
    'has_data' : dict
  }

  required_fields = ['name']
  use_dot_notation = True

  def __unicode__(self):
    return self._id

  def identity(self):
    return self.__unicode__()

# Analytics Class Defination
@connection.register
class Analytics(DjangoDocument):

  objects = models.Manager()

  collection_name = 'analytics_collection'

  structure = {
    'timestamp': datetime.datetime,
    'action' : dict,
    'user' : dict,
    'obj' : dict,
    'group_id' : basestring,
    'session_key' : basestring
  }

  required_fields = ['timestamp']
  use_dot_notation = True

  def __unicode__(self):
    return self._id

  def identity(self):
    return self.__unicode__()


#  TRIPLE CLASS DEFINITIONS
@connection.register
class Triple(DjangoDocument):

  objects = models.Manager()

  collection_name = 'Triples'
  structure = {
    '_type': unicode,
    'name': unicode,
    'subject_scope': basestring,
    'subject': ObjectId,  # ObjectId's of GSystem Class
    'lang': basestring,  # Put validation for standard language codes
    'status': STATUS_CHOICES_TU
  }

  required_fields = ['name', 'subject']
  use_dot_notation = True
  use_autorefs = True

  ########## Built-in Functions (Overridden) ##########
  def __unicode__(self):
    return self._id

  def identity(self):
    return self.__unicode__()

  def save(self, *args, **kwargs):
    is_new = False
    if "_id" not in self:
      is_new = True  # It's a new document, hence yet no ID!"

    """
    Check for correct GSystemType match in AttributeType and GAttribute, similarly for RelationType and GRelation
    """
    subject_system_flag = False

    subject_id = self.subject
    subject_document = node_collection.one({"_id": self.subject})
    subject_name = subject_document.name

    subject_type_list = []
    subject_member_of_list = []
    name_value = u""

    if self._type == "GAttribute":
      attribute_type_name = self.attribute_type['name']
      attribute_object_value = unicode(self.object_value)

      self.name = "%(subject_name)s -- %(attribute_type_name)s -- %(attribute_object_value)s" % locals()
      name_value = self.name

      subject_type_list = self.attribute_type['subject_type']
      subject_member_of_list = subject_document.member_of

      intersection = set(subject_member_of_list) & set(subject_type_list)
      if intersection:
        subject_system_flag = True

      else:
        # If instersection is not found with member_of fields' ObjectIds,
        # then check for type_of field of each one of the member_of node
        for gst_id in subject_member_of_list:
          gst_node = node_collection.one({'_id': gst_id}, {'type_of': 1})
          if set(gst_node.type_of) & set(subject_type_list):
            subject_system_flag = True
            break

    elif self._type == "GRelation":
      subject_type_list = self.relation_type['subject_type']
      object_type_list = self.relation_type['object_type']

      left_subject_member_of_list = subject_document.member_of
      relation_type_name = self.relation_type['name']
      if META_TYPE[4] in self.relation_type.member_of_names_list:
        #  print META_TYPE[3], self.relation_type.member_of_names_list,"!!!!!!!!!!!!!!!!!!!!!"
        # Relationship Other than Binary one found; e.g, Triadic
        # Single relation: [ObjectId(), ObjectId(), ...]
        # Multi relation: [[ObjectId(), ObjectId(), ...], [ObjectId(), ObjectId(), ...], ...]
        right_subject_member_of_list = []
        right_subject_member_of_list_append = right_subject_member_of_list.append

        right_subject_name_list = []
        right_subject_name_list_append = right_subject_name_list.append
        print self.right_subject,"%%%%%%%%%%%%%",type(self.right_subject)
        for each in self.right_subject:
          # Here each is an ObjectId
          right_subject_document = node_collection.one({
            "_id": each
          }, {
            "name": 1, "member_of": 1
          })

          right_subject_member_of_list_append(right_subject_document.member_of)
          right_subject_name_list_append(right_subject_document.name)

        right_subject_name_list_str = " >> ".join(right_subject_name_list)

        self.name = "%(subject_name)s -- %(relation_type_name)s -- %(right_subject_name_list_str)s" % locals()

        # Very much required as list comparison using set doesn't work
        # with list as it's sub-elements
        # Hence, converting list into comma separated values by extending
        # with other comma-separated values from another list(s)
        object_type_list = list(chain.from_iterable(object_type_list))
        right_subject_member_of_list = list(chain.from_iterable(right_subject_member_of_list))


      else:
          #META_TYPE[3] in self.relation_type.member_of_names_list:
          # If Binary relationship found
          # Single relation: ObjectId()
          # Multi relation: [ObjectId(), ObjectId(), ...]
          right_subject_document = node_collection.one({'_id': self.right_subject})

          right_subject_member_of_list = right_subject_document.member_of
          right_subject_name = right_subject_document.name

          self.name = "%(subject_name)s -- %(relation_type_name)s -- %(right_subject_name)s" % locals()


      name_value = self.name

      left_intersection = set(subject_type_list) & set(left_subject_member_of_list)
      right_intersection = set(object_type_list) & set(right_subject_member_of_list)
      if left_intersection and right_intersection:
        subject_system_flag = True

      else:
        left_subject_system_flag = False
        if left_intersection:
          left_subject_system_flag = True

        else:
          for gst_id in left_subject_member_of_list:
            gst_node = node_collection.one({'_id': gst_id}, {'type_of': 1})
            if set(gst_node.type_of) & set(subject_type_list):
              left_subject_system_flag = True
              break


        right_subject_system_flag = False
        if right_intersection:
          right_subject_system_flag = True

        else:
          for gst_id in right_subject_member_of_list:
            gst_node = node_collection.one({'_id': gst_id}, {'type_of': 1})
            if set(gst_node.type_of) & set(object_type_list):
              right_subject_system_flag = True
              break

        if left_subject_system_flag and right_subject_system_flag:
          subject_system_flag = True

    if self._type =="GRelation" and subject_system_flag == False:
      # print "The 2 lists do not have any common element"
      raise Exception("\n Cannot create the GRelation ("+name_value+") as the subject/object that you have mentioned is not a member of a GSytemType for which this RelationType is defined!!!\n")

    if self._type =="GAttribute" and subject_system_flag == False:
      # print "\n The 2 lists do not have any common element\n"
      error_message = "\n "+name_value+ " -- subject_type_list ("+str(subject_type_list)+") -- subject_member_of_list ("+str(subject_member_of_list)+") \n"
      raise Exception(error_message + "Cannot create the GAttribute ("+name_value+") as the subject that you have mentioned is not a member of a GSystemType which this AttributeType is defined")

    #it's me
    #check for data_type in GAttribute case. Object value of the GAttribute must have the same type as that of the type specified in AttributeType
    """if self._type == "GAttribute": data_type_in_attribute_type =
    self.attribute_type['data_type'] data_type_of_object_value =
    type(self.object_value) print "Attribute:: " +
    str(data_type_in_attribute_type) print "Value:: " +
    str(data_type_of_object_value) if data_type_in_attribute_type !=
    data_type_of_object_value: raise Exception("The DataType of the
    value you have entered for this attribute is not correct. Pls ener
    a value with type ---> " + str(data_type_in_attribute_type))

    """
    #end of data_type_check

    super(Triple, self).save(*args, **kwargs)

    history_manager = HistoryManager()
    rcs_obj = RCS()
    if is_new:
      # Create history-version-file
      if history_manager.create_or_replace_json_file(self):
        fp = history_manager.get_file_path(self)
        message = "This document (" + self.name + ") is created on " + datetime.datetime.now().strftime("%d %B %Y")
        rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

    else:
      # Update history-version-file
      fp = history_manager.get_file_path(self)

      try:
          rcs_obj.checkout(fp)
      except Exception as err:
          try:
              if history_manager.create_or_replace_json_file(self):
                  fp = history_manager.get_file_path(self)
                  message = "This document (" + self.name + ") is re-created on " + datetime.datetime.now().strftime("%d %B %Y")
                  rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

          except Exception as err:
              print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be re-created!!!\n"
              node_collection.collection.remove({'_id': self._id})
              raise RuntimeError(err)

      try:
          if history_manager.create_or_replace_json_file(self):
              message = "This document (" + self.name + ") is lastly updated on " + datetime.datetime.now().strftime("%d %B %Y")
              rcs_obj.checkin(fp, 1, message.encode('utf-8'))

      except Exception as err:
          print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be updated!!!\n"
          raise RuntimeError(err)


@connection.register
class GAttribute(Triple):
    structure = {
        'attribute_type_scope': basestring,
        'attribute_type': AttributeType,  # Embedded document of AttributeType Class
        'object_value_scope': basestring,
        'object_value': None  # value -- it's data-type, is determined by attribute_type field
    }

    indexes = [
        {
            # 1: Compound index
            'fields': [
                ('_type', INDEX_ASCENDING), ('subject', INDEX_ASCENDING), \
                ('attribute_type.$id', INDEX_ASCENDING), ('status', INDEX_ASCENDING)
            ],
            'check': False  # Required because $id is not explicitly specified in the structure
        }
    ]

    required_fields = ['attribute_type', 'object_value']
    use_dot_notation = True
    use_autorefs = True                   # To support Embedding of Documents


@connection.register
class GRelation(Triple):
    structure = {
        'relation_type_scope': basestring,
        'relation_type': RelationType,  # DBRef of RelationType Class
        'right_subject_scope': basestring,
        # ObjectId's of GSystems Class / List of list of ObjectId's of GSystem Class
        'right_subject': OR(ObjectId, list)
    }

    indexes = [{
        # 1: Compound index
        'fields': [
            ('_type', INDEX_ASCENDING), ('subject', INDEX_ASCENDING), \
            ('relation_type.$id'), ('status', INDEX_ASCENDING), \
            ('right_subject', INDEX_ASCENDING)
        ],
        'check': False  # Required because $id is not explicitly specified in the structure
    }, {
        # 2: Compound index
        'fields': [
            ('_type', INDEX_ASCENDING), ('right_subject', INDEX_ASCENDING), \
            ('relation_type.$id'), ('status', INDEX_ASCENDING)
        ],
        'check': False  # Required because $id is not explicitly specified in the structure
    }]

    required_fields = ['relation_type', 'right_subject']
    use_dot_notation = True
    use_autorefs = True  # To support Embedding of Documents


@connection.register
class Buddy(DjangoDocument):
    """
    Enables logged in user to add buddy.
    """

    collection_name = 'Buddies'

    structure = {
        '_type': unicode,
        'loggedin_userid': int,
        'session_key': basestring,
        'buddy_in_out': dict,
            # e.g:
            # buddy_in_out = {
            #           "auth_id": [
            #                         {"in": datetime.datetime, "out": datetime.datetime},
            #                         {"in": datetime.datetime, "out": datetime.datetime}
            #                    ]
            #           }
        'starts_at': datetime.datetime,
        'ends_at': datetime.datetime
    }

    required_fields = ['loggedin_userid', 'session_key']

    use_dot_notation = True

    @staticmethod
    def query_buddy_obj(loggedin_userid, session_key):
        '''
        query to get buddy object from following parameters:
            - loggedin_userid: django User ID.
            - session_key: unique session key generated by django session middleware.
        '''
        return buddy_collection.one({
                                        'loggedin_userid': int(loggedin_userid),
                                        'session_key': str(session_key)
                                    })


    def get_filled_buddy_obj(self,
                            loggedin_userid,
                            session_key,
                            buddy_in_out={},
                            starts_at=datetime.datetime.now(),
                            ends_at=None):

        self['loggedin_userid']= loggedin_userid
        self['session_key']    = session_key
        self['buddy_in_out']   = buddy_in_out
        self['starts_at']      = starts_at
        self['ends_at']        = ends_at

        return self


    @staticmethod
    def is_buddy_active(single_buddy_in_out_list):
        '''
        returns True or False 'bool' type value.

            - True : If buddy is active
                    (i.e: holding active session dict having {'out': None})

            - False: If buddy is not active
                    (i.e: holding active session dict having {'out': datetime.datetime})
        '''
        return (not bool(Buddy.get_latest_in_out_dict(single_buddy_in_out_list)['out']))


    @staticmethod
    def get_latest_in_out_dict(single_buddy_in_out_list):
        '''
        Returns last in out dict of buddy (if it exists)
        else returns empty structured dict.
        '''
        if len(single_buddy_in_out_list) > 0:
            return single_buddy_in_out_list[-1:][0]
        else:
            return { 'in': None, 'out': None }


    def get_active_authid_list_from_single_buddy(self):

        active_buddy_auth_list = []

        for auth_oid, in_out_list in self.buddy_in_out.iteritems():
            # if len(in_out_list) > 0:
            #     if not in_out_list[-1:][0]['out']:
                    # active_buddy_auth_list.append(auth_oid)
            if self.is_buddy_active(in_out_list):
                active_buddy_auth_list.append(auth_oid)

        # print "active_buddy_auth_list", active_buddy_auth_list
        return active_buddy_auth_list


    def add_buddy(self):
        pass


    def remove_buddy(self, buddy_authid):
        '''
        Removing/Relesing single buddy.
        and returning modified self object (without doing DB .save() operation).
        '''

        # only active buddies will be released
        if self.is_buddy_active(self.buddy_in_out[buddy_authid]):

            # this means buddy is successfully joined and not released.
            # now we need to release this buddy by adding datetime.datetime to 'out'
            self.get_latest_in_out_dict(self.buddy_in_out[buddy_authid])['out'] = datetime.datetime.now()

            return self


    def remove_all_buddies(self):
        '''
        Removes/releses all existing-active buddies.
        '''
        active_buddy_authid_list = self.get_active_authid_list_from_single_buddy()

        for each_buddy_authid in active_buddy_authid_list:
            self.get_latest_in_out_dict(self.buddy_in_out[each_buddy_authid])['out'] = datetime.datetime.now()

        return self


    def end_buddy_session(self):
        '''
        terminates the buddy session:
            - removes all buddies.
            - adds end time ('ends_at').
            - buddy object will be saved using .save() method.
        '''

        active_buddy_authid_list = self.get_active_authid_list_from_single_buddy()

        self = self.remove_all_buddies()
        self.ends_at = datetime.datetime.now()
        self.save()

        # active_buddy_userids_list = Author.get_user_id_list_from_author_oid_list(active_buddy_authid_list)
        # DjangoActiveUsersGroup.update_user_set(remove=active_buddy_userids_list)

        return self


    @staticmethod
    def get_added_and_removed_buddies_dict(existing_userids_list, updated_userids_list):

        # Example Set Operations:
        #
        # existing = {1, 2, 3}
        # updated  = {3, 4, 5}
        #
        # updated - existing
        # {4, 5}
        # ------- indicates added user's w.r.t updated
        #
        # existing - updated
        # {1, 2}
        # ------- indicates removed users w.r.t updated

        result_dict = {'added': [], 'removed': []}

        result_dict['added'] = list(set(updated_userids_list) - set(existing_userids_list))

        result_dict['removed'] = list(set(existing_userids_list) - set(updated_userids_list))

        return result_dict


    @staticmethod
    def get_active_buddies_user_ids_list():

        active_users = ActiveUsers.get_active_id_session_keys()
        active_users_session_keys = active_users.values()
        active_user_ids = active_users.keys()

        Buddy.close_incomplete_buddies(active_users)
        active_buddies = buddy_collection.find({
                                    'session_key': {'$in': active_users_session_keys},
                                    'ends_at': None
                                })

        active_buddy_auth_list = []
        active_buddy_userids_list = active_user_ids

        for each_buddy in active_buddies:
            active_buddy_auth_list += each_buddy.get_active_authid_list_from_single_buddy()
            active_buddy_userids_list.append(each_buddy['loggedin_userid'])

        active_buddy_userids_list += Author.get_user_id_list_from_author_oid_list(active_buddy_auth_list)
        active_buddy_userids_list = list(set(active_buddy_userids_list))

        return active_buddy_userids_list


    @staticmethod
    def close_incomplete_buddies(active_users=None):

        if not active_users:
            active_users = ActiveUsers.get_active_id_session_keys()

        active_users_session_keys = active_users.values()
        incomplete_buddies = buddy_collection.find({
                                    'session_key': {'$nin': active_users_session_keys},
                                    'ends_at': None
                                })

        for each_incomplete_buddy in incomplete_buddies:
            each_incomplete_buddy.end_buddy_session()


    @staticmethod
    def update_buddies(loggedin_userid, session_key, buddy_auth_ids_list=[]):
        buddy_obj = buddy_collection.one({
                    'session_key': str(session_key),
                    'loggedin_userid': int(loggedin_userid)
                })

        if not buddy_obj:
            # it's a new buddy-session. So create a new buddy instance.
            buddy_obj = buddy_collection.collection.Buddy()
            buddy_obj = buddy_obj.get_filled_buddy_obj(loggedin_userid, session_key)

        current_active_buddy_auth_list = buddy_obj.get_active_authid_list_from_single_buddy()

        if set(current_active_buddy_auth_list) == set(buddy_auth_ids_list):
            return current_active_buddy_auth_list

        new_in_dict = { 'in': datetime.datetime.now(), 'out': None }
        existing_buddy_in_out_auth_list  = buddy_obj.buddy_in_out.keys()

        # list of all buddies auth ids:
        all_buddies = list(set(existing_buddy_in_out_auth_list + buddy_auth_ids_list))

        for each_buddy in all_buddies:
            # each_buddy is author _id

            if each_buddy in buddy_auth_ids_list:
                if each_buddy in existing_buddy_in_out_auth_list:
                    # this means, user was/is already buddy and already contains some entries/dicts.
                    # in this we must ensure that last dict's out is None.

                    if not Buddy.is_buddy_active(buddy_obj.buddy_in_out[each_buddy]):
                        # this means buddy is successfully joined and released.
                        # now buddy is getting in again. so make new dict and append.
                        buddy_obj.buddy_in_out[each_buddy].append(new_in_dict)

                else:
                    buddy_obj.buddy_in_out[each_buddy] = [new_in_dict]

            else:
                # this means, user was/is already buddy and already contains some entries/dicts.
                if each_buddy in existing_buddy_in_out_auth_list:

                    buddy_obj.remove_buddy(each_buddy)

        active_buddy_auth_list = buddy_obj.get_active_authid_list_from_single_buddy()

        if current_active_buddy_auth_list != active_buddy_auth_list:
            buddy_obj.save()

            added_removed_buddies_dict = Buddy.get_added_and_removed_buddies_dict(
                                                        current_active_buddy_auth_list,
                                                        active_buddy_auth_list
                                                        )


            added_buddies_userids_list = Author.get_user_id_list_from_author_oid_list(added_removed_buddies_dict['added'])
            # print "added_buddies_userids_list : ", added_buddies_userids_list
            removed_buddies_userids_list = Author.get_user_id_list_from_author_oid_list(added_removed_buddies_dict['removed'])
            # print "removed_buddies_userids_list : ", removed_buddies_userids_list

            # DjangoActiveUsersGroup.update_user_set(
            #                                     add=added_buddies_userids_list,
            #                                     remove=removed_buddies_userids_list
            #                                     )

        else:
            buddy_obj = None

        return active_buddy_auth_list


    def save(self, *args, **kwargs):

        is_new = False if ('_id' in self) else True

        super(Buddy, self).save(*args, **kwargs)

        # storing Filehive JSON in RSC system:
        history_manager = HistoryManager()
        rcs_obj = RCS()

        if is_new:

            # Create history-version-file
            if history_manager.create_or_replace_json_file(self):
                fp = history_manager.get_file_path(self)
                message = "This document of Buddy (having session_key: " + str(self.session_key) + " and user id: " + str(self.loggedin_userid) + " ) is created on " + str(datetime.datetime.now())
                rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

        else:
            # Update history-version-file
            fp = history_manager.get_file_path(self)

            try:
                rcs_obj.checkout(fp)

            except Exception as err:
                try:
                    if history_manager.create_or_replace_json_file(self):
                        fp = history_manager.get_file_path(self)
                        message = "This document of Buddy (having session_key: " + str(self.session_key) + " and user id: " + str(self.loggedin_userid) + " ) is re-created on " + str(datetime.datetime.now())
                        rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

                except Exception as err:
                    print "\n DocumentError: This document (", self._id, ":", str(self.session_key), ") can't be re-created!!!\n"
                    node_collection.collection.remove({'_id': self._id})
                    raise RuntimeError(err)

            try:
                if history_manager.create_or_replace_json_file(self):
                    message = "This document of Buddy (having session_key: " + str(self.session_key) + " and user id: " + str(self.loggedin_userid) + " ) is lastly updated on " + str(datetime.datetime.now())
                    rcs_obj.checkin(fp, 1, message.encode('utf-8'))

            except Exception as err:
                print "\n DocumentError: This document (", self._id, ":", str(self.session_key), ") can't be updated!!!\n"
                raise RuntimeError(err)



####################################### Added on 19th June 2014 for SEARCH ##############################


@connection.register
class ReducedDocs(DjangoDocument):
	structure={
            '_type': unicode,
            'content':dict,  #This contains the content in the dictionary format
            'orignal_id':ObjectId, #The object ID of the orignal document
            'required_for':unicode,
            'is_indexed':bool, #This will be true if the map reduced document has been indexed. If it is not then it will be false
	}
	use_dot_notation = True

@connection.register
class ToReduceDocs(DjangoDocument):
	structure={
    '_type': unicode,
		'doc_id':ObjectId,
		'required_for':unicode,
	}
	use_dot_notation = True

@connection.register
class IndexedWordList(DjangoDocument):
	structure={
    '_type': unicode,
		'word_start_id':float,
		'words':dict,
		'required_for':unicode,
	}
	use_dot_notation = True
	#word_start_id = 0 --- a ,1---b,2---c .... 25---z,26--misc.

# This is like a temperory holder, where you can hold any node temporarily and later permenently save in database
@connection.register
class node_holder(DjangoDocument):
        objects = models.Manager()
        structure={
            '_type': unicode,
            'details_to_hold':dict
        }
        required_fields = ['details_to_hold']
        use_dot_notation = True

"""
@connection.register
class allLinks(DjangoDocument):
    structure = {
	'member_of':ObjectId,
	'link':unicode,
	'required_for':unicode,
    }
    # required_fields = ['member_of', 'link']
    use_dot_notation = True
"""

# DATABASE Variables
db = get_database()

node_collection     = db[Node.collection_name].Node
triple_collection   = db[Triple.collection_name].Triple
benchmark_collection= db[Benchmark.collection_name]
filehive_collection = db[Filehive.collection_name].Filehive
buddy_collection    = db[Buddy.collection_name].Buddy

gridfs_collection   = db["fs.files"]
chunk_collection    = db["fs.chunks"]

import signals
