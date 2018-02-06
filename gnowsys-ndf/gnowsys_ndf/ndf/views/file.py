''' -- Imports from python libraries -- '''
import json
import hashlib
import magic
import subprocess
import mimetypes
import os
import datetime
import tempfile
# import re
import ast
import ox
# import pandora_client
import threading

from PIL import Image, ImageDraw
from StringIO import StringIO

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import get_valid_filename
from django.core.files.move import file_move_safe
from django.core.files.temp import gettempdir
from django.core.files.uploadedfile import UploadedFile # django file handler
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from mongokit import paginator

from gnowsys_ndf.settings import GSTUDIO_SITE_VIDEO, EXTRA_LANG_INFO, GAPPS, MEDIA_ROOT, GSTUDIO_FILE_UPLOAD_FORM
# from gnowsys_ndf.settings import WETUBE_USERNAME, WETUBE_PASSWORD
from gnowsys_ndf.ndf.views.notify import set_notif_val
# from gnowsys_ndf.ndf.org2any import org2html
# from gnowsys_ndf.ndf.models import Node, GSystemType, File, GRelation, STATUS_CHOICES, Triple, node_collection, triple_collection, gridfs_collection
from gnowsys_ndf.ndf.models import Node, GSystemType, GRelation, STATUS_CHOICES, Triple, node_collection, triple_collection, gridfs_collection
from gnowsys_ndf.ndf.views.methods import get_node_metadata, get_node_common_fields, create_gattribute, get_page, get_execution_time,set_all_urls,get_group_name_id, get_language_tuple  # , get_page
from gnowsys_ndf.ndf.views.methods import node_thread_access, create_thread_for_node, create_grelation, delete_grelation
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_relation_value

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


from gnowsys_ndf.ndf.views.tasks import convertVideo


############################################

GST_FILE = node_collection.one({'_type':'GSystemType', 'name': 'File'})
GST_PAGE = node_collection.one({'_type':'GSystemType', 'name': 'Page'})
GST_IMAGE = node_collection.one({'_type':'GSystemType', 'name': 'Image'})
GST_VIDEO = node_collection.one({'_type':'GSystemType', 'name': 'Video'})
pandora_video_st = node_collection.one({'_type':'GSystemType', 'name':'Pandora_video'})
app = GST_FILE

lock = threading.Lock()
count = 0

