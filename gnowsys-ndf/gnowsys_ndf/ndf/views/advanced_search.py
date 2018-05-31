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
from gnowsys_ndf.ndf.models import node_collection,GSystemType
from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.views.methods import get_group_name_id, cast_to_data_type, get_execution_time
from gnowsys_ndf.ndf.views.methods import get_filter_querydict
from gnowsys_ndf.ndf.gstudio_es.es import *
from gnowsys_ndf.ndf.gstudio_es.paginator import Paginator ,EmptyPage, PageNotAnInteger
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_relation_value
from gnowsys_ndf.settings import GSTUDIO_ELASTIC_SEARCH
from django.core.exceptions import PermissionDenied

def search_detail(request,group_id,page_num=1):
	if GSTUDIO_ELASTIC_SEARCH:
		if not request.user.is_superuser:
			raise PermissionDenied
		q = Q('match',name=dict(query='File',type='phrase'))
		GST_FILE = Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
		GST_FILE1 = GST_FILE.execute()

		q = Q('match',name=dict(query='Page',type='phrase'))
		GST_PAGE = Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
		GST_PAGE1 = GST_PAGE.execute()

		q = Q('match',name=dict(query='interactive_page',type='phrase'))
		GST_IPAGE = Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
		GST_IPAGE1 = GST_IPAGE.execute()

		search_result = ''
		try:
			group_id = ObjectId(group_id)

		except:
			group_name, group_id = get_group_name_id(group_id)

		group_name_of_twist, group_id_of_twist = GSystemType.get_gst_name_id("Twist")
		chk_advanced_search = request.GET.get('chk_advanced_search',None)

		if request.GET.get('field_list',None):
			selected_field = request.GET.get('field_list',None)
		else:
			selected_field = "content"

		q = Q('bool', must=[Q('match',group_set=str(group_id)),Q('match',access_policy='public'),~Q('exists',field=selected_field)],
			should=[Q('match', member_of=GST_FILE1.hits[0].id),Q('match', member_of=GST_IPAGE1.hits[0].id)],
			must_not=[Q('match', member_of=GST_PAGE1.hits[0].id)])
		search_result =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q)
		search_result = search_result.exclude('terms', name=['thumbnail','jpg','png','svg'])

		if request.GET.get('field_list',None) == "true":

			search_text = request.GET.get("search_text",None)

			q = Q('bool', must=[Q('match', language='en'),Q('match', access_policy='public'),Q('match', group_set=str(group_id)),
				Q('terms', content=[search_text])] )
			search_result =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q)

		if_teaches = False
		search_str_user=""
		page_no = request.GET.get('page_no',None)

		has_next = True
		if search_result.count() <=20:
			has_next = False

		if request.GET.get('page_no',None) in [None,'']:
			search_result=search_result[0:20]
			page_no = 2
		else:
			p = int(int(page_no) -1)
			temp1=int((int(p)) * 20)
			temp2=temp1+20
			search_result=search_result[temp1:temp2]

			if temp1 < search_result.count() <= temp2:
				has_next = False
			page_no = int(int(page_no)+1)
		paginator_search_result = None

		if request.GET.get('field_list',None) == "attribute_type_set" or page_num > 1 :
			temp = node_collection.find({'_type': 'GSystem','access_policy':'PUBLIC','member_of': { '$nin': [ObjectId(group_id_of_twist)] } ,'group_set':ObjectId(group_id)}).limit(1000)

			lst = []
			for each in temp:
			    if each._id:
			        rel_val = get_relation_value(ObjectId(each._id),"teaches")
			        if not rel_val['grel_id']:
						lst.append(each._id)

			search_result = node_collection.find({ '_id': {'$in': lst} }).limit(1000)
			if_teaches = True
			paginator_search_result = paginator.Paginator(search_result, page_num, 30)

		return render_to_response('ndf/asearch.html', {"page_info":paginator_search_result,"page_no":page_no,"has_next":has_next,'GSTUDIO_ELASTIC_SEARCH':GSTUDIO_ELASTIC_SEARCH,'advanced_search':"true",'groupid':group_id,'group_id':group_id,'title':"advanced_search","search_curr":search_result,'field_list':selected_field,'chk_advanced_search':chk_advanced_search,'if_teaches':if_teaches},
					context_instance=RequestContext(request))

