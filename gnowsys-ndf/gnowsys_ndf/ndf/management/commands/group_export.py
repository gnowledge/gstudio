import os
import datetime
import subprocess
import re
# from threading import Thread
# import multiprocessing
# import math
from bs4 import BeautifulSoup

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.ndf.models import node_collection, triple_collection, filehive_collection, counter_collection
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.settings import GSTUDIO_DATA_ROOT, GSTUDIO_LOGS_DIR_PATH, MEDIA_ROOT, GSTUDIO_INSTITUTE_ID
from schema_mapping import create_factory_schema_mapper
from users_dump_restore import create_users_dump
from gnowsys_ndf.ndf.views.methods import get_group_name_id
from gnowsys_ndf.ndf.templatetags.simple_filters import get_latest_git_hash, get_active_branch_name

# global variables declaration
GROUP_CONTRIBUTORS = []
DUMP_PATH = None
TOP_PATH = os.path.join(GSTUDIO_DATA_ROOT, 'data_export')
GROUP_ID = None
DATA_EXPORT_PATH = None
MEDIA_EXPORT_PATH = None
RESTORE_USER_DATA = False
SCHEMA_MAP_PATH = None
log_file = None
historyMgr = HistoryManager()
DUMP_NODES_LIST = []
DUMPED_NODE_IDS = set()
ROOT_DUMP_NODE_ID = None
ROOT_DUMP_NODE_NAME = None
MULTI_DUMP = False

def create_log_file(dump_node_id):
    '''
        Creates log file in gstudio-logs/ with 
        the name of the dump folder
    '''
    log_file_name = 'group_dump_' + str(dump_node_id)+ '.log'
    if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
        os.makedirs(GSTUDIO_LOGS_DIR_PATH)

    log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
    # print log_file_path
    global log_file
    log_file = open(log_file_path, 'w+')
    log_file.write("\n######### Script ran on : " + str(datetime.datetime.now()) + " #########\n\n")
    return log_file_path

def setup_dump_path(node_name):
    '''
        Creates factory_schema.json which will hold basic info
        like ObjectId, name, type of TYPES_LIST and GSTUDIO_DEFAULT_GROUPS
    '''
    global DUMP_PATH
    global TOP_PATH
    global DATA_EXPORT_PATH
    global MEDIA_EXPORT_PATH
    # datetimestamp = datetime.datetime.now().isoformat()
    datetimestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    DUMP_PATH = os.path.join(TOP_PATH, node_name + "_" + str(datetimestamp))
    DATA_EXPORT_PATH = os.path.join(DUMP_PATH, 'dump')
    MEDIA_EXPORT_PATH = os.path.join(DATA_EXPORT_PATH, 'media_files')
    if not os.path.exists(DATA_EXPORT_PATH):
        os.makedirs(DATA_EXPORT_PATH)
    if not os.path.exists(MEDIA_EXPORT_PATH):
        os.makedirs(MEDIA_EXPORT_PATH)
    return DATA_EXPORT_PATH

def create_configs_file(group_id):
    global RESTORE_USER_DATA
    global DUMP_PATH
    configs_file_path = os.path.join(DUMP_PATH, "migration_configs.py")
    with open(configs_file_path, 'w+') as configs_file_out:
        configs_file_out.write("\nRESTORE_USER_DATA=" + str(RESTORE_USER_DATA))
        configs_file_out.write("\nGSTUDIO_INSTITUTE_ID='" + str(GSTUDIO_INSTITUTE_ID) + "'")
        configs_file_out.write("\nGROUP_ID='" + str(group_id) + "'")
        configs_file_out.write("\nROOT_DUMP_NODE_ID='" + str(ROOT_DUMP_NODE_ID) + "'")
        configs_file_out.write("\nROOT_DUMP_NODE_NAME='" + str(ROOT_DUMP_NODE_NAME) + "'")
        configs_file_out.write("\nMULTI_DUMP='" + str(MULTI_DUMP) + "'")
        configs_file_out.write("\nGIT_COMMIT_HASH='" + str(get_latest_git_hash()) + "'")
        configs_file_out.write("\nGIT_BRANCH_NAME='" + str(get_active_branch_name()) + "'")
        configs_file_out.write('\nSYSTEM_DETAILS="' + str(os.uname()) + '"')
    return configs_file_path

