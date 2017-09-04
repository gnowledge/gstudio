''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import re
''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
from django.template.defaultfilters import slugify
import json
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
# from gnowsys_ndf.ndf.views.methods import get_counter_obj
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GAPPS, GSTUDIO_QUIZ_CORRECT_POINTS
from gnowsys_ndf.ndf.models import GSystemType, GSystem
from gnowsys_ndf.ndf.models import QUIZ_TYPE_CHOICES
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.rcslib import RCS
# from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.views.methods import get_node_common_fields,create_grelation_list,get_execution_time
from gnowsys_ndf.ndf.management.commands.data_entry import create_gattribute
from gnowsys_ndf.ndf.views.methods import get_node_metadata, set_all_urls, get_group_name_id, create_thread_for_node
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_relation_value, get_attribute_value, get_thread_node


#######################################################################################################################################

gst_quiz = node_collection.one({'_type': u'GSystemType', 'name': "Quiz"})
history_manager = HistoryManager()
rcs = RCS()
app = gst_quiz

##############################################################################
#       V I E W S   D E F I N E D   F O R   G A P P -- ' Q U I Z '
##############################################################################
@get_execution_time
def quiz(request, group_id):
    """Renders a list of all 'Quiz-type-GSystems' available within the database.
    """
    group_obj = get_group_name_id(group_id, get_obj=True)
    group_id = group_obj._id
    group_name = group_obj.name
    title = gst_quiz.name
    quiz_nodes = node_collection.find({'member_of': gst_quiz._id, 'group_set': ObjectId(group_id)}).sort('last_update', -1)
    gst_quiz_names = ['QuizItem']
    supported_languages = ['Hindi', 'Telugu']
    if "CourseEventGroup" in group_obj.member_of_names_list or "announced_unit" in group_obj.member_of_names_list:
        gst_quiz_names.append('QuizItemEvent')
    gst_quiz_item = node_collection.find({'_type': 'GSystemType', 'name': {'$in': gst_quiz_names}})
    gst_quiz_item_ids = [each_quiz_gst._id for each_quiz_gst in gst_quiz_item]
    quiz_item_nodes = node_collection.find({'member_of': {'$in': gst_quiz_item_ids}, 'group_set': ObjectId(group_id)}).sort('last_update', -1)
    return render_to_response("ndf/quiz.html",
                              {'title': title,
                               'quiz_nodes': quiz_nodes,
                               'quiz_item_nodes': quiz_item_nodes,
                               'groupid':group_id,
                               'group_id':group_id,
                               'supported_languages': supported_languages
                              },
                              context_instance=RequestContext(request)
    )

@get_execution_time
def quiz_item_detail(request, group_id, node_id=None):
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    quiz_item_node = node_collection.one({'_id': ObjectId(node_id)})
    template = "ndf/node_details_base.html"
    print "\nLeaving"
    quiz_item_node.get_neighbourhood(quiz_item_node.member_of)
    variable = RequestContext(request, {'node': quiz_item_node, 'groupid': group_id,
     'group_id': group_id})
    return render_to_response(template,
                              variable,
                              context_instance=RequestContext(request))


