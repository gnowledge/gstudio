''' -- imports from python libraries -- '''
import os
import time
import datetime
import csv
from collections import OrderedDict
# import json


''' imports from installed packages '''
from django.utils.text import slugify
from django.core.management.base import BaseCommand, CommandError
# from django.contrib.auth.models import User

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Group, GSystemType, Counter, node_collection, Buddy, Author
from gnowsys_ndf.settings import GSTUDIO_LOGS_DIR_PATH, GSTUDIO_DATA_ROOT
from gnowsys_ndf.ndf.views.gcourse import course_analytics
# from gnowsys_ndf.ndf.views.methods import get_group_name_id   
# from gnowsys_ndf.ndf.views.analytics_methods import *

try:
    from gnowsys_ndf.server_settings import GSTUDIO_INSTITUTE_ID, GSTUDIO_INSTITUTE_ID_SECONDARY, GSTUDIO_INSTITUTE_NAME
except Exception, e:
    from gnowsys_ndf.settings import GSTUDIO_INSTITUTE_ID, GSTUDIO_INSTITUTE_ID_SECONDARY, GSTUDIO_INSTITUTE_NAME

if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
    os.makedirs(GSTUDIO_LOGS_DIR_PATH)

log_file_name = 'export_users_analytics.log'
log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
log_file = open(log_file_path, 'a+')
script_start_str = "\n\n######### Script ran on : " + time.strftime("%c") + " #########\n----------------\n"
log_file.write(str(script_start_str))

column_keys_list = ["server_id", "school_name", "school_code", "unit_name", "username", "user_id", "enrollment_status", "total_lessons", "lessons_completed", "percentage_lessons_completed", "total_activities", "activities_completed", "percentage_activities_completed", "total_quizitems", "visited_quizitems", "attempted_quizitems", "unattempted_quizitems", "correct_attempted_quizitems", "notapplicable_quizitems", "incorrect_attempted_quizitems", "user_files", "total_files_viewed_by_user", "other_viewing_my_files", "unique_users_commented_on_user_files", "total_rating_rcvd_on_files", "commented_on_others_files", "cmts_on_user_files", "total_cmnts_by_user", "user_notes", "others_reading_my_notes", "cmts_on_user_notes", "cmnts_rcvd_by_user", "total_notes_read_by_user", "commented_on_others_notes", "total_rating_rcvd_on_notes", "correct_attempted_assessments", "unattempted_assessments", "visited_assessments", "notapplicable_assessments", "incorrect_attempted_assessments", "attempted_assessments", "total_assessment_items", "buddies"]

column_keys_dict = OrderedDict()
map(lambda x: column_keys_dict.update({x: "NA"}), column_keys_list)


class Command(BaseCommand):

    def handle(self, *args, **options):
        gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('announced_unit')
        gst_course_ev_gr = node_collection.one({'_type': 'GSystemType', 'name': 'CourseEventGroup'})
        all_course_groups = node_collection.find({'_type': 'Group', 'member_of': {'$in': [gst_course_ev_gr._id, gst_base_unit_id]} })

        for each_group_obj in all_course_groups:
            assessment_and_quiz_data = True
            print "\n\n Exporting CSV for :", each_group_obj.name, "(Altnames:", each_group_obj.altnames, ")\n"
            export_group_analytics(each_group_obj, assessment_and_quiz_data)


