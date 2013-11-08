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
    

def UserRegistration(request):
	
	return render_to_response("ndf/UserRegistration.html",context_instance=RequestContext(request))


def Register(request):

	if request.method == 'POST':
								
            user = User()                       #Constructor of Author class

		# Take values from textboxes
            fname = request.POST.get('reg_Fname')
            lname = request.POST.get('reg_Lname')
            username = request.POST.get('reg_Username')
            password = request.POST.get('reg_Password')
            phone = request.POST.get('reg_Phone')
            email = request.POST.get('reg_Email')

            if username and password:
                username_exist = User.objects.get(username = unicode(username))
		
                if username_exist:
                    return HttpResponse("username is already taken, try another")
                
                else:	
                    # Store these values in django User table 
                    user.first_name = unicode(fname)
                    user.last_name = unicode(lname)
                    user.username = unicode(username)
                    user.set_password(password)
                    user.email = unicode(email)
                    user.save()
                    
                    return render_to_response("ndf/base.html",context_instance=RequestContext(request))		
            else:
                
                return HttpResponse("all fields are required")

'''
def Authentication(request):
    if request.method == 'POST':
        print "authentictn"
        # Takes values from templates
        username = request.POST.get('username')
        password = request.POST.get('password')
        request.session.flush()

	user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                return render_to_response("ndf/base.html",context_instance=RequestContext(request))
            else:
                # Return a 'disabled account' error message
                return HttpResponse("You are not authorised user ")
        else:
            # Return an 'invalid login' error message.			
            return HttpResponse("Please enter valid username & password")

    
    else:
        return render_to_response("ndf/base.html",context_instance=RequestContext(request))        

        
def logout_view(request):
    
    logout(request)
    request.user = AnonymousUser()
    
    return render_to_response("ndf/base.html",context_instance=RequestContext(request))    
'''
		
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
		objectid=fileobj.fs.files.put(files.read(),filename=title,content_type=filetype)
		#print "objectid:",objectid
	return HttpResponse("File uploaded succesfully and your object id:"+str(objectid))






