''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database
from mongokit import IS

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *
import csv
from collections import defaultdict

####################################################################################################################
''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.views.methods import create_gattribute

db=get_database()
collection =db['Nodes']
schema_file_csv = os.path.join( os.path.dirname(__file__), "schema_files/partners_details.csv")
house_street_AT = collection.Node.one({'$and':[{'name':'house_street'},{'_type':'AttributeType'}]})
town_city_AT = collection.Node.one({'$and':[{'name':'town_city'},{'_type':'AttributeType'}]})
contact_point_AT = collection.Node.one({'$and':[{'name':'contact_point'},{'_type':'AttributeType'}]})
state_AT = collection.Node.one({'$and':[{'name':'state'},{'_type':'AttributeType'}]})
pin_code_AT = collection.Node.one({'$and':[{'name':'pin_code'},{'_type':'AttributeType'}]})
email_id_AT = collection.Node.one({'$and':[{'name':'email_id'},{'_type':'AttributeType'}]})
telephone_AT = collection.Node.one({'$and':[{'name':'telephone'},{'_type':'AttributeType'}]})
website_AT = collection.Node.one({'$and':[{'name':'website'},{'_type':'AttributeType'}]})

class Command(BaseCommand):
    help = "Adding Parterns details "

    def handle(self, *args, **options):
      main()

def main():
  grp_dict={}
  columns = defaultdict(list)

  with open(schema_file_csv, 'rb') as f:
    reader = csv.DictReader(f, delimiter=",")
    file_content=[]
    for row in reader:
      file_content.append(row)
    for each in file_content:

      get_group = collection.Node.one({'name': str(each['name']), '_type' : 'Group'})
      get_group.content = unicode(each['description'])
      get_group.content = unicode(each['description'])
      get_group.save()
      create_gattribute(get_group._id, email_id_AT, unicode(each['email']))  
      create_gattribute(get_group._id, house_street_AT, unicode(each['address: Street']))  
      create_gattribute(get_group._id, town_city_AT, unicode(each['address: Place']))  
      create_gattribute(get_group._id, state_AT, unicode(each['address: State']))
      if each['address: PIN']:
        create_gattribute(get_group._id, pin_code_AT, long(each['address: PIN']))
      create_gattribute(get_group._id, contact_point_AT, unicode(each['contactPoint']))  
      create_gattribute(get_group._id, telephone_AT, unicode(each['telephone']))  
      create_gattribute(get_group._id, website_AT, unicode(each['website']))  
    
    print ("\n Partners details added!\n\n")





