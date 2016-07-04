from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from gnowsys_ndf.ndf.models import get_database
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.views.methods import get_execution_time
from django.contrib.auth.models import User
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_node_ratings
from gnowsys_ndf.ndf.models import *
import json

try:
	from bson import ObjectId
except ImportError:  # old pymongo
	from pymongo.objectid import ObjectId

from gnowsys_ndf.ndf.models import node_collection

sitename=Site.objects.all()[0]

@get_execution_time
def ratings(request, group_id, node_id):
	rating=request.POST.get('rating', '')
	node_obj = node_collection.one({'_id': ObjectId(node_id)})
	ratedict = {}
	already_rated_by_user = False
	#functions to modify counter collection for analytics
	counter_obj=counter_collection.one({'user_id':node_obj.created_by,'group_id':ObjectId(group_id)})
	unique=True
	blog=None
	if len(node_obj.type_of)!=0:
		blog=node_collection.one({'_id':node_obj.type_of[0]})
	#print blog,blog,blog,blog,blog,blog
	for rat in node_obj.rating:
		if rat['user_id']==request.user.id:
			unique=False
			if blog:
				if blog.name=='Blog page':
					total_rating=counter_obj.rating_count_received_on_notes*counter_obj.avg_rating_received_on_notes
					total_rating=total_rating-rat['score']
					total_rating=total_rating+int(rating)
					if counter_obj.rating_count_received_on_notes!=0:
						counter_obj.avg_rating_received_on_notes=total_rating/counter_obj.rating_count_received_on_notes
					counter_obj.save()
			if blog==None:
				total_rating=counter_obj.rating_count_received_on_files*counter_obj.avg_rating_received_on_files
				total_rating=total_rating-rat['score']
				total_rating=total_rating+int(rating)
				if counter_obj.rating_count_received_on_files!=0:
					counter_obj.avg_rating_received_on_files=total_rating/counter_obj.rating_count_received_on_files
				counter_obj.save()

	if unique:
		if blog:
			if blog.name=='Blog page':
				total_rating=counter_obj.rating_count_received_on_notes*counter_obj.avg_rating_received_on_notes
				total_rating=total_rating+int(rating)
				counter_obj.rating_count_received_on_notes+=1
				counter_obj.avg_rating_received_on_notes=total_rating/counter_obj.rating_count_received_on_notes
				counter_obj.save()
		if blog==None:
			total_rating=counter_obj.rating_count_received_on_files*counter_obj.avg_rating_received_on_files
			total_rating=total_rating+int(rating)
			counter_obj.rating_count_received_on_files+=1
			counter_obj.avg_rating_received_on_files=total_rating/counter_obj.rating_count_received_on_files
			counter_obj.save()

	# done modifying ratings for counter collection
	if rating:
		ratedict['score']=int(rating)
		ratedict['user_id']=request.user.id
		ratedict['ip_address']=request.META['REMOTE_ADDR']

		for each_rating in node_obj.rating:
			if each_rating['user_id'] == request.user.id:
				each_rating['score']=int(rating)
				already_rated_by_user = True
				break

		if not already_rated_by_user:
			node_obj.rating.append(ratedict)

		node_obj.save(groupid=group_id)

	result = get_node_ratings(request,node_id)
	# vars=RequestContext(request,{'node':node})
	# template="ndf/rating.html"
	# return render_to_response(template, vars)
	return HttpResponse(json.dumps(result))