@get_execution_time
def file(request, group_id, file_id=None, page_no=1):
    """
    Renders a list of all 'Files' available within the database.
    """
    ins_objectid  = ObjectId()
    is_video = request.GET.get('is_video', "")
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

    if file_id is None:
        file_ins = node_collection.find_one({'_type':"GSystemType", "name":"File"})
        if file_ins:
            file_id = str(file_ins._id)

    # Code for user shelf
    shelves = []
    shelf_list = {}
    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    # if auth:
    #   has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })
    #   dbref_has_shelf = has_shelf_RT.get_dbref()
    #   shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': dbref_has_shelf })
    #   shelf_list = {}

    #   if shelf:
    #     for each in shelf:
    #         shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)})
    #         shelves.append(shelf_name)

    #         shelf_list[shelf_name.name] = []
    #         for ID in shelf_name.collection_set:
    #           shelf_item = node_collection.one({'_id': ObjectId(ID) })
    #           shelf_list[shelf_name.name].append(shelf_item.name)

    #   else:
    #     shelves = []
    # End of user shelf

    pandoravideoCollection = node_collection.find({'member_of':pandora_video_st._id, 'group_set': ObjectId(group_id) })

    if request.method == "POST":
      # File search view
      title = GST_FILE.name

      search_field = request.POST.get('search_field', '')

      datavisual = []
      if GSTUDIO_SITE_VIDEO == "pandora" or GSTUDIO_SITE_VIDEO == "pandora_and_local":

          files = node_collection.find({'$or':[{'member_of': {'$all': [ObjectId(file_id)]},
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
                                                'group_set': {'$all': [ObjectId(group_id)]}
                                            },

                                               {'member_of': {'$all': [pandora_video_st._id]},
                                                'group_set': {'$all': [ObjectId(group_id)]}
                                               }
                                              ]
                                    }).sort('last_update', -1)
      else:
          files = node_collection.find({'member_of': {'$all': [ObjectId(file_id)]},
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
                                        'group_set': {'$all': [ObjectId(group_id)]}
                                    }).sort('last_update', -1)

      docCollection = node_collection.find({'member_of': {'$nin': [ObjectId(GST_IMAGE._id), ObjectId(GST_VIDEO._id)]},
                                            '_type': {'$in': ['File', 'GSystem']},
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
                                            'group_set': {'$all': [ObjectId(group_id)]}
                                          }).sort("last_update", -1)


      imageCollection = node_collection.find({'member_of': {'$all': [ObjectId(GST_IMAGE._id), GST_FILE._id]},
                                              '_type': {'$in': ['File', 'GSystem']},
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
                                              'group_set': {'$all': [ObjectId(group_id)]}
                                            }).sort("last_update", -1)

      videoCollection = node_collection.find({'member_of': {'$all': [ObjectId(GST_VIDEO._id), GST_FILE._id]},
                                              '_type': {'$in': ['File', 'GSystem']},
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
                                              'group_set': {'$all': [ObjectId(group_id)]}
                                            }).sort("last_update", -1)


      pandoraCollection = node_collection.find({'member_of': {'$all': [ObjectId(pandora_video_st._id)]},
                                                '_type': {'$in': ['File', 'GSystem']},
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
                                                'group_set': {'$all': [ObjectId(group_id)]}
                                            }).sort("last_update", -1)

      datavisual.append({"name":"Doc", "count":docCollection.count()})
      datavisual.append({"name":"Image","count":imageCollection.count()})
      datavisual.append({"name":"Video","count":videoCollection.count()})
      datavisual = json.dumps(datavisual)

      already_uploaded = request.GET.getlist('var', "")
      return render_to_response("ndf/file.html",
                                {'title': title,
                                 'appId':app._id, "app_gst": app,
                                 'searching': True, 'query': search_field,
                                 'already_uploaded': already_uploaded,'shelf_list': shelf_list,'shelves': shelves,
                                 'files': files, 'docCollection': docCollection, 'imageCollection': imageCollection,
                                 'videoCollection': videoCollection,'pandoravideoCollection':pandoravideoCollection,
                                 'pandoraCollection': pandoraCollection,
                                 'is_video':is_video,'groupid': group_id, 'group_id':group_id,"datavisual":datavisual
                                },
                                context_instance=RequestContext(request)
      )

    elif GST_FILE._id == ObjectId(file_id):
      # File list view
      title = GST_FILE.name
      datavisual = []
      no_of_objs_pp = 24  # no. of objects per page to be list

      if GSTUDIO_SITE_VIDEO == "pandora" or GSTUDIO_SITE_VIDEO == "pandora_and_local":


        files_dict = get_query_cursor_filetype('$all', [ObjectId(file_id)], group_id, request.user.id, page_no, no_of_objs_pp, "all_files")


        file_pages = files_dict["result_pages"]
        files_pc = files_dict["result_cur"]

      else:
        files_dict = get_query_cursor_filetype('$all', [ObjectId(file_id)], group_id, request.user.id, page_no, no_of_objs_pp)

        files_pc = files_dict["result_cur"]
        file_pages = files_dict["result_pages"]

      # --- for documents ---
      doc = get_query_cursor_filetype('$nin', [ObjectId(GST_IMAGE._id), ObjectId(GST_VIDEO._id)], group_id, request.user.id, page_no, no_of_objs_pp)

      docCollection = doc["result_cur"]
      docs_pc = doc["result_cur"]
      doc_pages = doc["result_pages"]

      # --- for pages ---
      page_dict = get_query_cursor_filetype('$all', [ObjectId(GST_PAGE._id)], group_id, request.user.id, page_no, no_of_objs_pp, "Pages")

      pageCollection = page_dict["result_cur"]
      pages_pc = page_dict["result_cur"]
      page_nodes = page_dict["result_pages"]

      # --- for images ---
      image_dict = get_query_cursor_filetype('$all', [ObjectId(GST_IMAGE._id)], group_id, request.user.id, page_no, no_of_objs_pp)

      imageCollection = image_dict["result_cur"]
      images_pc = image_dict["result_cur"]
      image_pages = image_dict["result_pages"]

      # --- for videos ---
      video_dict = get_query_cursor_filetype('$in', [ObjectId(GST_VIDEO._id),ObjectId(pandora_video_st._id)], group_id, request.user.id, page_no, no_of_objs_pp)

      videoCollection = video_dict["result_cur"]
      videos_pc = video_dict["result_cur"]
      video_pages = video_dict["result_pages"]

      already_uploaded = request.GET.getlist('var', "")

      new_list = []
      for each in already_uploaded:
        for name in eval(each):
          for k in name:
            if type(k) is list:
              new_list.append(k[0])

      already_uploaded = new_list

      # source_id_at=node_collection.one({'$and':[{'name':'source_id'},{'_type':'AttributeType'}]})

      # pandora_video_id = []
      # source_id_set=[]
      # get_member_set = node_collection.find({'$and':[{'member_of': {'$all': [ObjectId(pandora_video_st._id)]}},{'group_set': ObjectId(group_id)},{'_type':'File'}]})
      # pandora_pages = paginator.Paginator(get_member_set, page_no, no_of_objs_pp)
      all_videos = get_query_cursor_filetype('$all', [ObjectId(GST_VIDEO._id)], group_id, request.user.id, page_no, no_of_objs_pp, "all_videos")

      pandora_pages = all_videos["result_pages"]
      get_member_set = all_videos["result_cur"]

      collection_pages_cur = node_collection.find({
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

      coll_page_count = collection_pages_cur.count() if collection_pages_cur else 0
      collection_pages = paginator.Paginator(collection_pages_cur, page_no, no_of_objs_pp)

      #for each in get_member_set:

       #  pandora_video_id.append(each['_id'])
      # for each in get_member_set:
      #     att_set=triple_collection.one({'$and':[{'subject':each['_id']},{'_type':'GAttribute'},{'attribute_type':source_id_at._id}]})
      #     if att_set:
      #         obj_set={}
      #         obj_set['id']=att_set.object_value
      #         obj_set['object']=each
      #         source_id_set.append(obj_set)

              # for each in pandora_video_id:
              #     get_video = node_collection.find({'member_of': {'$all': [ObjectId(file_id)]}, '_type': 'File', 'group_set': {'$all': [ObjectId(group_id)]}})

      datavisual.append({"name":"Doc", "count":docCollection.count()})
      datavisual.append({"name":"Image","count":imageCollection.count()})
      datavisual.append({"name":"Video","count":videoCollection.count()})
      #datavisual.append({"name":"Pandora Video","count":pandoraCollection.count()})
      if collection_pages_cur:
          datavisual.append({"name":"Collections","count": coll_page_count})
      datavisual = json.dumps(datavisual)

      return render_to_response("ndf/file.html",
                                {'title': title,
                                 'appId':app._id, "app_gst": app,
                                 'already_uploaded': already_uploaded,'shelf_list': shelf_list,'shelves': shelves,
                                 # 'sourceid':source_id_set,
                                 'file_pages': file_pages, 'image_pages': images_pc.count(), 'page_count': pages_pc.count(),
                                 'doc_pages': docs_pc.count(), 'video_pages': videos_pc.count(), "pandora_pages": pandoravideoCollection.count(),
                                 'files': files_pc, 'docCollection': docs_pc, 'imageCollection': images_pc, 'page_nodes':pages_pc,
                                 'videoCollection': videos_pc, 'pandoravideoCollection':pandoravideoCollection,
                                 'pandoraCollection':get_member_set,'is_video':is_video,'groupid': group_id,
                                 'collection_pages': collection_pages, 'collection': collection_pages_cur,
                                 'group_id':group_id,"datavisual":datavisual, "detail_urlname": "file_detail"
                                },
                                context_instance = RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('homepage',kwargs={'group_id': group_id, 'groupid':group_id}))

@get_execution_time
def get_query_cursor_filetype(operator, member_of_list, group_id, userid, page_no, no_of_objs_pp, tab_type=None):
    '''
    This method used to fire mongoDB query and send its result along with pagination details. This method is specially for "_type": "File" objects only.

    Arguments:
    -- operator : it's mongoDB operators like "$all", "$nin", "$or", ..., etc.
    -- member_of_list : It's list of member_of. Example: [ObjectId('5401eb2c90b550696393b9df')]
    -- group_id : Group's "_id".
    -- userid : Example. request.user.id
    -- page_no : It's page no required for getting appropriate paginated cursor.
    -- no_of_objs_pp : No. of objects to be shown per page.

    Result: It gives result as dictionary. {"result_cur": "", "result_pages":"", "result_paginated_cur": ""}
    -- result_cur : It's mongoDB cursor.
    -- result_pages : It's mongokit.paginator cursor. Containing all the info for pagination.

    '''

    result_dict = {"result_cur": "", "result_pages":"", "result_paginated_cur": "", "result_count": ""}

    if tab_type == "all_videos" or tab_type == "all_files":

        result_cur = node_collection.find({'$or':[{'member_of': {'$all': member_of_list},
                                                '_type': {'$in': ['File', 'GSystem']}, 'fs_file_ids':{'$ne': []},
                                                'group_set': {'$all': [ObjectId(group_id)]},
                                                '$or': [
                                                    {'access_policy': u"PUBLIC"},
                                                    {'$and': [
                                                        {'access_policy': u"PRIVATE"},
                                                        {'created_by': userid}
                                                    ]
                                                 }
                                                ]
                                                },{'member_of': {'$all': [pandora_video_st._id]},
                                                  'group_set': {'$all': [ObjectId(group_id)]},
                                                  '_type': {'$in': ['File', 'GSystem']}, 'access_policy': u"PUBLIC"
                                                  }
                                           ]}).sort("last_update", -1)


    elif tab_type == "Pages":
        result_cur = node_collection.find({'member_of': GST_PAGE._id,
                                    '_type': 'GSystem',
                                    'group_set': {'$all': [ObjectId(group_id)]},
                                    '$or': [
                                        {'access_policy': u"PUBLIC"},
                                        {'$and': [
                                            {'access_policy': u"PRIVATE"},
                                            {'created_by': userid}
                                        ]
                                     }
                                    ]
                                }).sort("last_update", -1)


    elif tab_type == "Documents":
        result_cur = node_collection.find({'member_of': {'$nin':[ObjectId(GST_IMAGE._id), ObjectId(GST_VIDEO._id)]},
                                            '_type': {'$in': ['File', 'GSystem']},
                                            'group_set': {'$all': [ObjectId(group_id)]},

                                            'if_file.mime_type': {'$ne': None},
                                            '$or': [
                                                {'access_policy': u"PUBLIC"},
                                                {'$and': [
                                                    {'access_policy': u"PRIVATE"},
                                                    {'created_by': userid}
                                                ]
                                             }
                                            ]
                                        }).sort("last_update", -1)


    else:
        result_cur = node_collection.find({'member_of': {operator: member_of_list},
                                    '_type': {'$in': ['File', 'GSystem']}, 'fs_file_ids':{'$ne': []},
                                    'group_set': {'$all': [ObjectId(group_id)]},
                                    '$or': [
                                        {'access_policy': u"PUBLIC"},
                                        {'$and': [
                                            {'access_policy': u"PRIVATE"},
                                            {'created_by': userid}
                                        ]
                                     }
                                    ]
                                }).sort("last_update", -1)

    if result_cur:

        result_pages = paginator.Paginator(result_cur, page_no, no_of_objs_pp)
        result_dict["result_pages"] = result_pages
        result_dict["result_cur"] = result_cur

    return result_dict

@get_execution_time
def paged_file_objs(request, group_id, filetype, page_no):
    '''
    Method to implement pagination in File and E-Library app.


    '''
    if request.is_ajax() and request.method == "POST":

        app = request.POST.get("title", "")

        no_of_objs_pp = 24

        # ins_objectid  = ObjectId()

        # if ins_objectid.is_valid(group_id) is False :
        #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
        #     if group_ins:
        #         group_id = str(group_ins._id)
        #     else :
        #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        #         if auth :
        #             group_id = str(auth._id)

        group_name, group_id = get_group_name_id(group_id)

        # file_ins = node_collection.find_one({'_type':"GSystemType", "name":"File"})
        # if file_ins:
        #     file_id = str(file_ins._id)

        file_id = GST_FILE._id

        # if app == "E-Library":
        #     files = node_collection.find({'$or':[{'member_of': ObjectId(file_id),
        #                           '_type': 'File', 'fs_file_ids':{'$ne': []},
        #                           'group_set': ObjectId(group_id),
        #                           '$or': [{'access_policy': u"PUBLIC"},
        #                                     {'$and': [{'access_policy': u"PRIVATE"},
        #                                               {'created_by': request.user.id}
        #                                              ]
        #                                     }
        #                                 ]
        #                          },
        #                          {'member_of': ObjectId(pandora_video_st._id),
        #                           'group_set': ObjectId(group_id)
        #                          }]
        #                          }).sort("last_update", -1)

        #     coll = []
        #     for each in files:
        #         coll.append(each._id)

        #     files.rewind()
        #     gattr = node_collection.one({'_type': 'AttributeType', 'name': u'educationaluse'})

        if filetype == "all":

            if app == "File":
                if GSTUDIO_SITE_VIDEO == "pandora" or GSTUDIO_SITE_VIDEO == "pandora_and_local":
                    result_dict = get_query_cursor_filetype('$all', [ObjectId(file_id)], group_id, request.user.id, page_no, no_of_objs_pp, "all_files")

                else:
                    result_dict = get_query_cursor_filetype('$all', [ObjectId(file_id)], group_id, request.user.id, page_no, no_of_objs_pp)
            # elif app == "E-Library":
            #     if files:
            #         result_paginated_cur = files
            #         result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

        elif filetype == "Documents":
            if app == "File":
                result_dict = get_query_cursor_filetype('$nin', [ObjectId(GST_IMAGE._id), ObjectId(GST_VIDEO._id)], group_id, request.user.id, page_no, no_of_objs_pp,"Documents")

            # elif app == "E-Library":
            #     d_Collection = triple_collection.find({'_type': "GAttribute", 'attribute_type': gattr._id,"subject": {'$in': coll} ,"object_value": "Documents"}).sort("last_update", -1)

            #     doc = []
            #     for e in d_Collection:
            #         doc.append(e.subject)

            #     result_paginated_cur = node_collection.find({ '$or':[{'_id': {'$in': doc}},

            #                 {'member_of': {'$nin': [ObjectId(GST_IMAGE._id), ObjectId(GST_VIDEO._id),ObjectId(pandora_video_st._id)]},
            #                                     '_type': 'File', 'group_set': {'$all': [ObjectId(group_id)]},
            #                                     'mime_type': {'$not': re.compile("^audio.*")},
            #                                     '$or': [
            #                                           {'access_policy': u"PUBLIC"},
            #                                             {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
            #                                            ]
            #                                     }]

            #         }).sort("last_update", -1)


            #     result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

        elif filetype == "Pages":
            if app == "File":
                result_dict = get_query_cursor_filetype('$all', [ObjectId(GST_PAGE._id), GST_FILE._id], group_id, request.user.id, page_no, no_of_objs_pp, "Pages")


        elif filetype == "Images":
            if app == "File":
                result_dict = get_query_cursor_filetype('$all', [ObjectId(GST_IMAGE._id), GST_FILE._id], group_id, request.user.id, page_no, no_of_objs_pp)
            # elif app == "E-Library":
            #     img_Collection = triple_collection.find({'_type': "GAttribute", 'attribute_type': gattr._id,"subject": {'$in': coll} ,"object_value": "Images"}).sort("last_update", -1)
            #     image = []
            #     for e in img_Collection:
            #         image.append(e.subject)

            #     # result_paginated_cur = node_collection.find({'_id': {'$in': image} })
            #     result_paginated_cur = node_collection.find({'$or': [{'_id': {'$in': image} },

            #                 {'member_of': {'$all': [ObjectId(GST_IMAGE._id)]},
            #                                      '_type': 'File', 'group_set': {'$all': [ObjectId(group_id)]},
            #                                      '$or': [
            #                                           {'access_policy': u"PUBLIC"},
            #                                             {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
            #                                            ]
            #                                     }]

            #         }).sort("last_update", -1)

            #     result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

        elif filetype == "Videos":
            if app == "File":
                result_dict = get_query_cursor_filetype('$all', [ObjectId(GST_VIDEO._id), GST_FILE._id], group_id, request.user.id, page_no, no_of_objs_pp, "all_videos")

        elif filetype == "Collections":
            if app == "File":
                detail_urlname = "page_details"
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
                # print "=====================", result_cur.count()

                result_paginated_cur = result_cur
                result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)
                result_dict = {"result_cur": result_cur, "result_pages": result_pages, "result_paginated_cur": "", "result_count": ""}
                # print "=====================", result_pages


            # elif app == "E-Library":
            #     vid_Collection = node_collection.find({'_type': "GAttribute", 'attribute_type': gattr._id,"subject": {'$in': coll} ,"object_value": "Videos"}).sort("last_update", -1)
            #     video = []
            #     for e in vid_Collection:
            #         video.append(e.subject)

            #     result_paginated_cur = node_collection.find({'$or': [{'_id': {'$in': video} },

            #               {'member_of': {'$in': [ObjectId(GST_VIDEO._id),ObjectId(pandora_video_st._id)]},
            #                                      '_type': 'File', 'access_policy': {'$ne':u"PRIVATE"}, 'group_set': {'$all': [ObjectId(group_id)]},
            #                                      '$or': [
            #                                           {'access_policy': u"PUBLIC"},
            #                                             {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
            #                                            ]
            #                                     }]

            #         }).sort("last_update", -1)


            #     result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

        # elif filetype == "interactives" and app == "E-Library":
        #     interCollection = triple_collection.find({'_type': "GAttribute", 'attribute_type': gattr._id, "subject": {'$in': coll} ,"object_value": "Interactives"}).sort("last_update", -1)
        #     interactive = []
        #     for e in interCollection:
        #         interactive.append(e.subject)

        #     result_paginated_cur = node_collection.find({'_id': {'$in': interactive} })
        #     result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

        # elif filetype == "audio" and app == "E-Library":
        #     aud_Collection = triple_collection.find({'_type': "GAttribute", 'attribute_type': gattr._id,"subject": {'$in': coll} ,"object_value": "Audios"}).sort("last_update", -1)

        #     audio = []
        #     for e in aud_Collection:
        #         audio.append(e.subject)

        #     # result_paginated_cur = node_collection.find({'_id': {'$in': audio} })

        #     result_paginated_cur = node_collection.find({ '$or':[{'_id': {'$in': audio}},

        #               {'member_of': {'$nin': [ObjectId(GST_IMAGE._id), ObjectId(GST_VIDEO._id)]},
        #                                         '_type': 'File', 'group_set': {'$all': [ObjectId(group_id)]},
        #                                         'mime_type': {'$regex': 'audio','$options': "i"},
        #                                         '$or': [
        #                                               {'access_policy': u"PUBLIC"},
        #                                                 {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
        #                                                ]
        #                                         }]

        #             }).sort("last_update", -1)


        #     result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

        # result_dict = {"result_cur": "", "result_pages":"", "result_paginated_cur": "", "result_count": ""}

        if app == "File":
            result_cur = result_dict["result_cur"]
            result_paginated_cur = result_dict["result_cur"]
            result_pages = result_dict["result_pages"]

        if filetype == "Pages":
          detail_urlname = "page_details"
        else:
          detail_urlname = "file_detail"

        return render_to_response ("ndf/file_list_tab.html", {
                "group_id": group_id, "group_name_tag": group_id, "groupid": group_id,
                "resource_type": result_paginated_cur, "detail_urlname": detail_urlname,
                "filetype": filetype, "res_type_name": "", "page_info": result_pages
            },
            context_instance = RequestContext(request))


@login_required
@get_execution_time
def uploadDoc(request, group_id):

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    if request.method == "GET":
        topic_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})
        topic_nodes = node_collection.find({'member_of': {'$in': [topic_gst._id]}})
        program_res = request.GET.get("program_res", "")
        if program_res:
          program_res = eval(program_res)
        page_url = request.GET.get("next", "")
        # template = "ndf/UploadDoc.html"

        template = "ndf/UploadDoc.html"

        if GSTUDIO_FILE_UPLOAD_FORM == 'detail':
            template = "ndf/Uploader_Form.html"

    if  page_url:
        variable = RequestContext(request, {'page_url': page_url,'groupid':group_id,'group_id':group_id, 'program_res':program_res,'topic_nodes':topic_nodes})
    else:
        variable = RequestContext(request, {'groupid':group_id,'group_id':group_id,'program_res':program_res,'topic_nodes':topic_nodes})
    return render_to_response(template, variable)



