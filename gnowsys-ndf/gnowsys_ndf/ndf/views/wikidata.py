from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import get_execution_time

@get_execution_time
def index(request, group_id):
	# ins_objectid  = ObjectId()
 #    	if ins_objectid.is_valid(group_id) is False :
 #        	group_ins = node_collection.find_one({'_type': "Group","name": group_id})
 #        	auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
 #      	if group_ins:
 #       		group_id = str(group_ins._id)
 #      	else :
 #        	auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
 #        if auth :
 #         	group_id = str(auth._id)
 #    	else :
 #        	pass
	try:
		group_id = ObjectId(group_id)
	except:
		group_name, group_id = get_group_name_id(group_id)
	
	tag_coll = []
	selected_topic = None
	topic_coll = node_collection.find({"_type": u"GSystem"})
	topic_count =topic_coll.count()
	#print "here: " + str(topic_coll)	
	topics = node_collection.find({"_type": u"GSystem"})
	#Tag collection
	tag_count = 0
	for topic1 in topics:
		for tag1 in topic1.tags:
			tag_coll.append(tag1)
			tag_count += 1
	
	
	context = RequestContext(request, {'title': "WikiData Topics", 'topic_coll': topic_coll})
	template = "ndf/wikidata.html"
     	variable = RequestContext(request,{'title': "WikiData Topics"})
	context_variables = {'title': "WikiData Topics"}
	context_instance = RequestContext(request, {'title': "WikiData Topics", 'groupid':group_id, 'group_id':group_id})
	attribute_set = None
      	return render(request, template, {'title': "WikiData Topics", 'topic_coll': topic_coll, 'tag_count': tag_count, 'tag_coll': tag_coll, 'selected_topic': selected_topic, 'attribute_set' : attribute_set, 'groupid':group_id, 'group_id':group_id,'topic_count':topic_count})

@get_execution_time
def details(request, group_id, topic_id):
	# ins_objectid  = ObjectId()
	# group_ins = None
 #    	if ins_objectid.is_valid(group_id) is False :
 #        	group_ins = node_collection.find_one({'_type': "Group","name": group_id})
 #        	auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
 #      	if group_ins:
 #       		group_id = str(group_ins._id)
 #      	else :
 #        	auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
 #        if auth :
 #         	group_id = str(auth._id)
 #    	else :
 #        	pass
	try:
		group_id = ObjectId(group_id)
	except:
		group_name, group_id = get_group_name_id(group_id)

	selected_topic = node_collection.one({"_type":u"GSystem", "_id":ObjectId(topic_id)})
	topic_coll = node_collection.find({"_type": u"GSystem"})
	topic_count = topic_coll.count()
	#print "here: " + str(topic_coll)	
	context = RequestContext(request, {'title': "WikiData Topics", 'topic_coll': topic_coll})
	template = "ndf/wikidata.html"
     	variable = RequestContext(request,{'title': "WikiData Topics"})
	context_variables = {'title': "WikiData Topics"}
	context_instance = RequestContext(request, {'title': "WikiData Topics", 'groupid':group_id, 'group_id':group_id})
	attribute_set = triple_collection.find({"_type":u"GAttribute", "subject":ObjectId(topic_id)})
	#relation_set = triple_collection.find({"_type":u"GRelation", "subject":ObjectId(topic_id)})
	relation_set = selected_topic.get_possible_relations(selected_topic.member_of)
	#print relation_set
	relation_set_dict = {}
	
	for rk, rv in relation_set.iteritems():
		if rv["subject_or_right_subject_list"]:
			#print "\n val perse : ", rk
			for v in rv["subject_or_right_subject_list"]:
				#print "\t", v["name"]
				relation_set_dict[rk] = v["name"]
	flag=0==1
      	return render(request, template, {'title': "WikiData Topics", 'topic_coll': topic_coll, 'selected_topic': selected_topic, 'attribute_set': attribute_set,'relation_set':relation_set_dict, 'groupid':group_id, 'group_id':group_id,'flag':flag,'topic_count':topic_count, 'node':selected_topic})




@get_execution_time
def tag_view_list(request, group_id, topic_id, tag):
	# ins_objectid  = ObjectId()
	# group_ins = None
 #    	if ins_objectid.is_valid(group_id) is False :
 #        	group_ins = node_collection.find_one({'_type': "Group","name": group_id})
 #        	auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
 #      	if group_ins:
 #       		group_id = str(group_ins._id)
 #      	else :
 #        	auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
 #        if auth :
 #         	group_id = str(auth._id)
 #    	else :
 #        	pass
	try:
		group_id = ObjectId(group_id)
	except:
		group_name, group_id = get_group_name_id(group_id)

	all_topic = node_collection.find({"_type": u"GSystem"})
	topic_coll=['None']	
	for topic in all_topic:
		if tag in topic.tags:
			topic_coll.remove('None')
			topic_coll.append(topic)


	
	context = RequestContext(request, {'title': "WikiData Topics", 'topic_coll': topic_coll})
	template = "ndf/wikidata.html"
     	variable = RequestContext(request,{'title': "WikiData Topics"})
	context_variables = {'title': "WikiData Topics"}
	context_instance = RequestContext(request, {'title': "WikiData Topics", 'groupid':group_id, 'group_id':group_id})
	#attribute_set = triple_collection.find({"_type":u"GAttribute", "subject":ObjectId(topic_id)})
	#relation_set = triple_collection.find({"_type":u"GRelation", "subject":ObjectId(topic_id)})	
	#print attribute_set
	flag =1==1 #passing a true flag value
	selected_topic=None
	topic_count =len(topic_coll)
      	return render(request, template, {'group_id':group_id,'groupid':group_id,'topic_coll':topic_coll,'topic_count':topic_count,'tag':tag,'flag':flag})
	#return render_to_response(template,{'title': "WikiData Topics", 'groupid':group_id, 'group_id':group_id},context_instance=RequestContext(request))

