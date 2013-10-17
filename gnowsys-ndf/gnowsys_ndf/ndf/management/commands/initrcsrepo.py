''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError


''' imports from application folders/files '''
from gnowsys_ndf.settings import VERSIONING_COLLECTIONS
from gnowsys_ndf.ndf.models import HistoryManager

####################################################################################################################

class Command(BaseCommand):
    help = " Creates an RCS repository along with sub-directories for each collection inside it.\n\n" \
           " By calling create_rcs_repo_collections() function of HistoryManager class:\n" \
           "\tHistroyManager().create_rcs_repo_collections(self, *args)\n "

    def handle(self, *args, **options):
    	HistoryManager().create_rcs_repo_collections(*VERSIONING_COLLECTIONS)