@login_required
@get_execution_time
def submitDoc(request, group_id):
    """
    submit files for saving into gridfs and creating object
    """

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    alreadyUploadedFiles = []
    #a temp. variable which stores the lookup for append method
    alreadyUploadedFiles_append_temp=alreadyUploadedFiles.append
    str1 = ''
    img_type=""
    topic_file = ""
    is_video = ""
    obj_id_instance = ObjectId()
    if request.method == "POST":
        mtitle = request.POST.get("docTitle", "")
        userid = request.POST.get("user", "")
        language = request.POST.get("lan", "")
        img_type = request.POST.get("type", "")
        topic_file = request.POST.get("type", "")
        doc = request.POST.get("doc", "")
        usrname = request.user.username
        page_url = request.POST.get("page_url", "")
        content_org = request.POST.get('content_org', '')
        access_policy = request.POST.get("login-mode", '') # To add access policy(public or private) to file object
        tags = request.POST.get('tags', "")
        copyright = request.POST.get("Copyright", "")
        source = request.POST.get("Source", "")
        Audience = request.POST.getlist("audience", "")
        fileType = request.POST.get("FileType", "")
        Based_url = request.POST.get("based_url", "")
        co_contributors = request.POST.get("co_contributors", "")
        map_geojson_data = request.POST.get('map-geojson-data')
        subject = request.POST.get("Subject", "")
        level = request.POST.getlist("Level", "")

        subject = '' if (subject=='< Not Sure >') else subject
        level = '' if (level=='< Not Sure >') else level

        if map_geojson_data:
          map_geojson_data = map_geojson_data + ","
          map_geojson_data = list(ast.literal_eval(map_geojson_data))
        else:
          map_geojson_data = []


        i = 1
        filename=""
        for index, each in enumerate(request.FILES.getlist("doc[]", "")):
            if mtitle:
                filename=filename+mtitle+" "
                if index == 0:
                    # f, is_video = save_file(each, mtitle, userid, group_id, content_org, tags, img_type, language, usrname, access_policy, oid=True)

                    f, is_video = save_file(each, mtitle, userid, group_id, content_org, tags, img_type, language, usrname, access_policy, copyright, source, Audience, fileType, subject, level, Based_url, co_contributors, request, map_geojson_data)

                else:
                    title = mtitle + "_" + str(i)  # increament title
                    f, is_video = save_file(each, title, userid, group_id, content_org, tags, img_type, language, usrname, access_policy, copyright, source, Audience, fileType, subject, level, Based_url, co_contributors, request, map_geojson_data)
                    i = i + 1
            else:
                title = each.name

                # f, is_video = save_file(each,title,userid,group_id, content_org, tags, img_type, language, usrname, access_policy)
                # print "f: ", f
            # if not obj_id_instance.is_valid(f):
            # check if file is already uploaded file
            # if isinstance(f, list):
                f, is_video = save_file(each,title,userid,group_id, content_org, tags, img_type, language, usrname, access_policy, copyright, source, Audience, fileType, subject, level, Based_url, co_contributors, request, map_geojson_data)
                try:
                    ObjectId(f)
                except:
                    if isinstance(f, list):
                        f = f[1]
                fileobj = node_collection.one({'_id': ObjectId(f)})
                thread_create_val = request.POST.get("thread_create",'')
                help_info_page = request.POST.getlist('help_info_page','')
                # help_info_page = request.POST['help_info_page']
                if help_info_page:
                  help_info_page = json.loads(help_info_page)

                # print "\n\n help_info_page  === ", help_info_page
                discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
                if thread_create_val == "Yes":
                  create_gattribute(fileobj._id, discussion_enable_at, True)

                  return_status = create_thread_for_node(reaquest,group_id, fileobj)
                else:
                  create_gattribute(fileobj._id, discussion_enable_at, False)

                # print "\n\n help_info_page ================ ",help_info_page
                if help_info_page and u"None" not in help_info_page:
                  has_help_rt = node_collection.one({'_type': "RelationType", 'name': "has_help"})
                  try:
                    help_info_page = map(ObjectId, help_info_page)
                    create_grelation(fileobj._id, has_help_rt,help_info_page)
                  except Exception as invalidobjectid:
                    # print invalidobjectid
                    pass
                else:

                  # Check if node had has_help RT
                  grel_dict = get_relation_value(fileobj._id,"has_help")
                  # print "\n\n grel_dict ==== ", grel_dict
                  if grel_dict:
                    grel_id = grel_dict.get("grel_id","")
                    if grel_id:
                      for each_grel_id in grel_id:
                        del_status, del_status_msg = delete_grelation(
                            subject_id=fileobj._id,
                            node_id=each_grel_id,
                            deletion_type=0
                        )
                        # print "\n\n del_status == ",del_status
                        # print "\n\n del_status_msg == ",del_status_msg


            # print "=============== : ", f
            try:
                ObjectId(f)

            except:
                if isinstance(f, list):
                  # alreadyUploadedFiles_append_temp(f)
                  alreadyUploadedFiles = f
                  title = mtitle


        # str1 = alreadyUploadedFiles

        # print "=============== : ", alreadyUploadedFiles

        if img_type != "":
            # print "----------1-----------"
            return HttpResponseRedirect(reverse('dashboard', kwargs={'group_id': int(userid)}))

        elif topic_file != "":
            # print "----------2-----------"
            return HttpResponseRedirect(reverse('add_file', kwargs={'group_id': group_id }))

        else:
            if alreadyUploadedFiles:
                # return HttpResponseRedirect(page_url+'?var='+str1)
                # if (type(alreadyUploadedFiles[0][0]).__name__ == "ObjectId"):
                # print "----------3-----------", alreadyUploadedFiles
                return HttpResponseRedirect(reverse("file_detail", kwargs={'group_id': group_id, "_id": alreadyUploadedFiles[1].__str__() }))
                # else:
                    # if alreadyUploadedFiles[0][1]:
                        # return HttpResponseRedirect(reverse("file_detail", kwargs={'group_id': group_id, "_id": alreadyUploadedFiles[0][0].__str__() }))
            else:
                group_object = node_collection.one({'_id': ObjectId(group_id)})
                try:
                    f = ObjectId(f)
                except:
                    f = f[0]
                if group_object.edit_policy == 'EDITABLE_MODERATED' and isinstance(f, ObjectId):
                    # print "----------4-----------"
                    fileobj = node_collection.one({'_id': ObjectId(f)})
                    # newly appended group id in group_set is at last
                    from gnowsys_ndf.ndf.views.moderation import create_moderator_task

                    t = create_moderator_task(request, fileobj.group_set[0], fileobj._id,on_upload=True)
                    # return HttpResponseRedirect(reverse('moderation_status', kwargs={'group_id': fileobj.group_set[1], 'node_id': f }))
                    return HttpResponseRedirect(reverse('moderation_status', kwargs={'group_id': group_object.name, 'node_id': f }))
                else:
                    # print "----------5-----------", f

                    return HttpResponseRedirect(reverse("file_detail", kwargs={'group_id': group_id, "_id": ObjectId(f) }))

                # if is_video == "True":
                #     return HttpResponseRedirect(page_url+'?'+'is_video='+is_video)
                # else:
                #     return HttpResponseRedirect(page_url)

    else:
        # print "----------6-----------"
        return HttpResponseRedirect(reverse('homepage',kwargs={'group_id': group_id, 'groupid':group_id}))


