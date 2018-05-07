from base_imports import *
from group import *


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
    def get_author_obj_from_name_or_id(username_or_userid_or_authid):
        try:
            return node_collection.one({'_type': u'Author', 'created_by': int(username_or_userid_or_authid)})
        except Exception as e:
            return Group.get_group_name_id(username_or_userid_or_authid, get_obj=True)

    @staticmethod
    def extract_username(request, kwargs):
        if kwargs.get('user_name'):
            return kwargs['user_name']
        elif kwargs.get('username'):
            return kwargs['username']
        elif request:
            return request.user.username
        else:
            return ''

    @staticmethod
    def extract_userid(request, kwargs):
        if kwargs.get('user_id'):
            return kwargs['user_id']
        elif kwargs.get('userid'):
            return kwargs['userid']
        elif request and request.user.id:
            return request.user.id

        try:
            username = Author.extract_username(request, kwargs)
            return User.objects.get(username=username).id
        except Exception as e:
            print e            
        # elif:
        #     return 0

    @staticmethod
    def get_author_oid_list_from_user_id_list(user_ids_list=[], list_of_str_oids=False):
        all_authors_cur = node_collection.find({
                                            '_type': 'Author',
                                            'created_by': {'$in': [int(uid) for uid in user_ids_list]}
                                        }, {'_id': 1})
        if list_of_str_oids:
            return [str(user['_id']) for user in all_authors_cur]
        else:
            return [user['_id'] for user in all_authors_cur]


    @staticmethod
    def get_author_usernames_list_from_user_id_list(user_ids_list=[]):
        all_authors_cur = node_collection.find({
                                            '_type': 'Author',
                                            'created_by': {'$in': [int(uid) for uid in user_ids_list]}
                                        }, {'name': 1})

        result_list = auth_result_list = [user['name'] for user in all_authors_cur]
        user_ids_len = len(user_ids_list)

        # following to address objects inconsistency(if any) in mongo and sql db
        if all_authors_cur.count() != user_ids_len:
            user_result_list = User.objects.values_list('username', flat=True).filter(id__in=user_ids_list)
            if user_ids_len == user_result_list:
                result_list = user_result_list
            else:
                result_list = max(auth_result_list, user_result_list, key=len)

        return result_list


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

        auth = node_collection.find_one({'_type': u'Author', 'created_by': int(user_obj.id)})

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

