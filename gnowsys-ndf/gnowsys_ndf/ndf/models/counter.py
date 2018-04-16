from base_imports import *
from node import node_collection
from group import Group
from buddy import Buddy
from history_manager import HistoryManager


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
        # {userid: <count int>, userid: <count int>, ..}

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
        
        # following is mapping of fields w.r.t. newer unit/lesson/activity implementation
        # <i2c time course>: <newer unit implementation>
        #
        # course: unit
        # modules: lesson
        # units: activities
        'course':{'modules':{'completed':int, 'total':int}, 'units':{'completed':int, 'total':int}},

        # 'visited_nodes' = {str(ObjectId): int(count_of_visits)}
        'visited_nodes': {basestring: int},
        'assessment': []
        #             [{'id: basestring, 'correct': int, 'failed_attempts': int}]
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


    # static methods:

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
    def get_group_counters(group_id_or_name):
        group_name, group_id = Group.get_group_name_id(group_id_or_name)
        return counter_collection.find({'group_id': group_id})

     
    @staticmethod
    def add_comment_pt(resource_obj_or_id, current_group_id, active_user_id_or_list=[]):
        from node import Node
        from gsystem import GSystem

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
        from node import Node
        from gsystem import GSystem

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
        from node import Node
        from gsystem import GSystem

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


counter_collection  = db[Counter.collection_name].Counter


counter_collection  = db["Counters"].Counter
