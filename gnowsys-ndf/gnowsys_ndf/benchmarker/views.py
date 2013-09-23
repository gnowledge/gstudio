#-*- coding: iso-8859-1 -*

import datetime
import random
import csv
from cStringIO import StringIO
from time import time, sleep

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.timezone import utc
from gnowsys_ndf.ndf.models import *
from django_mongokit import get_database

'''
	The First method to get called.
'''
def run(request):
    how_many = int(request.GET.get('how_many', 10))

    TESTS = (('mongokit', _create_author_nodes, _create_nodes, 
    					  _read_nodes_without_ref, _read_nodes_with_ref, 
    					  _edit_nodes, 
    					  _delete_nodes, _delete_author_nodes, 
    					  _create_attribute_type,
    					  _create_GSystemType,
    					  _create_GSystem,
    					  _create_relation_type,
    					  _delete_gsystem_nodes,
    					  _delete_relation_type_nodes,
    					  _delete_gsystem_type_nodes,
    					  _delete_attribute_type_nodes,
              settings.DATABASES['mongodb']['ENGINE']),
             )

    response = StringIO()
	
    # Assigning short names to TEST var's set items respectively		
    for label, author_creator, node_creator, reader1, reader2, editor, deletor, author_deletor, attribute_type_creator, create_gsystem_type, create_gsystem, create_rt, _delete_gsystem, delete_rt, delete_gsystem_t, delete_at, engine in TESTS:
        total = 0.0
        print >>response, label, engine , "\n\n"
        
        print >>response, " CREATION OF OBJECTS :\n"        
        #Calling method _create_author_nodes() to create author nodes for inserting id's into Node class instance       
        data = _create_author_nodes_PreProc(how_many) #To gather required data for Author object
        t0=time()
        author_ids = author_creator(how_many,data)
        t1=time()
        total += t1-t0
        print >>response, "\t Creating", how_many, "Author objects took", t1-t0, "seconds"

        # give it a rest so that the database can  index all the IDs
        sleep(1)

        #Calling method _create_nodes() to create Node objects
        data = _create_nodes_PreProc(how_many) #To gather required data for Node object
        t0=time()
        ids = node_creator(how_many,data)
        t1=time()
        total += t1-t0
        print >>response, "\t Creating", how_many, "Node   objects took", t1-t0, "seconds"

        sleep(1)

        print >>response, "\n\n READING OBJECTS :\n"        
        #Calling method _read_nodes_without_ref() to read node objects.
        t0=time()
        data = reader1(ids)
        t1=time()
        total += t1-t0
        print >>response, "\t Reading ", how_many, "Node   objects took", t1-t0, "seconds (Withot reference to Author object)"
        #print >>response, data

        sleep(1)

        #Calling method _read_nodes_with_ref() to read node objects.
        t0=time()
        data = reader2(ids)
        t1=time()
        total += t1-t0
        print >>response, "\t Reading ", how_many, "Node   objects took", t1-t0, "seconds (With referencing Author object to get Author document)"        

        sleep(1)

        print >>response, "\n\n UPDATING OBJECTS :\n"        
        #Calling method _edit_nodes() to edit node objects.
        t0=time()
        editor(ids)
        t1=time()
        total += t1-t0
        print >>response, "\t Editing ", how_many, "nodes  objects took", t1-t0, "seconds"
	
        sleep(1)

        print >>response, "\n\n DELETION OF OBJECTS :\n"        
        #Calling method _delete_nodes() to delete node objects.
        t0=time()
        deletor(ids)
        t1=time()
        total += t1-t0
        print >>response, "\t Deleting", how_many, "nodes  objects took", t1-t0, "seconds"

        # give it a rest so that the database can index all the IDs
        sleep(1)
        
        #Calling method _delete_author_nodes() to delete Author objects.
        t0=time()
        author_deletor(author_ids)
        t1=time()
        total += t1-t0
        print >>response, "\t Deleting", how_many, "Author objects took", t1-t0, "seconds"
	
	#Print final result.
        print >>response, "\n\n -------------------------------------------------------------------"	
        print >>response, "\n FINAL RESULT : TOTAL TIME REQUIRED IS ", total, "seconds"

	#Attribute_type
        print >>response, "\n -------------------------------------------------------------------\n"	

        sleep(1)
        
        #Calling method attribute_type_creator(how_many) to create attribute_type objects.
        t0=time()
        a = attribute_type_creator()
        t1=time()
        total += t1-t0
        print >>response, "\t Creating", how_many, "Attribute Type objects took", t1-t0, "seconds"

        sleep(1)
        
        #Calling method gsystem_type_creator(how_many) to create attribute_type objects.
        t0=time()
	s = _create_GSystemType()
        t1=time()
        total += t1-t0
        print >>response, "\t Creating", how_many, "GsystemType objects took", t1-t0, "seconds"

        sleep(1)
        
        #Calling method gsystem_creator(how_many) to create attribute_type objects.
        t0=time()
	s = _create_GSystem()
        t1=time()
        total += t1-t0
        print >>response, "\t Creating", how_many, "Gsystem objects took", t1-t0, "seconds"

        sleep(1)
        
        #Calling method relation_type_creator() to create relation_type objects.
        t0=time()
        r = _create_relation_type()
        t1=time()
        total += t1-t0
        print >>response, "\t Creating RelationType objects took", t1-t0, "seconds"

        sleep(1)
        
        #Calling method delete_attribute_type_node() to delete attribute_type objects.
        t0=time()
	_delete_gsystem_nodes()
        t1=time()
        total += t1-t0
        print >>response, "\n\t Deleting GSystem objects took", t1-t0, "seconds"


        sleep(1)
        
        #Calling method delete_attribute_type_node() to delete attribute_type objects.
        t0=time()
	_delete_relation_type_nodes()
        t1=time()
        total += t1-t0
        print >>response, "\t Deleting RelationType objects took", t1-t0, "seconds"

        sleep(1)
        
        #Calling method _delete_gsystem_type_nodes() to delete attribute_type objects.
        t0=time()
	_delete_gsystem_type_nodes()
        t1=time()
        total += t1-t0
        print >>response, "\t Deleting GSystemType objects took", t1-t0, "seconds"

        sleep(1)
        
        #Calling method delete_attribute_type_node() to delete attribute_type objects.
        t0=time()
	_delete_attribute_type_nodes()
        t1=time()
        total += t1-t0
        print >>response, "\t Deleting AttributeType objects took", t1-t0, "seconds"

    return HttpResponse(response.getvalue(), mimetype='text/plain')

    
