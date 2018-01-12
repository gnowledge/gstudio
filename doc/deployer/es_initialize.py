from bson import json_util
import os
import sys
import json
from elasticsearch import Elasticsearch
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME
from gnowsys_ndf.local_settings import GSTUDIO_DOCUMENT_MAPPING

##### use the below commented lines if you are working with Python 2.x   #####
# reload(sys)  
# sys.setdefaultencoding('UTF8')

es = Elasticsearch("http://elastic:changeme@gsearch:9200", timeout=100, retry_on_timeout=True)

author_index = "author_" + GSTUDIO_SITE_NAME.lower()
index = GSTUDIO_SITE_NAME.lower()
gsystemtype_index = "node_type_" + GSTUDIO_SITE_NAME.lower()
page_id = 0 

def index_docs(all_docs):
	k = 0
	all_docs_count = all_docs.count()
	for node in all_docs:
		print "[ %s/%s ] : %s " % (k, all_docs_count, node._id)
		if(node._type == "GSystem"):
			try:
				node.get_neighbourhood(node.member_of)
			except Exception as e:
				print(e)
			else:
				pass
			
		doc = json.dumps(node, cls=NodeJSONEncoder) #convert mongoDB object to a JSON string
		#doc = json.loads(doc,object_hook=json_util.object_hook) ->get back mongoDB object from JSON string

		document = json.loads(doc) #convert JSON string to a python dictionary
		#doc = json.dumps(document) #convert python dictionary to JSON string

		if("name" in document.keys()):

			# replacing "_" starting keys:
			document["id"] = document.pop("_id")
			document["type"] = document.pop("_type")

			if("object_type" in document.keys()):
				document["object_type"] = str(document["object_type"])
			if("property_order" in document.keys()):
				document["property_order"] = str(document["property_order"])
			if("object_value" in document.keys()):
				document["object_value"] = str(document["object_value"])	#for consistent mapping 

			doc_type = get_document_type(document)
			es.index(index=index, doc_type=doc_type, id=document["id"], body=document)
			if "contributors" in document.keys():
				contributors = document["contributors"]
				for contributor_id in contributors:
					es.index(index = author_index, doc_type = contributor_id, id=document["id"], body = document)

			if(document["type"] == "GSystem"):
				for type_ids in document['member_of']:
					es.index(index = gsystemtype_index, doc_type = type_ids, id = document["id"], body = document)

			k+=1

def get_document_type(document):
	types_arr = ["Author", "GAttribute", "GRelation", "AttributeType", "Filehive", "RelationType", "Group", "GSystemType"]	
	if document["type"]=="GSystem":
		for ids in document['member_of']:  #document is a member of the Page GSystemType
			if(ids == page_id):
				return "Page"
		if('if_file' in document.keys()):
			if(document["if_file"]["mime_type"] is not None):
				data = document["if_file"]["mime_type"].split("/")
				doc_type = data[0]
			else:
				doc_type = "NotMedia"
		else:
			doc_type = "NotMedia"
	elif (document["type"] in types_arr):
		doc_type = document["type"]
	else:
		doc_type = "DontCare"
	return doc_type


def main():

	print("Starting the indexing process...")
	# DELETING existing/old indexes
	if(es.indices.exists(index)):
		print("Deleting the existing index: "+index+" for reindexing")
		res = es.indices.delete(index=index)
		print("The delete response is %s " % res)

	if(es.indices.exists(author_index)):
		print("Deleting the existing author_index: "+author_index +" for reindexing")
		res = es.indices.delete(index=author_index)
		print("The delete response is %s " % res)

	if(es.indices.exists(gsystemtype_index)):
		print("Deleting the existing gtype index: "+ index+ "for reindexing")
		res = es.indices.delete(index=gsystemtype_index)
	# --- END of DELETING existing/old indexes

	with open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/req_body.json") as req_body:
		request_body = json.load(req_body)
	with open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/req_body_gtype.json") as req_body_type:
		request_body_gtype = json.load(req_body_type)
	with open(GSTUDIO_DOCUMENT_MAPPING+"/gsystemtype_map.json") as gtypemap:
		gtype_map = json.load(gtypemap)
	page_id = gtype_map["Page"]

	res = es.indices.create(index=index, body=request_body)
	print("Response for index creation")
	print(res)

	res = es.indices.create(index=gsystemtype_index, body=request_body_gtype)
	print("Response for index creation")
	print(res)

	res = es.indices.create(index=author_index, body=request_body_gtype)
	print("Response for index creation")
	print(res)

	all_docs = node_collection.find(no_cursor_timeout=True).batch_size(5)
	index_docs(all_docs)

main()