
''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import datetime
import csv
import time
import ast
import json
import math
import multiprocessing

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.http import Http404
from django.core.paginator import Paginator
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from mongokit import paginator
from django.contrib.sites.models import Site
from django.core.cache import cache

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS,GSTUDIO_SUPPORTED_JHAPPS
from gnowsys_ndf.settings import STATIC_ROOT, STATIC_URL
from gnowsys_ndf.ndf.models import NodeJSONEncoder
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.views.gcourse import *
from gnowsys_ndf.ndf.views.translation import get_lang_node
from gnowsys_ndf.ndf.views.methods import check_existing_group, get_drawers, get_course_completed_ids,create_thread_for_node, delete_gattribute
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, get_node_metadata, create_grelation,create_gattribute
from gnowsys_ndf.ndf.views.methods import create_task,parse_template_data,get_execution_time,get_group_name_id, dig_nodes_field
from gnowsys_ndf.ndf.views.methods import get_widget_built_up_data, parse_template_data, get_prior_node_hierarchy, create_clone
from gnowsys_ndf.ndf.views.methods import create_grelation, create_gattribute, create_task, node_thread_access, get_course_units_tree, delete_node
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_profile_pic, edit_drawer_widget, get_contents, get_sg_member_of, get_attribute_value, check_is_gstaff
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME
# from gnowsys_ndf.mobwrite.models import ViewObj
from gnowsys_ndf.notification import models as notification
from gnowsys_ndf.ndf.views.asset import *
from gnowsys_ndf.ndf.views.trash import * 

theme_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Theme'})
topic_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})
theme_item_GST = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item'})
GST_FILE = node_collection.one({'_type':'GSystemType', 'name': 'File'})
GST_PAGE = node_collection.one({'_type':'GSystemType', 'name': 'Page'})
# This function is used to check (while creating a new group) group exists or not
# This is called in the lost focus event of the group_name text box, to check the existance of group, in order to avoid duplication of group names.


@get_execution_time
class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        else:
            return obj


def get_node_json_from_id(request, group_id, node_id=None):
    if not node_id:
        node_id = request.GET.get('node_id')
    node_obj = Node.get_node_by_id(node_id)

    if node_obj:
      if "QuizItem" in node_obj.member_of_names_list:
        from gnowsys_ndf.ndf.views.quiz import render_quiz_player
        return render_quiz_player(request, group_id, node_obj)
      trans_node = get_lang_node(node_obj._id,request.LANGUAGE_CODE)
      if trans_node:
        return HttpResponse(json.dumps(trans_node, cls=NodeJSONEncoder))
      else:
        return HttpResponse(json.dumps(node_obj, cls=NodeJSONEncoder))
    else:
      return HttpResponse(0)


def save_node(request, group_id, node_id=None):
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    if not node_id:
        node_id = request.POST.get('node_id')
    type_of_gst_name = request.POST.get('type_of_gst_name', '')
    member_of_gst_name = request.POST.get('member_of_gst_name', '')
    replicate_resource = request.POST.get('replicate_resource', 'False')
    node_obj = Node.get_node_by_id(node_id)
    type_of_gst_name, type_of_gst_id = GSystemType.get_gst_name_id(type_of_gst_name)
    member_of_gst_name, member_of_gst_id = GSystemType.get_gst_name_id(member_of_gst_name)
    if node_obj:
        if eval(replicate_resource):
            new_node_obj = create_clone(request.user.id, node_obj, group_id)
            new_node_obj.type_of = [type_of_gst_id]
            new_node_obj.member_of = [member_of_gst_id]
            node_obj = new_node_obj
            new_node_obj.origin = [{'template_from': node_obj._id}]
        else:
            node_obj.fill_gstystem_values(request=request)
            node_obj.member_of = [member_of_gst_id]
        node_obj.save(group_id=group_id)
        return HttpResponse(json.dumps(node_obj, cls=NodeJSONEncoder))
    else:
        return HttpResponse(0)


@login_required
def remove_from_nodelist(request, group_id):
    parent_node_id = request.POST.get('parent_node_id', None)
    child_node_id = request.POST.get('child_node_id', None)
    node_field = request.POST.get('node_field', None)
    result = 0

    if (parent_node_id and child_node_id) and (node_field in Node.structure):
        node_obj = Node.get_node_by_id(parent_node_id)
        try:
            node_obj[node_field].pop(node_obj[node_field].index(ObjectId(child_node_id)))
            node_obj.save(group_id=group_id)
        except Exception, e:
            print e
        result = 1

    return HttpResponse(result)


@login_required
def ajax_delete_node(request, group_id):
    node_to_delete = request.POST.get('node_to_delete', None)
    deletion_type = eval(request.POST.get('deletion_type', 0))
    right_subject = eval(request.POST.get('right_subject', None))
    if right_subject in [0, 1]:
        all_grels = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(node_to_delete)})
        for each_grel in all_grels:
            delete_node(node_id=each_grel['right_subject'], deletion_type=right_subject)
    return HttpResponse(json.dumps(delete_node(node_id=node_to_delete, deletion_type=deletion_type)))


def checkgroup(request, group_name):
    titl = request.GET.get("gname", "")
    retfl = check_existing_group(titl)
    if retfl:
        return HttpResponse("success")
    else:
        return HttpResponse("failure")

@get_execution_time
def terms_list(request, group_id):
    if request.is_ajax() and request.method == "POST":
        # page number which have clicked on pagination
        page_no = request.POST.get("page_no", '')
        terms = []
        gapp_GST = node_collection.one({'_type': 'MetaType', 'name': 'GAPP'})
        term_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Term', 'member_of':ObjectId(gapp_GST._id) })

        # To list all term instances
        terms_list = node_collection.find({
            '_type': 'GSystem', 'member_of': ObjectId(term_GST._id),
            'group_set': ObjectId(group_id)
        }).sort('name', 1)

        paged_terms = paginator.Paginator(terms_list, page_no, 25)

        # Since "paged_terms" returns dict ,we append the dict items in a list to forwarded into template
        for each in paged_terms.items:
            terms.append(each)

        return render_to_response(
            'ndf/terms_list.html',
            {
                'group_id': group_id, 'groupid': group_id, "paged_terms": terms,
                'page_info': paged_terms
            },
            context_instance=RequestContext(request)
        )


# This ajax view creates the page collection of selected nodes from list view
@get_execution_time
def collection_create(request, group_id):
  '''
  This ajax view creates the page collection of selected nodes from list view
  '''
  existing_collection = request.POST.get("existing_collection")
  # print "\n\n\n here",existing_collection
  coll_redir = request.POST.get('coll_redir',"")
  if existing_collection == "True":
    Collections = request.POST.getlist("collection[]", '')
    cur_collection_id = request.POST.get("cur_collection_id")
    obj = node_collection.one({'_id': ObjectId(cur_collection_id)})
    # print "\n\n\n\n obj",obj
    for each in Collections:
      node_collection.collection.update({'_id': ObjectId(cur_collection_id) }, {'$push': {'collection_set': ObjectId(each) }}, upsert=False, multi=False)
      return HttpResponse("success")

  elif request.is_ajax() and request.method == "POST":
    Collections = request.POST.getlist("collection[]", '')
    # name is comming from post request ajax


    gst_page = node_collection.one({'_type': "GSystemType", 'name': "Page"})
    page_node = node_collection.collection.GSystem()
    page_node.save(is_changed=get_node_common_fields(request, page_node, group_id, gst_page))
    discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
    create_gattribute(page_node._id, discussion_enable_at, True)
    return_status = create_thread_for_node(request,group_id, page_node)
    group_object = node_collection.one({'_id': ObjectId(group_id)})

    # if group_object.edit_policy == "EDITABLE_MODERATED":
    #                 # print "\n\n\n\ninside editable moderated block"
    #                 page_node.group_set = get_moderator_group_set(page_node.group_set, group_object._id)
    #                 # print "\n\n\npage_node._id",page_node._id
    #                 page_node.status = u'MODERATION'
    #                 # print "\n\n\n page_node.status",page_node.status

    if coll_redir == "raw-material":
      page_node.tags.append(u'raw@material')
    page_node.save()
    for each in Collections:
      node_collection.collection.update({'_id': page_node._id}, {'$push': {'collection_set': ObjectId(each) }}, upsert=False, multi=False)

    # print page_node,"\n"
    return HttpResponse("success")



# This ajax view renders the output as "node view" by clicking on collections
@get_execution_time
def collection_nav(request, group_id):
  '''
  This ajax function retunrs the node on main template, when clicked on collection hierarchy
  '''
  if request.is_ajax() and request.method == "GET":
    curr_node_obj = None
    node_id = request.GET.get("node_id", '')
    curr_node_id = request.GET.get("curr_node", '')
    node_type = request.GET.get("nod_type", '')
    template = "ndf/node_ajax_view.html"
    breadcrumbs_list = []
    curr_node_obj = node_collection.one({'_id': ObjectId(curr_node_id)})
    if node_type == "Topic":
      theme_item_GST = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item'})
      for e in curr_node_obj.prior_node:
        prior = node_collection.one({'_id': ObjectId(e)})
        if curr_node_obj._id in prior.collection_set and theme_item_GST._id in prior.member_of:
          breadcrumbs_list.append((str(prior._id), prior.name))

    topic = ""

    node_obj = node_collection.one({'_id': ObjectId(node_id)})
    group_obj = node_collection.one({'_id': ObjectId(group_id)})
    sg_type = None
    list_of_sg_member_of = get_sg_member_of(group_id)
    thread_node = None
    allow_to_comment = None

    if "CourseEventGroup" in group_obj.member_of_names_list or "ProgramEventGroup" in list_of_sg_member_of:
      node_obj.get_neighbourhood(node_obj.member_of)

      template = "ndf/res_node_ajax_view.html"
      if "ProgramEventGroup" in list_of_sg_member_of:
        sg_type = "ProgramEventGroup"
      elif "CourseEventGroup" in list_of_sg_member_of:
        sg_type = "CourseEventGroup"
      if "QuizItemEvent" in node_obj.member_of_names_list:
        template = "ndf/quiz_player.html"

      thread_node, allow_to_comment = node_thread_access(group_obj._id, node_obj)


    nav_list = request.GET.getlist("nav[]", '')
    n_list = request.GET.get("nav", '')

    # This "n_list" is for manipulating breadcrumbs events and its navigation
    if n_list:
      # Convert the incomming listfrom template into python list
      n_list = n_list.replace("&#39;", "'")
      n_list = ast.literal_eval(n_list)

      # For removing elements from breadcrumbs list to manipulate basd on which node is clicked
      for e in reversed(n_list):
        if e != unicode(node_obj._id):
          n_list.remove(e)
        else:
          break

      nav_list = n_list

    # Firstly original node should go into breadcrumbs list
    breadcrumbs_list.append( (str(curr_node_obj._id), curr_node_obj.name) )

    if nav_list:
      # create beadcrumbs list from navigation list sent from template.
      for each in nav_list:
        obj = node_collection.one({'_id': ObjectId(each) })
        breadcrumbs_list.append( (str(obj._id), obj.name) )

      b_list = []
      for each in breadcrumbs_list:
        b_list.append(each[0])

      if str(node_obj._id) not in b_list:
        # Add the tuple if clicked node is not there in breadcrumbs list
        breadcrumbs_list.append( (str(node_obj._id), node_obj.name) )
      else:
        # To remove breadcrumbs untill clicked node have not reached(Removal starts in reverse order)
        for e in reversed(breadcrumbs_list):
          if node_id in e:
            break
          else:
            breadcrumbs_list.remove(e)
    # print "breadcrumbs_list: ",breadcrumbs_list,"\n"
    node_obj.get_neighbourhood(node_obj.member_of)
    thread_node = None
    allow_to_comment = None
    thread_node, allow_to_comment = node_thread_access(group_id, node_obj)
    return render_to_response(template,
                                { 'node': node_obj,
                                  'original_node':curr_node_obj,
                                  'group_id': group_id,
                                  'groupid':group_id,
                                  'breadcrumbs_list':breadcrumbs_list,
                                  'sg_type': sg_type,
                                  'allow_to_comment': allow_to_comment,
                                  'thread_node': thread_node,
                                  'app_id': node_id, 'topic':topic, 'nav_list':nav_list,
                                  'allow_to_comment':allow_to_comment,'thread_node': thread_node
                                },
                                context_instance = RequestContext(request)
    )


# This view handles the collection list of resource and its breadcrumbs
@get_execution_time
def collection_view(request, group_id):
  '''
  This ajax function returns breadcrumbs_list for clicked node in collection hierarchy
  '''
  if request.is_ajax() and request.method == "POST":
    node_id = request.POST.get("node_id", '')
    # breadcrumbs_list = request.POST.get("breadcrumbs_list", '')

    node_obj = node_collection.one({'_id': ObjectId(node_id)})
    # breadcrumbs_list = breadcrumbs_list.replace("&#39;","'")
    # breadcrumbs_list = ast.literal_eval(breadcrumbs_list)

    # b_list = []
    # for each in breadcrumbs_list:
    #   b_list.append(each[0])

    # if str(node_obj._id) not in b_list:
    #   # Add the tuple if clicked node is not there in breadcrumbs list
    #   breadcrumbs_list.append( (str(node_obj._id), node_obj.name) )
    # else:
    #   # To remove breadcrumbs untill clicked node have not reached(Removal starts in reverse order)
    #   for e in reversed(breadcrumbs_list):
    #     if node_id in e:
    #       break
    #     else:
    #       breadcrumbs_list.remove(e)

    return render_to_response('ndf/collection_ajax_view.html',
                              {
                                'node': node_obj, 'group_id': group_id, 'groupid': group_id
                              },context_instance=RequestContext(request)
    )


@login_required
@get_execution_time
def shelf(request, group_id):
    if request.is_ajax() and request.method == "POST":
      shelf = request.POST.get("shelf_name", '')
      shelf_add = request.POST.get("shelf_add", '')
      shelf_remove = request.POST.get("shelf_remove", '')
      shelf_item_remove = request.POST.get("shelf_item_remove", '')

      shelf_available = ""
      shelf_item_available = ""

      shelf_gst = node_collection.one({'_type': u'GSystemType', 'name': u'Shelf'})

      auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
      has_shelf_RT = node_collection.one({'_type': u'RelationType', 'name': u'has_shelf'})

      if shelf:
        shelf_gs = node_collection.one({'name': unicode(shelf), 'member_of': [ObjectId(shelf_gst._id)] })
        if shelf_gs is None:
          shelf_gs = node_collection.collection.GSystem()
          shelf_gs.name = unicode(shelf)
          shelf_gs.created_by = int(request.user.id)
          shelf_gs.member_of.append(shelf_gst._id)
          shelf_gs.save(groupid=group_id)

          shelf_R = triple_collection.collection.GRelation()
          shelf_R.subject = ObjectId(auth._id)
          shelf_R.relation_type = has_shelf_RT._id
          shelf_R.right_subject = ObjectId(shelf_gs._id)
          shelf_R.save(groupid=group_id)
        else:
          if shelf_add:
            shelf_item = ObjectId(shelf_add)

            if shelf_item in shelf_gs.collection_set:
              shelf_Item = node_collection.one({'_id': ObjectId(shelf_item)}).name
              shelf_item_available = shelf_Item
              return HttpResponse("failure")

            else:
              node_collection.collection.update({'_id': shelf_gs._id}, {'$push': {'collection_set': ObjectId(shelf_item) }}, upsert=False, multi=False)
              shelf_gs.reload()

          elif shelf_item_remove:
            shelf_item = node_collection.one({'name': unicode(shelf_item_remove)})._id
            node_collection.collection.update({'_id': shelf_gs._id}, {'$pull': {'collection_set': ObjectId(shelf_item) }}, upsert=False, multi=False)
            shelf_gs.reload()

          else:
            shelf_available = shelf

      elif shelf_remove:
        shelf_gs = node_collection.one({'name': unicode(shelf_remove), 'member_of': [ObjectId(shelf_gst._id)] })
        shelf_rel = triple_collection.one({'_type': 'GRelation', 'subject': ObjectId(auth._id),'right_subject': ObjectId(shelf_gs._id) })

        shelf_rel.delete()
        shelf_gs.delete()

      else:
        shelf_gs = None

      shelves = []
      shelf_list = {}

      if auth:
        shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': has_shelf_RT._id})

        if shelf:
          for each in shelf:
            shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)})
            shelves.append(shelf_name)

            shelf_list[shelf_name.name] = []
            for ID in shelf_name.collection_set:
              shelf_item = node_collection.one({'_id': ObjectId(ID)})
              shelf_list[shelf_name.name].append(shelf_item.name)

        else:
          shelves = []

      return render_to_response('ndf/shelf.html',
                                  { 'shelf_obj': shelf_gs,'shelf_list': shelf_list,'shelves': shelves,
                                    'groupid':group_id
                                  },
                                  context_instance = RequestContext(request)
      )

@get_execution_time
def drawer_widget(request, group_id):
    drawer = None
    drawers = None
    drawer1 = None
    drawer2 = None
    dict_drawer = {}
    dict1 = {}
    dict2 = []
    nlist = []
    node = None

    node_id = request.POST.get("node_id", '')
    field = request.POST.get("field", '')
    app = request.POST.get("app", '')
    page_no = request.POST.get("page_no", '')

    if node_id:
      node = node_collection.one({'_id': ObjectId(node_id)})
      if field == "prior_node":
        app = None
        nlist = node.prior_node
        drawer, paged_resources = get_drawers(group_id, node._id, nlist, page_no, app)

      elif field == "teaches":
        app = None
        relationtype = node_collection.one({"_type": "RelationType", "name": "teaches"})
        list_grelations = triple_collection.find({"_type": "GRelation", "subject": node._id, "relation_type": relationtype._id})
        for relation in list_grelations:
          nlist.append(ObjectId(relation.right_subject))

        drawer, paged_resources = get_drawers(group_id, node._id, nlist, page_no, app)

      elif field == "assesses":
        app = field
        relationtype = node_collection.one({"_type": "RelationType", "name": "assesses"})
        list_grelations = triple_collection.find({"_type": "GRelation", "subject": node._id, "relation_type": relationtype._id})
        for relation in list_grelations:
          nlist.append(ObjectId(relation.right_subject))

        drawer, paged_resources = get_drawers(group_id, node._id, nlist, page_no, app)

      elif field == "collection":
        if app == "Quiz":
          app = "QuizItem"
        elif app == "Theme":
          app = "Theme"
        elif app == "Theme Item":
          app == "theme_item"
        elif app == "Topic":
          app = "Topic"
        elif app == "Module":
          app = "Module"
        else:
          app = None

        nlist = node.collection_set
        drawer, paged_resources = get_drawers(group_id, node._id, nlist, page_no, app)

    else:
      if field == "collection" and app == "Quiz":
        app = "QuizItem"
      elif field == "collection" and app == "Theme":
        app = "Theme"
      elif field == "collection" and app == "Theme Item":
        app = "theme_item"
      elif field == "collection" and app == "Course":
        app = "Module"
      else:
        app = None

      nlist = []
      drawer, paged_resources = get_drawers(group_id, None, nlist, page_no, app)

    drawers = drawer
    if not node_id:
      drawer1 = drawers

    else:
      drawer1 = drawers['1']
      drawer2 = drawers['2']

    return render_to_response('ndf/drawer_widget.html',
                              { 'widget_for': field,'drawer1': drawer1, 'drawer2': drawer2,'node_id': node_id,
                                'group_id': group_id,'groupid': group_id,"page_info": paged_resources
                              },
                              context_instance = RequestContext(request)
    )


@get_execution_time
def select_drawer(request, group_id):
    if request.is_ajax() and request.method == "POST":
        drawer = None
        drawers = None
        drawer1 = None
        drawer2 = None
        selection_flag = True
        node = None
        dict_drawer = {}
        dict1 = {}
        dict2 = []
        nlist=[]
        check = ""
        checked = ""
        relationtype = ""

        node_id = request.POST.get("node_id", '')
        page_no = request.POST.get("page_no", '')
        field = request.POST.get("field", '')
        checked = request.POST.get("homo_collection", '')
        node_type = request.POST.get("node_type", '')

        if node_id:
          node_id = ObjectId(node_id)
          node = node_collection.one({'_id': ObjectId(node_id)})
          if node_type:
            if len(node.member_of) > 1:
              n_type = node_collection.one({'_id': ObjectId(node.member_of[1])})
            else:
              n_type = node_collection.one({'_id': ObjectId(node.member_of[0])})
            checked = n_type.name

        if checked:
          if checked == "QuizObj" :
            quiz = node_collection.one({'_type': 'GSystemType', 'name': "Quiz" })
            quizitem = node_collection.one({'_type': 'GSystemType', 'name': "QuizItem"})

          elif checked == "Pandora Video":
            check = node_collection.one({'_type': 'GSystemType', 'name': 'Pandora_video'})

          else:
            check = node_collection.one({'_type': 'GSystemType', 'name': unicode(checked)})

        if node_id:
            if field:
              if field == "teaches":
                relationtype = node_collection.one({"_type": "RelationType", "name":"teaches"})
                list_grelations = triple_collection.find({
                    "_type": "GRelation", "subject": node._id,
                    "relation_type": relationtype._id
                })
                for relation in list_grelations:
                  nlist.append(ObjectId(relation.right_subject))
              elif field == "assesses":
                relationtype = node_collection.one({"_type": "RelationType", "name":"assesses"})
                list_grelations = triple_collection.find({
                    "_type": "GRelation", "subject": node._id,
                    "relation_type": relationtype._id
                })
                for relation in list_grelations:
                  nlist.append(ObjectId(relation.right_subject))
              elif field == "prior_node":
                nlist = node.prior_node
              elif field == "collection":
                nlist = node.collection_set

        else:
            node_id = None


        if node_id:
          if node.collection_set:
            if checked:
              for k in node.collection_set:
                obj = node_collection.one({'_id': ObjectId(k)})
                if check:
                  if check._id in obj.member_of:
                    nlist.append(k)
                else:
                  if quiz._id in obj.member_of or quizitem._id in obj.member_of:
                    nlist.append(k)

            else:
              nlist = node.collection_set
              if field == "assesses":
                checked = field
              checked = None

        drawer, paged_resources = get_drawers(group_id, node_id, nlist, page_no, checked)#get_drawers(group_id, node_id, nlist, checked)


        if field == "course_units":
            nlist.append("course_units")
            selection_flag = False
            drawers = get_drawers(group_id, node_id, nlist, checked)

        drawers = drawer
        if not node_id:
          drawer1 = drawers

        else:
          drawer1 = drawers['1']
          drawer2 = drawers['2']

        if not field:
          field = "collection"

        return render_to_response("ndf/drawer_widget.html",
                                  {"widget_for": field, "page_info": paged_resources,
                                   "drawer1": drawer1, 'selection': selection_flag, 'node_id':node_id,
                                   "drawer2": drawer2, "checked": checked,
                                   "groupid": group_id
                                  },
                                  context_instance=RequestContext(request)
        )


@get_execution_time
def search_drawer(request, group_id):
    if request.is_ajax() and request.method == "POST":

      search_name = request.POST.get("search_name", '')
      node_id = request.POST.get("node_id", '')
      selection = request.POST.get("selection", '')
      field = request.POST.get("field", '')

      search_drawer = None
      drawers = None
      drawer1 = None
      drawer2 = None
      dict_drawer = {}
      dict1 = {}
      dict2 = []
      nlist=[]
      node = None
      page_no = 1

      Page = node_collection.one({'_type': 'GSystemType', 'name': 'Page'})
      File = node_collection.one({'_type': 'GSystemType', 'name': 'File'})
      Quiz = node_collection.one({'_type': "GSystemType", 'name': "Quiz"})

      if node_id:
        node = node_collection.one({'_id': ObjectId(node_id)})
        node_type = node_collection.one({'_id': ObjectId(node.member_of[0])})

        if field:
          if field == "teaches":
            relationtype = node_collection.one({"_type": "RelationType", "name": "teaches"})
            list_grelations = triple_collection.find({
                "_type": "GRelation", "subject": node._id, "relation_type": relationtype._id
            })
            for relation in list_grelations:
              nlist.append(ObjectId(relation.right_subject))

          elif field == "assesses":
            relationtype = node_collection.one({"_type": "RelationType", "name": "assesses"})
            list_grelations = triple_collection.find({
                "_type": "GRelation", "subject": node._id, "relation_type": relationtype._id
            })
            for relation in list_grelations:
              nlist.append(ObjectId(relation.right_subject))

          elif field == "prior_node":
            nlist = node.prior_node

          elif field == "collection":
            nlist = node.collection_set

          node.reload()

        search_drawer = node_collection.find({'_type': {'$in' : [u"GSystem", u"File"]},
                                        'member_of':{'$in':[Page._id,File._id,Quiz._id]},
                                        '$and': [
                                          {'name': {'$regex': str(search_name), '$options': "i"}},
                                          {'group_set': {'$all': [ObjectId(group_id)]} }
                                        ]
                                      })


      else:
          search_drawer = node_collection.find({'_type': {'$in' : [u"GSystem", u"File"]},
                                          'member_of':{'$in':[Page._id,File._id,Quiz._id]},
                                          '$and': [
                                            {'name': {'$regex': str(search_name), '$options': "i"}},
                                            {'group_set': {'$all': [ObjectId(group_id)]} }
                                          ]
                                        })


      if node_id:
        for each in search_drawer:
          if each._id != node._id:
            if each._id not in nlist:
              dict1[each._id] = each

        for oid in nlist:
          obj = node_collection.one({'_id': oid })
          dict2.append(obj)

        dict_drawer['1'] = dict1
        dict_drawer['2'] = dict2

      else:
        if (node is None) and (not nlist):
          for each in search_drawer:
            dict_drawer[each._id] = each


      drawers = dict_drawer
      if not node_id:
        drawer1 = drawers
      else:
        drawer1 = drawers['1']
        drawer2 = drawers['2']

      return render_to_response("ndf/drawer_widget.html",
                                {"widget_for": field,
                                 "drawer1": drawer1, 'selection': selection,
                                 "drawer2": drawer2, 'search_name': search_name,
                                 "groupid": group_id, 'node_id': node_id
                                },
                                context_instance=RequestContext(request)
      )

@get_execution_time
def get_topic_contents(request, group_id):
  # if request.is_ajax() and request.method == "POST":
  node_id = request.GET.get("node_id", '')
  selected = request.GET.get("selected", '')
  choice = request.GET.get("choice", '')
  # node = node_collection.one({'_id': ObjectId(node_id) })

  contents = get_contents(node_id, selected, choice)

  return HttpResponse(json.dumps(contents))


####Bellow part is for manipulating theme topic hierarchy####
@get_execution_time
def get_collection_list(collection_list, node):
  inner_list = []
  error_list = []
  inner_list_append_temp=inner_list.append #a temp. variable which stores the lookup for append method
  if node.collection_set:
    for each in node.collection_set:
      col_obj = node_collection.one({'_id': ObjectId(each)})
      if col_obj:
        if theme_item_GST._id in col_obj.member_of or topic_GST._id in col_obj.member_of:
          for cl in collection_list:
            if cl['id'] == node.pk:
              node_type = node_collection.one({'_id': ObjectId(col_obj.member_of[0])}).name
              inner_sub_dict = {'name': col_obj.name, 'id': col_obj.pk , 'node_type': node_type}
              inner_sub_list = [inner_sub_dict]
              inner_sub_list = get_collection_list(inner_sub_list, col_obj)

              if inner_sub_list:
                inner_list_append_temp(inner_sub_list[0])
              else:
                inner_list_append_temp(inner_sub_dict)

              cl.update({'children': inner_list })
      else:
        error_message = "\n TreeHierarchyError: Node with given ObjectId ("+ str(each) +") not found!!!\n"
        print "\n " + error_message

    return collection_list

  else:
    return collection_list



@get_execution_time
def get_tree_hierarchy(request, group_id, node_id):

    Collapsible = request.GET.get("collapsible", "")
    # print "Collapsible : ", Collapsible

    # if cached result exists return it
    cache_key = u'get_tree_hierarchy_' + unicode(group_id) + "_" + unicode(node_id) + "_" + unicode(Collapsible)
    # print cache_key
    cache_result = cache.get(cache_key)
    # print cache_result

    if cache_result:
        return HttpResponse(cache_result)
    # ---------------------------------

    node = node_collection.one({'_id':ObjectId(node_id)})

    data = ""
    collection_list = []
    themes_list = []

    theme_node = node_collection.one({'_id': ObjectId(node._id) })
    # print "\ntheme_node: ",theme_node.name,"\n"
    if theme_node.collection_set:

      for e in theme_node.collection_set:
        objs = node_collection.one({'_id': ObjectId(e) })
        for l in objs.collection_set:
          themes_list.append(l)


      for each in theme_node.collection_set:
        obj = node_collection.one({'_id': ObjectId(each) })
        if obj._id not in themes_list:
          if theme_item_GST._id in obj.member_of or topic_GST._id in obj.member_of:
            node_type = node_collection.one({'_id': ObjectId(obj.member_of[0])}).name
            collection_list.append({'name': obj.name, 'id': obj.pk, 'node_type': node_type})
            collection_list = get_collection_list(collection_list, obj)

    if Collapsible:
      data = { "name": theme_node.name, "children": collection_list }
      cache.set(cache_key, json.dumps(data), 60*15)
    else:
      data = collection_list
      cache.set(cache_key, json.dumps(data), 60*15)

    return HttpResponse(json.dumps(data))
# ###End of manipulating theme topic hierarchy####

##### bellow part is for manipulating nodes collections#####

@get_execution_time
def get_inner_collection(collection_list, node, no_res=False):
  inner_list = []
  error_list = []
  inner_list_append_temp=inner_list.append #a temp. variable which stores the lookup for append method

  # if not no_res or not res_flag:
  is_unit = any(mem_of_name in ["CourseUnit", "CourseUnitEvent"] for mem_of_name in node.member_of_names_list)
  if not no_res or not is_unit:
    if node.collection_set:
      for each in node.collection_set:
        col_obj = node_collection.one({'_id': ObjectId(each)})
        if col_obj:
          for cl in collection_list:
            if cl['id'] == node.pk:
              node_type = node_collection.one({'_id': ObjectId(col_obj.member_of[0])}).name
              # if col_obj._id in completed_ids:
              #   inner_sub_dict = {'name': col_obj.name, 'id': col_obj.pk,'node_type': node_type, "status": "COMPLETED"}
              #   # print "\n completed_ids -- ",completed_ids
              #   # print "\n\n col_obj ---- ", col_obj.name, " - - ",col_obj.member_of_names_list, " -- ", col_obj._id
              # elif col_obj._id in incompleted_ids:
              #   inner_sub_dict = {'name': col_obj.name, 'id': col_obj.pk,'node_type': node_type, "status": "WARNING"}
              #   # print "\n completed_ids -- ",completed_ids
              #   # print "\n\n col_obj ---- ", col_obj.name, " - - ",col_obj.member_of_names_list, " -- ", col_obj._id
              # else:
              inner_sub_dict = {'name': col_obj.name, 'id': col_obj.pk,'node_type': node_type,"type":"division"}
              inner_sub_list = [inner_sub_dict]
              inner_sub_list = get_inner_collection(inner_sub_list, col_obj, no_res)
              # if "CourseSubSectionEvent" == node_type:
              #   start_date_val = get_attribute_value(col_obj._id, "start_time")
              #   if start_date_val:
              #     curr_date_val = datetime.datetime.now().date()
              #     start_date_val = start_date_val.date()
              #     if curr_date_val >= start_date_val or gstaff_access:
              #         inner_sub_dict.update({'start_time_val':start_date_val.strftime("%d/%m/%Y")})
              #     else:
              #         # do not send this CSS
              #         inner_sub_list.remove(inner_sub_dict)
              #         # pass
              if inner_sub_list:
                inner_list_append_temp(inner_sub_list[0])
              else:
                inner_list_append_temp(inner_sub_dict)
              # elif "CourseSubSectionEvent" != node_type:
              #   inner_list_append_temp(inner_sub_dict)

              cl.update({'children': inner_list })
        else:
          error_message = "\n TreeHierarchyError: Node with given ObjectId ("+ str(each) +") not found!!!\n"
          print "\n " + error_message
      return collection_list
    else:
      return collection_list
  elif is_unit:
    for cl in collection_list:
      if cl['id'] == node.pk:
        col_set = node.collection_set
        col_set = map(str,col_set)
        cl.update({'collection_set': col_set })
    return collection_list


