
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

@jsonrpc_method('resources', safe=True) 
def resources_list(request):
	'''
	This is RPC method for fetching the resources metadata using
	browser url: http://localhost:8000/json/resources
	using service proxy: s = ServiceProxy('http://localhost:8000/json/')
	                     s.resources()
	'''

	grp = collection.Node.one({'_type':'Group','name':'home'})
	File_GST = collection.Node.one({'_type':'GSystemType','name':'File'})
	Pandora_GST = collection.Node.one({'_type':'GSystemType','name':'Pandora_video'})

	if File_GST and Pandora_GST and grp:
		nodes = collection.Node.find(
			{'member_of': {'$nin':[Pandora_GST._id],'$in':[File_GST._id]}, 'access_policy':'PUBLIC','group_set':ObjectId(grp._id) },
			{'_id':0, 'name':1, 'attribute_set':1, 'created_by':1, 'relation_set':1, 'content_org':1, 'language':1, 'mime_type':1, 'start_publication':1, 'url':1}
		)

		resource_list = []
		relation_set = {}
		t_list = []
		# i = 0 
		for each in nodes:
			# To get the teaches relaion with particular object
			if each.relation_set:
				for e in each.relation_set:
					for k in e[e.keys()[0]]:
						obj = collection.Node.one({'_id': ObjectId(k) })
						t_list.append(obj.name)
					relation_set.update({ e.keys()[0] : t_list })

			each['relation_set'] = relation_set

			for k in each:
				node_dict = {str(k): each[k]}
				each.pop(k)
				each.update(node_dict)

			resource_list.append(each)

			# i=i+1
			# if i == 3:
				# break

	# print "\n",json.dumps(resource_dict),"\n"
	return json.dumps(resource_list)
