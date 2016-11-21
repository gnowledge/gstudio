''' -- imports from python libraries -- '''
import os
# import json
import time
import datetime
import csv

from pymongo import ASCENDING

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError
# from django.contrib.auth.models import User

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.settings import GSTUDIO_LOGS_DIR_PATH
from gnowsys_ndf.ndf.views.gcourse import course_analytics
# from gnowsys_ndf.ndf.views.methods import get_group_name_id
# from gnowsys_ndf.ndf.views.analytics_methods import *

if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
    os.makedirs(GSTUDIO_LOGS_DIR_PATH)

log_file_name = 'export_users_analytics.log'
log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
log_file = open(log_file_path, 'a+')
script_start_str = "######### Script ran on : " + time.strftime("%c") + " #########\n----------------\n"
log_file.write(str(script_start_str))

class Command(BaseCommand):

    def handle(self, *args, **options):
        print "Enter 'group name(case sensitive)' OR 'id': "
        group_name_or_id = raw_input()
        group_obj = Group.get_group_name_id(group_name_or_id, get_obj=True)

        if not group_obj:
            raise ValueError('\nSorry. Request could not be completed. \
                \nGroup/Course, matching argument entered "' + group_name_or_id + '" does not exists!')

        group_users = group_obj.author_set
        print group_users

        for index, each_user in enumerate(group_users):
            try:
                analytics_data = course_analytics(None, group_obj._id, each_user, get_result_dict=True)
                # refactor dict:
                analytics_data.pop('users_points_breakup')
                analytics_data.pop('users_points')

                temp_units_stat_str = analytics_data['units_progress_stmt']
                analytics_data['units_completed'] = int(temp_units_stat_str.split(' ')[0])
                analytics_data['total_units'] = int(temp_units_stat_str.split(' ')[3])
                analytics_data.pop('units_progress_stmt')

                temp_modules_stat_str = analytics_data['module_progress_stmt']
                analytics_data['modules_completed'] = int(temp_modules_stat_str.split(' ')[0])
                analytics_data['total_modules'] = int(temp_modules_stat_str.split(' ')[3])
                analytics_data.pop('module_progress_stmt')
                # print analytics_data

                with open('mycsvfile.csv', 'a') as f:  # Just use 'w' mode in 3.x
                    w = csv.DictWriter(f, analytics_data.keys())
                    if index == 0:
                        w.writeheader()
                    w.writerow(analytics_data)

            except Exception, e:
                print "\nUser with id: " + str(each_user) + " does not exists!!"
                continue