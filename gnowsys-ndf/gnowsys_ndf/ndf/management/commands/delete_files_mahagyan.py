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

    help = " This script will delete the files from 'Mahagyan' group "

    def handle(self, *args, **options):
        

        grp = collection.Node.one({'_type': 'Group', '_id': ObjectId('5315b7497d9d331e53c12bda')})

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

                print "\nfile object: ",each.name," removed successfully from Mahagyan grp"
                each.delete()


        else:
            print "\n Mahagyan Group not exists ... "

