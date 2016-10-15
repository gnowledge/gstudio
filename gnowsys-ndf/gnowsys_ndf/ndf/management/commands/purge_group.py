from django.core.management.base import BaseCommand
from gnowsys_ndf.ndf.models import Group

class Command(BaseCommand):
    def handle(self, *args, **options):

        print "Enter group name or _id: "
        group_id = raw_input()

        Group.purge_group(group_id, proceed=False)