'''
	Method to return document by accepting two args: ObjectId and collection_name.
'''
def _get_document(id_, collection):
    #print id_, collection
    #collection = get_database()[coll.collection_name]    
    document = collection.one({'_id': ObjectId(id_)})
    #print document
    return document


'''
	Method __random_name() to generate random names for node objects.
'''
def __random_name():
    return random.choice(
        (u'gnowsys',
         u'knowledge network',
         u'gnu',
         u"homi bhabha center for science education",
         u'tata institute of fundaemental research',
         u'Mumbai',
         u'gnowledge lab',
         u"free software",
         u'free knowledge',
        ))


'''
	Method __random_tags() to generate tags for node objects.
'''
def __random_tags():
    tags = [u'one', u'two', u'three', u'four', u'five', u'six',
            u'seven', u'eight', u'nine', u'ten']
    random.shuffle(tags)
    return tags[:random.randint(0, 3)]


'''
	Method __get_author_id() to select id/s of author.
'''
def __get_author_id(check):
	a_col = get_database()[Author.collection_name]
	a_cur = a_col.Author.find()
	
	#To return only one random Author object id
	if (check == "one"):
		return  a_cur[random.randint(0, (a_cur.count() - 1) if (a_cur.count()) else 0 ) ]._id
	#To return many random Author object id's		
	elif (check == "list"):
		l = []
		r = random.randint(1,9)
		for i in range(r): 
			l.append(a_cur[random.randint(0, (a_cur.count() - 1) if (a_cur.count()) else 0 ) ]._id)
		return l


