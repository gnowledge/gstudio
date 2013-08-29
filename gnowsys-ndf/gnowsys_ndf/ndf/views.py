try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

from django_mongokit import get_database

from models import Node, Author
from forms import NodeForm, AuthorForm


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

"""
def wiki_node(request):

	collection = get_database()[Node.collection_name]
	nodes = collection.Node.find()
    
	return render_to_response(
        "ndf/wiki_node.html", {
        	'nodes': nodes,
        },
        context_instance=RequestContext(request)
   )
"""

def userspage(request):

    collection = get_database()[Author.collection_name]
    authors = collection.Author.find()
    authors.sort('creationtime', -1)
    authors_count = authors.count()

    if request.method == "POST":
        form = AuthorForm(request.POST, collection=collection)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('userspage'))
    else:
        form = AuthorForm(collection=collection)

    return render_to_response(
        "ndf/users.html", {
            'authors': authors,
            'form': form,
            'authors_count': authors_count
        },
        context_instance=RequestContext(request)
    )



def delete_node(request, _id):
    collection = get_database()[Node.collection_name]
    node = collection.Node.one({"_id": ObjectId(_id)})
    node.delete()
    return HttpResponseRedirect(reverse("wikipage"))


