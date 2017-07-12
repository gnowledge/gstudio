from bson import json_util
import os, errno
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
			if(node._type == "Author"):
				author_map[node.name] = node.created_by
			if(node._type == "Group"):
				group_map[node.name] = str(node._id)
			if(node._type == "GSystem"):
				attr = []; rel = [];
				for grid in node.member_of:
					gid = str(grid)
					if(gid not in system_type_map.values()):
						id_attribute_map[gid] = []
						id_relation_map[gid] = []
					attr += id_attribute_map[gid]
					rel += id_relation_map[gid]

				attr = list(set(attr))
				rel = list(set(rel))
				for grid in node.member_of:
					gid = str(grid)
					for attr_dict in node.attribute_set:
						for key in attr_dict.keys():
							if(key not in attr):
								id_attribute_map[gid].append(key)
					for rel_dict in node.relation_set:
						for key in rel_dict.keys():
							if(key not in rel):
								id_relation_map[gid].append(key)

			if(node._type == "GSystemType"):
				create_advanced_map(node)
			# if(node._type == "GSystem"):
			# 	update_advanced_map(node)

		

def create_advanced_map(node):
	system_type_map[node.name] = str(node._id)
	attribute_type_set = []
	for attribute in node.attribute_type_set:
		attribute_type_set.append(attribute["name"])
	relation_type_set = []
	for relation in node.relation_type_set:
		relation_type_set.append(relation["name"])
	if(str(node._id) not in id_attribute_map.keys()):
		id_attribute_map[str(node._id)] = []
	if(str(node._id) not in id_relation_map.keys()):
		id_relation_map[str(node._id)] = []
	id_attribute_map[str(node._id)] += attribute_type_set
	id_relation_map[str(node._id)] += relation_type_set		

def main():
	print("Starting the map creation process")
	all_docs = node_collection.find(no_cursor_timeout=True).batch_size(5)
	create_map(all_docs)

	for key,val in id_attribute_map.iteritems():
		id_attribute_map[key] = list(set(val))
	for key,val in id_relation_map.iteritems():
		id_relation_map[key] = list(set(val))

	mapping_directory = "/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings"
	if not os.path.exists(mapping_directory):
		print("creating mapping directory")
		os.makedirs(mapping_directory)

	f = open(mapping_directory+"/authormap.json","w")
	json.dump(author_map,f,indent=4)
	f.close()

	f = open(mapping_directory+"/groupmap.json","w")
	json.dump(group_map,f,indent=4)
	f.close()

	f = open(mapping_directory+"/gsystemtype_map.json","w")
	json.dump(system_type_map,f,indent=4)
	f.close()

	f = open(mapping_directory+"/attribute_map.json","w")
	json.dump(id_attribute_map,f,indent=4)
	f.close()

	f = open(mapping_directory+"/relation_map.json","w")
	json.dump(id_relation_map,f,indent=4)
	f.close()

main()