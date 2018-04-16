from base_imports import *
from history_manager import HistoryManager

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

        if 'member_of' in values_dict  and not isinstance(values_dict['member_of'],ObjectId):
            from gsystem_type import GSystemType
            gst_node = GSystemType.get_gst_name_id(values_dict['member_of'])
            if gst_node:
                values_dict.update({'member_of': ObjectId(gst_node[1])})

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


    def get_tree_nodes(node_id_or_obj, field_name, level, get_obj=False):
        '''
        node_id_or_obj: root node's _id or obj
        field_name: It can be either of collection_set, prior_node
        level: starts from 0
        '''
        node_obj = Node.get_node_obj_from_id_or_obj(node_id_or_obj, Node)
        nodes_ids_list = node_obj[field_name]
        while level:
           nodes_ids_cur = Node.get_nodes_by_ids_list(nodes_ids_list)
           nodes_ids_list = []
           if nodes_ids_cur:
               [nodes_ids_list.extend(i[field_name]) for i in nodes_ids_cur]
           level = level - 1

        if get_obj:
            return Node.get_nodes_by_ids_list(nodes_ids_list)

        return nodes_ids_list


    ########## Setter(@x.setter) & Getter(@property) ##########
    @property
    def member_of_names_list(self):
        """Returns a list having names of each member (GSystemType, i.e Page,
        File, etc.), built from 'member_of' field (list of ObjectIds)

        """
        from gsystem_type import GSystemType
        return [GSystemType.get_gst_name_id(gst_id)[0] for gst_id in self.member_of]


    @property
    def group_set_names_list(self):
        """Returns a list having names of each member (Group name),
        built from 'group_set' field (list of ObjectIds)

        """
        from group import Group
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
            from buddy import Buddy
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

        # TO BE COMMENTED map-reduce code:
        # 
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
        from attribute_type import AttributeType

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
                from triple import triple_collection
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
        from relation_type import RelationType
        
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
                from triple import triple_collection
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
                from triple import triple_collection
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
        from gattribute import GAttribute
        return GAttribute.get_triples_from_sub_type(self._id, attribute_type_name, status)

    def get_attributes_from_names_list(self, attribute_type_name_list, status=None, get_obj=False):
        from gattribute import GAttribute
        return GAttribute.get_triples_from_sub_type_list(self._id, attribute_type_name_list, status, get_obj)

    def get_relation(self, relation_type_name, status=None):
        from grelation import GRelation
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

    @staticmethod
    def get_names_list_from_obj_id_list(obj_ids_list, node_type):
        obj_ids_list = map(ObjectId, obj_ids_list)
        nodes_cur = node_collection.find({
                                            '_type': node_type,
                                            '_id': {'$in': obj_ids_list}
                                        }, {'name': 1})
        result_list = [node['name'] for node in nodes_cur]
        return result_list


# DATABASE Variables
node_collection     = db[Node.collection_name].Node
