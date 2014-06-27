''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node
###################################################################################################################################################################################
collection = get_database()[Node.collection_name]
theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})    

class Command(BaseCommand):

    help = " This script will create the themes & its hierarchy from nodes collection "

    def handle(self, *args, **options):
        

        grp = collection.Node.one({'_type': 'Group', '_id': ObjectId('5315b7497d9d331e53c12bda')})

        lisp = []
        if grp:

            if grp.collection_set:
                for each in grp.collection_set:
                    col_obj = collection.Node.one({'_id': ObjectId(each) })
                    theme_obj = create_theme(col_obj)

        else:
            print "\n Mahagyan Group not exists ... "

def create_theme(node):

    theme_obj = save_theme(node)

    if node.collection_set:
        for each in node.collection_set:
            col_obj = collection.Node.one({'_id': ObjectId(each) })
            inner_col_obj = create_theme(col_obj)
            
            if inner_col_obj._id not in theme_obj.collection_set:
                theme_obj.collection_set.append(inner_col_obj._id)

    theme_obj.save()
    
    return theme_obj


def save_theme(node):
    
    theme_obj = None
    theme_obj = collection.Node.one({'_type': "GSystem", 'member_of': theme_GST._id, 'name': node.name})

    if theme_obj:
        print "\n Theme name : ", theme_obj.name, "already exists ... \n"
        return theme_obj

    else:
        theme_obj = collection.GSystem()

        for k in node.keys():
            if k == "collection_set":
                theme_obj[k] = []
            elif k == "member_of":
                theme_obj[k].append(theme_GST._id)
            elif k in ["_id", "_type"]:
                continue
            else:
                theme_obj[k] = node[k]


        print "\n Theme node: ", theme_obj.name, "created successfully \n"

        return theme_obj
