''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
import datetime
import multiprocessing as mp
from difflib import HtmlDiff
import json
''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext
from mongokit import paginator
try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import LANGUAGES, GSTUDIO_BUDDY_LOGIN
from gnowsys_ndf.settings import GAPPS, GSTUDIO_SITE_NAME, GSTUDIO_NOTE_CREATE_POINTS
from gnowsys_ndf.ndf.models import Node, GSystem, Triple, Counter, Buddy
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.ndf.rcslib import RCS
# from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, get_translate_common_fields,get_page,get_resource_type,diff_string,get_node_metadata,create_grelation_list,get_execution_time,parse_data
from gnowsys_ndf.ndf.management.commands.data_entry import create_gattribute
from gnowsys_ndf.ndf.views.html_diff import htmldiff
from gnowsys_ndf.ndf.views.methods import get_versioned_page, get_page, get_resource_type, diff_string, node_thread_access
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation, get_group_name_id, create_thread_for_node,delete_grelation

from gnowsys_ndf.ndf.templatetags.ndf_tags import group_type_info, get_relation_value

from gnowsys_ndf.mobwrite.diff_match_patch import diff_match_patch


#######################################################################################################################################

gst_page = node_collection.one({'_type': 'GSystemType', 'name': GAPPS[0]})
history_manager = HistoryManager()
rcs = RCS()
app = gst_page

#######################################################################################################################################
# VIEWS DEFINED FOR GAPP -- 'PAGE'
#######################################################################################################################################




