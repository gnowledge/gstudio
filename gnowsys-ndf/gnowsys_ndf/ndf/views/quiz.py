''' -- imports from python libraries -- '''
# import os -- Keep such imports here

''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
# from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
from django.template.defaultfilters import slugify

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import GSystemType, GSystem
from gnowsys_ndf.ndf.models import QUIZ_TYPE_CHOICES
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.views.methods import get_node_common_fields,create_grelation_list,get_execution_time
from gnowsys_ndf.ndf.management.commands.data_entry import create_gattribute
from gnowsys_ndf.ndf.views.methods import get_node_metadata, set_all_urls, get_group_name_id


#######################################################################################################################################

gst_quiz = node_collection.one({'_type': u'GSystemType', 'name': "Quiz"})
history_manager = HistoryManager()
rcs = RCS()
app = gst_quiz

#######################################################################################################################################
#                                                                            V I E W S   D E F I N E D   F O R   G A P P -- ' P A G E '
#######################################################################################################################################
@get_execution_time
def quiz(request, group_id):
    """Renders a list of all 'Quiz-type-GSystems' available within the database.
    """
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    title = gst_quiz.name
    quiz_nodes = node_collection.find({'member_of': gst_quiz._id, 'group_set': ObjectId(group_id)}).sort('last_update', -1)
    quiz_nodes_count = quiz_nodes.count()
    # gst_quiz_item_id = node_collection.one({'_type': 'GSystemType', 'name': u'QuizItem'})._id
    # quiz_item_nodes = node_collection.find({'member_of': {'$all': [gst_quiz_item_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})
    # quiz_item_nodes.sort('last_update', -1)
    # quiz_item_nodes_count = quiz_item_nodes.count()
    # quiz_node.get_neighbourhood(quiz_node.member_of)
    return render_to_response("ndf/quiz.html",
                              {'title': title, 
                               'quiz_nodes': quiz_nodes, 'quiz_nodes_count': quiz_nodes_count,
                               # 'quiz_item_nodes': quiz_item_nodes, 'quiz_item_nodes_count': quiz_item_nodes_count,
                               'groupid':group_id,
                               'group_id':group_id
                              }, 
                              context_instance=RequestContext(request)
    )

@login_required
@get_execution_time
def create_edit_quiz_item(request, group_id, quiz_node_id, node_id=None):
    """Creates/Modifies details about the given quiz-item.
    """
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    group_object = node_collection.one({'_id': ObjectId(group_id)})

    node = None
    quiz_node = None
    quiz_item_node = None

    gst_quiz_item = node_collection.one({'_type': u'GSystemType', 'name': u'QuizItem'})
    quiz_node = node_collection.one({'_id': ObjectId(quiz_node_id)})
    if node_id:
        quiz_item_node = node_collection.one({'_id': ObjectId(node_id)})

    context_variables = { 'title': gst_quiz_item.name,
                          'quiz_type_choices': QUIZ_TYPE_CHOICES,
                          'group_id': group_id,
                          'groupid': group_id
                        }

    if request.method == "POST":
        usrid = int(request.user.id)
        usrname = unicode(request.user.username)

        if node_id:
            quiz_item_node = node_collection.one({'_id': ObjectId(node_id)})
        else:
            # Add miscellaneous question
            quiz_item_node = node_collection.collection.GSystem()
        quiz_item_node.save(is_changed=get_node_common_fields(request, quiz_item_node, group_id, gst_quiz_item),groupid=group_id)

        quiz_type = request.POST.get('quiz_type_val','')
        quiz_item_node['quiz_type'] = unicode(quiz_type)

        # question = request.POST.get('question','')
        # quiz_item_node.content_org = unicode(question)
        # name = "quiz-item-" + (question.split()[3] if len(question.split()) > 4 else question.split()[0])   # Extracting the third word of the question if present, otherwise first word 
        # Required to link temporary files with the current user who is modifying this document
        # usrname = request.user.username
        # filename = slugify(name) + "-" + usrname + "-"
        # quiz_item_node.content = org2html(question, file_prefix=filename)

        # If "quiz_type" is either 'Single-Choice' or 'Multiple-Choice', then only extract options
        options = []
        if quiz_type != QUIZ_TYPE_CHOICES[0]:
            no_of_options = int(request.POST.get('no_of_options',''))
            quiz_item_node['options'] = []
            # print "\n\n no_of_options",no_of_options
            i = 1
            while i <= no_of_options:
                options.append(request.POST.get("option" if i == 1 else "option_"+str(i)))
                i = i + 1
            quiz_item_node['options'] = options

        # Extracting correct-answer, depending upon 'Multiple-Choice' / 'Single-Choice' 
        qt_initial = quiz_type[:quiz_type.find("-")].lower()
        quiz_item_node['correct_answer'] = []
        if quiz_type == QUIZ_TYPE_CHOICES[2]:
            correct_answer = request.POST.getlist('correct_answer_' + qt_initial)
            quiz_item_node['correct_answer'] = correct_answer
        else:
            correct_answer = request.POST.get('correct_answer_' + qt_initial)
            quiz_item_node['correct_answer'].append(correct_answer)

        tags = request.POST.get('tags','')
        if tags:
            quiz_item_node.tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]
        
        quiz_item_node.save(groupid=group_id)

        if quiz_node:
            quiz_node.collection_set.append(quiz_item_node._id)
            quiz_node.save(groupid=group_id)
	
        # assesses_list = request.POST.get('assesses_list','') 	
        # if assesses_list !='':
        #     assesses_list=assesses_list.split(",")
        # create_grelation_list(quiz_item_node._id,"assesses",assesses_list)
        return HttpResponseRedirect(reverse('quiz_details', kwargs={'group_id': group_id, 'node_id':quiz_node_id}))
        
    else:
        if node_id:
            context_variables['node'] = quiz_item_node
            context_variables['groupid'] = group_id
            context_variables['group_id'] = group_id
        context_variables['quiz_node']=quiz_node
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
    quiz_item_nodes = node_collection.find({'_id': {'$in': quiz_node.collection_set}, 'member_of': gst_quiz_item._id }).sort('last_update', -1)
    quiz_node.get_neighbourhood(quiz_node.member_of)

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

