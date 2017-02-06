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
    import os
    dirspot = os.getcwd()
    if "/home/docker/code/gstudio/gnowsys-ndf" == dirspot:
 		if not os.path.isdir('./dlkit') and not os.path.isdir('./dlkit_runtime'):
			local('git checkout dlkit')
			local('git pull origin dlkit')
			local('git clone https://bitbucket.org/cjshaw/dlkit_runtime.git')
			local('git clone https://bitbucket.org/cjshaw/dlkit-tests.git')
			local('git clone https://bitbucket.org/cjshaw/dlkit.git')
			os.chdir('/home/docker/code/gstudio/gnowsys-ndf/dlkit')
			local('git submodule update --init --recursive')
			os.chdir('/home/docker/code/gstudio/gnowsys-ndf/')
			update_data()
     	else:
         	print "dlkit and dlkit_runtime are already exists."
	else:
		os.chdir('/home/docker/code/gstudio/gnowsys-ndf')
		setup_dlkit()