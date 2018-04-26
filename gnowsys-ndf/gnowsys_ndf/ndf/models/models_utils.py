from base_imports import *

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
        from .buddy import Buddy
        
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
                print ('\nProcessing session of [ %d : "%s" ]' % (request.user.id, request.user.username))

                logout(request)
                print('- Successfully logout user with id: %r ' % user_id)

            except Exception as e:
                # print "Exception: ", e
                pass

        Buddy.sitewide_remove_all_buddies()


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
