''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node
import ox
db =get_database()
collection = db['Nodes']


####################################################################################################################

class Command(BaseCommand):
    help = "\tThis script sets access_policy for pandora videos"

    def handle(self, *args, **options):
        main()
        
        # --- End of handle() ---


def main():
    access_policy = u"PRIVATE"
    pandora_video_st=collection.Node.one({'$and':[{'name':'Pandora_video'},{'_type':'GSystemType'}]})
    get_member_set=collection.Node.find({'$and':[{'member_of': {'$all': [ObjectId(pandora_video_st._id)]}},{'_type':'File'}]})
    for each in list(get_member_set):
        collection.update({'_id':each._id},{'$set': {'access_policy': access_policy}})
    print "\n All pandora videos access policy sets to "+access_policy+"\n"
