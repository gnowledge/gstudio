from elasticsearch import Elasticsearch
from elasticsearch_dsl import *
from gnowsys_ndf.settings import GSTUDIO_ELASTIC_SEARCH ,GSTUDIO_ELASTIC_SEARCH_PROTOCOL,GSTUDIO_ELASTIC_SEARCH_SUPERUSER,GSTUDIO_ELASTIC_SEARCH_SUPERUSER_PASSWORD,GSTUDIO_ELASTIC_SEARCH_ALIAS,GSTUDIO_ELASTIC_SEARCH_PORT,GLITE_RCS_REPO_DIRNAME,GSTUDIO_ELASTIC_SEARCH_INDEX
from gnowsys_ndf.ndf.models.base_imports import *
from gnowsys_ndf.ndf.models.history_manager import HistoryManager
#from gnowsys_ndf.ndf.models.node import *
#from .node import Node
from bson.json_util import loads, dumps
from gnowsys_ndf.ndf.models.models_utils import NodeJSONEncoder

#es = Elasticsearch("http://"+GSTUDIO_ELASTIC_SEARCH_SUPERUSER+":"+GSTUDIO_ELASTIC_SEARCH_SUPERUSER_PASSWORD+"@"+GSTUDIO_ELASTIC_SEARCH_ALIAS+":"+GSTUDIO_ELASTIC_SEARCH_PORT, timeout=100, retry_on_timeout=True)

es = Elasticsearch(GSTUDIO_ELASTIC_SEARCH_PROTOCOL+"://"+GSTUDIO_ELASTIC_SEARCH_SUPERUSER+":"+GSTUDIO_ELASTIC_SEARCH_SUPERUSER_PASSWORD+"@"+GSTUDIO_ELASTIC_SEARCH_ALIAS+":"+GSTUDIO_ELASTIC_SEARCH_PORT,timeout=100, retry_on_timeout=True)

class esearch:
    
    #objects = models.Manager()
    
    #def __init__(self,fp):
    #	self.fp = fp
    @staticmethod
    def inject(fp):

        with open("/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/gstudio_configs/req_body.json") as req_body:
            request_body = json.load(req_body)

        if not os.path.exists(GLITE_RCS_REPO_DIRNAME):
			os.makedirs(GLITE_RCS_REPO_DIRNAME)
		
        #fp = history_manager.get_file_path(self)

        rcs_obj = RCS()
        rcs_obj.checkout(fp, otherflags="-f")

        temp1 = fp[:-29]
        temp2 = temp1[14:]

        glite_fp = "/data/"+GLITE_RCS_REPO_DIRNAME+ temp2

        try:
            os.makedirs(glite_fp)
        except OSError as exc:  # Python >2.5
            if os.path.isdir(glite_fp):
                pass
            else:
                raise

        temp = "cp " +fp+" "+glite_fp 
        os.system(temp)
        #temp = "rm -rf"+" "+fp
        #os.system(temp)
        
        #glite_fp = glite_fp + self._id + ".json"

        #with open(fp, 'r') as f:
        #    document = json.load(f)

        read_file_data = open(fp,'r').read()

        convert_oid_to_object_id = loads(read_file_data)

        doc = json.dumps(convert_oid_to_object_id,cls=NodeJSONEncoder)

        document = json.loads(doc)


        document["id"] = document.pop("_id")
        document["type"] = document.pop("_type")

        document_type = document["type"]

        index = None

        for k in GSTUDIO_ELASTIC_SEARCH_INDEX:
            for v in GSTUDIO_ELASTIC_SEARCH_INDEX[k]:
                if document_type in v:
                    index = k
                    index = index.lower()
                    
                    break

        document_type

        if document_type == "GSystem":
            es.index(index=index, doc_type="gsystem", id=document["id"], body=document)
            #file_name.write(document["id"] + '\n')
            if document["type"]=="GSystem":
                if('if_file' in document.keys()):
                    if(document["if_file"]["mime_type"] is not None):
                        data = document["if_file"]["mime_type"].split("/")
                        doc_type = data[0]
                    else:
                        doc_type = "notmedia"
                else:
                    doc_type = "notmedia"

            else:
                doc_type = "dontcare"
            
            if (not es.indices.exists("gsystem")):
                res = es.indices.create(index="gsystem", body=request_body)
            es.index(index="gsystem", doc_type=doc_type, id=document["id"], body=document)
            
        else:
            
            es.index(index=index, doc_type=document_type.lower(), id=document["id"], body=document)
        

    @staticmethod
    def es_filters(query_dict):
        i=-1
        strconcat=""
        endstring=""
        temp_dict={}
        lists = []

        for each in list(query_dict):
            for temp in each.values():
                for a in temp:
                    for key,value in a.items():
                        if isinstance(value, dict):

                            if value["$in"]:
                                key = list(key)
                                key[13]='__'
                                t="".join(key)
                                temp_dict[t]=value["$in"][0]
                                lists.append("Q('match',"+t+"=dict(query='"+value["$in"][0]+"',type='phrase'))")
                            elif value["$or"]:
                                key = list(key)
                                key[13]='__'
                                t="".join(key)
                                temp_dict[t]=value["$or"][0]
                                lists.append("Q('match',"+t+"=dict(query='"+value["$or"][0]+"',type='phrase'))")
                        elif isinstance(value, tuple):
                            temp_dict["language"]= value[1]
                            #strconcat=strconcat+"Q('match',"+key+"='"+value[1]+"') "
                            strconcat=strconcat+"Q('match',"+key+"=dict(query='"+value[1]+"',type='phrase'))$$"
                            lists.append("Q('match',"+key+"=dict(query='"+value[1]+"',type='phrase'))")
                        else:
                            if key != "source":
                                key = list(key)
                                key[13]='__'
                                t="".join(key)
                                temp_dict[t]=value
                                lists.append("Q('match',"+t+"=dict(query='"+value+"',type='phrase'))")  
                            else:
                                temp_dict[key]=value
                                lists.append("Q('match',"+key+"=dict(query='"+value+"',type='phrase'))")
        return lists