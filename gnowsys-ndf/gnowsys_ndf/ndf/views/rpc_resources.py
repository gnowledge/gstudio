
''' -- imports from installed packages -- ''' 
from django_mongokit import get_database
import json
from jsonrpc import jsonrpc_method

try:
	from bson import ObjectId
except ImportError:  # old pymongo
	from pymongo.objectid import ObjectId
from mongokit import paginator

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import Node

#######################################################################################################################################

collection = get_database()[Node.collection_name]

@jsonrpc_method('resources') 
def resources_list(request):

	grp = collection.Node.one({'_type':'Group','name':'home'})
	File_GST = collection.Node.one({'_type':'GSystemType','name':'File'})
	Pandora_GST = collection.Node.one({'_type':'GSystemType','name':'Pandora_video'})

	if File_GST and Pandora_GST and grp:
		nodes = collection.Node.find({'member_of': {'$nin':[Pandora_GST._id],'$in':[File_GST._id]}, 
									  'access_policy':'PUBLIC','group_set':ObjectId(grp._id) })

		resource_dict = {}
		# i = 0 
		for each in nodes:
			if each.attribute_set:
				resource_dict.update({each.url: {each.name: each.attribute_set} })

			# i=i+1
			# if i == 3:
				# break

	# print "\n",json.dumps(resource_dict),"\n"
	return json.dumps(resource_dict)