@get_execution_time
def get_collection(request, group_id, node_id, no_res=False):
  try:
    # cache_key = u'get_collection' + unicode(group_id) + "_" + unicode(node_id)
    # cache_result = cache.get(cache_key)
    # if cache_result:
    #   return HttpResponse(cache_result)

    node = node_collection.one({'_id':ObjectId(node_id)})
    # print "\nnode: ",node.name,"\n"
    collection_list = []
    gstaff_access = False
    gstaff_access = check_is_gstaff(group_id,request.user)
    for each in node.collection_set:
      obj = node_collection.one({'_id': ObjectId(each) })
      if obj:
        node_type = node_collection.one({'_id': ObjectId(obj.member_of[0])}).name
        # print "000000000000000000000",node.name
        
        collection_list.append({'name':obj.name,'id':obj.pk,'node_type':node_type,'type' : "branch"})
        # collection_list = get_inner_collection(collection_list, obj, gstaff_access, completed_ids_list, incompleted_ids_list)
        if "BaseCourseGroup" in node.member_of_names_list:
          no_res = True
        collection_list = get_inner_collection(collection_list, obj, no_res)
    data = collection_list
    updated_data = []
    # print data
    # cache.set(cache_key, json.dumps(data), 60*15)

    return HttpResponse(json.dumps(data))

  except Exception as ee:
    print ee

