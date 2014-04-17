''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
from difflib import HtmlDiff

''' -- imports from installed packages -- '''
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext


from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import get_drawers
from gnowsys_ndf.ndf.views.file import * 
from gnowsys_ndf.settings import GAPPS


#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]
collection_tr = db[Triple.collection_name]
GST_IMAGE = collection.GSystemType.one({'name': GAPPS[3]})


#######################################################################################################################################
#                                                                     V I E W S   D E F I N E D   F O R   U S E R   D A S H B O A R D
#######################################################################################################################################


def dashboard(request, group_id):	
    
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
    prof_pic = collection.Node.one({'_type': u'RelationType', 'name': u'has_profile_pic'})
    uploaded = "None"

    if request.method == "POST" :
      """
      This will take the image uploaded by user and it searches if its already available in gridfs 
      using its md5 
      """ 	
      for index, each in enumerate(request.FILES.getlist("doc[]", "")):
      	fcol = db[File.collection_name]
    	fileobj = fcol.File()
    	filemd5 = hashlib.md5(each.read()).hexdigest()
    	if fileobj.fs.files.exists({"md5":filemd5}):
    	  coll = get_database()['fs.files']
    	  a = coll.find_one({"md5":filemd5})
    	  # prof_image takes the already available document of uploaded image from its md5 
    	  prof_image = collection.Node.one({'_type': 'File', '_id': ObjectId(a['docid']) })

    	else:
    	  # If uploaded image is not found in gridfs stores this new image 
      	  submitDoc(request, group_id)
      	  # prof_image takes the already available document of uploaded image from its name
      	  prof_image = collection.Node.one({'_type': 'File', 'name': unicode(each) })

      # prof_img takes already available relation of user with its profile image
      prof_img = collection.GRelation.one({'subject': ObjectId(auth._id), 'right_subject': ObjectId(prof_image._id) })
      # If prof_img not found then it creates the relation of new uploaded image with its user
      if not prof_img:
        prof_img = collection.GRelation()
        prof_img.subject = ObjectId(auth._id) 
        prof_img.relation_type = prof_pic
        prof_img.right_subject = ObjectId(prof_image._id)
        prof_img.save()
      else:
        obj_img = collection.Node.one({'_id': ObjectId(prof_img.right_subject) })
        uploaded = obj_img.name


    ID = request.user.pk
    date_of_join = request.user.date_joined
    
    page_drawer = get_drawers(group_id,None,None,"Page")
    image_drawer = get_drawers(group_id,None,None,"Image")
    video_drawer = get_drawers(group_id,None,None,"Video")
    file_drawer = get_drawers(group_id,None,None,"File")
    quiz_drawer = get_drawers(group_id,None,None,"OnlyQuiz")
    group_drawer = get_drawers(None,None,None,"Group")
    forum_drawer = get_drawers(group_id,None,None,"Forum")
    
    obj = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, 'created_by': int(ID) ,'group_set': {'$all': [ObjectId(group_id)]}})
    collab_drawer = []	
    
    for each in obj.sort('last_update', -1):  	# To populate collaborators according to their latest modification of particular resource
        for val in each.contributors:
            name = User.objects.get(pk=val).username 		
            collab_drawer.append(name)			
            
    # prof_pic_rel will get the cursor object of relation of user with its profile picture 
    prof_pic_rel = collection.GRelation.find({'subject': ObjectId(auth._id) })
    if prof_pic_rel.count() > 0 :
      index = prof_pic_rel.count() - 1
      img_obj = collection.Node.one({'_type': 'File', '_id': ObjectId(prof_pic_rel[index].right_subject) })      
    else:
      img_obj = "" 


    has_shelf_RT = collection.Node.one({'_type': 'RelationType', 'name': u'has_shelf' })
    dbref_has_shelf = has_shelf_RT.get_dbref()

    shelf = collection_tr.Triple.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': dbref_has_shelf })        
    shelves = []
    shelf_list = {}

    if shelf:
      for each in shelf:
        shelf_name = collection.Node.one({'_id': ObjectId(each.right_subject)})           
        shelves.append(shelf_name)

        shelf_list[shelf_name.name] = []         
        for ID in shelf_name.collection_set:
          shelf_item = collection.Node.one({'_id': ObjectId(ID) })
          shelf_list[shelf_name.name].append(shelf_item.name)

    else:
      shelves = []

    return render_to_response("ndf/userDashboard.html",
                              {'username': request.user.username, 'user_id': ID, 'DOJ': date_of_join, 
                               'prof_pic_obj': img_obj,
                               'group_id':group_id,              
                               'already_uploaded': uploaded,
                               'shelf_list': shelf_list,'shelves': shelves,
                               'page_drawer':page_drawer,'image_drawer': image_drawer,
                               'video_drawer':video_drawer,'file_drawer': file_drawer,
                               'quiz_drawer':quiz_drawer,'group_drawer': group_drawer,
                               'forum_drawer':forum_drawer,'collab_drawer': collab_drawer,
                               'groupid':group_id
                              },
                              context_instance=RequestContext(request)
    )