@get_execution_time
def page(request, group_id, app_id=None,page_no=1):
    """Renders a list of all 'Page-type-GSystems' available within the database.
    """
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    if app_id is None:
        app_ins = node_collection.find_one({'_type': "GSystemType", "name": "Page"})
        if app_ins:
            app_id = str(app_ins._id)
    from gnowsys_ndf.settings import GSTUDIO_NO_OF_OBJS_PP
    content=[]
    version=[]
    con=[]
    group_object = node_collection.one({'_id': ObjectId(group_id)})

    # Code for user shelf
    shelves = []
    shelf_list = {}
    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })


    if request.method == "POST":
        title = gst_page.name
        search_field = request.POST['search_field']
        page_nodes = node_collection.find({
                                            'member_of': {'$all': [ObjectId(app_id)]},
                                            '$or': [
                                              {'$and': [
                                                {'name': {'$regex': search_field, '$options': 'i'}},
                                                {'$or': [
                                                  {'access_policy': u"PUBLIC"},
                                                  {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
                                                  ]
                                                }
                                                ]
                                              },
                                              {'$and': [
                                                {'tags': {'$regex':search_field, '$options': 'i'}},
                                                {'$or': [
                                                  {'access_policy': u"PUBLIC"},
                                                  {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
                                                  ]
                                                }
                                                ]
                                              }
                                            ],
                                            'group_set': {'$all': [ObjectId(group_id)]},
                                            'status': {'$nin': ['HIDDEN']}
                                        }).sort('last_update', -1)
        paginator_pages = paginator.Paginator(page_nodes, page_no, GSTUDIO_NO_OF_OBJS_PP)
        return render_to_response("ndf/page_list.html",
                                  {'title': title,
                                   'appId':app._id,'shelf_list': shelf_list,'shelves': shelves,
                                   'searching': True, 'query': search_field,
                                   'page_nodes': page_nodes, 'groupid':group_id, 'group_id':group_id,
                                   'page_info':paginator_pages
                                  },
                                  context_instance=RequestContext(request)
        )

    elif gst_page._id == ObjectId(app_id):
        group_type = node_collection.one({'_id': ObjectId(group_id)})
        group_info=group_type_info(group_id)
        node = node_collection.find({'member_of':ObjectId(app_id)})
        title = gst_page.name
        """
          Below query returns only those documents:
          (a) which are pages,
          (b) which belongs to given group,
          (c) which has status either as DRAFT or PUBLISHED, and
          (d) which has access_policy either as PUBLIC or if PRIVATE then it's created_by must be the logged-in user
        """
        page_nodes = node_collection.find({'member_of': {'$all': [ObjectId(app_id)]},
                                               'group_set': {'$all': [ObjectId(group_id)]},
                                               '$or': [
                                                {'access_policy': u"PUBLIC"},
                                                {'$and': [
                                                  {'access_policy': u"PRIVATE"},
                                                  {'created_by': request.user.id}
                                                  ]
                                                }
                                               ],
                                               'status': {'$nin': ['HIDDEN']}
                                           }).sort('last_update', -1)
        paginator_pages = paginator.Paginator(page_nodes, page_no, GSTUDIO_NO_OF_OBJS_PP)
        return render_to_response("ndf/page_list.html",
                                          {'title': title,
                                           'appId':app._id,
                                           'shelf_list': shelf_list,'shelves': shelves,
                                           'page_nodes': page_nodes,
                                           'groupid':group_id,
                                           'group_id':group_id,
                                           'page_info':paginator_pages
                                          },
                                          context_instance=RequestContext(request))

    else:
        # Page Single instance view
        page_node = node_collection.one({"_id": ObjectId(app_id)})
        thread_node = None
        allow_to_comment = None
        annotations = None
        if page_node:
          annotations = json.dumps(page_node.annotations)
          page_node.get_neighbourhood(page_node.member_of)

          thread_node, allow_to_comment = node_thread_access(group_id, page_node)
        return render_to_response('ndf/page_details.html',
                                  {'node': page_node,
                                    'node_has_thread': thread_node,
                                    'appId': app._id,
                                    'group_id': group_id,
                                    'shelf_list': shelf_list,
                                    'allow_to_comment':allow_to_comment,
                                    'annotations': annotations,
                                    'shelves': shelves,
                                    'groupid': group_id
                                  },
                                  context_instance = RequestContext(request)
        )



@login_required
@get_execution_time
def create_edit_page(request, group_id, node_id=None):
    """Creates/Modifies details about the given quiz-item.
    """

    # ins_objectid = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    group_name, group_id = get_group_name_id(group_id)
    ce_id = request.GET.get('course_event_id','')
    blog_type = request.GET.get('blog_type','')
    res = request.GET.get('res','')
    program_res = request.GET.get('program_res','')
    context_variables = { 'title': gst_page.name,
                          'group_id': group_id,
                          'groupid': group_id,
                          'ce_id': ce_id,
                          'res':res,
                          'program_res':program_res,
                          'blog_type': blog_type
                      }
    group_obj = node_collection.one({'_id': ObjectId(group_id)})
    available_nodes = node_collection.find({'_type': u'GSystem', 'member_of': ObjectId(gst_page._id),'group_set': ObjectId(group_id), '_id': {'$ne': ObjectId(node_id)} })

    nodes_list = []
    thread = None
    url_name = "/home"
    # for each in available_nodes:
    #   nodes_list.append(str((each.name).strip().lower()))
    # loop replaced by a list comprehension
    node_list = [str((each.name).strip().lower()) for each in available_nodes]
    # print "available_nodes: ", node_list

    if request.method == "POST":
        # get_node_common_fields(request, page_node, group_id, gst_page)
        page_name = request.POST.get('name', '')
        # print "====== page_name: ", page_name
        if page_name.strip().lower() in node_list and not node_id:
            new_page=False
            return render_to_response("error_base.html",
                                      {'message': 'Page with same name already exists in the group!'},
                                      context_instance=RequestContext(request))
        elif node_id:
            new_page = False
            page_node = node_collection.one({'_type': u'GSystem', '_id': ObjectId(node_id)})
        else:
            new_page = True
            page_node = node_collection.collection.GSystem()

        # page_type = request.POST.getlist("type_of",'')

        ce_id = request.POST.get("ce_id",'')
        blog_type = request.POST.get('blog_type','')

        res = request.POST.get("res",'')
        program_res = request.POST.get('program_res','')

        # we are fetching the value of release_response flag
        # if this is set, it means, we can proceed to create a thread node
        # for the current page node.
        thread_create_val = request.POST.get("thread_create",'')
        # print "\n\n thread_create_val", thread_create_val
        # print "\n\n request.POST === ",request.POST
        # raise Exception("demo")
        # help_info_page = request.POST.getlist('help_info_page','')
        help_info_page = request.POST['help_info_page']
        if help_info_page:
            help_info_page = json.loads(help_info_page)
        # print "\n\n help_info_page === ",help_info_page

        #program_res and res are boolean values
        if program_res:
            program_res = eval(program_res)

        if res:
            res = eval(res)

        if blog_type:
            blog_type = eval(blog_type)
        # if page_type:
        #     objid= page_type[0]
        #     if not ObjectId(objid) in page_node.type_of:
        #         page_type1=[]
        #         page_type1.append(ObjectId(objid))
        #         page_node.type_of = page_type1
        #         page_node.type_of
        page_node.save(is_changed=get_node_common_fields(request, page_node, group_id, gst_page))

        # if course event grp's id is passed, it means
        # its a blog page added in notebook and hence set type_of field as "Blog page"
        # print "\n\n blog_type---",blog_type
        if blog_type:
            blogpage_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"})
            page_node.type_of = [blogpage_gst._id]
        elif GSTUDIO_SITE_NAME == "NROER" and "Author" in group_obj.member_of_names_list:
            infopage_gst = node_collection.one({'_type': "GSystemType", 'name': "Info page"})
            page_node.type_of = [infopage_gst._id]
        # if the page created is as a resource in course or program event,
        # set status to PUBLISHED by default
        # one major reason for this, ONLY published nodes can be replicated.
        if res or program_res or ce_id:
            page_node.status = u"PUBLISHED"
        page_node.save()
        # if page is created in program event, add page_node to group's collection set
        if program_res:
            group_obj = node_collection.one({'_id': ObjectId(group_id)})
            group_obj.collection_set.append(page_node._id)
            group_obj.save()

        discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
        if thread_create_val == "Yes" or blog_type:
          create_gattribute(page_node._id, discussion_enable_at, True)
          return_status = create_thread_for_node(request,group_id, page_node)
        else:
          create_gattribute(page_node._id, discussion_enable_at, False)

        # print "\n\n help_info_page ================ ",help_info_page
        if "None" not in help_info_page:
          has_help_rt = node_collection.one({'_type': "RelationType", 'name': "has_help"})
          try:
            help_info_page = map(ObjectId, help_info_page)
            create_grelation(page_node._id, has_help_rt,help_info_page)
            page_node.reload()
          except Exception as invalidobjectid:
            # print invalidobjectid
            pass
        else:

          # Check if node had has_help RT
          grel_dict = get_relation_value(page_node._id,"has_help")
          # print "\n\n grel_dict ==== ", grel_dict
          if grel_dict:
            grel_id = grel_dict.get("grel_id","")
            if grel_id:
              for each_grel_id in grel_id:
                del_status, del_status_msg = delete_grelation(
                    subject_id=page_node._id,
                    node_id=each_grel_id,
                    deletion_type=0
                )
                # print "\n\n del_status == ",del_status
                # print "\n\n del_status_msg == ",del_status_msg

        # To fill the metadata info while creating and editing page node
        metadata = request.POST.get("metadata_info", '')
        if ("CourseEventGroup" in group_obj.member_of_names_list or 
            "announced_unit" in group_obj.member_of_names_list) and blog_type:
            if new_page:
              # counter_obj = Counter.get_counter_obj(request.user.id,ObjectId(group_id))
              # # counter_obj.no_notes_written=counter_obj.no_notes_written+1
              # counter_obj['page']['blog']['created'] += 1
              # # counter_obj.course_score += GSTUDIO_NOTE_CREATE_POINTS
              # counter_obj['group_points'] += GSTUDIO_NOTE_CREATE_POINTS
              # counter_obj.last_update = datetime.datetime.now()
              # counter_obj.save()

              active_user_ids_list = [request.user.id]
              if GSTUDIO_BUDDY_LOGIN:
                  active_user_ids_list += Buddy.get_buddy_userids_list_within_datetime(request.user.id, datetime.datetime.now())
                  # removing redundancy of user ids:
                  active_user_ids_list = dict.fromkeys(active_user_ids_list).keys()

              counter_objs_cur = Counter.get_counter_objs_cur(active_user_ids_list, group_id)

              for each_counter_obj in counter_objs_cur:
                  each_counter_obj['page']['blog']['created'] += 1
                  each_counter_obj['group_points'] += GSTUDIO_NOTE_CREATE_POINTS
                  each_counter_obj.last_update = datetime.datetime.now()
                  each_counter_obj.save()

            return HttpResponseRedirect(reverse('course_notebook_note',
                                    kwargs={
                                            'group_id': group_id,
                                            'node_id': page_node._id,
                                            # 'tab': 'my-notes'
                                            })
                                      )

        if ce_id or res or program_res:
            url_name = "/" + group_name + "/" + str(page_node._id)
            if ce_id and blog_type:
                if 'base_unit' in group_obj.member_of_names_list:
                    return HttpResponseRedirect(reverse('course_notebook_note',
                      kwargs={'group_id': group_id, "node_id": page_node._id,
                      'tab': 'my-notes' }))

                # url_name = "/" + group_name + "/#journal-tab"
                url_name = "/" + group_name
            if res or program_res:
                url_name = "/" + group_name + "/?selected=" + str(page_node._id) + "#view_page"
            # print "\n\n url_name---",url_name
            return HttpResponseRedirect(url_name)
        if metadata:
            # Only while metadata editing
            if metadata == "metadata":
                if page_node:
                    get_node_metadata(request,page_node,is_changed=True)
        # End of filling metadata

        return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'app_id': page_node._id }))

    else:
        if node_id:
            page_node = node_collection.one({'_type': u'GSystem', '_id': ObjectId(node_id)})
            #page_node,ver=get_page(request,page_node)
            page_node.get_neighbourhood(page_node.member_of)

            context_variables['node'] = page_node
            context_variables['groupid'] = group_id
            context_variables['group_id'] = group_id
    	# fetch Page instances
    	# Page_node = node_collection.find_one({'_type':"GSystemType","name":"Page"})
    	page_instances = node_collection.find({"type_of": gst_page._id})
    	page_ins_list = [i for i in page_instances]
        context_variables['page_instance'] = page_ins_list
        context_variables['nodes_list'] = json.dumps(nodes_list)
        # print "\n\n context_variables----\n",context_variables
        return render_to_response("ndf/page_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
                              )


