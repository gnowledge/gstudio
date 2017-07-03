from bson import json_util
import os
import sys
import json
from elasticsearch import Elasticsearch
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')
es = Elasticsearch("http://elsearch:changeit@gsearch:9200")

# doc_type = ""
author_map = {}
group_map = {}
author_index = "author_"+GSTUDIO_SITE_NAME
index = GSTUDIO_SITE_NAME


def index_docs(all_docs):
	k = 0
	for node in all_docs:
		doc = json.dumps(node,default=json_util.default) #convert mongoDB objectt to a JSON string
		#doc = json.loads(doc,object_hook=json_util.object_hook) ->get back mongoDB object from JSON string
		document = json.loads(doc) #convert JSON string to a python dictionary
		#doc = json.dumps(document) #convert python dictionary to JSON string
		#print(document)
		# print(document["_type"])
		if("name" in document.keys()):
			document["id"] = document.pop("_id")
			document["type"] = document.pop("_type")
			if("object_type" in document.keys() and index == "clix"):
				document["object_type"] = str(document["object_type"])
			if("property_order" in document.keys() and index == "clix"):
				document["property_order"] = str(document["property_order"])
			if("object_value" in document.keys()):
				document["object_value"] = str(document["object_value"])	#for consistent mapping 
			create_map(document)
			doc_type = get_document_type(document)
			print("indexing document %d with id: %s" % (k,document["id"]["$oid"]))
			es.index(index=index, doc_type=doc_type, id=document["id"]["$oid"], body=document)
			if "contributors" in document.keys():
				contributors = document["contributors"]
				for contributor_id in contributors:
					es.index(index = author_index, doc_type = contributor_id,id=document["id"]["$oid"], body = document)
			print("indexed document %d with id: %s" % (k,document["id"]["$oid"]))
			k+=1

def get_document_type(document):
	types_arr = ["Author", "GAttribute", "GRelation", "AttributeType", "Filehive", "RelationType", "Group"]	
	if document["type"]=="GSystem":
		if('if_file' in document.keys()):
			if document["if_file"]["mime_type"] is not None:
				data = document["if_file"]["mime_type"].split("/")
				doc_type = data[0]
			else:
				doc_type = "NotMedia"
		else:
			doc_type = "NotMedia"
		#doc_type = "GSystem"		
	elif (document["type"] in types_arr):
		doc_type = document["type"]
	else:
		doc_type = "DontCare"
	return doc_type


def create_map(document):
	if "name" in document.keys():
		if document["type"]=="Author":
			author_map[document["name"]] = document["created_by"]
		if document["type"]=="Group":
			group_map[document["id"]["$oid"]]=document["name"]


def main():
	print("Starting the indexing process")

	if(es.indices.exists(index)):
		print("Deleting the existing index:"+index+" for reindexing")
		res = es.indices.delete(index=index)
		print("The delete response is %s " % res)
	if(es.indices.exists(author_index)):
		print("Deleting the existing author_index:"+author_index +" for reindexing")
		res = es.indices.delete(index=author_index)
		print("The delete response is %s " % res)
	
	request_body = {}
	with open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/request_body_gsearch.json", 'r') as req_body:
		request_body = json.load(req_body)

	res = es.indices.create(index=index, body=request_body)
	print("Response for index creation")
	print(res)
	all_docs = node_collection.find()
	index_docs(all_docs)

	f = open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mapping_files/authormap_clix.json","w")
	json.dump(author_map,f,indent=4)
	f.close()

	f = open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mapping_files/groupmap_clix.json","w")
	json.dump(group_map,f,indent=4)
	f.close()

main()