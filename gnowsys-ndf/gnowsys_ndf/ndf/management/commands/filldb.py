''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from bson import ObjectId

from django_mongokit import get_database

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import GSystem
from gnowsys_ndf.ndf.models import GSystemType
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.ndf.rcslib import RCS

####################################################################################################################

class Command(BaseCommand):
    help = "Inserts few documents (consisting of dummy values) into the following collections:\n\n" \
           "\tGSystemType, GSystemType"

    def handle(self, *args, **options):
        db = get_database()
        hm = HistoryManager()
        rcsobj = RCS()

        db.drop_collection(GSystem.collection_name)
        db.drop_collection(GSystemType.collection_name)
        
        # Creating a GSystemType document as 'Wikipage'
        c_gt = db[GSystemType.collection_name]
        o_gt = c_gt.GSystemType()
        o_gt.name = u"Wikipage"
        o_gt.member_of = u"GSystemType"
        o_gt.save()

        if not hm.create_or_replace_json_file(o_gt):
            c_gt.remove({'_id': o_gt._id})
        else:
            fp = hm.get_file_path(o_gt)
            rcsobj.checkin(fp, 0, "This document("+str(o_gt.name)+") is of GSystemType.", "-i")
        

        # Extracting document-id
        objid = c_gt.GSystemType.one({'name': u"Wikipage"})._id

        # Creating five GSystem documents with dummy values
        c_gs = db[GSystem.collection_name]
        
        o_gs = []

        for i in range(0, 5):
            o_gs.append(c_gs. GSystem())
            o_gs[i].name = unicode("demo_wiki_" + str(i+1))
            o_gs[i].member_of = unicode("Wikipage")
            o_gs[i].gsystem_type = objid
            o_gs[i].save()

            if not hm.create_or_replace_json_file(o_gs[i]):
                c_gs.remove({'_id': o_gs[i]._id})
            else:
                fp = hm.get_file_path(o_gs[i])
                rcsobj.checkin(fp, 0, "This document("+str(o_gs[i].name)+") is of GSystem.", "-i")
        
        # --- End of handle() ---
