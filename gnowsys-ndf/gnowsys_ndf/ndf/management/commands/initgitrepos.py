''' imports from python libraries '''
import os

''' imports from installed packages '''
<<<<<<< HEAD
from django.core.management.base import BaseCommand, CommandError

#from git import Repo

''' imports from application folders/files '''
from gnowsys_ndf.settings import VERSIONING_COLLECTIONS
from gnowsys_ndf.ndf.models import HistoryManager

=======
# from django_mongokit import document
from django.core.management.base import BaseCommand, CommandError

from git import Repo


''' imports from application folders/files '''
from gnowsys_ndf import settings
from gnowsys_ndf.ndf import models

>>>>>>> 50041433bee53a620ba79bdc145a23e7beea01df
####################################################################################################################

class Command(BaseCommand):
    help = "Creates/Initiates git repositories for each collection.\n\n" \
           " By calling create_repos() function of HistoryManager class:\n" \
           "\tHistroyManager().create_repos(self, *args)\n which in turn calls:\n" \
           "\tgit.repo.base.Repo.init(path=<path>, mkdir=True)"

    def handle(self, *args, **options):
<<<<<<< HEAD
    	HistoryManager().create_repos(*VERSIONING_COLLECTIONS)
=======
    	git_repo_path = settings.GIT_REPO_PATH
    	
    	dir_exists = os.path.isdir(git_repo_path)
    	
    	if not dir_exists:
    		os.system("mkdir -p " + git_repo_path)
    		print(" Following path for git repository created successfully :- \n  " + git_repo_path + "\n")

    	for model in settings.VERSIONING_COLLECTIONS:
    		model_repo = Repo.init( os.path.join( git_repo_path, model ), True )
    		print(" " + str(model_repo) + " -- git repository created")
    	
    	print("\n")


>>>>>>> 50041433bee53a620ba79bdc145a23e7beea01df
