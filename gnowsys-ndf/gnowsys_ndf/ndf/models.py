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
from celery import task
from django.template.defaultfilters import slugify
from django.core.cache import cache

from django_mongokit import connection
from django_mongokit import get_database
from django_mongokit.document import DjangoDocument
from django.core.files.images import get_image_dimensions

from mongokit import IS, OR
from mongokit import INDEX_ASCENDING, INDEX_DESCENDING

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from registration.signals import user_registered

# imports from application folders/files
from gnowsys_ndf.settings import RCS_REPO_DIR, MEDIA_ROOT
from gnowsys_ndf.settings import RCS_REPO_DIR_HASH_LEVEL
from gnowsys_ndf.settings import MARKUP_LANGUAGE
from gnowsys_ndf.settings import MARKDOWN_EXTENSIONS
from gnowsys_ndf.settings import GSTUDIO_GROUP_AGENCY_TYPES, GSTUDIO_GROUP_AGENCY_TYPES_DEFAULT, GSTUDIO_AUTHOR_AGENCY_TYPES
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_COPYRIGHT, GSTUDIO_DEFAULT_LICENSE
from gnowsys_ndf.settings import META_TYPE
from gnowsys_ndf.settings import GSTUDIO_BUDDY_LOGIN
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.views.utils import add_to_list, cast_to_data_type


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

NODE_ACCESS_POLICY = (
    ('PUBLIC'),
    ('PRIVATE')
)

TYPES_OF_GROUP = (
    ('PUBLIC'),
    ('PRIVATE'),
    ('ANONYMOUS')
)
TYPES_OF_GROUP_DEFAULT = 'PUBLIC'

EDIT_POLICY = (
    ('EDITABLE_NON_MODERATED'),
    ('EDITABLE_MODERATED'),
    ('NON_EDITABLE')
)
EDIT_POLICY_DEFAULT = 'EDITABLE_NON_MODERATED'

SUBSCRIPTION_POLICY = (
    ('OPEN'),
    ('BY_REQUEST'),
    ('BY_INVITATION'),
)
SUBSCRIPTION_POLICY_DEFAULT = 'OPEN'

EXISTANCE_POLICY = (
    ('ANNOUNCED'),
    ('NOT_ANNOUNCED')
)
EXISTANCE_POLICY_DEFAULT = 'ANNOUNCED'

LIST_MEMBER_POLICY = (
    ('DISCLOSED_TO_MEM'),
    ('NOT_DISCLOSED_TO_MEM')
)
LIST_MEMBER_POLICY_DEFAULT = 'DISCLOSED_TO_MEM'

ENCRYPTION_POLICY = (
    ('NOT_ENCRYPTED'),
    ('ENCRYPTED')
)
ENCRYPTION_POLICY_DEFAULT = 'NOT_ENCRYPTED'


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

