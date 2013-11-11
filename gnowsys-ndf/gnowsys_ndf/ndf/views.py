try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser

# Imports regarding Session Management
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
import os
import shutil
import urllib
import datetime

from django.http import HttpResponse
import hashlib, os
from random import random
from random import choice

from django_mongokit import get_database

from models import *
#from forms import NodeForm, AuthorForm

from string import maketrans 
import magic #for this install python-magic example:pip install python-magic

def homepage(request):

    return render_to_response("ndf/home.html",context_instance=RequestContext(request))
      

def create_wiki(request):

    if request.user.is_authenticated():

        col_GSystem = get_database()[GSystem.collection_name]
        col_GST = get_database()[GSystemType.collection_name]
        
        if request.method == "POST":
            
            page = col_GSystem.GSystem()
            wiki_name = request.POST.get('wiki_name')
            wiki_member = request.POST.get('member_of')
            wiki_tags = request.POST.get('tags')
      
            page.name = unicode(wiki_name)
            page.member_of = unicode(wiki_member)
            page.tags.append(unicode(wiki_tags))
            page.gsystem_type = col_GST.GSystemType.one({'name':u"WIKIPAGE"})._id               
            page.save()
            
            return HttpResponseRedirect(reverse('wikipage'))
        
        else:
            return render_to_response("ndf/create_wiki.html",context_instance=RequestContext(request))
    else:
        
        return HttpResponseRedirect(reverse('wikipage'))


def wikipage(request):
    col_GSystem = get_database()[GSystem.collection_name]
    nodes = col_GSystem.GSystem.find()
    nodes.sort('creationtime', -1)
    nodes_count = nodes.count()

    #if member_id is not None:
    return render_to_response("ndf/wiki.html",{'nodes': nodes, 'nodes_count': nodes_count},context_instance=RequestContext(request))    
    
		
def delete_node(request, _id):
    collection = get_database()[GSystem.collection_name]
    node = collection.GSystem.one({"_id": ObjectId(_id)})
    node.delete()
    return HttpResponseRedirect(reverse("wikipage"))

def submitDoc(request):
	db=get_database()[File.collection_name]
	fileobj=db.File()
	if request.method=="POST":
		title = request.POST.get("docTitle","")
		user = request.POST.get("user","")
		memberOf = request.POST.get("memberOf","")
		files=request.FILES.get("doc","")
		#this code is for creating file document and saving
		fileobj.name=unicode(title)
		fileobj.user=unicode(user)
		fileobj.member_of=unicode(memberOf)
		fileobj.save()
		filetype=magic.from_buffer(files.read()) #Gusing filetype by python-magic
		print "test",title,user,memberOf	
		#this code is for storing Document in gridfs
		files.seek(0) #moving files cursor to start
		objectid=fileobj.fs.files.put(files.read(),filename=title,content_type=filetype)
		#files.seek(0)		
		#print "fileread:",files.read()
		#print "objectid:",objectid
<<<<<<< HEAD
	return HttpResponseRedirect("/ndf/documentList/")
	#return HttpResponse("File uploaded succesfully and your object id:"+str(objectid))

def GetDoc(request):
	filecollection=get_database()[File.collection_name]
	files=filecollection.File.find()
	template="ndf/DocumentList.html"
	variable=RequestContext(request,{'filecollection':files})
	return render_to_response(template,variable)

def readDoc(request,_id):
	filecollection=get_database()[File.collection_name]
	fileobj=filecollection.File.one({"_id": ObjectId(_id)})  
	fl=fileobj.fs.files.get_last_version(fileobj.name)
	return HttpResponse(fl.read(),content_type=fl.content_type)
=======
	return HttpResponse("File uploaded succesfully and your object id:"+str(objectid))
>>>>>>> 4da6a7769d212d3b1b2af4e1ee8593b5d88c1543
