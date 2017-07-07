from bson import json_util
import os
import sys
import json
from elasticsearch import Elasticsearch
from gnowsys_ndf.ndf.models import *

es = Elasticsearch("http://elsearch:changeit@gsearch:9200")

author_map = {}
group_map = {}
system_type_map  = {}
id_attribute_map = {}
id_relation_map = {}

def create_map(all_docs):
	for node in all_docs:
		if("name" in node):		#only docs with names will be considered for mapping
			if(node._type=="Author"):
				author_map[node.name] = node.created_by
			if(node._type=="Group"):
				group_map[str(node._id)] = node.name
			if(node._type == "GSystemType"):
				create_advanced_map(node)

def create_advanced_map(node):
	system_type_map[node.name] = str(node._id)
	attribute_type_set = []
	for attribute in node.attribute_type_set:
		attribute_type_set.append(attribute["name"])
	relation_type_set = []
	for relation in node.relation_type_set:
		relation_type_set.append(relation["name"])
	id_attribute_map[str(node._id)] = attribute_type_set
	id_relation_map[str(node._id)] = relation_type_set		

def main():
	print("Starting the map creation process")
	all_docs = node_collection.find(no_cursor_timeout=True).batch_size(5)
	create_map(all_docs)

	f = open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings/authormap_clix.json","w")
	json.dump(author_map,f,indent=4)
	f.close()

	f = open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings/groupmap_clix.json","w")
	json.dump(group_map,f,indent=4)
	f.close()

	f = open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings/gsystemtype_map.json","w")
	json.dump(system_type_map,f,indent=4)
	f.close()

	f = open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings/attribute_map.json","w")
	json.dump(id_attribute_map,f,indent=4)
	f.close()

	f = open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings/relation_map.json","w")
	json.dump(id_relation_map,f,indent=4)
	f.close()

main()