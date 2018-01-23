from bson import json_util
import os
import sys
import json
from elasticsearch import Elasticsearch
from gnowsys_ndf.ndf.models import *

#from gnowsys_ndf.settings import GSTUDIO_SITE_NAME
#from gnowsys_ndf.local_settings import GSTUDIO_DOCUMENT_MAPPING
from gnowsys_ndf.local_settings import GSTUDIO_ELASTIC_SEARCH_INDEX

##### use the below commented lines if you are working with Python 2.x   #####
# reload(sys)
# sys.setdefaultencoding('UTF8')

es = Elasticsearch("http://elastic:changeme@gsearch:9200", timeout=100, retry_on_timeout=True)

#author_index = "author_" + GSTUDIO_SITE_NAME.lower()
#index = GSTUDIO_SITE_NAME.lower()
#gsystemtype_index = "node_type_" + GSTUDIO_SITE_NAME.lower()



page_id = 0


def index_docs(all_docs,index,doc_type,file_name):
    k = 0
    all_docs_count = all_docs.count()
    for docs in all_docs:
        print "[ %s/%s ] : %s " % (k, all_docs_count, docs._id)


        doc = json.dumps(docs, cls=NodeJSONEncoder)  # convert mongoDB object to a JSON string
        # doc = json.loads(doc,object_hook=json_util.object_hook) ->get back mongoDB object from JSON string

        document = json.loads(doc)  # convert JSON string to a python dictionary
        # doc = json.dumps(document) #convert python dictionary to JSON string
        document["id"] = document.pop("_id")
        document["type"] = document.pop("_type")

        #for docs in doc_type:
        print document["type"]
        #print document

        if document["type"] == "GAttribute":
            es.index(index=index, doc_type="gattribute", id=document["id"], body=document)
            #file_name.write(document["id"] + '\n')

        elif document["type"] == "GRelation":
            es.index(index=index, doc_type="grelation", id=document["id"], body=document)
            #file_name.write(document["id"] + '\n')
        elif document["type"] == "MetaType":
            es.index(index=index, doc_type="metaType", id=document["id"], body=document)
            #file_name.write(document["id"] + '\n')
        elif document["type"] == "GSystemType":
            es.index(index=index, doc_type="gsystemType", id=document["id"], body=document)
            #file_name.write(document["id"] + '\n')
        elif document["type"] == "Author":
            es.index(index=index, doc_type="author", id=document["id"], body=document)
            #file_name.write(document["id"] + '\n')
        elif document["type"] == "RelationType":
            es.index(index=index, doc_type="relationtype", id=document["id"], body=document)
            #file_name.write(document["id"] + '\n')
        elif document["type"] == "AttributeType":
            es.index(index=index, doc_type="attributetype", id=document["id"], body=document)
            #file_name.write(document["id"] + '\n')
        elif document["type"] == "GSystem":
            es.index(index=index, doc_type="gsystem", id=document["id"], body=document)
            #file_name.write(document["id"] + '\n')
            get_doc_type=get_document_type(document)
            print(get_doc_type)
            es.index(index=index, doc_type=get_doc_type, id=document["id"], body=document)

        elif document["type"] == "Group":
            es.index(index=index, doc_type="group", id=document["id"], body=document)
            #file_name.write(document["id"] + '\n')
        elif document["type"] == "ToReduceDocs":
            es.index(index=index, doc_type="toreducedocs", id=document["id"], body=document)
           # file_name.write(document["id"] + '\n')
        elif document["type"] == "node_holder":
            es.index(index=index, doc_type="node_holder", id=document["id"], body=document)
            #file_name.write(document["id"] + '\n')
        elif document["type"] == "File":
            es.index(index=index, doc_type="file", id=document["id"], body=document)
            #file_name.write(document["id"] + '\n')

        else:
            print index
            # print str(doc_type).strip('[]').replace("'", "").lower()
            es.index(index=index, doc_type=str(doc_type).strip('[]').replace("'", "").lower(), id=document["id"],
                     body=document)
            #file_name.write(document["id"] + '\n')


        k += 1

    #file_name.close()



