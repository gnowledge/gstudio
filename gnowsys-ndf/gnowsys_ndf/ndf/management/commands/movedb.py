''' -- imports from python libraries -- '''
from os import path as OS_PATH

''' imports from installed packages '''
from django.core.management.base import BaseCommand

''' imports from application folders/files '''
from gnowsys_ndf.settings import PROJECT_ROOT, SQLITE3_DBNAME, RCS_REPO_DIRNAME, GSTUDIO_DATA_ROOT
from gnowsys_ndf.ndf.utils import is_dir_exists, get_project_abspath, get_current_dbs_path, move_file_or_dirctory

###############################################################################

class Command(BaseCommand):
    help = "This performs relocation of databases (including rcs) from source to destination." 

    def handle(self, *args, **options):
        source = raw_input('Enter source path (If empty, then settings.PROJECT_ROOT is considered): ')
        if not source: 
            source = get_project_abspath()
        destination = raw_input('Enter destination path (If empty, then settings.GSTUDIO_DATA_ROOT is considered): ')
        if not destination:
            destination = GSTUDIO_DATA_ROOT
        sql_dbname = raw_input('Enter SQLITE3 database-name (excluding extension) (If empty, then settings.SQLITE3_DBNAME is considered): ')
        if not sql_dbname:
            sql_dbname = SQLITE3_DBNAME
        rcs_dirname = raw_input('Enter RCS directory-name (excluding extension) (If empty, then settings.RCS_REPO_DIRNAME is considered): ')
        if not rcs_dirname:
            rcs_dirname = RCS_REPO_DIRNAME
        self.stdout.write('Data is going to be moved:')
        self.stdout.write('  FROM: {0}'.format(source))
        self.stdout.write('    TO: {0}'.format(destination))
        self.stdout.write('\n  SQLITE3: {0}'.format(sql_dbname))
        self.stdout.write('      RCS: {0}'.format(rcs_dirname))
        confirm = raw_input('Do you wish to continue? (y/n): ').lower()
        if confirm != 'y':
            self.stdout.write('Data transfer ABORTED!')
            return
        try:
            # Written here in order to make sure required database(s) exist(s) at their specified path.
            os_path_basename = OS_PATH.basename
            is_anything_moved = False
            destination = OS_PATH.expanduser(destination)
            for each_path in get_current_dbs_path(sql_dbname, rcs_dirname, source).values():
                if each_path:
                    # If exists, then only move.
                    move_file_or_dirctory(each_path, destination)
                    self.stdout.write("  {0} moved succesfully to {1}".format(os_path_basename(each_path), destination))
                    is_anything_moved = True
            if not is_anything_moved:
                self.stdout.write('NOTHING got transferred!')
            else:
                # Read in the file
                filedata = None
                file_to_update = OS_PATH.join(PROJECT_ROOT, 'local_settings.py')
                with open(file_to_update, 'r') as file :
                    filedata = file.read()

                # Create backup of the file
                with open(file_to_update.replace('local_settings', 'local_settings_backup'), 'w') as file:
                    file.write(filedata)

                u_filedata = ""
                for e in filedata.split("\n"):
                    if 'GSTUDIO_DATA_ROOT = ' in e:
                        u_filedata += "GSTUDIO_DATA_ROOT = '{0}'".format(destination) + "\n"
                    elif 'SQLITE3_DBNAME = ' in e:
                        u_filedata += "SQLITE3_DBNAME = '{0}'".format(sql_dbname) + "\n"
                    elif 'RCS_REPO_DIRNAME = ' in e:
                        u_filedata += "RCS_REPO_DIRNAME = '{0}'".format(rcs_dirname) + "\n"
                    else:
                        u_filedata += e + "\n"

                # Write the file out again
                with open(file_to_update, 'w') as file:
                    file.write(u_filedata)

                self.stdout.write('Data transferred SUCCESSFULLY.')
        except Exception as e:
            self.stderr.write("movedb: {0}".format(str(e)))
