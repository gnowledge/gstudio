from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from gnowsys_ndf.ndf.models import *
from django_mongokit import get_database
from django.template import RequestContext

database = get_database()
collection = database[Node.collection_name]

def index(request, group_id):
	ins_objectid  = ObjectId()
    	if ins_objectid.is_valid(group_id) is False :
        	group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        	auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      	if group_ins:
       		group_id = str(group_ins._id)
      	else :
        	auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if auth :
         	group_id = str(auth._id)
    	else :
        	pass

	selected_topic = None
	topic_coll = collection.Node.find({"_type": u"GSystem"})
	topic_count =topic_coll.count()
	print "here: " + str(topic_coll)	
	context = RequestContext(request, {'title': "WikiData Topics", 'topic_coll': topic_coll})
	template = "ndf/wikidata.html"
     	variable = RequestContext(request,{'title': "WikiData Topics"})
	context_variables = {'title': "WikiData Topics"}
	context_instance = RequestContext(request, {'title': "WikiData Topics", 'groupid':group_id, 'group_id':group_id})
	attribute_set = None
      	return render(request, template, {'title': "WikiData Topics", 'topic_coll': topic_coll, 'selected_topic': selected_topic, 'attribute_set' : attribute_set, 'groupid':group_id, 'group_id':group_id,'topic_count':topic_count})


def details(request, group_id, topic_id):
	ins_objectid  = ObjectId()
	group_ins = None
    	if ins_objectid.is_valid(group_id) is False :
        	group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        	auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      	if group_ins:
       		group_id = str(group_ins._id)
      	else :
        	auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if auth :
         	group_id = str(auth._id)
    	else :
        	pass

	selected_topic = collection.Node.one({"_type":u"GSystem", "_id":ObjectId(topic_id)})
	topic_coll = collection.Node.find({"_type": u"GSystem"})
	topic_count = topic_coll.count()
	print "here: " + str(topic_coll)	
	context = RequestContext(request, {'title': "WikiData Topics", 'topic_coll': topic_coll})
	template = "ndf/wikidata.html"
     	variable = RequestContext(request,{'title': "WikiData Topics"})
	context_variables = {'title': "WikiData Topics"}
	context_instance = RequestContext(request, {'title': "WikiData Topics", 'groupid':group_id, 'group_id':group_id})
	attribute_set = collection.Node.find({"_type":u"GAttribute", "subject":ObjectId(topic_id)})
	#relation_set = collection.Node.find({"_type":u"GRelation", "subject":ObjectId(topic_id)})
	relation_set = selected_topic.get_possible_relations(selected_topic.member_of)
	relation_set_dict = {}
	
	for rk, rv in relation_set.iteritems():
		if rv["subject_or_right_subject_list"]:
			print "\n val perse : ", rk
			for v in rv["subject_or_right_subject_list"]:
				print "\t", v["name"]
				relation_set_dict[rk] = v["name"]
	flag=0==1
      	return render(request, template, {'title': "WikiData Topics", 'topic_coll': topic_coll, 'selected_topic': selected_topic, 'attribute_set': attribute_set,'relation_set':relation_set_dict, 'groupid':group_id, 'group_id':group_id,'flag':flag,'topic_count':topic_count, 'node':selected_topic})





def tag_view_list(request, group_id, topic_id, tag):
	ins_objectid  = ObjectId()
	group_ins = None
    	if ins_objectid.is_valid(group_id) is False :
        	group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        	auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      	if group_ins:
       		group_id = str(group_ins._id)
      	else :
        	auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if auth :
         	group_id = str(auth._id)
    	else :
        	pass

	all_topic = collection.Node.find({"_type": u"GSystem"})
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
	#attribute_set = collection.Node.find({"_type":u"GAttribute", "subject":ObjectId(topic_id)})
	#relation_set = collection.Node.find({"_type":u"GRelation", "subject":ObjectId(topic_id)})	
	#print attribute_set
	flag =1==1 #passing a true flag value
	selected_topic=None
	topic_count =len(topic_coll)
      	return render(request, template, {'group_id':group_id,'groupid':group_id,'topic_coll':topic_coll,'topic_count':topic_count,'tag':tag,'flag':flag})
	#return render_to_response(template,{'title': "WikiData Topics", 'groupid':group_id, 'group_id':group_id},context_instance=RequestContext(request))