def get_document_type(document):

	if document["type"]=="GSystem":
		#for ids in document['member_of']:  #document is a member of the Page GSystemType
			#if(ids == page_id):
				#return "Page"
		if('if_file' in document.keys()):
			if(document["if_file"]["mime_type"] is not None):
				data = document["if_file"]["mime_type"].split("/")
				doc_type = data[0]
			else:
				doc_type = "NotMedia"
		else:
			doc_type = "NotMedia"

	else:
		doc_type = "DontCare"
	return doc_type



def main():


    nodes = node_collection.find(no_cursor_timeout=True).batch_size(5)
    triples= triple_collection.find(no_cursor_timeout=True).batch_size(5)
    benchmarks = benchmark_collection.find(no_cursor_timeout=True).batch_size(5)
    filehives = filehive_collection.find(no_cursor_timeout=True).batch_size(5)
    buddys = buddy_collection.find(no_cursor_timeout=True).batch_size(5)
    counters = counter_collection.find(no_cursor_timeout=True).batch_size(5)

    #all_docs = [ triples, buddys, benchmarks, nodes, counters]
    print("Starting the indexing process...")

    res = es.search(index="nodes", body={"query": {"match_all": {}},"_source": ["id"] }, scroll= "1m",size="10000")

    print(res['_scroll_id'])
    print(res['hits']['total'])



    if( res['hits']['total'] < nodes.counts()):
        if(nodes.counts() < 10000):
            f = open("/data/nodes.txt", "w+")
            os.chmod("/data/nodes.txt", 0o777)
            for hit in res['hits']['hits']:
                #print(hit["_source"]["id"])
                f.write(hit["_source"]["id"] + '\n')


    f.close()
    # DELETING existing/old indexes

    for index in GSTUDIO_ELASTIC_SEARCH_INDEX.keys():
        if (es.indices.exists(index.lower())):
            print("Deleting the existing index: " + index.lower() + " for reindexing")
            res = es.indices.delete(index=index.lower())
            print("The delete response is %s " % res)

    # --- END of DELETING existing/old indexes


    i=0

    with open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/req_body.json") as req_body:
        request_body = json.load(req_body)

    for index, doc_type in GSTUDIO_ELASTIC_SEARCH_INDEX.items():
        res = es.indices.create(index=index.lower(), body=request_body)
        print("Response for index creation")
        #print "%s/%s" %(i,len(all_docs))

        if(index.strip('[]').lower()=="triples"):
            #f = open("/data/triples.txt", "w")
            #os.chmod("/data/triples.txt", 0o777)
            index_docs(triples ,index.lower(),doc_type,f)

        elif(index.strip('[]').lower()=="buddies"):
            #f = open("/data/buddies.txt", "w")
            #os.chmod("/data/buddies.txt", 0o777)
            index_docs(buddys, index.lower(), doc_type,f)

        elif(index.strip('[]').lower()=="benchmarks"):
            #f = open("/data/benchmarks.txt", "w+")
            #os.chmod("/data/benchmarks.txt", 0o777)
            index_docs(benchmarks, index.lower(), doc_type,f)

        elif (index.strip('[]').lower() == "nodes"):
            #f = open("/data/nodes.txt", "w+")
            #os.chmod("/data/nodes.txt", 0o777)
            index_docs(nodes, index.lower(), doc_type,f)

        elif (index.strip('[]').lower() == "counters"):
            #f = open("/data/counters.txt", "w")
            #os.chmod("/data/counters.txt", 0o777)
            index_docs(counters, index.lower(), doc_type,f)

        elif (index.strip('[]').lower() == "filehives"):
            #f = open("/data/filehives.txt", "w")
            ##os.chmod("/data/filehives.txt", 0o777)
            index_docs(filehives, index.lower(), doc_type,f)

        i=i+1

main()