@login_required
@get_execution_time
def delete_page(request, group_id, node_id):
    """Change the status to Hidden.

    Just hide the page from users!
    """
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    try:
    	group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    op = node_collection.collection.update({'_id': ObjectId(node_id)}, {'$set': {'status': u"HIDDEN"}})
    return HttpResponseRedirect(reverse('page', kwargs={'group_id': group_id}))


@get_execution_time
def translate_node(request,group_id,node_id=None):
    """ translate the node content"""
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    context_variables = { 'title': gst_page.name,
                          'group_id': group_id,
                          'groupid': group_id
                        }

    if request.method == "POST":
        get_type = get_resource_type(request, node_id)
        # get_type can be GSystem/File/Author/Group
        page_node = eval("node_collection.collection"+"."+ get_type)()
        get_translate_common_fields(request, get_type,page_node, group_id, gst_page,node_id)
        page_node.save(groupid=group_id)
        # add triple to the GRelation
        # then append this ObjectId of GRelation instance in respective subject and object Nodes' relation_set field.
        relation_type = node_collection.one({'_type': 'RelationType', 'name': 'translation_of'})
        gr_node = create_grelation(ObjectId(node_id), relation_type, page_node._id)
        # grelation = node_collection.collection.GRelation()
        # grelation.relation_type=relation_type
        # grelation.subject=ObjectId(node_id)
        # grelation.right_subject=page_node._id
        # grelation.name=u""
        # grelation.save()
        return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'app_id': page_node._id}))

    node = node_collection.one({"_id": ObjectId(node_id)})

    fp = history_manager.get_file_path(node)
    # Retrieve rcs-file for a given version-number
    rcs.checkout(fp)

    # Copy content from rcs-version-file
    data = None
    with open(fp, 'r') as sf:
        data = sf.read()

        # Used json.loads(x) -- to covert string to dictionary object
        # If want to use key from this converted dictionay, use array notation because dot notation doesn't works!
        data = json.loads(data)

        # Remove retrieved rcs-file belonging to the given version-number
        rcs.checkin(fp)

        content = data
        node_details=[]
        for k,v in content.items():
          node_name = content['name']
          node_content_org=content['content_org']
          node_tags=content['tags']
        return render_to_response("ndf/translation_page.html",
                               {'content': content,
                                'appId':app._id,
                                'node':node,
                                'node_name':node_name,
                                'groupid':group_id,
                                'group_id':group_id
                                      },

                              context_instance = RequestContext(request)
    )


@get_execution_time
def publish_page(request,group_id,node):
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    node = node_collection.one({'_id': ObjectId(node)})
    group = node_collection.one({'_id': ObjectId(group_id)})
    if group.post_node:
        node.status=unicode("PUBLISHED")
        node.save('UnderModeration',groupid=group_id)
    else:
        page_node,v=get_page(request,node)
        node.content = unicode(page_node.content)
        # node.content_org = unicode(page_node.content_org)
        node.status = unicode("PUBLISHED")
        node.modified_by = int(request.user.id)
        node.save(groupid=group_id)

    #no need to use this section as seprate view is created for group publish
    #if node._type == 'Group':
    # return HttpResponseRedirect(reverse('groupchange', kwargs={'group_id': group_id}))
    if 'Quiz' in node.member_of_names_list or 'QuizItem' in node.member_of_names_list:
        return HttpResponseRedirect(reverse('quiz_details', kwargs={'group_id': group_id, 'app_id': node._id}))
    return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'app_id': node._id}))