'''
	Method __get_bool_value() to randomly generate bool values.
'''
def __get_bool_value():
	r = random.randint(0,9)
	return True if (r % 2 == 0) else False


'''
	Method __create_nodes_PreProc() to generate data for directly inserting into nodes objects.
	This method aims to avoid time required for: calling function and getting random values during node creation time.
'''
def _create_nodes_PreProc(how_many):
	
	name = altnames = plural = []
	tags = []
	start_publication = created_at = last_update = []
	featured = comment_enabled = login_required = []
	modified_by = []	
	created_by = []
    
	data = [name, altnames, plural, tags, start_publication, featured, comment_enabled, login_required, modified_by, last_update, created_at, created_by]
	for i in range(how_many):
		name.append(__random_name())
		altnames.append(__random_name())
		plural.append(__random_name())
		tags.append(__random_tags())
        
		start_publication.append(__random_creationdate())
		featured.append(__get_bool_value())
		comment_enabled.append(__get_bool_value())
		login_required.append(__get_bool_value())

		modified_by.append(__get_author_id("list"))				# list of Author Class id's
		last_update.append(__random_creationdate())

		created_at.append(__random_creationdate())
		created_by.append(__get_author_id("one"))
	#print data
	return data


'''
	Method __create_nodes() to create node objects and saving them.
'''
def _create_nodes(how_many, data):
    collection = get_database()[Node.collection_name]
    ids = set()

    for i in range(how_many):
    
        node = collection.Node()
    
        node.name = data[0][i]
        node.altnames = data[1][i]
        node.plural = data[2][i]
        node.tags = data[3][i]
        
        node.start_publication = data[4][i]
        node.content =  u"Hello World"
        node.content_org = u"<b> Hello World </b>"

        node.featured = data[5][i]
      	node.comment_enabled = data[6][i]
      	node.login_required = data[7][i]

      	node.modified_by = data[8][i]				# list of Author Class id's
        node.last_update = data[9][i]

        node.member_of = u'System'
        node.created_at = data[10][i]
        node.created_by = data[11][i]
        #print node
        node.save()
        ids.add(node.pk)

    return ids


'''
	Method _read_nodes_without_ref() to read generated node objects.
	i.e. Without calling/refering name of author. Just reading stored id of author object. 
'''
def _read_nodes_without_ref(ids):
    collection = get_database()[Node.collection_name]
    node_data = []	

    for id_ in ids:

        node = collection.Node.one({'_id': ObjectId(id_)})

        node_data.append( node.name )
        node_data.append( node.altnames )
        node_data.append( node.plural )
        node_data.append( node.tags )
        
        node_data.append( node.start_publication )
        node_data.append( node.content )
        node_data.append( node.content_org )

        node_data.append( node.featured )
      	node_data.append( node.comment_enabled )
      	node_data.append( node.login_required )

      	node_data.append( node.modified_by )
        node_data.append( node.last_update )

        node_data.append( node.member_of )
        node_data.append( node.created_at )
        node_data.append( node.created_by )
    #return node_data
    
'''
	Method _read_nodes_with_ref() to read generated node objects.
	i.e. Without calling/refering name of author. Just reading stored id of author object.
'''
def _read_nodes_with_ref(ids):
    collection = get_database()[Node.collection_name]
    node_data = []	

    for id_ in ids:

        node = collection.Node.one({'_id': ObjectId(id_)})

        node_data.append( node.name )
        node_data.append( node.altnames )
        node_data.append( node.plural )
        node_data.append( node.tags )
        
        node_data.append( node.start_publication )
        node_data.append( node.content )
        node_data.append( node.content_org )

        node_data.append( node.featured )
      	node_data.append( node.comment_enabled )
      	node_data.append( node.login_required )

	for i in node.modified_by:
		author_doc = _get_document(i, get_database()[Author.collection_name] )
		node_data.append(author_doc['name'])
	
        node_data.append( node.last_update )

        node_data.append( node.member_of )
        node_data.append( node.created_at )
        author_doc = _get_document(node.created_by, get_database()[Author.collection_name] )
        node_data.append( author_doc['name'] )
    return node_data