@login_required
def create_edit_quiz_item(request, group_id, node_id=None):
    """Creates/Modifies details about the given quiz-item.
    """
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    group_object = node_collection.one({'_id': ObjectId(group_id)})

    node = None
    quiz_node = None
    quiz_node_id = None
    quiz_item_node = None
    group_object_member_of_names_list = group_object.member_of_names_list
    gst_quiz_item = node_collection.one({'_type': u'GSystemType', 'name': u'QuizItem'})
    if "CourseEventGroup" in group_object_member_of_names_list or "announced_unit" in group_object_member_of_names_list:
        gst_quiz_item = node_collection.one({'_type': u'GSystemType', 'name': u'QuizItemEvent'})

    # if node_id:
    #     quiz_item_node = node_collection.one({'_id': ObjectId(node_id)})
    quiz_node_id = request.GET.get('quiznode','')
    return_url = request.GET.get('return_url','')
    context_variables = { 'title': gst_quiz_item.name,
                          'quiz_type_choices': QUIZ_TYPE_CHOICES,
                          'group_id': group_id,
                          'groupid': group_id,

                        }
    if return_url:
        context_variables['return_url'] = return_url
    if quiz_node_id:
        quiz_node = node_collection.one({'_id': ObjectId(quiz_node_id)})
        context_variables['quiz_node_id'] = quiz_node._id
    if node_id:
        node = node_collection.one({'_id': ObjectId(node_id)})
        if gst_quiz._id in node.member_of:
            # Add question from a given Quiz category's context
            quiz_node = node
        else:
            # Edit a question
            quiz_item_node = node


    if request.method == "POST":
        usrid = int(request.user.id)
        usrname = unicode(request.user.username)

        # if node_id:
        #     quiz_item_node = node_collection.one({'_id': ObjectId(node_id)})
        # else:
        #     # Add miscellaneous question
        #     quiz_item_node = node_collection.collection.GSystem()

        if node_id:
            node = node_collection.one({'_id': ObjectId(node_id)})

            if gst_quiz._id in node.member_of:
                # Add question from a given Quiz category's context
                quiz_node = node
                quiz_item_node = node_collection.collection.GSystem()

            else:
                # Edit a question
                quiz_item_node = node
        else:
            # Add miscellaneous question
            quiz_item_node = node_collection.collection.GSystem()
            # quiz_item_node = node_collection.one({'_id': ObjectId(node_id)})
        # question_content = request.POST.get('content_org','')
        question_content = request.POST.get('quiz_item_name','Untitled')
        question_content = question_content.split(' ')
        question_content = question_content[:4]
        question_content = ' '.join(question_content)
        # print "\n\n question_content---",question_content
        question_content = re.sub('<[^>]*>', ' ', question_content)
        quiz_item_node.name = unicode(question_content)
        quiz_type_AT = node_collection.one({'_type': "AttributeType", 'name': "quiz_type"})
        options_AT = node_collection.one({'_type': "AttributeType", 'name': "options"})
        correct_answer_AT = node_collection.one({'_type': "AttributeType", 'name': "correct_answer"})
        quizitem_show_correct_ans_AT = node_collection.one({'_type': "AttributeType", 'name': "quizitem_show_correct_ans"})
        quizitem_problem_weight_AT = node_collection.one({'_type': "AttributeType", 'name': "quizitem_problem_weight"})
        quizitem_max_attempts_AT = node_collection.one({'_type': "AttributeType", 'name': "quizitem_max_attempts"})
        quizitem_check_ans_AT = node_collection.one({'_type': "AttributeType", 'name': "quizitem_check_answer"})


        quiz_node_id = request.POST.get('quiz_node_id','')
        maximum_attempts_val = request.POST.get('maximum_attempts','1')
        problem_weight_val = request.POST.get('problem_weight','1')
        show_correct_ans_val = request.POST.get('show_correct_ans','False')
        check_ans_val = request.POST.get('check_ans','False')
        # print "\n\n maximum_attempts",maximum_attempts_val

        # print "\n problem_weight",problem_weight_val
        # print "\n show_correct_ans",show_correct_ans_val

        quiz_item_node.save(is_changed=get_node_common_fields(request, quiz_item_node, group_id, gst_quiz_item),groupid=group_id)
        if quiz_node_id:
            quiz_node = node_collection.one({'_id': ObjectId(quiz_node_id)})
        quiz_type = request.POST.get('quiz_type_val','')

        # create gattribute quiz_type,options, correct_answer
        # quiz_item_node['quiz_type'] = unicode(quiz_type)
        create_gattribute(quiz_item_node._id, quizitem_max_attempts_AT, int(maximum_attempts_val))
        create_gattribute(quiz_item_node._id, quizitem_problem_weight_AT, float(problem_weight_val))
        create_gattribute(quiz_item_node._id, quizitem_show_correct_ans_AT, eval(show_correct_ans_val))
        create_gattribute(quiz_item_node._id, quiz_type_AT, unicode(quiz_type))
        create_gattribute(quiz_item_node._id, quizitem_check_ans_AT, eval(check_ans_val))

        # If "quiz_type" is either 'Single-Choice' or 'Multiple-Choice', then only extract options
        options = []
        if quiz_type != QUIZ_TYPE_CHOICES[0]:
            no_of_options = int(request.POST.get('no_of_options',''))
            # quiz_item_node['options'] = []
            # print "\n\n no_of_options",no_of_options
            i = 1
            while i <= no_of_options:
                options.append(request.POST.get("option" if i == 1 else "option_"+str(i)))
                i = i + 1

            # quiz_item_node['options'] = options
            create_gattribute(quiz_item_node._id, options_AT, options)

        # Extracting correct-answer, depending upon 'Multiple-Choice' / 'Single-Choice'
        qt_initial = quiz_type[:quiz_type.find("-")].lower()
        # quiz_item_node['correct_answer'] = []

        correct_ans_val = None
        if quiz_type == QUIZ_TYPE_CHOICES[1]: # Single Choice
            correct_ans_val = request.POST.getlist('correct_answer_' + qt_initial)
            # quiz_item_node['correct_answer'].append(correct_answer)
        elif quiz_type == QUIZ_TYPE_CHOICES[2]: # Multiple Choice
            correct_ans_val = request.POST.getlist('correct_answer_' + qt_initial)
            # quiz_item_node['correct_answer'] = correct_answer

        if correct_ans_val: # To handle if Quiz-type is Short-Response
            correct_answer = map(int,correct_ans_val) # Convert list of unicode ele to list of int ele
            correct_ans_val_list = [options[each_val-1] for each_val in correct_answer]
            create_gattribute(quiz_item_node._id, correct_answer_AT, correct_ans_val_list)

        # thread_obj = create_thread_for_node(request,group_id, quiz_item_node)

        quiz_item_node.reload()
        quiz_item_node.status = u"PUBLISHED"

        quiz_item_node.save(groupid=group_id)

        # Create a thread for QuizItem also. Can be used in preview
        # Create thread node
        create_thread_for_node_flag = True
        if quiz_item_node.relation_set:
            for eachrel in quiz_item_node.relation_set:
                if eachrel and "has_thread" in eachrel:
                    create_thread_for_node_flag = False
        if create_thread_for_node_flag:
            return_status = create_thread_for_node(request,group_id, quiz_item_node)
        if "QuizItemEvent" in quiz_item_node.member_of_names_list:
            return_url = request.POST.get("return_url")
            # print "\n\n return_url", return_url, type(return_url)
            if return_url:
                return HttpResponseRedirect(reverse(return_url, kwargs={'group_id': group_id}))
            return HttpResponseRedirect(return_url)
        if quiz_node:
            quiz_node.collection_set.append(quiz_item_node._id)
            quiz_node.save(groupid=group_id)
        return HttpResponseRedirect(reverse('quiz', kwargs={'group_id': group_id}))
    else:
        if node_id:
            if quiz_item_node:
                quiz_item_node.get_neighbourhood(quiz_item_node.member_of)
                context_variables['node'] = quiz_item_node
            context_variables['groupid'] = group_id
            context_variables['group_id'] = group_id
            # context_variables['quiz_node']=quiz_node
        return render_to_response("ndf/quiz_item_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
                              )

