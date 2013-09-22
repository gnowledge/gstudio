''' imports from python libraries '''
import os

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

#from git import Repo

''' imports from application folders/files '''
from gnowsys_ndf.settings import VERSIONING_COLLECTIONS
from gnowsys_ndf.ndf.models import HistoryManager

####################################################################################################################

class Command(BaseCommand):
    help = "Creates/Initiates git repositories for each collection.\n\n" \
           " By calling create_repos() function of HistoryManager class:\n" \
           "\tHistroyManager().create_repos(self, *args)\n which in turn calls:\n" \
           "\tgit.repo.base.Repo.init(path=<path>, mkdir=True)"

    def handle(self, *args, **options):
    	HistoryManager().create_repos(*VERSIONING_COLLECTIONS)