'''
	Method _edit_nodes() to edit generated Node objects.
'''
def _edit_nodes(ids):
    collection = get_database()[Node.collection_name]
    for id_ in ids:
        node = collection.Node.one({'_id': ObjectId(id_)})
        node.name += " edited text"
        node.history.append( ObjectId(id_) )
        node.save()


'''
	Method _delete_nodes() to delete generated Node objects.
'''
def _delete_nodes(ids):
    collection = get_database()[Node.collection_name]
    for id_ in ids:
        node = collection.Node.one({'_id': ObjectId(id_)})
        node.delete()


#################### Functions Common for both Author and Node objects ########################


'''
	Method __random_creationdate() to generate random dates for node objects.
'''
def __random_creationdate():
    return datetime.datetime(random.randint(2010, 2013),
                             random.randint(1, 12),
                             random.randint(1, 28),
                             0, 0, 0).replace(tzinfo=utc)


#################### Functions for Author objects ########################


'''
	Method __random_author_name() to generate random names for author objects.
'''
def __random_author_name():
    return random.choice(
        (u'John Doe',
         u'Kedar',
         u'Avdoot',
         u"Dhiru",
         u'Sunny',
         u'San',
         u'Peter',
         u"Amit",
         u'Jonathan',
        ))


'''
	Method __create_author_nodes_PreProc() to generate data for directly inserting into author objects.
	This method aims to avoid time required for: calling function and getting random values during node creation time.
'''    
def _create_author_nodes_PreProc(how_many):
	name = []
	creationtime = []
	data = [name,creationtime]	
	for i in range(how_many):
		name.append(__random_author_name())
		creationtime.append(__random_creationdate())
	return data
	
	
'''
	_create_author_nodes() to generate Author class's objects.
'''
def _create_author_nodes(how_many,data):
    collection = get_database()[Author.collection_name]
    author_ids = set()
    for i in range(how_many):
        author = collection.Author()
        author.name = data[0][i]
        author.creationtime = data[1][i]
        author.save()
        author_ids.add(author.pk)
    return author_ids


'''
	Method _delete_author_nodes(author_ids) to delete generated Author objects.
'''
def _delete_author_nodes(author_ids):
    collection = get_database()[Author.collection_name]
    for id_ in author_ids:
        author = collection.Author.one({'_id': ObjectId(id_)})
        author.delete()


################################### AttributeType functions #################################


'''
	Method _create_attribute_type() to create AttributeType objects.
'''
def _create_attribute_type():
	collection = get_database()[AttributeType.collection_name]
	attribute_type_ids = set()
	attr_type_names = [u"country", u"capital"]
	
	for i in attr_type_names:
		attribute_type = collection.AttributeType()
		attribute_type.name = i
		attribute_type.member_of = u"attribute_type"
		
		attribute_type.data_type = "unicode"
		attribute_type.verbose_name = "Place"
		attribute_type.null = True
		attribute_type.blank = True
		attribute_type.help_text = u"helptext"
		attribute_type.max_digits = 10
		attribute_type.decimal_places = 2
		attribute_type.auto_now = True
		attribute_type.auto_now_at = True
		attribute_type.upload_to = u"url"
		attribute_type.path = u"url/name"
		attribute_type.verify_exist = True
		attribute_type.min_length = 5
		attribute_type. required = True
		attribute_type.label = u"Label"
		attribute_type.unique = True
		attribute_type.validators = []
		attribute_type.default = u"default"
		attribute_type.editable = True
		
	        attribute_type.save()
        	attribute_type_ids.add(attribute_type.pk)      
	return attribute_type_ids

	
'''
	Method _delete_attribute_type_nodes(ids) to delete generated AttributeType objects.
'''
def _delete_attribute_type_nodes():
    collection = get_database()[AttributeType.collection_name]
    collection.remove()
	

