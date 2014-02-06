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
    help = "\tThis is a migration script that reassigns 'member_of' field of each document \n\twith list of embedded documents of GSystemType " \
           "to which the document belongs."

    def handle(self, *args, **options):
        db = get_database()
        collection = db[Node.collection_name]

        print "\n In progress... \n"

        # [A] Get the " GSystemType/AttributeType/RelationType " nodes (for whom 'gsystem_type' field doesn't exist)
        cur_ty_mo = collection.Node.find({'_type': {'$in': ['GSystemType', 'AttributeType', 'RelationType']}})

        # Listing the nodes
        for n in cur_ty_mo:
            # Replace 'member_of' field with ObjectId of MetaType to which that document belongs
            # - But right now we don't have such MetaType documents
            # - Currently going to keep 'member_of' field... EMPTY!

            n.member_of = []
    
            # print "  ", n._id, " - ", n.name, " - ", n.gsystem_type, " - ", n.member_of
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
                # print "\n Group document: "

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
                # print "\n Other GAPP document: "

                gsystem_oid_list = n.gsystem_type
                n.member_of = []

                n.member_of = gsystem_oid_list
                # # Iterate ObjectId list
                # for oid in gsystem_oid_list:
                #     gsystem_node = collection.Node.one({'_id': oid})
                #     n.member_of.append(gsystem_node)
                
            # print "  ", n._id, " - ", n.name, " - ", n.gsystem_type, " - ", n.member_of
            n.save()

        # Remove 'gsystem_type' field from already existing documents where ever it exists!
        collection.update({'gsystem_type': {'$exists': True}}, {'$unset': {'gsystem_type': ""}}, multi=True)

        # --- End of handle() ---

