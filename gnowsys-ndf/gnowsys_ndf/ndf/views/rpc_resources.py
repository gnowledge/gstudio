''' -- imports from installed packages -- ''' 
import json
from jsonrpc import jsonrpc_method
from django.contrib.auth.models import User

from mongokit import paginator

try:
	from bson import ObjectId
except ImportError:  # old pymongo
	from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import Node
from django.contrib.auth.models import User
from gnowsys_ndf.ndf.views.methods import get_execution_time
from gnowsys_ndf.ndf.models import node_collection


#######################################################################################################################################


@jsonrpc_method('resources', safe=True) 
def resources_list(request):
	'''
	This is RPC method for fetching the resources metadata using
	browser url: http://localhost:8000/json/resources
	using service proxy: s = ServiceProxy('http://localhost:8000/json/')
	                     s.resources()
	'''

	grp = node_collection.one({'_type': 'Group', 'name': 'home'})
	File_GST = node_collection.one({'_type': 'GSystemType', 'name': 'File'})
	Pandora_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Pandora_video'})
	nodes = []

	if File_GST and Pandora_GST and grp:
		if User.objects.filter(username='nroer_team').exists():
			auth_id = User.objects.get(username='nroer_team').pk
			# Filter only ebooks based on "mime_type:zip"
			nodes = node_collection.find(
				{'member_of': {'$nin':[Pandora_GST._id],'$in':[File_GST._id]}, 'access_policy':'PUBLIC','group_set':ObjectId(grp._id), 'mime_type': 'application/zip', 'created_by': auth_id },
				{'_id':0, 'name':1, 'attribute_set':1, 'created_by':1, 'relation_set':1, 'collection_set':1, 'content_org':1, 'language':1, 'mime_type':1, 'start_publication':1, 'url':1}
			)

		
		efile = None
		ebooks_dict = {}
		ebook_res = []		
		ebook_collection_set = []

		# i = 0 
		for each in nodes:
			if each.collection_set:
				'''
				"ebook_collection_set" variable Keeps resource collection_set as list of ObjectId's for further iteration
				because "efile = each" statement bellow, changes the collection_set as a list of unicode values
				Since "each" is dict and getting updated with unicode values in collection_set in "get_metadata()" function
				'''
				ebook_collection_set = each.collection_set

			# This is for updating fields in string values to show the metadata of ebook i.e zip file
			efile = each
			ebook = get_metadata(efile)
			ebooks_dict.update({ str(ebook) : ebook_res })
			# After updating ebook metadata, now process its collection elements
			if ebook_collection_set:
				ebook_res_list = []
				for res in ebook_collection_set:
					# Selected particular fields only of resource object as bellow
					res_obj = node_collection.one({'_id': ObjectId(res) },
												  {'_id':0, 'name':1, 'attribute_set':1, 'created_by':1, 'relation_set':1, 'collection_set':1, 'content_org':1, 'language':1, 'mime_type':1, 'start_publication':1, 'url':1})
					
					efile = res_obj
					ebook_res = get_metadata(efile)					
					for eb in ebook_res:
						# Taken all collection element of ebook (zip) file
						ebook_res_list.append(eb)

				# Update json { ebook (zip) file document : Its collection elements along with metadata }
				ebooks_dict.update({ str(ebook) : ebook_res_list })
					

			# i=i+1
			# if i == 2:
				# break

	# print "\n",json.dumps(ebooks_dict),"\n"
	return json.dumps(ebooks_dict)

@get_execution_time
def get_metadata(efile):
	'''
	This function converts "relation_set" object values in defined relation from ObjectId to unicode names
	also changes "collection_set" from ObjectId to unicode names
	also makes all the keys in string format in resource dict and shows all metadata together
	'''
	resource_list = []
	relation_set = {}
	t_list = []
	coll_list=[]
	# To get the teaches relaion with particular object
	if efile.relation_set:
		for e in efile.relation_set:
			for k in e[e.keys()[0]]:
				obj = node_collection.one({'_id': ObjectId(k) })
				t_list.append(obj.name)
			relation_set.update({ e.keys()[0] : t_list })

	efile['relation_set'] = relation_set

	# To fetch collection elements of resource
	if efile.collection_set:
		for m in efile.collection_set:
			coll_obj = node_collection.one({'_id': ObjectId(m) })
			coll_list.append(coll_obj.name)

	efile['collection_set'] = coll_list
	
	# Update entire node dict into string values 
	for k in efile:
		node_dict = {str(k): efile[k]}
		efile.pop(k)
		efile.update(node_dict)

	resource_list.append(efile)
	
	return resource_list
