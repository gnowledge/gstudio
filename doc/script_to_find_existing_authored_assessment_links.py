#script to find the existing authored assessments based on a given Assessment_Offered Id as input.
import pymongo
import pprint
from pymongo import MongoClient
from gnowsys_ndf.ndf.models import *

client = MongoClient('localhost', 27017)
db = client['assessment']
#print db
#print client
collection = db['AssessmentOffered']
#print collection

print "General Instructions for authoring: Open the existing assessment activity that u want to modify"
print "check the iframe source and copy the Assessment Offered Id  that lies in between %3A <Assessment_Offered Id> %40ODL.MIT.EDU"
print "\n"

Offrd_id=raw_input("Enter the Assessment_Offered Id:")
print "Please verify the Assessment_Offered_Id you entered:",Offrd_id

# sample authoring link: auth_link='https://assessments-clix.tiss.edu/#/banks/assessment.Bank%3A58bd924b91d0d90b7ee4aa8e%40ODL.MIT.EDU/assessments/assessment.Assessment%3A58be5f0591d0d91c07bbb6f2%40ODL.MIT.EDU/'

ofd_data=collection.find_one({"_id": ObjectId(Offrd_id)},{'_id':0,'assessmentId':1})
#print ofd_data['assessmentId']

bank_id=collection.find_one({"_id":ObjectId(Offrd_id)},{'_id':0,'assignedBankIds':1})
bnk_id= bank_id['assignedBankIds']
#print bnk_id[0]
print"="*90
auth_link='https://assessments-clix.tiss.edu/#/banks/'+bnk_id[0]+'/assessments/'+ofd_data['assessmentId']+'/'
print "\n"	
print "Click on this authoring link to edit the existing assessment:-",auth_link
print "\n"
print "Note:- Click on the authoring link above to edit the assessment, first click on unpublish, edit the assessment, then click on publish and recheckwhether the assessments modification getting reflected."





