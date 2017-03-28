import os
import datetime
import subprocess
import multiprocessing
import math
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.ndf.models import node_collection, triple_collection, filehive_collection, counter_collection
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.settings import GSTUDIO_DATA_ROOT, GSTUDIO_LOGS_DIR_PATH, MEDIA_ROOT
from schema_mapping import create_factory_schema_mapper


node_collection_ids = set()
triple_collection_ids = set()
filehives_collection_ids = set()
counter_collection_ids = set()
filehives_media_urls = set()
build_rcs = set()
rcs_paths_found = set()
media_url_not_found = set()
media_url_found = set()
historyMgr = HistoryManager()
data_export_path = None
media_export_path = None
log_file = None

def create_log_file(dump_path):
    dump_path = dump_path.split("/")[-1]
    log_file_name = 'group_dump_' + str(dump_path)+ '.log'
    if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
        os.makedirs(GSTUDIO_LOGS_DIR_PATH)

    log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
    # print log_file_path
    global log_file
    log_file = open(log_file_path, 'w+')
    log_file.write("\n######### Script ran on : " + str(datetime.datetime.now()) + " #########\n\n")
    return log_file_path

def setup_dump_path(group_name):
    '''
        Creates factory_schema.json which will hold basic info
        like ObjectId, name, type of TYPES_LIST and GSTUDIO_DEFAULT_GROUPS
    '''
    global data_export_path
    global media_export_path
    datetimestamp = datetime.datetime.now().isoformat()
    data_export_path = os.path.join(GSTUDIO_DATA_ROOT, 'data_export', group_name + "_" + str(datetimestamp))
    media_export_path = os.path.join(data_export_path, 'media_files')
    if not os.path.exists(data_export_path):
        os.makedirs(data_export_path)
    if not os.path.exists(media_export_path):
        os.makedirs(media_export_path)
    return data_export_path


def get_triple_data(node_id):

    triple_query = {"_type": {'$in': ["GAttribute", "GRelation"]}, "subject": node_id}

    node_gattr_grel_cur = triple_collection.find(triple_query)
    fetch_value = None
    if node_gattr_grel_cur:

        for each_triple_node in node_gattr_grel_cur:
            dump_node(node=each_triple_node,
                collection_name=triple_collection)
            # Get ObjectIds in object_value fields
            if each_triple_node._type is "GAttribute":
                fetch_value = "object_value"
            elif each_triple_node._type is "GRelation":
                fetch_value = "right_subject"
            if fetch_value:
                print "\n fetch_value -- ", fetch_value
                if type(each_triple_node[fetch_value]) == list and all(isinstance(each_obj_value, ObjectId) for each_obj_value in each_triple_node[fetch_value]):
                    dump_node(node_id_list=each_triple_node[fetch_value],
                        collection_name=node_collection)
                elif isinstance(each_triple_node[fetch_value], ObjectId):
                    dump_node(node_id=each_triple_node[fetch_value],
                            collection_name=node_collection)


class Command(BaseCommand):
    def handle(self, *args, **options):
        group_id = raw_input("Please enter group id:\t")
        group_node = node_collection.one({"_type":"Group","_id":ObjectId(group_id)})
        if group_node:
            print "\tRequest received for Export of : ", group_node.name
            nodes_falling_under_grp = node_collection.find({"group_set":ObjectId(group_node._id)})
            print "\n\tTotal GSystem objects found: ", nodes_falling_under_grp.count()
            confirm_export = raw_input("\n\tDo you want to continue? Enter y/n:\t ")
            if confirm_export == 'y' or confirm_export == 'Y':
                print "START : ", str(datetime.datetime.now())
                group_dump_path = setup_dump_path(group_node.name)
                create_factory_schema_mapper(group_dump_path)
                log_file_path = create_log_file(group_dump_path)

                print "*"*70
                print "\n Export will be found at: ", data_export_path
                print "\n Log will be found at: ", log_file_path

                print "\n This will take few minutes. Please be patient.\n"
                print "*"*70
                # import ipdb; ipdb.set_trace()

                call_group_export(nodes_falling_under_grp, num_of_processes=multiprocessing.cpu_count())
                get_counter_ids(group_id)
                # dump_media_data()
            global log_file
            log_file.write("\n*************************************************************")
            log_file.write("\n######### Script Completed at : " + str(datetime.datetime.now()) + " #########\n\n")
            print "END : ", str(datetime.datetime.now())

        else:
            print "\n Enter a valid ObjectId"