'''
	Method _create_GSystemType() to create GSystemType objects.
''' 
def _create_GSystemType():
	collection = get_database()[GSystemType.collection_name]

	at_coll = get_database()[AttributeType.collection_name]	
	#at_cur = at_coll.AttributeType.find({"name":u"country"})
	at_cur = at_coll.AttributeType.find()

	for i in at_cur:
		gsystem_type = collection.GSystemType()
		gsystem_type.name = i.name
		gsystem_type.member_of = u"GSystemType"

		#print "\n\n\t", i.name
		gsystem_type.attribute_type_set.append(i)
		
	        gsystem_type.save()
		#print gsystem_type
        
	return gsystem_type


'''
	Method _delete_gsystem_type_nodes() to delete generated GSystemType objects.
'''
def _delete_gsystem_type_nodes():
    collection = get_database()[GSystemType.collection_name]
    collection.remove()	


'''
	Method _create_GSystem() to create GSystem objects.
''' 
def _create_GSystem():
	collection = get_database()[GSystem.collection_name]

	with open('hasCapital.tsv', 'rb') as f:
		reader = csv.reader(f)
		for row in reader:
			data = row[0].split("\t")
			#To exctract country
			#print data[1]

			gsystem = collection.GSystem()
			gsystem.name = unicode(data[1],"utf-8")
			gsystem.member_of = u"GSystem"
			gsys_type_coll = get_database()[GSystemType.collection_name]
			gsys_type_cur  = gsys_type_coll.GSystemType.find()
#			gsys_type_cur  = gsys_type_coll.GSystemType.one({"name":u"country"})
			gsystem.gsystem_type = gsys_type_cur[0]._id
			gsystem.attribute_set = {u"country":unicode(data[1],"utf-8")}
#			if (len(gsystem.attribute_set) and gsystem.attribute_set.has_key(u"country") ):
#				print gsys_type_cur[0].name
			gsystem.relation_set = {"has_capital":unicode(data[2])}
			#print gsystem.attribute_set
			#print gsystem.relation_set
		        gsystem.save()
		        #print gsystem
        
	return gsystem
	

'''
	Method _delete_gsystem_nodes() to delete generated gsystem objects.
'''
def _delete_gsystem_nodes():
    collection = get_database()[GSystem.collection_name]
    collection.remove()	


'''
	Method _create_relation_type() to create RelationTypes objects.
'''
def _create_relation_type():
	collection = get_database()[RelationType.collection_name]
	relation_type_ids = set()
	
	relation_type = collection.RelationType()
	relation_type.name = u"has capital"
	relation_type.member_of = u"relation_type"
	
	relation_type.inverse_name = u"is capital of"
	relation_type.slug = "has-capital"
	relation_type.is_symmetric = False
	relation_type.is_reflexive = True
	relation_type.is_transitive = False				

	relation_type.save()
        relation_type_ids.add(relation_type.pk)      
        #print "\n", relation_type
	return relation_type_ids


'''
	Method _delete_relation_type_nodes() to delete generated AttributeType objects.
'''
def _delete_relation_type_nodes():
    collection = get_database()[RelationType.collection_name]
    collection.remove()	


'''
	Method _create_attribute() to create attribute objects.
	This object's id will be of Attribute class objects. 
'''
'''
def _create_attribute(how_many):
	collection = get_database()[Attribute.collection_name]
	at_coll = get_database()[AttributeType.collection_name]	
	at_cur = at_coll.AttributeType.find()
	
	for i in range(how_many):
		attribute = collection.Attribute()
		attribute.name = u"place"
		attribute.member_of = u"attribute"

		#To return random AttributeType object id			
		attribute.attribute_type = a_cur[random.randint(0, (a_cur.count() - 1) if (a_cur.count()) else 0 ) ]._id
		attribute.attribute_value = "jhbdfkjzbdf"		
		#print attribute
'''

'''
############## Miscellaneous ######################################################
'''

'''
	Method __get_tsvdata() to get data from external file (kept at TP_MK/gnowsys_ndf/)
'''

def __get_tsvdata():
	with open('hasCapital.tsv', 'rb') as f:
		reader = csv.reader(f)
		for row in reader:
			data = row[0].split("\t")
			#To exctract country
			print data[1]
			#To exctract capital
			#print data[2]
