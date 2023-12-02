import pymongo
from pymongo import MongoClient
from gnowsys_ndf.ndf.models import *
import os
import json
import codecs

unit_id=raw_input("Enter the unit id:")
unit_data=node_collection.find({"_id": ObjectId(unit_id)})
atts=unit_data.distinct('attribute_set.assessment_list')
l1=[]

l1=[each[1] for each in atts]
print "The following Asssessment Offred Id's for the particular unit is :",l1


def strip(ids,lfttxt,rgttxt):
    new_ids = []
    for each in ids:
        each_mod = each.split(lfttxt)
        # print each_mod
        new_ids.append((each_mod[1].rsplit(rgttxt)[0]))
    return new_ids

def createJSONFile(document):
    document_path = '{0}/{1}.json'.format(collection_path,str(document['_id']))
    print document_path
    if os.path.isfile(document_path):
        os.remove(document_path)

    with codecs.open(document_path, 'w', encoding='utf-8') as doc_file:
        if db_name != 'id':
            document = serialize_doc(document)
        json.dump(document, doc_file)
    print('Hurray!!!!!!Saved document {0}.{1}: {2}'.format(db_name,collection_name,document['_id']))

PROJECT_PATH = os.getcwd()
#print "\n",PROJECT_PATH

DLKIT_DATABASES = ['assessment', 'assessment_authoring', 'hierarchy','id', 'logging', 'relationship', 'repository']
#DLKIT_DATABASES=['assessment']
#print "\n",DLKIT_DATABASES
COLLECTIONS_TO_SKIP = ['AssessmentTaken', 'AssessmentSection', 'LogEntry']
#print "\n",COLLECTIONS_TO_SKIP
MC = MongoClient()

def serialize_date(date_object):
    return {
        'year': date_object.year,
        'month': date_object.month,
        'day': date_object.day,
        'hour': date_object.hour,
        'minute': date_object.minute,
        'second': date_object.second,
        'microsecond': date_object.microsecond
    }
def serialize_doc(doc):
    """ turn things like ObjectId into string,
        datetime into dicts

        Ignore the `id` table for these"""
    doc['_id'] = str(doc['_id'])
    #print doc['_id']
    #print doc['question']
    if 'question' in doc and doc['question'] is not None:
        doc['question']['_id'] = str(doc['question']['_id'])
        print doc['question']['_id']
    if 'answers' in doc and doc['answers'] != []:
        for answer in doc['answers']:
            answer['_id'] = str(answer['_id'])
    if 'assetContents' in doc and doc['assetContents'] != []:
        for asset_content in doc['assetContents']:
            asset_content['_id'] = str(asset_content['_id'])

    time_keys = ['creationTime', 'actualStartTime', 'completionTime',
                 'startDate', 'deadline', 'endDate']
    for time_key in time_keys:
        if time_key in doc and doc[time_key] is not None:
            doc[time_key] = serialize_date(doc[time_key])
    if 'questions' in doc and doc['questions'] is not None:
        for index, question in enumerate(doc['questions']):
            if 'responses' in question and question['responses'] is not None:
                for response in question['responses']:
                    if response is not None and 'submissionTime' in response and response['submissionTime'] is not None:
                        response['submissionTime'] = serialize_date(response['submissionTime'])
                        response['_id'] = str(response['_id'])
            doc['questions'][index]['_id'] = str(question['_id'])
    return doc


#item_list=[]
#input_txt()
for db_name in DLKIT_DATABASES:
    db = MC[db_name]
    #print "\n",db

    db_path = '{0}/{1}'.format(PROJECT_PATH,db_name)
    #print "\n",db_path
    
    if not os.path.isdir(db_path):
        os.mkdir(db_path)
    collections = db.collection_names()
    #print collections
    
    assetid_list=[]
    item_list=[]
    
    for collection_name in collections:
        if collection_name in COLLECTIONS_TO_SKIP:
            continue
            #print collection_name
        collection = MC[db_name][collection_name]
        #print collection       #print the collections of a specific database plus skip of the particular collections.
        collection_path = '{0}/{1}'.format(db_path,collection_name)
        #print collection_path   #print the collection path to be specific under a particular database e.g. assessment/AssessmentOffered
        
        if not os.path.isdir(collection_path):
            os.mkdir(collection_path)             #creating a directory of the specific collection under specific db.