def write_md5_of_dump(group_dump_path, configs_file_path):
    global DUMP_PATH
    from checksumdir import dirhash
    md5hash = dirhash(group_dump_path, 'md5')
    with open(configs_file_path, 'a+') as configs_file_out:
        configs_file_out.write("\nMD5='" + str(md5hash) + "'")

def get_triple_data(node_id):
    '''
    Gets all data stored in triples for this node.
    Fetches GAttrtibutes as wells as GRelations.
    '''
    try:
        global log_file
        log_file.write("\n get_triple_data invoked for: " + str(node_id))

        triple_query = {"_type": {'$in': ["GAttribute", "GRelation"]}, "subject": ObjectId(node_id)}

        node_gattr_grel_cur = triple_collection.find(triple_query)
        if node_gattr_grel_cur:
            for each_triple_node in node_gattr_grel_cur:
                fetch_value = None
                dump_node(node=each_triple_node,
                    collection_name=triple_collection)
                # Get ObjectIds in object_value fields

                if each_triple_node._type == u"GAttribute":
                    fetch_value = "object_value"
                elif each_triple_node._type == u"GRelation":
                    fetch_value = "right_subject"
                log_file.write("\n fetch_value: " + str(fetch_value))
                if fetch_value == "right_subject":
                    log_file.write("\n Picking up right-subject nodes.\n\t " + str(each_triple_node[fetch_value]))

                    if type(each_triple_node[fetch_value]) == list and all(isinstance(each_obj_value, ObjectId) for each_obj_value in each_triple_node[fetch_value]):
                        log_file.write("\n List:  " + str(True))
                        dump_node(node_id_list=each_triple_node[fetch_value],
                            collection_name=node_collection)

                    elif isinstance(each_triple_node[fetch_value], ObjectId):
                        log_file.write("\n ObjectId:  " + str(True))
                        dump_node(node_id=each_triple_node[fetch_value],
                                collection_name=node_collection)

        log_file.write("\n get_triple_data finished for: " + str(node_id))

    except Exception as get_triple_data_err:
        error_log = "\n !!! Error found while taking triple data in get_triple_data() ."
        error_log += "\nError: " + str(get_triple_data_err)
        print "\n Error: ", error_log
        log_file.write(error_log)
        print error_log
        pass


def core_export(group_node):
    if group_node:
        print "\tRequest received for Export of : ", group_node.name , ' | ObjectId: ', group_node._id
        global RESTORE_USER_DATA
        user_data_dump = raw_input("\n\tDo you want to include Users in this export ? Enter y/Y to continue:\t ")
        if user_data_dump in ['y', 'Y']:
            RESTORE_USER_DATA = True
        else:
            RESTORE_USER_DATA = False

        nodes_falling_under_grp = node_collection.find({
                "group_set":ObjectId(group_node._id),
                "_type": {'$nin': ['Group', 'Author']}})
        print "\n\tTotal objects found: ", nodes_falling_under_grp.count()
        confirm_export = raw_input("\n\tEnter y/Y to Continue or any other key to Abort:\t ")
        if confirm_export in ['y', 'Y']:
            print "START : ", str(datetime.datetime.now())
            group_dump_path = setup_dump_path(slugify(group_node.name))

            global GROUP_ID
            GROUP_ID = group_node._id
            call_group_export(group_node, nodes_falling_under_grp)
            get_counter_ids(group_node._id)
            # import ipdb; ipdb.set_trace()
            global GROUP_CONTRIBUTORS
            if RESTORE_USER_DATA:
                GROUP_CONTRIBUTORS = list(set(GROUP_CONTRIBUTORS))
                create_users_dump(group_dump_path, GROUP_CONTRIBUTORS)

            configs_file_path = create_configs_file(group_node._id)
            write_md5_of_dump(group_dump_path, configs_file_path)
            global log_file

            log_file.write("\n*************************************************************")
            log_file.write("\n######### Script Completed at : " + str(datetime.datetime.now()) + " #########\n\n")
            print "END : ", str(datetime.datetime.now())
        else:
            call_exit()
    else:
        print "\n Node not found with provided Name or ObjectID"
        call_exit()