first_object = ''
@get_execution_time
def save_file(files,title, userid, group_id, content_org, tags, img_type=None, language=None, usrname=None, access_policy=None, copyright=None, source=None, Audience=None, fileType=None, subject=None, level=None, Based_url=None, co_contributors="", request=None, map_geojson_data=[], **kwargs):
    """
      this will create file object and save files in gridfs collection
    """
    global count, first_object
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    group_object = node_collection.one({'_id': ObjectId(group_id)})

    # overwritting count and first object by sending arguments kwargs (count=0, first_object="")
    # this is to prevent from forming collection of first object containing subsequent objects.
    count = kwargs["count"] if "count" in kwargs else count
    first_object = kwargs["first_object"] if "first_object" in kwargs else first_object

    is_video = ""
    fileobj = node_collection.collection.File()
    filemd5 = hashlib.md5(files.read()).hexdigest()
    files.seek(0)
    size, unit = getFileSize(files)
    size = {'size': round(size, 2), 'unit': unicode(unit)}

    if fileobj.fs.files.exists({"md5": filemd5}):
        # gridfs_collection = get_database()['fs.files']
        cur_oid = gridfs_collection.find_one({"md5": filemd5}, {'docid': 1, '_id': 0})

        # coll_new = get_database()['Nodes']
        new_name = node_collection.find_one({'_id': ObjectId(str(cur_oid["docid"]))})
        # if calling function is passing oid=True as last parameter then reply with id and name.
        if "oid" in kwargs:
            if kwargs["oid"]:
                # gridfs_collection = get_database()['fs.files']
                cur_oid = gridfs_collection.find_one({"md5": filemd5}, {'docid': 1, '_id': 0})
                # Fetch file node by docid
                file_node = node_collection.one({'_id': ObjectId(cur_oid['docid'])})
                # print "\n\n file_node\n\n",file_node
                if file_node:
                    # Check if already existing file is uploaded in same group as earlier
                    if ObjectId(group_id) not in file_node.group_set:
                        # if not, add current request group_id in group_set of file_node
                        file_node.group_set.append(ObjectId(group_id))
                        file_node.last_update = datetime.datetime.now()
                        file_node.modified_by = int(userid)
                        file_node.save()
                        # This change is made in order to fetch file nodes
                        # from a group

                # returning only ObjectId (of GSystem containing file info) in dict format.
                # e.g : {u'docid': ObjectId('539a999275daa21eb7c048af')}
                return cur_oid["docid"], 'True'
        else:
            # print "already Uploaded file"
            return [files.name, new_name._id], 'True'

    else:
        try:
            files.seek(0)
            filetype = magic.from_buffer(files.read(100000), mime='true')  # Gusing filetype by python-magic
            # print "\nfiletype : ", filetype, "\n"
            filetype1 = mimetypes.guess_type(files.name)[0]
            if filetype1:
                filetype1 = filetype1
            else:
                filetype1 = ""
            filename = files.name
            fileobj.name = unicode(title)

            if language:
                # fileobj.language = unicode(language)
                fileobj.language = get_language_tuple(language)
            fileobj.created_by = int(userid)

            fileobj.modified_by = int(userid)
            fileobj.status = u'PUBLISHED'

            if int(userid) not in fileobj.contributors:
                fileobj.contributors.append(int(userid))
            if access_policy:
                fileobj.access_policy = unicode(access_policy)  # For giving privacy to file objects
            fileobj.file_size = size

            if group_object._id not in fileobj.group_set:
                # group id stored in group_set field
                fileobj.group_set.append(group_object._id)

            if "CourseEventGroup" not in group_object.member_of_names_list:
                # if group is of EDITABLE_MODERATED, update group_set accordingly
                if group_object.edit_policy == "EDITABLE_MODERATED":
                    from gnowsys_ndf.ndf.views.moderation import get_moderator_group_set
                    fileobj.group_set = get_moderator_group_set(fileobj.group_set, group_object._id)
                    fileobj.status = u'MODERATION'

            if usrname:
                user_group_object = node_collection.one({'$and': [{'_type': u'Author'},{'name': usrname}]})
                if user_group_object:
                    if user_group_object._id not in fileobj.group_set:  # File creator_group_id stored in group_set field
                        fileobj.group_set.append(user_group_object._id)

            # Commented bellow code to avoid redundancy (this will be removed once testing done)
            # if group_object._id not in fileobj.group_set:
            #     fileobj.group_set.append(group_object._id)        #group id stored in group_set field
            # if usrname:
            #     user_group_object=node_collection.one({'$and':[{'_type':u'Author'},{'name':usrname}]})
            #     if user_group_object:
            #         if user_group_object._id not in fileobj.group_set:                 # File creator_group_id stored in group_set field
            #             fileobj.group_set.append(user_group_object._id)

            fileobj.member_of.append(GST_FILE._id)
            #  ADDED ON 14th July.IT's DONE
            fileobj.url = set_all_urls(fileobj.member_of)
            fileobj.mime_type = filetype
            if img_type == "" or img_type is None:
                if content_org:
                    fileobj.content_org = unicode(content_org)
                    # Required to link temporary files with the current user who is modifying this document
                    filename_content = slugify(title) + "-" + usrname + "-"
                    fileobj.content = content_org
                if tags:
                    # print "\n\n tags",tags
                    if not type(tags) is list:
                        tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]
                    fileobj.tags = tags

            # new fields added
            fileobj.legal['copyright'] = unicode(copyright)

            fileobj.location = map_geojson_data
            fileobj.save(groupid=group_id)

            if source:
              # create gattribute for file with source value
              source_AT = node_collection.one({'_type':'AttributeType','name':'source'})
              src = create_gattribute(fileobj._id, source_AT, source)

            if Audience:
              # create gattribute for file with Audience value
              audience_AT = node_collection.one({'_type':'AttributeType','name':'audience'})
              aud = create_gattribute(fileobj._id, audience_AT, Audience)

            if fileType:
              # create gattribute for file with 'educationaluse' value
              educationaluse_AT = node_collection.one({'_type':'AttributeType', 'name': 'educationaluse'})
              FType = create_gattribute(fileobj._id, educationaluse_AT, fileType)

            if subject:
              # create gattribute for file with 'educationaluse' value
              subject_AT = node_collection.one({'_type':'AttributeType', 'name': 'educationalsubject'})
              sub = create_gattribute(fileobj._id, subject_AT, subject)

            if level:
              # create gattribute for file with 'educationaluse' value
              educationallevel_AT = node_collection.one({'_type':'AttributeType', 'name': 'educationallevel'})
              edu_level = create_gattribute(fileobj._id, educationallevel_AT, level)
            if Based_url:
              # create gattribute for file with 'educationaluse' value
              basedonurl_AT = node_collection.one({'_type':'AttributeType', 'name': 'basedonurl'})
              basedUrl = create_gattribute(fileobj._id, basedonurl_AT, Based_url)

            if co_contributors:
              # create gattribute for file with 'co_contributors' value
              co_contributors_AT = node_collection.one({'_type':'AttributeType', 'name': 'co_contributors'})
              co_contributors = create_gattribute(fileobj._id, co_contributors_AT, co_contributors)
            files.seek(0)                                                                  #moving files cursor to start

            objectid = fileobj.fs.files.put(files.read(), filename=filename, content_type=filetype) #store files into gridfs
            node_collection.find_and_modify({'_id': fileobj._id}, {'$push': {'fs_file_ids': objectid}})

            print '+' * 20
            # For making collection if uploaded file more than one
            if count == 0:
                first_object = fileobj
            else:
                node_collection.find_and_modify({'_id': first_object._id}, {'$push': {'collection_set': fileobj._id}})


            """
            code for uploading video to wetube.gnowledge.org
            """
            if 'video' in filetype or 'video' in filetype1 or filename.endswith('.webm') is True:

                # --- code for wetube processing part ---

                # is_video = 'True'
                # path = files.temporary_file_path() # method gets temporary location of the file
                # base_url = "http://wetube.gnowledge.org/"
                # api_url = base_url + "api/"
                # # connenting to wetube api using pandora_client
                # api = pandora_client.API(api_url)
                # # signin takes username, password & returns user data
                # api.signin(username=WETUBE_USERNAME, password=WETUBE_PASSWORD)
                # # return metadata about the file
                # info = ox.avinfo(path)
                # oshash = info['oshash']
                # # add media file the given item
                # r = api.addMedia({
                #     'id': oshash,
                #     'filename': fileobj.name,
                #     'info': info
                # })
                # # return unique item id for file
                # item = r['data']['item']
                # url = '%supload/direct/' % api_url
                # # upload one or more media file for given item
                # r = api.upload_chunks(url, path, {
                #     'id': oshash
                # })
                # --- END of code for wetube processing part ---

                fileobj.reload()
                node_collection.find_and_modify({'_id': fileobj._id}, {'$push': {'member_of': GST_VIDEO._id}})
                # node_collection.find_and_modify({'_id': fileobj._id}, {'$set': {'mime_type': 'video'}})
                fileobj.reload()

                # --- code for wetube processing part ---
                # # create gattribute
                # source_id_AT = node_collection.one({'$and':[{'name':'source_id'},{'_type':'AttributeType'}]})
                # create_gattribute(fileobj._id, source_id_AT, unicode(item))
                # --- END of code for wetube processing part ---

                # # -- convert viedo into webm format
                # webmfiles, filetype, thumbnailvideo = convertVideo(files, userid, fileobj, filename)


                '''put video conversion in the Q using celery'''
                convertVideo.delay(userid, str(fileobj._id), filename)
                # convertVideo(userid, str(fileobj._id), filename)


                # t = threading.Thread(target=convertVideo, args=(files, userid, fileobj, filename, ))
                # t.start()

            '''storing thumbnail of pdf and svg files  in saved object'''
            # if 'pdf' in filetype or 'svg' in filetype:
            #     thumbnail_pdf = convert_pdf_thumbnail(files,fileobj._id)
            #     tobjectid = fileobj.fs.files.put(thumbnail_pdf.read(), filename=filename+"-thumbnail", content_type=filetype)
            #     node_collection.find_and_modify({'_id':fileobj._id},{'$push':{'fs_file_ids':tobjectid}})

            '''storing thumbnail of image in saved object'''
            # print "\n\n filetype------ ",filetype
            if 'image' in filetype:
                node_collection.find_and_modify({'_id': fileobj._id}, {'$push': {'member_of': GST_IMAGE._id}})
                thumbnailimg = convert_image_thumbnail(files)
                if thumbnailimg:
                    tobjectid = fileobj.fs.files.put(thumbnailimg, filename="thumbnail-of-"+filename, content_type=filetype)
                    node_collection.find_and_modify({'_id': fileobj._id}, {'$push': {'fs_file_ids': tobjectid}})

                files.seek(0)
                mid_size_img = convert_mid_size_image(files)
                if mid_size_img:
                    mid_img_id = fileobj.fs.files.put(mid_size_img, filename="mid_size_img-of-"+filename, content_type=filetype)
                    node_collection.find_and_modify({'_id': fileobj._id}, {'$push': {'fs_file_ids':mid_img_id}})
            count = count + 1
            # print "----- fileobj._id", fileobj._id


            '''
            For server-sync
            '''
            # This function captures the data and a decorater is put on this function so that node to be saved in the parent function
            # can be sent as a mail to the mailing-list

            return fileobj._id, is_video

        except Exception as e:
            print "Some Exception:", files.name, "Execption:", e


