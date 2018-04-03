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
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import get_group_name_id
try:
    from gnowsys_ndf.server_settings import GSTUDIO_INSTITUTE_ID, GSTUDIO_INSTITUTE_ID_SECONDARY, GSTUDIO_INSTITUTE_NAME
except Exception, e:
    from gnowsys_ndf.settings import GSTUDIO_INSTITUTE_ID, GSTUDIO_INSTITUTE_ID_SECONDARY, GSTUDIO_INSTITUTE_NAME

def activity_details(group_id, username):
    group_obj = get_group_name_id(group_id, get_obj=True)
    user_obj = None
    username = unicode(username.strip())
    try:
        user_obj = User.objects.get(username=username)
    except Exception as no_user:
        print "\n No user found with this {0}".format(username)

    if group_obj and user_obj:
        dt = "{:%Y%m%d-%Hh%Mm}".format(datetime.datetime.now())
        file_name = GSTUDIO_INSTITUTE_ID_SECONDARY + '-' + GSTUDIO_INSTITUTE_ID + '-' + group_id + '-activity-timespent-' + username+ '-' + dt + '.csv'

        GSTUDIO_EXPORTED_CSVS_DIRNAME = 'gstudio-exported-users-analytics-csvs'
        GSTUDIO_EXPORTED_CSVS_DIR_PATH = os.path.join('/data/', GSTUDIO_EXPORTED_CSVS_DIRNAME)

        if not os.path.exists(GSTUDIO_EXPORTED_CSVS_DIR_PATH):
            os.makedirs(GSTUDIO_EXPORTED_CSVS_DIR_PATH)

        file_name_path = os.path.join(GSTUDIO_EXPORTED_CSVS_DIR_PATH, file_name)
        column_keys_list = ['VisitedOn', 'Language','Lesson', 'Activity', 'Timespent']
        f = open(file_name_path, 'w')
        w = csv.DictWriter(f, column_keys_list)
        w.writeheader()

        regex_pattern = '^/'+group_id+'/course.*|.*my-desk.*|.*explore.*|.*tools/tool-page.*|.*course/content.*'

        all_visits = benchmark_collection.find({'calling_url': {'$regex': '.*course/activity_player.*',
         '$options': "i"}, 'user': username}).sort('last_update', -1)
        
        print "\nTotal activity-player visits in {0}: {1}".format(group_obj.name, all_visits.count())
        
        for ind, each_visit in enumerate(all_visits):
            # print each_visit
            row_dict = {'VisitedOn': 'NA', 'Language': 'NA', 'Lesson': 'NA', 'Activity': 'NA', 'Timespent': 'NA'}
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
                    lesson_id = splitted_results[4]
                    activity_id = splitted_results[5]
                    lesson_node = node_collection.one({'_id': ObjectId(lesson_id)})
                    activity_node = node_collection.one({'_id': ObjectId(activity_id)})
                    lesson_name = lesson_node.name
                    activity_name = activity_node.name
                    row_dict.update({'Lesson': lesson_name, 'Activity': activity_name})
                    print "\n {0}. Visited On: {1}".format(ind, visited_on) 
                    print " Language: ", locale
                    print " Lesson Name: ", lesson_name 
                    activity_disp_name = activity_node.name
                    if activity_node.altnames:
                        activity_disp_name = activity_node.altnames
                    print " Activity Name ({0}): {1}".format(activity_node._id, activity_disp_name)

                    nav_action_cur = benchmark_collection.find({'last_update': {'$gte': each_visit['last_update']}, 
                        '_id': {'$ne': each_visit['_id']}, 'user': username, 
                        'calling_url': {'$regex': regex_pattern, '$options': 'i' }}).sort('last_update', -1)
                    if nav_action_cur.count():
                        out_nav = nav_action_cur[0]
                        end_time = out_nav['last_update']
                        timespent = (end_time-visited_on).total_seconds()
                        print " Time spent: ", timespent, " seconds."
                        row_dict['Timespent'] = str(timespent)
                    else:
                        print " ## Unable to track time psent on this activity. ##"
                else:
                    print "## Unable to track time psent on this activity. ##"
                w.writerow(row_dict)
        f.close()
    else:
        print "\n No Group or User found with {0}/{1}".format(group_id, username)

class Command(BaseCommand):
    def handle(self, *args, **options):
        if args and len(args) == 2:
            activity_details(args[0], args[1])
        else:
            print "\n Please enter arguments"