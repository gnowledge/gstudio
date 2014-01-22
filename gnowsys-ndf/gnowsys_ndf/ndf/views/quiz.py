''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
from difflib import HtmlDiff

''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import Node, GSystemType, GSystem
from gnowsys_ndf.ndf.models import QUIZ_TYPE_CHOICES
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.views.methods import get_node_common_fields


#######################################################################################################################################

db = get_database()

collection = db[Node.collection_name]
gst_quiz = collection.Node.one({'_type': u'GSystemType', 'name': GAPPS[6]})
history_manager = HistoryManager()
rcs = RCS()

#######################################################################################################################################
#                                                                            V I E W S   D E F I N E D   F O R   G A P P -- ' P A G E '
#######################################################################################################################################

def quiz(request, group_name, app_id):
    """Renders a list of all 'Quiz-type-GSystems' available within the database.
    """
    if gst_quiz._id == ObjectId(app_id):
        title = gst_quiz.name

        quiz_nodes = collection.Node.find({'gsystem_type': {'$all': [ObjectId(app_id)]}, 'group_set': {'$all': [group_name]}})
        quiz_nodes.sort('last_update', -1)
        quiz_nodes_count = quiz_nodes.count()

        gst_quiz_item_id = collection.Node.one({'_type': u'GSystemType', 'name': u'QuizItem'})._id
        quiz_item_nodes = collection.Node.find({'gsystem_type': {'$all': [gst_quiz_item_id]}, 'group_set': {'$all': [group_name]}})
        quiz_item_nodes.sort('last_update', -1)
        quiz_item_nodes_count = quiz_item_nodes.count()

        return render_to_response("ndf/quiz_list.html",
                                  {'title': title, 
                                   'quiz_nodes': quiz_nodes, 'quiz_nodes_count': quiz_nodes_count,
                                   'quiz_item_nodes': quiz_item_nodes, 'quiz_item_nodes_count': quiz_item_nodes_count
                                  }, 
                                  context_instance=RequestContext(request)
        )

    else:
        quiz_node = collection.Node.one({"_id": ObjectId(app_id)})
        return render_to_response('ndf/quiz_details.html', 
                                  { 'node': quiz_node,
                                    'group_name': group_name
                                  },
                                  context_instance = RequestContext(request)
        )        


@login_required
def create_edit_quiz_item(request, group_name, node_id=None):
    """Displays/Modifies details about the given quiz-item.
    """

    gst_quiz_item = collection.Node.one({'_type': u'GSystemType', 'name': u'QuizItem'})

    context_variables = { 'title': gst_quiz_item.name,
                          'quiz_type_choices': QUIZ_TYPE_CHOICES,
                          'group_name': group_name
                      }

    if node_id:
        quiz_item_node = collection.Node.one({'_type': u'GSystem', '_id': ObjectId(node_id)})
    else:
        quiz_item_node = collection.GSystem()

    if request.method == "POST":
        usrid = int(request.user.id)

        if not quiz_item_node.has_key('_id'):
            quiz_item_node.created_by = usrid
            quiz_item_node.member_of.append(gst_quiz_item.name)
            quiz_item_node.gsystem_type.append(gst_quiz_item._id)

        if usrid not in quiz_item_node.modified_by:
            quiz_item_node.modified_by.append(usrid)

        if group_name not in quiz_item_node.group_set:
            quiz_item_node.group_set.append(group_name)

        quiz_type = request.POST.get('quiz_type_val')
        quiz_item_node['quiz_type'] = unicode(quiz_type)

        question = request.POST.get('question')
        quiz_item_node.content_org = unicode(question)
            
        name = "quiz-item-" + (question.split()[3] if len(question.split()) > 4 else question.split()[0])   # Extracting the third word of the question if present, otherwise first word 

        quiz_item_node.name = name if type(name) == unicode else unicode(name) 

        # Required to link temporary files with the current user who is modifying this document
        usrname = request.user.username
        filename = slugify(name) + "-" + usrname + "-"
        quiz_item_node.content = org2html(question, file_prefix=filename)

        # If "quiz_type" is either 'Single-Choice' or 'Multiple-Choice', then only extract options
        options = []
        if quiz_type != QUIZ_TYPE_CHOICES[0]:
            no_of_options = int(request.POST.get('no_of_options'))
            quiz_item_node['options'] = []

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

        tags = request.POST.get('tags')
        quiz_item_node.tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]
        
        quiz_item_node.save()
        
        return HttpResponseRedirect(reverse('quiz', kwargs={'group_name': group_name, 'app_id': gst_quiz._id}))
        
    else:
        if node_id:
            context_variables['node'] = quiz_item_node
            
        return render_to_response("ndf/quiz_item_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
                              )

@login_required
def create_edit_quiz(request, group_name, node_id=None):
    """Creates/Edits quiz category.
    """
    context_variables = { 'title': gst_quiz.name,
                          'group_name': group_name
                      }

    if node_id:
        quiz_node = collection.Node.one({'_type': u'GSystem', '_id': ObjectId(node_id)})
    else:
        quiz_node = collection.GSystem()

    if request.method == "POST":
        get_node_common_fields(request, quiz_node, group_name, gst_quiz)
        quiz_node.save()
        
        return HttpResponseRedirect(reverse('quiz_details', kwargs={'group_name': group_name, 'app_id': quiz_node._id}))

    else:
        if node_id:
            context_variables['node'] = quiz_node
            
        return render_to_response("ndf/quiz_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
        )
        

