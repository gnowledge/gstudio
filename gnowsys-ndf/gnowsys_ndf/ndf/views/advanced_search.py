import re
import urllib

''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response
from django.template import RequestContext
from mongokit import paginator


try:
	from bson import ObjectId
except ImportError:  # old pymongo
	from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
# from gnowsys_ndf.ndf.models import Node, GRelation,GSystemType,File,Triple
from gnowsys_ndf.ndf.models import Node, GRelation,GSystemType, Triple
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.views.methods import get_group_name_id, cast_to_data_type, get_execution_time
from gnowsys_ndf.ndf.views.methods import get_filter_querydict
from gnowsys_ndf.ndf.gstudio_es.es import *
from gnowsys_ndf.ndf.gstudio_es.paginator import Paginator ,EmptyPage, PageNotAnInteger
from gnowsys_ndf.local_settings import GSTUDIO_ADVANCED_SEARCH
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_relation_value



q = Q('match',name=dict(query='File',type='phrase'))
GST_FILE = Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
GST_FILE1 = GST_FILE.execute()

def search_detail(request,group_id,page_no=1):

	search_result = ''
	try:
		group_id = ObjectId(group_id)

	except:
		group_name, group_id = get_group_name_id(group_id)

	chk_advanced_search = request.GET.get('chk_advanced_search',None)
	
	if request.GET.get('field_list',None):
		selected_field = request.GET.get('field_list',None)
	else:
		selected_field = "content"


	q = Q('bool', must=[Q('match', member_of=GST_FILE1.hits[0].id),Q('match',group_set='55ab34ff81fccb4f1d806025'),Q('match',access_policy='public'),~Q('exists',field=selected_field)])
	search_result =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q)

	if request.GET.get('field_list',None) == "true":

		search_text = request.GET.get("search_text",None)

		q = Q('bool', must=[Q('match', language='en'),Q('match', access_policy='public'),Q('match', group_set=str(group_id)),
			Q('bool', must=[Q('match_phrase', content=search_text)])])
		search_result =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q)


	if_teaches = False

	search_str_user=""


	page_no = request.GET.get('page_no',None)

	has_next = True
	if search_result.count() <=20:
		has_next = False

	if request.GET.get('page_no',None) in [None,'']:
		print "siddhu11"
		search_result=search_result[0:20]
		page_no = 2	
	else:
		p = int(int(page_no) -1)
		temp1=int((int(p)) * 20)
		temp2=temp1+20
		search_result=search_result[temp1:temp2]

		if temp1 < search_result.count() <= temp2:
			print temp2
			has_next = False
		page_no = int(int(page_no)+1)

	if request.GET.get('field_list',None) == "attribute_type_set" :
		
		temp = node_collection.find({'_type': 'GSystem','access_policy':'PUBLIC'})
		
		lst = []
		for each in temp:
		    if each._id:
		        rel_val = get_relation_value(ObjectId(each._id),"teaches")
		        if not rel_val['grel_id']:
		            lst.append(each._id)

		search_result = node_collection.find({ '_id': {'$in': lst} })

		if_teaches = True


	return render_to_response('ndf/asearch.html', {"page_no":page_no,"has_next":has_next,'GSTUDIO_ELASTIC_SEARCH':GSTUDIO_ELASTIC_SEARCH,'advanced_search':"true",'groupid':group_id,'group_id':group_id,'title':"advanced_search","search_curr":search_result,'field_list':selected_field,'chk_advanced_search':chk_advanced_search,'if_teaches':if_teaches},
				context_instance=RequestContext(request))
		 