print"---------------------Accessing AssessmentOffredId---------------------------------"
db_name="assessment"
collection_name="AssessmentOffered"
db_path = '{0}/{1}'.format(PROJECT_PATH,db_name)   
collection=MC['assessment'][collection_name]
collection_path = '{0}/{1}'.format(db_path,collection_name)
#print collection


l1_mod = strip(l1,'assessment.AssessmentOffered:','@ODL.MIT.EDU')
l1_mod = [ObjectId(each_id) for each_id in l1_mod]
print "\n"
print "modified AssessmentOffered ids:",l1_mod
cursor=collection.find({"_id":{"$in": l1_mod} })
print cursor.count()
b1=[]
a1=[]
ap1=[]
bp1=[]
itm=[]
asset_lst=[]
repid_lst=[]

for doc in cursor:
    #print "document:",doc
    ofd_id=doc['_id']
    print "="*20
    #print "Offred Ids:-------------",ofd_id
    # print collection
    for document in collection.find({'_id':ObjectId(ofd_id)}):
        #print document['_id']
        createJSONFile(document)

    bank_id= doc['assignedBankIds'][0]
    #print bank_id
    b1.append(bank_id)

    as_id= doc['assessmentId']
    #print as_id
    a1.append(as_id)

print "\n"    
print"---------------------Accessing Bank Id from AssessmentOffredId---------------------------------"

db_name="assessment"
collection_name="Bank"
db_path = '{0}/{1}'.format(PROJECT_PATH,db_name)   
collection=MC['assessment'][collection_name]
collection_path = '{0}/{1}'.format(db_path,collection_name)

b1_mod = strip(b1,'assessment.Bank%3A','%40ODL.MIT.EDU')
print "\n"
print "Modified bankid:",b1_mod
for bid in b1_mod:
    print "="*20
    #print "Bank Ids:-------------",bid
    for document in collection.find({'_id':ObjectId(bid)}):
        #print document['_id']
        createJSONFile(document)



print "\n"
print"-----------------------Accessing Assessment Id from AssessmentOffredId--------------------------"
#print a1
db_name="assessment"
collection_name="Assessment"
db_path = '{0}/{1}'.format(PROJECT_PATH,db_name)   
collection=MC['assessment'][collection_name]
collection_path = '{0}/{1}'.format(db_path,collection_name)

a1_mod = strip(a1,'assessment.Assessment%3A','%40ODL.MIT.EDU')
print "\n"
print "Modified assessmentid:",a1_mod
for aid in a1_mod:
    print "="*20
    #print "Assessment Ids:-----------",aid
    for document in collection.find({'_id':ObjectId(aid)}):
        #print document['_id']
        createJSONFile(document)
        t=document['childIds'][0]
        ap1.append(t)

print "\n"
print"------------------------Accessing AssessmentPart Id from AssessmentId---------------------------"
#print ap1
db_name="assessment_authoring"
collection_name="AssessmentPart"
db_path = '{0}/{1}'.format(PROJECT_PATH,db_name)   
collection=MC['assessment_authoring'][collection_name]
collection_path = '{0}/{1}'.format(db_path,collection_name)

ap1_mod = strip(ap1,'assessment_authoring.AssessmentPart%3A','%40ODL.MIT.EDU')
print "Modified assessmentid:",ap1_mod
for ap in ap1_mod:
    print "="*20
    #print "AssessmentPart Ids:-----------",ap
    for document in collection.find({'_id':ObjectId(ap)}):
        #print document['_id']
        createJSONFile(document)
        bnk_id= document['assignedBankIds'][0]
        #print bnk_id
        bp1.append(bnk_id)

        i=document['itemIds']
        #print "Item Id's :---------",i
        for iim in i:
            #print iim
            itm.append(iim)


#print itm
print "\n"
print itm
##storing itemids in id/assessmentIds
db_name="id"
collection_name="assessmentIds"
db_path = '{0}/{1}'.format(PROJECT_PATH,db_name)   
collection=MC['id'][collection_name]
collection_path = '{0}/{1}'.format(db_path,collection_name)
for each_it in itm:
    print each_it
    print "="*20
    #print "Item Ids:-------------",itn
    for document in collection.find({'_id':each_it}):
        #print document["_id"]
        createJSONFile(document)




