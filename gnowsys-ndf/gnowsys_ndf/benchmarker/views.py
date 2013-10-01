import datetime
import csv

from cStringIO import StringIO
from time import time, sleep

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.timezone import utc
from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from gnowsys_ndf.ndf.models import *

import random

'''
    The First method to get called.
'''
def run(request):
    
    '''
            data_cleanup() cleans the data in mongodb database.
    '''
    #data_cleanup()


    how_many = int(request.GET.get('how_many', 10))

    TESTS = ((
            'mongokit', 
            _create_author_nodes, _create_attribute_type, _create_GSystemType, _create_relation_type, _create_GSystem,
            _read_author_nodes, _read_attribute_type, _read_GSystemType, _read_relation_type, _read_GSystem,
            _update_author_nodes, _update_attribute_type, _update_GSystemType, _update_relation_type, _update_GSystem,
            _delete_author_nodes, _delete_attribute_type, _delete_GSystemType, _delete_relation_type, _delete_GSystem,
            settings.DATABASES['mongodb']['ENGINE']
            ),)

    response = StringIO()

    total = 0.0
    print >>response, "\n\tBENCHMARKING TEST : mongokit and mongodb engine"    
    print >>response,   "\t===============================================\n"    
    
    print >>response, "(C):CREATE >> creation of objects\n"        

    # 1 . Calling method _create_author_nodes(how_many,data)       
    
    data = _create_author_nodes_PreProc(how_many)
    t0=time()
    author_ids = _create_author_nodes(how_many,data)
    t1=time()
    total += t1-t0
    print >>response, "\t Creating", how_many, "Author objects took", t1-t0, "seconds"
		
    # give it a rest so that the database can  index all the IDs
    sleep(1)
    
    # 2 . Calling method _create_attribute_type()       
    t0=time()
    attribute_type_ids = _create_attribute_type()
    t1=time()
    total += t1-t0
    print >>response, "\t Creating 2 AttributeType (country and capital) objects took", t1-t0, "seconds"
    sleep(1)
    
    # 3 . Calling method _create_GSystemType()       
    t0=time()
    GSystemType_ids = _create_GSystemType()
    t1=time()
    total += t1-t0
    print >>response, "\t Creating 1 GSystemType places objects took", t1-t0, "seconds"
    
    sleep(1)

    # 4 . Calling method _create_relation_type()        
    t0=time()
    relation_type_ids = _create_relation_type()
    t1=time()
    total += t1-t0
    print >>response, "\t Creating 2 RelationType objects took", t1-t0, "seconds"
    
    sleep(1)
    
    # 5 . Calling method _create_GSystem(data,how_many)       
    data = _create_GSystem_PreProc(how_many)
    t0=time()
    GSystem_ids = _create_GSystem(data,how_many)
    t1=time()
    total += t1-t0
    print >>response, "\t Creating", how_many * 2, "GSystem objects (10 of each country and capital) took", t1-t0, "seconds"

    sleep(1)
    
    print >>response, "\n(R):READ >> reading of objects\n"        
    
    # 6 . Calling method _read_author_nodes(author_ids)       
    
    t0=time()
    _read_author_nodes(author_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Reading", how_many, "Author objects took", t1-t0, "seconds"

    sleep(1)
    
    # 7 . Calling method _read_attribute_type(attribute_type_ids)       
    t0=time()
    _read_attribute_type(attribute_type_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Reading 2 AttributeType (country and capital) objects took", t1-t0, "seconds"
    sleep(1)
    
    # 8 . Calling method _read_GSystemType(GSystemType_ids)        
    t0=time()
    _read_GSystemType(GSystemType_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Reading 1 GSystemType places objects took", t1-t0, "seconds"
    
    sleep(1)
    
    # 9 . Calling method _read_relation_type(relation_type_ids)        
    t0=time()
    _read_relation_type(relation_type_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Reading 2 RelationType objects took", t1-t0, "seconds"

    sleep(1)

    # 10 . Calling method _read_GSystem(GSystem_ids)       
    t0=time()
    _read_GSystem(GSystem_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Reading", how_many * 2, "GSystem objects took", t1-t0, "seconds"

    sleep(1)

    print >>response, "\n(U):UPDATE >> updating of objects\n"        
    
    # 11 . Calling method _update_author_nodes(author_ids)       
    
    t0=time()
    _update_author_nodes(author_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Updating", how_many, "Author objects took", t1-t0, "seconds"
    
    sleep(1)
    
    # 12 . Calling method _update_attribute_type(attribute_type_ids)       
    t0=time()
    _update_attribute_type(attribute_type_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Updating 2 AttributeType (country and capital) objects took", t1-t0, "seconds"
    sleep(1)
    
    # 13 . Calling method _update_GSystemType(GSystemType_ids)       
    t0=time()
    _update_GSystemType(GSystemType_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Updating 1 GSystemType places objects took", t1-t0, "seconds"
    
    sleep(1)
    
    # 14 . Calling method _update_relation_type(relation_type_ids)        
    t0=time()
    _update_relation_type(relation_type_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Updating 2 RelationType objects took", t1-t0, "seconds"

    sleep(1)
    
    # 15 . Calling method _update_GSystem(GSystem_ids)       
    t0=time()
    _update_GSystem(GSystem_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Updating", how_many * 2, "GSystem objects took", t1-t0, "seconds"
    
    sleep(1)
    
    print >>response, "\n(D):DELETE >> deletion of objects:\n"        
    
    # 16 . Calling method _delete_relation_type(relation_type_ids)       
    t0=time()
    _delete_relation_type(relation_type_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Deleting 2 RelationType objects took", t1-t0, "seconds"
    
    sleep(1)
    
    # 17 . Calling method _delete_GSystem(GSystem_ids)       
    
    t0=time()
    _delete_GSystem(GSystem_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Deleting", how_many * 2, " GSystem objects took", t1-t0, "seconds"

    sleep(1)
    
    # 18 . Calling method _delete_GSystemType(GSystemType_ids)       
    
    t0=time()
    _delete_GSystemType(GSystemType_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Deleting 1 GSystemType places object took", t1-t0, "seconds"

    sleep(1)
    
    # 19 . Calling method _delete_author_nodes(author_ids)       
    
    t0=time()
    _delete_author_nodes(author_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Deleting", how_many, " Author node objects took", t1-t0, "seconds"
    
    sleep(1)
    
    # 20 . Calling method _delete_attribute_type(attribute_type_ids)       
    
    t0=time()
    _delete_attribute_type(attribute_type_ids)
    t1=time()
    total += t1-t0
    print >>response, "\t Deleting 2 AttributeType objects took", t1-t0, "seconds"
    
    sleep(1)
    
    #Print final result.
    print >>response, "\n\n -------------------------------------------------------------------"	
    print >>response, "\n FINAL RESULT : TOTAL TIME REQUIRED IS", total, "seconds"
                
    return HttpResponse(response.getvalue(), mimetype='text/plain')                
    #End of run()
    
#####################################################################################################


'''
Method __random_creationdate() to generate random dates for node objects.
'''
def __random_creationdate():
    return datetime.datetime(random.randint(2010, 2013),
                             random.randint(1, 12),
                             random.randint(1, 28),
                             0, 0, 0).replace(tzinfo=utc)


'''
	Method __get_bool_value() to randomly generate bool values.
'''
def __get_bool_value():
	r = random.randint(0,9)
	return True if (r % 2 == 0) else False


'''
	Method __random_name() to generate random names. 
'''
def __random_name():
    return random.choice(
        (u'nagarjun',
         u'dhiru',
         u'kedar',
         u"avdoot",
         u'sunny',
         u'joel',
         u'krishna',
         u"anil",
         u'rupesh',
        ))


'''
	Method __random_tags() to generate tags for node objects.
'''
def __random_tags():
    tags = [u'one', u'two', u'three', u'four', u'five', u'six',
            u'seven', u'eight', u'nine', u'ten']
    random.shuffle(tags)
    return tags[:random.randint(0, 3)]

#------------------------------------------------------------------------------------------------------------    

'''
	Method __create_author_nodes_PreProc() to generate data for directly inserting into author objects.
	This method aims to avoid time required for: calling function and getting random values during node creation time.
'''    
def _create_author_nodes_PreProc(how_many):
    username = password = email = first_name = last_name = address = []
    created_at = last_login = []
    phone = []
    is_active = is_staff = is_superuser = []
    data = [username, password, email, first_name, last_name, address, phone, is_active, is_staff, is_superuser,  created_at, last_login]	
    for i in range(how_many):
        username.append(__random_name())
        password.append(__random_name())
        email.append(u"abc@domainname.com")
        first_name.append(__random_name())
        last_name.append(__random_name())
        address.append(u"mumbai, maharashtra")
        phone.append(9876543212L)
        is_active.append(__get_bool_value())
        is_staff.append(__get_bool_value())
        is_superuser.append(__get_bool_value())
        created_at.append(__random_creationdate())
        last_login.append(__random_creationdate())
    return data


'''
	_create_author_nodes() to generate Author class's objects.
'''
def _create_author_nodes(how_many,data):
    collection = get_database()[Author.collection_name]
    author_ids = set()
    for i in range(how_many):
    	author = collection.Author()

    	author.username = data[0][i]
    	author.password = data[1][i]
    	author.email = data[2][i]
    	author.first_name = data[3][i]
    	author.last_name = data[4][i]
    	author.address = data[5][i]
    	author.phone = data[6][i]
    	author.is_active = data[7][i]
    	author.is_staff = data[8][i]
    	author.is_superuser = data[9][i]
    	author.created_at = data[10][i]
    	author.last_login = data[11][i]

    	author.save()
    	author_ids.add(author.pk)
    return author_ids
    

'''
        Method _read_author_nodes() to read author objects.
'''
def _read_author_nodes(author_ids):
    collection = get_database()[Author.collection_name]
    for id_ in author_ids:
        author = collection.Author.one({'_id': ObjectId(id_)})

    	author.username
    	author.password
    	author.email
    	author.first_name
    	author.last_name
        author.address
    	author.phone
    	author.is_active
    	author.is_staff
    	author.is_superuser
    	author.created_at
    	author.last_login

'''
        Method _update_author_nodes() to update author objects.
'''
def _update_author_nodes(author_ids):
    collection = get_database()[Author.collection_name]
    for id_ in author_ids:
        collection.update({'_id': ObjectId(id_)}, 
                          {'$set': {'username': u'edited_text', 
                                    'password': u'edit12%',
                                    'email': u'jkdsg@kdhj.com',
                                    'first_name':'uyhskk',
                                    'last_name':'ksdbmplp',
                                    'phone':'4568965874L',
                                    'is_active':'true',
                                    'is_staff':'false',
                                    'is_superuser':'false',
                                    'created_at':'datetime.datetime(2013, 9, 20, 14, 13, 44, 304360)',
                                    'last_login':'datetime.datetime(2013, 9, 20, 14, 13, 44, 304360)'}
                          }, 
                          upsert=False, multi=True)


'''
	Method _delete_author_nodes(author_ids) to delete generated Author objects.
'''
def _delete_author_nodes(author_ids):
    collection = get_database()[Author.collection_name]
    for id_ in author_ids:
        author = collection.Author.one({'_id': ObjectId(id_)})
        author.delete()


#------------------------------------------------------------------------------------------------------


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
        attribute_type.required = True
        attribute_type.label = u"Label"
        attribute_type.unique = True
        attribute_type.validators = []
        attribute_type.default = u"default"
        attribute_type.editable = True
		
        attribute_type.save()
        attribute_type_ids.add(attribute_type.pk)
      
    return attribute_type_ids


'''
        Method read_attribute_type() to read AttributeType objects.
'''
def _read_attribute_type(attribute_type_ids):
    collection = get_database()[AttributeType.collection_name]
    for id_ in attribute_type_ids:
        attribute_type = collection.AttributeType.one({'_id': ObjectId(id_)})

    	attribute_type.name
        attribute_type.member_of
		
        attribute_type.data_type
        attribute_type.verbose_name
        attribute_type.null
        attribute_type.blank
        attribute_type.help_text
        attribute_type.max_digits
        attribute_type.decimal_places
        attribute_type.auto_now
        attribute_type.auto_now_at
        attribute_type.upload_to
        attribute_type.path
        attribute_type.verify_exist
        attribute_type.min_length
        attribute_type.required
        attribute_type.label
        attribute_type.unique
        attribute_type.validators
        attribute_type.default
        attribute_type.editable
	

'''
        Method _update_attribute_type() to update AttributeType objects.
'''
def _update_attribute_type(attribute_type_ids):
    collection = get_database()[AttributeType.collection_name]
    for id_ in attribute_type_ids:
        collection.update({'_id': ObjectId(id_)}, 
                          {'$set': {'name': u"edited_text",
                                    'data_type':'bool',
                                    'verbose_name':'mnbdvf',
                                    'null':'false',
                                    'blank':'false',
                                    'help_text': u'help ... ,jkjkuh',
                                    'max_digits': '15',
                                    'decimal_places': '2',
                                    'auto_now':'true',
                                    'auto_now_at':'false',
                                    'upload_to':u'url.....',
                                    'path':u'url.......',
                                    'verify_exist': 'true',
                                    'min_length': '10',
                                    'required': 'true',
                                    'label': u'label text',
                                    'unique': 'false',
                                    'validators':'[is_blank, valid, is_email]',
                                    'default': u'this is default',
                                    'editable': 'false'}
                           }, 
                          upsert=False, multi=True)


'''
	Method _delete_attribute_type(ids) to delete generated AttributeType objects.
'''
def _delete_attribute_type(attribute_type_ids):
    collection = get_database()[AttributeType.collection_name]
    for id_ in attribute_type_ids:
        at = collection.AttributeType.one({'_id': ObjectId(id_)})
        at.delete()


#------------------------------------------------------------------------------------------------------


'''
	Method _create_GSystemType() to create GSystemType objects.
''' 
def _create_GSystemType():
    collection = get_database()[GSystemType.collection_name]

    GSystemType_ids = set()    

    at_coll = get_database()[AttributeType.collection_name]	
    at_cur = at_coll.AttributeType.find()

    gsystem_type = collection.GSystemType()
    gsystem_type.name = u"places"
    gsystem_type.member_of = u"GSystemType"

    for i in at_cur:
        gsystem_type.attribute_type_set.append(i)

    gsystem_type.save()
    GSystemType_ids.add(gsystem_type.pk)

    return GSystemType_ids


'''
        Method read_GSystemType() to read GSystemType objects.
'''
def _read_GSystemType(GSystemType_ids):
    collection = get_database()[GSystemType.collection_name]
    for id_ in GSystemType_ids:
        gsystem_type = collection.GSystemType.one({'_id': ObjectId(id_)})

    	gsystem_type.name
        gsystem_type.member_of
        gsystem_type.attribute_type_set
		

'''
        Method _update_GSystemType() to update GSystemType objects.
'''
def _update_GSystemType(GSystemType_ids):
    collection = get_database()[GSystemType.collection_name]
    for id_ in GSystemType_ids:
        collection.update({'_id': ObjectId(id_)}, {'$set': {'name': u"edited_text"}}, upsert=False, multi=True)


'''
        Method _delete_gsystem_type_nodes() to delete generated GSystemType objects.
'''
def _delete_GSystemType(GSystemType_ids):
    collection = get_database()[GSystemType.collection_name]
    for id_ in GSystemType_ids:
        gst = collection.GSystemType.one({'_id': ObjectId(id_)})
        gst.delete()        


#------------------------------------------------------------------------------------------------------


'''
	Method _create_relation_type() to create RelationTypes objects.
'''
def _create_relation_type():
    collection = get_database()[RelationType.collection_name]
    gstype_coll = get_database()[GSystemType.collection_name]
    relation_type_ids = set()
    
    relation_type = collection.RelationType()
    relation_type.name = u"has_capital"
    relation_type.member_of = u"relation_type"
    
    relation_type.inverse_name = u"is_capital_of"
    relation_type.slug = "has_capital"
    
    relation_type.subject_type = [gstype_coll.GSystemType.one({"name":"places"})._id]
    relation_type.object_type = [gstype_coll.GSystemType.one({"name":"places"})._id]
    
    relation_type.is_symmetric = True
    relation_type.is_reflexive = True
    relation_type.is_transitive = True				
    
    relation_type.save()
    relation_type_ids.add(relation_type.pk)      
    
    #Automatic creation of reverse RelationType from above RelationType object
    relation_type = collection.RelationType()

    relation_type.name = u"is_capital_of"
    relation_type.member_of = u"relation_type"
    
    relation_type.inverse_name = u"has_capital"
    relation_type.slug = "is_capital_of"

    relation_type.subject_type = [gstype_coll.GSystemType.one({"name":"places"})._id]
    relation_type.object_type = [gstype_coll.GSystemType.one({"name":"places"})._id]

    relation_type.is_symmetric = True
    relation_type.is_reflexive = True
    relation_type.is_transitive = True				

    relation_type.save()
    relation_type_ids.add(relation_type.pk)      

    return relation_type_ids


'''
        Method _read_relation_type() to read RelationType objects.
'''
def _read_relation_type(relation_type_ids):
    collection = get_database()[RelationType.collection_name]
    for id_ in relation_type_ids:
        relation_type = collection.RelationType.one({'_id': ObjectId(id_)})

    	relation_type.name
        relation_type.member_of

        relation_type.inverse_name
        relation_type.slug
        relation_type.subject_type
        relation_type.object_type
        relation_type.is_symmetric
        relation_type.is_reflexive
        relation_type.is_transitive
	

'''
        Method _update_relation_type() to read AttributeType objects.
'''
def _update_relation_type(relation_type_ids):
    collection = get_database()[RelationType.collection_name]
    for id_ in relation_type_ids:
        collection.update({'_id': ObjectId(id_)},
                          {'$set': {'name': u'edited_text',
                                    'inverse_name': u'xkmjdkgkl',
                                    'slug':'slug-string',
                                    'is_symmetric':'false',
                                    'is_reflexive':'false',
                                    'is_transitive':'false'}
                           }, 
                          upsert=False, multi=True)


'''
	Method _delete_relation_type_nodes() to delete generated AttributeType objects.
'''
def _delete_relation_type(relation_type_ids):
    collection = get_database()[RelationType.collection_name]
    for id_ in relation_type_ids:
        rt = collection.RelationType.one({'_id': ObjectId(id_)})
        rt.delete()


#------------------------------------------------------------------------------------------------------


'''
	Method _create_GSystem_PreProc() to create GSystem objects.
'''
def _create_GSystem_PreProc(how_many):
    country = capital = []
    cnt = 0
    data = [country, capital]
    with open('hasCapital.tsv', 'rb') as f:
        reader = csv.reader(f)
        
        for row in reader:
            d = row[0].split("\t")
	    #To exctract country
            #print d[1]
            country.append(d[1])
            capital.append(d[2])
            cnt+=1
            if (cnt==how_many):
                break
    return data           


'''
	Method _create_GSystem() to create GSystem objects.
''' 
def _create_GSystem(data,how_many):
    collection = get_database()[GSystem.collection_name]  
    GSystem_ids = set()

    gsys_type_coll = get_database()[GSystemType.collection_name]
    gsys_type_cur  = gsys_type_coll.GSystemType.find()

    rel_type_coll = get_database()[RelationType.collection_name]
    at_type_coll = get_database()[AttributeType.collection_name]

    for i in range (how_many):
        #To create GSystemType of capital
        gsystem = collection.GSystem()
        
        gsystem.name = unicode(data[1][i],"utf-8")
        gsystem.member_of = u"GSystem"
        
        gsystem.gsystem_type = gsys_type_cur[0]._id
        
        at_type_name =  at_type_coll.AttributeType.one({"name":"capital"}).name
        gsystem.attribute_set = [{unicode(at_type_name):unicode(data[1][i],"utf-8")}]

        rel_type_name = rel_type_coll.RelationType.one({"name":"is_capital_of"}).name
        gsystem.relation_set =[{unicode(rel_type_name):unicode(data[0][i])}]
        
        gsystem.collection_set = []
        gsystem.save()

        GSystem_ids.add(gsystem.pk)

        #To create GSystemType of country        
        gsystem = collection.GSystem()
        
        gsystem.name = unicode(data[0][i],"utf-8")
        gsystem.member_of = u"GSystem"
        
        gsystem.gsystem_type = gsys_type_cur[0]._id

        at_type_name =  at_type_coll.AttributeType.one({"name":"country"}).name
        gsystem.attribute_set = [{unicode(at_type_name):unicode(data[0][i],"utf-8")}]

        rel_type_name = rel_type_coll.RelationType.one({"name":"has_capital"}).name
        gsystem.relation_set =[{rel_type_name:unicode(data[1][i])}]

        gsystem.collection_set = []
        gsystem.save()

        GSystem_ids.add(gsystem.pk)
    return GSystem_ids



'''
        Method read_GSystem() to read GSystem objects.
'''
def _read_GSystem(GSystem_ids):
    collection = get_database()[GSystem.collection_name]
    gstype_coll = get_database()[GSystemType.collection_name]
    for id_ in GSystem_ids:
        gsystem = collection.GSystem.one({'_id': ObjectId(id_)})

    	gsystem.name
        gsystem.member_of

        gstype_coll.GSystemType.one({'_id':gsystem.gsystem_type})
        gsystem.attribute_set
        gsystem.relation_set
        gsystem.collection_set
	

'''
        Method _update_GSystem() to update GSystem objects.
'''
def _update_GSystem(GSystem_ids):
    collection = get_database()[GSystem.collection_name]
    for id_ in GSystem_ids:
        collection.update({'_id': ObjectId(id_)}, 
                          {'$set': {'name': u'edited_text',
                                    'gsystem_type': u'52495d205a40920ab18ed028',
                                    'relation_set': "{u'has_capital': u'Alberta'}",
                                    'attribute_set': ''}
                           }, 
                          upsert=False, multi=True)


'''
         Method _delete_GSystem() to delete generated gsystem objects.
'''
def _delete_GSystem(GSystem_ids):
    collection = get_database()[GSystem.collection_name]
    for id_ in GSystem_ids:
        gs = collection.GSystem.one({'_id': ObjectId(id_)})
        gs.delete()


#------------------------------------------------------------------------------------------------------


'''
        Method data_cleanup() is to remove data in mongodb database.
'''
def data_cleanup():
    collection = get_database()[Author.collection_name]
    collection.remove()	

    collection = get_database()[AttributeType.collection_name]
    collection.remove()	

    collection = get_database()[GSystemType.collection_name]
    collection.remove()	

    collection = get_database()[GSystem.collection_name]
    collection.remove()	

    collection = get_database()[RelationType.collection_name]
    collection.remove()	
