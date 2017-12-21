# imports from python libraries
from os import walk as OS_WALK
from os import makedirs as OS_MD
from os import path as OS_PATH
import fnmatch
from shutil import move as SHUTIL_MOVE

# imports from django libraries

# imports from third-party app(s)

# imports from project-app(s)

# NOTE: Please write all import(s) from settings file, inside the function(s)
# wherever it is required. For e.g., refer get_project_abspath() function.


def get_project_abspath():
    """Returns absolute path of this project-directory.
    """
    from gnowsys_ndf.settings import PROJECT_ROOT
    return PROJECT_ROOT.split('gnowsys-ndf')[0]


def get_current_dbs_path(sqlite_dbname=None, rcs_repo_dirname=None, search_in_path=None):
    """Returns absolute path of the all databases including following:
        > sqlite database
        > rcs-repo directory

    search_in_path: This is the path where all database(s) needs to be searched in.
        If not specified, by default project-directory is used.

    Returns dictionary with following set of key-value pairs:
        > current_sqlite_db_abspath: This is an aboslute path of the sqlite database;
          if found in the search_in_path, otherwise None
        > current_rcs_repo_abspath: This is an aboslute path of the rcs-repo directory;
          if found in the search_in_path, otherwise None
    """
    if not sqlite_dbname:
        from gnowsys_ndf.settings import SQLITE3_DBNAME
        sqlite_dbname = SQLITE3_DBNAME

    if not rcs_repo_dirname:
        from gnowsys_ndf.settings import RCS_REPO_DIRNAME
        rcs_repo_dirname = RCS_REPO_DIRNAME

    if not search_in_path:
        search_in_path = get_project_abspath()

    rcs_repo_found = False
    sqlite_db_found = False

    current_sqlite_db_abspath = None
    current_rcs_repo_abspath = None

    try:
        for root, dirnames, filenames in OS_WALK(OS_PATH.expanduser(search_in_path)):
            if not rcs_repo_found:
                dir_matches = fnmatch.filter(dirnames, rcs_repo_dirname)
                if dir_matches:
                    rcs_repo_found = True
                    current_rcs_repo_abspath = OS_PATH.join(root, dir_matches[0])

            if not sqlite_db_found:
                file_matches = fnmatch.filter(filenames, sqlite_dbname)
                if file_matches:
                    sqlite_db_found = True
                    current_sqlite_db_abspath = OS_PATH.join(root, file_matches[0])

            if sqlite_db_found and rcs_repo_found:
                break
    except Exception as e:
        raise Exception("Exception (ndf.utils.get_current_dbs_path): {0}".format(str(e)))

    return {
        'current_sqlite_db_abspath': current_sqlite_db_abspath,
        'current_rcs_repo_abspath': current_rcs_repo_abspath,
    }


def is_dir_exists(dir_path):
    """Returns whether given directory-path exists or not.
    """
    try:
        return OS_PATH.exists(OS_PATH.expanduser(dir_path))
    except AttributeError:
        return False


def ensure_dir(dir_path):
    """Ensures the given directory-path exists.

    If given directory path doesn't exists, it is created.

    Returns a boolean value.
        > True: If given directory-path exists.
        > False: If any exception occurs while directory creation.
    """
    try:
        dir_path = OS_PATH.expanduser(dir_path)
        if not is_dir_exists(dir_path):
            OS_MD(dir_path)
    except Exception as e:
        raise Exception("InvalidDirectoryPath - {0}".format(str(e)))
    return True


def move_file_or_dirctory(src_path, dest_path):
    """Recursively moves a file or directory to another location.

    src_path: This is absolute filesystem path of the source (file/directory)
    dest_path: This is absolute filesystem path of the destination directory

    For directory that needs to be moved to new location, appending
    os-path separator (i.e. '/') to end of the src_path. This is required
    , so the parent-directory along with it's content is shifted; otherwise
    only the content is moved to the dest_path.

    For more details, refer shutil.move() function.

    Returns a boolean value.
        > True: On successful movement of file or directory to another location.
        > False: If invalid arguments are passed or exception/error occurs while
            moving file or directory.
    """
    src_path = OS_PATH.expanduser(src_path)
    dest_path = OS_PATH.expanduser(dest_path)

    if OS_PATH.isdir(src_path):
        os_path_sep = OS_PATH.sep
        if not src_path.endswith(os_path_sep):
            # Required in order to move all sub-folders including the given parent-directory
            # If not done, only the sub-folders of the given parent-directory will be moved
            src_path += os_path_sep

    ensure_dir(dest_path)

    try:
        SHUTIL_MOVE(src_path, dest_path)
    except Exception as e:
        raise Exception("InvalidSourceOrDestination - {0}".format(str(e)))

    return True

