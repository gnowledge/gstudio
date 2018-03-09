from elasticsearch import Elasticsearch
from elasticsearch_dsl import *
from gnowsys_ndf.local_settings import GSTUDIO_ELASTIC_SEARCH

es = Elasticsearch("http://elastic:changeme@gsearch:9200", timeout=100, retry_on_timeout=True)

es_client = Search(using=es)