@login_required
@get_execution_time
def create_edit_quiz(request, group_id, node_id=None):
    """Creates/Edits quiz category.
    """
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    context_variables = { 'title': gst_quiz.name,
                          'group_id': group_id,
                          'groupid': group_id
                        }
    if node_id:
        quiz_node = node_collection.one({'_type': u'GSystem', '_id': ObjectId(node_id)})

    if request.method == "POST":
        if node_id:
            quiz_node = node_collection.one({'_type': u'GSystem', '_id': ObjectId(node_id)})
        else:
            quiz_node = node_collection.collection.GSystem()
        # get_node_common_fields(request, quiz_node, group_id, gst_quiz)
        quiz_node.save(is_changed=get_node_common_fields(request, quiz_node, group_id, gst_quiz),groupid=group_id)
        quiz_node.get_neighbourhood(quiz_node.member_of)
        # get_node_metadata(request, quiz_node,gst_quiz)
        #if teaches is required
        # teaches_list = request.POST.get('teaches_list','') # get the teaches list
        # if teaches_list !='':
        #       teaches_list=teaches_list.split(",")
        # create_grelation_list(quiz_node._id,"teaches",teaches_list)

        # assesses_list = request.POST.get('assesses_list','') # get the assesses list
        # if assesses_list !='':
        #       assesses_list=assesses_list.split(",")
        # create_grelation_list(quiz_node._id,"assesses",assesses_list)
        return HttpResponseRedirect(reverse('quiz_details', kwargs={'group_id': group_id, 'node_id': quiz_node._id}))
    else:
        if node_id:
            context_variables['node'] = quiz_node
            context_variables['groupid'] = group_id
            context_variables['group_id']=group_id
            # context_variables['appId']=app._id
        return render_to_response("ndf/quiz_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
        )

