import datetime
import re
import json
import csv

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import get_group_name_id
try:
    from gnowsys_ndf.server_settings import GSTUDIO_INSTITUTE_ID, GSTUDIO_INSTITUTE_ID_SECONDARY, GSTUDIO_INSTITUTE_NAME
except Exception, e:
    from gnowsys_ndf.settings import GSTUDIO_INSTITUTE_ID, GSTUDIO_INSTITUTE_ID_SECONDARY, GSTUDIO_INSTITUTE_NAME

def activity_details(username):
    '''
    For particular user, fetches all benchmarks records that satisfies the url match.
    Parses the records to get information about the page/activity details (name/altnames/id)
        and context (group-id aka unit-id)
    '''
    user_obj = None
    username = unicode(username.strip())
    try:
        user_obj = User.objects.get(username=username)
    except Exception as no_user:
        print "\n No user found with this {0}".format(username)

    if user_obj:
        dt = "{:%Y%m%d-%Hh%Mm}".format(datetime.datetime.now())
        file_name = GSTUDIO_INSTITUTE_ID + '-' + username+ '-activity-visits-' + dt + '.csv'

        GSTUDIO_EXPORTED_CSVS_DIRNAME = 'activity-timestamp-csvs'
        GSTUDIO_EXPORTED_CSVS_DIR_PATH = os.path.join('/data/', GSTUDIO_EXPORTED_CSVS_DIRNAME)

        if not os.path.exists(GSTUDIO_EXPORTED_CSVS_DIR_PATH):
            os.makedirs(GSTUDIO_EXPORTED_CSVS_DIR_PATH)

        file_name_path = os.path.join(GSTUDIO_EXPORTED_CSVS_DIR_PATH, file_name)
        column_keys_list = ['Unit','Lesson', 'Activity', 'Language', 'VisitedOn', 'OutTime', 'OutAction','TimeSpentInSeconds', 'Buddies']
        f = open(file_name_path, 'w')
        w = csv.DictWriter(f, column_keys_list)
        w.writeheader()

        activity_in_regex_pattern = ".*/course/activity_player.*"
        activity_out_regex_pattern = '.*/course.*|.*my-desk.*|.*explore.*|.*tools/tool-page.*|.*course/content.*'
        #activity_out_regex_pattern = '^/'+group_id+'/course.*|.*my-desk.*|.*explore.*|.*tools/tool-page.*|.*course/content.*'

        all_visits = benchmark_collection.find({'calling_url': {'$regex': activity_in_regex_pattern,
         '$options': "i"}, 'user': username},timeout=False).sort('last_update', -1)
        
        print "\nTotal activity-player visits: {0}".format(all_visits.count())
        
        for ind, each_visit in enumerate(all_visits):
            # print each_visit
            row_dict = {'Unit' : 'NA','Lesson' : 'NA', 'Activity' : 'NA', 'Language' : 'NA', 'VisitedOn' : 'NA', 'OutTime' : 'NA', 'OutAction' : 'NA','TimeSpentInSeconds' : 'NA', 'Buddies' : 'NA'}
            unit_name = 'NA'
            activity_name = 'NA'
            lesson_name = 'NA'
            visited_on = each_visit['last_update']
            row_dict['VisitedOn'] = str(visited_on)
            locale = each_visit['locale']
            if not locale:
                locale = 'en'
            row_dict['Language'] = str(locale)
            calling_url_str = each_visit['calling_url']
            if calling_url_str.startswith('/') and calling_url_str.endswith('/'):
                splitted_results = calling_url_str.split('/')

                if len(splitted_results) == 7:
                    unit_id = splitted_results[1]
                    lesson_id = splitted_results[4]
                    activity_id = splitted_results[5]
                    unit_node = get_group_name_id(unit_id, get_obj=True)
                    lesson_node = node_collection.one({'_id': ObjectId(lesson_id)})
                    activity_node = node_collection.one({'_id': ObjectId(activity_id)})
                    if lesson_node and lesson_id:
                        lesson_name = lesson_node.name
                    if activity_node and activity_id:
                        activity_name = activity_node.name
                    if unit_node and unit_id:
                        unit_name = unit_node.name
                        if unit_node.altnames:
                            unit_name = unit_node.altnames
                    if activity_node:
                        if activity_node.altnames:
                            activity_name = activity_node.altnames
                    
                    row_dict.update({'Unit': slugify(unit_name), 'Lesson': slugify(lesson_name), 
                        'Activity': slugify(activity_name)})

                    
                    # print "\n {0}. Unit: ".format(ind), unit_name
                    # print " Lesson Name: ", lesson_name
                    # print " Activity Name ({0}): {1}".format(activity_node._id, activity_disp_name)
                    # print " Visited On: {0}".format(visited_on)
                    # print " Language: ", locale

                    nav_out_action_cur = benchmark_collection.find({'last_update': {'$gte': each_visit['last_update']}, 
                        '_id': {'$ne': each_visit['_id']}, 'user': username, 'session_key': each_visit['session_key'],
                        'calling_url': {'$regex': activity_out_regex_pattern, '$options': 'i' }},timeout=False).sort('last_update', 1)
                    if nav_out_action_cur.count():
                        nav_out_obj = nav_out_action_cur[0]
                        end_time = nav_out_obj['last_update']
                        timespent = (end_time-visited_on).total_seconds()
                        print " Time spent: ", timespent, " seconds."
                        row_dict.update({'TimeSpentInSeconds': str(timespent), 'OutAction': nav_out_obj['name'], 'OutTime' : end_time})
                    else:
                        print " ## Unable to track time spent on this activity. ##"
                    buddies_obj = Buddy.query_buddy_obj(user_obj.pk, each_visit['session_key'])
                    if buddies_obj:
                        auth_id_list = buddies_obj.get_all_buddies_auth_ids()
                        buddies_names = Node.get_names_list_from_obj_id_list(auth_id_list, u'Author')
                        print " Buddies: ", buddies_names
                        row_dict.update({'Buddies': buddies_names})
                else:
                    print "## Unable to track time psent on this activity. ##"
                w.writerow(row_dict)
        f.close()
    else:
        print "\n No User found with {0}".format(username)


class Command(BaseCommand):

    def handle(self, *args, **options):
        username = ''

        if args and len(args) == 1:
            username = args[0]
        else:
            while not username.strip():
                username = raw_input("\n Please enter username: ")

        if username:
            print "\n====: Processing for username: {} :====".format(username)
            from timeit import default_timer
            start_time = default_timer()
            activity_details(username)
            end_time = default_timer()
            print "\n\n", ("=" * 50)
            print "Time Required to process: {} Minutes".format((end_time - start_time)/60)
            print "=" * 50, "\n\n"
