from fabric.api import local

# from django.conf import settings
# settings.configure()
# from gnowsys_ndf.settings import PROJECT_ROOT


def copy_schema_csvs():
	local('cp -v ../doc/schema_directory/* gnowsys_ndf/ndf/management/commands/schema_files/')


def update_data():
	copy_schema_csvs()
	local('python manage.py filldb')
	local('python manage.py create_schema STs_run1.csv')
	local('python manage.py create_schema ATs.csv')
	local('python manage.py create_schema RTs.csv')
	local('python manage.py create_schema STs_run2.csv')
	local('python manage.py sync_existing_documents')


def install_requirements():
	local('pip install -r ../requirements.txt')


def purge_group():
	local('python manage.py purge_group')


def setup_dlkit():
	# 1. confirm path
	# 2. check whether dlkit already exists. if not clone dlkit else update dlkit.
	# 3. check whether dlkit_runtime already exists. if not clone dlkit else update dlkit_runtime.
	# 4. get files for app_configs.
	pass