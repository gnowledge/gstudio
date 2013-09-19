''' imports from python libraries '''
import os

''' imports from installed packages '''
# from django_mongokit import document
from django.core.management.base import BaseCommand, CommandError

from git import Repo


''' imports from application folders/files '''
from gnowsys_ndf import settings
from gnowsys_ndf.ndf import models

####################################################################################################################

class Command(BaseCommand):
    help = 'Creates required git repositories for each collection'

    def handle(self, *args, **options):
    	git_repo_path = settings.GIT_REPO_PATH
    	
    	dir_exists = os.path.isdir(git_repo_path)
    	
    	if not dir_exists:
    		os.system("mkdir -p " + git_repo_path)
    		print(" Following path for git repository created successfully :- \n  " + git_repo_path + "\n")

    	for model in settings.VERSIONING_COLLECTIONS:
    		model_repo = Repo.init( os.path.join( git_repo_path, model ), True )
    		print(" " + str(model_repo) + " -- git repository created")
    	
    	print("\n")


