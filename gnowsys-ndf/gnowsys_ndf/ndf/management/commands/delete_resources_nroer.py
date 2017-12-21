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

class Command(BaseCommand):

    help = " This script will delete the files from 'home' group "

    def handle(self, *args, **options):
        

        grp = collection.Node.one({'_type': 'Group', '_id': ObjectId('53747277c1704121fe54be46')})
        # grp = collection.Node.one({'_type': 'Group', 'name': 'home'})
        page_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Page'})

        if grp:

            files_cur = collection.Node.find({'_type': "File", 'group_set': ObjectId(grp._id)})
            all_obj = collection.Node.find({'group_set': ObjectId(grp._id)})

            for each in files_cur:
                all_obj.rewind()
                for grp_obj in all_obj:
                    if grp_obj.collection_set:
                        collection.update({'_id': grp_obj._id}, {'$pull': {'collection_set': ObjectId(each._id) }}, upsert=False, multi=False)


                if each.fs_file_ids:
                    for objs in each.fs_file_ids:
                        each.fs.files.delete(objs)

                each.delete()
                print "\nfile object: ",each.name," removed successfully from home group"

            data = collection.Node.find({'_type': {'$nin': ['Group','Author']},'group_set': ObjectId(grp._id), 'member_of': {'$nin':[page_GST._id]} })
            for each in data:
                each.delete()
                print "\nObject : ", each.name," removed successfully from home group"

        else:
            print "\n home Group not exists ... "

