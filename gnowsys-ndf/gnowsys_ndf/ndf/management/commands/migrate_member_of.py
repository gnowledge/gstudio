''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node, GSystemType

####################################################################################################################

class Command(BaseCommand):
    """To replace gsystem_type by member_of field and drop gsystem_type field, perform following steps:
    
    (1) Make sure following fields (with given data-types, if doesn't so make the necessary changes) exists in models.py file as it is:
        (a) 'member_of' : [ObjectId]
        (b) 'gsystem_type' : [ObjectId]     -- NOTE: Must exist (under "GSystem" class) before going ahead!!
      
    (2) Perform the following command:
        - python manage.py migrate_member_of
      
        - NOTE: This command replaces the occurences of member_of field having data stored as [unicode] by [ObjectId] (values copied from gsystem_type field) in exsisting documents in the database; and also removes gsystem_type field from the corresponding documents. Exception to this, for documents having values GSystemType/AttributeType/RelationType for '_type' field, member_of field is kept empty (i.e. empty list []) as there is no MetaType defined for these types!
  
    (3) IMPORTANT: Remove the following field explicitly from models.py:
        - 'gsystem_type': [ObjectId]
        - Otherwise, it is going to cause a major problem!!!
    """

    help = "\tThis is a migration script that reassigns 'member_of' field of each document \n\twith list of embedded documents of GSystemType " \
           "to which the document belongs."

    def handle(self, *args, **options):
        db = get_database()
        collection = db[Node.collection_name]

        # [A] Get the " GSystemType/AttributeType/RelationType " nodes (for whom 'gsystem_type' field doesn't exist)
        cur_ty_mo = collection.Node.find({'_type': {'$in': ['GSystemType', 'AttributeType', 'RelationType']}})

        # Listing the nodes
        for n in cur_ty_mo:
            # Replace 'member_of' field with ObjectId of MetaType to which that document belongs
            # - But right now we don't have such MetaType documents
            # - Currently going to keep 'member_of' field... EMPTY!

            n.member_of = []
            n.save()

        # ===================================================================================================================================


        # [B] Get the " GSystem/File/Group " nodes for whom 'member_of' and 'gsystem_type' fields exist
        cur_nc_mo = collection.Node.find({'member_of': {'$exists': True}, 'gsystem_type': {'$exists': True}})

        # Listing the nodes
        for n in cur_nc_mo:

            # Replace 'member_of' field with ObjectId of GSystemType to which that document belongs

            if not n.gsystem_type:
                # If 'gsystem_type' field is EMPTY
                #   - Special case: Exists with 'Group' documents, they consists of value only for 'member_of' field (not for 'gsystem_type' field)
                #   - In this case, 'member_of' field is a list that consists of name of the GSystemType (i.e. 'Group')
                #   - So extract this value first from 'member_of' field, then assign/override 'member_of' field with an empty list.
                #   - For extracted value (i.e. name of the GSystemType), fetch it's documents ObjectId from database; and append this ObjectId to the 'member_of' field

                gsystem_name_list = n.member_of
                n.member_of = []

                # Iterate name list
                for name in gsystem_name_list:
                    gsystem_node = collection.Node.one({'_type': 'GSystemType', 'name': name})
                    n.member_of.append(gsystem_node._id)

            else:
                # Else 'gsystem_type' field is NOT empty
                #   - This field contains list of ObjectIds' of GSystemType to which the document belongs
                #   - Assign/Override 'member_of' field with an empty list
                #   - Append these ObjectIds to the 'member_of' field

                gsystem_oid_list = n.gsystem_type
                n.member_of = []

                n.member_of = gsystem_oid_list

            n.save()

        # Remove 'gsystem_type' field from already existing documents where ever it exists!
        collection.update({'gsystem_type': {'$exists': True}}, {'$unset': {'gsystem_type': ""}}, multi=True)

        # --- End of handle() ---

