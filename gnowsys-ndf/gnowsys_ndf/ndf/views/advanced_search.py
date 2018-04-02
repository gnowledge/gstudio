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
from gnowsys_ndf.ndf.models.es import *
from gnowsys_ndf.ndf.paginator import Paginator ,EmptyPage, PageNotAnInteger
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
	print chk_advanced_search
	if request.GET.get('field_list',None):
		selected_field = request.GET.get('field_list',None)
	else:
		selected_field = "content"
	print selected_field
	print "mmmmmmmmmmmmmmmmmmmmmmmmmmmm----------------------"
	#,Q('exists',field='content')55ab34ff81fccb4f1d806025

	q = Q('bool', must=[Q('match', member_of=GST_FILE1.hits[0].id),Q('match',group_set='55ab34ff81fccb4f1d806025'),Q('match',access_policy='public'),~Q('exists',field=selected_field)])
	search_result =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q)
	#search_result.filter('exists', field='attribute_set__educationaluse')

	if request.GET.get('field_list',None) == "true":
		print "chk_advanced_search"
		#q = Q('bool', must=[Q('match',language=dict(query='english',type='phrase')),Q('match', access_policy='public'),Q('match', group_set=str(group_id))])
		#lan = Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q)
		#lan1 = lan.execute()
		#print lan.count()
		print ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
		#Q('match',language=dict(query='hindi',type='phrase'))
		#Q('match', content=request.GET.get('search_text','')),
		q = Q('bool', must=[Q('match', language='en'),Q('match', access_policy='public'),Q('match', group_set=str(group_id))])
		search_result =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q)
		#search_result =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author")
		#search_result.filter( 'range', gte='900', lte='097f', field='content' )
		#for a in search_result:
		#	print a.id
		search_result = search_result.filter("terms", content=["ncert"])
		
    	#search_result.query('regexp', title="my * is")
		response = s.execute()


	search_str_user=""
	#print search_result.count()
	#print group_id

	page_no = request.GET.get('page_no',None)
	print page_no
	print "44444444444444444444444444"

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
		print "if block"
		temp = node_collection.find({'_type': 'GSystem'})
		

		lst = []
		for each in temp:
		    if each._id:
		        rel_val = get_relation_value(ObjectId(each._id),"teaches")
		        if not rel_val['grel_id']:
		            lst.append(each._id)

		search_result = node_collection.find({ '_id': {'$in': lst} })


		#print search_result1
		print "aaaaaaaaaaaa"
		#temp.rewind()




	return render_to_response('ndf/asearch.html', {"page_no":page_no,"has_next":has_next,'GSTUDIO_ELASTIC_SEARCH':GSTUDIO_ELASTIC_SEARCH,'advanced_search':"true",'groupid':group_id,'group_id':group_id,'title':"advanced_search","search_curr":search_result,'field_list':selected_field,'chk_advanced_search':chk_advanced_search},
				context_instance=RequestContext(request))
		 