def call_exit():
    print "\n Exiting..."
    os._exit(0)

def worker_export(nodes_cur):
    for each_node in nodes_cur:
        print ".",
        dump_node(node=each_node,collection_name=node_collection)
        # node_collection_ids.add(each_node._id)

        if each_node.collection_set:
            get_nested_ids(each_node,'collection_set')

        if each_node.prior_node:
            get_nested_ids(each_node,'prior_node')

        if each_node.post_node:
            get_nested_ids(each_node,'post_node')


def call_group_export(group_node, nodes_cur, num_of_processes=5):
    '''
        Introducing multiprocessing to use cores available on the system to 
        take dump of nodes of the entire group.
    '''
    dump_node(node=group_node,collection_name=node_collection)
    if group_node.collection_set:
        get_nested_ids(group_node,'collection_set')

    nodes_cur = list(nodes_cur)
    worker_export(nodes_cur)
    # print "\nlen(nodes_cur): ", len(nodes_cur)
    # Include Group Object.
    # nodes_cur.append(group_node)
    # Each process will get 'chunksize' student_cur and a queue to put his out
    # dict into
    # out_q = multiprocessing.Queue()
    # chunksize = int(math.ceil(len(nodes_cur) / float(num_of_processes)))
    # procs = []
    # print "\n chunk: ", chunksize

    # for i in range(num_of_processes):
    #     list_of_nodes = nodes_cur[chunksize * i:chunksize * (i + 1)]
    #     print "\nlist_of_nodes", len(list_of_nodes)
    #     p = Thread(
    #         target=worker,
    #         args=(list_of_nodes)
    #     )
    #     p.start()

    # Collect all results into a single result list. We know how many lists
    # with results to expect.
    # resultlist = []
    # for i in range(num_of_processes):
    #     resultlist.extend(out_q.get())

    # Wait for all worker processes to finish
    # for p in procs:
    #     p.join()

    # return resultlist


def build_rcs(node, collection_name):
    '''
    Updates the rcs json with the current node's strcuture that 
    might have missed due to update queries.
    Runs a save() method on the node and calls copy_rcs()
    '''
    # import ipdb; ipdb.set_trace()
    if node:
        global log_file
        global GROUP_CONTRIBUTORS
        try:
            node.save()
            if collection_name is node_collection and node.content:
                pick_media_from_content(BeautifulSoup(node.content, 'html.parser'))

            # if collection_name is triple_collection:
            #     # if 'attribute_type' in node:
            #     #     triple_node_RT_AT = node_collection.one({'_id': node.attribute_type})
            #     # elif 'relation_type' in node:
            #     #     triple_node_RT_AT = node_collection.one({'_id': node.relation_type})
            #     # node.save(triple_node=triple_node_RT_AT, triple_id=triple_node_RT_AT._id)
            #     node.save()
            # elif collection_name is node_collection:
            #     node.save()
            #     if node.content:
            #         pick_media_from_content(BeautifulSoup(node.content, 'html.parser'))
            # elif collection_name is filehive_collection:
            #     # dump_node(node_id=node['first_parent'], collection_name=node_collection)
            #     node.save()
            # else:
            #     node.save()
            try:
                global RESTORE_USER_DATA
                if RESTORE_USER_DATA:
                    if "contributors" in node:
                        GROUP_CONTRIBUTORS.extend(node.contributors)
            except Exception as no_contributors_err:
                log_file.write("\n Error while fetching contributors " + str(no_contributors_err) +\
                 " for: " + str(node._id) + " with contributors: " + str(node.contributors))
                pass
            log_file.write("\n RCS Built for " + str(node._id) )
            copy_rcs(node)
        except Exception as buildRCSError:
            error_log = "\n !!! Error found while Building RCS ."
            error_log += "\nError: " + str(buildRCSError)
            log_file.write(error_log)
            print error_log
            pass

