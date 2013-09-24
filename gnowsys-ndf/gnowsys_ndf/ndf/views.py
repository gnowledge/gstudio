try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages

from django.http import HttpResponse
import hashlib, os
from random import random
from random import choice

from django_mongokit import get_database

from models import Node, Author
from forms import NodeForm, AuthorForm

from string import maketrans 


def homepage(request):

   	return render_to_response(
        "ndf/home.html",context_instance=RequestContext(request)
        
    )
    

def wikipage(request):

    collection = get_database()[Node.collection_name]
    nodes = collection.Node.find()
    nodes.sort('creationtime', -1)
    nodes_count = nodes.count()

    if request.method == "POST":
        form = NodeForm(request.POST, collection=collection)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('wikipage'))
    else:
        form = NodeForm(collection=collection)

    return render_to_response(
        "ndf/wiki.html", {
            'nodes': nodes,
            'form': form,
            'nodes_count': nodes_count,
        },
        context_instance=RequestContext(request)
    )

	
def UserRegistration(request):
	
	a = request.session.session_key			#or request.session._get_or_create_session_key()
	return render_to_response(
        "ndf/UserRegistration.html",{'key':a},context_instance=RequestContext(request)
       	
	)
        
def Register(request):

	if request.method == 'POST':
	
		col_author = get_database()[Author.collection_name]
		auth = col_author.Author()								#Constructor of Author class
		
		# Take values from textboxes
		fname = request.POST.get('reg_Fname')
		lname = request.POST.get('reg_Lname')
		username = request.POST.get('reg_Username')
		password = request.POST.get('reg_Password')
		phone = request.POST.get('reg_Phone')
		email = request.POST.get('reg_Email')
		
		if username and password:
			username_exist = col_author.Author.one({'username': unicode(username)})
		
			if username_exist:
				return HttpResponse("username is already taken, try another")
				
			else:	# Store these values in Database
				auth.username = unicode(username)
				
				auth.password = auth.password_crypt(password)   	
				
				auth.phone = long(phone)
				auth.email = unicode(email)
				auth.save()
				
				#print number of registred users
				authors = col_author.Author.find()	  #TAking 'authors' as cursor object
				authors.sort('created_at', -1)
				authors_count = authors.count()
				
				return render_to_response("ndf/home.html",context_instance=RequestContext(request))		
		else:
			
			return HttpResponse("all fields are required")


def Authentication(request):
	if request.method == 'POST':
		
	
		# Takes values from templates
		username = request.POST.get('username')
		password = request.POST.get('password')
		
		if username and password: 	
			
			col_author = get_database()[Author.collection_name]
			author = col_author.Author.one({'username': unicode(username)})
			PASSWORD = author.password_crypt(password)
			
			if author :
				
				password = author.password
				
				if password == PASSWORD :
					#print "password matched"
					request.session.flush()					# clear session cache
					a = request.session.session_key			# or request.session._get_or_create_session_key()
				
					return render_to_response("ndf/home.html",{'User': author, 'key': a},context_instance=RequestContext(request))
				
				else:
				
					#error = "username and password is incorrect"
					#return render_to_response("ndf/home.html",{'Error':error},context_instance=RequestContext(request))
					return HttpResponse("username and password is incorrect")
					
	else:
	
		return render_to_response("ndf/home.html",context_instance=RequestContext(request))
		
def delete_node(request, _id):
    collection = get_database()[Node.collection_name]
    node = collection.Node.one({"_id": ObjectId(_id)})
    node.delete()
    return HttpResponseRedirect(reverse("wikipage"))




