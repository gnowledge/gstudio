''' -- imports from python libraries -- '''
import os
# import json
import time
import datetime
import csv


''' imports from installed packages '''
from django.utils.text import slugify
from django.core.management.base import BaseCommand, CommandError
# from django.contrib.auth.models import User

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Group, GSystemType, node_collection
from gnowsys_ndf.settings import GSTUDIO_LOGS_DIR_PATH, GSTUDIO_DATA_ROOT
from gnowsys_ndf.ndf.views.gcourse import course_analytics
# from gnowsys_ndf.ndf.views.methods import get_group_name_id
# from gnowsys_ndf.ndf.views.analytics_methods import *

try:
    from gnowsys_ndf.server_settings import GSTUDIO_INSTITUTE_ID
except Exception, e:
    from gnowsys_ndf.settings import GSTUDIO_INSTITUTE_ID

if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
    os.makedirs(GSTUDIO_LOGS_DIR_PATH)

log_file_name = 'export_users_analytics.log'
log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
log_file = open(log_file_path, 'a+')
script_start_str = "######### Script ran on : " + time.strftime("%c") + " #########\n----------------\n"
log_file.write(str(script_start_str))


class Command(BaseCommand):

    def handle(self, *args, **options):
        gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('announced_unit')
        gst_course_ev_gr = node_collection.one({'_type': 'GSystemType', 'name': 'CourseEventGroup'})
        all_course_groups = node_collection.find({'_type': 'Group', 'member_of': {'$in': [gst_course_ev_gr._id, gst_base_unit_id]}})

        for each_group_obj in all_course_groups:
            print "\n\n Exporting CSV for :", each_group_obj.name, "(Altnames:", each_group_obj.altnames, ")\n"
            export_group_analytics(each_group_obj)


def export_group_analytics(group_obj):

        # print "Enter 'group name(case sensitive)' OR 'id': "
        # group_name_or_id = raw_input()
        # group_obj = Group.get_group_name_id(group_name_or_id, get_obj=True)

        # if not group_obj:
        #     raise ValueError('\nSorry. Request could not be completed. \
        #         \nGroup/Course, matching argument entered "' + group_name_or_id + '" does not exists!')

        group_users = group_obj.author_set
        # print group_users

        # CSV file name-convention: schoolcode-course-name-datetimestamp.csv
        try:
            group_name = slugify(group_obj['name'])
        except Exception, e:
            print e
            group_name = 'i2c'

        # dt: date time
        # e.g: '21-November-2016-19h-08m-10s'
        dt = "{:%d-%B-%Y-%Hh-%Mm-%Ss}".format(datetime.datetime.now())

        file_name = GSTUDIO_INSTITUTE_ID + '-' + group_name + '-' + dt + '.csv'

        GSTUDIO_EXPORTED_CSVS_DIRNAME = 'gstudio-exported-users-analytics-csvs'
        GSTUDIO_EXPORTED_CSVS_DIR_PATH = os.path.join('/data/', GSTUDIO_EXPORTED_CSVS_DIRNAME)

        if not os.path.exists(GSTUDIO_EXPORTED_CSVS_DIR_PATH):
            os.makedirs(GSTUDIO_EXPORTED_CSVS_DIR_PATH)

        file_name_path = os.path.join(GSTUDIO_EXPORTED_CSVS_DIR_PATH, file_name)

        for index, each_user in enumerate(group_users):
            try:
                analytics_data = course_analytics(None, group_obj._id, each_user, get_result_dict=True)
                if not analytics_data:
                    continue

                # refactor dict:
                analytics_data.pop('users_points_breakup')
                analytics_data.pop('users_points')

                try:
                    temp_units_stat_str = analytics_data['units_progress_stmt']
                    temp_units_stat_str = analytics_data['units_progress_stmt']
                    analytics_data['units_completed'] = int(temp_units_stat_str.split(' ')[0])
                    analytics_data['total_units'] = int(temp_units_stat_str.split(' ')[3])
                    analytics_data.pop('units_progress_stmt')

                    temp_modules_stat_str = analytics_data['module_progress_stmt']
                    analytics_data['modules_completed'] = int(temp_modules_stat_str.split(' ')[0])
                    analytics_data['total_modules'] = int(temp_modules_stat_str.split(' ')[3])
                    analytics_data.pop('module_progress_stmt')

                except Exception, e:
                    temp_lessons_stat_str = analytics_data['level1_progress_stmt']
                    temp_lessons_stat_str = analytics_data['level1_progress_stmt']
                    analytics_data['lessons_completed'] = int(temp_lessons_stat_str.split(' ')[0])
                    analytics_data['total_lessons'] = int(temp_lessons_stat_str.split(' ')[3])
                    analytics_data.pop('level1_progress_stmt')

                    temp_activities_stat_str = analytics_data['level2_progress_stmt']
                    analytics_data['activities_completed'] = int(temp_activities_stat_str.split(' ')[0])
                    analytics_data['total_activities'] = int(temp_activities_stat_str.split(' ')[3])
                    analytics_data.pop('level2_progress_stmt')

                    # remove non required fields
                    analytics_data.pop('level1_lbl')
                    analytics_data.pop('level2_lbl')

                    analytics_data['percentage_lessons_completed'] = analytics_data['level1_progress_meter']
                    analytics_data['percentage_activities_completed'] = analytics_data['level2_progress_meter']
                    analytics_data.pop('level1_progress_meter')
                    analytics_data.pop('level2_progress_meter')

                # print analytics_data

                with open(file_name_path, 'a') as f:  # Just use 'w' mode in 3.x
                    w = csv.DictWriter(f, analytics_data.keys())
                    if index == 0:
                        w.writeheader()
                    w.writerow(analytics_data)

            except Exception, e:
                print e
                print "\nUser with id: " + str(each_user) + " does not exists!!"
                continue
                