def find_file_from_media_url(source_attr):
    try:
        global log_file
        log_file.write("\n find_file_from_media_url invoked for: " + str(source_attr))

        if "media" in source_attr:
            source_attr = source_attr.split("media/")[-1]
            file_node = node_collection.find_one({"$or": [{'if_file.original.relurl': source_attr},
                {'if_file.mid.relurl': source_attr},{'if_file.thumbnail.relurl': source_attr}]})

        elif "readDoc" in source_attr:
            split_src = source_attr.split('/')
            node_id = split_src[split_src.index('readDoc') + 1]
            file_node = node_collection.one({'_id': ObjectId(node_id)})

        if file_node:
            log_file.write("\n media file_node gs found:  " + str(file_node._id) )
            get_file_node_details(file_node)

    except Exception as find_file_from_media_url_err:
        error_log = "\n !!! Error found while taking dump in find_file_from_media_url() ."
        error_log += "\nError: " + str(find_file_from_media_url_err)
        print "\n Error: ", error_log
        log_file.write(error_log)
        print error_log
        pass

def pick_media_from_content(content_soup):
    '''
    Parses through the content of node and finds the media 
    files and dump it
    '''
    try:
        global log_file
        log_file.write("\n pick_media_from_content invoked.")

        all_src = content_soup.find_all(src=re.compile('media|readDoc'))
        # Fetching the files
        for each_src in all_src:
            src_attr = each_src["src"]
            find_file_from_media_url(src_attr)

        all_transcript_data = content_soup.find_all(attrs={'class':'transcript'})
        for each_transcript in all_transcript_data:
            data_ele = each_transcript.findNext('object',data=True)
            if data_ele:
                if 'media' in data_ele['data']:
                    find_file_from_media_url(data_ele['data'])

        all_transcript_data = content_soup.find_all(attrs={'class':'transcript-data'})
        for each_transcript in all_transcript_data:
            data_ele = each_transcript.findNext('object',data=True)
            if data_ele:
                if 'media' in data_ele['data']:
                    find_file_from_media_url(data_ele['data'])
    except Exception as pick_media_err:
        error_log = "\n !!! Error found in pick_media_from_content()."
        error_log += "\nError: " + str(pick_media_err)
        print "\n Error: ", error_log
        log_file.write(error_log)
        print error_log
        pass

def copy_rcs(node):
    '''
    Actual copying of RCS files from /data/rcs-repo/ to export_path/rcs-repo
     of the nodes called from dump_node() and build_rcs()
    '''
    if node:
        global log_file
        try:
            # To update RCS
            path = historyMgr.get_file_path(node)
            path = path + ",v"

            if not os.path.exists(path):
                path = historyMgr.get_file_path(node)
                path = path + ",v"

            cp = "cp  -vu " + path + " " +" --parents " + DATA_EXPORT_PATH + "/"
            subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)

            log_file.write("\n RCS Copied " + str(path) )

        except Exception as copyRCSError:
            error_log = "\n !!! Error found while Copying RCS ."
            error_log += "\nError: " + str(copyRCSError)
            log_file.write(error_log)
            print error_log
            pass

def dumping_call(node, collection_name):
    try:
        global log_file
        global GROUP_ID
        global DUMPED_NODE_IDS
        log_file.write("\nDumping Call for : " + str(node))
        if (node._id == GROUP_ID or node._type != "Group") and node._id not in DUMPED_NODE_IDS:
            build_rcs(node, collection_name)

            if collection_name == node_collection:
                get_triple_data(node._id)
                DUMPED_NODE_IDS.add(node._id)
                if 'File' in node.member_of_names_list:
                    get_file_node_details(node, exclude_node=True)
            else:
                DUMPED_NODE_IDS.add(node._id)
            log_file.write("\n Dump node finished for:  " + str(node._id) )
        else:
            log_file.write("\n Already dumped node: " + str(node._id) )

    except Exception as dumping_call_err:
        error_log = "\n !!! Error found in dumping_call_node() ."
        error_log += "\nError: " + str(dumping_call_err)
        log_file.write(error_log)
        print error_log
        pass

