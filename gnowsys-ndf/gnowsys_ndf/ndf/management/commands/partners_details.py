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
from gnowsys_ndf.ndf.views.group import create_group
import csv
from collections import defaultdict
from gnowsys_ndf.ndf.management.commands.nroer_data_entry import get_user_id, create_user_nroer_team
####################################################################################################################
''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.views.methods import create_gattribute
from gnowsys_ndf.settings import GAPPS       

db=get_database()
collection =db[Node.collection_name]
schema_file_csv = os.path.join( os.path.dirname(__file__), "schema_files/partners_details.csv")
house_street_AT = node_collection.one({'$and':[{'name':'house_street'},{'_type':'AttributeType'}]})
town_city_AT = node_collection.one({'$and':[{'name':'town_city'},{'_type':'AttributeType'}]})
contact_point_AT = node_collection.one({'$and':[{'name':'contact_point'},{'_type':'AttributeType'}]})
state_AT = node_collection.one({'$and':[{'name':'state'},{'_type':'AttributeType'}]})
pin_code_AT = node_collection.one({'$and':[{'name':'pin_code'},{'_type':'AttributeType'}]})
email_id_AT = node_collection.one({'$and':[{'name':'email_id'},{'_type':'AttributeType'}]})
telephone_AT = node_collection.one({'$and':[{'name':'telephone'},{'_type':'AttributeType'}]})
website_AT = node_collection.one({'$and':[{'name':'website'},{'_type':'AttributeType'}]})
gst_group = node_collection.one({"_type": "GSystemType", 'name': GAPPS[2]})

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
      check_group = node_collection.one({'name': str(each['category']), '_type' : 'Group'})
      check_sub_group = node_collection.one({'name': str(each['name']), '_type' : 'Group'})

      if not check_group:
          group_create(each['category'])
      if not check_sub_group:
          group_create(each['name'])
              
      get_parent_group = node_collection.one({'name': str(each['category']), '_type' : 'Group'})
      get_child_group = node_collection.one({'name': str(each['name']), '_type' : 'Group'})
      if get_child_group._id not in get_parent_group.collection_set:
        get_parent_group.collection_set.append(get_child_group._id)
        get_parent_group.save()
      if get_child_group._id not in get_parent_group.post_node:
        get_parent_group.post_node.append(get_child_group._id)
        get_parent_group.save()
      get_group = node_collection.one({'name': str(each['name']), '_type' : 'Group'})
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

def group_create(group_name):
          create_user_nroer_team()

          group_id=group_name 
          ins_objectid  = ObjectId()
          if ins_objectid.is_valid(group_id) is False :
            group_ins = node_collection.find_one({'_type': "Group","name": group_id}) 
            auth = node_collection.one({'_type': 'Author', 'name': u'nroer_team' }) 
            if group_ins:
              group_id = str(group_ins._id)
            else :
              auth = node_collection.one({'_type': 'Author', 'name': u'nroer_team'})
              if auth :
                group_id = str(auth._id)	
          else :
            pass

          colg = node_collection.collection.Group()
          Mod_colg = node_collection.collection.Group()

          cname=group_name.strip()
          colg.altnames=unicode(cname)
          colg.name = unicode(cname)
          colg.member_of.append(gst_group._id)
          usrid = get_user_id("nroer_team")
          
          colg.created_by = usrid
          if usrid not in colg.author_set:
            colg.author_set.append(usrid)

          colg.modified_by = usrid
          if usrid not in colg.contributors:
            colg.contributors.append(usrid)

          colg.group_type = "PUBLIC"        
          colg.edit_policy = "EDITABLE_NON_MODERATED"
          colg.subscription_policy = "OPEN"
          colg.agency_type="Partner"
          colg.save()
    




