'''
Units can be linked with the assessments details using command line args as following:
    like:
        python manage.py unit_assessments <domain_name> y
        E.g
        python manage.py unit_assessments https://localhost y
'''

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.ndf.models import node_collection, GSystemType
from gnowsys_ndf.ndf.views.methods import get_all_iframes_of_unit

# domain = "https://localhost"

class Command(BaseCommand):
    def handle(self, *args, **options):

        if args and len(args)==2 :
            domain_name = args[0]
            confirm_process = args[1]
        else:
            print "\n Example domain names: \n\t\t1. https://clixserver" + \
            " \n\t\t2.https://clixplatform.tiss.edu"
            domain_name = raw_input("Enter domain name/IP(with 'https://'): ")
            confirm_process = raw_input("\nConfirm to proceed with domain-name: " + \
                str(domain_name) + "\n(Enter y or Y to continue)")
        
        if (domain_name.startswith("https://")) and confirm_process in ['y', 'Y']:
            print "\nProceeding with Domain: ", domain_name
            gst_announced_unit_name, gst_announced_unit_id = GSystemType.get_gst_name_id("announced_unit")
            announced_unit_cur = node_collection.find({'member_of': gst_announced_unit_id})

            for each_ann_unit in announced_unit_cur:
                get_all_iframes_of_unit(each_ann_unit, domain_name)
        else:
            print "\nPlease try again."