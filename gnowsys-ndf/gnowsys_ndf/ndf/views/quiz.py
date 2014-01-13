''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
from difflib import HtmlDiff

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

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
from gnowsys_ndf.ndf.views.methods import get_drawers
from gnowsys_ndf.ndf.views.methods import get_node_common_fields


#######################################################################################################################################

db = get_database()
gst_collection = db[Node.collection_name]
gst_quiz = gst_collection.GSystemType.one({'name': GAPPS[6]})
gs_collection = db[GSystem.collection_name]
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
        
        quiz_nodes = gs_collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(app_id)]}, 'group_set': {'$all': [group_name]}})
        quiz_nodes.sort('last_update', -1)
        quiz_nodes_count = quiz_nodes.count()

        return render_to_response("ndf/quiz_list.html",
                                  {'title': title, 
                                   'quiz_nodes': quiz_nodes, 'quiz_nodes_count': quiz_nodes_count
                                  }, 
                                  context_instance=RequestContext(request)
        )

    else:
        quiz_node = gs_collection.GSystem.one({"_id": ObjectId(app_id)})
        return render_to_response('ndf/quiz_details.html', 
                                  { 'node': quiz_node,
                                    'group_name': group_name
                                  },
                                  context_instance = RequestContext(request)
        )        

def create_quiz_item(request, group_name):
    """Creates a new quiz-item.
    """
    if request.user.is_authenticated():
        gst_quiz_item = gst_collection.GSystemType.one({'name': u'QuizItem'})
        quiz_item_node = gs_collection.GSystem()

        if request.method == "POST":
            #get_node_common_fields(request, page_node, group_name, gst_page)
            #page_node.save()
            return HttpResponseRedirect(reverse('quiz', kwargs={'group_name': group_name, 'app_id': gst_quiz._id}))

        else:
            return render_to_response("ndf/quiz_item_create.html",
                                      { 'title': gst_quiz_item.name,
                                        'quiz_type_choices': QUIZ_TYPE_CHOICES,
                                        'group_name': group_name
                                      },
                                      context_instance=RequestContext(request)
            )
