from bson import json_util
import os
import sys
import json
from elasticsearch import Elasticsearch
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME

es = Elasticsearch("http://elsearch:changeit@gsearch:9200")
mapping_directory = '/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings'

#during deleting or updating do we need need to set refresh=true to make the document available for search

author_index = "author_" + GSTUDIO_SITE_NAME
index = GSTUDIO_SITE_NAME
gsystemtype_index = "node_type_" + GSTUDIO_SITE_NAME

author_map = {}
group_map = {}
gsystemtype_map = {}
attribute_map = {}
relation_map = {}
with open(mapping_directory+'/authormap.json') as fe:
	author_map = json.load(fe)

with open(mapping_directory+'/groupmap_clix.json') as fe:
	group_map = json.load(fe)

with open(mapping_directory+"/gsystemtype_map.json") as gm:
	gsystemtype_map = json.load(gm)

with open(mapping_directory+"/attribute_map.json") as am:
	attribute_map = json.load(am)

with open(mapping_directory+"/relation_map.json") as rm:
	relation_map = json.load(rm)

doc_type = ""
page_id = gsystemtype_map["Page"]

def update_doc(node):
	global doc_type
	if(node._type == "GSystem"):
			try:
				node.get_neighbourhood(node.member_of)
			except Exception as e:
				print(e)
			else:
				pass

	doc = json.dumps(node, default=json_util.default)
	document = json.loads(doc)
	if("name" not in document.keys()):
		return
	document["id"] = document.pop("_id")
	document["type"] = document.pop("_type")
	if("object_type" in document.keys()):
		document["object_type"] = str(document["object_type"])
	if("property_order" in document.keys()):
		document["property_order"] = str(document["property_order"])
	if("object_value" in document.keys()):
		document["object_value"] = str(document["object_value"])
	doc_type = get_document_type(document)
	update_author_index(document)
	if(document["type"] == "Author"):
		indexAuthor(document)
	elif(document["type"] == "GSystem");
		indexGSystem(document)
	elif(document["type"] == "GSystemType"):
		indexGSystemType(document)
	elif(document["type"] == "Group"):
		indexGroup(document)
	else:
		indexDoc(document)

def update_author_index(document):
	if("contributors" in document.keys()):
		res = es.get(index=index,doc_type=doc_type,id=document["id"]["$oid"])
		if(len(res["hits"]["hits"]) != 0): #check the syntax
			old_contributor_set = res["hits"]["hits"][0]["_source"]["contributors"]
			new_contributor_set = document["contributors"]
			for contributor_id in old_contributor_set:
				es.delete(index=author_index, doc_type=contributor_id,id=document["id"]["$oid"]) #check the syntax
			for contributor_id in new_contributor_set:
				es.index(index = author_index, doc_type = contributor_id, id=document["id"]["$oid"], body = document)
		else:
			new_contributor_set = document["contributors"]
			for contributor_id in new_contributor_set:
				es.index(index = author_index, doc_type = contributor_id, id=document["id"]["$oid"], body = document)



def indexGroup(document):
	if(document["name"] not in group_map):
		group_map[document["name"]] = document["id"]["$oid"]
	es.index(index=index, doc_type=doc_type, id=document["id"]["$oid"], body=document)

def indexAuthor(document):
	if(document["name"] not in author_map.keys()):
		author_map[document["name"]] = document["created_by"]

	contributors = document["contributors"]
	for contributor_id in contributors:
		es.index(index=author_index, doc_type=contributor_id,id=document["id"]["$oid"], body = document)
	es.index(index=index, doc_type=doc_type, id=document["id"]["$oid"], body=document)

def indexGSystemType(document):
	if(document["name"] not in gsystemtype_map.keys()):
		gsystemtype_map[document["name"]] = document["id"]["$oid"]
	for attribute in document["attribute_type_set"]:
		if(attribtue not in attribute_map[document["id"]["$oid"]]):
			attribute_map[document["id"]].append(attribute)
	for relation in document["relation_type_set"]:
		if(relation not in relation_map[document["id"]["$oid"]]):
			relation_map[document["id"]["$oid"]].append(relation)
	es.index(index=index, doc_type=doc_type, id=document["id"]["$oid"], body=document)
	
def indexGSystem(document):
	es.index(index=index, doc_type=doc_type, id=document["id"]["$oid"], body=document)
	attr_set = []
	reln_set = []
	for gsyst in document["member_of"]:
		gsyst_id = gsyst["$oid"]
		poss_attr = attribute_map[gsyst_id]
		poss_reln = relation_map[gsyst_id]
		attr_set.extend(poss_attr)
		reln_set.extend(poss_reln)
	for attr_dict in document["attribute_set"]:
		attr_name = attr_dict.keys()[0]
		if(attr_name not in attr_set):
			for gsyst in document["member_of"]:
				gsyst_id = gsyst["$oid"]
				attribute_map[gsyst_id].append(attr_name)
	for reln_dict in document["relation_set"]:
		reln_name = reln_dict.keys()[0]
		if(reln_name not in reln_set):
			for gsyst in document["member_of"]:
				gsyst_id = gsyst["$oid"]
				relation_map[gsyst_id].append(reln_name)

	for type_ids in document['member_of']:
		es.index(index = gsystemtype_index, doc_type = type_ids["$oid"], id = document["id"]["$oid"], body = document)

def indexDoc(document):
	es.index(index=index, doc_type=doc_type, id=document["id"]["$oid"], body=document)

def get_document_type(document):
	types_arr = ["Author", "GAttribute", "GRelation", "AttributeType", "Filehive", "RelationType", "Group", "GSystemType"]	
	if document["type"]=="GSystem":
		for ids in document['member_of']:  #document is a member of the Page GSystemType
			if(ids['$oid'] == page_id):
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
