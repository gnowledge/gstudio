''' -- imports from python libraries -- '''
import os

import hashlib
import urllib

from random import random
from random import choice
from string import maketrans
import datetime

from subprocess import call 
from tempfile import NamedTemporaryFile


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser

# Imports regarding Session Management
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
<<<<<<< HEAD
import os
import shutil
import urllib
import datetime

from django.http import HttpResponse
import hashlib, os
from random import random
from random import choice
=======
>>>>>>> c2df2e7f0cb9abeb1f54a7a11073099f83332542

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from models import *
<<<<<<< HEAD
#from forms import NodeForm, AuthorForm

from string import maketrans 
import magic #for this install python-magic example:pip install python-magic

def homepage(request):

    return render_to_response("ndf/home.html",context_instance=RequestContext(request))
=======
from rcslib import RCS

###########################################################################

DB = get_database()
history_manager = HistoryManager()
rcs_obj = RCS()
unicode_wikipage = unicode("Wikipage")

def homepage(request):
    
    return render_to_response("ndf/base.html",context_instance=RequestContext(request))
>>>>>>> c2df2e7f0cb9abeb1f54a7a11073099f83332542
      

def create_wiki(request):

    if request.user.is_authenticated():

        if request.method == "POST":
<<<<<<< HEAD
            
            page = col_GSystem.GSystem()
            wiki_name = request.POST.get('wiki_name')
            wiki_member = request.POST.get('member_of')
            wiki_tags = request.POST.get('tags')
      
            page.name = unicode(wiki_name)
            page.member_of = unicode(wiki_member)
            page.tags.append(unicode(wiki_tags))
            page.gsystem_type = col_GST.GSystemType.one({'name':u"WIKIPAGE"})._id               
            page.save()
            
=======
            # Creating Collection-objects
            col_GSystemType = DB[GSystemType.collection_name]
            col_GSystem = DB[GSystem.collection_name]
            
            # Retrieving values from request object
            u_wiki_name = unicode(request.POST.get('wiki_name'))
            u_wiki_tags = unicode(request.POST.get('tags'))
            u_wiki_content_org = unicode(request.POST.get('content_org'))
            u_wiki_member_of = unicode_wikipage
            id_wiki_gsystem_type = col_GSystemType.GSystemType.one({'name': unicode_wikipage})._id

            usrid = int(request.POST.get('usrid'))
            usrname = request.POST.get('usrname')
            
            # Instantiating & Initializing GSystem object
            doc_page = col_GSystem.GSystem()
            doc_page.name = u_wiki_name
            doc_page.tags.append(u_wiki_tags)
            doc_page.member_of = u_wiki_member_of
            doc_page.gsystem_type = id_wiki_gsystem_type
            #doc_page.created_by = usrid          # Confirm the data-type for this field in models.py file is changed from ObjectId (Prev-{Author, django_mongokit}) to int (Curr-{User, django})
            
            # org editor content manipulation for document
            content_org = u_wiki_content_org
            content_org = urllib.unquote_plus(content_org)
            doc_page.content_org = unicode(content_org.encode('utf8') + "\n\n")

            # org editor content manipulation for temporary file (".org")
            content_org_header_for_file = "#+OPTIONS: timestamp:nil author:nil creator:nil ^:{} H:3 num:nil toc:nil @:t ::t |:t ^:t -:t f:t *:t <:t" \
                + "\n#+TITLE: \n"
            content_org_for_file = (doc_page.content_org).replace("\r","")

            ''' -- Creating a temporary file with ".org" extension -- in order to export the org-editor's content to html -- '''
            ext_org = ".org"
            org_file_obj = NamedTemporaryFile('w+t', suffix=ext_org)     # ".org" suffix must; otherwise emacs command won't work!
            filename_org = org_file_obj.name
            # Example (filename_org): "/tmp/tmptCd4aq.org"
            org_file_obj.write(content_org_header_for_file + \
                                   content_org_for_file)
            # NOTE: Don't close this file till the time, html file is created

            # Move the cursor - pointing to start of the file
            org_file_obj.seek(0)     # Must, otherwise cursor remains @ end (as this file isn't closed after writing data into it) and you won't get any data

            ''' -- Exporting the above created ".org" file to html -- '''
            ext_html = ".html"
            filename_html = filename_org[:-4] + ext_html     # "/tmp/tmptCd4aq" + ".html"
            # Example (filename_html): "/tmp/tmptCd4aq.html"
            cmd = "emacs --batch " + filename_org + " --eval '(org-export-as-html nil)'"
            retcode = call((cmd + ' </dev/null'), shell=True)
            
            # Close ".org" temporary file
            org_file_obj.close()
            
            if retcode <= 0:
                print "\n\n Html file created @ {0}\n".format(filename_html)
            else:
                # TODO: Throw error, may be I/O
                print "\n\n Some error occurred!!!\n"

            # Reading data from ".html" file and pasting it in wikipage object's "content" variable 
            with open(filename_html, 'r') as html_file_obj:
                html_data = html_file_obj.readlines()

            # Stripping and storing html data i.e. between <body>...</body> (Both elements are not included)
            strip_html_data = ""
            start_index = html_data.index("<body>\n") + 1         # Start copying data after <body>\n element
            end_index = html_data.index("</body>\n")              # Copy data until you reach before </body>\n element
            for line in html_data[start_index:end_index]:
                strip_html_data += line.lstrip()

            doc_page.content = unicode(strip_html_data)

            # Saving the current document's instance into database
            doc_page.save()

            ''' -- Storing history of this current document's instance -- '''
            if history_manager.create_or_replace_json_file(doc_page):
                fp = history_manager.get_file_path(doc_page)
                rcs_obj.checkin(fp, 0, "This document("+str(doc_page.name)+") is of GSystem(" + doc_page.member_of  +").", "-i")

            #create_wikipage(wiki_name, usrid, wiki_org_content, usrname, collection=False, list=[], private=False)