@get_execution_time
def getFileSize(File):
    """
    obtain file size if provided file object
    """
    try:
        File.seek(0,os.SEEK_END)
        num=int(File.tell())
        for x in ['bytes','KB','MB','GB','TB']:
            if num < 1024.0:
                return  (num, x)
            num /= 1024.0
    except Exception as e:
        print "Unabe to calucalate size",e
        return 0,'bytes'


@get_execution_time
def convert_image_thumbnail(files):
    """
    convert image file into thumbnail
    """
    try:
        thumb_io = StringIO()
        size = 128, 128
        files.seek(0)
        try:
            img = Image.open(StringIO(files.read()))
        except Exception, e:
            return None
        img.thumbnail(size, Image.ANTIALIAS)

        file_type = mimetypes.guess_type(files.name)[0]

        extension = None
        if 'jpg' in file_type or 'jpeg' in file_type:
          extension = 'JPEG'
        elif 'png' in file_type:
          extension = 'PNG'
        elif 'svg' in file_type:
          extension = 'SVG'
        else:
          temp_extension = mimetypes.guess_extension(files.name)
          if temp_extension:
              extension = extension.rsplit('.')[1]

        if extension:
            img.save(thumb_io, extension)
        else:
            img.save(thumb_io, 'JPEG')

        thumb_io.seek(0)
        return thumb_io

    except Exception, e:
        return None


