''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import node_collection
###################################################################################################################################################################################
theme_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Theme'})  
theme_item_GST = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item' })


class Command(BaseCommand):

    help = " This script will create the themes & its hierarchy from its previous theme & sub-theme structure "

    def handle(self, *args, **options):
        

        grp = node_collection.one({'_type': 'Group', '_id': ObjectId('5315b7497d9d331e53c12bda')})
        # grp = node_collection.one({'_type': 'Group', 'name': 'home'})

        lisp = []
        themes_list = []
        theme_item_list = [] 


        if grp:
            nodes = node_collection.find({'_type': 'GSystem', 'group_set': ObjectId(grp._id), 'member_of': {'$in': [theme_GST._id]} })

            for each in nodes:
                if each.collection_set:
                    for l in each.collection_set:
                        lisp.append(l)

            nodes.rewind()
            for e in nodes:
                if e._id not in lisp:
                    themes_list.append(e._id)


            nodes.rewind()
            for theme_item in nodes:
                if theme_item._id not in themes_list:
                    theme_item.member_of = []
                    theme_item.member_of.append(theme_item_GST._id)
                    theme_item.save()


        else:
            print "\n Mahagyan Group not exists ... "