def dump_node(collection_name=node_collection, node=None, node_id=None, node_id_list=None):
    '''
    Receives all nodes pertaining to exporting group belonging to all existing collections.
    Calls build_rcs.
    '''
    try:
        global log_file
        log_file.write("\n dump_node invoked for: " + str(collection_name))
        if node:
                dumping_call(node,collection_name)
        elif node_id:
            log_file.write("\tNode_id : " + str(node_id))
            node = collection_name.one({'_id': ObjectId(node_id), '_type': {'$nin': ['Group', 'Author']}})
            if node:
                dumping_call(node,collection_name)

        elif node_id_list:
            node_cur = collection_name.one({'_id': {'$in': node_id_list}, '_type': {'$nin': ['Group', 'Author']}})
            log_file.write("\tNode_id_list : " + str(node_id_list))
            for each_node in nodes_cur:
                if each_node:
                    dumping_call(node,collection_name)

    except Exception as dump_err:
        error_log = "\n !!! Error found while taking dump in dump_node() ."
        error_log += "\nError: " + str(dump_err)
        log_file.write(error_log)
        print error_log
        pass

def dump_media_data(media_path):
    # Copy media file to /data/media location
    # print MEDIA_EXPORT_PATH
    global log_file
    log_file.write("\n--- Media Copying in process --- "+ str(media_path))
    try:
        if media_path:
            fp = os.path.join(MEDIA_ROOT,media_path)
            if os.path.exists(fp):
                cp = "cp  -u " + fp + " " +" --parents " + MEDIA_EXPORT_PATH + "/"
                subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
                log_file.write("\n Media Copied:  " + str(fp) )

            else:
                log_file.write("\n Media NOT Copied:  " + str(fp) )
        else:
            log_file.write("\n No MediaPath found:  " + str(media_path) )
    
    except Exception as dumpMediaError:
        error_log = "\n !!! Error found while taking dump of Media.\n" +  str(media_path)
        error_log += "\nError: " + str(dumpMediaError)
        log_file.write(error_log)
        print error_log
        pass

def get_file_node_details(node, exclude_node=False):
    '''
    Check if_file field and take its dump
    'if_file': {
                    'mime_type': basestring,
                    'original': {'id': ObjectId, 'relurl': basestring},
                    'mid': {'id': ObjectId, 'relurl': basestring},
                    'thumbnail': {'id': ObjectId, 'relurl': basestring}
                },

    '''
    try:
        global log_file
        log_file.write("\n get_file_node_details invoked for: " + str(node))
        if not exclude_node:
            dump_node(node=node, collection_name=node_collection)
        dump_node(node_id=node.if_file['original']['id'], collection_name=filehive_collection)
        dump_node(node_id=node.if_file['mid']['id'], collection_name=filehive_collection)
        dump_node(node_id=node.if_file['thumbnail']['id'], collection_name=filehive_collection)
        dump_media_data(node.if_file['original']['relurl'])
        dump_media_data(node.if_file['mid']['relurl'])
        dump_media_data(node.if_file['thumbnail']['relurl'])
        # if each_field == 'group_set':
        #     for each_grp_id in node.group_set:
        #         group_node = node_collection.find_one({"_id":ObjectId(each_grp_id)})
        #         if group_node and group_node._type != unicode('Author'):
        #             group_set.extend(group_node.group_set)
        # if each_field == 'author_set':
        #     user_list.extend(node.author_set)
    except Exception as file_dump_err:
        error_log = "\n !!! Error found while taking dump in get_file_node_details() ."
        error_log += "\nError: " + str(file_dump_err)
        log_file.write(error_log)
        print error_log
        pass