>>>>>>> c2df2e7f0cb9abeb1f54a7a11073099f83332542
            return HttpResponseRedirect(reverse('wikipage'))
        
        else:
            return render_to_response("ndf/create_wiki.html",context_instance=RequestContext(request))
    else:
        
        return HttpResponseRedirect(reverse('wikipage'))


def wikipage(request):
    col_GSystem = DB[GSystem.collection_name]
    nodes = col_GSystem.GSystem.find({'member_of': unicode_wikipage})
    nodes.sort('creationtime', -1)
    nodes_count = nodes.count()

    #if member_id is not None:
    return render_to_response("ndf/wiki.html", {'nodes': nodes, 'nodes_count': nodes_count}, context_instance=RequestContext(request))    
    
<<<<<<< HEAD
=======

def UserRegistration(request):
	
	return render_to_response("ndf/UserRegistration.html",context_instance=RequestContext(request))
        

def Register(request):

	if request.method == 'POST':
	
		user = User()

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
                        # Store these values in sqlite Database
                        user.first_name = unicode(fname)
                        user.last_name = unicode(lname)
                        user.username = unicode(username)
                        user.set_password(password)
                        user.email = unicode(email)
                        user.save()
				
                        return render_to_response("ndf/base.html", context_instance=RequestContext(request))
		else:
			
			return HttpResponse("all fields are required")


def Authentication(request):
    if request.method == 'POST':
        
        # Takes values from templates
        username = request.POST.get('username')
        password = request.POST.get('password')
        request.session.flush()
        
	user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                return render_to_response("ndf/base.html", context_instance=RequestContext(request))
            else:
                # Return a 'disabled account' error message
                return HttpResponse("You are not authorised user!!!")
        else:
            # Return an 'invalid login' error message.			
            return HttpResponse("Please enter valid username & password")
    
    else:
        return render_to_response("ndf/base.html", context_instance=RequestContext(request))        

        
def logout_view(request):
    
    logout(request)
    request.user = AnonymousUser()
    
    return render_to_response("ndf/base.html", context_instance=RequestContext(request))    

>>>>>>> c2df2e7f0cb9abeb1f54a7a11073099f83332542
		
def delete_node(request, _id):
    col_GSystem = DB[GSystem.collection_name]
    node = col_GSystem.GSystem.one({"_id": ObjectId(_id)})
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
