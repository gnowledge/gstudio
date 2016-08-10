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


@get_execution_time
def ratings(request, group_id, node_id):

	rating_given = request.POST.get('rating', '')
	node_obj = node_collection.one({'_id': ObjectId(node_id)})
	ratedict = {}
	already_rated_by_user = False

	# # functions to modify counter collection for analytics
	# # counter_obj=counter_collection.one({'user_id':node_obj.created_by,'group_id':ObjectId(group_id)})
	# counter_obj = Counter.get_counter_obj(node_obj.created_by, ObjectId(group_id))
	# # import ipdb; ipdb.set_trace()
	# unique=True
	# blog=None

	# import ipdb; ipdb.set_trace()

	# if len(node_obj.type_of)!=0:
	# 	blog=node_collection.one({'_id':node_obj.type_of[0]})
	# for rat in node_obj.rating:
	# 	if rat['user_id']==request.user.id:
	# 		unique=False
	# 		if blog:
	# 			if blog.name=='Blog page':
	# 				# total_rating = counter_obj.rating_count_received_on_notes*counter_obj.avg_rating_received_on_notes
	# 				# get total rating by multiplying
	# 				total_rating = counter_obj['page']['blog']['rating_count_received'] * counter_obj['page']['blog']['avg_rating_gained']
	# 				total_rating = total_rating - rat['score']
	# 				total_rating = total_rating + int(rating_given)

	# 				if counter_obj['page']['blog']['rating_count_received'] != 0:
	# 					# counter_obj.avg_rating_received_on_notes=total_rating/counter_obj.rating_count_received_on_notes
	# 					counter_obj['page']['blog']['avg_rating_gained'] = total_rating / counter_obj['page']['blog']['rating_count_received']

	# 				counter_obj.save()

	# 		if blog == None:
	# 			# total_rating = counter_obj.rating_count_received_on_files*counter_obj.avg_rating_received_on_files
	# 			total_rating = counter_obj['file']['rating_count_received'] * counter_obj['file']['avg_rating_gained']
	# 			total_rating = total_rating - rat['score']
	# 			total_rating = total_rating + int(rating_given)
	# 			# if counter_obj.rating_count_received_on_files!=0:
	# 			if counter_obj['file']['rating_count_received'] != 0:
	# 				# counter_obj.avg_rating_received_on_files=total_rating/counter_obj.rating_count_received_on_files
	# 				counter_obj['file']['avg_rating_gained'] = total_rating / counter_obj['file']['rating_count_received']

	# 			counter_obj.save()

	# if unique:
	# 	if blog:
	# 		if blog.name=='Blog page':
	# 			# total_rating=counter_obj.rating_count_received_on_notes*counter_obj.avg_rating_received_on_notes
	# 			total_rating=counter_obj['page']['blog']['rating_count_received'] * counter_obj['page']['blog']['avg_rating_gained']
	# 			total_rating = total_rating + int(rating_given)
	# 			# counter_obj.rating_count_received_on_notes+=1
	# 			counter_obj['page']['blog']['rating_count_received'] += 1
	# 			# counter_obj.avg_rating_received_on_notes=total_rating/counter_obj.rating_count_received_on_notes
	# 			counter_obj['page']['blog']['avg_rating_gained'] = total_rating / counter_obj['page']['blog']['rating_count_received']
	# 			counter_obj.save()

	# 	if blog == None:
	# 		# total_rating = counter_obj.rating_count_received_on_files*counter_obj.avg_rating_received_on_files
	# 		total_rating = counter_obj['file']['rating_count_received'] * counter_obj['file']['avg_rating_gained']
	# 		total_rating = total_rating + int(rating_given)
	# 		# counter_obj.rating_count_received_on_files += 1
	# 		counter_obj['file']['rating_count_received'] += 1
	# 		# counter_obj.avg_rating_received_on_files = total_rating/counter_obj.rating_count_received_on_files
	# 		counter_obj['file']['avg_rating_gained'] = total_rating / counter_obj['file']['rating_count_received']
	# 		counter_obj.save()

	# done modifying ratings for counter collection

	Counter.update_ratings(node_obj, group_id, rating_given, active_user_id_or_list=[request.user.id])

	if rating_given:
		ratedict['score']=int(rating_given)
		ratedict['user_id']=request.user.id
		ratedict['ip_address']=request.META['REMOTE_ADDR']

		for each_rating in node_obj.rating:
			if each_rating['user_id'] == request.user.id:
				each_rating['score']=int(rating_given)
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