@get_execution_time
def convert_pdf_thumbnail(files,_id):
    '''
    convert pdf file's thumnail
    '''
    filename = str(_id)
    os.system("mkdir -p "+ "/tmp"+"/"+filename+"/")
    fd = open('%s/%s/%s' % (str("/tmp"),str(filename),str(filename)), 'wb')
    files.seek(0)
    fd.write(files.read())
    fd.close()
    subprocess.check_call(['convert', '-thumbnail', '128x128',str("/tmp/"+filename+"/"+filename+"[0]"),str("/tmp/"+filename+"/"+filename+"-thumbnail.png")])
    thumb_pdf = open("/tmp/"+filename+"/"+filename+"-thumbnail.png", 'r')
    return thumb_pdf


@get_execution_time
def convert_mid_size_image(files, **kwargs):
    """
    convert image into mid size image w.r.t. max width of 500
    """
    try:
        files.seek(0)
        mid_size_img = StringIO()
        size = (500, 300)  # (width, height)
        try:
          img = Image.open(StringIO(files.read()))
        except Exception, e:
          return None
        # img = img.resize(size, Image.ANTIALIAS)
        # img.save(mid_size_img, "JPEG")
        # mid_size_img.seek(0)

        if (img.size > size) or (img.size[0] >= size[0]):
          # both width and height are more than width:500 and height:300
          # or
          # width is more than width:500
          factor = img.size[0]/500.00
          img = img.resize((500, int(img.size[1] / factor)), Image.ANTIALIAS)

        elif (img.size <= size) or (img.size[0] <= size[0]):
          img = img.resize(img.size, Image.ANTIALIAS)

        file_type = mimetypes.guess_type(files.name)[0]

        if kwargs.get('extension', ''):
          extension = kwargs['extension']
        elif 'jpg' in file_type or 'jpeg' in file_type:
          extension = 'JPEG'
        elif 'png' in file_type:
          extension = 'PNG'
        elif 'svg' in file_type:
          extension = 'SVG'
        else:
          extension = mimetypes.guess_extension(files.name)
          extension = extension.rsplit('.')[1]

        if extension:
            img.save(mid_size_img, extension)

        else:
          img.save(mid_size_img, "JPEG")

        mid_size_img.seek(0)

        return mid_size_img

    except Exception, e:
        return None



