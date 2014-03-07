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
from gnowsys_ndf.settings import GAPPS


#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]
GST_IMAGE = collection.GSystemType.one({'name': GAPPS[3]})


#######################################################################################################################################
#                                                                     V I E W S   D E F I N E D   F O R   U S E R   D A S H B O A R D
#######################################################################################################################################


def dashboard(request, group_id, user, uploaded=None):	
    
    ID = User.objects.get(username=user).pk
    
    date_of_join = User.objects.get(username=user).date_joined
    
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
        for val in each.modified_by:
            name = User.objects.get(pk=val).username 		
            collab_drawer.append(name)			
            

    img_cur = collection.GSystem.find({'_type': 'File', 'type_of': 'profile_pic', 'member_of': {'$all': [ObjectId(GST_IMAGE._id)]}, 'created_by': int(ID) })        
    
    if img_cur.count() > 1: 
      cur = collection.GSystem.one({'_id':ObjectId(img_cur[0]._id)})
      if cur.fs_file_ids:
        for each in cur.fs_file_ids:
            cur.fs.files.delete(each)
      cur.delete()

      img_obj = collection.GSystem.one({'_type': 'File', 'type_of': 'profile_pic', 'member_of': {'$all': [ObjectId(GST_IMAGE._id)]}, 'created_by': int(ID) })
    
    else:
      img_obj = collection.GSystem.one({'_type': 'File', 'type_of': 'profile_pic', 'member_of': {'$all': [ObjectId(GST_IMAGE._id)]}, 'created_by': int(ID) })  
    
        

    return render_to_response("ndf/userDashboard.html",
                              {'username': user, 'user_id': ID, 'DOJ': date_of_join, 
                               'prof_pic': img_obj,'group_id':group_id,              
                               'already_uploaded': uploaded,
                               'page_drawer':page_drawer,'image_drawer': image_drawer,
                               'video_drawer':video_drawer,'file_drawer': file_drawer,
                               'quiz_drawer':quiz_drawer,'group_drawer': group_drawer,
                               'forum_drawer':forum_drawer,'collab_drawer': collab_drawer,
                               'groupid':group_id
                              },
                              context_instance=RequestContext(request)
    )

