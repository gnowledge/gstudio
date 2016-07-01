
''' -- imports from python libraries -- '''
import os
import json
import time
import datetime
from pymongo import ASCENDING
''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GSTUDIO_LOGS_DIR_PATH
from gnowsys_ndf.ndf.views.analytics_methods import *


if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
    os.makedirs(GSTUDIO_LOGS_DIR_PATH)
log_file_name = 'fillCounter.log'
log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
log_file = open(log_file_path, 'a+')
script_start_str = "######### Script ran on : " + time.strftime("%c") + " #########\n----------------\n"
log_file.write(str(script_start_str))

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            ce_gst = node_collection.one({'_type': 'GSystemType', 'name': 'CourseEventGroup'},{'_id':1})
            all_course_events_cur = node_collection.find({'member_of': ce_gst._id})
            # Loop over each Announced Course and get their members (using author_set)
            for each_ce in all_course_events_cur:
                log_file.write("\n\n------- Course/Group: "+ str(each_ce._id) + " ----------")
                print "\n Group/Course: ", each_ce.name
                users_set = each_ce.author_set
                for each_user in users_set:
                    user_obj = User.objects.get(pk=each_user)
                    create_or_update_counter(user_obj,each_ce._id)
            log_file.close()
        except Exception as fillCounterError:
            print "\n Error occurred!!!" + str(fillCounterError)


def create_or_update_counter(user_obj, group_id):

    counter_obj = counter_collection.one({'user_id': user_obj.id, 'group_id': group_id})
    if not counter_obj:
        log_file.write("\n\nCreating Counter for User: "+ str(user_obj.id)+ "  Group :"+ str(group_id))
        counter_obj = counter_collection.collection.Counter()
    else:
        log_file.write("\n\nUpdating Counter for User: "+ str(user_obj.id)+ "  Group :"+ str(group_id))
    auth_node = node_collection.one({'_type': 'Author', 'created_by': user_obj.id})

    analytics_instance = AnalyticsMethods(user_obj.id,user_obj.username, group_id)

    counter_obj.auth_id = auth_node._id
    counter_obj.group_id = group_id
    counter_obj.user_id = user_obj.id

    #counter_obj.modules_completed = analytics_instance.get_completed_modules_count()
    #counter_obj.units_completed = analytics_instance.get_completed_units_count()
    # Calculate points of user
    #counter_obj.course_score = analytics_instance.get_users_points()
    # Get all comments posted by user

    ## INTERACTIONS ##
    counter_obj.no_comments_by_user = analytics_instance.get_total_comments_by_user()

    ## FILES ##
    # Get all files uploaded by user
    counter_obj.no_files_created = analytics_instance.get_user_files_count()
    # Get all comments posted on files uploaded by user
    counter_obj.no_comments_received_on_files = analytics_instance.get_comments_counts_on_users_files()
    # Get all files on which the user has posted a comment
    counter_obj.no_comments_on_others_files = analytics_instance.get_other_files_commented_by_user_count()
    # Get all unique users who visited files uploaded by user
    counter_obj.no_others_files_visited = analytics_instance.get_others_files_read_count()
    counter_obj.avg_rating_received_on_files = float(analytics_instance.get_ratings_received_on_user_files())

    ## NOTES ##
    # Get all notes/blog pages created by user
    counter_obj.no_notes_written = analytics_instance.get_user_notes_count()
    # Get all comments posted on notes created by user
    counter_obj.no_comments_received_on_notes = analytics_instance.get_comments_counts_on_users_notes()
    # Get all notes on which user has posted comment
    counter_obj.no_comments_on_others_notes = analytics_instance.get_other_notes_commented_by_user_count()
    # Get all unique users who visited notes created by user
    counter_obj.no_views_gained_on_notes = analytics_instance.total_users_read_my_notes()
    counter_obj.no_others_notes_visited = analytics_instance.get_others_notes_read_count()
    counter_obj.avg_rating_received_on_notes = float(analytics_instance.get_ratings_received_on_user_notes())

    ## QUIZ ##
    # Get all quizitemevents attempted correctly by user
    counter_obj.no_correct_answers= analytics_instance.get_evaluated_quizitems_count(True,False)
    # Get all quizitemevents attempted incorrectly by user
    counter_obj.no_incorrect_answers = analytics_instance.get_evaluated_quizitems_count(False,True)
    # Get all quizitemevents attempted by user
    counter_obj.no_questions_attempted = analytics_instance.get_attempted_quizitems_count()

    counter_obj.save()
    log_file.write(str(counter_obj.to_json()))

