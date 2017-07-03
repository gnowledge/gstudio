from gnowsys_ndf.ndf.models import *
from elasticsearch import Elasticsearch
from bson import json_util
import os
import sys
import json
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')
es = Elasticsearch("http://elsearch:changeit@gsearch:9200")

# doc_type = ""
author_map = {}
group_map = {}
author_index = "author_clix"
index = "clix"


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
			# print("indexed document %d with id: %s" % (k,document["id"]["$oid"]))
			k+=1

def get_document_type(document):
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
	elif document["type"]=="Author":
		doc_type = "Author"
	elif document["type"]=="GAttribute":
		doc_type = "GAttribute"
	elif document["type"]=="GRelation":
		doc_type = "GRelation"
	elif document["type"]=="AttributeType":
		doc_type = "AttributeType"
	elif document["type"]=="Filehive":
		doc_type = "Filehive"
	elif document["type"]=="RelationType":
		doc_type = "RelationType"
	elif document["type"]=="Group":
		doc_type = "Group"
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
	request_body = {
			"settings": {
				"index.mapping.total_fields.limit": 5000, #Limit of total fields [1000] in index [clix] has been exceeded-bcoz of this error
				"number_of_shards": 1,
				"number_of_replicas": 0,
				"analysis": {
					"analyzer": {
						"trigram": {
							"type": "custom",
							"tokenizer": "standard",
							"stopwords": "_english_",
							"filter": [
								"standard",
								"lowercase",
								"shingle"
							],
							"char_filter": ["html_strip"],
						},
					},
					"filter": {
						# "stopwords": {
						# 	"type": "stop",
						# 	"ignore_case": True,
						# 	"stopwords": "_english_"
						# },
						"shingle": {
							"type": "shingle",
							"min_shingle_size": 2,
							"max_shingle_size": 3
						}
					},
				}
			},
			"mappings": {

				"Author": {
					"properties": {
						"name": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"altnames":{
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"content": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"tags": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						}
					}
				},
				"image": {		#all those Gsystem docs that have mime_type as null
					"properties": {
						"name": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"altnames":{
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"content": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"tags": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						}
					}
				},
				"video": {		#all those Gsystem docs that have mime_type as null
					"properties": {
						"name": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"altnames":{
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"content": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"tags": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						}
					}
				},
				"text": {		#all those Gsystem docs that have mime_type as null
					"properties": {
						"name": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"altnames":{
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"content": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"tags": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						}
					}
				},
				"application": {		#all those Gsystem docs that have mime_type as null
					"properties": {
						"name": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"altnames":{
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"content": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"tags": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						}
					}
				},
				"audio": {		#all those Gsystem docs that have mime_type as null
					"properties": {
						"name": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"altnames":{
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"content": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"tags": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						}
					}
				},
				"NotMedia": {		#all those Gsystem docs that have mime_type as null
					"properties": {
						"name": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"altnames":{
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"content": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"tags": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						}
					}
				},
				"Filehive": {
					"properties": {
						"filename": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}					
						}
					}
				},
				"RelationType": {	
					"properties": {
						"name": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"altnames":{
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"content": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
							}
						},
						"tags": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						}
					}
				},
				"Group": {
					"properties": {
						"name": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"altnames":{
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"content": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"tags": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						}
					}
				},
				"AttributeType": {
					"properties": {
						"name": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"altnames":{
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"content": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"tags": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						}
					}
				},
				"GAttribute": {
					"properties": {
						"name": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						},
						"tags": {
							"type": "text",
							"fields": {
								"trigram": {
									"type": "text",
									"analyzer": "trigram"
								},
								# "reverse": {
								# 	"type": "text",
								# 	"analyzer": "reverse"
								# }
							}
						}
					}
				}
			}
	}

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