def call_group_export(nodes_cur, num_of_processes=4):
    nodes_cur = list(nodes_cur)
    def worker(nodes_cur, out_q):
        for each_node in nodes_cur:
            print ".",
            dump_node(node=each_node,collection_name=node_collection)
            # node_collection_ids.add(each_node._id)
            if 'File' in each_node.member_of_names_list:
                get_file_node_details(each_node)

            if each_node.collection_set:
                get_nested_ids(each_node,'collection_set')

            if each_node.prior_node:
                get_nested_ids(each_node,'prior_node')

            if each_node.post_node:
                get_nested_ids(each_node,'post_node')

            #fetch triple_data
            get_triple_data(each_node._id)
    # Each process will get 'chunksize' student_cur and a queue to put his out
    # dict into
    out_q = multiprocessing.Queue()
    chunksize = int(math.ceil(len(nodes_cur) / float(num_of_processes)))
    procs = []

    for i in range(num_of_processes):
        p = multiprocessing.Process(
            target=worker,
            args=(nodes_cur[chunksize * i:chunksize * (i + 1)], out_q)
        )
        procs.append(p)
        p.start()

    # Collect all results into a single result list. We know how many lists
    # with results to expect.
    # resultlist = []
    # for i in range(num_of_processes):
    #     resultlist.extend(out_q.get())

    # Wait for all worker processes to finish
    for p in procs:
        p.join()

    # return resultlist

def build_rcs(node, collection_name):
    if node:
        global log_file
        if collection_name is triple_collection:
            if 'attribute_type' in node:
                triple_node_RT_AT = node_collection.one({'_id': node.attribute_type})
            elif 'relation_type' in node:
                triple_node_RT_AT = node_collection.one({'_id': node.relation_type})
            node.save(triple_node=triple_node_RT_AT, triple_id=triple_node_RT_AT._id)
        else:
            node.save()
        log_file.write("\n RCS Built for " + str(node._id) )
        copy_rcs(node)

def copy_rcs(node):

    if node:
        global log_file
        try:
            # To update RCS
            path = historyMgr.get_file_path(node)
            path = path + ",v"

            if not os.path.exists(path):
                path = historyMgr.get_file_path(node)
                path = path + ",v"
                build_rcs.add(path)
            cp = "cp  -vu " + path + " " +" --parents " + data_export_path + "/"
            subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
            log_file.write("\n RCS Copied " + str(path) )

        except Exception as copyRCSError:
            error_log = "\n !!! Error found while Copying RCS ."
            error_log += "\nError: " + str(copyRCSError)
            log_file.write(error_log)
            print error_log
            pass


def dump_node(collection_name=node_collection, node=None, node_id=None, node_id_list=None):
    try:
        global log_file
        log_file.write("\n dump_node invoked for: " + str(collection_name))
        if node:
            log_file.write("\tNode: " + str(node))
            build_rcs(node, collection_name)
            log_file.write("\n dump node finished for:  " + str(node._id) )
        elif node_id:
            log_file.write("\tNode_id : " + str(node_id))
            node = collection_name.one({'_id': ObjectId(node_id)})
            build_rcs(node, collection_name)
            log_file.write("\n dump node finished for:  " + str(node._id) )
        elif node_id_list:
            node_cur = collection_name.one({'_id': {'$in': node_id_list}})
            log_file.write("\tNode_id_list : " + str(node_id_list))
            for each_node in nodes_cur:
                build_rcs(node, collection_name)
                log_file.write("\n dump node finished for:  " + str(node._id) )

    except Exception as dump_err:
        error_log = "\n !!! Error found while taking dump in dump_node() ."
        error_log += "\nError: " + str(dump_err)
        log_file.write(error_log)
        print error_log
        pass

def dump_media_data(media_path):
    # Copy media file to /data/media location
    print "\n--- Copying Inititated for Filehives Media --- "
    # print media_export_path
    global log_file
    try:
        print "\n each_file_media_url: ", media_path
        fp = os.path.join(MEDIA_ROOT,media_path)
        if os.path.exists(fp):
            cp = "cp  -u " + fp + " " +" --parents " + media_export_path + "/"
            subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
            media_url_found.add(fp)
            log_file.write("\n Media Copied:  " + str(fp) )

        else:
            log_file.write("\n Media NOT Copied:  " + str(fp) )
            media_url_not_found.add(fp)
    except Exception as dumpMediaError:
        error_log = "\n !!! Error found while taking dump of Media.\n" +  str(media_path)
        error_log += "\nError: " + str(dumpMediaError)
        log_file.write(error_log)
        print error_log
        pass

def get_file_node_details(node):
    '''
    Check if_file field and update filehives_collection_ids list
    'if_file': {
                    'mime_type': basestring,
                    'original': {'id': ObjectId, 'relurl': basestring},
                    'mid': {'id': ObjectId, 'relurl': basestring},
                    'thumbnail': {'id': ObjectId, 'relurl': basestring}
                },

    '''
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

def get_nested_ids(node,field_name):
    if node[field_name]:
        for each_id in node[field_name]:
            each_node = node_collection.one({"_id":ObjectId(each_id)})
            dump_node(node=each_node, collection_name=node_collection)
            if each_node and each_node[field_name]:
                get_nested_ids(each_node, field_name)

def get_counter_ids(group_id) :
    counter_collection_cur = counter_collection.find({'group_id':ObjectId(group_id)})
    if counter_collection_cur :
        for each_obj in counter_collection_cur :
            dump_node(node=each_obj,collection_name="counter_collection")