TYPES_LIST = ['GSystemType', 'RelationType', 'AttributeType', 'MetaType', 'ProcessType']

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

    required_fields = ['name', '_type', 'created_by'] # 'group_set' to be included
                                        # here after the default
                                        # 'Administration' group is
                                        # ready.
    default_values = {
                        'name': u'',
                        'altnames': u'',
                        'plural': u'',
                        'prior_node': [],
                        'post_node': [],
                        'language': ('en', 'English'),
                        'type_of': [],
                        'member_of': [],
                        'access_policy': u'PUBLIC',
                        'created_at': datetime.datetime.now,
                        # 'created_by': int,
                        'last_update': datetime.datetime.now,
                        # 'modified_by': int,
                        # 'contributors': [],
                        'location': [],
                        'content': u'',
                        'content_org': u'',
                        'group_set': [],
                        'collection_set': [],
                        'property_order': [],
                        # 'start_publication': datetime.datetime.now,
                        'tags': [],
                        # 'featured': True,
                        'url': u'',
                        # 'comment_enabled': bool,
                        # 'login_required': bool,
                        # 'password': basestring,
                        'status': u'PUBLISHED',
                        'rating':[],
                        'snapshot':{}
                    }

    validators = {
        'name': lambda x: x.strip() not in [None, ''],
        'created_by': lambda x: isinstance(x, int) and (x != 0),
        'access_policy': lambda x: x in (list(NODE_ACCESS_POLICY) + [None])
    }

    use_dot_notation = True


    def add_in_group_set(self, group_id):
        if group_id not in self.group_set:
            self.group_set.append(ObjectId(group_id))
        return self


    def remove_from_group_set(self, group_id):
        if group_id in self.group_set:
            self.group_set.remove(ObjectId(group_id))
        return self


    # custom methods provided for Node class
    def fill_node_values(self, request=HttpRequest(), **kwargs):

        user_id = kwargs.get('created_by', None)
        # dict to sum both dicts, kwargs and request.POST
        values_dict = {}
        if request:
            if request.POST:
                values_dict.update(request.POST.dict())
            if (not user_id) and request.user:
                user_id = request.user.id
        # adding kwargs dict later to give more priority to values passed via kwargs.
        values_dict.update(kwargs)

        # handling storing user id values.
        if user_id:
            if not self['created_by'] and ('created_by' not in values_dict):
                # if `created_by` field is blank i.e: it's new node and add/fill user_id in it.
                # otherwise escape it (for subsequent update/node-modification).
                values_dict.update({'created_by': user_id})
            if 'modified_by' not in values_dict:
                values_dict.update({'modified_by': user_id})
            if 'contributors' not in values_dict:
                values_dict.update({'contributors': add_to_list(self.contributors, user_id)})

        # filter keys from values dict there in node structure.
        node_str = Node.structure
        node_str_keys_set = set(node_str.keys())
        values_dict_keys_set = set(values_dict.keys())

        for each_key in values_dict_keys_set.intersection(node_str_keys_set):
            temp_prev_val = self[each_key]
            # checking for proper casting for each field
            if isinstance(node_str[each_key], type):
                node_str_data_type = node_str[each_key].__name__
            else:
                node_str_data_type = node_str[each_key]
            casted_new_val = cast_to_data_type(values_dict[each_key], node_str_data_type)
            # check for uniqueness and addition of prev values for dict, list datatype values
            self[each_key] = casted_new_val


        # # 'name': unicode,
        # name = self.name
        # if kwargs.has_key('name'):
        #     name = kwargs.get('name', '')
        # elif request:
        #     name = request.POST.get('name', '').strip()
        # self.name = unicode(name) if name else self.name

        # # 'altnames': unicode,
        # if kwargs.has_key('altnames'):
        #     self.altnames = kwargs.get('altnames', self.name)
        # elif request:
        #     self.altnames = request.POST.get('altnames', self.name).strip()
        # self.altnames = unicode(self.altnames)

        # # 'plural': unicode,
        # if kwargs.has_key('plural'):
        #     self.plural = kwargs.get('plural', None)
        # elif request:
        #     self.plural = request.POST.get('plural', None)
        # # self.plural = unicode(plural)

        # # 'prior_node': [ObjectId],
        # if kwargs.has_key('prior_node'):
        #     self.prior_node = kwargs.get('prior_node', [])
        # elif request:
        #     self.prior_node = request.POST.get('prior_node', [])
        # # self.prior_node = prior_node
        # if self.prior_node and not isinstance(self.prior_node, list):
        #     self.prior_node = [ObjectId(each) for each in self.prior_node]

        # # 'post_node': [ObjectId]
        # if kwargs.has_key('post_node'):
        #     self.post_node = kwargs.get('post_node', [])
        # elif request:
        #     self.post_node = request.POST.get('post_node', [])
        # # self.post_node = post_node
        # if self.post_node and not isinstance(self.post_node, list):
        #     self.post_node = [ObjectId(each) for each in self.post_node]

        # # 'language': (basestring, basestring)
        # if kwargs.has_key('language'):
        #     self.language = kwargs.get('language', ('en', 'English'))
        # elif request:
        #     self.language = request.POST.get('language', ('en', 'English'))
        # # self.language = language

        # # 'type_of': [ObjectId]
        # if kwargs.has_key('type_of'):
        #     self.type_of = kwargs.get('type_of', [])
        # elif request:
        #     self.type_of = request.POST.get('type_of', [])
        # # self.type_of = type_of
        # if self.type_of and not isinstance(self.type_of, list):
        #     self.type_of = [ObjectId(each) for each in self.type_of]

        # # 'member_of': [ObjectId]
        # if kwargs.has_key('member_of'):
        #     self.member_of = kwargs.get('member_of', [])
        # elif request:
        #     self.member_of = request.POST.get('member_of', [])
        # self.member_of = [ObjectId(self.member_of)] if self.member_of and not isinstance(self.member_of, list) else self.member_of
        # # if member_of and not isinstance(member_of, list):
        # #     self.member_of = [ObjectId(each) for each in member_of]

        # # 'access_policy': unicode
        # if kwargs.has_key('access_policy'):
        #     self.access_policy = kwargs.get('access_policy', u'PUBLIC')
        # elif request:
        #     self.access_policy = request.POST.get('access_policy', u'PUBLIC')
        # # self.access_policy = unicode(access_policy)

        # # 'created_at': datetime.datetime
        # #   - this will be system generated (while instantiation time), always.

        # # 'last_update': datetime.datetime,
        # #   - this will be system generated (from save method), always.

        # created_by = 0
        # # 'created_by': int
        # if not self.created_by:
        #     if kwargs.has_key('created_by'):
        #         self.created_by = kwargs.get('created_by', '')
        #     elif request and request.user.is_authenticated():
        #         self.created_by = request.user.id
        #     self.created_by = int(self.created_by) if self.created_by else 0

        # modified_by = 0
        # # 'modified_by': int, # test required: only ids of Users
        # if kwargs.has_key('modified_by'):
        #     self.modified_by = kwargs.get('modified_by', None)
        # elif request:
        #     if hasattr(request, 'user'):
        #         self.modified_by = request.user.id
        #     elif kwargs.has_key('created_by'):
        #         self.modified_by = self.created_by
        # self.modified_by = int(self.modified_by) if self.modified_by else self.created_by

        # contributors = []
        # self.contributors = contributors
        # # 'contributors': [int]
        # if kwargs.has_key('contributors'):
        #     self.contributors = kwargs.get('contributors', [self.created_by])
        # elif request:
        #     self.contributors = request.POST.get('contributors', [self.created_by])
        # if self.contributors and not isinstance(self.contributors, list):
        #     self.contributors = [int(each) for each in self.contributors]

        # # 'location': [dict]
        # if kwargs.has_key('location'):
        #     self.location = kwargs.get('location', [])
        # elif request:
        #     self.location = request.POST.get('location', [])
        #     self.location = list(self.location) if not isinstance(self.location, list) else self.location

        # # 'content': unicode
        # if kwargs.has_key('content'):
        #     self.content = kwargs.get('content', '')
        # elif request:
        #     self.content = request.POST.get('content', '')
        # self.content = unicode(self.content)

        # # 'content_org': unicode
        # if kwargs.has_key('content_org'):
        #     self.content_org = kwargs.get('content_org', '')
        # elif request:
        #     self.content_org = request.POST.get('content_org', '')
        # self.content_org = unicode(self.content_org)

        # # 'group_set': [ObjectId]
        # if kwargs.has_key('group_set'):
        #     self.group_set = kwargs.get('group_set', [])
        # elif request:
        #     self.group_set = request.POST.get('group_set', [])
        # if self.group_set and not isinstance(self.group_set, list):
        #     self.group_set = [self.group_set]
        #     self.group_set = [ObjectId(each) for each in self.group_set]

        # # 'collection_set': [ObjectId]
        # if kwargs.has_key('collection_set'):
        #     self.collection_set = kwargs.get('collection_set', [])
        # elif request:
        #     self.collection_set = request.POST.get('collection_set', [])
        # if self.collection_set and not isinstance(self.collection_set, list):
        #     self.collection_set = [ObjectId(each) for each in self.collection_set]

        # # 'property_order': []
        # if kwargs.has_key('property_order'):
        #     self.property_order = kwargs.get('property_order', [])
        # elif request:
        #     self.property_order = request.POST.get('property_order', [])
        # self.property_order = list(self.property_order) if not isinstance(self.property_order, list) else self.property_order

        # # 'start_publication': datetime.datetime,
        # if kwargs.has_key('start_publication'):
        #     self.start_publication = kwargs.get('start_publication', None)
        # elif request:
        #     self.start_publication = request.POST.get('start_publication', None)

        # # self.start_publication = datetime.datetime(start_publication) if not isinstance(start_publication, datetime.datetime) elif request start_publication

        # # 'tags': [unicode],
        # if kwargs.has_key('tags'):
        #     self.tags = kwargs.get('tags', [])
        # elif request:
        #     self.tags = request.POST.get('tags', [])
        # if self.tags and not isinstance(self.tags, list):
        #     self.tags = [unicode(each.strip()) for each in self.tags.split(',')]

        # # 'featured': bool,
        # if kwargs.has_key('featured'):
        #     self.featured = kwargs.get('featured', None)
        # elif request:
        #     self.featured = request.POST.get('featured', None)
        # self.featured = bool(self.featured)

        # # 'url': unicode,
        # if kwargs.has_key('url'):
        #     self.url = kwargs.get('url', None)
        # elif request:
        #     self.url = request.POST.get('url', None)
        # self.url = unicode(self.url)

        # # 'comment_enabled': bool,
        # if kwargs.has_key('comment_enabled'):
        #     self.comment_enabled = kwargs.get('comment_enabled', None)
        # elif request:
        #     self.comment_enabled = request.POST.get('comment_enabled', None)
        # self.comment_enabled = bool(self.comment_enabled)

        # # 'login_required': bool,
        # if kwargs.has_key('login_required'):
        #     self.login_required = kwargs.get('login_required', None)
        # elif request:
        #     self.login_required = request.POST.get('login_required', None)
        # self.login_required = bool(self.login_required)

        # # 'status': STATUS_CHOICES_TU,
        # if kwargs.has_key('status'):
        #     status = kwargs.get('status', u'DRAFT')
        # else:
        #     status = request.POST.get('status', u'DRAFT')
        # self.status = unicode(status)
        # 'rating':[{'score':int, 'user_id':int, 'ip_address':basestring}],
        #       - mostly, it's on detail view and by AJAX and not in/within forms.

        # 'snapshot':dict
        #       - needs to think on this.

        return self

    @staticmethod
    def get_node_by_id(node_id):
        '''
            Takes ObjectId or objectId as string as arg
                and return object
        '''
        if node_id and (isinstance(node_id, ObjectId) or ObjectId.is_valid(node_id)):
            return node_collection.one({'_id': ObjectId(node_id)})
        else:
            # raise ValueError('No object found with id: ' + str(node_id))
            return None

    @staticmethod
    def get_nodes_by_ids_list(node_id_list):
        '''
            Takes list of ObjectIds or objectIds as string as arg
                and return list of object
        '''
        try:
            node_id_list = map(ObjectId, node_id_list)
        except:
            node_id_list = [ObjectId(nid) for nid in node_id_list if nid]
        if node_id_list:
            return node_collection.find({'_id': {'$in': node_id_list}})
        else:
            return None


    @staticmethod
    def get_node_obj_from_id_or_obj(node_obj_or_id, expected_type):
        # confirming arg 'node_obj_or_id' is Object or oid and
        # setting node_obj accordingly.
        node_obj = None

        if isinstance(node_obj_or_id, expected_type):
            node_obj = node_obj_or_id
        elif isinstance(node_obj_or_id, ObjectId) or ObjectId.is_valid(node_obj_or_id):
            node_obj = node_collection.one({'_id': ObjectId(node_obj_or_id)})
        else:
            # error raised:
            raise RuntimeError('No Node class instance found with provided arg for get_node_obj_from_id_or_obj(' + str(node_obj_or_id) + ', expected_type=' + str(expected_type) + ')')

        return node_obj



    def type_of_names_list(self, smallcase=False):
        """Returns a list having names of each type_of (GSystemType, i.e Wiki page,
        Blog page, etc.), built from 'type_of' field (list of ObjectIds)
        """
        type_of_names = []
        if self.type_of:
            node_cur = node_collection.find({'_id': {'$in': self.type_of}})
            if smallcase:
                type_of_names = [node.name.lower() for node in node_cur]
            else:
                type_of_names = [node.name for node in node_cur]

        return type_of_names


    @staticmethod
    def get_name_id_from_type(node_name_or_id, node_type, get_obj=False):
        '''
        e.g:
            Node.get_name_id_from_type('pink-bunny', 'Author')
        '''
        if not get_obj:
            # if cached result exists return it

            slug = slugify(node_name_or_id)
            cache_key = node_type + '_name_id' + str(slug)
            cache_result = cache.get(cache_key)

            if cache_result:
                # todo:  return OID after casting
                return (cache_result[0], ObjectId(cache_result[1]))
            # ---------------------------------

        node_id = ObjectId(node_name_or_id) if ObjectId.is_valid(node_name_or_id) else None
        node_obj = node_collection.one({
                                        "_type": {"$in": [
                                                # "GSystemType",
                                                # "MetaType",
                                                # "RelationType",
                                                # "AttributeType",
                                                # "Group",
                                                # "Author",
                                                node_type
                                            ]},
                                        "$or":[
                                            {"_id": node_id},
                                            {"name": unicode(node_name_or_id)}
                                        ]
                                    })

        if node_obj:
            node_name = node_obj.name
            node_id = node_obj._id

            # setting cache with ObjectId
            cache_key = node_type + '_name_id' + str(slugify(node_id))
            cache.set(cache_key, (node_name, node_id), 60 * 60)

            # setting cache with node_name
            cache_key = node_type + '_name_id' + str(slugify(node_name))
            cache.set(cache_key, (node_name, node_id), 60 * 60)

            if get_obj:
                return node_obj
            else:
                return node_name, node_id

        if get_obj:
            return None
        else:
            return None, None



    ########## Setter(@x.setter) & Getter(@property) ##########
    @property
    def member_of_names_list(self):
        """Returns a list having names of each member (GSystemType, i.e Page,
        File, etc.), built from 'member_of' field (list of ObjectIds)

        """
        return [GSystemType.get_gst_name_id(gst_id)[0] for gst_id in self.member_of]


    @property
    def group_set_names_list(self):
        """Returns a list having names of each member (Group name),
        built from 'group_set' field (list of ObjectIds)

        """
        return [Group.get_group_name_id(gr_id)[0] for gr_id in self.group_set]


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
                        self.structure.pop(each_invalid_field)
                        # print "=== removed from structure", each_invalid_field, ' : ',


            keys_list = self.structure.keys()
            keys_list.append('_id')
            invalid_struct_fields_list = list(set(self.keys()) - set(keys_list))
            # print '\n invalid_struct_fields_list: ',invalid_struct_fields_list
            if invalid_struct_fields_list:
                for each_invalid_field in invalid_struct_fields_list:
                    if each_invalid_field in self:
                        self.pop(each_invalid_field)
                        # print "=== removed ", each_invalid_field, ' : ',


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

        # if Add-Buddy feature is enabled:
        #   - Get all user id's of active buddies with currently logged in user.
        #   - Check if each of buddy-user-id does not exists in contributors of node object, add it.
        if GSTUDIO_BUDDY_LOGIN:
            buddy_contributors = Buddy.get_buddy_userids_list_within_datetime(
                                                    self.created_by,
                                                    self.last_update or self.created_at
                                                )
            # print 'buddy_contributors : ', buddy_contributors

            if buddy_contributors:
                for each_bcontrib in buddy_contributors:
                    if each_bcontrib not in self.contributors:
                        self.contributors.append(each_bcontrib)

        super(Node, self).save(*args, **kwargs)

        # This is the save method of the node class.It is still not
        # known on which objects is this save method applicable We
        # still do not know if this save method is called for the
        # classes which extend the Node Class or for every class There
        # is a very high probability that it is called for classes
        # which extend the Node Class only The classes which we have
        # i.e. the MyReduce() and ToReduce() class do not extend from
        # the node class Hence calling the save method on those objects
        # should not create a recursive function

        # If it is a new document then Make a new object of ToReduce
        # class and the id of this document to that object else Check
        # whether there is already an object of ToReduce() with the id
        # of this object.  If there is an object present pass else add
        # that object I have not applied the above algorithm

        # Instead what I have done is that I have searched the
        # ToReduce() collection class and searched whether the ID of
        # this document is present or not.  If the id is not present
        # then add that id.If it is present then do not add that id

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
                    user_list = User.objects.filter(pk=self.created_by)
                    user = user_list[0].username if user_list else 'user'
                    # user = User.objects.get(pk=self.created_by).username
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
                rcs_obj.checkout(fp, otherflags="-f")
            except Exception as err:
                try:
                    if history_manager.create_or_replace_json_file(self):
                        fp = history_manager.get_file_path(self)
                        # user = User.objects.get(pk=self.created_by).username
                        user_list = User.objects.filter(pk=self.created_by)
                        user = user_list[0].username if user_list else 'user'
                        message = "This document (" + self.name + ") is re-created by " + user + " on " + self.created_at.strftime("%d %B %Y")
                        rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

                except Exception as err:
                    print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be re-created!!!\n"
                    node_collection.collection.remove({'_id': self._id})
                    raise RuntimeError(err)

            try:
                if history_manager.create_or_replace_json_file(self):
                    # user = User.objects.get(pk=self.modified_by).username
                    user_list = User.objects.filter(pk=self.created_by)
                    user = user_list[0].username if user_list else 'user'
                    message = "This document (" + self.name + ") is lastly updated by " + user + " status:" + self.status + " on " + self.last_update.strftime("%d %B %Y")
                    rcs_obj.checkin(fp, 1, message.encode('utf-8'))

            except Exception as err:
                print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be updated!!!\n"
                raise RuntimeError(err)

        #update the snapshot feild
        if kwargs.get('groupid'):
            # gets the last version no.
            rcsno = history_manager.get_current_version(self)
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
                    # PREV: AttributeType.append_attribute(node_collection.collection.AttributeType(attr_obj.attribute_type), possible_attributes, attr_obj.object_value)
                    AttributeType.append_attribute(attr_obj.attribute_type, possible_attributes, attr_obj.object_value)

            # Case [B]: While creating GSystem / if new attributes get added
            # Again checking in AttributeType collection - because to collect newly added user-defined attributes, if any!
            attributes = node_collection.find({'_type': 'AttributeType', 'subject_type': gsystem_type_id})
            for attr_type in attributes:
                # Here attr_type is of type -- AttributeType
                # PREV: AttributeType.append_attribute(attr_type, possible_attributes)
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
                        # PREV:  node_collection.collection.RelationType(rel_obj.relation_type),
                        rel_obj.relation_type,
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
                    rel_type_node = node_collection.one({'_id': ObjectId(rel_obj.relation_type)})
                    if META_TYPE[4] in rel_type_node.member_of_names_list:
                        # We are not handling inverse relation processing for
                        # Triadic relationship(s)
                        continue

                    RelationType.append_relation(
                        # node_collection.collection.RelationType(rel_obj.relation_type),
                        rel_obj.relation_type,
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


    def get_attribute(self, attribute_type_name, status=None):
        return GAttribute.get_triples_from_sub_type(self._id, attribute_type_name, status)

    def get_attributes_from_names_list(self, attribute_type_name_list, status=None, get_obj=False):
        return GAttribute.get_triples_from_sub_type_list(self._id, attribute_type_name_list, status, get_obj)

    def get_relation(self, relation_type_name, status=None):
        return GRelation.get_triples_from_sub_type(self._id, relation_type_name, status)


    def get_relation_right_subject_nodes(self, relation_type_name, status=None):
        return node_collection.find({'_id': {'$in': [r.right_subject for r in self.get_relation(relation_type_name)]} })


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
    'subject_scope': list,
    'object_scope': list,
    'attribute_type_scope': list,
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

    #   raise issue y used
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
    default_values = {
                        'subject_scope': [],
                        'object_scope': [],
                        'attribute_type_scope': [],
                    }

    # validators={
    # 'data_type':x in DATA_TYPE_CHOICES
    # 'data_type':lambda x: x in DATA_TYPE_CHOICES
    # }

    ##########  User-Defined Functions ##########

    @staticmethod
    def append_attribute(attr_id_or_node, attr_dict, attr_value=None, inner_attr_dict=None):

        from bson.dbref import DBRef
        if isinstance(attr_id_or_node, DBRef):
            attr_id_or_node = AttributeType(db.dereference(attr_id_or_node))

        elif isinstance(attr_id_or_node, (unicode, ObjectId)):
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
        'subject_scope': list,
        'object_scope': list,
        'relation_type_scope': list,
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
    default_values = {
                        'subject_scope': [],
                        'object_scope': [],
                        'relation_type_scope': [],
                    }

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
        if isinstance(rel_type_node, (unicode, ObjectId)):
            # Convert unicode representation of ObjectId into it's
            # corresponding ObjectId type Then fetch
            # attribute-type-node from AttributeType collection of
            # respective ObjectId
            if ObjectId.is_valid(rel_type_node):
                rel_type_node = node_collection.one({'_type': 'RelationType', '_id': ObjectId(rel_type_node)})
            else:
                print "\n Invalid ObjectId: ", rel_type_node, " is not a valid ObjectId!!!\n"
                # Throw indicating the same

        left_or_right_subject_node = None

        if left_or_right_subject:
            if META_TYPE[3] in rel_type_node.member_of_names_list:
                # If Binary relationship found
                left_or_right_subject_node = node_collection.one({
                    '_id': left_or_right_subject
                })
            else:
                left_or_right_subject_node = []
                if isinstance(left_or_right_subject, ObjectId):
                    left_or_right_subject = [left_or_right_subject]
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


    @staticmethod
    def get_gst_name_id(gst_name_or_id):
        # if cached result exists return it
        slug = slugify(gst_name_or_id)
        cache_key = 'gst_name_id' + str(slug)
        cache_result = cache.get(cache_key)

        if cache_result:
            return (cache_result[0], ObjectId(cache_result[1]))
        # ---------------------------------

        gst_id = ObjectId(gst_name_or_id) if ObjectId.is_valid(gst_name_or_id) else None
        gst_obj = node_collection.one({
                                        "_type": {"$in": ["GSystemType", "MetaType"]},
                                        "$or":[
                                            {"_id": gst_id},
                                            {"name": unicode(gst_name_or_id)}
                                        ]
                                    })

        if gst_obj:
            gst_name = gst_obj.name
            gst_id = gst_obj._id

            # setting cache with ObjectId
            cache_key = u'gst_name_id' + str(slugify(gst_id))
            cache.set(cache_key, (gst_name, gst_id), 60 * 60)

            # setting cache with gst_name
            cache_key = u'gst_name_id' + str(slugify(gst_name))
            cache.set(cache_key, (gst_name, gst_id), 60 * 60)

            return gst_name, gst_id

        return None, None



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
        'origin': [],                # e.g:
                                        # [
                                        #   {"csv-import": <fn name>},
                                        #   {"sync_source": "<system-pub-key>"}
                                        # ]
        # Replace field 'license': basestring with
        # legal: dict
        'legal': {
                    'copyright': basestring,
                    'license': basestring
                    }
    }

    use_dot_notation = True

    # default_values = "CC-BY-SA 4.0 unported"
    default_values = {
                        'legal': {
                            'copyright': GSTUDIO_DEFAULT_COPYRIGHT,
                            'license': GSTUDIO_DEFAULT_LICENSE
                        }
                    }

    def fill_gstystem_values(self,
                            request=None,
                            attribute_set=[],
                            relation_set=[],
                            author_set=[],
                            origin=[],
                            uploaded_file=None,
                            **kwargs):
        '''
        all node fields will be passed from **kwargs and rest GSystem's fields as args.
        '''

        existing_file_gs = None
        existing_file_gs_if_file = None

        if "_id" not in self and uploaded_file:

            fh_obj = filehive_collection.collection.Filehive()
            existing_fh_obj = fh_obj.check_if_file_exists(uploaded_file)

            if existing_fh_obj:
                existing_file_gs = node_collection.find_one({
                                    '_type': 'GSystem',
                                    'if_file.original.id': existing_fh_obj._id
                                })

            if kwargs.has_key('unique_gs_per_file') and kwargs['unique_gs_per_file']:

                if existing_file_gs:
                    print "Returning:: "
                    return existing_file_gs

        self.fill_node_values(request, **kwargs)

        # fill gsystem's field values:
        self.author_set = author_set

        user_id = self.created_by

        # generating '_id':
        if not self.has_key('_id'):
            self['_id'] = ObjectId()

        # origin:
        if origin:
            self['origin'].append(origin)
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

            file_name = original_filehive_obj.get_file_name(original_file)
            if not file_name:
                file_name = self.name
            mime_type = original_filehive_obj.get_file_mimetype(original_file, file_name)
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

        # Add legal information[copyright and license] to GSystem node
        license = kwargs.get('license', None)
        copyright = kwargs.get('copyright', None)

        if license:
            if self.legal['license'] is not license:
                self.legal['license'] = license
        else:
            self.legal['license'] = GSTUDIO_DEFAULT_LICENSE

        if copyright:
            if self.legal['copyright'] is not copyright:
                self.legal['copyright'] = copyright
        else:
            self.legal['copyright'] = GSTUDIO_DEFAULT_COPYRIGHT

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


    # static query methods
    @staticmethod
    def query_list(group_id, member_of_name, user_id=None):

        group_name, group_id = Group.get_group_name_id(group_id)
        gst_name, gst_id = GSystemType.get_gst_name_id(member_of_name)

        return node_collection.find({
                            '_type': 'GSystem',
                            'status': 'PUBLISHED',
                            'group_set': {'$in': [group_id]},
                            'member_of': {'$in': [gst_id]},
                            '$or':[
                                    {'access_policy': {'$in': [u'Public', u'PUBLIC']}},
                                    # {'$and': [
                                    #     {'access_policy': u"PRIVATE"},
                                    #     {'created_by': user_id}
                                    #     ]
                                    # },
                                    {'created_by': user_id}
                                ]
                        }).sort('last_update', -1)

    @staticmethod
    def child_class_names():
        '''
        Currently, this is hardcoded but it should be dynamic.
        Try following:
        import inspect
        inspect.getmro(GSystem)
        '''
        return ['Group', 'Author', 'File']
    # --- END of static query methods


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


    def get_file_mimetype(self, file_blob, file_name=None):
        file_mime_type = ''

        file_content_type = file_blob.content_type if hasattr(file_blob, 'content_type') else None
        if file_name and "vtt" in file_name:
            return "text/vtt"
        if file_name and "srt" in file_name:
            return "text/srt"
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

        elif poss_ext == '.vtt':
            file_mime_type = 'text/vtt'
            file_extension = '.vtt'

        elif poss_ext == '.srt':
            file_mime_type = 'text/srt'
            file_extension = '.srt'

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
                rcs_obj.checkout(fp, otherflags="-f")

            except Exception as err:
                try:
                    if history_manager.create_or_replace_json_file(self):
                        fp = history_manager.get_file_path(self)
                        message = "This document (" + str(self.md5) + ") is re-created on " + self.uploaded_at.strftime("%d %B %Y")
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
        'moderation_level': int,              # range from 0 till any integer level
        'project_config': dict
    }

    use_dot_notation = True

    # required_fields = ['_type', 'name', 'created_by']

    default_values = {
                        'group_type': TYPES_OF_GROUP_DEFAULT,
                        'edit_policy': EDIT_POLICY_DEFAULT,
                        'subscription_policy': SUBSCRIPTION_POLICY_DEFAULT,
                        'visibility_policy': EXISTANCE_POLICY_DEFAULT,
                        'disclosure_policy': LIST_MEMBER_POLICY_DEFAULT,
                        'encryption_policy': ENCRYPTION_POLICY_DEFAULT,
                        'agency_type': GSTUDIO_GROUP_AGENCY_TYPES_DEFAULT,
                        'group_admin': [],
                        'moderation_level': -1
                    }

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

    @staticmethod
    def get_group_name_id(group_name_or_id, get_obj=False):
        '''
          - This method takes possible group name/id as an argument and returns (group-name and id) or group object.

          - If no second argument is passed, as method name suggests, returned result is "group_name" first and "group_id" second.

          - When we need the entire group object, just pass second argument as (boolian) True. In the case group object will be returned.

          Example 1: res_group_name, res_group_id = Group.get_group_name_id(group_name_or_id)
          - "res_group_name" will contain name of the group.
          - "res_group_id" will contain _id/ObjectId of the group.

          Example 2: res_group_obj = Group.get_group_name_id(group_name_or_id, get_obj=True)
          - "res_group_obj" will contain entire object.

          Optimization Tip: before calling this method, try to cast group_id to ObjectId as follows (or copy paste following snippet at start of function or wherever there is a need):
          try:
              group_id = ObjectId(group_id)
          except:
              group_name, group_id = Group.get_group_name_id(group_id)

        '''
        # if cached result exists return it
        if not get_obj:

            slug = slugify(group_name_or_id)
            # for unicode strings like hindi-text slugify doesn't works
            cache_key = 'get_group_name_id_' + str(slug) if slug else str(abs(hash(group_name_or_id)))
            cache_result = cache.get(cache_key)

            if cache_result:
                return (cache_result[0], ObjectId(cache_result[1]))
        # ---------------------------------

        # case-1: argument - "group_name_or_id" is ObjectId
        if ObjectId.is_valid(group_name_or_id):

            group_obj = node_collection.one({"_id": ObjectId(group_name_or_id),
                "_type": {"$in": ["Group", "Author"]}})

            # checking if group_obj is valid
            if group_obj:
                # if (group_name_or_id == group_obj._id):
                group_id = ObjectId(group_name_or_id)
                group_name = group_obj.name

                if get_obj:
                    return group_obj
                else:
                    # setting cache with both ObjectId and group_name
                    cache.set(cache_key, (group_name, group_id), 60 * 60)
                    cache_key = u'get_group_name_id_' + slugify(group_name)
                    cache.set(cache_key, (group_name, group_id), 60 * 60)
                    return group_name, group_id

        # case-2: argument - "group_name_or_id" is group name
        else:
            group_obj = node_collection.one(
                {"_type": {"$in": ["Group", "Author"]}, "name": unicode(group_name_or_id)})

            # checking if group_obj is valid
            if group_obj:
                # if (group_name_or_id == group_obj.name):
                group_name = group_name_or_id
                group_id = group_obj._id

                if get_obj:
                    return group_obj
                else:
                    # setting cache with both ObjectId and group_name
                    cache.set(cache_key, (group_name, group_id), 60*60)
                    cache_key = u'get_group_name_id_' + slugify(group_name)
                    cache.set(cache_key, (group_name, group_id), 60*60)
                    return group_name, group_id

        if get_obj:
            return None
        else:
            return None, None


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
            auth_obj = node_collection.one({'_type': 'Author', 'created_by': user.id})
            if auth_obj and auth_obj.agency_type == 'Teacher':
                return True
        return False


    @staticmethod
    def can_access(user_id, group):
        '''Returns True if user can access (read/edit/write) group resource.
        ARGS:
            - user_id (int): Django User id
            - group (Group or ObjectID or str-of-group-name): It can be either group's
                                                        object or _id or name.
        '''
        if isinstance(group, Group):
            group_obj = group
        else:
            group_obj = Group.get_group_name_id(group, get_obj=True)

        user_query = User.objects.filter(id=user_id)

        if group_obj and user_query:
            return group_obj.is_gstaff(user_query[0]) or (user_id in group_obj.author_set)
        else:
            return False


    @staticmethod
    def can_read(user_id, group):
        if isinstance(group, Group):
            group_obj = group
        else:
            group_obj = Group.get_group_name_id(group, get_obj=True)

        if group_obj:
            if group_obj.group_type == 'PUBLIC':
                return True
            else:
                user_query = User.objects.filter(id=user_id)
                if user_query:
                    return group_obj.is_gstaff(user_query[0]) or (user_id in group_obj.author_set)

        return False


    def fill_group_values(self,
                        request=None,
                        group_type=None,
                        edit_policy=None,
                        subscription_policy=None,
                        visibility_policy=None,
                        disclosure_policy=None,
                        encryption_policy=None,
                        agency_type=None,
                        group_admin=None,
                        moderation_level=None,
                        **kwargs):
        '''
        function to fill the group object with values supplied.
        - group information may be sent either from "request" or from "kwargs".
        - returning basic fields filled group object
        '''
        # gdv: Group default Values
        gdv = Group.default_values.keys()
        # gsdv: GSystem default Values
        gsdv = GSystem.default_values
        [gsdv.pop(each_gsdv, None) for each_gsdv in gdv]

        arguments = locals()
        for field_key, default_val in gsdv.items():
            try:
                if arguments[field_key]:
                    self[field_key] = arguments[field_key]
            except:
                if self.request:
                    self[field_key] = self.request.POST.get(field_key, default_val)
            finally:
                self[field_key] = default_val

        if group_type:
            self.group_type = group_type
        self.fill_gstystem_values(request=request, **kwargs)

        # explicit: group's should not have draft stage. So publish them:
        self.status = u"PUBLISHED"

        return self
    # --- END --- fill_group_values() ------


    # def create(request=None,
    #             group_type=Group.default_values['group_type'],
    #             edit_policy=Group.default_values['edit_policy'],
    #             subscription_policy=Group.default_values['subscription_policy'],
    #             visibility_policy=Group.default_values['visibility_policy'],
    #             disclosure_policy=Group.default_values['disclosure_policy'],
    #             encryption_policy=Group.default_values['encryption_policy'],
    #             agency_type=Group.default_values['agency_type'],
    #             group_admin=Group.default_values['group_admin'],
    #             moderation_level=Group.default_values['moderation_level'],
    #             **kwargs):

    #     new_group_obj = node_collection.collection.Group()

    #     GSystem.fill_gstystem_values(request=None,
    #                         author_set=[],
    #                         **kwargs)


    @staticmethod
    def purge_group(group_name_or_id, proceed=True):

        # fetch group object
        group_obj = Group.get_group_name_id(group_name_or_id, get_obj=True)

        if not group_obj:
            raise Exception('Expects either group "name" or "_id". Got invalid argument or that group does not exists.')

        group_id = group_obj._id

        # get all the objects belonging to this group
        all_nodes_under_gr = node_collection.find({'group_set': {'$in': [group_id]}})

        # separate nodes belongs to one and more groups
        only_group_nodes_cnt = all_nodes_under_gr.clone().where("this.group_set.length == 1").count()
        multi_group_nodes_cnt = all_nodes_under_gr.clone().where("this.group_set.length > 1").count()

        print "Group:", group_obj.name, "(", group_obj.altnames, ") contains:\n",\
            "\t- unique (belongs to this group only) : ", only_group_nodes_cnt, \
            "\n\t- shared (belongs to other groups too): ", multi_group_nodes_cnt, \
            "\n\t============================================", \
            "\n\t- total: ", all_nodes_under_gr.count()

        if not proceed:
            print "\nDo you want to purge group and all unique nodes(belongs to this group only) under it?"
            print 'Enter Y/y to proceed else N/n to reject group deletion:'
            to_proceed = raw_input()
            proceed = True if (to_proceed in ['y', 'Y']) else False

        if proceed:
            print "\nProceeding further for purging of group and unique resources/nodes under it..."
            from gnowsys_ndf.ndf.views.methods import delete_node

            grp_res = node_collection.find({ '$and': [ {'group_set':{'$size':1}}, {'group_set': {'$all': [ObjectId(group_id)]}} ] })
            print "\n Total (unique) resources to be purge: ", grp_res.count()

            for each in grp_res:
                del_status, del_status_msg = delete_node(node_id=each._id, deletion_type=1 )
                # print del_status, del_status_msg
                if not del_status:
                    print "*"*80
                    print "\n Error node: _id: ", each._id, " , name: ", each.name, " type: ", each.member_of_names_list
                    print "*"*80

            print "\n Purging group: "
            del_status, del_status_msg = delete_node(node_id=group_id, deletion_type=1)
            print del_status, del_status_msg

            # poping group_id from each of shared nodes under group
            all_nodes_under_gr.rewind()
            print "\n Total (shared) resources to be free from this group: ", all_nodes_under_gr.count()
            for each_shared_node in all_nodes_under_gr:
                if group_id in each_shared_node.group_set:
                    each_shared_node.group_set.remove(group_id)
                    each_shared_node.save()

            return True

        print "\nAborting group deletion."
        return True


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
    def get_author_by_userid(user_id):
        return node_collection.one({'_type': 'Author', 'created_by': user_id})

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


    @staticmethod
    def get_total_comments_by_user(user_id, return_cur=False, site_wide=False, group_id=None):

        reply_gst = node_collection.one({'_type': "GSystemType", 'name': "Reply"}, {'_id': 1})

        comments_query = {'member_of': reply_gst._id,'created_by': user_id}

        if not site_wide:
            group_id = group_id | ObjectId()
            comments_query.update({'group_set': group_id})

        users_replies_cur = node_collection.find(comments_query)

        if users_replies_cur:
            if return_cur:
                return users_replies_cur
            return users_replies_cur.count()
        else:
            return 0


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

        collection_tuple = (MetaType, GSystemType, GSystem, AttributeType, GAttribute, RelationType, GRelation, Filehive, Buddy, Counter)
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
        rcs.checkout((fp, version_no), otherflags="-f")

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
                    print "\n Exception for document's ("+str(doc_obj._id)+") key ("+k+") -- ", str(e), "\n"

        return doc_obj


    @staticmethod
    def delete_json_file(node_id_or_obj, expected_type):
        node_obj = Node.get_node_obj_from_id_or_obj(node_id_or_obj, expected_type)
        history_manager = HistoryManager()
        json_file_path = history_manager.get_file_path(node_obj)
        version_file_path = json_file_path + ',v'
        try:
            os.remove(version_file_path)
            print "\nDeleted RCS json version file : ", version_file_path
            os.remove(json_file_path)
            print "\nDeleted RCS json file : ", json_file_path
        except Exception, e:
            print "\nException occured while deleting RCS file for node '", node_obj._id.__str__(), "' : ", e




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
            if user_id:
                userid_session_key_dict[user_id] = session.session_key
            # uid_list_append(user_id)
            # session_key_list.append(session.session_key)

        return userid_session_key_dict

        # # Query all logged in users based on id list
        # if list_of_ids:
        #     return User.objects.filter(id__in=uid_list).values_list('id', flat=True)
        # else:
        #     return User.objects.filter(id__in=uid_list)

    @staticmethod
    def logout_all_users():
        """
        Read all available users and all available not expired sessions. Then
        logout from each session. This method also releases all buddies with each user session.
        """
        from django.utils.importlib import import_module
        from django.conf import settings
        from django.contrib.auth import logout
        
        request = HttpRequest()

        # sessions = Session.objects.filter(expire_date__gte=timezone.now())
        sessions = Session.objects.filter(expire_date__gte=timezone.now()).distinct('session_data')

        # Experimental trial (aggregate query):
        # unique_sessions_list = Session.objects.filter(expire_date__gte=timezone.now()).values('session_data').annotate(Count('session_data')).filter(session_data__count__lte=1)
        
        print('Found %d non-expired session(s).' % len(sessions))

        for session in sessions:
            try:
                user_id = session.get_decoded().get('_auth_user_id')
                engine = import_module(settings.SESSION_ENGINE)
                request.session = engine.SessionStore(session.session_key)

                request.user = User.objects.get(id=user_id)
                print ('\nProcessing session of [ %d : "%s" ]\n' % (request.user.id, request.user.username))

                logout(request)
                print('- Successfully logout user with id: %r ' % user_id)

            except Exception as e:
                # print "Exception: ", e
                pass

        Buddy.sitewide_remove_all_buddies()



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
    'object_scope': basestring,
    'subject': ObjectId,  # ObjectId's of GSystem Class
    'language': (basestring, basestring),  # e.g: ('en', 'English') or ['en', 'English']
    'status': STATUS_CHOICES_TU
  }

  required_fields = ['name', 'subject']
  use_dot_notation = True
  use_autorefs = True
  default_values = {
                      'subject_scope': None,
                      'object_scope': None
                  }

  @classmethod
  def get_triples_from_sub_type(cls, subject_id, gt_or_rt_name_or_id, status=None):
        '''
        getting triples from SUBject and TYPE (attribute_type or relation_type)
        '''
        triple_node_mapping_dict = {
            'GAttribute': 'AttributeType',
            'GRelation': 'RelationType'
        }
        triple_class_field_mapping_dict = {
            'GAttribute': 'attribute_type',
            'GRelation': 'relation_type'
        }
        gr_or_rt_name, gr_or_rt_id = Node.get_name_id_from_type(gt_or_rt_name_or_id,
            triple_node_mapping_dict[cls._meta.verbose_name])
        status = [status] if status else ['PUBLISHED', 'DELETED']
        return triple_collection.find({
                                    '_type': cls._meta.verbose_name,
                                    'subject': ObjectId(subject_id),
                                    triple_class_field_mapping_dict[cls._meta.verbose_name]: gr_or_rt_id,
                                    'status': {'$in': status}
                                })


  @classmethod
  def get_triples_from_sub_type_list(cls, subject_id, gt_or_rt_name_or_id_list, status=None, get_obj=True):
        '''
        getting triples from SUBject and TYPE (attribute_type or relation_type)
        '''
        triple_node_mapping_dict = {
            'GAttribute': 'AttributeType',
            'GRelation': 'RelationType'
        }
        triple_class_field_mapping_dict = {
            'GAttribute': 'attribute_type',
            'GRelation': 'relation_type'
        }
        triple_class_field_mapping_key_dict = {
            'GAttribute': 'object_value',
            'GRelation': 'right_subject'
        }

        if not isinstance(gt_or_rt_name_or_id_list, list):
            gt_or_rt_name_or_id_list = [gt_or_rt_name_or_id_list]

        gt_or_rt_id_name_dict = {}
        for each_gr_or_rt in gt_or_rt_name_or_id_list:
            gr_or_rt_name, gr_or_rt_id = Node.get_name_id_from_type(each_gr_or_rt,
                triple_node_mapping_dict[cls._meta.verbose_name])
            gt_or_rt_id_name_dict.update({gr_or_rt_id: gr_or_rt_name})

        status = [status] if status else ['PUBLISHED', 'DELETED']

        tr_cur = triple_collection.find({
                                    '_type': cls._meta.verbose_name,
                                    'subject': ObjectId(subject_id),
                                    triple_class_field_mapping_dict[cls._meta.verbose_name]: {'$in': gt_or_rt_id_name_dict.keys()},
                                    'status': {'$in': status}
                                })

        gt_or_rt_name_value_or_obj_dict = {gt_or_rt: '' for gt_or_rt in gt_or_rt_name_or_id_list}
        for each_tr in tr_cur:
            gt_or_rt_name_value_or_obj_dict[gt_or_rt_id_name_dict[each_tr[triple_class_field_mapping_dict[cls._meta.verbose_name]]]] = each_tr if get_obj else each_tr[triple_class_field_mapping_key_dict[cls._meta.verbose_name]]
        return gt_or_rt_name_value_or_obj_dict


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
    if not subject_document:
        return
    subject_name = subject_document.name
    right_subject_member_of_list = []

    subject_type_list = []
    subject_member_of_list = []
    name_value = u""
    # if (self._type == "GAttribute") and ('triple_node' in kwargs):
    if (self._type == "GAttribute"):
      # self.attribute_type = kwargs['triple_node']
      at_node = node_collection.one({'_id': ObjectId(self.attribute_type)})
      attribute_type_name = at_node.name
      attribute_object_value = unicode(self.object_value)
      attribute_object_value_for_name = attribute_object_value[:20]
      self.name = "%(subject_name)s -- %(attribute_type_name)s -- %(attribute_object_value_for_name)s" % locals()
      name_value = self.name

      subject_type_list = at_node.subject_type
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
      # self.attribute_type = kwargs['triple_id']

    elif self._type == "GRelation":
      rt_node = node_collection.one({'_id': ObjectId(self.relation_type)})
      # self.relation_type = kwargs['triple_node']
      subject_type_list = rt_node.subject_type
      object_type_list = rt_node.object_type

      left_subject_member_of_list = subject_document.member_of
      relation_type_name = rt_node.name
      if META_TYPE[4] in rt_node.member_of_names_list:
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

          right_subject_list = self.right_subject if isinstance(self.right_subject, list) else [self.right_subject]
          right_subject_document = node_collection.find_one({'_id': {'$in': right_subject_list} })
          if right_subject_document:
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

      # self.relation_type = kwargs['triple_id']

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
          rcs_obj.checkout(fp, otherflags="-f")
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
        'attribute_type_scope': dict,
        # 'attribute_type': AttributeType,  # Embedded document of AttributeType Class
        'attribute_type': ObjectId,  # ObjectId of AttributeType node
        # 'object_value_scope': basestring,
        'object_value': None  # value -- it's data-type, is determined by attribute_type field
    }

    indexes = [
        {
            # 1: Compound index
            'fields': [
                ('_type', INDEX_ASCENDING), ('subject', INDEX_ASCENDING), \
                ('attribute_type', INDEX_ASCENDING), ('status', INDEX_ASCENDING)
            ],
            'check': False  # Required because $id is not explicitly specified in the structure
        }
    ]

    required_fields = ['attribute_type', 'object_value']
    use_dot_notation = True
    use_autorefs = True                   # To support Embedding of Documents
    default_values = {
                        'attribute_type_scope': {}
                    }