def get_nested_ids(node,field_name):
    '''
        Recursive function to fetch Objectids from a 
        particular field of passed node.
        field_name can be : collection_set, post_node, prior_node
    '''
    if node[field_name]:
        for each_id in node[field_name]:
            each_node = node_collection.one({"_id":ObjectId(each_id), '_type': {'$nin': ['Group', 'Author']}})
            if each_node and (node._id != each_node._id):
                dump_node(node=each_node, collection_name=node_collection)
                if each_node and each_node[field_name]:
                    get_nested_ids(each_node, field_name)

def get_counter_ids(group_id):
    '''
    Fetch all the Counter instances of the exporting Group
    '''
    counter_collection_cur = counter_collection.find({'group_id':ObjectId(group_id)})
    if counter_collection_cur :
        for each_obj in counter_collection_cur :
            dump_node(node=each_obj,collection_name=counter_collection)

class Command(BaseCommand):
    def handle(self, *args, **options):
        global SCHEMA_MAP_PATH
        global DUMP_PATH
        global ROOT_DUMP_NODE_ID
        global ROOT_DUMP_NODE_NAME
        global MULTI_DUMP
        input_name_or_id = raw_input("\n\tPlease enter ObjectID of the Group: ")
        dump_node_obj = node_collection.one({'_id': ObjectId(input_name_or_id)})
        group_node = None

        if dump_node_obj:
            # import ipdb; ipdb.set_trace()
            log_file_path = create_log_file(dump_node_obj._id)
            ROOT_DUMP_NODE_ID = dump_node_obj._id
            ROOT_DUMP_NODE_NAME = dump_node_obj.name

            if dump_node_obj._type == 'Group':
                core_export(dump_node_obj)
                SCHEMA_MAP_PATH = DUMP_PATH
                create_factory_schema_mapper(SCHEMA_MAP_PATH)
            else:
                global DUMP_NODE_objS_LIST
                global TOP_PATH
                datetimestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
                TOP_PATH = os.path.join(GSTUDIO_DATA_ROOT, 'data_export', slugify(dump_node_obj.name) + "_"+ str(datetimestamp))
                SCHEMA_MAP_PATH = TOP_PATH
                UNIT_NAMES = []
                print "\n********REQUEST DUMP NODE IS NOT GROUP.*********\n"
                confirm_non_grp_exp = raw_input("\n\tDo you want to continue? Enter y/n:\t ")
                if confirm_non_grp_exp in ['y', 'Y']:
                    MULTI_DUMP = True
                    # Based on the request dump_node_obj member_of and type fields, query for the field contents.
                    # if "module" in dump_node_obj.member_of_names_list:
                    module_units_cur = node_collection.find({
                                        '_id': {'$in': dump_node_obj.collection_set},
                                        '_type': 'Group'})
                    if module_units_cur.count():
                        print "\nFollowing are the Groups part of request dump. \n\tEnter y/Y to select or any other key to skip the group:\t "
                        for each_unit in module_units_cur:
                            select_grp = raw_input(each_unit.name + "("+ each_unit.member_of_names_list[0]+  ") :\t")
                            if select_grp in ['y', 'Y']:
                                DUMP_NODES_LIST.append(each_unit)
                                UNIT_NAMES.append(each_unit.name)
                        dump_grp_list_confirm = raw_input("\n\n\t\tFollowing are the selected Units to be dumped:\n\t\t\t "+ ','.join(UNIT_NAMES)+"\n\n\t\tEnter y/Y to continue:\t ")
                        if dump_grp_list_confirm in ['y', 'Y']:
                            for each_unit in DUMP_NODES_LIST:
                                core_export(each_unit)
                        else:
                            call_exit()
                        dump_node(node=dump_node_obj,collection_name=node_collection)
                        create_factory_schema_mapper(SCHEMA_MAP_PATH)
            print "*"*70
            print "\n This will take few minutes. Please be patient.\n"
            print "\n Log will be found at: ", log_file_path
            print "*"*70
            log_file.close()
            call_exit()