@login_required
@get_execution_time
def quiz_details(request, group_id, node_id):
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    title = gst_quiz.name
    gst_quiz_item = node_collection.one({'_type': 'GSystemType', 'name': u'QuizItem'})

    quiz_node = node_collection.one({'_id': ObjectId(node_id)})
    quiz_item_nodes = None
    # quiz_item_nodes = node_collection.find({'_id': {'$in': quiz_node.collection_set}, 'member_of': gst_quiz_item._id }).sort('last_update', -1)
    # quiz_node.get_neighbourhood(quiz_node.member_of)

    context_variables = {'groupid': group_id,
                        'group_id': group_id,
                        'title': title,
                        'node': quiz_node,
                        'quiz_item_nodes':quiz_item_nodes
    }
    return render_to_response("ndf/quiz_details.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
        )


@login_required
@get_execution_time
def save_quizitem_answer(request, group_id):
    response_dict = {"success": False}
    try:
        if request.is_ajax() and request.method == "POST":
            try:
                group_id = ObjectId(group_id)
            except:
                group_name, group_id = get_group_name_id(group_id)
            import datetime

            new_list = []
            old_submitted_ans = None
            recent_ans = None
            is_user_given_ans_not_in_recent_submitted_ans = False
            recent_submitted_ans_was_correct = False

            user_given_ans = request.POST.getlist("user_given_ans[]", '')
            node_id = request.POST.get("node", '')
            node_obj = node_collection.one({'_id': ObjectId(node_id)})
            thread_obj = user_ans = None
            '''
            print "\n\n node_obj::::::::",node_obj.relation_set
            try:
                for each_rel in node_obj.relation_set:
                    if each_rel and "has_thread" in each_rel:
                        thread_id = each_rel['has_thread'][0]
                        thread_obj = node_collection.one({'_id': ObjectId(thread_id)})
                        # print "\n\n thread_obj === ", thread_obj.name , "==="
            except:
                pass
            '''

            thread_obj = get_thread_node(node_obj._id)
            # grel_dict = get_relation_value(node_obj._id,"has_thread", True)
            # is_cursor = grel_dict.get("cursor",False)
            # if not is_cursor:
            #     thread_obj = grel_dict.get("grel_node")
            print "\n thread_obj: ", thread_obj

            user_action = request.POST.get("user_action", '')

            user_id = int(request.user.id)
            user_name = unicode(request.user.username)
            qip_gst = node_collection.one({ '_type': 'GSystemType', 'name': 'QuizItemPost'})
            qip_user_submitted_ans_AT = node_collection.one({'_type': "AttributeType", 'name': "quizitempost_user_submitted_ans"})
            qip_user_checked_ans_AT = node_collection.one({'_type': "AttributeType", 'name': "quizitempost_user_checked_ans"})
            already_ans_obj = already_submitted_ans = None
            # print "\n\n thread_obj == ", thread_obj
            if thread_obj != None:
                already_ans_obj = node_collection.find_one({'member_of': qip_gst._id,'created_by': user_id, 'prior_node': thread_obj._id})

                if already_ans_obj:
                    already_submitted_ans = get_attribute_value(already_ans_obj._id,"quizitempost_user_submitted_ans")
                    # print "\n already_submitted_ans == ", already_submitted_ans
                    # check whether user has already checked or submitted ans
                    user_ans = already_ans_obj
                else:
                    user_ans = node_collection.collection.GSystem()
                    user_ans.created_by = user_id
                    user_ans.modified_by = user_id
                    user_ans.contributors.append(user_id)
                    user_ans.member_of.append(qip_gst._id)
                    user_ans.group_set.append(group_id)
                if node_obj._id not in user_ans.prior_node:
                    user_ans.prior_node.append(node_obj._id)
                user_ans.origin = [{'thread_id': thread_obj._id, 'prior_node_id_of_thread': node_obj._id}]
                user_ans.status = u"PUBLISHED"
                user_ans.name = unicode("Answer_of:" + str(node_obj.name) + "-Answer_by:"+ str(user_name))
                user_ans.save()
                # print "\n\n user_ans== ",user_ans
                if user_id not in thread_obj.author_set:
                    thread_obj.author_set.append(user_id)
                    thread_obj.save()
                    # print "\n thread_obj.author_set",thread_obj.author_set
                if thread_obj._id not in user_ans.prior_node:
                    # add user's post/reply obj to thread obj's post_node
                    node_collection.collection.update({'_id': user_ans._id}, {'$push': {'prior_node':thread_obj._id}},upsert=False,multi=False)
                if user_ans._id not in thread_obj.post_node:
                    # add thread obj to user's post/reply prior_node
                    node_collection.collection.update({'_id': thread_obj._id}, {'$push': {'post_node':user_ans._id}},upsert=False,multi=False)
                quiz_type_val = get_attribute_value(node_obj._id,"quiz_type")
                quiz_correct_ans = get_attribute_value(node_obj._id,"correct_answer")
                # print "\n quiz_type_val: ", quiz_type_val
                # print "\n quiz_correct_ans: ", quiz_correct_ans
                # print "\n user_given_ans: ",user_given_ans
                quiz_correct_ans = (map(unicode,[re.sub(r'[\r]', '', cor_ans) for cor_ans in quiz_correct_ans]))


                # print "\n get_attribute_value--", get_attribute_value
                if user_given_ans and user_ans:
                    if quiz_type_val == "Short-Response":
                        create_gattribute(user_ans._id, qip_user_submitted_ans_AT, user_given_ans)
                    else:
                        curr_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        if user_given_ans:
                            if user_action == "check":
                                if already_ans_obj:
                                    old_checked_ans = get_attribute_value(user_ans._id,"quizitempost_user_checked_ans")
                                    if old_checked_ans != "None" and old_checked_ans != "":
                                        new_list = old_checked_ans
                                new_list.append({str(curr_datetime):user_given_ans})
                                if new_list:
                                    create_gattribute(user_ans._id, qip_user_checked_ans_AT, new_list)
                            elif user_action == "submit":
                                if already_ans_obj:
                                    old_submitted_ans = get_attribute_value(user_ans._id,"quizitempost_user_submitted_ans")
                                    if old_submitted_ans != "None" and old_submitted_ans != "" and old_submitted_ans:
                                        new_list = old_submitted_ans
                                new_list.append({str(curr_datetime):user_given_ans})
                                if new_list:
                                    create_gattribute(user_ans._id, qip_user_submitted_ans_AT, new_list)
                            user_ans.reload()
                # print "\n user_ans.attribute_set",user_ans.attribute_set
                response_dict['count'] = len(new_list)
                response_dict['success'] = True

                active_user_ids_list = [request.user.id]
                if old_submitted_ans:
                    recent_ans = old_submitted_ans[-1].values()
                    if recent_ans:
                        recent_ans = recent_ans[0]
                    is_user_given_ans_not_in_recent_submitted_ans = all(each_usr_given_ans not in recent_ans for each_usr_given_ans in user_given_ans)
                    recent_submitted_ans_was_correct = any(each_submitted_ans in quiz_correct_ans for each_submitted_ans in recent_ans)
                # print "\n recent_ans == ", recent_ans
                # print "\n user_given_ans == ", user_given_ans

                if GSTUDIO_BUDDY_LOGIN:
                    active_user_ids_list += Buddy.get_buddy_userids_list_within_datetime(request.user.id, datetime.datetime.now())
                    # removing redundancy of user ids:
                    # active_user_ids_list = dict.fromkeys(active_user_ids_list).keys()

                counter_objs_cur = Counter.get_counter_objs_cur(active_user_ids_list, group_id)

                #code to update counter collection
                # counter_obj = Counter.get_counter_obj(user_id, group_id)

                if not already_submitted_ans:
                    # This is the first time to attempt this quizitemevent
                    for userr_each_attr in user_ans.attribute_set:
                        if 'quizitempost_user_submitted_ans' in userr_each_attr:
                            if len(userr_each_attr['quizitempost_user_submitted_ans'])!=0:
                                # counter_obj.no_questions_attempted+=1
                                for each_counter_obj in counter_objs_cur:
                                    each_counter_obj['quiz']['attempted'] += 1
                                    each_counter_obj.save()
                                counter_objs_cur.rewind()
                '''
                for each_attr in node_obj.attribute_set:
                    if 'correct_answer' in each_attr:
                        quiz_correct_ans = each_attr['correct_answer']
                    if 'quiz_type' in each_attr:
                        type_of_quiz = each_attr['quiz_type']
                '''

                for each_user_ans_attr in user_ans.attribute_set:
                    if 'quizitempost_user_submitted_ans' in each_user_ans_attr:
                        if quiz_type_val=='Single-Choice':
                            if len(each_user_ans_attr['quizitempost_user_submitted_ans'])!=0:

                                for each_counter_obj in counter_objs_cur:
                                    if cmp(quiz_correct_ans,user_given_ans)==0:
                                        # counter_obj.no_correct_answers+=1
                                        if not already_submitted_ans or is_user_given_ans_not_in_recent_submitted_ans:
                                            if is_user_given_ans_not_in_recent_submitted_ans and each_counter_obj['quiz']['incorrect']:
                                                each_counter_obj['quiz']['incorrect'] -= 1
                                            if not recent_submitted_ans_was_correct:
                                                each_counter_obj['quiz']['correct'] += 1
                                                each_counter_obj['group_points'] += GSTUDIO_QUIZ_CORRECT_POINTS
                                            each_counter_obj.save()
                                    else:
                                        # each_counter_obj.no_incorrect_answers+=1
                                        if not already_submitted_ans or is_user_given_ans_not_in_recent_submitted_ans:
                                            if is_user_given_ans_not_in_recent_submitted_ans and each_counter_obj['quiz']['correct']:
                                                each_counter_obj['quiz']['correct'] -= 1
                                            if recent_submitted_ans_was_correct:
                                                each_counter_obj['quiz']['incorrect'] += 1
                                            each_counter_obj.save()
                                counter_objs_cur.rewind()

                        if quiz_type_val=='Multiple-Choice':
                            if each_user_ans_attr['quizitempost_user_submitted_ans']:
                                search = False
                                user_given_ans = [x.encode('UTF8') for x in user_given_ans]
                                quiz_correct_ans = [x.encode('UTF8') for x in quiz_correct_ans]
                                # print "\n user_given_ans : ", user_given_ans
                                # print "\n quiz_correct_ans: ", quiz_correct_ans
                                # Remove Carriage Return from Python strings ['\r'] in quiz_correct_ans
                                quiz_correct_ans_tmp = []
                                for each_option in quiz_correct_ans:
                                    each_option = each_option.replace('\r','')
                                    quiz_correct_ans_tmp.append(each_option)
                                quiz_correct_ans = quiz_correct_ans_tmp

                                for each_user_given_ans in user_given_ans:
                                    if each_user_given_ans in quiz_correct_ans:
                                        search = True

                                # print "\n search : ", search

                                '''
                                i=0
                                while i<len(user_given_ans):

                                    try:
                                        quiz_correct_ans.index(user_given_ans[i])
                                        search=True
                                        i=i+1
                                    except Exception as e1:
                                        search=False
                                        break
                                '''


                                for each_counter_obj in counter_objs_cur:
                                    if search==True:
                                        try:
                                            if not already_submitted_ans or is_user_given_ans_not_in_recent_submitted_ans:
                                                if is_user_given_ans_not_in_recent_submitted_ans and  each_counter_obj['quiz']['incorrect']:
                                                    each_counter_obj['quiz']['incorrect'] -= 1
                                                if not recent_submitted_ans_was_correct:
                                                    each_counter_obj['quiz']['correct'] += 1
                                                    # each_counter_obj.course_score+=GSTUDIO_QUIZ_CORRECT_POINTS
                                                    each_counter_obj['group_points'] += GSTUDIO_QUIZ_CORRECT_POINTS
                                                each_counter_obj.save()
                                        except Exception as rer:
                                            print "\n Error ", rer
                                    else:
                                        # each_counter_obj.no_incorrect_answers+=1
                                        if not already_submitted_ans or is_user_given_ans_not_in_recent_submitted_ans:
                                            if is_user_given_ans_not_in_recent_submitted_ans and  each_counter_obj['quiz']['correct']:
                                                each_counter_obj['quiz']['correct'] -= 1
                                            if recent_submitted_ans_was_correct:
                                                each_counter_obj['quiz']['incorrect'] += 1
                                            each_counter_obj.save()
                                counter_objs_cur.rewind()

                        if quiz_type_val=='Short-Response':
                            if len(user_given_ans)!=0:
                                # counter_obj.no_correct_answers+=1
                                for each_counter_obj in counter_objs_cur:
                                    if not already_submitted_ans:
                                        each_counter_obj['quiz']['correct'] += 1
                                        # each_counter_obj.course_score += GSTUDIO_QUIZ_CORRECT_POINTS
                                        each_counter_obj['group_points'] += GSTUDIO_QUIZ_CORRECT_POINTS
                                        each_counter_obj.save()
                #updated counter collection



            return HttpResponse(json.dumps(response_dict))


    except Exception as e:
        print "\n Something went wrong while saving quiz answer!!! ", str(e)
        return response_dict