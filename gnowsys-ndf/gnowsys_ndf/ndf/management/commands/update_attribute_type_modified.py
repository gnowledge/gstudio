''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node, Triple, HistoryManager
from gnowsys_ndf.ndf.rcslib import RCS

####################################################################################################################

class Command(BaseCommand):
    """This update-script updates attribute_type field's value (of all GAttribute instances) from ObjectId to it's corresponding DBRef; and also creates it's version-file(history) in rcs-repo.
    """

    help = "\tThis update-script updates attribute_type field's value (of all GAttribute instances) from ObjectId to it's corresponding DBRef; and also creates it's version-file(history) in rcs-repo."

    def handle(self, *args, **options):

        history_manager = HistoryManager()
        rcs_obj = RCS()

        collection = get_database()[Triple.collection_name]
        cur = collection.Triple.find( {'_type': 'GAttribute'} )

        for n in cur:
            if type(n['attribute_type']) == ObjectId:
                attr_type = collection.Node.one( {'_id': n['attribute_type']} )
                if attr_type:
                    collection.update({'_id':n['_id']},{'$set':{'attribute_type':{"$ref" : attr_type.collection_name, "$id" : attr_type._id,"$db" :attr_type.db.name}}})
                else:
                    collection.remove({'_id':n['_id']})

            subject_doc = collection.Node.one({'_id': n.subject})
            n.name = subject_doc.name + " -- " + n.attribute_type['name'] + " -- " + n.object_value

            # Creates a history (version-file) for GAttribute documents
            if history_manager.create_or_replace_json_file(n):
                fp = history_manager.get_file_path(n)
                message = "This document (" + n.name + ") is created on " + subject_doc.created_at.strftime("%d %B %Y")
                rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

        # --- End of handle() ---

