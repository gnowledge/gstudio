''' -- Imports from python libraries -- '''
import datetime
import json
import pymongo
import re


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from mongokit import paginator
from gnowsys_ndf.ndf.models import *
from pymongo import Connection

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse


try:
	from bson import ObjectId
except ImportError:  # old pymongo
	from pymongo.objectid import ObjectId

from gnowsys_ndf.ndf.views.methods import get_group_name_id

benchmark_collection = db[Benchmark.collection_name]
analytics_collection = db[Analytics.collection_name]
ins_objectid = ObjectId()


class activity_feed(Feed):

	title_template = 'ndf/feed_updates_title.html'
	description_template = 'ndf/feed_updates_description.html'

	def title(self, obj):
		group_name, group_id = get_group_name_id(obj['group_id'])
		return "Updates for the group : "+ group_name+" @ MetaStudio"

	def link(self, obj):
		group_name, group_id = get_group_name_id(obj['group_id'])
		return '/analytics/' + str(group_id) + '/summary/'

	def description(self, obj):
		group_name, group_id = get_group_name_id(obj['group_id'])
		return "Changes and additions to group : " + group_name

	author_name = 'MetaStudio'
	author_link = 'http://metastudio.org'
	feed_copyright = '&#x24B8; Homi Bhabha Centre for Science Education, TIFR'

	def get_object(self, request, group_id) :
		data = {}
		data['group_id'] = group_id
		return data

	def get_context_data(self, **kwargs) :
		context = super(activity_feed, self).get_context_data(**kwargs)
		node = db['Nodes'].find_one({ "_id" : ObjectId(kwargs['item']['obj'][kwargs['item']['obj'].keys()[0]]['id'])})
		try :
			context['node'] = node
			author = db['Nodes'].find_one({"_type" : "Author", "created_by" : node['created_by']})
			try :
				context['author'] = author
			except :
				pass
		except :
			pass
		return context

	def items(self, obj):
		cursor = analytics_collection.find({"action.key" : { '$in' : ['create', 'edit']}, "group_id" : obj['group_id']}).sort("timestamp", -1)
		return cursor

	def item_link(self, item):
		return "/"

	def item_guid(self, item) :
		return item['_id']

