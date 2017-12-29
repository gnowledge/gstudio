import os

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


def update(branch='master'):
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
    try:
        local('pip install -r ../requirements.txt')
    except Exception as e:
        print e
    finally:
        local('bower install --allow-root')


def purge_node():
	local('python manage.py purge_node')


def group_import(dump_path):
    # Example Usage: 
    # fab group_import:/data/data_export/test-module_2017-09-09_13-11
    print "\n Path of node/group to restore: ", dump_path
    local('python manage.py group_import %s y y y' % dump_path)
    local('rm 5*')


def group_import_all(dump_folder):
    # Example Usage: 
    # fab group_import_all:/data/data_export
    dump_folder_list = filter( lambda f: not f.startswith('.'), os.listdir(dump_folder))
    for each_dump in dump_folder_list:
        print "\n\n\nRestoring dump of : ", each_dump
        group_import(os.path.join(dump_folder, each_dump))


def backup_psql_data(location='/data/postgres-dump/'):
    # Example Usage: 
    # fab backup_psql_data
    # OUTPUT:
    #   ls /data/postgres-dump/
    #   20170925162540.sql
    # fab backup_psql_data:/data/

    import datetime
    backup_file_name = "pgdump-{:%Y%m%d%H-%M%S}".format(datetime.datetime.now()) + ".sql"
    local('echo "pg_dumpall > %s" | sudo su - postgres' % backup_file_name)
    try:
        local('mv /var/lib/postgresql/%s %s' % (backup_file_name, location))
    except Exception as e:
        raise e
    print "\nBackup file would be found at: ", os.path.join(location, backup_file_name)


def restore_psql_data(backup_file_path_name):
    # Example Usage: 
    # fab restore_psql_data:/data/20170925162649.sql
    # fab restore_psql_data:/data/postgres-dump/20170925162540.sql
    try:
        local('echo "psql -f %s;" | sudo su - postgres' % backup_file_path_name)
    except Exception as e:
        raise e


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
