from fabric.api import local

# from django.conf import settings
# settings.configure()
# from gnowsys_ndf.settings import PROJECT_ROOT


def copy_schema_csvs():
	local('cp -v ../doc/schema_directory/* gnowsys_ndf/ndf/management/commands/schema_files/')


def create_schema():
	copy_schema_csvs()
	local('python manage.py create_schema STs_run1.csv')
	local('python manage.py create_schema ATs.csv')
	local('python manage.py create_schema RTs.csv')
	local('python manage.py create_schema STs_run2.csv')


def update_data():
	try:
		# for existing data
		local('python manage.py sync_existing_documents')
	except Exception, e:
		# exception will happen for fresh data
		pass
	finally:
		create_schema()
		local('python manage.py filldb')
		local('python manage.py create_schema ATs.csv')
		local('python manage.py sync_existing_documents')


def update(branch):
	try:
		local('git pull origin ' + branch)
		local('python manage.py syncdb')
		install_requirements()
		local('python manage.py collectstatic --noinput')
	except Exception, e:
		print e
	finally:
		update_data()


def install_requirements():
	local('pip install -r ../requirements.txt')
	local('bower install --allow-root')


def purge_node():
	local('python manage.py purge_node')


# def setup_dlkit():
# 	import os
# 	dirspot = os.getcwd()
# 	if "/home/docker/code/gstudio/gnowsys-ndf" == dirspot:
# 		if not os.path.isdir('./dlkit') and not os.path.isdir('./dlkit_runtime'):
# 			local('git checkout dlkit')
# 			local('git pull origin dlkit')
# 			local('git clone https://bitbucket.org/cjshaw/dlkit_runtime.git')
# 			local('git clone https://bitbucket.org/cjshaw/dlkit-tests.git')
# 			local('git clone https://bitbucket.org/cjshaw/dlkit.git')
# 			os.chdir('/home/docker/code/gstudio/gnowsys-ndf/dlkit')
# 			local('git submodule update --init --recursive')
# 			os.chdir('/home/docker/code/gstudio/gnowsys-ndf/')
# 		else:
# 			print "dlkit and dlkit_runtime are already exists."
# 	else:
# 		os.chdir('/home/docker/code/gstudio/gnowsys-ndf')
# 		setup_dlkit()