def export_group_analytics(group_obj, assessment_and_quiz_data):

    # print "Enter 'group name(case sensitive)' OR 'id': "
    # group_name_or_id = raw_input()
    # group_obj = Group.get_group_name_id(group_name_or_id, get_obj=True)

    # if not group_obj:
    #     raise ValueError('\nSorry. Request could not be completed. \
    #         \nGroup/Course, matching argument entered "' + group_name_or_id + '" does not exists!')

    # group_users = group_obj.author_set
    # Previously, above was implementation strategy. Now we are using counter users instead of group's author_set,
    # because we do wanted to gather all data irrespective of student enrollment.
    group_users = Counter.get_group_counters(group_obj._id).distinct('user_id')
    # group_users is a list of integer user ids
    # print group_users

    # CSV file name-convention: schoolcode-course-name-datetimestamp.csv
    try:
        group_name = slugify(group_obj['name'])
    except Exception, e:
        print e
        group_name = str(group_obj['_id'])

    # dt: date time
    # e.g: '21-November-2016-19h-08m-10s'
    # dt = "{:%d-%B-%Y-%Hh-%Mm-%Ss}".format(datetime.datetime.now())
    dt = "{:%Y%m%d-%Hh%Mm}".format(datetime.datetime.now())

    file_name = GSTUDIO_INSTITUTE_ID_SECONDARY + '-' + GSTUDIO_INSTITUTE_ID + '-' + group_name + '-' + dt + '.csv'

    GSTUDIO_EXPORTED_CSVS_DIRNAME = 'gstudio-exported-users-analytics-csvs'
    GSTUDIO_EXPORTED_CSVS_DIR_PATH = os.path.join('/data/', GSTUDIO_EXPORTED_CSVS_DIRNAME)

    if not os.path.exists(GSTUDIO_EXPORTED_CSVS_DIR_PATH):
        os.makedirs(GSTUDIO_EXPORTED_CSVS_DIR_PATH)

    file_name_path = os.path.join(GSTUDIO_EXPORTED_CSVS_DIR_PATH, file_name)

    header_written = False
    for index, each_user in enumerate(group_users):
        try:
            analytics_data = course_analytics(None, group_obj._id, each_user, get_result_dict=True, assessment_and_quiz_data=assessment_and_quiz_data)
            if not analytics_data:
                continue

            print index, "] Group User ID: ", each_user

            each_row_dict = column_keys_dict.copy()    
            each_row_dict['server_id'] = GSTUDIO_INSTITUTE_ID
            each_row_dict['school_code'] = GSTUDIO_INSTITUTE_ID_SECONDARY
            each_row_dict['school_name'] = GSTUDIO_INSTITUTE_NAME
            each_row_dict['unit_name'] = group_name

            temp_lessons_stat_str = analytics_data['level1_progress_stmt']
            temp_lessons_stat_str = analytics_data['level1_progress_stmt']
            each_row_dict['lessons_completed'] = int(temp_lessons_stat_str.split(' ')[0])
            each_row_dict['total_lessons'] = int(temp_lessons_stat_str.split(' ')[3])

            temp_activities_stat_str = analytics_data['level2_progress_stmt']
            each_row_dict['activities_completed'] = int(temp_activities_stat_str.split(' ')[0])
            each_row_dict['total_activities'] = int(temp_activities_stat_str.split(' ')[3])

            each_row_dict['percentage_lessons_completed'] = analytics_data['level1_progress_meter']
            each_row_dict['percentage_activities_completed'] = analytics_data['level2_progress_meter']

            each_row_dict['username'] = analytics_data['username']
            each_row_dict['user_id'] = each_user
            each_row_dict['enrollment_status'] = "Yes" if (each_user in group_obj.author_set) else "No"
            each_row_dict['total_quizitems'] = analytics_data['total_quizitems']
            each_row_dict['visited_quizitems'] = analytics_data['visited_quizitems']
            each_row_dict['unattempted_quizitems'] = analytics_data['unattempted_quizitems']
            each_row_dict['attempted_quizitems'] = analytics_data['attempted_quizitems']
            each_row_dict['incorrect_attempted_quizitems'] = analytics_data['incorrect_attempted_quizitems']
            each_row_dict['correct_attempted_quizitems'] = analytics_data['correct_attempted_quizitems']
            each_row_dict['notapplicable_quizitems'] = analytics_data['notapplicable_quizitems']
            each_row_dict['unique_users_commented_on_user_files'] = analytics_data['unique_users_commented_on_user_files']
            each_row_dict['user_files'] = analytics_data['user_files']
            each_row_dict['total_files_viewed_by_user'] = analytics_data['total_files_viewed_by_user']
            each_row_dict['other_viewing_my_files'] = analytics_data['other_viewing_my_files']
            each_row_dict['total_rating_rcvd_on_files'] = analytics_data['total_rating_rcvd_on_files']
            each_row_dict['commented_on_others_files'] = analytics_data['commented_on_others_files']
            each_row_dict['cmts_on_user_files'] = analytics_data['cmts_on_user_files']
            each_row_dict['total_cmnts_by_user'] = analytics_data['total_cmnts_by_user']
            each_row_dict['user_notes'] = analytics_data['user_notes']
            each_row_dict['others_reading_my_notes'] = analytics_data['others_reading_my_notes']
            each_row_dict['cmts_on_user_notes'] = analytics_data['cmts_on_user_notes']
            each_row_dict['cmnts_rcvd_by_user'] = analytics_data['cmnts_rcvd_by_user']
            each_row_dict['total_notes_read_by_user'] = analytics_data['total_notes_read_by_user']
            each_row_dict['commented_on_others_notes'] = analytics_data['commented_on_others_notes']
            each_row_dict['total_rating_rcvd_on_notes'] = analytics_data['total_rating_rcvd_on_notes']
            each_row_dict["correct_attempted_assessments"] = analytics_data["correct_attempted_assessments"]
            each_row_dict["unattempted_assessments"] = analytics_data["unattempted_assessments"]
            each_row_dict["visited_assessments"] = analytics_data["visited_assessments"]
            each_row_dict["notapplicable_assessments"] = analytics_data["notapplicable_assessments"]
            each_row_dict["incorrect_attempted_assessments"] = analytics_data["incorrect_attempted_assessments"]
            each_row_dict["attempted_assessments"] = analytics_data["attempted_assessments"]
            each_row_dict["total_assessment_items"] = analytics_data["total_assessment_items"]
            # each_row_dict["buddies"] = str(Buddy.get_buddy_userids_list_within_datetime(1, datetime.datetime.now()))
            each_row_dict["buddies"] = Author.get_author_usernames_list_from_user_id_list\
                (Buddy.get_buddy_userids_list_within_datetime(each_user, datetime.datetime.now()))
            # print analytics_data

            with open(file_name_path, 'a') as f:  # Just use 'w' mode in 3.x
                w = csv.DictWriter(f, column_keys_list)
                if not header_written:
                    w.writeheader()
                    header_written = True
                w.writerow(each_row_dict)

        except Exception, e:
            print e
            error_msg = "\nUser with id: " + str(each_user) + " does not exists!!"
            log_file.write(str(e))
            log_file.write(error_msg)
            continue
            