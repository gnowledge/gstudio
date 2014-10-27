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
from gnowsys_ndf.ndf.views.methods import get_node_common_fields,create_grelation_list
from gnowsys_ndf.ndf.management.commands.data_entry import create_gattribute
from gnowsys_ndf.ndf.views.methods import get_node_metadata, set_all_urls


#######################################################################################################################################

db = get_database()

collection = db[Node.collection_name]
gst_quiz = collection.Node.one({'_type': u'GSystemType', 'name': GAPPS[6]})
history_manager = HistoryManager()
rcs = RCS()
app = collection.Node.one({'_type': u'GSystemType', 'name': GAPPS[6]})

#######################################################################################################################################
#                                                                            V I E W S   D E F I N E D   F O R   G A P P -- ' P A G E '
#######################################################################################################################################

def quiz(request, group_id, app_id=None):
    """Renders a list of all 'Quiz-type-GSystems' available within the database.
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    if app_id is None:
        app_ins = collection.Node.find_one({'_type':"GSystemType", "name":"Quiz"})
        if app_ins:
            app_id = str(app_ins._id)
    if gst_quiz._id == ObjectId(app_id):
        title = gst_quiz.name
        quiz_nodes = collection.Node.find({'member_of': {'$all': [ObjectId(app_id)]}, 'group_set': {'$all': [ObjectId(group_id)]}})
        quiz_nodes.sort('last_update', -1)
        quiz_nodes_count = quiz_nodes.count()
        gst_quiz_item_id = collection.Node.one({'_type': 'GSystemType', 'name': u'QuizItem'})._id
        quiz_item_nodes = collection.Node.find({'member_of': {'$all': [gst_quiz_item_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})
        quiz_item_nodes.sort('last_update', -1)
        quiz_item_nodes_count = quiz_item_nodes.count()
	#quiz_node.get_neighbourhood(quiz_node.member_of)
        return render_to_response("ndf/quiz_list.html",
                                  {'title': title, 
                                   'appId':app._id,
                                   'quiz_nodes': quiz_nodes, 'quiz_nodes_count': quiz_nodes_count,
                                   'quiz_item_nodes': quiz_item_nodes, 'quiz_item_nodes_count': quiz_item_nodes_count,
                                   'groupid':group_id,
                                   'group_id':group_id
                                  }, 
                                  context_instance=RequestContext(request)
        )

    else:
        node = collection.Node.one({"_id": ObjectId(app_id)})

        title = gst_quiz.name

        template_name = ""
        context_variables = { 'node': node,
                              'title': title,
                              'appId':app._id,
                              'group_id': group_id,
                              'groupid':group_id
                          }
        node.get_neighbourhood(node.member_of)
        if gst_quiz._id in node.member_of:
	    
            template_name = "ndf/quiz_details.html"

        else:
            template_name = "ndf/quiz_item_details.html"
	
        return render_to_response(template_name, 
                                  context_variables,                          
                                  context_instance = RequestContext(request)
        )        


@login_required
def create_edit_quiz_item(request, group_id, node_id=None):
    """Creates/Modifies details about the given quiz-item.
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    gst_quiz_item = collection.Node.one({'_type': u'GSystemType', 'name': u'QuizItem'})

    context_variables = { 'title': gst_quiz_item.name,
                          'quiz_type_choices': QUIZ_TYPE_CHOICES,
                          'group_id': group_id,
                          'groupid': group_id
                      }

    node = None
    quiz_node = None
    quiz_item_node = None

    if node_id:
        node = collection.Node.one({'_id': ObjectId(node_id)})

        if gst_quiz._id in node.member_of:
            # Add question from a given Quiz category's context
            quiz_node = node
            quiz_item_node = collection.GSystem()

        else:
            # Edit a question
            quiz_item_node = node
    else:
        # Add miscellaneous question
        quiz_item_node = collection.GSystem()


    if request.method == "POST":
        usrid = int(request.user.id)
        usrname = unicode(request.user.username)

        if not quiz_item_node.has_key('_id'):
            quiz_item_node.created_by = usrid
            quiz_item_node.member_of.append(gst_quiz_item._id)
            ###################### ADDED ON 14th JULY.IT'S DONE
	    quiz_item_node.url = set_all_urls(quiz_item_node.member_of)
	    quiz_item_node.access_policy = u"PUBLIC"	
        quiz_item_node.modified_by = usrid

        if usrid not in quiz_item_node.contributors:
            quiz_item_node.contributors.append(usrid)

        group_object=collection.Group.one({'_id':ObjectId(group_id)})
        if group_object._id not in quiz_item_node.group_set:
            quiz_item_node.group_set.append(group_object._id)
        user_group_object=collection.Group.one({'$and':[{'_type':u'Group'},{'name':usrname}]})
        if user_group_object:
            if user_group_object._id not in quiz_item_node.group_set:
                quiz_item_node.group_set.append(user_group_object._id)

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
        if tags:
            quiz_item_node.tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]
        
        quiz_item_node.save()

        if quiz_node:
            quiz_node.collection_set.append(quiz_item_node._id)
            quiz_node.save()
	
        assesses_list = request.POST.get('assesses_list','') 	
	if assesses_list !='':
			assesses_list=assesses_list.split(",")
	create_grelation_list(quiz_item_node._id,"assesses",assesses_list)

        return HttpResponseRedirect(reverse('quiz', kwargs={'group_id': group_id, 'appId':app._id,'app_id': quiz_item_node._id}))
        
    else:
        if node_id:
            context_variables['node'] = quiz_item_node
            context_variables['groupid'] = group_id
            context_variables['group_id'] = group_id
            content_variable['appId']=app._id
            
        return render_to_response("ndf/quiz_item_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
                              )

@login_required
def create_edit_quiz(request, group_id, node_id=None):
    """Creates/Edits quiz category.
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    context_variables = { 'title': gst_quiz.name,
                          'group_id': group_id,
                          'groupid': group_id
                      }

    if node_id:
        quiz_node = collection.Node.one({'_type': u'GSystem', '_id': ObjectId(node_id)})
    else:
        quiz_node = collection.GSystem()

    if request.method == "POST":

        # get_node_common_fields(request, quiz_node, group_id, gst_quiz)
        quiz_node.save(is_changed=get_node_common_fields(request, quiz_node, group_id, gst_quiz))
	get_node_metadata(request,quiz_node,gst_quiz)
	
       
	
	#if teaches is required
	teaches_list = request.POST.get('teaches_list','') # get the teaches list 
	if teaches_list !='':
			teaches_list=teaches_list.split(",")
	create_grelation_list(quiz_node._id,"teaches",teaches_list)
        
	assesses_list = request.POST.get('assesses_list','') # get the assesses list 	
	if assesses_list !='':
			assesses_list=assesses_list.split(",")
	create_grelation_list(quiz_node._id,"assesses",assesses_list)

	
        return HttpResponseRedirect(reverse('quiz_details', kwargs={'group_id': group_id,'appId':app._id, 'app_id': quiz_node._id}))
	
    else:
        if node_id:
            context_variables['node'] = quiz_node
            context_variables['groupid'] = group_id
            context_variables['group_id']=group_id
            content_variables['appId']=app._id
        quiz_node.get_neighbourhood(quiz_node.member_of)    
        return render_to_response("ndf/quiz_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
        )
        