print "\n"
print"-------------------------Access ItemIds from AssessmentPartId----------------------------------"
db_name="assessment"
collection_name="Item"
db_path = '{0}/{1}'.format(PROJECT_PATH,db_name)   
collection=MC['assessment'][collection_name]
collection_path = '{0}/{1}'.format(db_path,collection_name)
#print itm
itm_mod = strip(itm,'assessment.Item%3A','%40ODL.MIT.EDU')
print "Modified itemids:",itm_mod
for it in itm_mod:
    print "="*20
    #print "ItemIds:-----------",it
    for document in collection.find({'_id':ObjectId(it)}):
        #print document['_id']
        createJSONFile(document)
        ast_id = document.get("question", {'x': None}).get("fileIds")
        #print ast_id
        if ast_id is not None:
            for key, value in ast_id.items():
                #print key
                asset_nm=key
                asset_id=value['assetId']
                #print asset_id
                asset_lst.append(asset_id)




print "\n"
print"-------------------------Access Asset Id from ItemIds----------------------------------"
#print asset_lst
db_name="repository"
collection_name="Asset"
db_path = '{0}/{1}'.format(PROJECT_PATH,db_name)   
collection=MC['repository'][collection_name]
collection_path = '{0}/{1}'.format(db_path,collection_name)

asst1_mod = strip(asset_lst,'repository.Asset%3A','%40ODL.MIT.EDU')
print "Modified Assetids:",asst1_mod
for asst in asst1_mod:
    print "="*20
    #print "AssetIds:-----------",asst
    for document in collection.find({'_id':ObjectId(asst)}):
        #print document['_id']
        createJSONFile(document)

        rep_id=document['assignedRepositoryIds'][0]
        #print rep_id
        repid_lst.append(rep_id)




print "\n"
print "------------------------------------Access Repository Ids from Asset Ids---------------------"
#print repid_lst
collection_name="Repository"
db_path = '{0}/{1}'.format(PROJECT_PATH,db_name)   
collection=MC['repository'][collection_name]
collection_path = '{0}/{1}'.format(db_path,collection_name)

rep1_mod = strip(repid_lst,'repository.Repository%3A','%40ODL.MIT.EDU')
print "Modified Repositoryids:",rep1_mod
for rep in rep1_mod:
    print "="*20
    #print "Assigned RepositoryIds:-----------",rep
    for document in collection.find({'_id':ObjectId(rep)}):
        #print document['_id']
        createJSONFile(document)


print "\n"
print"-------------------------Access Bank Id from AssessmentPartId----------------------------------"
#print bp1
db_name="assessment_authoring"
collection_name="Bank"
db_path = '{0}/{1}'.format(PROJECT_PATH,db_name)   
collection=MC['assessment_authoring'][collection_name]
collection_path = '{0}/{1}'.format(db_path,collection_name)

bp1_mod = strip(bp1,'assessment.Bank%3A','%40ODL.MIT.EDU')
print "Modified Assessment_authoring bankids:",ap1_mod
for bp in bp1_mod:
    print "="*20
    #print "BankIds:-----------",bp
    for document in collection.find({'_id':ObjectId(bp)}):
        #print document['_id']
        createJSONFile(document)

#-----------------------------------Ids------------------------
##storing bankids in id/assessmentIds
db_name="id"
collection_name="assessmentIds"
db_path = '{0}/{1}'.format(PROJECT_PATH,db_name)   
collection=MC['id'][collection_name]
collection_path = '{0}/{1}'.format(db_path,collection_name)
for bn in b1:
    #print bn
    print "="*20
    print "Bank Ids:-------------",bn
    for document in collection.find({'_id':bn}):
        #print document['_id']
        createJSONFile(document)


print repid_lst
##storing repids in id/repositoryIds
collection_name="repositoryIds"
db_path = '{0}/{1}'.format(PROJECT_PATH,db_name)   
collection=MC['id'][collection_name]
collection_path = '{0}/{1}'.format(db_path,collection_name)
for rp in repid_lst:
    #print rp
    print "="*20
    print "Repository Ids:-------------",rp
    for document in collection.find({'_id' : rp}):
        #print document["_id"]
        createJSONFile(document)