@get_execution_time
def GetDoc(request, group_id):
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

    files = node_collection.find({'_type': {'$in': ['File', 'GSystem']}, 'member_of': {'$in': [GST_FILE._id]}})
    #return files
    template = "ndf/DocumentList.html"
    variable = RequestContext(request, {'filecollection':files,'groupid':group_id,'group_id':group_id})
    return render_to_response(template, variable)


@get_execution_time
def file_search(request, group_id):
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

    if request.method == "GET":
        keyword = request.GET.get("search", "")
        file_search = node_collection.find({'$or':[{'name':{'$regex': keyword}}, {'tags':{'$regex':keyword}}]}) #search result from file
        template = "ndf/file_search.html"
        variable = RequestContext(request, {'file_collection':file_search, 'view_name':'file_search','groupid':group_id,'group_id':group_id})
        return render_to_response(template, variable)


@login_required
@get_execution_time
def delete_file(request, group_id, _id):
  """Delete file and its data
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

  auth = node_collection.one({'_type': u'Author', 'name': unicode(request.user.username) })
  pageurl = request.GET.get("next", "")
  try:
    cur = node_collection.one({'_id':ObjectId(_id)})
    rel_obj = triple_collection.one({"_type": "GRelation", 'subject': ObjectId(auth._id), 'right_subject': ObjectId(_id) })
    if rel_obj :
        rel_obj.delete()
    if cur.fs_file_ids:
        for each in cur.fs_file_ids:
            cur.fs.files.delete(each)
    cur.delete()
  except Exception as e:
    print "Exception:", e
  return HttpResponseRedirect(pageurl)


@get_execution_time
def file_detail(request, group_id, _id):
    """Depending upon mime-type of the node, this view returns respective display-view.
    """
    imageCollection = ""
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

    group_name, group_id = get_group_name_id(group_id)
    file_node = node_collection.one({"_id": ObjectId(_id)})
    file_node.get_neighbourhood(file_node.member_of)
    if file_node._type == "GSystemType":
      return file(request, group_id, _id)

    file_template = ""
    if file_node.has_key('mime_type') and file_node.mime_type:
        if file_node.mime_type == 'video':
            file_template = "ndf/video_detail.html"
        elif 'image' in file_node.mime_type:

            imageCollection = node_collection.find({'member_of': {'$all': [ObjectId(GST_IMAGE._id), GST_FILE._id]},
                                              '_type': {'$in': ['File', 'GSystem']},
                                              '$or': [
                                                  {'$or': [
                                                    {'access_policy': u"PUBLIC"},
                                                      {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
                                                    ]
                                                  }
                                                ,
                                                {'$and': [
                                                  {'$or': [
                                                    {'access_policy': u"PUBLIC"},
                                                    {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
                                                    ]
                                                  }
                                                  ]
                                                }
                                              ],
                                              'group_set': {'$all': [ObjectId(group_id)]}
                                            }).sort("last_update", -1)

            file_template = "ndf/image_detail.html"
        else:
            file_template = "ndf/document_detail.html"
        #grid_fs_obj = file_node.fs.files.get(ObjectId(file_node.fs_file_ids[0]))
        #return HttpResponse(grid_fs_obj.read(), content_type = grid_fs_obj.content_type)
    else:
         # raise Http404
         file_template = "ndf/document_detail.html"
    thread_node = None
    allow_to_comment = None
    thread_node, allow_to_comment = node_thread_access(group_id, file_node)
    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    shelves = []
    shelf_list = {}

    # First get the navigation list till topic from theme map
    nav_l=request.GET.get('nav_li','')
    breadcrumbs_list = []
    nav_li = ""

    if nav_l:
      nav_li = nav_l

    if auth:
        has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })
        shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': has_shelf_RT._id })
        #a temp. variable which stores the lookup for append method
        shelves_append_temp=shelves.append
        if shelf:
            for each in shelf:
                shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)})
                shelves_append_temp(shelf_name)

                shelf_list[shelf_name.name] = []
                #a temp. variable which stores the lookup for append method
                shelf_list_shelfname_append_temp=shelf_list[shelf_name.name].append
                for ID in shelf_name.collection_set:
                    shelf_item = node_collection.one({'_id': ObjectId(ID) })
                    shelf_list_shelfname_append_temp(shelf_item.name)

        else:
            shelves = []

    annotations = json.dumps(file_node.annotations)
    # print "=== ", type(file_node)

    return render_to_response(file_template,
                              { 'node': file_node,
                                'group_id': group_id,
                                'groupid':group_id,
                                'annotations' : annotations,
                                'shelf_list': shelf_list,
                                'allow_to_comment':allow_to_comment,
                                'node_has_thread': thread_node,
                                'shelves': shelves, 'nav_list':nav_li,
                                'imageCollection':imageCollection
                              },
                              context_instance = RequestContext(request)
                             )


def file_content(request, group_id):

    node_id = request.GET.get('id', None)

    # print "========", node_id
    node = node_collection.one({'_id': ObjectId(node_id)});

    return render_to_response('ndf/node_ajax_content.html',
                                {
                                    'group_id': group_id,'groupid': group_id,
                                    'node': node
                                }, context_instance = RequestContext(request))

@get_execution_time
def getFileThumbnail(request, group_id, _id):
    """Returns thumbnail of respective file
    """
    # ins_objectid = ObjectId()
    # if ins_objectid.is_valid(group_id) is False:
    #     group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     elif auth:
    #         group_id = str(auth._id)
    # else:
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)


    file_node = node_collection.one({"_type": {'$in': ['File', 'GSystem']}, "_id": ObjectId(_id)})
    """
    if file_node is not None:
        if file_node.fs_file_ids:
          # getting latest uploaded pic's _id

          file_fs = ""
          if len(file_node.fs_file_ids) > 1:
            file_fs = file_node.fs_file_ids[2]

          if (file_node.fs.files.exists(file_fs)):

            if len(file_node.fs_file_ids) > 0:
              f = file_node.fs.files.get(ObjectId(file_node.fs_file_ids[1]))
            else:
              f = file_node.fs.files.get(ObjectId(file_node.fs_file_ids[0]))

            return HttpResponse(f.read(), content_type=f.content_type)

          else:
              return HttpResponse("")
        else:
            return HttpResponse("")
    else:
        return HttpResponse("")
    """
    if file_node is not None:
      if hasattr(file_node, 'fs_file_ids'):
        fs_file_ids = file_node.fs_file_ids
        if fs_file_ids and len(fs_file_ids) == 3:
          # getting latest uploaded pic's _id
          # file_fs = file_node.fs_file_ids[2]

          # if (file_node.fs.files.exists(file_fs)):


          f = file_node.fs.files.get(ObjectId(fs_file_ids[2]))

          return HttpResponse(f.read(), content_type=f.content_type)

          # else:
          #     return HttpResponse("")
        elif fs_file_ids and 'image' in file_node.mime_type:
            f = file_node.fs.files.get(ObjectId(fs_file_ids[0]))
            return HttpResponse(f.read(), content_type=f.content_type)

        elif fs_file_ids and ((len(fs_file_ids) >= 1) or ('video' in file_node.mime_type)):
            # -- for video thumbnail
            f = file_node.fs.files.get(ObjectId(fs_file_ids[1]))
            return HttpResponse(f.read(), content_type=f.content_type)

        else:
            # --  image thumbnail
            f = file_node.fs.files.get(ObjectId(fs_file_ids[0]))

        return HttpResponse(f.read(), content_type=f.content_type)
      elif hasattr(file_node, 'if_file'):
        f = file_node.get_file(file_node.if_file.thumbnail.relurl)
        return HttpResponse(f.read(), content_type=file_node.if_file.mime_type)

    else:
        return HttpResponse("")


@get_execution_time
def readDoc(request, _id, group_id, file_name=""):
    '''Return Files
    '''
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


    file_node = node_collection.one({"_id": ObjectId(_id)})


    if file_node is not None:

        if hasattr(file_node, 'if_file') and file_node.if_file.original.relurl:
            # print "md5_or_relurl : ", file_node.if_file.original
            return HttpResponse(file_node.get_file(file_node.if_file.original.relurl),
                                content_type=file_node.if_file.mime_type)

        elif file_node.fs_file_ids:
            if file_node.mime_type == 'video':
                if len(file_node.fs_file_ids) > 2:
                    if (file_node.fs.files.exists(file_node.fs_file_ids[2])):
                        f = file_node.fs.files.get(ObjectId(file_node.fs_file_ids[2]))
                        return HttpResponse(f.read(), content_type=f.content_type)
            elif (file_node.fs.files.exists(file_node.fs_file_ids[0])):
                grid_fs_obj = file_node.fs.files.get(ObjectId(file_node.fs_file_ids[0]))
                return HttpResponse(grid_fs_obj.read(), content_type = grid_fs_obj.content_type)
            else:
                return HttpResponse("")
        else:
            return HttpResponse("")
    else:
        return HttpResponse("")



@get_execution_time
def read_attachment(request, group_id, file_path):
  file_path = '/' + file_path
  with open(file_path,'r') as download_file:
    mime = magic.Magic(mime=True)
    response = HttpResponse(download_file.read(), content_type=mime.from_file(file_path))
    response['Content-Disposition'] = 'attachment; filename=' + file_path.split("/")[-1]
    return response


@get_execution_time
def file_edit(request,group_id,_id):
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

    group_obj = node_collection.one({'_id': ObjectId(group_id)})
    file_node = node_collection.one({"_id": ObjectId(_id)})
    title = GST_FILE.name
    ce_id = request.GET.get('course_event_id')
    course_tab_title = request.GET.get('course_tab_title','')
    res = request.GET.get('res')

    if request.method == "POST":

        # get_node_common_fields(request, file_node, group_id, GST_FILE)
        file_node.save(is_changed=get_node_common_fields(request, file_node, group_id, GST_FILE),groupid=group_id)

        thread_create_val = request.POST.get("thread_create",'')
        course_tab_title = request.POST.get("course_tab_title",'')
        # help_info_page = request.POST.getlist('help_info_page','')
        help_info_page = request.POST['help_info_page']
        if help_info_page:
          help_info_page = json.loads(help_info_page)

        discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
        if thread_create_val == "Yes":
          create_gattribute(file_node._id, discussion_enable_at, True)
          return_status = create_thread_for_node(request,group_id, file_node)
        else:
          create_gattribute(file_node._id, discussion_enable_at, False)

        # print "\n\n help_info_page ================ ",help_info_page
        if help_info_page and u"None" not in help_info_page:
          has_help_rt = node_collection.one({'_type': "RelationType", 'name': "has_help"})
          try:
            help_info_page = map(ObjectId, help_info_page)
            create_grelation(file_node._id, has_help_rt,help_info_page)
          except Exception as invalidobjectid:
            # print invalidobjectid
            pass
        else:

          # Check if node had has_help RT
          grel_dict = get_relation_value(file_node._id,"has_help")
          # print "\n\n grel_dict ==== ", grel_dict
          if grel_dict:
            grel_id = grel_dict.get("grel_id","")
            if grel_id:
              for each_grel_id in grel_id:
                del_status, del_status_msg = delete_grelation(
                    subject_id=file_node._id,
                    node_id=each_grel_id,
                    deletion_type=0
                )
                # print "\n\n del_status == ",del_status
                # print "\n\n del_status_msg == ",del_status_msg

        if "CourseEventGroup" not in group_obj.member_of_names_list:
            # To fill the metadata info while creating and editing file node
            metadata = request.POST.get("metadata_info", '')
            # print ".....................",metadata
            if metadata:
                # Only while metadata editing
                if metadata == "metadata":
                    if file_node:
                        get_node_metadata(request,file_node)
                        file_node.save()
            # End of filling metadata

            return HttpResponseRedirect(reverse('file_detail', kwargs={'group_id': group_id, '_id': file_node._id}))
        else:
            file_node.status = u"PUBLISHED"
            file_node.save()
            if course_tab_title:
                if course_tab_title == "raw material":
                    course_tab_title = "raw_material"
                return HttpResponseRedirect(reverse('course_'+course_tab_title + '_detail', kwargs={'group_id': group_id, 'node_id': str(file_node._id)}))

            return HttpResponseRedirect(reverse('course_about', kwargs={'group_id': group_id}))
            # url = "/"+ str(group_id) +"/?selected="+str(file_node._id)+"#view_page"
            # return HttpResponseRedirect(url)

    else:
        if file_node:
            file_node.get_neighbourhood(file_node.member_of)

        return render_to_response("ndf/document_edit.html",
                                  { 'node': file_node,'title':title,
                                    'group_id': group_id,
                                    'groupid':group_id,
                                    'ce_id': ce_id,
                                    'res': res,'course_tab_title':course_tab_title
                                },
                                  context_instance=RequestContext(request)
                              )


def get_gridfs_resource(request, gridfs_id):

    # print gridfs_id

    f = node_collection.find_one({'_type': 'File'})
    gridfs_obj = f.fs.files.get(ObjectId(gridfs_id))

    return HttpResponse(gridfs_obj.read(), content_type=gridfs_obj.content_type)