@get_execution_time
def add_sub_themes(request, group_id):
  if request.is_ajax() and request.method == "POST":

    context_node_id = request.POST.get("context_node", '')
    sub_theme_name = request.POST.get("sub_theme_name", '')
    themes_list = request.POST.get("nodes_list", '')
    themes_list = themes_list.replace("&quot;","'")
    themes_list = ast.literal_eval(themes_list)

    theme_GST = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item'})
    context_node = node_collection.one({'_id': ObjectId(context_node_id) })

    # Save the sub-theme first
    if sub_theme_name:
      if not sub_theme_name.upper() in (theme_name.upper() for theme_name in themes_list):

        node = node_collection.collection.GSystem()
        # get_node_common_fields(request, node, group_id, theme_GST)

        node.save(is_changed=get_node_common_fields(request, node, group_id, theme_item_GST),groupid=group_id)
        node.reload()
        # Add this sub-theme into context nodes collection_set
        node_collection.collection.update({'_id': context_node._id}, {'$push': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)
        context_node.reload()

        return HttpResponse("success")

      return HttpResponse("failure")

    return HttpResponse("None")

@get_execution_time
def add_theme_item(request, group_id):
  if request.is_ajax() and request.method == "POST":

    existing_id = request.POST.get("existing_id", '')
      
    context_theme_id = request.POST.get("context_theme", '')
    name =request.POST.get('name','')
    parent_node_id =request.POST.get('parent_id','')
    is_topic =request.POST.get('is_topic','')

    context_theme = node_collection.one({'_id': ObjectId(context_theme_id) })
    if existing_id:
      existing_node = Node.get_node_by_id(ObjectId(existing_id))
      if existing_node:
        existing_node.name = unicode(name)
        existing_node.save()
        return HttpResponse("success")
    list_theme_items = []
    if name and context_theme:

      for each in context_theme.collection_set:
        obj = node_collection.one({'_id': ObjectId(each) })
        if obj.name == name:
          return HttpResponse("failure")

      theme_item_node = node_collection.collection.GSystem()
      if is_topic == "True":
        theme_item_node.save(is_changed=get_node_common_fields(request, theme_item_node, group_id, topic_GST),groupid=group_id)
      else:
        theme_item_node.save(is_changed=get_node_common_fields(request, theme_item_node, group_id, theme_item_GST),groupid=group_id)
      theme_item_node.reload()

      # Add this theme item into context theme's collection_set
      if parent_node_id:
        node_collection.collection.update({'_id': ObjectId(parent_node_id)}, {'$push': {'collection_set': ObjectId(theme_item_node._id) }}, upsert=False, multi=False)
      else:
        node_collection.collection.update({'_id': context_theme._id}, {'$push': {'collection_set': ObjectId(theme_item_node._id) }}, upsert=False, multi=False)
      context_theme.reload()

    return HttpResponse("success")

@get_execution_time
def add_topics(request, group_id):
  if request.is_ajax() and request.method == "POST":
    # print "\n Inside add_topics ajax view\n"
    context_node_id = request.POST.get("context_node", '')
    add_topic_name = request.POST.get("add_topic_name", '')
    topics_list = request.POST.get("nodes_list", '')
    topics_list = topics_list.replace("&quot;","'")
    topics_list = ast.literal_eval(topics_list)

    topic_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})
    context_node = node_collection.one({'_id': ObjectId(context_node_id) })

    # Save the topic first
    if add_topic_name:
      # print "\ntopic name: ", add_topic_name
      if not add_topic_name.upper() in (topic_name.upper() for topic_name in topics_list):
        node = node_collection.collection.GSystem()
        # get_node_common_fields(request, node, group_id, topic_GST)

        node.save(is_changed=get_node_common_fields(request, node, group_id, topic_GST),groupid=group_id)
        node.reload()
        # Add this topic into context nodes collection_set
        node_collection.collection.update({'_id': context_node._id}, {'$push': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)
        context_node.reload()

        return HttpResponse("success")

      return HttpResponse("failure")

    return HttpResponse("None")

@get_execution_time
def add_page(request, group_id):
  is_create_note = request.POST.get("is_create_note", '')
  tags = request.POST.get("tags", '')
  if request.is_ajax() and request.method == "POST" and  is_create_note == "True":
      blog_type = request.POST.get("blog_type", '')
      # return HttpResponseRedirect(reverse('page_create_edit', kwargs={'group_id': group_id}))
      gst_page = node_collection.one({'_type': "GSystemType", 'name': "Page"})
      page_node = node_collection.collection.GSystem()
      page_node.save(is_changed=get_node_common_fields(request, page_node, group_id, gst_page))
      page_node.status = u"PUBLISHED"
      blogpage_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"})
      page_node.type_of = [blogpage_gst._id]
      page_node.save()
      discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
      if blog_type:
        create_gattribute(page_node._id, discussion_enable_at, True)
        return_status = create_thread_for_node(request,group_id, page_node)
      page_node.save()
      return HttpResponseRedirect(reverse('course_notebook_note',
                                    kwargs={
                                            'group_id': group_id,
                                            'node_id': page_node._id,
                                            # 'tab': 'my-notes'
                                            })
                                      )


  if request.is_ajax() and request.method == "POST":
    context_node_id = request.POST.get("context_node", '')
    css_node_id = request.POST.get("css_node", '')
    unit_name = request.POST.get("unit_name", '')
    context_name = request.POST.get("context_name", '')

    gst_page = node_collection.one({'_type': "GSystemType", 'name': "Page"})
    name = request.POST.get('name', '')
    collection_list = []
    context_node = None
    response_dict = {"success": False}
    context_node = node_collection.one({'_id': ObjectId(context_node_id)})

    for each in context_node.collection_set:
        obj = node_collection.one({'_id': ObjectId(each), 'group_set': ObjectId(group_id)})
        if obj:
            collection_list.append(obj.name)

    if name not in collection_list:
        page_node = node_collection.collection.GSystem()
        page_node.save(is_changed=get_node_common_fields(request, page_node, group_id, gst_page),groupid=group_id)
        page_node.status = u"PUBLISHED"
        page_node.save()
        context_node.collection_set.append(page_node._id)
        context_node.save(groupid=group_id)
        page_node.prior_node.append(context_node._id)
        page_node.save()
        response_dict["success"] = True
        return HttpResponse(json.dumps(response_dict))

    else:
        response_dict["success"] = False
        return HttpResponse(json.dumps(response_dict))

    response_dict["success"] = None
    return HttpResponse(json.dumps(response_dict))

@get_execution_time
def add_file(request, group_id):
    # this is context node getting from the url get request
    context_node_id = request.GET.get('context_node', '')

    context_node = node_collection.one({'_id': ObjectId(context_node_id)})
    if request.method == "POST":

        context_name = request.POST.get("context_name", "")
        css_node_id = request.POST.get("css_node_id", "")
        course_node = request.POST.get("course_node", "")
        unit_name = request.POST.get("unit_name_file", "")
        app_id = request.POST.get("app_id", "")
        app_set_id = request.POST.get("app_set_id", "")

        if context_name is "Topic":
            url_name = "/" + group_id + "/topic_details/" + context_node_id + ""
        else:
            # i.e  if context_name is "Course"
            url_name = "/" + group_id + "/course/add_units/?css_node_id=" + \
                css_node_id + "&unit_node_id=" + context_node_id + "&course_node="+ course_node
            if app_id and app_set_id:
                url_name += "&app_id=" + app_id + "&app_set_id=" + app_set_id + ""
            if context_node_id:
                # set the unit node name
                node_collection.collection.update({'_id': ObjectId(context_node_id)}, {'$set': {'name': unit_name }}, upsert=False, multi=False)

        new_list = []
        # For checking the node is already available in gridfs or not
        for index, each in enumerate(request.FILES.getlist("doc[]", "")):
            fileobj = node_collection.collection.File()
            filemd5 = hashlib.md5(each.read()).hexdigest()
            if not fileobj.fs.files.exists({"md5": filemd5}):
                # If not available append to the list for making the collection for topic below
                new_list.append(each)
            else:
                if context_name == "Course":
                        # If file exists, PUBLISH it and add to collection set
                        cur_oid = gridfs_collection.find_one({"md5": filemd5}, {'docid': 1, '_id': 0})
                        old_file_node = node_collection.find_one({'_id': ObjectId(str(cur_oid["docid"]))})
                        if old_file_node._id not in context_node.collection_set:
                                context_node.collection_set.append(old_file_node._id)
                                old_file_node.status = u"PUBLISHED"
                                old_file_node.prior_node.append(context_node._id)
                                old_file_node.save(groupid=group_id)
                                context_node.save(groupid=group_id)
                else:
                        # If availbale ,then return to the topic page
                        return HttpResponseRedirect(url_name)
        # After taking new_lst[] , now go for saving the files
        submitDoc(request, group_id)

    # After file gets saved , that file's id should be saved in collection_set of context topic node

    for k in new_list:
        cur_oid = gridfs_collection.find_one({"md5": filemd5}, {'docid': 1, '_id': 0})
        file_obj = node_collection.find_one({'_id': ObjectId(str(cur_oid["docid"]))})
        file_obj.prior_node.append(context_node._id)
        file_obj.status = u"PUBLISHED"
        file_obj.save(groupid=group_id)
        context_node.collection_set.append(file_obj._id)
        file_obj.save(groupid=group_id)
        context_node.save(groupid=group_id)
    return HttpResponseRedirect(url_name)



def collection_of_node(node=None, group_id=None):
    theme_item_GST = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item'})

    if node.collection_set:
      for each in node.collection_set:
        each_node = node_collection.one({'_id': ObjectId(each)})
        if each_node.collection_set:
          collection_of_node(each_node, group_id)
        else:
          # After deleting theme instance it's should also remove from collection_set
          cur = node_collection.find({'member_of': {'$all': [theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

          for e in cur:
            if each_node._id in e.collection_set:
              node_collection.collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(each_node._id) }}, upsert=False, multi=False)


          # print "\n node ", each_node.name ,"has been deleted \n"
          each_node.delete()


      # After deleting theme instance it's should also remove from collection_set
      cur = node_collection.find({'member_of': {'$all': [theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

      for e in cur:
        if node._id in e.collection_set:
          node_collection.collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)

      # print "\n node ", node.name ,"has been deleted \n"
      node.delete()

    else:

      # After deleting theme instance it's should also remove from collection_set
      cur = node_collection.find({'member_of': {'$all': [theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

      for e in cur:
        if node._id in e.collection_set:
          node_collection.collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)


      # print "\n node ", node.name ,"has been deleted \n"
      node.delete()

    return True

@get_execution_time
def theme_node_collection(node=None, group_id=None):
    theme_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Theme'})
    theme_item_GST = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item'})

    if node.collection_set:
      for each in node.collection_set:

        each_node = node_collection.one({'_id': ObjectId(each)})

        if each_node.collection_set:

          collection_of_node(each_node, group_id)
        else:
          # After deleting theme instance it's should also remove from collection_set
          cur = node_collection.find({'member_of': {'$all': [theme_GST._id,theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

          for e in cur:
            if each_node._id in e.collection_set:
              node_collection.collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(each_node._id) }}, upsert=False, multi=False)


          # print "\n node ", each_node.name ,"has been deleted \n"
          each_node.delete()

      # After deleting theme instance it's should also remove from collection_set
      cur = node_collection.find({'member_of': {'$all': [theme_GST._id,theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

      for e in cur:
        if node._id in e.collection_set:
          node_collection.collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)

      # print "\n node ", node.name ,"has been deleted \n"
      node.delete()

    else:

      # After deleting theme instance it's should also remove from collection_set
      cur = node_collection.find({'member_of': {'$all': [theme_GST._id,theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

      for e in cur:
        if node._id in e.collection_set:
          node_collection.collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)

      # print "\n node ", node.name ,"has been deleted \n"
      node.delete()

    return True

@get_execution_time
def delete_themes(request, group_id):
  '''delete themes objects'''
  send_dict = []
  deleteobjects = ""
  deleteobj = ""
  if request.is_ajax() and request.method =="POST":
    context_node_id=request.POST.get('context_theme','')
    if context_node_id:
      context_theme_node = node_collection.one({'_id': ObjectId(context_node_id)})

    confirm = request.POST.get("confirm","")
    deleteobj = request.POST.get('deleteobj',"")
    theme_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Theme'})
    theme_item_GST = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item'})

    if deleteobj:
      obj = node_collection.one({'_id': ObjectId(deleteobj) })
      obj.delete()
      node = node_collection.one({'member_of': {'$in':[theme_GST._id, theme_item_GST._id]}, 'collection_set': ObjectId(deleteobj) })
      node_collection.collection.update({'_id': node._id}, {'$pull': {'collection_set': ObjectId(deleteobj) }}, upsert=False, multi=False)

    else:
      deleteobjects = request.POST['deleteobjects']

    if deleteobjects:
      for each in deleteobjects.split(","):
          node = node_collection.one({ '_id': ObjectId(each)})
          # print "\n confirmed objects: ", node.name

          if confirm:
            if context_node_id:
              collection_of_node(node, group_id)
              if node._id in context_theme_node.collection_set:
                node_collection.collection.update({'_id': context_theme_node._id}, {'$pull': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)

            else:
              theme_node_collection(node, group_id)

          else:
            send_dict.append({"title":node.name})

  return StreamingHttpResponse(json.dumps(send_dict).encode('utf-8'),content_type="text/json", status=200)


@login_required
@get_execution_time
def change_group_settings(request,group_id):
    '''
    changing group's object data
    '''
    if request.is_ajax() and request.method == "POST":
        try:
            edit_policy = request.POST['edit_policy']
            group_type = request.POST['group_type']
            subscription_policy = request.POST['subscription_policy']
            visibility_policy = request.POST['visibility_policy']
            disclosure_policy = request.POST['disclosure_policy']
            encryption_policy = request.POST['encryption_policy']
            # group_id = request.POST['group_id']
            group_node = node_collection.one({"_id": ObjectId(group_id)})
            if group_node:
                group_node.edit_policy = edit_policy
                group_node.group_type = group_type
                group_node.subscription_policy = subscription_policy
                group_node.visibility_policy = visibility_policy
                group_node.disclosure_policy = disclosure_policy
                group_node.encryption_policy = encryption_policy
                group_node.modified_by = int(request.user.id)
                group_node.save(groupid=group_id)
                return HttpResponse("changed successfully")
        except:
            return HttpResponse("failed")

    return HttpResponse("failed")


list_of_collection = []
hm_obj = HistoryManager()

@get_execution_time
def get_module_set_list(node):
    '''
        Returns the list of collection inside the collections with hierarchy as they are in collection
    '''
    list = []
    for each in node.collection_set:
        each = node_collection.one({'_id': each})
        dict = {}
        dict['id'] = unicode(each._id)
        dict['version_no'] = hm_obj.get_current_version(each)
        if each._id not in list_of_collection:
            list_of_collection.append(each._id)
            if each.collection_set:                                   #checking that same collection can'not be called again
                dict['collection'] = get_module_set_list(each)         #calling same function recursivaly
        list.append(dict)
    return list


@login_required
@get_execution_time
def make_module_set(request, group_id):
    '''
    This methode will create module of collection and stores objectid's with version number's
    '''
    if request.is_ajax():
        try:
            GST_MODULE = node_collection.one({"_type": "GSystemType", 'name': GAPPS[8]})
            _id = request.GET.get("_id","")
            if _id:
                node = node_collection.one({'_id':ObjectId(_id)})
                if node:
                    list_of_collection.append(node._id)
                    dict = {}
                    dict['id'] = unicode(node._id)
                    dict['version_no'] = hm_obj.get_current_version(node)
                    if node.collection_set:
                        dict['collection'] = get_module_set_list(node)     #gives the list of collection with proper hierarchy as they are

                    #creating new Gsystem object and assining data of collection object
                    gsystem_obj = node_collection.collection.GSystem()
                    gsystem_obj.name = unicode(node.name)
                    gsystem_obj.content = unicode(node.content)
                    gsystem_obj.member_of.append(GST_MODULE._id)
                    gsystem_obj.group_set.append(ObjectId(group_id))
                    # if usrname not in gsystem_obj.group_set:
                    #     gsystem_obj.group_set.append(int(usrname))
                    user_id = int(request.user.id)
                    gsystem_obj.created_by = user_id
                    gsystem_obj.modified_by = user_id
                    if user_id not in gsystem_obj.contributors:
                        gsystem_obj.contributors.append(user_id)
                    gsystem_obj.module_set.append(dict)
                    module_set_md5 = hashlib.md5(str(gsystem_obj.module_set)).hexdigest() #get module_set's md5
                    check =check_module_exits(module_set_md5)          #checking module already exits or not
                    if(check == 'True'):
                        return HttpResponse("This module already Exists")
                    else:
                        gsystem_obj.save(groupid=group_id)
                        create_relation_of_module(node._id, gsystem_obj._id)
                        create_version_of_module(gsystem_obj._id,node._id)
                        check1 = sotore_md5_module_set(gsystem_obj._id, module_set_md5)
                        if (check1 == 'True'):
                            return HttpResponse("module succesfull created")
                        else:
                            gsystem_obj.delete()
                            return HttpResponse("Error Occured while storing md5 of object in attribute'")
                else:
                    return HttpResponse("Object not present corresponds to this id")

            else:
                return HttpResponse("Not a valid id passed")
        except Exception as e:
            print "Error:",e
            return HttpResponse(e)

@get_execution_time
def sotore_md5_module_set(object_id, module_set_md5):
    '''
    This method will store md5 of module_set of perticular GSystem into an Attribute
    '''
    node_at = node_collection.one({'$and':[{'_type': 'AttributeType'},{'name': 'module_set_md5'}]}) #retrving attribute type
    if node_at is not None:
        try:
            attr_obj = triple_collection.collection.GAttribute()                #created instance of attribute class
            attr_obj.attribute_type = node_at._id
            attr_obj.subject = object_id
            attr_obj.object_value = unicode(module_set_md5)
            attr_obj.save()
        except Exception as e:
            print "Exception:",e
            return 'False'
        return 'True'
    else:
        print "Run 'python manage.py filldb' commanad to create AttributeType 'module_set_md5' "
        return 'False'



# under construction
@get_execution_time
def create_version_of_module(subject_id, node_id):
    '''
    This method will create attribute version_no of module with at type version
    '''
    rt_has_module = node_collection.one({'_type':'RelationType', 'name':'has_module'})
    relation = triple_collection.find({'_type': 'GRelation', 'subject': node_id, 'relation_type':rt_has_module._id})
    at_version = node_collection.one({'_type':'AttributeType', 'name':'version'})
    attr_versions = []
    if relation.count() > 0:
        for each in relation:
            module_id = triple_collection.one({'_id': each['_id']})
            if module_id:
                attr = triple_collection.one({
                    '_type': 'GAttribute', 'subject': ObjectId(module_id.right_subject),
                    'attribute_type': at_version._id
                })
            if attr:
                attr_versions.append(attr.object_value)

    if attr_versions:
        attr_versions.sort()
        attr_ver = float(attr_versions[-1])
        attr = triple_collection.collection.GAttribute()
        attr.attribute_type = at_version._id
        attr.subject = subject_id
        attr.object_value = round((attr_ver+0.1),1)
        attr.save()
    else:
        attr = triple_collection.collection.GAttribute()
        attr.attribute_type = at_version._id
        attr.subject = ObjectId(subject_id)
        attr.object_value = 1
        attr.save()


@get_execution_time
def create_relation_of_module(subject_id, right_subject_id):
    rt_has_module = node_collection.one({'_type': 'RelationType', 'name': 'has_module'})
    if rt_has_module and subject_id and right_subject_id:
        relation = triple_collection.collection.GRelation()                         #instance of GRelation class
        relation.relation_type = rt_has_module._id
        relation.right_subject = right_subject_id
        relation.subject = subject_id
        relation.save()


@get_execution_time
def check_module_exits(module_set_md5):
    '''
    This method will check is module already exits ?
    '''
    node_at = node_collection.one({'$and':[{'_type': 'AttributeType'},{'name': 'module_set_md5'}]})
    attribute = triple_collection.one({'_type':'GAttribute', 'attribute_type': node_at._id, 'object_value': module_set_md5})
    if attribute is not None:
        return 'True'
    else:
        return 'False'

@get_execution_time
def walk(node):
    hm = HistoryManager()
    list = []
    for each in node:
       dict = {}
       node = node_collection.one({'_id':ObjectId(each['id'])})
       n = hm.get_version_document(node,each['version_no'])
       dict['label'] = n.name
       dict['id'] = each['id']
       dict['version_no'] = each['version_no']
       if "collection" in each.keys():
             dict['children'] = walk(each['collection'])
       list.append(dict)
    return list

@get_execution_time
def get_module_json(request, group_id):
    _id = request.GET.get("_id", "")
    node = node_collection.one({'_id': ObjectId(_id)})
    data = walk(node.module_set)
    return HttpResponse(json.dumps(data))


# ------------- For generating graph json data ------------
@get_execution_time
def graph_nodes(request, group_id):
  page_node = node_collection.one({'_id': ObjectId(request.GET.get("id"))})
  page_node.get_neighbourhood(page_node.member_of)
  # print page_node.keys()
  coll_relation = {'relation_name': 'has_collection', 'inverse_name': 'member_of_collection'}

  prior_relation = {'relation_name': 'prerequisite', 'inverse_name': 'is_required_for'}

  def _get_node_info(node_id):
    node = node_collection.one( {'_id':node_id}  )
    # mime_type = "true"  if node.structure.has_key('mime_type') else 'false'

    return node.name

  # def _get_username(id_int):
    # return User.objects.get(id=id_int).username

  # def _get_node_url(node_id):

  #   node_url = '/' + str(group_id)
  #   node = node_collection.one({'_id':node_id})

  #   if len(node.member_of) > 1:
  #     if node.mime_type == 'image/jpeg':
  #       node_url += '/image/image_detail/' + str(node_id)
  #     elif node.mime_type == 'video':
  #       node_url += '/video/video_detail/' + str(node_id)

  #   elif len(node.member_of) == 1:
  #     gapp_name = (node_collection.one({'_id':node.member_of[0]}).name).lower()

  #     if gapp_name == 'forum':
  #       node_url += '/forum/show/' + str(node_id)

  #     elif gapp_name == 'file':
  #       node_url += '/image/image_detail/' + str(node_id)

  #     elif gapp_name == 'page':
  #       node_url += '/page/details/' + str(node_id)

  #     elif gapp_name == 'quiz' or 'quizitem':
  #       node_url += '/quiz/details/' + str(node_id)
  #   return node_url

  # page_node_id = str(id(page_node._id))
  node_metadata ='{"screen_name":"' + page_node.name + '",  "title":"' + page_node.name + '",  "_id":"'+ str(page_node._id) +'", "refType":"GSystem"}, '
  node_relations = ''
  exception_items = [
                      "name", "content", "_id", "login_required", "attribute_set", "relation_set",
                      "member_of", "status", "comment_enabled", "start_publication",
                      "_type", "contributors", "created_by", "modified_by", "last_update", "url", "featured", "relation_set", "access_policy", "snapshot",
                      "created_at", "group_set", "type_of", "content_org", "author_set",
                      "fs_file_ids", "file_size", "mime_type", "location", "language",
                      "property_order", "rating", "apps_list", "annotations", "instance of","if_file"
                    ]

  # username = User.objects.get(id=page_node.created_by).username

  i = 1
  for key, value in page_node.items():
    if (key in exception_items) or (not value):
      pass

    elif isinstance(value, list):

      if len(value):

        # node_metadata +='{"screen_name":"' + key + '", "_id":"'+ str(i) +'_r"}, '
        node_metadata +='{"screen_name":"' + key + '", "_id":"'+ str(abs(hash(key+str(page_node._id)))) +'_r"}, '
        node_relations += '{"type":"'+ key +'", "from":"'+ str(page_node._id) +'", "to": "'+ str(abs(hash(key+str(page_node._id)))) +'_r"},'
        # key_id = str(i)
        key_id = str(abs(hash(key+str(page_node._id))))
        # i += 1

        # if key in ("modified_by", "author_set"):
        #   for each in value:
        #     node_metadata += '{"screen_name":"' + _get_username(each) + '", "_id":"'+ str(i) +'_n"},'
        #     node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(i) +'_n"},'
        #     i += 1

        # else:

        for each in value:
          # print "\n====", key, "------", type(each)

          if isinstance(each, ObjectId):
            node_name = _get_node_info(each)
            if key == "collection_set":
              inverse = coll_relation['inverse_name']
            elif key == "prior_node":
              inverse = prior_relation['inverse_name']
            else:
              inverse = ""

            node_metadata += '{"screen_name":"' + node_name + '", "title":"' + page_node.name + '", "_id":"'+ str(each) +'", "refType":"Relation", "inverse":"' + inverse + '", "flag":"1"},'
            # node_metadata += '{"screen_name":"' + node_name + '", "_id":"'+ str(each) +'", "refType":"relation"},'
            node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(each) +'"},'
            i += 1

          # if "each" is Object of GSystem
          elif isinstance(each, GSystem):
            node_metadata += '{"screen_name":"' + each.name + '", "title":"' + page_node.name + '", "_id":"'+ str(each._id) + '", "refType":"Relation"},'
            node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(each._id) +'"},'

          else:

            node_metadata += '{"screen_name":"' + unicode(each) + '", "_id":"'+ unicode(each) +'_n"},'
            node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ unicode(each) +'_n"},'
            i += 1

    else:
      # possibly gives GAttribute
      node_metadata +='{"screen_name":"' + key + '", "_id":"'+ str(abs(hash(key+str(page_node._id)))) +'_r"},'
      node_relations += '{"type":"'+ key +'", "from":"'+ str(page_node._id) +'", "to": "'+ str(abs(hash(key+str(page_node._id)))) +'_r"},'

      # key_id = str(i)
      key_id = str(abs(hash(key+str(page_node._id))))

      if isinstance( value, list):
        for each in value:
          node_metadata += '{"screen_name":"' + each + '", "_id":"'+ str(i) +'_n"},'
          node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(i) +'_n"},'
          i += 1

      else:
        node_metadata += '{"screen_name":"' + str(value) + '", "_id":"'+ str(i) +'_n"},'
        node_relations += '{"type":"'+ key +'", "from":"'+ str(abs(hash(key+str(page_node._id)))) +'_r", "to": "'+ str(i) +'_n"},'

        i += 1
    # End of if - else
  # End of for loop


  # # getting all the relations of current node
  # node_rel = page_node.get_possible_relations(page_node.member_of)
  # # print "\n\n", node_rel
  # for keyy, vall in node_rel.iteritems():

  #   if vall['subject_or_right_subject_list']:

  #     for eachnode in vall['subject_or_right_subject_list']:
    # if keyy == "event_organised_by":
    #   pass
    #   # node_metadata +='{"screen_name":"' + keyy + '", "_id":"'+ str(abs(hash(keyy+str(page_node._id)))) +'_r"},'
    #   # node_relations += '{"type":"'+ keyy +'", "from":"'+ str(page_node._id) +'", "to": "'+ str(abs(hash(keyy+str(page_node._id)))) +'_r"},'

    #   # node_metadata += '{"screen_name":"' + str(vall) + '", "_id":"'+ str(i) +'_n"},'
    #   # node_relations += '{"type":"'+ keyy +'", "from":"'+ str(abs(hash(keyy+str(page_node._id)))) +'_r", "to": "'+ str(i) +'_n"},'
    # else:

    #   node_metadata +='{"screen_name":"' + keyy + '", "_id":"'+ str(abs(hash(keyy+str(page_node._id)))) +'_r"},'
    #   node_relations += '{"type":"'+ keyy +'", "from":"'+ str(page_node._id) +'", "to": "'+ str(abs(hash(keyy+str(page_node._id)))) +'_r"},'
    #   vall = vall.altnames if ( len(vall['altnames'])) else _get_node_info(vall['subject_or_right_subject_list'][0])
    #   node_metadata += '{"screen_name":"' + str(vall) + '", "_id":"'+ str(i) +'_n"},'
    #   node_relations += '{"type":"'+ keyy +'", "f**rom":"'+ str(abs(hash(keyy+str(page_node._id)))) +'_r", "to": "'+ str(i) +'_n"},'
    # print "\nkey : ", key, "=====", val


  node_metadata = node_metadata[:-1]
  node_relations = node_relations[:-1]

  node_graph_data = '{ "node_metadata": [' + node_metadata + '], "relations": [' + node_relations + '] }'

  # print node_graph_data

  return StreamingHttpResponse(node_graph_data)
# ------ End of processing for graph ------


@get_execution_time
def get_data_for_switch_groups(request,group_id):
    coll_obj_list = []
    node_id = request.GET.get("object_id", "")
    st = node_collection.find({"_type": "Group"})
    node = node_collection.one({"_id": ObjectId(node_id)})
    for each in node.group_set:
        coll_obj_list.append(node_collection.one({'_id': each}))
    data_list = set_drawer_widget(st, coll_obj_list)
    return HttpResponse(json.dumps(data_list))


@get_execution_time
def get_data_for_drawer(request, group_id):
    '''
    designer module's drawer widget function
    '''
    coll_obj_list = []
    node_id = request.GET.get("id","")
    st = node_collection.find({"_type":"GSystemType"})
    node = node_collection.one({"_id":ObjectId(node_id)})
    for each in node.collection_set:
        coll_obj_list.append(node_collection.one({'_id':each}))
    data_list=set_drawer_widget(st,coll_obj_list)
    return HttpResponse(json.dumps(data_list))


# This method is not in use
@get_execution_time
def get_data_for_user_drawer(request, group_id,):
    # This method will return data for user widget
    d1 = []
    d2 = []
    draw1 = {}
    draw2 = {}
    drawer1 = []
    drawer2 = []
    data_list = []
    all_batch_user = []
    users = []
    st_batch_id = request.GET.get('st_batch_id','')
    node_id = request.GET.get('_id','')
    if st_batch_id:
        batch_coll = node_collection.find({'member_of': {'$all': [ObjectId(st_batch_id)]}, 'group_set': {'$all': [ObjectId(group_id)]}})
        group = node_collection.one({'_id':ObjectId(group_id)})
        if batch_coll:
            for each in batch_coll:
                users = users+each.author_set
        else:
            users = []
        user_list = list(set(group.author_set) - set(users))
        for each in user_list:
            user= User.objects.get(id=each)
            dic = {}
            dic['id'] = user.id
            dic['name'] = user.username
            d1.append(dic)
        draw1['drawer1'] = d1
        data_list.append(draw1)
        if node_id:
            for each in node_collection.one({'_id':ObjectId(node_id)}).author_set:
                user= User.objects.get(id=each)
                dic = {}
                dic['id'] = user.id
                dic['name'] = user.username
                d2.append(dic)
        draw2['drawer2'] = d2
        data_list.append(draw2)
        return HttpResponse(json.dumps(data_list))
    else:
        return HttpResponse("GSystemType for batch required")


@get_execution_time
def set_drawer_widget_for_users(st, coll_obj_list):
    '''
    NOTE : this method is used only for user drwers (Django user class)
    '''
    draw2={}
    draw1={}
    data_list=[]
    d1=[]
    d2=[]
    for each in st:
       dic = {}
       dic['id'] = str(each.id)
       dic['email'] = each.email  # username
       dic['username'] = each.username  # username
       d1.append(dic)
    draw1['drawer1'] = d1
    data_list.append(draw1)

    for each in coll_obj_list:
       dic = {}
       dic['id'] = str(each.id)
       # dic['name'] = each.email  # username
       dic['email'] = each.email  # username
       dic['username'] = each.username  # username
       d2.append(dic)

    draw2['drawer2'] = d2
    data_list.append(draw2)
    return data_list

@get_execution_time
def get_data_for_batch_drawer(request, group_id):
    '''
    This method will return data for batch drawer widget
    '''
    d1 = []
    d2 = []
    draw1 = {}
    draw2 = {}
    drawer1 = []
    drawer2 = []
    data_list = []
    st = node_collection.one({'_type':'GSystemType','name':'Student'})
    node_id = request.GET.get('_id','')
    batch_coll = node_collection.find({"_type": "GSystem", 'member_of':st._id, 'group_set': {'$all': [ObjectId(group_id)]}})
    if node_id:
        rt_has_batch_member = node_collection.one({'_type':'RelationType','name':'has_batch_member'})
        relation_coll = triple_collection.find({'_type':'GRelation', 'right_subject':ObjectId(node_id), 'relation_type':rt_has_batch_member._id})
        for each in relation_coll:
            dic = {}
            n = triple_collection.one({'_id':ObjectId(each.subject)})
            drawer2.append(n)
    for each in batch_coll:
        drawer1.append(each)
    drawer_set1 = set(drawer1) - set(drawer2)

    drawer_set2 = drawer2
    for each in drawer_set1:
        dic = {}
        dic['id'] = str(each._id)
        dic['name'] = each.name
        d1.append(dic)
    draw1['drawer1'] = d1
    data_list.append(draw1)
    for each in drawer_set2:
        dic = {}
        dic['id'] = str(each._id)
        dic['name'] = each.name
        d2.append(dic)
    draw2['drawer2'] = d2
    data_list.append(draw2)
    return HttpResponse(json.dumps(data_list))

@get_execution_time
def set_drawer_widget(st, coll_obj_list, extra_key=None):
    '''
    this method will set data for drawer widget
    '''
    stobjs=[]
    coll_objs=[]
    data_list = []
    d1 = []
    d2 = []
    draw1 = {}
    draw2 = {}
    drawer1=[]
    drawer2=[]
    for each in st:
        stobjs.append(each['_id'])
    for each in coll_obj_list:
        coll_objs.append(each['_id'])
    drawer1_set = set(stobjs) - set(coll_objs)
    lstset=[]
    for each in drawer1_set:
        obj=node_collection.one({'_id':each})
        lstset.append(obj)
    drawer1=lstset
    drawer2 = coll_obj_list
    for each in drawer1:
       dic = {}
       dic['id'] = str(each['_id'])
       dic['name'] = each['name']
       try:
         dic[extra_key] = each[extra_key]
       except:
         pass
       d1.append(dic)
    draw1['drawer1'] = d1
    data_list.append(draw1)
    for each in drawer2:
       dic = {}
       dic['id'] = str(each['_id'])
       dic['name'] = each['name']
       try:
         dic[extra_key] = each[extra_key]
       except:
         pass
       d2.append(dic)
    draw2['drawer2'] = d2
    data_list.append(draw2)
    return data_list

@get_execution_time
def get_data_for_event_task(request, group_id):
    #date creation for task type is date month and year
    day_list=[]
    append = day_list.append
    event_count={}
    list31=[1,3,5,7,8,10,12]
    list30=[4,6,9,11]
    import datetime
    currentYear = datetime.datetime.now().year
    #create the date format in unix format for querying it from data
    #Task attribute_type start time's object value takes the only date
    #in month/date/year format
    #As events are quried from the nodes which store the date time in unix format
    no = request.GET.get('no','')
    month = request.GET.get('start','')[5:7]
    year = request.GET.get('start','')[0:4]
    start = datetime.datetime(int(currentYear), int(month), 1)
    task_start = str(int(month))+"/"+"01"+"/"+str(int(year))

    now = datetime.datetime.now()
    e_status = node_collection.one({'_type' : 'AttributeType' , 'name': 'event_status'})

    if int(month) in list31:
     end=datetime.datetime(int(currentYear),int(month), 31)
     task_end=str(int(month))+"/"+"31"+"/"+str(int(year))
    elif int(month) in list30:
     end=datetime.datetime(int(currentYear),int(month), 30)
     task_end=str(int(month))+"/"+"30"+"/"+str(int(year))
    # Check for leap year
    elif currentYear%4 == 0:
      if currentYear%100 == 0:
        if currentYear%400 == 0:
          end=datetime.datetime(int(currentYear),int(month), 29)
          task_end=str(int(month))+"/"+"29"+"/"+str(int(year))
        else:
          end=datetime.datetime(int(currentYear),int(month), 28)
          task_end=str(int(month))+"/"+"28"+"/"+str(int(year))
      else:
        end=datetime.datetime(int(currentYear),int(month), 29)
        task_end=str(int(month))+"/"+"29"+"/"+str(int(year))
    else:
       end=datetime.datetime(int(currentYear),int(month), 28)
       task_end=str(int(month))+"/"+"28"+"/"+str(int(year))

    #day_list of events

    # For including events on the last date of the month uptill 00:00:00 of first date of next month
    end = end + datetime.timedelta(days = 1)

    if no == '1' or no == '2':
       #condition to search events only in case of above condition so that it
       #doesnt gets executed when we are looking for other data
       event = node_collection.one({'_type': "GSystemType", 'name': "Event"})
       obj = node_collection.find({'type_of': event._id},{'_id':1})
       all_list = [ each_gst._id for each_gst in obj ]

    if no == '1':
        nodes = node_collection.find({'_type':'GSystem','member_of':{'$in':all_list},'attribute_set.start_time':{'$gte':start,'$lt': end},'group_set':ObjectId(group_id)})
        for i in nodes:
          attr_value={}
          update = attr_value.update
          event_url="/"+str(group_id)+"/event/"+str(i.member_of[0]) +"/"+str(i._id)
          update({'url':event_url})
          update({'id':i._id})
          update({'title':i.name})
          date=i.attribute_set[0]['start_time']
          formated_date=date.strftime("%Y-%m-%dT%H:%M:%S")
          update({'start':formated_date})

          for j in i.attribute_set:
            if unicode('end_time') in j.keys():
              end_time = j['end_time']
            elif unicode('event_status') in j.keys():
              status = j['event_status']

          if now > end_time and status == "Scheduled":
            create_gattribute(i._id , e_status , unicode("Completed"))
            status = "Completed"

          if status == "Rescheduled":
            update({'backgroundColor':'#ffd700'})
          if status == "Completed":
            update({'backgroundColor':'green'})
          if status == "Incomplete":
            update({'backgroundColor':'red'})

          append(dict(attr_value))

    if no == '2':
        #All the Rescheduled ones
        nodes = node_collection.find({'_type':'GSystem','member_of':{'$in':list(all_list)},'attribute_set.event_edit_reschedule.reschedule_dates':{ '$elemMatch':{'$gt':start}},'group_set':ObjectId(group_id)},{'attribute_set.event_edit_reschedule.reschedule_dates':1,"name":1})
        for k in nodes:
          for a in k.attribute_set:
             if  unicode('event_edit_reschedule') in a:
                for v in a['event_edit_reschedule']['reschedule_dates']:
                      attr_value={}
                      update = attr_value.update
                      event_url=" "
                      update({'url':event_url})
                      update({'id':k._id})
                      update({'title':k.name})
                      date = v
                      try:
                              formated_date=date.strftime("%Y-%m-%dT%H:%M:%S")
                              update({'start':formated_date})
                              update({'backgroundColor':'#7e7e7e'})
                              append(dict(attr_value))
                      except:
                              pass
    date=""
    user_assigned=[]
    user_append = user_assigned.append
    #day_list of task
    if no == '3':
          groupname=node_collection.find_one({"_id":ObjectId(group_id)})
          attributetype_assignee = node_collection.find_one({"_type":'AttributeType', 'name':'Assignee'})
          attributetype_key1 = node_collection.find_one({"_type":'AttributeType', 'name':'start_time'})
          #check wheather the group is author group or the common group
          if groupname._type == "Group":
                GST_TASK = node_collection.one({'_type': "GSystemType", 'name': 'Task'})
                task_nodes = node_collection.find({"_type": "GSystem", 'member_of':GST_TASK._id, 'group_set': ObjectId(group_id)})
          if groupname._type == "Author":
                task_nodes = triple_collection.find({"_type":"GAttribute", "attribute_type":attributetype_assignee._id, "object_value":request.user.id}).sort('last_update',-1)
          for attr in task_nodes:
           if groupname._type == "Group":
               task_node = node_collection.one({'_id':attr._id})
           if groupname._type == "Author":
               task_node = node_collection.one({'_id':attr.subject})
           if task_node:
                        attr1=triple_collection.find_one({
                            "_type":"GAttribute", "subject":task_node._id, "attribute_type":attributetype_key1._id,
                            'object_value':{'$gte':task_start,'$lte':task_end}
                         })
                        attr_value={}
                        update = attr_value.update
                        task_url="/" + groupname.name +"/" + "task"+"/" + str(task_node._id)
                        update({'id':task_node._id})
                        update({'title':task_node.name})
                        if attr1:
                              date = attr1.object_value
                              formated_date=date.strftime("%Y-%m-%dT%H:%M:%S")
                              update({'start':formated_date})
                        else:
                              date=task_node.created_at
                              formated_date=date.strftime("%Y-%m-%dT%H:%M:%S")
                              attr_value.update({'start':formated_date})
                        update({'url':task_url})
                        append(attr_value)

    return HttpResponse(json.dumps(day_list,cls=NodeJSONEncoder))

@get_execution_time
def get_data_for_drawer_of_attributetype_set(request, group_id):
    '''
    this method will fetch data for designer module's drawer widget
    '''
    data_list = []
    d1 = []
    d2 = []
    draw1 = {}
    draw2 = {}
    node_id = request.GET.get("id","")
    coll_obj_list = []
    st = node_collection.find({"_type":"AttributeType"})
    node = node_collection.one({"_id":ObjectId(node_id)})
    for each in node.attribute_type_set:
        coll_obj_list.append(each)
    drawer1 = list(set(st) - set(coll_obj_list))
    drawer2 = coll_obj_list
    for each in drawer1:
       dic = {}
       dic['id'] = str(each._id)
       dic['name'] = str(each.name)
       d1.append(dic)
    draw1['drawer1'] = d1
    data_list.append(draw1)
    for each in drawer2:
       dic = {}
       dic['id'] = str(each._id)
       dic['name'] = str(each.name)
       d2.append(dic)
    draw2['drawer2'] = d2
    data_list.append(draw2)
    return HttpResponse(json.dumps(data_list))

@get_execution_time
def get_data_for_drawer_of_relationtype_set(request, group_id):
    '''
    this method will fetch data for designer module's drawer widget
    '''
    data_list = []
    d1 = []
    d2 = []
    draw1 = {}
    draw2 = {}
    node_id = request.GET.get("id","")
    coll_obj_list = []
    st = node_collection.find({"_type":"RelationType"})
    node = node_collection.one({"_id":ObjectId(node_id)})
    for each in node.relation_type_set:
        coll_obj_list.append(each)
    drawer1 = list(set(st) - set(coll_obj_list))
    drawer2 = coll_obj_list
    for each in drawer1:
       dic = {}
       dic['id'] = str(each._id)
       dic['name'] = str(each.name)
       d1.append(dic)
    draw1['drawer1'] = d1
    data_list.append(draw1)
    for each in drawer2:
       dic = {}
       dic['id'] = str(each._id)
       dic['name'] = str(each.name)
       d2.append(dic)
    draw2['drawer2'] = d2
    data_list.append(draw2)
    return HttpResponse(json.dumps(data_list))


@login_required
@get_execution_time
def deletion_instances(request, group_id):
  """
  Deletes the given node(s) and associated GAttribute(s) & GRelation(s)
  or provides all information before deleting for confirmation.
  """

  send_dict = []
  if request.is_ajax() and request.method =="POST":
    deleteobjects = request.POST['deleteobjects']
    confirm = request.POST.get("confirm", "")

    for each in deleteobjects.split(","):
      delete_list = []
      node = node_collection.one({'_id': ObjectId(each)})
      left_relations = triple_collection.find({"_type": "GRelation", "subject": node._id})
      right_relations = triple_collection.find({"_type": "GRelation", "right_subject": node._id})
      attributes = triple_collection.find({"_type": "GAttribute", "subject": node._id})

      # When confirm holds "yes" value, all given node(s) is/are deleted.
      # Otherwise, required information is provided for confirmation before deletion.
      if confirm:
        # Deleting GRelation(s) where given node is used as "subject"
        for each_left_gr in left_relations:
          # Special case
          if each_left_gr.relation_type.name == "has_login":
            auth_node = node_collection.one(
              {'_id': each_left_gr.right_subject},
              {'created_by': 1}
            )

            if auth_node:
              node_collection.collection.update(
                {'_type': "Group", '$or': [{'group_admin': auth_node.created_by}, {'author_set': auth_node.created_by}]},
                {'$pull': {'group_admin': auth_node.created_by, 'author_set': auth_node.created_by}},
                upsert=False, multi=True
              )

          # If given node is used in relationship with any other node (as subject)
          # Then given node's ObjectId must be removed from "relation_set" field
          # of other node, referred under key as inverse-name of the RelationType
          node_collection.collection.update(
            {'_id': each_left_gr.right_subject, 'relation_set.'+each_left_gr.relation_type.inverse_name: {'$exists': True}},
            {'$pull': {'relation_set.$.'+each_left_gr.relation_type.inverse_name: node._id}},
            upsert=False, multi=False
          )
          each_left_gr.delete()

        # Deleting GRelation(s) where given node is used as "right_subject"
        for each_right_gr in right_relations:
          # If given node is used in relationship with any other node (as subject)
          # Then given node's ObjectId must be removed from "relation_set" field
          # of other node, referred under key as name of the RelationType
          node_collection.collection.update({'_id': each_right_gr.subject, 'relation_set.'+each_right_gr.relation_type.name: {'$exists': True}},
            {'$pull': {'relation_set.$.'+each_right_gr.relation_type.name: node._id}},
            upsert=False, multi=False
          )
          each_right_gr.delete()

        # Deleting GAttribute(s)
        for each_ga in attributes:
          each_ga.delete()

        # Finally deleting given node
        node.delete()

      else:
        if left_relations :
          list_rel = []
          for each in left_relations:
            rname = node_collection.find_one({"_id":each.right_subject})
            if not rname:
              continue
            rname = rname.name
            alt_names = each.relation_type.name
            if each.relation_type.altnames:
              if ";" in each.relation_type.altnames:
                alt_names = each.relation_type.altnames.split(";")[0]
            list_rel.append(alt_names + " (Relation): " + rname)

          delete_list.append({'left_relations': list_rel})

        if right_relations :
          list_rel = []
          for each in right_relations:
            lname = node_collection.find_one({"_id":each.subject})
            if not lname:
              continue
            lname = lname.name
            alt_names = each.relation_type.name
            if each.relation_type.altnames:
              if ";" in each.relation_type.altnames:
                alt_names = each.relation_type.altnames.split(";")[1]
            list_rel.append(alt_names + " (Inverse-Relation): " + lname)

          delete_list.append({'right_relations': list_rel})

        if attributes:
          list_att = []
          for each in attributes:
            alt_names = each.attribute_type.name
            if each.attribute_type.altnames:
              alt_names = each.attribute_type.altnames
            list_att.append(alt_names + " (Attribute): " + str(each.object_value))

          delete_list.append({'attributes': list_att})

        send_dict.append({"title": node.name, "content": delete_list})

    if confirm:
      return StreamingHttpResponse(str(len(deleteobjects.split(",")))+" objects deleted")

  return StreamingHttpResponse(json.dumps(send_dict).encode('utf-8'),content_type="text/json", status=200)


@get_execution_time
def get_visited_location(request, group_id):
  usrid = request.user.id
  visited_location = ""

  if(usrid):

    usrid = int(request.user.id)
    usrname = unicode(request.user.username)

    author = node_collection.one({'_type': "GSystemType", 'name': "Author"})
    user_group_location = node_collection.one({'_type': "Author", 'member_of': author._id, 'created_by': usrid, 'name': usrname})

    if user_group_location:
      visited_location = user_group_location.visited_location

  return StreamingHttpResponse(json.dumps(visited_location))


'''
@login_required
@get_execution_time
def get_online_editing_user(request, group_id):
    #get user who is currently online and editing the node
    if request.is_ajax() and request.method == "POST":
        editorid = request.POST.get('editorid', "")
    viewobj = ViewObj.objects.filter(filename=editorid)
    userslist = []
    if viewobj:
        for each in viewobj:
            if not each.username == request.user.username:
                blankdict = {}
                blankdict['username']=each.username
                get_profile =  get_profile_pic(each.username)
                if get_profile :
                    blankdict['pro_img'] = "/"+str(group_id)+"/image/thumbnail/"+str(get_profile._id)
                else :
                    blankdict['pro_img'] = "no";
                userslist.append(blankdict)
        if len(userslist) == 0:
            userslist.append("No users")
    else :
        userslist.append("No users")

    return StreamingHttpResponse(json.dumps(userslist).encode('utf-8'),content_type="text/json")
'''

@get_execution_time
def view_articles(request, group_id):
  if request.is_ajax():
    # extracting all the bibtex entries from database
    GST_one=node_collection.one({'_type':'AttributeType','name':'Citation'})
    list_item=['article','book','booklet','conference','inbook','incollection','inproceedings','manual','masterthesis','misc','phdthesis','proceedings','techreport','unpublished_entry']
    response_dict=[]

    for each in list_item:
      dict2={}
      ref=node_collection.one({'_type':'GSystemType','name':each})

      ref_entry=node_collection.find({"_type": "GSystem", 'member_of':{'$all':[ref._id]},'group_set':{'$all':[ObjectId(group_id)]},'status':u'PUBLISHED'})

      list_entry=[]
      for every in ref_entry:

        id=every._id
        gst_attribute=triple_collection.one({"_type": "GAttribute", 'subject': ObjectId(every._id), 'attribute_type':ObjectId(GST_one._id)})
        cite=gst_attribute.object_value
        dict1 = {'name': every.name, 'cite': cite}
        list_entry.append(dict1)
      dict2[each]=list_entry
      response_dict.append(dict2)

  return StreamingHttpResponse(json.dumps(response_dict))

@get_execution_time
def get_author_set_users(request, group_id):
    '''
    This ajax function will give all users present in node's author_set field
    '''
    user_list = []
    can_remove = False

    if request.is_ajax():
        _id = request.GET.get('_id',"")
        node = node_collection.one({'_id':ObjectId(_id)})
        # course_name = ""
        # rt_has_course = node_collection.one({'_type':'RelationType', 'name':'has_course'})
        # if rt_has_course and node._id:
        #     course = triple_collection.one({"_type": "GRelation", 'right_subject':node._id, 'relation_type':rt_has_course._id})
        #     if course:
        #         course_name = node_collection.one({'_id':ObjectId(course.subject)}).name
        if node.created_by == request.user.id:
            can_remove = True
        if node.author_set:
            user_list = User.objects.filter(id__in=node.author_set).order_by('id')
            # for each in node.author_set:
            #     user_list.append(User.objects.get(id = each))
            return render_to_response("ndf/refresh_subscribed_users.html",
                                       {
                                       "user_list":user_list,'can_remove':can_remove,'node_id':node._id,
                                       # 'course_name':course_name
                                       },
                                       context_instance=RequestContext(request)
            )
        else:
            return StreamingHttpResponse("Empty")
    else:
        return StreamingHttpResponse("Invalid ajax call")


@login_required
@get_execution_time
def remove_user_from_author_set(request, group_id):
    '''
    This ajax function remove the user from athor_set
    '''
    user_list = []
    can_remove = False
    if request.is_ajax():
        _id = request.GET.get('_id',"")
        user_id = int(request.GET.get('user_id',""))
        node = node_collection.one({'_id':ObjectId(_id)})
        if node.created_by == request.user.id:
            node.author_set.remove(user_id)
            can_remove = True
            node.save(groupid=group_id)

            if node.author_set:
                for each in node.author_set:
                    user_list.append(User.objects.get(id = each))
            return render_to_response("ndf/refresh_subscribed_users.html",
                                      {"user_list":user_list,'can_remove':can_remove,'node_id':node._id},
                                      context_instance=RequestContext(request)
            )
        else:
            return StreamingHttpResponse("You are not authorised to remove user")
    else:
        return StreamingHttpResponse("Invalid Ajax call")

@get_execution_time
def get_filterd_user_list(request, group_id):
    '''
    This function will return (all user's) - (subscribed user for perticular group)
    '''
    user_list = []
    if request.is_ajax():
        _id = request.GET.get('_id',"")
        node = node_collection.one({'_id':ObjectId(_id)})
        all_users_list =  [each.username for each in User.objects.all()]
        if node._type == 'Group':
            for each in node.author_set:
                user_list.append(User.objects.get(id = each).username)

        filtered_users = list(set(all_users_list) - set(user_list))
        return HttpResponse(json.dumps(filtered_users))

@get_execution_time
def search_tasks(request, group_id):
    '''
    This function will return (all task's)
    '''
    user_list = []
    app_id = node_collection.find_one({'_type':"GSystemType", "name":"Task"})
    if request.is_ajax():
        term = request.GET.get('term',"")
        task_nodes = node_collection.find({
                                          'member_of': {'$all': [app_id._id]},
					  'name': {'$regex': term, '$options': 'i'},
                                          'group_set': {'$all': [ObjectId(group_id)]},
                                          'status': {'$nin': ['HIDDEN']}
                                      }).sort('last_update', -1)
	for each in task_nodes :
		user_list.append({"label":each.name,"value":each.name,"id":str(each._id)})
        return HttpResponse(json.dumps(user_list))
    else:
	raise Http404

@get_execution_time
def get_group_member_user(request, group_id):
  """Returns member(s) of the group excluding (group-admin(s)) in form of
  dictionary that consists of key-value pair:

  key: Primary key from Django's User table
  value: User-name of that User record
  """
  user_list = {}
  group = node_collection.find_one({'_id': ObjectId(group_id)})
  if request.is_ajax():
    if group.author_set:
      for each in group.author_set:
        user_list[each] = User.objects.get(id=each).username
    return HttpResponse(json.dumps(user_list))

  else:
    raise Http404

@get_execution_time
def annotationlibInSelText(request, group_id):
  """
  This view parses the annotations field of the currently selected node_id and evaluates if entry corresponding this selectedText already exists.
  If it does, it appends the comment to this entry else creates a new one.

  Arguments:
  group_id - ObjectId of the currently selected group
  obj_id - ObjectId of the currently selected node_id
  comment - The comment added by user
  selectedText - text for which comment was added

 Returns:
  The updated annoatations field
  """

  obj_id = str(request.POST["node_id"])
  sg_obj = node_collection.one({"_id":ObjectId(obj_id)})

  comment = request.POST ["comment"]
  comment = json.loads(comment)
  comment_modified = {
                        'authorAvatarUrl' : comment['authorAvatarUrl'],
                        'authorName'      : comment['authorName'],
                        'comment'         : comment['comment']
  }
  selectedText = request.POST['selectedText']

  # check if annotations for this text already exist!
  flag = False

  for entry in sg_obj.annotations:
    if (entry['selectedText'].lower() == selectedText.lower()):
      entry['comments'].append(comment_modified)
      flag = True
      break

  if(not(flag)):
    comment_list = []
    comment_list.append(comment_modified)
    ann = {
          'selectedText' : selectedText,
          'sectionId'    : str(comment['sectionId']),
          'comments'     : comment_list
    }
    sg_obj.annotations.append(ann)

  sg_obj.save(groupid=group_id)

  return HttpResponse(json.dumps(sg_obj.annotations))


@get_execution_time
def delComment(request, group_id):
  '''
  Delete comment from thread
  '''
  return HttpResponse("comment deleted")


# Views related to MIS -------------------------------------------------------------


@get_execution_time
def get_students(request, group_id):
  """
  This view returns list of students along with required data based on selection criteria
  to student_data_review.html

  Arguments:
  group_id - ObjectId of the currently selected group

  Returns:
  A dictionary consisting of following key-value pairs:-
  success - Boolean giving the state of ajax call
  message - Basestring giving the error/information message
  """
  response_dict = {'success': False, 'message': ""}
  all_students_text = ""
  group_name, group_id = get_group_name_id(group_id)
  try:
    if request.is_ajax() and request.method == "POST":
      groupid = request.POST.get("groupid", None)
      app_id = request.POST.get("app_id", None)
      app_set_id = request.POST.get("app_set_id", None)
      stud_reg_year = str(request.POST.get("reg_year", None))
      university_id = request.POST.get("student_belongs_to_university",None)
      college_id = request.POST.get("student_belongs_to_college",None)

      person_gst = node_collection.one({'_type': "GSystemType", 'name': "Student"}, {'name': 1, 'type_of': 1})

      widget_for = []
      query = {}
      person_gs = node_collection.collection.GSystem()
      person_gs.member_of.append(person_gst._id)
      person_gs.get_neighbourhood(person_gs.member_of)
      # university_gst = node_collection.one({'_type': "GSystemType", 'name': "University"})
      mis_admin = node_collection.one({"_type": "Group", "name": "MIS_admin"}, {"_id": 1})

      # univ_cur = node_collection.find({"member_of":university_gst._id,'group_set':mis_admin._id},{'name':1,"_id":1})

      # rel_univ = node_collection.one({'_type': "RelationType", 'name': "student_belongs_to_university"}, {'_id': 1})
      # rel_colg = node_collection.one({'_type': "RelationType", 'name': "student_belongs_to_college"}, {'_id': 1})
      attr_deg_yr = node_collection.one({'_type': "AttributeType", 'name': "degree_year"}, {'_id': 1})

      widget_for = ["name",
                    # rel_univ._id,
                    # rel_colg._id,
                    attr_deg_yr._id
                  ]
                  #   'status'
                  # ]
      widget_for = get_widget_built_up_data(widget_for, person_gs)

      # Fetch field(s) from POST object
      # if request.POST.has_key("student_belongs_to_university"):
      #   university_id = query_data = request.POST.get("student_belongs_to_university", "")
      for each in widget_for:
        field_name = each["name"]

        if each["_type"] == "BaseField":
          if field_name in request.POST:
            query_data = request.POST.get(field_name, "")
            query_data = parse_template_data(each["data_type"], query_data)
            if field_name == "name":
              query.update({field_name: {'$regex': query_data, '$options': "i"}})
            else:
              query.update({field_name: query_data})

        elif each["_type"] == "AttributeType":
          if field_name in request.POST:
            query_data = request.POST.get(field_name, "")
            query_data = parse_template_data(each["data_type"], query_data)
            query.update({"attribute_set."+field_name: query_data})

        # elif each["_type"] == "RelationType":
        #   if request.POST.has_key(field_name):
        #     print field_name,"\n\n"
        #     query_data = request.POST.get(field_name, "")
        #     query_data = parse_template_data(each["data_type"], query_data, field_instance=each)
        #     print query_data,"\n\n"

        #     if field_name == "student_belongs_to_university":
        #       university_id = query_data
        #     else:
        #       query.update({"relation_set."+field_name: query_data})

      student = node_collection.one({'_type': "GSystemType", 'name': "Student"}, {'_id': 1})
      query["member_of"] = student._id

      date_lte = datetime.datetime.strptime("31/12/" + stud_reg_year, "%d/%m/%Y")
      date_gte = datetime.datetime.strptime("1/1/" + stud_reg_year, "%d/%m/%Y")
      query["attribute_set.registration_date"] = {'$gte': date_gte, '$lte': date_lte}
      college_groupid = None
      if college_id:
        # Get selected college's groupid, where given college should belongs to MIS_admin group
        college_groupid = node_collection.one({'_id': ObjectId(college_id), 'group_set': mis_admin._id, 'relation_set.has_group': {'$exists': True}},
                                              {'relation_set.has_group': 1, 'name': 1}
        )
        response_dict["college"] = college_groupid.name

      if college_groupid:
        for each in college_groupid.relation_set:
          if "has_group" in each.keys():
            college_groupid = each["has_group"][0]
            break
      else:
        college_groupid = None

      groupid = ObjectId(groupid)
      group_set_to_check = []

      if groupid == mis_admin._id:
        # It means group is either a college group or MIS_admin group
        # In either case append MIS_admin group's ObjectId
        # and if college_groupid exists, append it's ObjectId too!
        if college_groupid:
          group_set_to_check.append(college_groupid)
        else:
          group_set_to_check.append(mis_admin._id)

      else:
        # Otherwise, append given group's ObjectId
        group_set_to_check.append(groupid)
      university_id = None
      if university_id:
        university_id = ObjectId(university_id)
        university = node_collection.one({'_id': university_id}, {'name': 1})
        if university:
          response_dict["university"] = university.name
          query.update({'relation_set.student_belongs_to_university': university_id})

      query.update({'group_set': {'$in': group_set_to_check}})
      query.update({'status': u"PUBLISHED"})
      rec = node_collection.collection.aggregate([{'$match': query},
                                  {'$project': {'_id': 0,
                                                'stud_id': '$_id',
                                                'Enrollment Code': '$attribute_set.enrollment_code',
                                                'Name': '$name',
                                                # 'First Name': '$attribute_set.first_name',
                                                # 'Middle Name': '$attribute_set.middle_name',
                                                # 'Last Name': '$attribute_set.last_name',
                                                'Reg# Date': '$attribute_set.registration_date',
                                                'Gender': '$attribute_set.gender',
                                                'Birth Date': '$attribute_set.dob',
                                                'Religion': '$attribute_set.religion',
                                                'Email ID': '$attribute_set.email_id',
                                                'Languages Known': '$attribute_set.languages_known',
                                                'Caste': '$relation_set.student_of_caste_category',
                                                'Contact Number (Mobile)': '$attribute_set.mobile_number',
                                                'Alternate Number / Landline': '$attribute_set.alternate_number',
                                                'House / Street': '$attribute_set.house_street',
                                                'Village': '$attribute_set.village',
                                                'Taluka': '$attribute_set.taluka',
                                                'Town / City': '$attribute_set.town_city',
                                                'District': '$relation_set.person_belongs_to_district',
                                                'State': '$relation_set.person_belongs_to_state',
                                                'Pin Code': '$attribute_set.pin_code',
                                                'Year of Passing 12th Standard': '$attribute_set.12_passing_year',
                                                'Degree Name / Highest Degree': '$attribute_set.degree_name',
                                                'Year of Study': '$attribute_set.degree_year',
                                                'Stream / Degree Specialization': '$attribute_set.degree_specialization',
                                                'College Enrolment Number / Roll No': '$attribute_set.college_enroll_num',
                                                'College ( Graduation )': '$relation_set.student_belongs_to_college',
                                                'University': '$relation_set.student_belongs_to_university',
                                                'Are you registered for NSS?': '$attribute_set.is_nss_registered'
                                  }},
                                  {'$sort': {'Enrollment Code': 1}}
            ])
      json_data = []
      filename = ""
      column_header = []
      if len(rec["result"]):
        for each_dict in rec["result"]:
          new_dict = {}

          for each_key in each_dict:
            if each_dict[each_key]:
              if type(each_dict[each_key]) == list:
                data = each_dict[each_key][0]
              else:
                data = each_dict[each_key]

              if type(data) == list:
                # Perform parsing
                if type(data) == list:
                  # Perform parsing
                  if type(data[0]) in [unicode, basestring, int]:
                    new_dict[each_key] = ', '.join(str(d) for d in data)

                  elif type(data[0]) in [ObjectId]:
                    # new_dict[each_key] = str(data)
                    d_list = []
                    for oid in data:
                      d = node_collection.one({'_id': oid}, {'name': 1})
                      d_list.append(str(d.name))
                    new_dict[each_key] = ', '.join(str(n) for n in d_list)

                elif type(data) == datetime.datetime:
                  new_dict[each_key] = data.strftime("%d/%m/%Y")

                elif type(data) == long:
                  new_dict[each_key] = str(data)

                elif type(data) == bool:
                  if data:
                    new_dict[each_key] = "Yes"
                  else:
                    new_dict[each_key] = "No"

                else:
                  new_dict[each_key] = str(data)

              else:
                # Perform parsing
                if type(data) == list:
                  # Perform parsing
                  if type(data[0]) in [unicode, basestring, int]:
                    new_dict[each_key] = ', '.join(str(d) for d in data)
                  elif type(data[0]) in [ObjectId]:
                    new_dict[each_key] = str(data)

                elif type(data) == datetime.datetime:
                  new_dict[each_key] = data.strftime("%d/%m/%Y")

                elif type(data) == long:
                  new_dict[each_key] = str(data)

                elif type(data) == bool:
                  if data:
                    new_dict[each_key] = "Yes"
                  else:
                    new_dict[each_key] = "No"

                else:
                  new_dict[each_key] = str(data)

            else:
              new_dict[each_key] = ""

          json_data.append(new_dict)

        # Start: CSV file processing -------------------------------------------
        column_header = [u"Enrollment Code", u'Name', u'Reg# Date', u'Gender', u'Birth Date', u'Religion', u'Email ID', u'Languages Known', u'Caste', u'Contact Number (Mobile)', u'Alternate Number / Landline', u'House / Street', u'Village', u'Taluka', u'Town / City', u'District', u'State', u'Pin Code', u'Year of Passing 12th Standard', u'Degree Name / Highest Degree', u'Year of Study', u'Stream / Degree Specialization', u'College Enrolment Number / Roll No', u'College ( Graduation )', u'Are you registered for NSS?','University']

        t = time.strftime("%c").replace(":", "_").replace(" ", "_")
        filename = "csv/" + "student_registration_data_" + t + ".csv"
        filepath = os.path.join(STATIC_ROOT, filename)
        filedir = os.path.dirname(filepath)
        if not os.path.exists(filedir):
          os.makedirs(filedir)
        with open(filepath, 'wb') as csv_file:
          fw = csv.DictWriter(csv_file, delimiter=',', fieldnames=column_header)
          fw.writerow(dict((col,col) for col in column_header))
          for row in json_data:
            v = {}
            v["stud_id"] = row.pop("stud_id")
            fw.writerow(row)
            row.update(v)
        # End: CSV file processing --------------------------------------------

      # Column headers to be displayed on html
      column_headers = [
          #('University', 'University'),
          ('College ( Graduation )', 'College'),
          ("Name", "Name"),
          ("Enrollment Code", "Enr Code"),
          ("Email ID", "Email ID"),
          ('Year of Study', 'Year of Study'),
          ('Contact Number (Mobile)', 'Phone'),
          ('Degree Name / Highest Degree', 'Degree'),
          ('House / Street', 'Street')
      ]
      # college = node_collection.one({'_id': ObjectId(college_id)}, {"name": 1})
      students_count = len(json_data)
      response_dict["success"] = True
      response_dict["groupid"] = groupid
      response_dict["app_id"] = app_id
      response_dict["app_set_id"] = app_set_id
      response_dict["filename"] = filename
      response_dict["students_count"] = students_count
      response_dict["column_headers"] = column_headers
      response_dict["students_data_set"] = json_data
      return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

    else:
      error_message = "StudentFindError: Either not an ajax call or not a POST request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

  except OSError as oe:
    error_message = "StudentFindError: " + str(oe) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

  except Exception as e:
    error_message = "StudentFindError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))


@get_execution_time
def get_statewise_data(request, group_id):
    """
    This view returns a download link of CSV created consisting of students statistical data based on degree_year for each college.

    Arguments:
    group_id - ObjectId of the currently selected group

    Returns:
    A dictionary consisting of following key-value pairs:-
    success - Boolean giving the state of ajax call
    message - Basestring giving the error/information message
    download_link - file path of CSV created
    """
    response_dict = {'success': False, 'message': ""}

    try:
        if request.is_ajax() and request.method == "GET":
            # Fetching selected state's name
            state_val = request.GET.get("state_val", None)

            mis_admin = node_collection.one(
                {'_type': "Group", 'name': "MIS_admin"},
                {'_id': 1}
            )

            # Fetching selected state's node
            state_gst = node_collection.one(
                {'_type': "GSystemType", 'name': "State"}
            )
            state_gs = node_collection.one(
                {
                    'member_of': state_gst._id,
                    'name': {'$regex': state_val, '$options': "i"},
                    'group_set': mis_admin._id
                }
            )

            # Fetching universities belonging to that state
            university_gst = node_collection.one(
                {'_type': "GSystemType", 'name': "University"}
            )
            university_cur = node_collection.find(
                {
                    'member_of': university_gst._id,
                    'group_set': mis_admin._id,
                    'relation_set.organization_belongs_to_state': state_gs._id
                },
                {
                    'name': 1,
                    'relation_set.affiliated_college': 1
                }
            ).sort('name', 1)

            student_gst = node_collection.one(
                {'_type': "GSystemType", 'name': "Student"}
            )

            university_wise_data = {}
            # Fetching university-wise data
            for each_univ in university_cur:
                university_wise_data[each_univ.name] = {}

                # Fetching college(s) affiliated to given university
                colleges_id_list = []
                for rel in each_univ.relation_set:
                    if rel and "affiliated_college" in rel:
                        colleges_id_list = rel["affiliated_college"]
                        break

                # Fetching college-wise data
                college_cur = node_collection.find(
                    {'_id': {'$in': colleges_id_list}}
                ).sort('name', 1)

                for each_college in college_cur:
                    university_wise_data[each_univ.name][each_college.name] = {}
                    rec = node_collection.collection.aggregate([
                        {
                            '$match': {
                                'member_of': student_gst._id,
                                'relation_set.student_belongs_to_college': each_college._id,
                                # 'attribute_set.registration_date': {
                                #     '$gte': date_gte, '$lte': date_lte
                                # },
                                'status': u"PUBLISHED"
                            }
                        },
                        {
                            '$group': {
                                '_id': {
                                    'College': '$each_college.name',
                                    'Degree Year': '$attribute_set.degree_year'
                                },
                                'No of students': {'$sum': 1}
                            }
                        }
                    ])

                    data = {}
                    for res in rec["result"]:
                        if res["_id"]["Degree Year"]:
                            data[res["_id"]["Degree Year"][0]] = \
                                res["No of students"]

                    if "I" not in data:
                        data["I"] = 0
                    if "II" not in data:
                        data["II"] = 0
                    if "III" not in data:
                        data["III"] = 0

                    data["Total"] = data["I"] + data["II"] + data["III"]

                    university_wise_data[each_univ.name][each_college.name] = data

            response_dict["success"] = True
            response_dict["university_wise_data"] = university_wise_data
            return HttpResponse(json.dumps(response_dict))

        else:
            error_message = "CollegeSummaryDataError: Either not an ajax call or not a POST request!!!"
            response_dict["message"] = error_message
            return HttpResponse(json.dumps(response_dict))

    except OSError as oe:
        error_message = "CollegeSummaryDataError: " + str(oe) + "!!!"
        response_dict["message"] = error_message
        return HttpResponse(json.dumps(response_dict))

    except Exception as e:
        error_message = "CollegeSummaryDataError: " + str(e) + "!!!"
        response_dict["message"] = error_message
        return HttpResponse(json.dumps(response_dict))

@get_execution_time
def get_college_wise_students_data(request, group_id):
  """
  This view returns a download link of CSV created consisting of students statistical data based on degree_year for each college.

  Arguments:
  group_id - ObjectId of the currently selected group

  Returns:
  A dictionary consisting of following key-value pairs:-
  success - Boolean giving the state of ajax call
  message - Basestring giving the error/information message
  download_link - file path of CSV created
  """
  response_dict = {'success': False, 'message': ""}
  all_students_text = ""

  try:
    if request.is_ajax() and request.method == "GET":
      groupid = request.GET.get("groupid", None)

      mis_admin = node_collection.one({'_type': "Group", 'name': "MIS_admin"}, {'_id': 1})
      college_gst = node_collection.one({'_type': "GSystemType", 'name': "College"}, {'_id': 1})
      student = node_collection.one({'_type': "GSystemType", 'name': "Student"})

      current_year = str(datetime.datetime.today().year)

      date_gte = datetime.datetime.strptime("1/1/" + current_year, "%d/%m/%Y")
      date_lte = datetime.datetime.strptime("31/12/" + current_year, "%d/%m/%Y")

      college_cur = node_collection.find({'member_of': college_gst._id, 'group_set': mis_admin._id},
                                         {'_id': 1, 'name': 1, 'relation_set': 1}).sort('name', 1)

      json_data = []

      for i, each in enumerate(college_cur):
        data = {}
        college_group_id = None
        for each_dict in each.relation_set:
          if u"has_group" in each_dict.keys():
            college_group_id = each_dict["has_group"]
            break

        rec = node_collection.collection.aggregate([{'$match': {'member_of': student._id,
                                                'group_set': {'$in': [college_group_id, mis_admin._id]},
                                                'relation_set.student_belongs_to_college': each._id,
                                                'attribute_set.registration_date': {'$gte': date_gte, '$lte': date_lte},
                                                'status': u"PUBLISHED"
                                    }},
                                    {'$group': {
                                      '_id': {'College': '$each.name', 'Degree Year': '$attribute_set.degree_year'},
                                      'No of students': {'$sum': 1}
                                    }}
                                  ])

        data["College"] = each.name
        for res in rec["result"]:
          data[res["_id"]["Degree Year"][0]] = res["No of students"]
        if "I" not in data:
          data["I"] = 0
        if "II" not in data:
          data["II"] = 0
        if "III" not in data:
          data["III"] = 0

        data["Total"] = data["I"] + data["II"] + data["III"]

        json_data.append(data)

      t = time.strftime("%c").replace(":", "_").replace(" ", "_")
      filename = "csv/" + "college_wise_student_data_" + t + ".csv"
      filepath = os.path.join(STATIC_ROOT, filename)
      filedir = os.path.dirname(filepath)

      if not os.path.exists(filedir):
        os.makedirs(filedir)

      column_header = [u"College", u"Program Officer", u"I", u"II", u"III", u"Total"]

      PO = {
        "Agra College": ["Mr. Rajaram Yadav"],
        "Arts College Shamlaji": ["Mr. Ashish Varia"],
        "Baba Bhairabananda Mahavidyalaya": ["Mr. Mithilesh Kumar"],
        "Balugaon College": ["Mr. Pradeep Pradhan"],
        "City Women's College": ["Ms. Rajni Sharma"],
        "Comrade Godavari Shamrao Parulekar College of Arts, Commerce & Science": ["Mr. Rahul Sable"],
        "Faculty of Arts": ["Mr. Jokhim", "Ms. Tusharika Kumbhar"],
        "Gaya College": ["Ms. Rishvana Sheik"],
        "Govt. M. H. College of Home Science & Science for Women, Autonomous": [],
        "Govt. Mahakoshal Arts and Commerce College": ["Ms. Davis Yadav"],
        "Govt. Mahaprabhu Vallabhacharya Post Graduate College": ["Mr. Gaurav Sharma"],
        "Govt. Rani Durgavati Post Graduate College": ["Mr. Asad Ullah"],
        "Jamshedpur Women's College": ["Mr. Arun Agrawal"],
        "Kalyan Post Graduate College": ["Mr. Praveen Kumar"],
        "Kamla Nehru College for Women": ["Ms. Tusharika Kumbhar", "Ms. Thaku Pujari"],
        "L. B. S. M. College": ["Mr. Charles Kindo"],
        "Mahila College": ["Mr. Sonu Kumar"],
        "Marwari College": ["Mr. Avinash Anand"],
        "Matsyodari Shikshan Sanstha's Arts, Commerce & Science College": ["Ms. Jyoti Kapale"],
        "Nirmala College": [],
        "Ranchi College": [],
        "Ranchi Women's College": ["Mr. Avinash Anand"],
        "Shiv Chhatrapati College": ["Mr. Swapnil Sardar"],
        "Shri & Smt. PK Kotawala Arts College": ["Mr. Sawan Kumar"],
        "Shri VR Patel College of Commerce": ["Mr. Sushil Mishra"],
        "Sree Narayana Guru College of Commerce": ["Ms. Bharti Bhalerao"],
        "Sri Mahanth Shatanand Giri College": ["Mr. Narendra Singh"],
        "St. John's College": ["Mr. Himanshu Guru"],
        "The Graduate School College For Women": ["Mr. Pradeep Gupta"],
        "Vasant Rao Naik Mahavidyalaya": ["Mr. Dayanand Waghmare"],
        "Vivekanand Arts, Sardar Dalip Singh Commerce & Science College": ["Mr. Anis Ambade"]
      }

      with open(filepath, 'wb') as csv_file:
        fw = csv.DictWriter(csv_file, delimiter=',', fieldnames=column_header)
        fw.writerow(dict((col,col) for col in column_header))

        for row in json_data:
          if row[u"College"] not in PO or not PO[row[u"College"]]:
            row[u"Program Officer"] = "Not assigned yet"
          else:
            row[u"Program Officer"] = ", ".join(PO[row[u"College"]])
          fw.writerow(row)

      response_dict["success"] = True
      response_dict["download_link"] = (STATIC_URL + filename)

      return HttpResponse(json.dumps(response_dict))

    else:
      error_message = "CollegeSummaryDataError: Either not an ajax call or not a POST request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict))

  except OSError as oe:
    error_message = "CollegeSummaryDataError: " + str(oe) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

  except Exception as e:
    error_message = "CollegeSummaryDataError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

@get_execution_time
def set_user_link(request, group_id):
  """
  This view creates a relationship (has_login) between the given node (node_id) and the author node (username);
  and also subscribes the user to his/her respective college group

  Arguments:
  group_id - ObjectId of the currently selected group
  node_id - ObjectId of the currently selected node_id
  username - Username of the user

  Returns:
  A dictionary consisting of following key:-
  result - a bool variable indicating whether link is created or not and subscribed to group or not
  message - a string variable giving the status of the link (also reason if any error occurs)
  """
  gr_node = None

  try:
    if request.is_ajax() and request.method =="POST":
      node_id = request.POST.get("node_id", "")
      username = request.POST.get("username", "")

      # Creating link between user-node and it's login credentials
      author = node_collection.one({'_type': "Author", 'name': unicode(username)}, {'created_by': 1})
      rt_has_login = node_collection.one({'_type': "RelationType", 'name': u"has_login"})

      gr_node = create_grelation(node_id, rt_has_login, author._id)

      if gr_node:
        # Assigning the userid to respective private college groups's author_set,
        # i.e. making user, member of college group to which he/she belongs
        # Only after the given user's link (i.e., has_login relation) gets created
        node = node_collection.one({'_id': ObjectId(node_id)}, {'member_of': 1})
        node_type = node.member_of_names_list

        has_group = node_collection.one({'_type': "RelationType", 'name': "has_group"}, {'_id': 1})

        if "Student" in node_type:
          student_belonds_to_college = node_collection.one({'_type': "RelationType", 'name': "student_belongs_to_college"}, {'_id': 1})

          colleges = triple_collection.find({
              '_type': "GRelation", 'subject': node._id,
              'relation_type': student_belonds_to_college._id
          })

          for each in colleges:
            g = triple_collection.one({'_type': "GRelation", 'subject': each.right_subject, 'relation_type': has_group._id})
            node_collection.collection.update({'_id': g.right_subject}, {'$addToSet': {'author_set': author.created_by}}, upsert=False, multi=False)

        elif "Voluntary Teacher" in node_type:
          trainer_of_college = node_collection.one({'_type': "RelationType", 'name': "trainer_of_college"}, {'_id': 1})

          colleges = triple_collection.find({'_type': "GRelation", 'subject': node._id, 'relation_type': trainer_of_college._id})

          for each in colleges:
            g = triple_collection.one({'_type': "GRelation", 'subject': each.right_subject, 'relation_type': has_group._id})
            node_collection.collection.update({'_id': g.right_subject}, {'$addToSet': {'author_set': author.created_by}}, upsert=False, multi=False)


      return HttpResponse(json.dumps({'result': True, 'message': " Link successfully created. \n\n Also subscribed to respective college group(s)."}))

    else:
      error_message = " UserLinkSetUpError: Either not an ajax call or not a POST request!!!"
      return HttpResponse(json.dumps({'result': False, 'message': " Link not created - Something went wrong in ajax call !!! \n\n Please contact system administrator."}))

  except Exception as e:
    error_message = "\n UserLinkSetUpError: " + str(e) + "!!!"
    result = False

    if gr_node:
      # node_collection.collection.remove({'_id': gr_node._id})
      result = True
      error_message = " Link created successfully. \n\n But facing problem(s) in subscribing to respective college group(s)!!!\n Please use group's 'Subscribe members' button to do so !!!"

    else:
      result = False
      error_message = " Link not created - May be invalid username entered !!!"

    return HttpResponse(json.dumps({'result': result, 'message': error_message}))

@get_execution_time
def set_enrollment_code(request, group_id):
  """
  """
  if request.is_ajax() and request.method == "POST":
    return HttpResponse("Five digit code")

  else:
    error_message = " EnrollementCodeError: Either not an ajax call or not a POST request!!!"
    raise Exception(error_message)

@get_execution_time
def get_students_assignments(request, group_id):
  """
  Arguments:
  group_id - ObjectId of the currently selected group

  Returns:
  """
  gr_node = None

  try:
    if request.is_ajax() and request.method =="GET":
      user_id = 0

      if "user_id" in request.GET:
        user_id = int(request.GET.get("user_id", ""))

      # Fetching college group
      college_group = node_collection.one({'_id': ObjectId(group_id)}, {'name': 1, 'tags': 1, 'author_set': 1, 'created_by': 1})
      page_res = node_collection.one({'_type': "GSystemType", 'name': "Page"}, {'_id': 1})
      file_res = node_collection.one({'_type': "GSystemType", 'name': "File"}, {'_id': 1})
      image_res = node_collection.one({'_type': "GSystemType", 'name': "Image"}, {'_id': 1})
      video_res = node_collection.one({'_type': "GSystemType", 'name': "Video"}, {'_id': 1})

      student_list = []

      if user_id:
        # Fetch assignment details of a given student
        student_dict = {}
        num_pages = []
        num_images = []
        num_videos = []
        num_files = []

        # Fetch student's user-group
        user_group = node_collection.one({'_type': "Author", 'created_by': user_id})
        student_dict["username"] = user_group.name

        # Fetch all resources from student's user-group
        resources = node_collection.find({'group_set': user_group._id}, {'name': 1, 'member_of': 1, 'created_at': 1})

        for res in resources:
          if page_res._id in res.member_of:
            num_pages.append(res)

          elif image_res._id in res.member_of:
            num_images.append(res)

          elif video_res._id in res.member_of:
            num_videos.append(res)

          elif file_res._id in res.member_of:
            num_files.append(res)

        student_dict["Pages"] = num_pages
        student_dict["Images"] = num_images
        student_dict["Videos"] = num_videos
        student_dict["Files"] = num_files

        return HttpResponse(json.dumps(student_dict, cls=NodeJSONEncoder))

      else:
        # Fetch assignment details of all students belonging to the college group
        for user_id in college_group.author_set:
          if user_id == college_group.created_by:
            continue

          student_dict = {}
          num_pages = 0
          num_images = 0
          num_videos = 0
          num_files = 0

          # Fetch student's user-group
          user_group = node_collection.one({'_type': "Author", 'created_by': user_id})

          # Fetch student's node from his/her has_login relationship
          student_has_login_rel = triple_collection.one({'_type': "GRelation", 'right_subject': user_group._id})
          student_node = node_collection.one({'_id': student_has_login_rel.subject}, {'name': 1})
          student_dict["Name"] = student_node.name
          student_dict["user_id"] = user_id

          # Fetch all resources from student's user-group
          resources = node_collection.find({'group_set': user_group._id}, {'member_of': 1})

          for res in resources:
            if page_res._id in res.member_of:
              num_pages = num_pages + 1

            elif image_res._id in res.member_of:
              num_images = num_images + 1

            elif video_res._id in res.member_of:
              num_videos = num_videos + 1

            elif file_res._id in res.member_of:
              num_files = num_files + 1

          student_dict["Pages"] = num_pages
          student_dict["Images"] = num_images
          student_dict["Videos"] = num_videos
          student_dict["Files"] = num_files
          student_dict["Total"] = num_pages + num_images + num_videos + num_files

          student_list.append(student_dict)

        # Outside of above for loop

        return render_to_response("ndf/student_statistics.html",
                                  {'node': college_group,'student_list': student_list},
                                  context_instance = RequestContext(request)
                                )

    else:
      error_message = "StudentDataGetError: Invalid ajax call!!!"
      return StreamingHttpResponse(error_message)

  except Exception as e:
    print "\n StudentDataGetError: " + str(e)
    raise Http404(e)

@login_required
@get_execution_time
def get_districts(request, group_id):
  """
  This view fetches district(s) belonging to given state.

  Arguments:
  group_id - ObjectId of the currently selected group
  state_id - ObjectId of the currently selected state`

  Returns:
  A dictionary consisting of following key:-
  districts - a list variable consisting of two elements i.e.,
              first-element: subject (District's ObjectId), second-element: manipulated-name-value (District's name)
  message - a string variable giving the error-message
  """
  gr_node = None

  try:
    if request.is_ajax() and request.method == "GET":
      state_id = request.GET.get("state_id", "")

      # districts -- [first-element: subject (District's ObjectId), second-element: manipulated-name-value (District's name)]
      districts = []

      # Fetching RelationType: District - district_of (name) | has_district (inverse_name) - State
      rt_district_of = node_collection.one({'_type': "RelationType", 'name': "district_of"})

      # Fetching all districts belonging to given state in sorted order by name
      if rt_district_of:
        cur_districts = triple_collection.find({
            '_type': "GRelation", 'right_subject': ObjectId(state_id),
            'relation_type': rt_district_of._id
        }).sort('name', 1)

        if cur_districts.count():
          #loop replaced by a list comprehension
          districts=[[str(d.subject), d.name.split(" -- ")[0]] for d in cur_districts]
        else:
          error_message = "No districts found"
          raise Exception(error_message)

      else:
        error_message = "RelationType (district_of) doesn't exists"
        raise Exception(error_message)

      return HttpResponse(json.dumps(districts))

    else:
      error_message = " DistrictFetchError: Either not an ajax call or not a GET request!!!"
      return HttpResponse(json.dumps({'message': " DistrictFetchError - Something went wrong in ajax call !!! \n\n Please contact system administrator."}))

  except Exception as e:
    error_message = "\n DistrictFetchError: " + str(e) + "!!!"
    return HttpResponse(json.dumps({'message': error_message}))


@login_required
@get_execution_time
def get_affiliated_colleges(request, group_id):
  """
  This view returns list of colleges affiliated to given university.

  Each element of the list is again a list where,
  0th index-element: ObjectId of college
  1st index-element: Name of college

  Arguments:
  group_id - ObjectId of the currently selected group

  Returns:
  A dictionary consisting of following key-value pairs:-
  success - Boolean giving the state of ajax call
  message - Basestring giving the error/information message
  affiliated_colleges - List consisting of affiliated colleges (ObjectIds & names)
  """
  response_dict = {'success': False, 'message': ""}
  all_students_text = ""

  try:
    if request.is_ajax() and request.method == "GET":
      # Fetch field(s) from GET object
      university_id = request.GET.get("university_id", "")
      req_university = None
      req_affiliated_colleges = None
      colg_gst = node_collection.one({'_type': "GSystemType", 'name': "College"})
      # Check whether any field has missing value or not
      if university_id == "":
        error_message = "AffiliatedCollegeFindError: Invalid data (No university selected)!!!"
        raise Exception(error_message)

      if university_id == "ALL":
        req_affiliated_colleges = node_collection.find({'member_of': colg_gst._id}, {'name': 1}).sort('name', 1)

      else:
        # Type-cast fetched field(s) into their appropriate type
        university_id = ObjectId(university_id)

        # Fetch required university
        req_university = node_collection.one({'_id': university_id})

        if not req_university:
          error_message = "AffiliatedCollegeFindError: No university exists with given ObjectId("+university_id+")!!!"
          raise Exception(error_message)

        for each in req_university["relation_set"]:
          if u"affiliated_college" in each.keys():
            req_affiliated_colleges = node_collection.find({'_id': {'$in': each[u"affiliated_college"]}}, {'name': 1}).sort('name', 1)

      req_affiliated_colleges_list = []
      for each in req_affiliated_colleges:
        req_affiliated_colleges_list.append([str(each._id), each.name])

      response_dict["affiliated_colleges"] = req_affiliated_colleges_list

      response_dict["success"] = True
      response_dict["message"] = "This university ("+req_university.name+") has following list of affiliated colleges:"
      for i, each in enumerate(req_affiliated_colleges_list):
        response_dict["message"] += "\n\n " + str(i+1) + ". " + each[1]

      return HttpResponse(json.dumps(response_dict))

    else:
      error_message = "AffiliatedCollegeFindError: Either not an ajax call or not a GET request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict))

  except Exception as e:
    error_message = "AffiliatedCollegeFindError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

@get_execution_time
def get_courses(request, group_id):
    """
    This view returns list of NUSSD-Course(s) belonging to given course type.

    Arguments:
    group_id - ObjectId of the currently selected group
    nussd_course_type - Type of NUSSD Course

    Returns:
    A dictionary consisting of following key-value pairs:-
    success - Boolean giving the state of ajax call
    message - Basestring giving the error/information message
    unset_nc - dictionary consisting of NUSSD-Course(s)
    """
    response_dict = {'success': False, 'message': ""}
    try:
        if request.is_ajax() and request.method == "GET":
            # Fetch field(s) from GET object
            nussd_course_type = request.GET.get("nussd_course_type", "")

            if GSTUDIO_SITE_NAME == "TISS":
                # Check whether any field has missing value or not
                if nussd_course_type == "":
                    error_message = "Invalid data: No data found in any of the " \
                        + "field(s)!!!"
                    raise Exception(error_message)

                mis_admin = node_collection.one(
                    {'_type': "Group", 'name': "MIS_admin"},
                    {'name': 1}
                )
                if not mis_admin:
                    # If not found, throw exception
                    error_message = "'MIS_admin' (Group) doesn't exists... " \
                        + "Please create it first!"
                    raise Exception(error_message)

                # Fetch "NUSSD Course" GSystemType
                nussd_course_gt = node_collection.one(
                    {'_type': "GSystemType", 'name': "NUSSD Course"}
                )
                if not nussd_course_gt:
                    # If not found, throw exception
                    error_message = "'NUSSD Course' (GSystemType) doesn't exists... " \
                        + "Please create it first!"
                    raise Exception(error_message)
            else:
                # Fetch "Course" GSystemType
                nussd_course_gt = node_collection.one(
                    {'_type': "GSystemType", 'name': "Course"}
                )
                mis_admin = node_collection.one(
                    {'_id': ObjectId(group_id)},
                    {'name': 1}
                )

            # Type-cast fetched field(s) into their appropriate type
            nussd_course_type = unicode(nussd_course_type)

            # Fetch registered NUSSD-Courses of given type
            nc_cur = node_collection.find(
                {
                    'member_of': nussd_course_gt._id,
                    'group_set': mis_admin._id,
                    'attribute_set.nussd_course_type': nussd_course_type
                },
                {'name': 1}
            )

            nc_dict = {}
            if nc_cur.count():
                # If found, append them to a dict
                for each in nc_cur:
                    nc_dict[str(each._id)] = each.name

                response_dict["success"] = True
                response_dict["unset_nc"] = nc_dict

            else:
                response_dict["message"] = "No " + nussd_course_type + " type of course exists." \
                    + " Please register"
                response_dict["success"] = False

            return HttpResponse(json.dumps(response_dict))

        else:
            error_message = "AnnouncedCourseError: Either not an ajax call or" \
                " not a GET request!!!"
            response_dict["message"] = error_message
            return HttpResponse(json.dumps(response_dict))
    except Exception as e:
        error_message = "AnnouncedCourseError: " + str(e) + "!!!"
        response_dict["message"] = error_message
        return HttpResponse(json.dumps(response_dict))

@get_execution_time
def get_announced_courses_with_ctype(request, group_id):
    """
    This view returns list of announced-course(s) that match given criteria
    along with NUSSD-Course(s) for which match doesn't exists.

    Arguments:
    group_id - ObjectId of the currently selected group
    nussd_course_type - Type of NUSSD course

    Returns:
    A dictionary consisting of following key-value pairs:-
    acourse_ctype_list - list consisting of announced-course(s)
         and/or NUSSD-Courses [if match not found]
    """
    response_dict = {'success': False, 'message': ""}
    try:
        if request.is_ajax() and request.method == "GET":
            # Fetch field(s) from GET object
            nussd_course_type = request.GET.get("nussd_course_type", "")
            ann_course_type = request.GET.get("ann_course_type", "0")
            acourse_ctype_list = []
            ac_of_colg = []
            start_enroll = ""
            end_enroll = ""
            query = {}
            # curr_date = datetime.datetime.now()

            # Fetch "Announced Course" GSystemType
            announced_course_gt = node_collection.one(
                {'_type': "GSystemType", 'name': "Announced Course"}
            )
            if not announced_course_gt:
                # If not found, throw exception
                error_message = "Announced Course (GSystemType) doesn't " \
                    + "exists... Please create it first!"
                raise Exception(error_message)

            mis_admin = node_collection.one(
                {'_type': "Group", 'name': "MIS_admin"}
            )

            # Type-cast fetched field(s) into their appropriate type
            nussd_course_type = unicode(nussd_course_type)
            ann_course_type = int(ann_course_type)

            if ann_course_type == 1:
                # Return all Announced Course(s) for which enrollment not started yet
                query = {
                    "member_of": announced_course_gt._id,
                    "group_set": ObjectId(mis_admin._id),
                    "status": "PUBLISHED",
                    "attribute_set.nussd_course_type": nussd_course_type,
                    "attribute_set.ann_course_closure": u"Open",
                    "relation_set.course_has_enrollment": {"$exists": False}
                }

                college = {}
                course = {}
                ac_data_set = []
                records_list = []

                if nussd_course_type == "Foundation Course":
                    rec = node_collection.collection.aggregate([{
                        "$match": {
                            "member_of": announced_course_gt._id,
                            "group_set": ObjectId(mis_admin._id),
                            "status": "PUBLISHED",
                            "attribute_set.nussd_course_type": nussd_course_type,
                            "attribute_set.ann_course_closure": u"Open",
                            "relation_set.course_has_enrollment": {"$exists": False}
                        }
                    }, {
                        '$group': {
                            "_id": {
                                "start_time": "$attribute_set.start_time",
                                "end_time": "$attribute_set.end_time",
                                'college': '$relation_set.acourse_for_college'
                            },
                            "foundation_course": {"$addToSet": {'ac_id': "$_id", 'course': '$relation_set.announced_for', 'created_at': "$created_at"}},
                            "fc_ann_ids": {"$addToSet": "$_id"}
                        }
                    }, {
                        '$sort': {'created_at': 1}
                    }])

                    records_list = rec["result"]
                    if records_list:
                        for each in records_list:
                            newrec = {}
                            if each['_id']["college"]:
                                colg_id = each['_id']["college"][0][0]
                                if colg_id not in college:
                                    c = node_collection.one({"_id": colg_id}, {"name": 1, "relation_set.college_affiliated_to": 1,"attribute_set.enrollment_code":1})
                                    newrec[u"college"] = c.name
                                    newrec[u"college_id"] = c._id
                                    newrec[u"created_at"] = each["foundation_course"][0]["created_at"]
                                    college[colg_id] = {}
                                    college[colg_id]["name"] = newrec[u"college"]
                                    for rel in c.relation_set:
                                        if rel and "college_affiliated_to" in rel:
                                            univ_id = rel["college_affiliated_to"][0]
                                            u = node_collection.one({"_id": univ_id}, {"name": 1})
                                            each.update({"university": u.name})
                                            college[colg_id]["university"] = each["university"]
                                            college[colg_id]["university_id"] = u._id
                                            newrec[u"university"] = u.name
                                            newrec[u"university_id"] = u._id
                                else:
                                    newrec["college"] = college[colg_id]["name"]
                                    newrec["college_id"] = ObjectId(colg_id)
                                    newrec["university_id"] = college[colg_id]["university_id"]
                                    newrec["university"] = college[colg_id]["university"]

                            newrec[u"course"] = "Foundation Course"
                            newrec[u"ac_id"] = each["fc_ann_ids"]
                            newrec[u"name"] = "Foundation_Course_" + c["attribute_set"][0]["enrollment_code"] + "_" + each["_id"]["start_time"][0].strftime('%Y') + "_" + each["_id"]["end_time"][0].strftime('%Y')
                            ac_data_set.append(newrec)

                else:
                    rec = node_collection.collection.aggregate([
                        {
                            '$match': query
                        }, {
                            '$project': {
                                '_id': 0,
                                'ac_id': "$_id",
                                'name': '$name',
                                'course': '$relation_set.announced_for',
                                'college': '$relation_set.acourse_for_college',
                                'created_at': "$created_at"
                            }
                        },
                        {
                            '$sort': {'created_at': 1}
                        }
                    ])

                    records_list = rec["result"]
                    if records_list:
                        for each in rec["result"]:
                            if each["college"]:
                                colg_id = each["college"][0][0]
                                if colg_id not in college:
                                    c = node_collection.one({"_id": colg_id}, {"name": 1, "relation_set.college_affiliated_to": 1})
                                    each["college"] = c.name
                                    each["college_id"] = c._id
                                    college[colg_id] = {}
                                    college[colg_id]["name"] = each["college"]
                                    for rel in c.relation_set:
                                        if rel and "college_affiliated_to" in rel:
                                            univ_id = rel["college_affiliated_to"][0]
                                            u = node_collection.one({"_id": univ_id}, {"name": 1})
                                            each.update({"university": u.name})
                                            college[colg_id]["university"] = each["university"]
                                            college[colg_id]["university_id"] = u._id
                                            each["university_id"] = u._id
                                else:
                                    each["college"] = college[colg_id]["name"]
                                    each["college_id"] = colg_id
                                    each.update({"university": college[colg_id]["university"]})
                                    each.update({"university_id": college[colg_id]["university_id"]})

                            if each["course"]:
                                course_id = each["course"][0][0]
                                if course_id not in course:
                                    each["course"] = node_collection.one({"_id": course_id}).name
                                    course[course_id] = each["course"]
                                else:
                                    each["course"] = course[course_id]

                            ac_data_set.append(each)

                column_headers = [
                    ("name", "Announced Course Name"),
                    ("course", "Course Name"),
                    ("college", "College"),
                    ("university", "University")
                ]

                if records_list:
                    # If Announced Course(s) records found
                    response_dict["column_headers"] = column_headers
                    response_dict["ac_data_set"] = ac_data_set
                else:
                    # Else, where No Announced Course exist
                    response_dict["ac_data_set"] = records_list
                    response_dict["message"] = "No Announced Course found of selected type (" + nussd_course_type + ") !"

                response_dict["success"] = True
                return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

            if(ObjectId(group_id) == mis_admin._id):
                ac_cur = node_collection.find({
                    'member_of': announced_course_gt._id,
                    'group_set': ObjectId(group_id),
                    'attribute_set.nussd_course_type': nussd_course_type
                }, {
                    "name": 1, "attribute_set": 1, "relation_set": 1
                })

            else:
                colg_gst = node_collection.one(
                    {'_type': "GSystemType", 'name': 'College'}
                )

                # Fetch Courses announced for given college (or college group)
                # Get college node & courses announced for it from
                # college group's ObjectId
                req_colg_id = node_collection.one({
                    'member_of': colg_gst._id,
                    'relation_set.has_group': ObjectId(group_id)
                }, {
                    'relation_set.college_has_acourse': 1
                })

                for rel in req_colg_id.relation_set:
                    if rel and "college_has_acourse" in rel:
                        ac_of_colg = rel["college_has_acourse"]

                # Keeping only those announced courses which are active
                # (i.e. PUBLISHED)
                ac_cur = node_collection.find({
                    '_id': {'$in': ac_of_colg},
                    'member_of': announced_course_gt._id,
                    'attribute_set.nussd_course_type': nussd_course_type,
                    # 'relation_set.course_selected': {'$exists': True, '$not': {'$size': 0}},
                    'status': u"PUBLISHED"
                    # 'attribute_set.start_enroll':{'$lte': curr_date},
                    # 'attribute_set.end_enroll':{'$gte': curr_date}
                }, {
                    "name": 1, "attribute_set": 1, "relation_set": 1
                })

            if ac_cur.count():
                sce_gs_dict = {}
                for each_ac in ac_cur:
                    # NOTE: This ajax-call is used in various templates
                    # Following is used especially only in new_create_batch.html
                    # Fetch enrolled students count from announced course node's course_selected
                    enrolled_stud_count = 0
                    if ann_course_type != 1:
                        for rel in each_ac.relation_set:
                            if rel and "course_has_enrollment" in rel:
                                if rel["course_has_enrollment"]:
                                    sce_gs_id = rel["course_has_enrollment"][0]
                                    str_sce_gs_id = str(sce_gs_id)
                                    if str_sce_gs_id in sce_gs_dict:
                                        enrolled_stud_count = sce_gs_dict[str_sce_gs_id]
                                        break

                                    sce_gs_node = node_collection.one({
                                        "_id": ObjectId(sce_gs_id)
                                    }, {
                                        "attribute_set.has_approved": 1
                                    })

                                    sce_gs_dict[str_sce_gs_id] = enrolled_stud_count
                                    for attr in sce_gs_node.attribute_set:
                                        if attr and "has_approved" in attr:
                                            if attr["has_approved"]:
                                                enrolled_stud_count = len(attr["has_approved"])
                                                sce_gs_dict[str_sce_gs_id] = enrolled_stud_count
                                            break
                                break

                        each_ac["enrolled_stud_count"] = enrolled_stud_count

                    acourse_ctype_list.append(each_ac)

                response_dict["success"] = True
                info_message = "Announced Courses are available"

            else:
                response_dict["success"] = False
                info_message = "No Announced Courses are available"

            response_dict["message"] = info_message
            response_dict["acourse_ctype_list"] = json.dumps(
                acourse_ctype_list, cls=NodeJSONEncoder
            )

            return HttpResponse(json.dumps(response_dict))

        else:
            error_message = " AnnouncedCourseFetchError - Something went wrong in " \
                + "ajax call !!! \n\n Please contact system administrator."
            return HttpResponse(json.dumps({
                'message': error_message
            }))

    except Exception as e:
        error_message = "\n AnnouncedCourseFetchError: Either you are in user " \
            + "group or something went wrong!!!"
        return HttpResponse(json.dumps({'message': error_message}))

@get_execution_time
def get_colleges(request, group_id, app_id):
    """This view returns HttpResponse with following data:
      - List of college(s) affiliated to given university where
        Program Officer is not subscribed
      - List of college(s) affiliated to given university where
        Course(s) is/are already announced for given duration
      - List of college(s) affiliated to given university where
        Course(s) is/are not announced for given duration

    Arguments:
    group_id - ObjectId of the currently selected group
    univ_id - ObjectId of currently selected University
    start_time - Start time of announcement (MM/YYYY)
    end_time - End time of announcement (MM/YYYY)
    dc_courses_id_list - List of ObjectId(s) of Course(s)

    Returns:
    A dictionary consisting of following key-value pairs:-
    success - Boolean giving the state of ajax call
    message - Basestring giving the error/information message
    unassigned_po_colg_list - List of college(s) affiliated to given university
      where Program Officer is not subscribed
    already_announced_in_colg_list - List of college(s) affiliated to given
      university where Course(s) is/are already announced for given duration
    drawer_widget - Drawer containing list of college(s) affiliated to given
      university where Course(s) is/are not announced for given duration
    """

    response_dict = {'success': False, 'message': ""}
    try:
        if request.is_ajax() and request.method == "GET":
            # Fetch field(s) from GET object
            nussd_course_type = request.GET.get("nussd_course_type", "")

            mis_admin = node_collection.one(
                {'_type': "Group", 'name': "MIS_admin"}, {'name': 1}
            )
            if not mis_admin:
                # If not found, throw exception
                error_message = "'MIS_admin' (Group) doesn't exists... " \
                    "Please create it first!"
                raise Exception(error_message)

            univ_id = request.GET.get("univ_id", "")
            start_time = request.GET.get("start_time", "")
            end_time = request.GET.get("end_time", "")
            dc_courses_id_list = request.GET.getlist("dc_courses_id_list[]")
            # all_univs = request.GET.get("all_univs", "")

            # Check whether any field has missing value or not
            if univ_id == "" or start_time == "" or end_time == "":
                error_message = "Invalid data: " \
                    "No data found in any of the field(s)!!!"
                raise Exception(error_message)

            # Fetch all college groups
            college = node_collection.one(
                {'_type': "GSystemType", 'name': "College"}, {'name': 1}
            )
            if not college:
                # If not found, throw exception
                error_message = "'College' (GSystemType) doesn't exists... "\
                    "Please create it first!"
                raise Exception(error_message)

            # Type-cast fetched field(s) into their appropriate type
            univ_id = ObjectId(univ_id)
            start_time = datetime.datetime.strptime(start_time, "%m/%Y")
            end_time = datetime.datetime.strptime(end_time, "%m/%Y")
            dc_courses_id_list = [ObjectId(dc) for dc in dc_courses_id_list]

            # Fetch the node of selected university
            # university_node = node_collection.one(
            #     {'_id': univ_id},
            #     {'relation_set': 1, 'name': 1}
            # )

            # Fetch the list of colleges that are affiliated to
            # the selected university (univ_id)
            colg_under_univ_id = node_collection.find(
                {
                    'member_of': college._id,
                    'relation_set.college_affiliated_to': univ_id
                },
                {
                    'name': 1, 'member_of': 1, 'created_by': 1,
                    'created_at': 1, 'content': 1,
                    'relation_set.has_officer_incharge': 1,
                    'relation_set.college_has_acourse': 1
                }
            ).sort('name', 1)

            list_colg = []
            unassigned_po_colg_list = []
            already_announced_in_colg_list = []
            for each in colg_under_univ_id:
                is_po_exists = False
                if each.relation_set:
                    for rel in each.relation_set:
                        if rel and "has_officer_incharge" in rel:
                            if rel["has_officer_incharge"]:
                                is_po_exists = True

                        if rel and "college_has_acourse" in rel:
                            if rel["college_has_acourse"]:
                                if dc_courses_id_list:
                                    acourse_exists = node_collection.find_one({
                                        '_id': {'$in': rel["college_has_acourse"]},
                                        'relation_set.announced_for': {'$in': dc_courses_id_list},
                                        'attribute_set.start_time': start_time,
                                        'attribute_set.end_time': end_time,
                                        'attribute_set.ann_course_closure': "Open",
                                        'status': "PUBLISHED"
                                    })

                                if acourse_exists:
                                    if each._id not in already_announced_in_colg_list:
                                        already_announced_in_colg_list.append(each.name)

                if each.name in already_announced_in_colg_list:
                    continue

                elif is_po_exists:
                    if each not in list_colg:
                        list_colg.append(each)

                else:
                    if each not in unassigned_po_colg_list:
                        unassigned_po_colg_list.append(each.name)

            response_dict["already_announced_in_colg_list"] = \
                already_announced_in_colg_list

            response_dict["unassigned_PO_colg_list"] = unassigned_po_colg_list

            if list_colg:
                drawer_template_context = edit_drawer_widget(
                    "RelationType", group_id, None, None,
                    checked="announced_course_create_edit",
                    left_drawer_content=list_colg
                )
                drawer_template_context["widget_for"] = \
                    "announced_course_create_edit"
                drawer_widget = render_to_string(
                    'ndf/drawer_widget.html', drawer_template_context,
                    context_instance=RequestContext(request)
                )
                response_dict["drawer_widget"] = drawer_widget
                msg_string = "Following are the list of colleges where " + \
                    "selected Course(s) should be announced:"

            else:
                msg_string = "There are no colleges under this university " + \
                    "where selected Course(s) could be announced!!!"

            # nc_dict = {}
            if colg_under_univ_id.count():
                response_dict["success"] = True
            else:
                msg_string = "No college is affiliated to under selected " + \
                    "University!!!"
                response_dict["success"] = False

            # response_dict["unset_nc"] = nc_dict
            response_dict["message"] = msg_string

            return HttpResponse(json.dumps(response_dict))

    except Exception as e:
        error_message = "CollegeFetchError: " + str(e) + "!!!"
        response_dict["message"] = error_message
        return HttpResponse(json.dumps(response_dict))

@get_execution_time
def get_anncourses_allstudents(request, group_id):
  """
  This view returns ...

  Arguments:
  group_id - ObjectId of the currently selected group

  Returns:
  A dictionary consisting of following key-value pairs:-
  success - Boolean giving the state of ajax call
  message - Basestring giving the error/information message
  """
  response_dict = {'success': False, 'message': ""}
  all_students_text = ""
  query = {}
  try:
    if request.is_ajax() and request.method == "GET":
      registration_year = str(request.GET.get("registration_year", ""))
      all_students = request.GET.get("all_students", "")
      degree_year = request.GET.get("degree_year", "")
      degree_name = request.GET.get("degree_name", "")
      sce_gs_id = request.GET.get("sce_gs_id", "")
      acourse_val = request.GET.getlist("acourse_val[]", "")
      for i, each in enumerate(acourse_val):
        acourse_val[i] = ObjectId(each)

      # Following parameters to be used for edit_drawer_widget()
      # node = None
      # checked = None

      enrolled_stud_count = 0
      non_enrolled_stud_count = 0

      colg_of_acourse_id = None

      # Check whether any field has missing value or not
      if registration_year == "" or all_students == "":
        # registration_year = datetime.datetime.now().year.__str__()
        all_students = u"false"
        # error_message = "Invalid data: No data found in any of the field(s)!!!"
      student = node_collection.one({'_type': "GSystemType", 'name': "Student"})

      sce_gs = node_collection.one({'_id':ObjectId(sce_gs_id)},
        {'member_of': 1, 'attribute_set.has_enrolled': 1, 'relation_set.for_college':1}
      )
      # From Announced Course node fetch College's ObjectId
      # acourse_node = node_collection.find_one(
      #   {'_id': {'$in': acourse_val}, 'relation_set.acourse_for_college': {'$exists': True}},
      #   {'attribute_set': 1, 'relation_set.acourse_for_college': 1}
      # )
      for rel in sce_gs.relation_set:
        if rel:
          colg_of_acourse_id = rel["for_college"][0]
          break

      date_gte = datetime.datetime.strptime("1/1/"+registration_year, "%d/%m/%Y")
      date_lte = datetime.datetime.strptime("31/12/"+registration_year, "%d/%m/%Y")

      # query = {
      #   'member_of': student._id,
      #   'attribute_set.registration_date': {'$gte': date_gte, '$lte': date_lte},
      #   # 'attribute_set.degree_year':degree_year,
      #   # 'attribute_set.degree_name':degree_name,
      #   'relation_set.student_belongs_to_college': ObjectId(colg_of_acourse_id)
      # }

      # If College's ObjectId exists, fetch respective College's group
      if colg_of_acourse_id:
        colg_of_acourse = node_collection.one(
          {'_id': colg_of_acourse_id, 'relation_set.has_group': {'$exists': True}},
          {'relation_set.has_group': 1}
        )

        if colg_of_acourse:
          for rel in colg_of_acourse.relation_set:
            if rel and "has_group" in rel:
              # If rel exists, it means it's has_group
              # then update query
              query = {
                '$or': [
                  {
                    'member_of': student._id,
                    'group_set': rel["has_group"][0],
                    'attribute_set.registration_date': {'$gte': date_gte, '$lte': date_lte},
                  },
                  {
                    'member_of': student._id,
                    'relation_set.student_belongs_to_college': ObjectId(colg_of_acourse_id),
                    'attribute_set.registration_date': {'$gte': date_gte, '$lte': date_lte},
                  }
                ]
              }
              break

      if degree_year:
        query.update({'attribute_set.degree_year': degree_year })

      if degree_name:
        query.update({'attribute_set.degree_name': degree_name })

      # Check whether StudentCourseEnrollment created for given acourse_val
      # Set node as StudentCourseEnrollment node
      # and checked as "has_enrolled", i.e. AT of StudentCourseEnrollment node
      enrolled_stud_list = []
      if sce_gs:
        for attr in sce_gs.attribute_set:
          if attr and "has_enrolled" in attr:
            enrolled_stud_list = attr["has_enrolled"]
            enrolled_stud_count = str(len(attr["has_enrolled"]))
            break

            # sce_gs.get_neighbourhood(sce_gs.member_of)
            # node = sce_gs
            # checked = "has_enrolled"

      res = None

      if all_students == u"true":
        all_students_text = "All students (including enrolled ones)"
        res = node_collection.collection.aggregate([
            {
                '$match': query
            }, {
                '$project': {
                    '_id': 1,
                    'name': '$name',
                    'degree_name': '$attribute_set.degree_name',
                    'degree_year':'$attribute_set.degree_year',
                    'registration_year':'$attribute_set.registration_year'
                }
            },
            {
                '$sort': {'name': 1}
            }
        ])
        total_students_count = len(res["result"])
        all_students_text += " [Count("+str(total_students_count)+")]"
        non_enrolled_stud_count = total_students_count - int(enrolled_stud_count)

      elif all_students == u"false":
        query.update({'_id': {'$nin': enrolled_stud_list}})
        all_students_text = "Only non-enrolled students"

        # Find students which are not enrolled in selected announced course
        # query.update({'relation_set.selected_course': {'$ne': acourse_node._id}})
        # query.update({'relation_set.selected_course': {'$nin': acourse_val}})

        res = node_collection.collection.aggregate([
            {
                '$match': query
            }, {
                '$project': {
                    '_id': 1,
                    'name': '$name',
                    'degree_name': '$attribute_set.degree_name',
                    'degree_year':'$attribute_set.degree_year',
                    'registration_year':'$attribute_set.registration_year'
                }
            },
            {
                '$sort': {'name': 1}
            }
        ])
        non_enrolled_stud_count = str(len(res["result"]))
        all_students_text += " [Count("+non_enrolled_stud_count+")]"

      # response_dict["announced_courses"] = []

      column_headers = [
          ("name", "Name"),
          ("degree_name", "Degree"),
          ("degree_year", "Year"),
      ]

      response_dict["column_headers"] = column_headers
      response_dict["success"] = True
      response_dict["students_data_set"] = res["result"]
      if not res["result"]:
        response_dict["message"] = "No filtered results found"
      response_dict["enrolled_stud_count"] = enrolled_stud_count
      response_dict["non_enrolled_stud_count"] = non_enrolled_stud_count

      return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

    else:
      error_message = "EnrollInCourseError: Either not an ajax call or not a GET request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict))

  except Exception as e:
    error_message = "EnrollInCourseError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))


@get_execution_time
def get_course_details_for_trainer(request, group_id):
  """
  This view returns a dictionary holding data required for trainer's enrollment
  into given announced course(s).

  Arguments:
  group_id - ObjectId of the currently selected group

  Returns:
  A dictionary consisting of following key-value pairs:-
  success - Boolean giving the state of ajax call
  message - Basestring giving the error/information message
  course_enrollement_details - Dictionary that has following structure:
    Key: Course-name
    Value: A list of dictionary where this dictionary's structure is as follows:
      1) Key: ann_course_id; Value: ObjectId of corresponding Announced Course
      2) Key: university; Value: University-name
      3) Key: college; Value: College GSystem's document
  """
  response_dict = {'success': False, 'message': ""}

  try:
    if request.is_ajax() and request.method == "GET":
      course_type = request.GET.get("course_type", "")
      trainer_type = request.GET.get("trainer_type", "")

      # Check whether any field has missing value or not
      if course_type == "" or trainer_type == "":
          error_message = "Invalid data: No data found in any of the field(s)!!!"
          raise Exception(error_message)

      # Using below text variable to fetch specific attribute based on which
      # type of trainer we are dealing with
      # Voluntary Teacher -- voln_tr_qualifications
      # Master Trainer -- mast_tr_qualifications
      fetch_attribute_for_trainer = ""
      bool_trainer_type = None
      if trainer_type == "Voluntary Teacher":
          fetch_attribute_for_trainer = "voln_tr_qualifications"
          bool_trainer_type = True
      elif trainer_type == "Master Trainer":
          fetch_attribute_for_trainer = "mast_tr_qualifications"
          bool_trainer_type = False

      # Fetch required GSystemTypes (NUSSD Course, Announced Course, University, College)
      course_gst = node_collection.one({
          '_type': "GSystemType", 'name': "NUSSD Course"
      }, {
          '_id': 1
      })
      college_gst = node_collection.one({
          '_type': "GSystemType", 'name': "College"
      }, {
          '_id': 1
      })
      university_gst = node_collection.one({
          '_type': "GSystemType", 'name': "University"
      }, {
          '_id': 1
      })
      mis_admin = node_collection.one({
          '_type': "Group", 'name': "MIS_admin"
      }, {
          '_id': 1
      })

      course_enrollement_details = {}
      course_requirements = {}
      college_dict = {}
      university_dict = {}
      course_dict = {}

      # Fetching NUSSD Course(s) registered under MIS_admin group
      nussd_courses_cur = node_collection.find({
          "member_of": course_gst._id,
          "group_set": mis_admin._id,
          "attribute_set.nussd_course_type": course_type
      }, {
          "name": 1,
          "attribute_set." + fetch_attribute_for_trainer: 1
      })

      for course in nussd_courses_cur:
          course_dict[course.name] = course._id

          # Set given course's requirements
          for requirement in course.attribute_set:
              if requirement:
                  course_requirements[course.name] = requirement[fetch_attribute_for_trainer]

          course_enrollement_details[course.name] = []

      if nussd_courses_cur.count():
          college_cur = node_collection.find({
              "member_of": college_gst._id,
              "group_set": mis_admin._id
          }, {
              "name": 1,
              "college_affiliated_to": 1
          })
          for college in college_cur:
              university_gs = None
              if college._id not in university_dict:
                  university_gs = node_collection.find_one({
                      'member_of': university_gst._id,
                      'relation_set.affiliated_college': college._id
                  }, {
                      '_id': 1,
                      'name': 1
                  })
                  if university_gs:
                      university_dict[college._id] = university_gs

                      college_data = {}
                      college_data["college"] = college.name
                      college_data["university"] = university_gs.name
                      if bool_trainer_type:
                          # If bool_trainer_type (True, i.e Voluntary Teacher)
                          # Set organization_id as College's ObjectId
                          # As creating linking between Voluntary Teacher & College
                          college_data["organization_id"] = college._id
                      else:
                          # If bool_trainer_type (False, i.e Master Trainer)
                          # Set organization_id as University's ObjectId
                          # As creating linking between Master Trainer & University
                          college_data["organization_id"] = university_gs._id
                      college_dict[college._id] = college_data

              if college._id in university_dict:
                  for course_name in course_enrollement_details.keys():
                      data_dict = {}
                      data_dict["ann_course_id"] = course_dict[course_name]
                      data_dict.update(college_dict[college._id])

                      course_enrollement_details[course_name].append(data_dict)

      response_dict["course_enrollement_details"] = course_enrollement_details
      response_dict["course_requirements"] = course_requirements

      response_dict["success"] = True
      response_dict["message"] = ""

      return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

    else:
      error_message = "TrainerCourseDetailError: Either not an ajax call or not a GET request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict))

  except Exception as e:
    error_message = "TrainerCourseDetailError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))


@get_execution_time
def get_students_for_approval(request, group_id):
  """This returns data-review list of students that need approval for Course enrollment.
  """
  response_dict = {'success': False, 'message': ""}

  try:
    if request.is_ajax() and request.method == "POST":
      enrollment_id = request.POST.get("enrollment_id", "")

      sce_gst = node_collection.one({'_type': "GSystemType", 'name': "StudentCourseEnrollment"})
      if sce_gst:
        sce_gs = node_collection.one(
            {'_id': ObjectId(enrollment_id), 'member_of': sce_gst._id, 'group_set': ObjectId(group_id), 'status': u"PUBLISHED"},
            {'member_of': 1}
        )

        approval_nodes = []
        data = {}
        if sce_gs:
          sce_gs.get_neighbourhood(sce_gs.member_of)

          data["pk"] = str(sce_gs._id)
          data["CollegeId"] = sce_gs.for_college[0]._id
          data["College"] = sce_gs.for_college[0].name

          course_id_list = []
          for each in sce_gs.for_acourse:
            course_id_list.append(each._id.__str__())
          data["CourseId"] = ",".join(course_id_list)

          if len(sce_gs.for_acourse) > 1:
              # It means it's a Foundation Course's (FC) enrollment
              start_enroll = None
              end_enroll = None
              for each in sce_gs.for_acourse[0].attribute_set:
                  if not each:
                      pass
                  elif "start_time" in each:
                      start_time = each["start_time"]
                  elif "end_time" in each:
                      end_time = each["end_time"]

              data["Course"] = "Foundation_Course" + "_" + start_time.strftime("%b-%Y") + "_" + end_time.strftime("%b-%Y")

          else:
              # Courses other than FC
              data["Course"] = sce_gs.for_acourse[0].name

          # data["CompletedOn"] = sce_gs.completed_on
          data["Enrolled"] = len(sce_gs.has_enrolled)
          # approve_task = sce_gs.has_current_approval_task[0]
          approve_task = sce_gs.has_current_approval_task[0]
          approve_task.get_neighbourhood(approve_task.member_of)
          # Code should be written in create_task: rename it create_update_task
          # Patch: doing here only
          # if data["Enrolled"] > 0:
          #   approve_task.Status = u"In Progress"
          # else:
          #   approve_task.Status = u"Resolved"
          # approve_task.save()
          data["Status"] = approve_task.Status

          if sce_gs.has_key("has_approved"):
              if sce_gs.has_approved:
                  data["Approved"] = len(sce_gs.has_approved)
              else:
                  data["Approved"] = None

          if sce_gs.has_key("has_rejected"):
              if sce_gs.has_rejected:
                  data["Rejected"] = len(sce_gs.has_rejected)
              else:
                  data["Rejected"] = None

          enrolled_students_list = []
          if sce_gs.has_enrolled:
            enrolled_students_list = sce_gs.has_enrolled

          approved_students_list = []
          if sce_gs.has_approved:
            approved_students_list = sce_gs.has_approved

          rejected_students_list = []
          if sce_gs.has_rejected:
            rejected_students_list = sce_gs.has_rejected

          # Update Enrolled students list
          updated_enrolled_students_list = []
          for each_id in enrolled_students_list:
            if (each_id not in approved_students_list) and (each_id not in rejected_students_list):
              updated_enrolled_students_list.append(each_id)
          res = node_collection.collection.aggregate([
              {
                  '$match': {
                      '_id':{"$in":updated_enrolled_students_list}
                  }
              }, {
                  '$project': {
                      '_id': 1,
                      'name': '$name',
                      'degree_name': '$attribute_set.degree_name',
                      'degree_year':'$attribute_set.degree_year',
                      # 'registration_year':{"$date": "$attribute_set.registration_date"}
                      'registration_year':"$attribute_set.registration_date"
                  }
              },
              {
                  '$sort': {'name': 1}
              }
          ])

          # To convert full registration date
          for each in res["result"]:
            reg_year = each["registration_year"][0]
            each["registration_year"] = datetime.datetime.strftime(reg_year,"%Y")

          enrollment_columns = [
              ("name", "Name"),
              ("degree_name", "Degree"),
              ("degree_year", "Year of Study"),
              ("registration_year", "Registration Year")
          ]
          response_dict["success"] = True
          response_dict["enrollment_details"] = data

          response_dict["column_headers"] = enrollment_columns
          response_dict["student_approval_data"] = res["result"]

          return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

  except Exception as e:
    error_message = "StudentCourseApprovalError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

@get_execution_time
def approve_students(request, group_id):
    """This returns approved and/or rejected students count respectively.
    """
    try:
        response_dict = {'success': False, 'message': ""}

        if request.is_ajax() and request.method == "POST":
            approval_state = request.POST.get("approval_state", "")

            enrollment_id = request.POST.get("enrollment_id", "")
            enrollment_id = ObjectId(enrollment_id)

            course_ids = request.POST.get("course_id", "")
            course_ids = [(ObjectId(each.strip()), each.strip()) for each in course_ids.split(",")]
            course_name = request.POST.get("course_name", "")

            students_selected = request.POST.getlist("students_selected[]", "")
            students_selected = [ObjectId(each_str_id) for each_str_id in students_selected]

            college_id = request.POST.get("college_id", "")
            college_id = ObjectId(college_id)
            college_name = request.POST.get("college_name", "")

            sce_gs = node_collection.collection.aggregate([{
                "$match": {
                    "_id": enrollment_id, "group_set": ObjectId(group_id),
                    "relation_set.has_current_approval_task": {"$exists": True},
                    "status": u"PUBLISHED"
                }
            }, {
                "$project": {
                    "has_enrolled": "$attribute_set.has_enrolled",
                    "has_approved": "$attribute_set.has_approved",
                    "has_rejected": "$attribute_set.has_rejected",
                    "has_approval_task": "$attribute_set.has_approval_task",
                    "has_current_approval_task": "$relation_set.has_current_approval_task"
                }
            }])

            user_id = int(request.user.id)  # getting django user's id
            user_name = request.user.username  # getting django user's username
            remaining_count = None
            enrolled_list = []
            approved_list = []
            rejected_list = []
            error_id_list = []
            has_approval_task_dict = {}
            approved_or_rejected_list = []

            has_approval_task_dict = sce_gs["result"][0]["has_approval_task"]
            if has_approval_task_dict:
                has_approval_task_dict = has_approval_task_dict[0]

            enrolled_list = sce_gs["result"][0]["has_enrolled"]
            if enrolled_list:
                enrolled_list = enrolled_list[0]

            approved_list = sce_gs["result"][0]["has_approved"]
            if approved_list:
                approved_list = approved_list[0]

            rejected_list = sce_gs["result"][0]["has_rejected"]
            if rejected_list:
                rejected_list = rejected_list[0]

            at_name = ""
            course_enrollment_status_text = u""
            has_approved_or_rejected_at = None
            if approval_state == "Approve":
                at_name = "has_approved"
                course_enrollment_status_text = u"Enrollment Approved"
                approved_or_rejected_list = approved_list

            elif approval_state == "Reject":
                at_name = "has_rejected"
                course_enrollment_status_text = u"Enrollment Rejected"
                approved_or_rejected_list = rejected_list

            course_enrollment_status_at = node_collection.one({
                '_type': "AttributeType", 'name': "course_enrollment_status"
            })

            # For each student, approve enrollment into given course(Domain)/courses(Foundation Course)
            # For that update value as "Enrollment Approved" against corresponding course (Course ObjectId)
            # in "course_enrollment_status" attribute of respective student
            # This should be done only for Course(s) which exists in "selected_course" relation for that student
            stud_cur = node_collection.collection.aggregate([{
                "$match": {
                    "_id": {"$in": students_selected}
                }
            }, {
                "$project": {
                    "_id": 1,
                    "selected_course": "$relation_set.selected_course",
                    "course_enrollment_status": "$attribute_set.course_enrollment_status"
                }
            }])

            # Performing multiprocessing to fasten out the below processing of
            # for loop; that is, performing approval of students to respective course(s)
            prev_approved_or_rejected_list = []
            new_list = []
            prev_approved_or_rejected_list.extend(approved_or_rejected_list)
            new_list = mp_approve_students(
                stud_cur["result"], course_ids,
                course_enrollment_status_text,
                course_enrollment_status_at,
                prev_approved_or_rejected_list,
                num_of_processes=multiprocessing.cpu_count()
            )

            approved_or_rejected_list.extend(new_list)

            has_approved_or_rejected_at = node_collection.one({
                '_type': "AttributeType", 'name': at_name
            })
            try:
                attr_node = create_gattribute(
                    enrollment_id,
                    has_approved_or_rejected_at,
                    approved_or_rejected_list
                )
            except Exception as e:
                error_id_list.append(enrollment_id)

            # Update student's counts in enrolled, approved & rejecetd list
            enrolled_count = len(enrolled_list)

            if approval_state == "Approve":
                approved_count = len(approved_or_rejected_list)
            else:
                approved_count = len(approved_list)

            if approval_state == "Reject":
                rejected_count = len(approved_or_rejected_list)
            else:
                rejected_count = len(rejected_list)

            remaining_count = enrolled_count - (approved_count + rejected_count)

            # Update status of Approval task
            has_current_approval_task_id = sce_gs["result"][0]["has_current_approval_task"]
            if has_current_approval_task_id:
                has_current_approval_task_id = has_current_approval_task_id[0][0]

            task_status_at = node_collection.one({
                '_type': "AttributeType", 'name': "Status"
            })

            task_status_value = ""
            task_status_msg = ""
            if remaining_count == 0:
                if enrolled_count == (approved_count + rejected_count):
                    task_status_value = u"Closed"
                    task_status_msg = "This task has been closed after successful completion " + \
                        "of approval process of students."

            else:
                task_status_value = u"In Progress"
                task_status_msg = "This task is in progress."

            try:
                # Update the approval task's status as "Closed"
                task_dict = {}
                task_dict["_id"] = has_current_approval_task_id
                task_dict["Status"] = task_status_value

                # Update description of Approval task only at time of it's closure
                if task_status_value is u"Closed":
                    task_dict["created_by_name"] = user_name

                    task_message = task_status_msg + " Following are the details " + \
                        "of this approval process:-" + \
                        "\n Total No. of student(s) enrolled: " + str(enrolled_count) + \
                        "\n Total No. of student(s) approved: " + str(approved_count) + \
                        "\n Total No. of student(s) rejected: " + str(rejected_count) + \
                        "\n Total No. of student(s) remaining: " + str(remaining_count)
                    task_dict["content_org"] = unicode(task_message)

                task_dict["modified_by"] = user_id
                task_node = create_task(task_dict)

                if task_status_value == u"Closed":
                    # Update the StudentCourseEnrollment node's status as "CLOSED"
                    at_type_node = None
                    at_type_node = node_collection.one({
                        '_type': "AttributeType",
                        'name': u"enrollment_status"
                    })
                    if at_type_node:
                        at_node = create_gattribute(enrollment_id, at_type_node, u"CLOSED")

                    # Set completion status for closed approval task in StudentCourseEnrollment node's has_enrollment_task
                    completed_on = datetime.datetime.now()

                    if str(has_current_approval_task_id) in has_approval_task_dict:
                        has_approval_task_dict[str(has_current_approval_task_id)] = {
                            "completed_on": completed_on, "completed_by": user_id
                        }
                        at_type_node = None
                        at_type_node = node_collection.one({
                            '_type': "AttributeType",
                            'name': u"has_approval_task"
                        })

                        if at_type_node:
                            attr_node = create_gattribute(enrollment_id, at_type_node, has_approval_task_dict)

                    # Send intimation to PO's and admin to create batches
                    from_user = user_id
                    url_link_without_domain_part = ""
                    url_link = ""
                    activity_text = "batch creation"
                    msg = "This is to inform you that approval process of " + \
                        "students for " + college_name + " college has been " + \
                        "completed with following details:" + \
                        "\n\tCourse name: " + course_name + \
                        "\n\tTotal No. of student(s) enrolled: " + str(enrolled_count) + \
                        "\n\tTotal No. of student(s) approved: " + str(approved_count) + \
                        "\n\tTotal No. of student(s) rejected: " + str(rejected_count) + \
                        "\n\tTotal No. of student(s) remaining: " + str(remaining_count) + \
                        "\n\nYou can proceed with batch creation for given course in this college."

                    # Fetch college group to get Program Officers of the college
                    college_group_node = node_collection.find_one({
                        "_type": "Group", "relation_set.group_of": college_id
                    }, {
                        "created_by": 1, "group_admin": 1
                    })

                    to_django_user_list = []
                    user_id_list = []
                    user_id_list.extend(college_group_node.group_admin)
                    user_id_list.append(college_group_node.created_by)
                    for each_user_id in user_id_list:
                        user_obj = User.objects.get(id=each_user_id)
                        if user_obj not in to_django_user_list:
                            to_django_user_list.append(user_obj)

                    if url_link_without_domain_part:
                        site = Site.objects.get(pk=1)
                        site = site.name.__str__()

                        domain = "http://" + site
                        url_link = domain + url_link_without_domain_part

                    render_label = render_to_string(
                        "notification/label.html",
                        {
                            "sender": from_user,
                            "activity": activity_text,
                            "conjunction": "-",
                            "link": url_link
                        }
                    )
                    notification.create_notice_type(render_label, msg, "notification")
                    notification.send(to_django_user_list, render_label, {"from_user": from_user})

            except Exception as e:
                error_id_list.append(has_current_approval_task_id)

            response_dict["success"] = True
            response_dict["enrolled"] = enrolled_count
            response_dict["approved"] = approved_count
            response_dict["rejected"] = rejected_count
            response_dict["remaining"] = remaining_count
            response_dict["task_status"] = task_status_value

            return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

    except Exception as e:
        error_message = "ApproveStudentsError: " + str(e) + "!!!"
        response_dict["message"] = error_message
        return HttpResponse(json.dumps(response_dict))

@get_execution_time
def mp_approve_students(student_cur, course_ids, course_enrollment_status_text, course_enrollment_status_at, approved_or_rejected_list, num_of_processes=4):
    def worker(student_cur, course_ids, course_enrollment_status_text, course_enrollment_status_at, approved_or_rejected_list, out_q):
        updated_approved_or_rejected_list = []
        for each_stud in student_cur:
            # Fetch student node along with selected_course and course_enrollment_status
            student_id = each_stud["_id"]

            selected_course = each_stud["selected_course"]
            if selected_course:
                selected_course = selected_course[0]

            # Fetch course_enrollment_status -- Holding Course(s) along with it's enrollment status
            course_enrollment_status = each_stud["course_enrollment_status"]
            if course_enrollment_status:
                course_enrollment_status = course_enrollment_status[0]
            else:
                course_enrollment_status = {}

            for each_course_id, str_course_id in course_ids:
                # If ObjectId exists in selected_course and ObjectId(in string format)
                # exists as key in course_enrollment_status
                # Then only update status as "Enrollment Approved"/"Enrollment Rejected"
                if each_course_id in selected_course and str_course_id in course_enrollment_status:
                    # course_enrollment_status.update({str_course_id: course_enrollment_status_text})
                    course_enrollment_status[str_course_id] = course_enrollment_status_text
                    try:
                        at_node = create_gattribute(student_id, course_enrollment_status_at, course_enrollment_status)
                        if at_node:
                            # If status updated, then only update approved_or_rejected_list
                            # by appending given student's ObjectId into it
                            if student_id not in approved_or_rejected_list and student_id not in updated_approved_or_rejected_list:
                                # approved_or_rejected_list.appendingpend(student_id)
                                updated_approved_or_rejected_list.append(student_id)
                    except Exception as e:
                        error_id_list.append(student_id)
                        continue
        out_q.put(updated_approved_or_rejected_list)

    # Each process will get 'chunksize' student_cur and a queue to put his out
    # dict into
    out_q = multiprocessing.Queue()
    chunksize = int(math.ceil(len(student_cur) / float(num_of_processes)))
    procs = []

    for i in range(num_of_processes):
        p = multiprocessing.Process(
            target=worker,
            args=(student_cur[chunksize * i:chunksize * (i + 1)], course_ids, course_enrollment_status_text, course_enrollment_status_at, approved_or_rejected_list, out_q)
        )
        procs.append(p)
        p.start()

    # Collect all results into a single result list. We know how many lists
    # with results to expect.
    resultlist = []
    for i in range(num_of_processes):
        resultlist.extend(out_q.get())

    # Wait for all worker processes to finish
    for p in procs:
        p.join()

    return resultlist
# ====================================================================================================


@get_execution_time
def get_students_for_batches(request, group_id):
    """
    This view returns ...

    Arguments:
    group_id - ObjectId of the currently selected group
    Returns:
    A dictionary consisting of following key-value pairs:-
    success - Boolean giving the state of ajax call
    message - Basestring giving the error/information message
    """
    response_dict = {'success': False, 'message': ""}
    result_set = None
    query = {}
    try:
        if request.is_ajax() and request.method == "POST":
            ann_course_id = unicode(request.POST.get('ac_id', ""))
            added_ids_list = request.POST.getlist('added_ids_list[]', "")
            if added_ids_list:
                added_ids_list = list(set(added_ids_list))
            search_text = unicode(request.POST.get('search_text', ""))
            stud_gst = node_collection.one({'_type': "GSystemType", 'name': "Student"})
            query.update({'member_of': stud_gst._id})
            if added_ids_list:
                added_ids_list = [ObjectId(each) for each in added_ids_list]
                query.update({'_id': {'$nin': added_ids_list}})
            query.update({'name': {'$regex': search_text, '$options': "i"}})
            query.update({'attribute_set.course_enrollment_status.' + ann_course_id: 'Enrollment Approved'})
            response_dict["success"] = True
            rec = node_collection.collection.aggregate([{'$match': query},
                                      {'$project': {'_id': 0,
                                                    'stud_id': '$_id',
                                                    'enrollment_code': '$attribute_set.enrollment_code',
                                                    'name': '$name',
                                                    # 'email_id': '$attribute_set.email_id',
                                                    # 'phone': '$attribute_set.mobile_number',
                                                    'year_of_study': '$attribute_set.degree_year',
                                                    'degree': '$attribute_set.degree_specialization',
                                                    # 'college': '$relation_set.student_belongs_to_college',
                                                    # 'college_roll_num': '$attribute_set.college_enroll_num',
                                                    # 'university': '$relation_set.student_belongs_to_university',
                                      }},
                                      {'$sort': {'enrollment_code': 1}}
            ])
            result_set = rec['result']
            # Column headers to be displayed on json_data
            column_headers = [
                        ('enrollment_code', 'Enr Code'),
                        ("name", "Name"),
                        ("degree", "Degree/Stream"),
                        ("year_of_study", "Year of Study"),
            ]

            students_count = len(result_set)
            response_dict["students_data_set"] = result_set
            response_dict["success"] = True
            response_dict["students_count"] = students_count
            response_dict["column_headers"] = column_headers
            return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))
        else:
            error_message = "BatchFetchError: Either not an ajax call or not a GET request!!!"
            response_dict["message"] = json_datarror_message
            return HttpResponse(json.dumps(response_dict))

    except Exception as e:
        error_message = "BatchFetchError: " + str(e) + "!!!"
        response_dict["message"] = error_message
        return HttpResponse(json.dumps(response_dict))


@get_execution_time
def edit_task_title(request, group_id):
    '''
    This function will edit task's title
    '''
    if request.is_ajax() and request.method =="POST":
        taskid = request.POST.get('taskid',"")
        title = request.POST.get('title',"")
	task = node_collection.find_one({'_id':ObjectId(taskid)})
        task.name = title
	task.save(groupid=group_id)
        return HttpResponse(task.name)
    else:
	raise Http404

@get_execution_time
def edit_task_content(request, group_id):
    '''
    This function will edit task's title
    '''
    if request.is_ajax() and request.method =="POST":
        taskid = request.POST.get('taskid',"")
        content_org = request.POST.get('content_org',"")
	task = node_collection.find_one({'_id':ObjectId(taskid)})
        task.content_org = unicode(content_org)

  	# Required to link temporary files with the current user who is modifying this document
    	usrname = request.user.username
    	filename = slugify(task.name) + "-" + usrname + "-"
    	task.content = content_org
	task.save(groupid=group_id)
        return HttpResponse(task.content)
    else:
	raise Http404

@get_execution_time
def insert_picture(request, group_id):
    if request.is_ajax():
        resource_list=node_collection.find(
          {
            '_type' : 'File',
            'group_set': {'$in': [ObjectId(group_id)]},
            'mime_type' : u"image/jpeg"
          },
          {'name': 1})

        resources=list(resource_list)
        n=[]
        for each in resources:
            each['_id'] =str(each['_id'])
            file_obj = node_collection.one({'_id':ObjectId(str(each['_id']))})
            if file_obj.fs_file_ids:
                grid_fs_obj =  file_obj.fs.files.get(file_obj.fs_file_ids[0])
                each['fname']=grid_fs_obj.filename
                each['name'] = each['name']
            n.append(each)
        return StreamingHttpResponse(json.dumps(n))
# =============================================================================


@get_execution_time
def close_event(request, group_id, node):
	#close_event checks if the event start date is greater than or less than current date time
	#if current date time if greater than event time than it changes tha edit button
	#on the Gui to reschedule and in database puts the current date and time for reference check
	#till when the event is allowed to reschedule

    reschedule_event=node_collection.one({"_type":"AttributeType","name":"event_edit_reschedule"})
    create_gattribute(ObjectId(node),reschedule_event,{"reschedule_till":datetime.datetime.today(),"reschedule_allow":False})

    return HttpResponse("event closed")
@get_execution_time
def save_time(request, group_id, node):
  start_time = request.POST.get('start_time','')
  end_time = request.POST.get('end_time','')

  reschedule_event_start = node_collection.one({"_type":"AttributeType","name":"start_time"})
  reschedule_event_end = node_collection.one({"_type":"AttributeType","name":"end_time"})
  reschedule_event=node_collection.one({"_type":"AttributeType","name":"event_edit_reschedule"})
  start_time= parse_template_data(datetime.datetime,start_time, date_format_string="%d/%m/%Y %H:%M")
  end_time= parse_template_data(datetime.datetime,end_time, date_format_string="%d/%m/%Y %H:%M")
  create_gattribute(ObjectId(node),reschedule_event_start,start_time)
  create_gattribute(ObjectId(node),reschedule_event_end,end_time)
  reschedule_event=node_collection.one({"_type":"AttributeType","name":"event_edit_reschedule"})
  event_node = node_collection.one({"_id":ObjectId(node)})
  # below code gets the old value from the database
  # if value exists it append new value to it
  # else a new time is assigned to it
  a = {}
  for i in event_node.attribute_set:
               if unicode('event_edit_reschedule') in i.keys():
                 a = i['event_edit_reschedule']
  a['reschedule_till'] = start_time
  create_gattribute(ObjectId(node),reschedule_event,a)
  #change the name of the event based on new time
  if event_node:
     name = event_node.name
     name_arr = name.split("--")
     new_name = unicode(str(name_arr[0]) + "--" + str(name_arr[1]) + "--" + str(start_time))
     event_node.name = new_name
     event_node.save(groupid=group_id)
  return HttpResponse("Session rescheduled")

@get_execution_time
def check_date(request, group_id, node):

    reschedule = request.POST.get('reschedule','')
    test_output = node_collection.find({"_id":ObjectId(node),"attribute_set.start_time":{'$gt':datetime.datetime.today()}})
    a = {}
    if test_output.count()  == 0 and reschedule == 'True':
       test_output = node_collection.find({"_id":ObjectId(node),"attribute_set.event_edit_reschedule.reschedule_till":{'$gt':datetime.datetime.today()}})
    if test_output.count() != 0:
       message = "event Open"
    if test_output.count() == 0:
      reschedule_event=node_collection.one({"_type":"AttributeType","name":"event_edit_reschedule"})
      event_node = node_collection.one({"_id":ObjectId(node)})
      a=""
      for i in event_node.attribute_set:
               if unicode('event_edit_reschedule') in i.keys():
                 a = i['event_edit_reschedule']
      if a:
          for i in a:
              if unicode('reschedule_allow') in i:
                  a['reschedule_allow'] = False
          create_gattribute(ObjectId(node),reschedule_event,a)
      else:
          create_gattribute(ObjectId(node),reschedule_event,{'reschedule_allow':False})

      event_node = node_collection.one({"_id":ObjectId(node)})
      message = "event closed"
    return HttpResponse(message)

@get_execution_time
def reschedule_task(request, group_id, node):

 task_dict={}
 #name of the programe officer who has initiated this task
 '''Required keys: _id[optional], name, group_set, created_by, modified_by, contributors, content_org,
        created_by_name, Status, Priority, start_time, end_time, Assignee, has_type
 '''

 task_groupset=node_collection.one({"_type":"Group","name":"MIS_admin"})

 a=[]
 b=[]
 c=[]
 listing=task_groupset.group_admin
 listing.append(task_groupset.created_by)
 return_message=""
 values=[]
 if request.user.id in listing:

    reschedule_attendance = node_collection.one({"_type":"AttributeType","name":"reschedule_attendance"})
    marks_entry = node_collection.find({"_type":"AttributeType","name":"marks_entry_completed"})
    reschedule_type = request.POST.get('reschedule_type','')
    reshedule_choice = request.POST.get('reshedule_choice','')
    session = request.POST.get('session','')
    end_time = node_collection.one({"name":"end_time"})
    from datetime import date,time,timedelta
    date1 = datetime.date.today() + timedelta(2)
    ti = datetime.time(0,0)
    event_start_time = ""
    start_time = request.POST.get('reschedule_date','')
    b = parse_template_data(datetime.datetime,start_time, date_format_string="%d/%m/%Y %H:%M")
    #fetch event
    event_node = node_collection.one({"_id":ObjectId(node)})
    reschedule_dates = []
    #for any type change the event status to re-schdueled if the request comes
    #for generating a task for reschdueling a event
    event_status = node_collection.one({"_type":"AttributeType","name":"event_status"})
    create_gattribute(ObjectId(node),event_status,unicode('Rescheduled'))
    task_id= {}
    if  reschedule_type == 'event_reschedule' :
         for i in event_node.attribute_set:
	         if unicode('event_edit_reschedule') in i.keys():
        	    	   if unicode ('reschedule_dates') in i['event_edit_reschedule']:
        	    	   	  reschedule_dates = i['event_edit_reschedule']['reschedule_dates']
                 if unicode("event_date_task") in i.keys():
                      task_id = i["event_date_task"]
                 if unicode("start_time") in i.keys():
                      event_start_time = i["start_time"]
         if task_id:

            for i in task_id:
              if unicode('Task')  ==  i:
                 tid = i
                 task_node = node_collection.find({"_id":ObjectId(task_id["Task"])})
                 task_attribute = node_collection.one({"_type":"AttributeType","name":"Status"})
                 create_gattribute(ObjectId(task_node[0]._id),task_attribute,unicode("Closed"))
         reschedule_event=node_collection.one({"_type":"AttributeType","name":"event_date_task"})
         task_id['Reschedule_Task'] = True
         create_gattribute(ObjectId(node),reschedule_event,task_id)
         reschedule_dates.append(event_start_time)
         reschedule_event=node_collection.one({"_type":"AttributeType","name":"event_edit_reschedule"})
         create_gattribute(ObjectId(node),reschedule_event,{"reschedule_till":b,"reschedule_allow":True,"reschedule_dates":reschedule_dates})
         return_message = "Event Dates Re-Schedule Opened"

    else:
        event_details = ""
        for i in event_node.attribute_set:
            if unicode('reschedule_attendance') in i.keys():
                if unicode ('reschedule_dates') in i['reschedule_attendance']:
                    reschedule_dates = i['reschedule_attendance']['reschedule_dates']
            if unicode('marks_entry_completed') in i.keys():
                    marks_entry_completed = i['marks_entry_completed']
            if unicode("event_attendance_task") in i.keys():
              task_id = i["event_attendance_task"]

        if task_id:
            for i in task_id:
            	if unicode('Task') == i:
                 tid = task_id['Task']
                 task_node = node_collection.find({"_id":ObjectId(tid)})
                 task_attribute = node_collection.one({"_type":"AttributeType","name":"Status"})
                 create_gattribute(ObjectId(task_node[0]._id),task_attribute,unicode("Closed"))
                 break

        reschedule_dates.append(datetime.datetime.today())
        if reshedule_choice == "Attendance" or reshedule_choice == "" :
                create_gattribute(ObjectId(node),reschedule_attendance,{"reschedule_till":b,"reschedule_allow":True,"reschedule_dates":reschedule_dates})
        if session != str(1) and reshedule_choice == "Assessment" :
          create_gattribute(ObjectId(node),marks_entry[0],False)
        task_id['Reschedule_Task'] = True
        reschedule_event=node_collection.one({"_type":"AttributeType","name":"event_attendance_task"})
	create_gattribute(ObjectId(node),reschedule_event,task_id)
        return_message="Event Re-scheduled"
 else:
    reschedule_type = request.POST.get('reschedule_type','')
    reshedule_choice = request.POST.get('reshedule_choice','')
    if reschedule_type == "attendance_reschedule":
       if  reshedule_choice == "Attendance" or reshedule_choice == "":
           content = "Attendance"
       if  reshedule_choice == "Assessment":
           content = "Assessment"
    else:
       content = "start time"
    mis_admin_grp = node_collection.one({'_type':"Group","name":"MIS_admin"})
    mis_admin_list = mis_admin_grp.group_admin
    mis_admin_list.append(mis_admin_grp.created_by)
    path = request.POST.get('path','')
    site = Site.objects.get(pk=1)
    site = site.name.__str__()
    event_reschedule_link = "http://" + site + path
    b.append(task_groupset._id)
    glist_gst = node_collection.one({'_type': "GSystemType", 'name': "GList"})
    task_type = []
    task_type.append(node_collection.one({'member_of': glist_gst._id, 'name':"Re-schedule Event"})._id)
    task_dict.update({"has_type": task_type})
    task_dict.update({'name': unicode("Re-schedule Event" + " " + content)})
    task_dict.update({'group_set': b})
    task_dict.update({'created_by': request.user.id})
    task_dict.update({'modified_by': request.user.id})
    task_dict.update({'content_org': unicode("Please Re-Schedule the Following event"+"   \t " "\n- Please click [[" + event_reschedule_link + "][here]] to reschedule event " + " " + content )})
    task_dict.update({'created_by_name': request.user.username})
    task_dict.update({'Status': unicode("New")})
    task_dict.update({'Priority': unicode('Normal')})
    date1 = datetime.date.today()
    ti = datetime.time(0,0)
    Today = datetime.datetime.combine(date1,ti)
    task_dict.update({'start_time': Today})
    task_dict.update({'Assignee': mis_admin_list})
    task = create_task(task_dict)

    if  reschedule_type == 'event_reschedule' :
      reschedule_event=node_collection.one({"_type":"AttributeType","name":"event_date_task"})
      create_gattribute(ObjectId(node),reschedule_event,{'Task':ObjectId(task._id),'Reschedule_Task':False})
    else:
      reschedule_event=node_collection.one({"_type":"AttributeType","name":"event_attendance_task"})
      create_gattribute(ObjectId(node),reschedule_event,{'Task':ObjectId(task._id),'Reschedule_Task':False})
    return_message="Message is sent to central office soon you will get update."
 return HttpResponse(return_message)

@get_execution_time
def event_assginee(request, group_id, app_set_instance_id=None):

 Event=   request.POST.getlist("Event","")

 Event_attended_by=request.POST.getlist("Event_attended_by[]","")

 marks=request.POST.getlist("marks","")

 assessmentdone = request.POST.get("assessmentdone","")

 attendancedone = request.POST.get("attendancedone","")

 attendancesession = request.POST.get("attendancesession","")

 oid=node_collection.find_one({"_type" : "RelationType","name":"has_attended"})

 Assignment_rel=node_collection.find({"_type":"AttributeType","name":"Assignment_marks_record"})

 Assessmentmarks_rel=node_collection.find({"_type":"AttributeType","name":"Assessment_marks_record"})

 performance_record=node_collection.find({"_type":"AttributeType","name":"performance_record"})

 student_attendace_record=node_collection.find({"_type":"AttributeType","name":"attendance_record"})

 marks_entry_completed=node_collection.find({"_type":"AttributeType","name":"marks_entry_completed"})

 reschedule_attendance = node_collection.one({"_type":"AttributeType","name":"reschedule_attendance"})

 event_node = node_collection.one({"_id":ObjectId(app_set_instance_id)})

 student_details = node_collection.one({"_type":"AttributeType","name":"student_event_details"})

 #code for saving Attendance and Assesment of Assignment And Assesment Session
 attendedlist=[]
 for info in Event_attended_by:
     a=ast.literal_eval(info)
     if (a['Name'] != 'undefined'):
      student_dict={}
      attendance_dict = {}
      performance_record_dict = {}
      marks_dict = {}
      student_node = node_collection.find_one({"_id":ObjectId(a['Name'])})

      for i in student_node.attribute_set:
          if unicode('student_event_details') in i.keys():
            student_dict.update(i['student_event_details'])
          if unicode("attendance_record") in i.keys():
            attendance_dict.update(i["attendance_record"])
          if unicode("performance_record") in i.keys():
            performance_record_dict.update(i["performance_record"])

      if (a['save'] == '2' or a['save'] == '3'):
        marks_dict["Assignment_marks_record"] = a['Attendance_marks']
      if(a['save'] == '2' or  a['save'] == '4'):
      	marks_dict["Assessment_marks_record"] = a['Assessment_marks']
      if (a['save'] == '2' or a['save'] == '3' or a['save'] == '4'):
        student_dict[Event[0]] = marks_dict
        create_gattribute(ObjectId(a['Name']),student_details,student_dict)

      if(a['save'] == '5'):
      	performance_record_dict[Event[0]] = a['Assessment_marks']
        create_gattribute(ObjectId(a['Name']),performance_record[0],performance_record_dict)
      if(a['Presence'] == 'True'):
          attendedlist.append(a['Name'])
      attendance_dict.update({unicode(Event[0]):a['Presence']})
      create_gattribute(ObjectId(a['Name']),student_attendace_record[0],attendance_dict)

 if attendancesession != str(1):
   create_gattribute(ObjectId(app_set_instance_id),marks_entry_completed[0],False)
 if assessmentdone == 'True':
     event_status = node_collection.one({"_type":"AttributeType","name":"event_status"})
     create_gattribute(ObjectId(app_set_instance_id),event_status,unicode('Completed'))
     create_gattribute(ObjectId(app_set_instance_id),marks_entry_completed[0],True)

 reschedule_dates={}

 if attendancedone == 'True' or assessmentdone == 'True':
    for j in event_node.attribute_set:
       if unicode('reschedule_attendance') in j.keys():
          reschedule_dates = j['reschedule_attendance']
    if attendancesession != str(1):
        reschedule_dates["reschedule_allow"] = False
        create_gattribute(ObjectId(app_set_instance_id),reschedule_attendance,reschedule_dates)
    if attendancesession == str(1):
    	event_status = node_collection.one({"_type":"AttributeType","name":"event_status"})
        create_gattribute(ObjectId(app_set_instance_id),event_status,unicode('Completed'))

 create_grelation(ObjectId(app_set_instance_id), oid,attendedlist)


 return HttpResponse("Details Entered")

@get_execution_time
def fetch_course_name(request, group_id,Course_type):
  courses=node_collection.find({"attribute_set.nussd_course_type":unicode(Course_type)})

  course_detail={}
  course_list=[]
  for i in courses:
    course_detail.update({"name":i.name})
    course_detail.update({"id":str(i._id)})
    course_list.append(course_detail)
    course_detail={}
  return HttpResponse(json.dumps(course_list))

@get_execution_time
def fetch_course_Module(request, group_id,announced_course):
  #Course_name
  batch = request.GET.get('batchid','')

  superdict={}
  module_Detail={}
  module_list=[]
  event_type_ids=[]

  courses = node_collection.one({"_id":ObjectId(announced_course)},{'relation_set.announced_for':1,'relation_set.acourse_for_college':1})

  eventtypes = node_collection.find({'_type': "GSystemType", 'name': {'$in': ["Classroom Session", "Exam"]}})
  for i in eventtypes:
  	  event_type_ids.append(i._id)

  for i in courses.relation_set:
    if unicode('announced_for') in i.keys():
      	announced_for = i['announced_for']
    if unicode('acourse_for_college') in i.keys():
        for j in  i['acourse_for_college']:
            group_of = j

  courses = node_collection.find({"_id":{'$in':announced_for}})
  trainers = node_collection.find({"relation_set.trainer_teaches_course_in_college":[ObjectId(courses[0]._id),ObjectId(group_of)]})
  course_modules = node_collection.find({"_id":{'$in':courses[0].collection_set}})

  #condition for all the modules to be listed is session in it should not be part of the event
  checklist=[]
  for i in course_modules:
    checklist = i.collection_set
    #check if this collection_set exists in any
    event = node_collection.find({"member_of":{'$in':event_type_ids},"relation_set.session_of":{'$elemMatch':{'$in':i.collection_set}}
    	                  ,'relation_set.event_has_batch':ObjectId(batch)})
    for k in event:
    	 for j in k.relation_set:
             if unicode('session_of') in j.keys():
             	if j['session_of'][0] in checklist:
             		checklist.remove(j['session_of'][0])
    if len(checklist) > 0:
	    module_Detail.update({"name":i.name})
	    module_Detail.update({"id":str(i._id)})
	    module_list.append(module_Detail)
	    module_Detail={}

  trainerlist=[]
  trainer_detail={}
  for i in trainers:
    trainer_detail.update({"name":i.name})
    trainer_detail.update({"id":str(i._id)})
    trainerlist.append(trainer_detail)
    trainer_detail={}
  superdict['Module']=json.dumps(module_list,cls=NodeJSONEncoder)
  superdict['trainer'] = json.dumps(trainerlist,cls=NodeJSONEncoder)
  return HttpResponse(json.dumps(superdict))

@get_execution_time
def fetch_batch_student(request, group_id,Course_name):
  try:
    courses=node_collection.one({"_id":ObjectId(Course_name)},{'relation_set.has_batch_member':1})
    dict1={}
    list1=[]
    for i in courses.relation_set:
    	 if unicode('has_batch_member') in i.keys():
           has_batch = i['has_batch_member']
    for i in has_batch:
     dict1.update({"id":str(i)})
     list1.append(dict1)
     dict1={}
    return HttpResponse(json.dumps(list1))
  except:
    return HttpResponse(json.dumps(list1))

@get_execution_time
def fetch_course_session(request, group_id,Course_name):
  try:
	  courses=node_collection.one({"_id":ObjectId(Course_name)})
	  batch = request.GET.get('batchid','')
	  dict1={}
	  list1=[]
	  checklist = []
	  event_type_ids = []
	  checklist =  courses.collection_set
	  eventtypes = node_collection.find({'_type': "GSystemType", 'name': {'$in': ["Classroom Session", "Exam"]}})
	  for i in eventtypes:
	  	  event_type_ids.append(i._id)

	  module_node  = node_collection.find({"member_of":{'$in':event_type_ids},"relation_set.session_of":{'$elemMatch':{'$in':checklist}}
	    	                  ,'relation_set.event_has_batch':ObjectId(batch)})
	  for i in module_node:
	     for k in i.relation_set:
		if unicode('session_of') in k.keys():
		   if k['session_of'][0] in checklist:
		       checklist.remove(k['session_of'][0])
	  course_modules=node_collection.find({"_id":{'$in':checklist}})
	  for i in course_modules:
	      dict1.update({"name":i.name})
	      dict1.update({"id":str(i._id)})
	      for j in i.attribute_set:
	          if "course_structure_minutes" in j.keys()  :
	              dict1.update({"minutes":str(j["course_structure_minutes"])})
	      list1.append(dict1)
	      dict1={}
	  return HttpResponse(json.dumps(list1))
  except:
    return HttpResponse(json.dumps(list1))



@get_execution_time
def fetch_course_batches(request, group_id,Course_name):
  #courses=node_collection.one({"_id":ObjectId(Course_name)})
  #courses=node_collection.find({"relation_set.announced_for":ObjectId(Course_name)})
  try:
    dict1={}
    list1=[]
    batch=node_collection.find({"_type":"GSystemType","name":"Batch"})
    batches=node_collection.find({"member_of":batch[0]._id,"relation_set.has_course":ObjectId(Course_name)})
    for i in batches:
        dict1.update({"name":i.name})
        dict1.update({"id":str(i._id)})
        list1.append(dict1)
        dict1={}

    return HttpResponse(json.dumps(list1))
  except:
    return HttpResponse(json.dumps(list1))


@get_execution_time
def save_csv(request,group_id,app_set_instance_id=None):
        #column_header = [u'Name', 'Presence','Attendance_marks','Assessment_marks']
        json_data=request.POST.getlist("attendance[]","")
        column_header=request.POST.getlist("column[]","")
        t = time.strftime("%c").replace(":", "_").replace(" ", "_")
        filename = "csv/" + "Attendance_data_" + t + ".csv"
        filepath = os.path.join(STATIC_ROOT, filename)
        filedir = os.path.dirname(filepath)
        if not os.path.exists(filedir):
          os.makedirs(filedir)
        data={}
        with open(filepath, 'wb') as csv_file:
          fw = csv.DictWriter(csv_file, delimiter=',', fieldnames=column_header)
          fw.writerow(dict((col,col) for col in column_header))

          for row in list(json_data):
            v = {}
            fw.writerow(ast.literal_eval(row))
        return HttpResponse((STATIC_URL + filename))

def get_assessment(request,group_id,app_set_instance_id):
    node = node_collection.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
    node.get_neighbourhood(node.member_of)
    marks_list=[]
    Assesslist=[]
    val=False
    for i in node.has_attendees:
       dict1={}
       dict1.update({'name':i.name})
       for j in  i.attribute_set:
            if  j.keys()[0] == 'performance_record':
               if (str(j['performance_record']['Event']) == str(app_set_instance_id)) is True:
                  val=True
                  dict1.update({'marks':j['performance_record']['marks']})
               else:
                  dict1.update({'marks':""})

       dict1.update({'id':str(i._id)})
       if val is True:
             marks_list.append(dict1)
       else:
             dict1.update({'marks':"0"})
             marks_list.append(dict1)
    return HttpResponse(json.dumps(marks_list))

@get_execution_time
def get_attendees(request,group_id,node):
 #get all the ObjectId of the people who would attend the event
 node=node_collection.one({'_id':ObjectId(node)})
 attendieslist=[]
 #below code would give the the Object Id of Possible attendies
 for i in node.relation_set:
     if ('has_attendees' in i):
        for j in  i['has_attendees']:
                attendieslist.append(j)

 attendee_name=[]
 #below code is meant for if a batch or member of group id  is found, fetch the attendees list-
 #from the members of the batches if members are selected from the interface their names would be returned
 #attendees_id=node_collection.find({ '_id':{'$in': attendieslist}},{"group_admin":1})
 attendees_id=node_collection.find({ '_id':{'$in': attendieslist}})
 for i in attendees_id:
    #if i["group_admin"]:
    #  User_info=(collectigeton.Node.find({'_type':"Author",'created_by':{'$in':i["group_admin"]}}))
    #else:
    User_info=(node_collection.find({'_id':ObjectId(i._id)}))
    for i in User_info:
       attendee_name.append(i)
 attendee_name_list=[]
 for i in attendee_name:
    if i not in attendee_name_list:
        attendee_name_list.append(i)
 a=[]
 d={}
 for i in attendee_name_list:
    d={}
    d.update({'name':i.name})
    d.update({'id':str(i._id)})
    a.append(d)

 return HttpResponse(json.dumps(a))

@get_execution_time
def get_attendance(request,group_id,node):
 #method is written to get the presence and absence of attendees for the event
 node=node_collection.one({'_id':ObjectId(node)})
 attendieslist=[]
 #below code would give the the Object Id of Possible attendies
 for i in node.relation_set:
     if ('has_attendees' in i):
        for j in  i['has_attendees']:
                attendieslist.append(j)

 attendee_name=[]
 attendees_id=node_collection.find({ '_id':{'$in': attendieslist}})
 for i in attendees_id:
    #if i["group_admin"]:
    #  User_info=(node_collection.find({'_type':"Author",'created_by':{'$in':i["group_admin"]}}))
    #else:
    User_info=(node_collection.find({'_id':ObjectId(i._id)}))
    for i in User_info:
       attendee_name.append(i)
 attendee_name_list=[]
 for i in attendee_name:
    if i not in attendee_name_list:
        attendee_name_list.append(i)
 a=[]
 d={}

 has_attended_event=node_collection.find({'_id':ObjectId(node.pk)},{'relation_set':1})
 #get all the objectid
 attendieslist=[]
 for i in has_attended_event[0].relation_set:
     if ('has_attended' in i):
           for j in  i['has_attended']:
                attendieslist.append(j)
 #create the table
 count=0
 attendance=[]
 temp_attendance={}
 #the below code would compare between the supposed attendees and has_attended the event
 #and accordingly mark their presence or absence for the event

 node.get_neighbourhood(node.member_of)
 Assess_marks_list=[]
 Assign_marks_list=[]
 Assesslist=[]
 marks_list=[]
 val=False
 assign=False
 asses=False
 member_of=node_collection.one({"_id":{'$in':node.member_of}})

 for i in attendee_name_list:
    if (i._id in attendieslist):
      attendees = node_collection.one({"_id":ObjectId(i._id)})
      dict1={}
      dict2={}
      for j in  attendees.attribute_set:
         if member_of.name != "Exam":
            	if   unicode('student_event_details') in j.keys():
                   if(unicode(node._id) in j['student_event_details'].keys()):
                           if unicode('Assignment_marks_record') in j['student_event_details'][str(node._id)].keys():
                              val=True
                              assign=True
                              dict1.update({'marks':j['student_event_details'][str(node._id)]['Assignment_marks_record']})
                           else:
                              dict1.update({'marks':"0"})
                      	   if unicode('Assessment_marks_record')  in j['student_event_details'][str(node._id)].keys():
          	                  val=True
          	                  asses=True
          	                  dict2.update({'marks':j['student_event_details'][str(node._id)]['Assessment_marks_record']})
          	           else:
          	                  dict2.update({'marks':"0"})
                           break;
                else:
                        dict1.update({'marks':'0'})
                        dict2.update({'marks':'0'})
         if member_of.name == "Exam":
            dict1.update({'marks':"0"})
            if  unicode('performance_record') in j.keys():
               if(unicode(node._id) in j['performance_record'].keys()) :
                  val=True
                  asses=True
                  dict2.update({'marks':j['performance_record'][unicode(node._id)]})
               else:
                  dict2.update({'marks':"0"})
      temp_attendance.update({'id':str(i._id)})
      temp_attendance.update({'name':i.name})
      temp_attendance.update({'presence':'Present'})
      if dict1.has_key('marks'):
        temp_attendance.update({'Assignment_marks':dict1['marks']})
      if dict2.has_key('marks'):
        temp_attendance.update({'Assessment_marks':dict2['marks']})
      attendance.append(temp_attendance)
    else:
      temp_attendance.update({'id':str(i._id)})
      temp_attendance.update({'name':i.name})
      temp_attendance.update({'presence':'Absent'})
      temp_attendance.update({'Assignment_marks':"0"})
      temp_attendance.update({'Assessment_marks':"0"})
      attendance.append(temp_attendance)
    temp_attendance={}
 return HttpResponse(json.dumps(attendance))

@get_execution_time
def attendees_relations(request,group_id,node):
 test_output = node_collection.find({"_id":ObjectId(node),"attribute_set.start_time":{'$lt':datetime.datetime.today()}})
 if test_output.count() != 0:
         event_has_attended=node_collection.find({'_id':ObjectId(node)})
         column_list=[]
         column_count=0
         course_assignment=False
         course_assessment=False
         reschedule = True
         #marks = False
         marks = True

         member_of=node_collection.one({"_id":{'$in':event_has_attended[0].member_of}})
         if member_of.name != "Exam":
           for i in event_has_attended[0].relation_set:
              #True if (has_attended relation is their means attendance is already taken)
              #False (signifies attendence is not taken yet for the event)
              if ('has_attended' in i):
                a = "True"
              else:
                a = "False"
              if ('session_of' in i):
                 session=node_collection.one({"_id":{'$in':i['session_of']}})
                 for i in session.attribute_set:
                      if unicode('course_structure_assignment') in i:
                       if i['course_structure_assignment'] == True:
                          course_assignment=True
                      if unicode('course_structure_assessment') in i:
                       if i['course_structure_assessment'] == True:
                          course_assessment=True

           # meaning of the numbers
           #2 :- populate both assesment and assignment marks columns
           #3 :- popuplate only Asssignment marks Columns
           #4 :- populate only Assesment marks Columns
           #1 :- populate Only Attendance taking part donot populate Assesment and Attendance taking part
           if course_assessment == True:
             column_count = 4
           if course_assignment == True:
             column_count = 3
           if (course_assessment == True and course_assignment == True):
             column_count = 2
           if (course_assignment == False and course_assessment == False):
             column_count = 1
           column_list.append(a)
           column_list.append(column_count)
         else:
           column_count=5
           column_list.append('True')
           column_list.append(column_count)
         node = node_collection.one({"_id":ObjectId(node)})
         for i in node.attribute_set:
            if unicode("reschedule_attendance") in i.keys():
              if unicode('reschedule_allow') in i['reschedule_attendance']:
               reschedule=i['reschedule_attendance']['reschedule_allow']
            if unicode("marks_entry_completed") in i.keys():
                marks=i["marks_entry_completed"]
         column_list.append(reschedule)
         column_list.append(marks)
 else:
         column_list=[]
 return HttpResponse(json.dumps(column_list))


@get_execution_time
def page_scroll(request,group_id,page):
  hyperlinks = request.GET.get("links")
  if hyperlinks:
    hyperlinks = json.loads(hyperlinks)
  else:
    hyperlinks = True

  group_obj = node_collection.find({'group_set':ObjectId(group_id)}).sort('last_update', -1)
  if group_obj.count() >=10:
    paged_resources = Paginator(group_obj,10)
  else:
    paged_resources = Paginator(group_obj,group_obj.count())
  files_list = []
  user_activity = []
  # tot_page=paged_resources.num_pages
  if paged_resources.count and (int(page) <= int(paged_resources.num_pages)):
    if int(page)==1:
      page='1'
    if int(page) != int(paged_resources.num_pages) and int(page) != int(1):
      page=int(page)+1
    # temp. variables which stores the lookup for append method
    user_activity_append_temp=user_activity.append
    files_list_append_temp=files_list.append
    for each in (paged_resources.page(int(page))).object_list:
      if each.created_by == each.modified_by :
        if each.last_update == each.created_at:
          activity =  'created'
        else:
          activity =  'modified'
      else:
        activity =  'created'
      if each._type == 'Group':
        user_activity_append_temp(each)
      each.update({'activity':activity})
      files_list_append_temp(each)
  else:
    page=0

  return render_to_response('ndf/scrolldata.html',
                                { 'activity_list': files_list,
                                  'group_id': group_id,
                                  'groupid':group_id,
                                  'page':page, 'hyperlinks': hyperlinks
                                # 'imageCollection':imageCollection
                                },
                                context_instance = RequestContext(request)
  )

@login_required
@get_execution_time
def get_batches_with_acourse(request, group_id):
  """
  This view returns list of batches that match given criteria
  along with Announced-course for which match doesn't exists.

  Arguments:
  group_id - ObjectId of the currently selected group

  """
  response_dict = {'success': False, 'message': ""}
  batches_list = []
  batch_gst = node_collection.one({'_type':'GSystemType','name':'Batch'})
  try:
    if request.is_ajax() and request.method == "GET":
      # Fetch field(s) from GET object
      announced_course_id = request.GET.get("ac_id", "")
      mis_admin = node_collection.one({'_type': "Group", 'name': "MIS_admin"})
      if(ObjectId(group_id) == mis_admin._id):
        pass
      else:
        colg_gst = node_collection.one({'_type': "GSystemType", 'name': 'College'})
        req_colg_id = node_collection.one({'member_of':colg_gst._id,'relation_set.has_group':ObjectId(group_id)})
        b = node_collection.find({'member_of':batch_gst._id,'relation_set.has_course':ObjectId(announced_course_id)})
        for each in b:
          batches_list.append(each)

        response_dict["success"] = True
        info_message = "Batch for this course is available"
      response_dict["message"] = info_message

      response_dict["batches_list"] = json.dumps(batches_list, cls=NodeJSONEncoder)

      return HttpResponse(json.dumps(response_dict))

    else:
      error_message = " BatchFetchError: Either not an ajax call or not a GET request!!!"
      return HttpResponse(json.dumps({'message': " BatchCourseFetchError - Something went wrong in ajax call !!! \n\n Please contact system administrator."}))

  except Exception as e:
    error_message = "\n BatchFetchError: " + str(e) + "!!!"
    return HttpResponse(json.dumps({'message': error_message}))


@login_required
@get_execution_time
def get_universities(request, group_id):
    """
    This view fetches Universities belonging to given state.

    Arguments:
    group_id - ObjectId of the currently selected group
    state_id - ObjectId of the currently selected state`

    Returns:
    A dictionary consisting of following key:-
    universities - a list variable consisting of two elements i.e.,
                first-element: University's ObjectId,
                second-element:University's name
    message - a string variable giving the error-message
    """

    try:
        if request.is_ajax() and request.method == "GET":
            state_id = request.GET.get("state_id", "")

            # universities -- [first-element: subject (University's ObjectId),
            # second-element: manipulated-name-value (University's name)]
            universities = []
            univ_gst = node_collection.one({'_type': "GSystemType", 'name': "University"})
            mis_admin_grp = node_collection.one({'_type': "Group", 'name': "MIS_admin"})

            if state_id == "ALL":
                # Fetching all universities belonging to given state in sorted order by name
                university_cur = node_collection.find(
                    {
                        'member_of': univ_gst._id,
                        'group_set': mis_admin_grp._id,
                    }).sort('name', 1)

            else:
                # Fetching all universities belonging to given state in sorted order by name
                university_cur = node_collection.find(
                    {
                        'member_of': univ_gst._id,
                        'group_set': mis_admin_grp._id,
                        'relation_set.organization_belongs_to_state': ObjectId(state_id)
                    }).sort('name', 1)

            if university_cur.count():
                for d in university_cur:
                    universities.append([str(d._id), d.name])

            else:
                error_message = "No University found for the selected State"
                raise Exception(error_message)

            return HttpResponse(json.dumps(universities))

        else:
            error_message = " UniversityFetchError: Either not an ajax call or not a GET request!!!"
            return HttpResponse(json.dumps({'message': " UniversityFetchError - Something went wrong in ajax call !!! \n\n Please contact system administrator."}))

    except Exception as e:
        error_message = str(e)
        return HttpResponse(json.dumps({'message': error_message}))



# MIS Reports
@get_execution_time
def get_detailed_report(request, group_id):
  """
  This view returns list of students along with required data based on selection criteria
  to student_data_review.html

  Arguments:
  group_id - ObjectId of the currently selected group

  Returns:
  A dictionary consisting of following key-value pairs:-
  success - Boolean giving the state of ajax call
  message - Basestring giving the error/information message
  """
  response_dict = {'success': False, 'message': ""}
  column_header = []
  group_name, group_id = get_group_name_id(group_id)
  app_set_id = None
  try:
    if request.is_ajax() and request.method == "POST":
      query_rcvd = str(request.POST.get("query", ''))
      gst_name = str(request.POST.get("gst_name", ''))
      if gst_name == "Event":
          gst_name = "Classroom Session"
      person_gst = node_collection.one({'_type': "GSystemType", 'name': gst_name})
      gapp_gst = node_collection.one({'_type':'MetaType','name':"GAPP"})
      mis_gapp = node_collection.one({'member_of':gapp_gst._id,'name':"MIS"})
      app_id = mis_gapp._id
      result_set = None
      if query_rcvd:
        query = eval(query_rcvd)

      mis_admin = node_collection.one({"_type": "Group", "name": "MIS_admin"}, {"_id": 1})
      if person_gst.name == "Voluntary Teacher":
          column_header = [u'University', u'College',u'Name', u'Email ID', u'Phone', u'Street',u'Events',u'College-Course']

          rec = node_collection.collection.aggregate([{'$match': query},
                                      {'$project': {'_id': 0,
                                                    'stud_id': '$_id',
                                                    'Name': '$name',
                                                    'Email ID': '$attribute_set.email_id',
                                                    'Phone': '$attribute_set.mobile_number',
                                                    'Street': '$attribute_set.town_city',
                                                    'Events': '$relation_set.coordinator_of_event',
                                                    'College-Course': '$relation_set.trainer_teaches_course_in_college',
                                      }},
                                      {'$sort': {'Name': 1}}
                ])
      elif person_gst.name == "Classroom Session":
          app_set_id = person_gst._id
          column_header = [u'Name', u'Course', u'VT',u'University', u'College', u'NUSSD Course',u'Module', u'Session', u'Start', u'End', u'Batch', u'Status',u'Attendance']

          rec = node_collection.collection.aggregate([{'$match': query},
                                {'$project': {'_id': 0,
                                              'stud_id': '$_id',
                                              'Name': '$name',
                                              'Course': '$attribute_set.nussd_course_type',
                                              'VT': '$relation_set.event_coordinator',
                                              'Session': '$relation_set.session_of',
                                              'Start': '$attribute_set.start_time',
                                              'End': '$attribute_set.end_time',
                                              'Batch': "$relation_set.event_has_batch",
                                              'Status': '$attribute_set.event_status',
                                              'Attendees': "$relation_set.has_attendees",
                                              'Attended': "$relation_set.has_attended",
                                }},
                                {'$sort': {'Start': 1}}
          ])

      elif person_gst.name == "Student":
          column_header = [u"Enrollment Code", u'Name', u'Reg# Date', u'Gender', u'Birth Date', u'Religion', u'Email ID', u'Languages Known', u'Caste', u'Contact Number (Mobile)', u'Alternate Number / Landline', u'House / Street', u'Village', u'Taluka', u'Town / City', u'District', u'State', u'Pin Code', u'Year of Passing 12th Standard', u'Degree Name / Highest Degree', u'Year of Study', u'Stream / Degree Specialization', u'College Enrolment Number / Roll No', u'College ( Graduation )', u'Are you registered for NSS?','University']
          rec = node_collection.collection.aggregate([{'$match': query},
                                      {'$project': {'_id': 0,
                                                    'stud_id': '$_id',
                                                    'Enrollment Code': '$attribute_set.enrollment_code',
                                                    'Name': '$name',
                                                    # 'First Name': '$attribute_set.first_name',
                                                    # 'Middle Name': '$attribute_set.middle_name',
                                                    # 'Last Name': '$attribute_set.last_name',
                                                    'Reg# Date': '$attribute_set.registration_date',
                                                    'Gender': '$attribute_set.gender',
                                                    'Birth Date': '$attribute_set.dob',
                                                    'Religion': '$attribute_set.religion',
                                                    'Email ID': '$attribute_set.email_id',
                                                    'Languages Known': '$attribute_set.languages_known',
                                                    'Caste': '$relation_set.student_of_caste_category',
                                                    'Contact Number (Mobile)': '$attribute_set.mobile_number',
                                                    'Alternate Number / Landline': '$attribute_set.alternate_number',
                                                    'House / Street': '$attribute_set.house_street',
                                                    'Village': '$attribute_set.village',
                                                    'Taluka': '$attribute_set.taluka',
                                                    'Town / City': '$attribute_set.town_city',
                                                    'District': '$relation_set.person_belongs_to_district',
                                                    'State': '$relation_set.person_belongs_to_state',
                                                    'Pin Code': '$attribute_set.pin_code',
                                                    'Year of Passing 12th Standard': '$attribute_set.12_passing_year',
                                                    'Degree Name / Highest Degree': '$attribute_set.degree_name',
                                                    'Year of Study': '$attribute_set.degree_year',
                                                    'Stream / Degree Specialization': '$attribute_set.degree_specialization',
                                                    'College Enrolment Number / Roll No': '$attribute_set.college_enroll_num',
                                                    'College ( Graduation )': '$relation_set.student_belongs_to_college',
                                                    'University': '$relation_set.student_belongs_to_university',
                                                    'Are you registered for NSS?': '$attribute_set.is_nss_registered'
                                      }},
                                      {'$sort': {'Enrollment Code': 1}}
                ])

      json_data = []
      filename = ""
      course_section_node_id = course_subsection_node = None
      result_set = rec["result"]
      if result_set:
        # old_dict = result_set[0]
        for old_dict in result_set:
          if old_dict:
            if person_gst.name == "Voluntary Teacher":
                str_colg_course = ""
                if 'Events' in old_dict:
                    if old_dict['Events']:
                        if old_dict['Events'][0]:
                            old_dict['Events'] = str(len(old_dict['Events'][0]))
                        else:
                            old_dict['Events'] = [0]

                old_colg = []
                if 'College-Course' in old_dict:
                    if old_dict['College-Course']:
                        if old_dict["College-Course"][0]:
                            for old_dictcc in old_dict["College-Course"][0]:
                                # old_dictcc is one list holding Course and College
                                first = True
                                for colg_course in old_dictcc:
                                    n = node_collection.one({'_id': ObjectId(colg_course)})
                                    if 'College' in n.member_of_names_list:
                                      if 'College' in old_dict:
                                        if n.name not in old_colg:
                                            old_colg.append(n.name)
                                        else:
                                            pass
                                      else:
                                          old_colg.append(n.name)
                                      str_colg = ""
                                      for each in old_colg:
                                          str_colg += each +" \n"
                                      old_dict.update({'College': str(str_colg)})
                                      if n.relation_set:
                                        for rel in n.relation_set:
                                          if rel and 'college_affiliated_to' in rel:
                                            univ_id = rel['college_affiliated_to'][0]
                                            univ_name = node_collection.one({'_id': ObjectId(univ_id)}).name
                                            if 'University' in old_dict and univ_name not in old_dict['University']:
                                              old_univ = old_dict['University']+"; "
                                            else:
                                              old_univ = ""
                                            new_univ_list = str(old_univ) + univ_name
                                            old_dict.update({'University': new_univ_list})
                                    str_colg_course += n.name
                                    if first:
                                        str_colg_course += " - "
                                    else:
                                        str_colg_course += "; "
                                    first = False
                    old_dict["College-Course"][0] = str_colg_course

                else:
                    old_dict.update({'College': "Not Assigned"})
                    old_dict.update({'University': "Not Assigned"})

            if person_gst.name == "Classroom Session":
                if u'Attendees' in old_dict:
                    if old_dict['Attendees']:
                        old_dict['Attendees'] = len(old_dict['Attendees'][0])
                    else:
                        old_dict['Attendees'] = "Not Applicable"
                if u'Attended' in old_dict:
                    if old_dict['Attended']:
                        old_dict['Attended'] = len(old_dict['Attended'][0])
                    else:
                        old_dict['Attended'] = "Not Applicable"
                if old_dict['Attended'] != "Not Applicable" and old_dict['Attendees'] != "Not Applicable":

                    attendance_percent = (old_dict['Attended']/float(old_dict['Attendees']))*100
                    old_dict['Attendance'] = str(round(attendance_percent,2))+" %"
                else:
                    old_dict['Attendance'] = "Pending"

                del old_dict['Attended']
                del old_dict['Attendees']
                if u"Session" in old_dict:
                   course_subsection_node = node_collection.one({'_id': ObjectId(old_dict['Session'][0][0])})
                   if course_subsection_node:
                     course_section_node_id = course_subsection_node.prior_node[0]
                     old_dict.update({'Module': [[course_section_node_id]]})
                   if course_section_node_id:
                     course_section_node = node_collection.one({'_id': ObjectId(course_section_node_id)})
                     nussd_course_node = course_section_node.prior_node[0]
                     old_dict.update({'NUSSD Course': [[nussd_course_node]]})
                if u"stud_id" in old_dict:
                  event_node = node_collection.one({'_id': ObjectId(old_dict['stud_id'])})
                  if event_node:
                    colg_group_id = event_node.group_set[0]
                    colg_group_node = node_collection.one({'_id':ObjectId(colg_group_id)})
                    if colg_group_node.relation_set:
                      for rel in colg_group_node.relation_set:
                        if rel and 'group_of' in rel:
                          colg_node_id = rel['group_of'][0]
                          colg_node = node_collection.one({'_id': ObjectId(colg_node_id)},{'name':1,'relation_set':1})
                          colg_node_name = colg_node.name
                          old_dict.update({'College': colg_node_name})
                          if colg_node.relation_set:
                            for rel in colg_node.relation_set:
                              if rel and 'college_affiliated_to' in rel:
                                univ_id = rel['college_affiliated_to'][0]
                                old_dict.update({'University': [[univ_id]]})
      if result_set:
        for each_dict in result_set:
          new_dict = {}
          for each_key in each_dict:
            if each_dict[each_key]:
              if type(each_dict[each_key]) == list:
                data = each_dict[each_key][0]
              else:
                data = each_dict[each_key]

              if type(data) == list:
                # Perform parsing
                if type(data) == list:
                  # Perform parsing
                  if type(data[0]) in [unicode, basestring, int]:
                    new_dict[each_key] = ', '.join(str(d) for d in data)
                  elif type(data[0]) in [ObjectId]:
                    # new_dict[each_key] = str(data)
                    d_list = []
                    for oid in data:
                      d = node_collection.one({'_id': oid}, {'name': 1})
                      d_list.append(str(d.name))
                    new_dict[each_key] = ', '.join(str(n) for n in d_list)
                elif type(data) == datetime.datetime:
                  new_dict[each_key] = data.strftime("%d/%m/%Y")
                elif type(data) == long:
                  new_dict[each_key] = str(data)
                elif type(data) == bool:
                  if data:
                    new_dict[each_key] = "Yes"
                  else:
                    new_dict[each_key] = "No"
                else:
                  new_dict[each_key] = str(data)

              else:
                # Perform parsing
                if type(data) == list:
                  # Perform parsing
                  if type(data[0]) in [unicode, basestring, int]:
                    new_dict[each_key] = ', '.join(str(d) for d in data)
                  elif type(data[0]) in [ObjectId]:
                    new_dict[each_key] = str(data)

                elif type(data) == datetime.datetime:
                  new_dict[each_key] = data.strftime("%d/%m/%Y")

                elif type(data) == long:
                  new_dict[each_key] = str(data)

                elif type(data) == bool:
                  if data:
                    new_dict[each_key] = "Yes"
                  else:
                    new_dict[each_key] = "No"

                else:
                  new_dict[each_key] = str(data)

            else:
              new_dict[each_key] = ""
          json_data.append(new_dict)

        # Start: CSV file processing -------------------------------------------

        t = time.strftime("%c").replace(":", "_").replace(" ", "_")
        filename = "csv/" + gst_name + "_" + t + ".csv"
        filepath = os.path.join(STATIC_ROOT, filename)
        filedir = os.path.dirname(filepath)
        if not os.path.exists(filedir):
          os.makedirs(filedir)
        with open(filepath, 'wb') as csv_file:
          fw = csv.DictWriter(csv_file, delimiter=',', fieldnames=column_header)
          fw.writerow(dict((col,col) for col in column_header))
          for row in json_data:
            v = {}
            v["stud_id"] = row.pop("stud_id")
            fw.writerow(row)
            row.update(v)
        # End: CSV file processing --------------------------------------------

      if person_gst.name == "Voluntary Teacher":
          # Column headers to be displayed on html
          column_headers = [
              ('University', 'University'),
              ('College', 'College'),
              ("Name", "Name"),
              ("Email ID", "Email ID"),
              ("Phone", "Phone"),
              ("Street", "Street"),
              ("Events", "Events"),
              ("College-Course", "College-Course"),
          ]
      elif person_gst.name == "Classroom Session":
          column_headers = [
              ("University", "University"),
              ("College", "College"),
              ("Name", "Name"),
              ("Course", "Course"),
              ("VT", "VT"),
              ("NUSSD Course", "NUSSD Course"),
              ("Module", "Module"),
              ('Session', 'Session'),
              ('Start', 'Start'),
              ('End', 'End'),
              ('Batch', 'Batch'),
              ('Status', 'Status'),
              ('Attendance', 'Attendance'),

          ]
      elif person_gst.name == "Student":
          column_headers = [
              ('University', 'University'),
              ('College ( Graduation )', 'College'),
              ("Name", "Name"),
              ("Enrollment Code", "Enr Code"),
              ("Email ID", "Email ID"),
              ('Year of Study', 'Year of Study'),
              ('Contact Number (Mobile)', 'Phone'),
              ('Degree Name / Highest Degree', 'Degree'),
              ('House / Street', 'Street')
          ]

      students_count = len(json_data)
      response_dict["success"] = True
      response_dict["groupid"] = group_id
      response_dict["app_id"] = app_id
      response_dict["app_set_id"] = app_set_id
      response_dict["filename"] = filename
      response_dict["students_count"] = students_count
      response_dict["column_headers"] = column_headers
      response_dict["students_data_set"] = json_data
      return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

    else:
      error_message = "ReportFetchError: Either not an ajax call or not a POST request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

  except OSError as oe:
    error_message = "ReportFetchError: " + str(oe) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

  except Exception as e:
    error_message = "ReportFetchError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))


def get_resource_by_oid(request, group_id):

    oid = request.GET.get('oid', None)
    if oid:
      # print "oid : ", oid
      node_obj = node_collection.one({  '_id': ObjectId(oid)},
                                      {
                                        'name': 1,
                                        'altnames': 1,
                                        'content': 1,
                                        '_id': 0
                                      }
                                    )
      return HttpResponse(json.dumps(node_obj))

    return HttpResponse('false')


def get_resource_by_oid_list(request, group_id):

    oid_list = request.GET.get('oid_list', None)

    oid_list = eval(oid_list)
    # print oid_list
    oid_list = [ObjectId(each_oid) for each_oid in oid_list if each_oid]

    if oid_list:

      node_obj = node_collection.find({  '_id': {'$in': oid_list}},
                                      {
                                        'name': 1,
                                        'altnames': 1,
                                        'content': 1,
                                        '_id': 1
                                      }
                                    )

      # print node_obj.count()
      if node_obj.count() > 0:
          node_list = [n for n in node_obj]
          # print node_list
          return HttpResponse(json.dumps(node_list, cls=NodeJSONEncoder))
      else:
          pass

    return HttpResponse('false')


def show_coll_cards(request, group_id):

    node_id = request.GET.get('node_id')
    node = node_collection.one({'_id': ObjectId(node_id)})

    node_collection_set = list(node.collection_set)
    coll_objs = node_collection.find({'_id': {'$in': node_collection_set} })

    return render_to_response('ndf/collection_set_cards.html',
            {
                'group_id': group_id, 'groupid': group_id,
                'coll_objs': coll_objs, 'node': node
            },
            context_instance=RequestContext(request))




def get_visits_count(request, group_id):
	'''
	Accepts:
	* group_id
	* current-url
		pathname used to search in benchmark_collection 'calling_url'
	* group_name
		To avoid fetching group_obj and then name
	* get_params
		get_params is used for get-parameters
		This param is passed only in case of collections
		Currently, Course and Event player are only considered.

	Actions:
	* Fetches from benchmark_collection,
		the total instances matching the query
	* From the total, fetches user related instances

	Returns:
	* success (i.e True/False)
	* Count of total visits
	* Count of user visits
	'''
	response_dict = {'success': False, 'total_views': 0}
	try:
		curr_url = request.GET.get('curr_url','')
		get_params =  request.GET.get('get_params','')
		# group_name = request.GET.get('group_name','')
		# if not group_name:
		group_obj   = get_group_name_id(group_id, get_obj=True)
		group_id    = group_obj._id
		group_name  = group_obj.name
		group_altnames = group_obj.altnames

		group_id_str = str(group_id)
		query = {}
		curr_url_other = []
		if curr_url and group_name:

			if group_id_str in curr_url:
				curr_url_other = [curr_url.replace(group_id_str,group_name), curr_url.replace(group_id_str,group_altnames)]

			elif group_name in curr_url:
				curr_url_other = [curr_url.replace(group_name,group_id_str), curr_url.replace(group_name,group_altnames)]

			elif group_altnames in curr_url:
				curr_url_other = [curr_url.replace(group_altnames,group_id_str), curr_url.replace(group_altnames,group_name)]

			# print "\n curr_url_other\n",curr_url_other
			curr_url_other.append(curr_url)
			query = {'calling_url': {'$in': curr_url_other}}
			# query = {'calling_url': {'$in': [curr_url,curr_url_other]}}
			if get_params:
				query = {'calling_url': {'$regex': u"/"+ unicode(get_params)},'name': "collection_nav"}

			# print "\n\nquery", query
			total_views = benchmark_collection.find(query,{'name':1})
			response_dict['total_views'] = total_views.count()
			if request.user.is_authenticated():
				username = request.user.username
				user_views = total_views.where("this.user =='"+str(username)+"'")
				response_dict['user_views'] = user_views.count()
		response_dict['success'] = True
		return HttpResponse(json.dumps(response_dict))
	except Exception as e:
		print e
		return HttpResponse(json.dumps(response_dict))

@get_execution_time
def get_ckeditor(request,group_id):
    ckeditor_toolbar_val = request.GET.get('ckeditor_toolbar')
    return render_to_response('ndf/html_editor.html',
            {
                'group_id': group_id, 'groupid': group_id,
                'ckeditor_toolbar': ckeditor_toolbar_val
            },
            context_instance=RequestContext(request))

@get_execution_time
def get_gin_line_template(request,group_id,node_id):
    node_obj = node_collection.one({'_id': ObjectId(node_id)})
    global_disc_all_replies = []
    thread_node = get_thread_node(node_id)

    allow_to_comment = node_thread_access(group_id, node_obj)
    all_replies =  get_disc_replies(thread_node, group_id ,global_disc_all_replies)
    return render_to_response('ndf/gin-line-texteditor.html',
            {
                'group_id': group_id, 'groupid': group_id,
                'node': node_obj,
                'all_replies' : all_replies,
                'thread_node':thread_node,
                'allow_to_comment':allow_to_comment

            },
            context_instance=RequestContext(request))

@get_execution_time
def course_create_collection(request, group_id):
  is_create_collection =  request.GET.get('is_create_collection','')
  is_add_to_collection =  request.GET.get('is_add_to_collection','')
  is_raw_material =  request.GET.get('is_raw_material','')
  is_gallery =  request.GET.get('is_gallery','')
  if is_raw_material == "true":
    coll_redir = "raw-material"
  else:
    coll_redir = "gallery"
  result_cur = node_collection.find({
                          'member_of': {'$in': [GST_FILE._id, GST_PAGE._id]},
                                            'group_set': {'$all': [ObjectId(group_id)]},
                                            '$or': [
                                                {'access_policy': u"PUBLIC"},
                                                {'$and': [
                                                    {'access_policy': u"PRIVATE"},
                                                    {'created_by': request.user.id}
                                                ]
                                             }
                                            ],
                                            'collection_set': {'$exists': "true", '$not': {'$size': 0} }
                                        }).sort("last_update", -1)
  # print "\n\n\n result",result_cur.count()


  return render_to_response('ndf/course_create_collection.html',
    {
     "coll_redir" :coll_redir ,"group_id":group_id,"result_cur":result_cur,"is_create_collection":is_create_collection,"is_add_to_collection":is_add_to_collection
    },context_instance=RequestContext(request))

@get_execution_time
def course_create_note(request, group_id):
  img_list = request.GET.get('img_list','')
  audio_list = request.GET.get('audio_list','')
  video_list = request.GET.get('video_list','')
  img_res = img_list.split(',')
  audio_res = audio_list.split(',')
  video_res = video_list.split(',')
  # print "\n\n\nfetch_res",audio_res,img_res,video_res
  # print "\n\n",fetch_res
  # # print "image_coll",image_coll
  return render_to_response('ndf/course_create_note.html',
      {
        "group_id":group_id,"img_res":img_res,"audio_res":audio_res,"video_res":video_res
      },context_instance=RequestContext(request))

@get_execution_time
def adminRenderGraph(request,group_id,node_id=None,graph_type="concept"):
  '''
  Renders the Concept Graph, Collection Graph, Dependency Graph
  '''
  try :
    if request.is_ajax() and request.method == "GET":
      if node_id:
          req_node = node_collection.one({'_type':'GSystem','_id':ObjectId(node_id)})
      template = "ndf/graph_"+graph_type+".html"
      variable = RequestContext(request, { 'group_id':group_id,'groupid':group_id , 'node':req_node })
      return render_to_response(template, { 'group_id':group_id,'groupid':group_id , 'node':req_node })
  except Exception as e :
    print "from "+ graph_type +" Graph, exception",e,"\n\n"

@login_required
@get_execution_time
def upload_file_ckeditor(request,group_id):
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    group_obj = node_collection.one({'_id': ObjectId(group_id)})
    title = request.POST.get('context_name','')
    usrid = request.user.id

    from gnowsys_ndf.ndf.views.filehive import write_files

    gs_obj_list = write_files(request, group_id)
    gs_obj_id = gs_obj_list[0]['if_file']['original']['relurl']
    print "gs_obj_list: ", gs_obj_id

    discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
    for each_gs_file in gs_obj_list:
        #set interaction-settings
        create_gattribute(each_gs_file._id, discussion_enable_at, True)
        return_status = create_thread_for_node(request,group_obj._id, each_gs_file)

    return StreamingHttpResponse(gs_obj_id)
    # if title == "gallery":
    # else:
    #     return HttpResponseRedirect(reverse('course_raw_material', kwargs={'group_id': group_id}))
    # return HttpResponseRedirect(url_name)

# @login_required
# @get_execution_time
# def upload_file(request,group_id):
#     try:
#         group_id = ObjectId(group_id)
#     except:
#         group_name, group_id = get_group_name_id(group_id)

#     group_obj = node_collection.one({'_id': ObjectId(group_id)})
#     title = request.POST.get('context_name','')
#     usrid = request.user.id

#     from gnowsys_ndf.ndf.views.filehive import write_files

#     gs_obj_list = write_files(request, group_id)
#     gs_obj_id = gs_obj_list[0]['_id']

#     discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
#     for each_gs_file in gs_obj_list:
#         each_gs_file.status = u"PUBLISHED"
#         each_gs_file.save()
#         #set interaction-settings
#         create_gattribute(each_gs_file._id, discussion_enable_at, True)
#         return_status = create_thread_for_node(request,group_obj._id, each_gs_file)

#     # return HttpResponseRedirect(reverse('homepage',kwargs={'group_id': group_id, 'groupid':group_id}))
#     return HttpResponseRedirect( reverse('file_detail', kwargs={"group_id": group_id,'_id':gs_obj_id}) )

@login_required
def search_users(request, group_id):
    if request.is_ajax() and request.method == "GET":
        from bson import json_util
        username_str = request.GET.get("username_str", '')
        subscription_status_val = request.GET.get("subscription_status_val", '')
        if subscription_status_val:
            filtered_users = []
            users_data = User.objects.filter(username__icontains=str(username_str)).values_list('id', 'username')
            group_object = node_collection.one({'_id': ObjectId(group_id)})
            for each_filtered_user in users_data:
                if each_filtered_user[0] in group_object.author_set:
                    if each_filtered_user[0] in group_object.group_admin:
                        filtered_users.append(each_filtered_user+(True,True))
                    else:
                        filtered_users.append(each_filtered_user+(True,False))
                else:
                    if each_filtered_user[0] in group_object.group_admin:
                        filtered_users.append(each_filtered_user+(False,True))
                    else:
                        filtered_users.append(each_filtered_user+(False,False))
        else:
            filtered_users = User.objects.filter(username__icontains=str(username_str)).values_list('id', 'username')
        return HttpResponse(json_util.dumps(filtered_users, cls=NodeJSONEncoder))


@login_required
def save_user_password(request, group_id):
    response_dict = {'success': False}
    if request.is_ajax() and request.method == "POST":
        user_id = request.POST.get("stud_id", '')
        new_password = request.POST.get("new_password", '')
        user_obj = User.objects.get(pk=int(user_id))
        user_obj.set_password(str(new_password))
        # print "\n\n new_password ", new_password
        user_obj.save()
        response_dict['success'] = True
    return HttpResponse(json.dumps(response_dict))

@login_required
@get_execution_time
def upload_video_thumbnail(request,group_id):
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    # group_obj = node_collection.one({'_id': ObjectId(group_id)})
    # title = request.POST.get('context_name','')
    parent_node = request.POST.get('parent_node','')
    # print "\n\nparent_node",request.POST
    usrid = request.user.id
    from gnowsys_ndf.ndf.views.filehive import write_files

    gs_obj_list = write_files(request, group_id)

    gs_obj_id = gs_obj_list[0]['_id']
    if gs_obj_id:
      gs_obj_node = node_collection.one({'_id':ObjectId(gs_obj_id)})
      pr_obj_node = node_collection.one({'_id':ObjectId(parent_node)})

      has_thumbnail_rt = node_collection.one({'_type': 'RelationType', 'name': unicode('has_thumbnail') })

      gr_node = create_grelation(pr_obj_node._id, has_thumbnail_rt, gs_obj_id)
      # print "\n\n\ngr_node",gr_node
      warehouse_grp_obj = node_collection.one({'_type': "Group", 'name': "warehouse"})
      node_collection.collection.update({'_id': ObjectId(gs_obj_id)}, {'$set': {'group_set': [warehouse_grp_obj._id] }}, upsert=False, multi=False)

    return StreamingHttpResponse(str(gs_obj_id))


@get_execution_time
def get_paged_images(request, group_id):
  is_create_collection =  request.GET.get('is_create_collection','')
  is_add_to_collection =  request.GET.get('is_add_to_collection','')
  result_cur = node_collection.find({
                          'member_of': {'$in': [GST_FILE._id, GST_PAGE._id]},
                                            'group_set': {'$all': [ObjectId(group_id)]},
                                            '$or': [
                                                {'access_policy': u"PUBLIC"},
                                                {'$and': [
                                                    {'access_policy': u"PRIVATE"},
                                                    {'created_by': request.user.id}
                                                ]
                                             }
                                            ],
                                            'collection_set': {'$exists': "true", '$not': {'$size': 0} }
                                        }).sort("last_update", -1)
  # print "\n\n\n result",result_cur.count()


  return render_to_response('ndf/course_create_collection.html',
    {
      "group_id":group_id,"result_cur":result_cur,"is_create_collection":is_create_collection,"is_add_to_collection":is_add_to_collection
    },context_instance=RequestContext(request))


@get_execution_time
def get_templates_page(request, group_id):
  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)
  templates_gst = node_collection.one({"_type":"GSystemType","name":"Template"})
  if templates_gst._id:
    # templates_cur = node_collection.find({"member_of":ObjectId(GST_PAGE._id),"type_of":ObjectId(templates_gst._id)})
    templates_cur = node_collection.find({"type_of":ObjectId(templates_gst._id)})
  template = "ndf/templates_list.html"
  already_uploaded=request.GET.getlist('var',"")
  variable = RequestContext(request, {'groupid':group_id,'group_id':group_id,'templates_cur':templates_cur })
  return render_to_response(template, variable)


@get_execution_time
def get_group_templates_page(request, group_id):
  # try:
  #     group_id = ObjectId(group_id)
  # except:
  #     group_name, group_id = get_group_name_id(group_id)
  templates_gst = node_collection.one({"_type":"GSystemType","name":"Template"})
  if templates_gst:
    templates_cur = node_collection.find({"member_of":ObjectId(GST_PAGE._id),"type_of":ObjectId(templates_gst._id)})
  template = "ndf/group_templates_list.html"
  # already_uploaded=request.GET.getlist('var',"")
  variable = RequestContext(request, {'templates_cur':templates_cur })
  return render_to_response(template, variable)

'''
@login_required
def get_group_pages(request, group_id):
    except_collection_set_of_id = request.GET.get('except_collection_set_of_id', None)
    except_collection_set_of_obj = Node.get_node_by_id(except_collection_set_of_id)
    except_collection_set = []
    if except_collection_set_of_obj:
        except_collection_set = except_collection_set_of_obj.collection_set
    gst_page_name, gst_page_id = GSystemType.get_gst_name_id('Page')
    gst_blog_page_name, gst_blog_page_id = GSystemType.get_gst_name_id('Blog page')
    gst_info_page_name, gst_info_page_id = GSystemType.get_gst_name_id('Info page')
    pages_cur = node_collection.find({
                                      '_type': 'GSystem',
                                      'member_of': ObjectId(gst_page_id),
                                      'type_of': {'$nin': [gst_blog_page_id, gst_info_page_id]},
                                      'group_set': ObjectId(group_id),
                                      '_id': {'$nin': except_collection_set}
                                    }).sort('last_update', -1)
    template = "ndf/group_pages.html"
    card_class = 'activity-page'
    variable = RequestContext(request, {'cursor': pages_cur, 'groupid': group_id, 'group_id': group_id, 'card_class': card_class })
    return render_to_response(template, variable)
'''

@login_required
def get_group_resources(request, group_id, res_type="Page"):
    except_collection_set = []
    res_cur = None
    template = "ndf/group_pages.html"
    card_class = 'activity-page'

    try:
        res_query = {'_type': 'GSystem', 'group_set': ObjectId(group_id)}
        except_collection_set_of_id = request.GET.get('except_collection_set_of_id', None)

        except_collection_set_of_obj = Node.get_node_by_id(except_collection_set_of_id)
        if except_collection_set_of_obj:
            except_collection_set = except_collection_set_of_obj.collection_set
            if except_collection_set:
                res_query.update({'_id': {'$nin': except_collection_set}})
        if res_type.lower() == "page":
            gst_page_name, gst_page_id = GSystemType.get_gst_name_id('Page')
            gst_blog_type_name, gst_blog_type_id = GSystemType.get_gst_name_id("Blog page")
            gst_info_type_name, gst_info_type_id = GSystemType.get_gst_name_id("Info page")
            res_query.update({'type_of': {'$nin': [gst_blog_type_id, gst_info_type_id]}})
            res_query.update({'member_of': gst_page_id})

        elif res_type.lower() == "quiz":
            gst_quizitem_name, gst_quizitem_id = GSystemType.get_gst_name_id('QuizItem')
            gst_quizitemevent_name, gst_quizitemevent_id = GSystemType.get_gst_name_id('QuizItemEvent')
            res_query.update({'member_of': {"$in": [gst_quizitem_id, gst_quizitemevent_id]}})
        res_cur = node_collection.find(res_query).sort('last_update', -1)
    except Exception as get_group_resources_err:
      print "\n Error occurred in get_group_resources(). Error: {0}".format(str(get_group_resources_err))
      pass

    variable = RequestContext(request, {'cursor': res_cur, 'groupid': group_id, 'group_id': group_id, 'card_class': card_class })
    return render_to_response(template, variable)

def get_info_pages(request, group_id):
    node_id = request.POST.get("node_id", '')
    page_type = request.POST.get("page_type", '')
    node  = Node.get_node_obj_from_id_or_obj(node_id, GSystem)
    template = "ndf/get_info_pages.html"
    variable = RequestContext(request, {'node': node, 'groupid': group_id, 'group_id': group_id,'page_type':unicode(page_type) })
    return render_to_response(template, variable)


@get_execution_time
def add_transcript(request, group_id):
  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)
  if request.is_ajax() and request.method == "POST":
    node_id = request.POST.get("nodeid", '')
    trans_text = request.POST.get("transcript_text", '')
    trans_of  = node_collection.one({'$and':[{'name':'has_transcript'},{'_type':'AttributeType'}]})
    if node_id and trans_of:
      create_gattribute(ObjectId(node_id), trans_of,unicode(trans_text))

  return HttpResponse(json.dumps("success"))


@get_execution_time
def get_video_player(request, group_id):
  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)
  node_id = request.GET.get("datasrc", '')
  if node_id:
    node_obj = node_collection.one({'_id': ObjectId(node_id) })
  return render_to_response('ndf/widget_video_player.html',
            {
                'group_id': group_id, 'groupid': group_id,'video_obj':node_obj
            },
            context_instance=RequestContext(request))

@get_execution_time
def get_audio_player(request, group_id):
  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)
  node_id = request.GET.get("datasrc", '')
  if node_id:
    node_obj = node_collection.one({'_id': ObjectId(node_id) })

  return render_to_response('ndf/widget_audio_player.html',
            {
                'group_id': group_id, 'groupid': group_id,'audio_obj':node_obj
            },
            context_instance=RequestContext(request))

@login_required
@get_execution_time
def get_jhapps(request,group_id):
  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)

  group_obj = node_collection.one({'_id': ObjectId(group_id)})
  jhapp_list = []
  for each in GSTUDIO_SUPPORTED_JHAPPS:
    each_node = node_collection.one({'name':unicode(each)})
    if each_node:
      jhapp_list.append(ObjectId(each_node._id))
  jhapp_res = node_collection.find({'member_of': {'$in': jhapp_list}})

  return render_to_response("ndf/jhapp_list.html",RequestContext(request, {"groupid":group_id, "group_id":group_id,'jhapp_res':jhapp_res}))

@login_required
@get_execution_time
def add_asset(request,group_id):
  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)
  group_obj = Group.get_group_name_id(group_id, get_obj=True)
  topic_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})
  topic_nodes = node_collection.find({'member_of': {'$in': [topic_gst._id]}})
  context_variables = {'group_id':group_id, 'groupid':group_id,'edit': False}
  node_id = request.GET.get('node_id', None)
  title = request.GET.get('title', None)
  node_obj = node_collection.one({'_id': ObjectId(node_id)})
  if node_obj:
    context_variables.update({'asset_obj': node_obj,'topic_nodes':topic_nodes})
    context_variables.update({'edit': True})
  context_variables.update({'group_obj': group_obj, 'group_name': group_obj.name, 'title':title,'topic_nodes':topic_nodes})
  return render_to_response("ndf/add_asset.html",RequestContext(request,
    context_variables))

@login_required
@get_execution_time
def create_edit_asset(request,group_id):
  
  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)
  group_obj = Group.get_group_name_id(group_id, get_obj=True)
  selected_topic =  request.POST.get("topic_list", '')
  # selected_topic_list =  request.POST.getlist("coll_arr[]", '')
  
  if request.method == "POST":
    asset_name =  str(request.POST.get("asset_name", '')).strip()
    asset_disp_name =  str(request.POST.get("asset_disp_name", '')).strip()
    asset_desc =  str(request.POST.get("asset_description", '')).strip()
    title =  request.POST.get("title", '')
    tags =  request.POST.get("sel_tags", [])

    if tags:
        tags = json.loads(tags)
    else:
        tags = []
    
    asset_lang =  request.POST.get("sel_asset_lang", '')
    
    is_raw_material = eval(request.POST.get('is_raw_material', "False"))
    # print "\nis_raw_material: ", is_raw_material, " type: ", type(is_raw_material)

    node_id = request.POST.get('node_id', None)
    asset_obj = create_asset(name=asset_name, group_id=group_id,
      created_by=request.user.id, content=unicode(asset_desc), node_id=node_id)


    asset_obj.fill_gstystem_values(tags=tags)
    
    rt_teaches = node_collection.one({'_type': "RelationType", 'name': unicode("teaches")})
    
    if selected_topic:
      # selected_topic_list = map(ObjectId,selected_topic_list)
      create_grelation(asset_obj._id,rt_teaches,ObjectId(selected_topic))
    if "asset@asset" not in asset_obj.tags and "base_unit" in group_obj.member_of_names_list:
      asset_obj.tags.append(u'asset@asset')


    # if is_raw_material and u'raw@material' not in asset_obj.tags and "base_unit" in group_obj.member_of_names_list:
    if is_raw_material and u'raw@material' not in asset_obj.tags:
      # marking Asset as RawMaterial
      asset_obj.tags.append(u'raw@material')

    elif not is_raw_material and u'raw@material' in asset_obj.tags:
      # elif not is_raw_material and u'raw@material' in asset_obj.tags and "base_unit" in group_obj.member_of_names_list:
      # UNmarking Asset as RawMaterial
      asset_obj.tags.remove(u'raw@material')
    
    if "announced_unit" in group_obj.member_of_names_list and title == "raw material":
      asset_obj.tags.append(u'raw@material')
    
    if ("announced_unit" in group_obj.member_of_names_list  or "Group" in group_obj.member_of_names_list) and "gallery" == title:
      asset_obj.tags.append(u'asset@gallery')    
    
    if "announced_unit" in group_obj.member_of_names_list  and title == None or title == "None":
      asset_obj.tags.append(u'asset@asset')

    if asset_lang:
      language = get_language_tuple(asset_lang)
      asset_obj.language = language
    if asset_disp_name:
      asset_obj.altnames = unicode(asset_disp_name)
    asset_obj.save()
    thread_node = create_thread_for_node(request,group_id, asset_obj)

    return HttpResponse("success")


@login_required
@get_execution_time
def add_assetcontent(request,group_id):
  asset_obj = request.POST.get('asset_obj','')
  if_subtitle = request.POST.get('if_subtitle','')
  if_transcript = request.POST.get('if_transcript','')
  if_alt_lang_file = request.POST.get('if_alt_file','')
  if_alt_format_file = request.POST.get('if_alt_format_file','')
  assetcontentid = request.POST.get('assetcontentid','')

  uploaded_files = request.FILES.getlist('filehive', [])
  uploaded_transcript = request.FILES.getlist('uploaded_transcript', [])
  uploaded_subtitle = request.FILES.getlist('uploaded_subtitle', [])
  uploaded_alt_lang_file = request.FILES.getlist('uploaded_alt_lang_file', [])

  subtitle_lang = request.POST.get('sel_sub_lang','')
  # sel_alt_value = request.POST.get('sel_alt_value','')
  alt_file_format = request.POST.get('sel_alt_fr_type','')

  asset_cont_desc = request.POST.get('asset_cont_desc','')
  asset_cont_name = request.POST.get('asset_cont_name','')
  node_id = request.POST.get('node_id',None)
  if if_subtitle == "True":
    file_name = uploaded_subtitle[0].name
    if not file_name:
      file_name = asset_cont_name
    subtitle_obj = create_assetcontent(asset_id=ObjectId(asset_obj),
      name=file_name, group_name_or_id=group_id, created_by=request.user.id, 
      files=uploaded_subtitle,resource_type='File', request=request)

    rt_subtitle = node_collection.one({'_type':'RelationType', 'name':'has_subtitle'})
    subtitle_list = [ObjectId(subtitle_obj._id)]

    subtitle_grels = triple_collection.find({'_type': 'GRelation', \
    'relation_type': rt_subtitle._id,'subject': ObjectId(assetcontentid)},
    {'_id': 0, 'right_subject': 1})
    for each_asset in subtitle_grels:
      subtitle_list.append(each_asset['right_subject'])
    #   sub_grel = create_grelation(ObjectId(assetcontentid), rt_subtitle, subtitle_list)

    altlang_node = create_grelation(ObjectId(assetcontentid), rt_subtitle, subtitle_list, **{'triple_scope':{'relation_type_scope':{u'alt_language': unicode(subtitle_lang)}, 'subject_scope': "many"}})

    return StreamingHttpResponse("success")


  if if_transcript == "True":
    file_name = uploaded_transcript[0].name
    if not file_name:
      file_name = asset_cont_name

    rt_transcript = node_collection.one({'_type':'RelationType', 'name':'has_transcript'})
    transcript_obj = create_assetcontent(asset_id=ObjectId(asset_obj),
      name=file_name,  group_name_or_id=group_id, created_by=request.user.id, 
      files=uploaded_transcript, resource_type='File', request=request)
    transcript_list = [ObjectId(transcript_obj._id)]

    transcript_grels = triple_collection.find({'_type': 'GRelation', \
    'relation_type': rt_transcript._id,'subject': ObjectId(assetcontentid)},
    {'_id': 0, 'right_subject': 1})
    for each_trans in transcript_grels:
      transcript_list.append(each_trans['right_subject'])
    trans_grel = create_grelation(ObjectId(assetcontentid), rt_transcript, transcript_list)
    return StreamingHttpResponse("success")

  if if_alt_lang_file == "True":
    file_name = uploaded_alt_lang_file[0].name
    if not file_name:
      file_name = asset_cont_name
    alt_file_type = request.POST.get('alt_file_type','')
    alt_lang_file_obj = create_assetcontent(asset_id=ObjectId(asset_obj), 
      name=file_name, group_name_or_id=group_id, created_by=request.user.id,
      files=uploaded_alt_lang_file,resource_type='File', request=request)
    rt_alt_content = node_collection.one({'_type':'RelationType', 'name':'has_alt_content'})
    alt_lang_file_list = [ObjectId(alt_lang_file_obj._id)]

    alt_lang_file_grels = triple_collection.find({'_type': 'GRelation', \
    'relation_type': rt_alt_content._id,'subject': ObjectId(assetcontentid)},
    {'_id': 0, 'right_subject': 1})
    for each_asset in alt_lang_file_grels:
      alt_lang_file_list.append(each_asset['right_subject'])

    alt_lang_file_node = create_grelation(ObjectId(assetcontentid), rt_alt_content, alt_lang_file_list, **{'triple_scope':{'relation_type_scope':{ alt_file_type : '' }, 'subject_scope': "many"}})

    return StreamingHttpResponse("success")

  create_assetcontent(ObjectId(asset_obj),asset_cont_name,group_id,
    request.user.id,content=asset_cont_desc,files=uploaded_files,
    resource_type='File', request=request)
  return StreamingHttpResponse("success")


def add_to_collection_set(request, group_id):
    child_node_id = request.POST.get('child_node_id', None)
    parent_node_id = request.POST.get('parent_node_id', None)

    parent_node_obj = Node.get_node_by_id(parent_node_id)
    if parent_node_obj and (ObjectId(child_node_id) not in parent_node_obj.collection_set):
        parent_node_obj.collection_set.append(ObjectId(child_node_id))
        parent_node_obj.save(group_id=group_id)
        from gnowsys_ndf.ndf.views.unit import _get_unit_hierarchy
        group_obj = Group.get_group_name_id(group_id, get_obj=True)
        return HttpResponse(json.dumps(_get_unit_hierarchy(group_obj)))
    else:
        return HttpResponse(0)


def delete_asset(request, group_id):
    if_delete_asset = request.POST.get('delete_asset', '')
    if_delete_asset_content = request.POST.get('delete_asset_content', '')
    if if_delete_asset == "True":
      asset_id = request.POST.get('asset_id', '')
      asset_obj = node_collection.one({'_id':ObjectId(asset_id)})
      if asset_obj:
        trash_resource(request,ObjectId(group_id),asset_obj._id)
      return HttpResponse('success')

    if if_delete_asset_content:
      file_list = request.POST.getlist('delete_files_list[]', '')
      for each_file in file_list:
        asset_cont_node = node_collection.one({'_id':ObjectId(each_file)})
        if asset_cont_node:
          trash_resource(request,ObjectId(group_id),ObjectId(asset_cont_node._id))
          del_rel = delete_grelation(subject_id=ObjectId(asset_cont_node._id),deletion_type=0)
          print '\nDeleted Node',del_rel
      return HttpResponse('success')


def get_metadata_page(request, group_id):
  node_id = request.POST.get('node_id', None)
  node_obj = node_collection.one({'_id':ObjectId(node_id)})
  return render_to_response('ndf/widget_metadata.html',
            {
                'group_id': group_id, 'groupid': group_id,
                'node_id':node_id,'node':node_obj
            },
            context_instance=RequestContext(request))

def get_admin_page_form(request, group_id):
  node_id = request.POST.get('node_id', None)
  node_obj = node_collection.one({'_id':ObjectId(node_id)})
  return render_to_response('ndf/widget_admin_page.html',
           {
              'group_id': group_id, 'groupid': group_id,
              'node_id':node_id,'node':node_obj
            },
            context_instance=RequestContext(request))

def get_help_page_form(request, group_id):
  node_id = request.POST.get('node_id', None)
  node_obj = node_collection.one({'_id':ObjectId(node_id)})
  return render_to_response('ndf/widget_help_page.html',
           {
              'group_id': group_id, 'groupid': group_id,
              'node_id':node_id,'node':node_obj
            },
            context_instance=RequestContext(request))

def get_interaction_widget(request, group_id):
  node_id = request.POST.get('node_id', None)
  node_obj = node_collection.one({'_id':ObjectId(node_id)})
  return render_to_response('ndf/widget_interaction.html',
            {
                'group_id': group_id, 'groupid': group_id,
                'node_id':node_id,'node':node_obj
            },
            context_instance=RequestContext(request)) 

def save_interactions(request, group_id):
  group_obj = get_group_name_id(group_id, get_obj=True)
  node_id = request.POST.get('node_id', None)
  node  = node_collection.one({"_id":ObjectId(node_id)})

  thread_create_val = request.POST.get("thread_create",'')

  # print "\n\n help_info_page  === ", help_info_page
  group_obj_member_of_names_list= group_obj.member_of_names_list
  if "base_unit" in group_obj_member_of_names_list:
    discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "player_discussion_enable"})
  else:
    discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
  if thread_create_val == "Yes":
    create_gattribute(node._id, discussion_enable_at, True)
    return_status = create_thread_for_node(request,group_id, node)
  else:
    create_gattribute(node._id, discussion_enable_at, False)
  return HttpResponseRedirect(reverse('view_course_page', kwargs={'group_id':ObjectId(group_id),'page_id': ObjectId(node._id)}))
  

def save_metadata(request, group_id):
  node_id = request.POST.get('node_id', None)
  node  = node_collection.one({"_id":ObjectId(node_id)})
  source = request.POST.get("source_val", "")
  copyright = request.POST.get("copyright_val", "")
  Based_url = request.POST.get("basedonurl_val", "")
  obj_list = request.POST.get("obj_list", "")

  if obj_list :
    for k, v in json.loads(obj_list).iteritems():
      attr_node = node_collection.one({'_type':'AttributeType','name':unicode(k)})
      if v is not None and (not isinstance(v,list) and "select" not in v.lower()) or (isinstance(v,list) and "select" not in v[0].lower() ):
        if attr_node:
          create_gattribute(ObjectId(node_id), attr_node, v)
      else:
          ga_node = triple_collection.find_one({'_type': "GAttribute",
               "subject": ObjectId(node_id), 'attribute_type': attr_node._id, 'status':"PUBLISHED"})
          if ga_node:
              d,dd = delete_gattribute(subject_id=None, deletion_type=1, **{'node_id': ga_node._id})
  if source:
    source_attr = node_collection.one({'_type':'AttributeType','name':'source'})
    create_gattribute(ObjectId(node_id), source_attr, source)

  if copyright:
    node.legal.copyright = unicode(copyright)
    node.save()

  if Based_url:
    basedurl_attr = node_collection.one({'_type':'AttributeType','name':'basedonurl'})
    create_gattribute(ObjectId(node_id), basedurl_attr, Based_url)
  if "Page" in node.member_of_names_list:
    return HttpResponseRedirect(reverse('view_course_page', kwargs={'group_id':ObjectId(group_id),'page_id': ObjectId(node._id)}))
  else:
    return HttpResponseRedirect(reverse('asset_detail', kwargs={'group_id':ObjectId(group_id),'asset_id': ObjectId(node._id)}))
  # return HttpResponse('success')

def export_to_epub(request, group_id, node_id):
    from gnowsys_ndf.ndf.views.export_to_epub import *
    response_dict = {'success': False}
    try:
        node_obj = node_collection.one({'_id': ObjectId(node_id)})
        epub_loc = create_epub(node_obj)
        zip_file = open(epub_loc, 'rb')
        response = HttpResponse(zip_file.read(), content_type="application/epub+zip")
        response['Content-Disposition'] = 'attachment; filename="'+ slugify(node_obj.name) + '.epub"'
        return response
    except Exception as export_fail:
        print "\n export_fail: ", export_fail
        pass
    return HttpResponseRedirect(reverse('unit_detail', kwargs={'group_id': group_id}))

def remove_related_doc(request, group_id):
    node = request.POST.get('node', None)
    selected_obj = request.POST.get('sel_file', None)
    node_obj = node_collection.one({'_id': ObjectId(node)})

    grel_name = request.POST.get('grel_name', None)
    asset_obj = request.POST.get('asset_obj', None)
    rel_node = triple_collection.one({'right_subject':ObjectId(selected_obj),'subject':ObjectId(node_obj.pk)})
    delete_grelation(subject_id=ObjectId(node_obj.pk), deletion_type=1, **{'node_id': ObjectId(rel_node._id)})
    return HttpResponse('success')

def get_translated_node(request, group_id):
    node_id = request.GET.get('node_id', None)
    language = request.GET.get('language', None)
    node_obj = Node.get_node_by_id(node_id)
    trans_node = get_lang_node(node_obj._id,language)
    if trans_node:
      return HttpResponse(json.dumps(trans_node, cls=NodeJSONEncoder))
    else:
      return HttpResponse(json.dumps(node_obj, cls=NodeJSONEncoder))


@get_execution_time
def get_rating_template(request, group_id):
  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)
    
  node_id = request.GET.get('node_id', None)
  node_obj = Node.get_node_by_id(ObjectId(node_id))
  is_comments = request.GET.get('if_comments', None)
  if is_comments == "True":
    is_comments = True
  else:
    is_comments = False

  return render_to_response('ndf/rating.html',
            {
              "group_id":group_id,"node":node_obj,"if_comments":is_comments,'nodeid':node_obj._id,
            },
            context_instance=RequestContext(request))

def delete_curriculum_node(request, group_id):
    node_id = request.POST.get('node_id', None)
    node_obj = Node.get_node_by_id(node_id)
    if node_obj:
      trash_resource(request,ObjectId(group_id),ObjectId(node_id))
      trash_resource(request,ObjectId(group_id),ObjectId(node_id))
      return HttpResponse("Success")