@connection.register
class GRelation(Triple):
    structure = {
        'relation_type_scope': dict,
        # 'relation_type': RelationType,  # DBRef of RelationType Class
        'relation_type': ObjectId,  # ObjectId of RelationType node
        # 'right_subject_scope': basestring,
        # ObjectId's of GSystems Class / List of list of ObjectId's of GSystem Class
        'right_subject': OR(ObjectId, list)
    }
    default_values = {
                        'relation_type_scope': {}
                    }

    indexes = [{
        # 1: Compound index
        'fields': [
            ('_type', INDEX_ASCENDING), ('subject', INDEX_ASCENDING), \
            ('relation_type'), ('status', INDEX_ASCENDING), \
            ('right_subject', INDEX_ASCENDING)
        ],
        'check': False  # Required because $id is not explicitly specified in the structure
    }, {
        # 2: Compound index
        'fields': [
            ('_type', INDEX_ASCENDING), ('right_subject', INDEX_ASCENDING), \
            ('relation_type'), ('status', INDEX_ASCENDING)
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
        - Removes/releses all existing-active buddies in single buddy object.
        - it doesn't close buddy session/object.
        - i.e: It don't add datetime.datetime.now() to 'ends_at' field.
        - without doing DB .save() operation.
        '''
        active_buddy_authid_list = self.get_active_authid_list_from_single_buddy()

        for each_buddy_authid in active_buddy_authid_list:
            print "- Released Buddy: ", Node.get_name_id_from_type(each_buddy_authid, u'Author')[0]
            self.get_latest_in_out_dict(self.buddy_in_out[each_buddy_authid])['out'] = datetime.datetime.now()

        return self


    def end_buddy_session(self):
        '''
        terminates the buddy session:
            - removes all buddies.
            - It add datetime.datetime.now() to 'ends_at' field.
            - buddy object will be saved using .save() method.
        '''

        if not self.ends_at:
            self = self.remove_all_buddies()
            self.ends_at = datetime.datetime.now()
            self.save()

        # active_buddy_authid_list = self.get_active_authid_list_from_single_buddy()
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


    def get_all_buddies_auth_ids(self):
        return self['buddy_in_out'].keys()

    def get_all_buddies_user_ids(self):
        return Author.get_user_id_list_from_author_oid_list(self['buddy_in_out'].keys())

    @staticmethod
    def get_buddy_cur_from_userid_datetime(user_id, datetime_obj):
        return buddy_collection.find({
                                    'loggedin_userid': user_id,
                                    'starts_at': {'$lte': datetime_obj},
                                    '$or': [
                                            {'ends_at': {'$gte': datetime_obj}},
                                            {'ends_at': None}
                                        ]
                                })

    @staticmethod
    def get_buddy_userids_list_within_datetime(user_id, datetime_obj):
        buddy_cur = Buddy.get_buddy_cur_from_userid_datetime(user_id, datetime_obj)
        all_buddies_authid_list = []
        for each_buddy_obj in buddy_cur:
            # all_buddies_authid_list += each_buddy_obj.get_all_buddies_auth_ids()
            for each_buddy_authid, in_out_time in each_buddy_obj.buddy_in_out.iteritems():
                for each_io in in_out_time:
                    if (not each_io['out'] and datetime_obj > each_io['in']) \
                    or (each_io['out'] and datetime_obj < each_io['out'] and datetime_obj > each_io['in']):
                        all_buddies_authid_list.append(each_buddy_authid)

        if not all_buddies_authid_list:
            return []

        else:
            return Author.get_user_id_list_from_author_oid_list(set(dict.fromkeys(all_buddies_authid_list).keys()))


    # method for sitewide buddies:

    @staticmethod
    def sitewide_all_buddies():
        return buddy_collection.find()

    @staticmethod
    def sitewide_all_active_buddies():
        return buddy_collection.find({'ends_at': None})

    @staticmethod
    def sitewide_remove_all_buddies():
        sitewide_all_active_buddies = Buddy.sitewide_all_active_buddies()

        for each_buddy in sitewide_all_active_buddies:
            each_buddy.end_buddy_session()

        return sitewide_all_active_buddies

    # --- END OF method for sitewide buddies


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
                rcs_obj.checkout(fp, otherflags="-f")

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


@connection.register
class Counter(DjangoDocument):

    collection_name = 'Counters'

    # resources will be created will be of following type:
    resource_list = ['page', 'file']

    # resources will be created will have following default schema dict:
    default_resource_stats = {
        'created' : 0,  # no of files/pages/any-app's instance created

        'visits_gained': 0, # Count of unique visitors(user's) not total visits
        'visits_on_others_res':  0, # count of visits not resources

        'comments_gained':  0,  # Count of comments not resources
        'commented_on_others_res':  0, # count of resources not comments
        'comments_by_others_on_res': {},

        'avg_rating_gained': 0,  # total_rating/rating_count_received
        'rating_count_received': 0,
    }


    structure = {
       '_type': unicode,
        'user_id': int,
        'auth_id': ObjectId,
        'group_id': ObjectId,
        'last_update': datetime.datetime,

        # 'enrolled':bool,
        'is_group_member': bool,
        # 'course_score':int,
        'group_points': int,

        # -- notes --
        'page': {'blog': dict, 'wiki': dict, 'info': dict},  # resource

        # -- files --
        'file': dict,  # resource

        # -- quiz --
        'quiz': {'attempted': int, 'correct': int, 'incorrect': int},

        # -- interactions --
        'total_comments_by_user': int,

        # Total fields should be updated on enroll action
        # On module/unit add/delete, update 'total' fields for all users in celery
        
        'course':{'modules':{'completed':int, 'total':int}, 'units':{'completed':int, 'total':int}},

        # 'visited_nodes' = {str(ObjectId): int(count_of_visits)}
        'visited_nodes': {basestring: int},
        'assessment': []
        #             [{'id: basestring, 'correct': int, 'failed_attempts': int}]
        # 'assessment': {
        #             'offered_id': {'total': int, 'correct': int, 'incorrect_attempts': int}
        #             }
    }

    default_values = {
        'last_update': datetime.datetime.now(),
        'is_group_member': False,
        'group_points': 0,
        'page.blog': default_resource_stats,
        'page.wiki': default_resource_stats,
        'page.info': default_resource_stats,
        'file': default_resource_stats,
        'quiz.attempted': 0,
        'quiz.correct': 0,
        'quiz.incorrect': 0,
        'total_comments_by_user': 0,
        'course.modules.total': 0,
        'course.modules.completed': 0,
        'course.units.total': 0,
        'course.units.completed': 0,
    }

    indexes = [
        {
            # 1: Compound index
            'fields': [
                ('user_id', INDEX_ASCENDING), ('group_id', INDEX_ASCENDING)
            ]
        },
    ]

    required_fields = ['user_id', 'group_id', 'auth_id']
    use_dot_notation = True

    def __unicode__(self):
        return self._id

    def identity(self):
        return self.__unicode__()

    @staticmethod
    def _get_resource_type_tuple(resource_obj):

        # identifying resource's type:
        resource_type = ''
        resource_type_of = ''

        # ideally, member_of field should be used to check resource_type. But it may cause performance hit.
        # hence using 'if_file.mime_type'
        if resource_obj.if_file.mime_type or \
         u'File' in resource_obj.member_of_names_list or \
         u'Asset' in resource_obj.member_of_names_list or \
         u'AssetContent' in resource_obj.member_of_names_list:
            resource_type = 'file'

        elif u'Page' in resource_obj.member_of_names_list:
            resource_type = 'page'
            # mostly it 'type_of' will be [] hence kept: if not at first.
            if not resource_obj.type_of:
                resource_type_of = 'blog'
            else:
                resource_type_of_names_list = resource_obj.type_of_names_list(smallcase=True)
                resource_type_of = resource_type_of_names_list[0].split(' ')[0]

        return (resource_type, resource_type_of)


    def fill_counter_values(self,
                            user_id,
                            auth_id,
                            group_id,
                            is_group_member=default_values['is_group_member'],
                            group_points=default_values['group_points'],
                            last_update=datetime.datetime.now()
                            ):

        self['user_id'] = int(user_id)
        self['auth_id'] = ObjectId(auth_id)
        self['group_id'] = ObjectId(group_id)
        self['is_group_member'] = is_group_member
        self['group_points'] = group_points
        self['last_update'] = last_update

        return self


    @staticmethod
    def get_counter_obj(userid, group_id, auth_id=None):
        user_id  = int(userid)
        group_id = ObjectId(group_id)

        # query and check for existing counter obj:
        counter_obj = counter_collection.find_one({'user_id': user_id, 'group_id': group_id})

        # create one if not exists:
        if not counter_obj :

            # instantiate new counter instance
            counter_obj = counter_collection.collection.Counter()

            if not auth_id:
                auth_obj = node_collection.one({'_type': u'Author', 'created_by': user_id})
                auth_id = auth_obj._id

            counter_obj.fill_counter_values(user_id=user_id, group_id=group_id, auth_id=auth_id)
            counter_obj.save()

        return counter_obj


    @staticmethod
    def get_counter_objs_cur(user_ids_list, group_id):
        group_id = ObjectId(group_id)

        # query and check for existing counter obj:
        counter_objs_cur = counter_collection.find({
                                                'user_id': {'$in': user_ids_list},
                                                'group_id': group_id
                                            })

        if counter_objs_cur.count() == len(user_ids_list):
            return counter_objs_cur

        else:
            # following will create counter instances for one which does not exists
            create_counter_for_user_ids = set(user_ids_list) - {uc['user_id'] for uc in counter_objs_cur}
            for each_user_id in create_counter_for_user_ids:
                Counter.get_counter_obj(each_user_id, group_id)

            return counter_objs_cur.rewind()


    def get_file_points(self):
        from gnowsys_ndf.settings import GSTUDIO_FILE_UPLOAD_POINTS
        return self['file']['created'] * GSTUDIO_FILE_UPLOAD_POINTS


    def get_page_points(self, page_type='blog'):
        from gnowsys_ndf.settings import GSTUDIO_NOTE_CREATE_POINTS
        return self['page'][page_type]['created'] * GSTUDIO_NOTE_CREATE_POINTS


    def get_quiz_points(self):
        from gnowsys_ndf.settings import GSTUDIO_QUIZ_CORRECT_POINTS
        return self['quiz']['correct'] * GSTUDIO_QUIZ_CORRECT_POINTS

    def get_assessment_points(self):
        from gnowsys_ndf.settings import GSTUDIO_QUIZ_CORRECT_POINTS
        total_correct = 0
        for each_dict in self['assessment']:
            try:
                total_correct = each_dict['correct']
            except Exception as possible_key_err:
                print "Ignore if KeyError. Error: {0}".forma
        return total_correct * GSTUDIO_QUIZ_CORRECT_POINTS

    def get_interaction_points(self):
        from gnowsys_ndf.settings import GSTUDIO_COMMENT_POINTS
        return self['total_comments_by_user'] * GSTUDIO_COMMENT_POINTS


    def get_all_user_points_dict(self):
        point_breakup_dict = {"Files": 0, "Notes": 0, "Quiz": 0, "Interactions": 0}

        point_breakup_dict['Files'] = self.get_file_points()
        point_breakup_dict['Notes'] = self.get_page_points(page_type='blog')
        if 'assessment' in self and self['assessment']:
            point_breakup_dict['Assessment']  = self.get_assessment_points()
        else:
            point_breakup_dict['Quiz']  = self.get_quiz_points()
        point_breakup_dict['Interactions'] = self.get_interaction_points()

        return point_breakup_dict


    def total_user_points(self):
        point_breakup_dict = self.get_all_user_points_dict()
        return sum(point_breakup_dict.values())


    # private helper functions:
    @staticmethod
    def __key_str_counter_resource_type_of(resource_type,
                                        resource_type_of,
                                        counter_obj_var_name='counter_obj'):
        # returns str of counter_objs, resource_type and resource_type_of
        # e.g: 'counter_obj[resource_type][resource_type_of]'

        key_str_resource_type = '["' + resource_type + '"]'\
                                + (('["' + resource_type_of + '"]') if resource_type_of else '')

        return (counter_obj_var_name + key_str_resource_type)


    @staticmethod
    def add_comment_pt(resource_obj_or_id, current_group_id, active_user_id_or_list=[]):
        if not isinstance(active_user_id_or_list, list):
            active_user_id_list = [active_user_id_or_list]
        else:
            active_user_id_list = active_user_id_or_list

        resource_obj = Node.get_node_obj_from_id_or_obj(resource_obj_or_id, GSystem)
        resource_oid = resource_obj._id
        resource_type, resource_type_of = Counter._get_resource_type_tuple(resource_obj)

        # if resource_type and resource_type_of:
        if resource_type:
            # get resource's creator:
            resource_created_by_user_id = resource_obj.created_by
            resource_contributors_user_ids_list = resource_obj.contributors

            key_str_resource_type = '["' + resource_type + '"]'\
                                    + (('["' + resource_type_of + '"]') if resource_type_of else '')
            key_str = 'counter_obj_each_contributor' \
                      + key_str_resource_type \
                      + '["comments_by_others_on_res"]'

            # counter object of resource contributor
            # ------- creator counter update: done ---------
            for each_resource_contributor in resource_contributors_user_ids_list:
                if each_resource_contributor not in active_user_id_list:
                    counter_obj_each_contributor = Counter.get_counter_obj(each_resource_contributor, current_group_id)

                    # update counter obj
                    for each_active_user_id in active_user_id_list:
                        existing_user_comment_cnt = eval(key_str).get(str(each_active_user_id), 0)
                        eval(key_str).update({str(each_active_user_id): (existing_user_comment_cnt + 1) })

                    # update comments gained:
                    key_str_comments_gained = "counter_obj_each_contributor" \
                                              + key_str_resource_type
                    comments_gained = eval(key_str_comments_gained + '["comments_gained"]')
                    eval(key_str_comments_gained).update({"comments_gained": (comments_gained + 1)})

                    counter_obj_each_contributor.last_update = datetime.datetime.now()
                    counter_obj_each_contributor.save()
            # ------- creator counter update: done ---------

            # processing analytics for (one) active user.
            # NOTE: [Only if active user is other than resource creator]
            from gnowsys_ndf.settings import GSTUDIO_COMMENT_POINTS
            for each_active_user_id in active_user_id_list:
                if each_active_user_id not in resource_contributors_user_ids_list:

                    counter_obj = Counter.get_counter_obj(each_active_user_id, current_group_id)

                    # counter_obj['file']['commented_on_others_res'] += 1
                    key_str = 'counter_obj' \
                              + key_str_resource_type \
                              + '["commented_on_others_res"]'
                    existing_commented_on_others_res = eval(key_str)
                    eval('counter_obj' + key_str_resource_type).update( \
                        { 'commented_on_others_res': (existing_commented_on_others_res + 1) })

                    counter_obj['total_comments_by_user'] += 1
                    counter_obj['group_points'] += GSTUDIO_COMMENT_POINTS

                    counter_obj.last_update = datetime.datetime.now()
                    counter_obj.save()

    @staticmethod
    # @task
    def add_visit_count(resource_obj_or_id, current_group_id, loggedin_userid):

        active_user_ids_list = [loggedin_userid]
        if GSTUDIO_BUDDY_LOGIN:
            active_user_ids_list += Buddy.get_buddy_userids_list_within_datetime(loggedin_userid, datetime.datetime.now())
            # removing redundancy of user ids:
            # active_user_ids_list = dict.fromkeys(active_user_ids_list).keys()

        resource_obj = Node.get_node_obj_from_id_or_obj(resource_obj_or_id, GSystem)
        resource_oid = resource_obj._id
        resource_type, resource_type_of = Counter._get_resource_type_tuple(resource_obj)

        # get resource's creator:
        resource_created_by_user_id = resource_obj.created_by
        resource_contributors_user_ids_list = resource_obj.contributors

        # contributors will not get increament in visit count increment for own resource.
        diff_user_ids_list = list(set(active_user_ids_list) - set(resource_contributors_user_ids_list))
        diff_user_ids_list_length = len(diff_user_ids_list)
        if diff_user_ids_list_length == 0:
            return

        counter_objs_cur = Counter.get_counter_objs_cur(diff_user_ids_list, current_group_id)

        key_str_counter_resource_type = Counter.__key_str_counter_resource_type_of(resource_type,
                                                                           resource_type_of,
                                                                           'each_uc')
        key_str_counter_resource_type_visits_on_others_res = key_str_counter_resource_type \
                                                              + '["visits_on_others_res"]'
        key_str_creator_counter_resource_type_visits_gained = key_str_counter_resource_type \
                                                              + '["visits_gained"]'

        for each_uc in counter_objs_cur:
            # if each_uc['user_id'] not in resource_contributors_user_ids_list:
            visits_on_others_res = eval(key_str_counter_resource_type_visits_on_others_res)
            eval(key_str_counter_resource_type).update({"visits_on_others_res": (visits_on_others_res + 1)})
            each_uc.save()


        # contributors will not get increament in visit count increment for own resource.
        diff_contrib_ids_list = list(set(resource_contributors_user_ids_list) - set(active_user_ids_list))
        if not diff_contrib_ids_list:
            return

        creator_counter_objs_cur = Counter.get_counter_objs_cur(diff_contrib_ids_list, current_group_id)

        for each_uc in creator_counter_objs_cur:
            visits_gained = eval(key_str_creator_counter_resource_type_visits_gained)
            eval(key_str_counter_resource_type).update({"visits_gained": (visits_gained + diff_user_ids_list_length)})
            each_uc.save()


    @staticmethod
    def update_ratings(resource_obj_or_id, current_group_id, rating_given, active_user_id_or_list=[]):

        if not isinstance(active_user_id_or_list, list):
            active_user_id_list = [active_user_id_or_list]
        else:
            active_user_id_list = active_user_id_or_list

        resource_obj = Node.get_node_obj_from_id_or_obj(resource_obj_or_id, GSystem)
        resource_oid = resource_obj._id
        resource_type, resource_type_of = Counter._get_resource_type_tuple(resource_obj)
        # get resource's creator:
        # resource_created_by_user_id = resource_obj.created_by
        resource_contributors_user_ids_list = resource_obj.contributors

        # creating {user_id: score}
        # e.g: {162: 5, 163: 3, 164: 4}
        userid_score_rating_dict = {d['user_id']: d['score'] for d in resource_obj.rating}
        for user_id_val in active_user_id_list:
            if user_id_val in userid_score_rating_dict.keys():
                userid_score_rating_dict.pop(user_id_val)

        user_counter_cur = Counter.get_counter_objs_cur(resource_contributors_user_ids_list, current_group_id)

        key_str_counter_resource_type = Counter.__key_str_counter_resource_type_of(resource_type,
                                                                           resource_type_of,
                                                                           'each_uc')
        key_str_counter_resource_type_rating_count_received = key_str_counter_resource_type \
                                                              + '["rating_count_received"]'
        key_str_counter_resource_type_avg_rating_gained = key_str_counter_resource_type \
                                                              + '["avg_rating_gained"]'

        # iterating over each user id in contributors
        # uc: user counter
        for each_uc in user_counter_cur:
            for each_active_user_id in active_user_id_list:
                if each_active_user_id not in resource_contributors_user_ids_list:
                    userid_score_rating_dict_copy = userid_score_rating_dict.copy()

                    rating_count_received = eval(key_str_counter_resource_type_rating_count_received)
                    avg_rating_gained = eval(key_str_counter_resource_type_avg_rating_gained)
                    total_rating = sum(userid_score_rating_dict_copy.values())
                    # total_rating = rating_count_received * avg_rating_gained

                    # first time rating giving user:
                    if each_active_user_id not in userid_score_rating_dict_copy:
                        # add new key: value in dict to avoid errors
                        userid_score_rating_dict_copy.update({each_active_user_id: 0})
                        eval(key_str_counter_resource_type).update( \
                                            {'rating_count_received': (rating_count_received + 1)} )
                    total_rating = total_rating - userid_score_rating_dict_copy[each_active_user_id]
                    total_rating = total_rating + int(rating_given)

                    # getting value from updated 'rating_count_received'. hence repeated.
                    rating_count_received = eval(key_str_counter_resource_type_rating_count_received) or 1
                    # storing float result to get more accurate avg.
                    avg_rating_gained = float(format(total_rating / float(len(userid_score_rating_dict_copy.keys())), '.2f'))
                    eval(key_str_counter_resource_type).update( \
                                            {'avg_rating_gained': avg_rating_gained})

                    each_uc.save()


    def save(self, *args, **kwargs):

        is_new = False if ('_id' in self) else True

        super(Counter, self).save(*args, **kwargs)

        # storing Filehive JSON in RSC system:
        history_manager = HistoryManager()
        rcs_obj = RCS()

        if is_new:

            # Create history-version-file
            if history_manager.create_or_replace_json_file(self):
                fp = history_manager.get_file_path(self)
                message = "This document of Counter is created on " + str(datetime.datetime.now())
                rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

        else:
            # Update history-version-file
            fp = history_manager.get_file_path(self)

            try:
                rcs_obj.checkout(fp, otherflags="-f")

            except Exception as err:
                try:
                    if history_manager.create_or_replace_json_file(self):
                        fp = history_manager.get_file_path(self)
                        message = "This document of Counter is re-created on " + str(datetime.datetime.now())
                        rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

                except Exception as err:
                    print "\n DocumentError: This document (", self._id, ") can't be re-created!!!\n"
                    node_collection.collection.remove({'_id': self._id})
                    raise RuntimeError(err)

            try:
                if history_manager.create_or_replace_json_file(self):
                    message = "This document of Counter is lastly updated on " + str(datetime.datetime.now())
                    rcs_obj.checkin(fp, 1, message.encode('utf-8'))

            except Exception as err:
                print "\n DocumentError: This document (", self._id, ") can't be updated!!!\n"
                raise RuntimeError(err)

# DATABASE Variables
db = get_database()

node_collection     = db[Node.collection_name].Node
triple_collection   = db[Triple.collection_name].Triple
benchmark_collection= db[Benchmark.collection_name]
filehive_collection = db[Filehive.collection_name].Filehive
buddy_collection    = db[Buddy.collection_name].Buddy
counter_collection  = db[Counter.collection_name].Counter
gridfs_collection   = db["fs.files"]
chunk_collection    = db["fs.chunks"]

import signals

