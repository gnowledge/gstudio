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
from schema_mapping import create_factory_schema_mapper
from users_dump_restore import create_users_dump
from gnowsys_ndf.ndf.models import node_collection, triple_collection, filehive_collection, counter_collection
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.settings import GSTUDIO_DATA_ROOT, GSTUDIO_LOGS_DIR_PATH, MEDIA_ROOT, GSTUDIO_INSTITUTE_ID
from gnowsys_ndf.ndf.views.methods import get_group_name_id
from gnowsys_ndf.ndf.templatetags.simple_filters import get_latest_git_hash, get_active_branch_name

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


def create_log_file(req_log_file_name):
    '''
        Creates log file in gstudio-logs/ with 
        the name of the dump folder
    '''
    log_file_name = req_log_file_name + '.log'
    if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
        os.makedirs(GSTUDIO_LOGS_DIR_PATH)
    log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
    return log_file_path

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
                log_file.write( "\n Error while fetching contributors " + str(no_contributors_err) +\
                 " for: " + str(node._id) + " with contributors: " + str(node.contributors))
                pass
            log_file.write( "\n RCS Built for " + str(node._id))
            copy_rcs(node)
        except Exception as buildRCSError:
            error_log = "\n !!! Error found while Building RCS ."
            error_log += "\nError: " + str(buildRCSError)
            log_file.write( str(error_log))
            print error_log
            pass

def find_file_from_media_url(source_attr):
    try:
        global log_file
        log_file.write( "\n find_file_from_media_url invoked for: " + str(source_attr))

        if "media" in source_attr:
            source_attr = source_attr.split("media/")[-1]
            file_node = node_collection.find_one({"$or": [{'if_file.original.relurl': source_attr},
                {'if_file.mid.relurl': source_attr},{'if_file.thumbnail.relurl': source_attr}]})

        elif "readDoc" in source_attr:
            split_src = source_attr.split('/')
            node_id = split_src[split_src.index('readDoc') + 1]
            file_node = node_collection.one({'_id': ObjectId(node_id)})

        if file_node:
            log_file.write( "\n media file_node gs found:  " + str(file_node._id))
            get_file_node_details(file_node)

    except Exception as find_file_from_media_url_err:
        error_log = "\n !!! Error found while taking dump in find_file_from_media_url() ."
        error_log += "\nError: " + str(find_file_from_media_url_err)
        print "\n Error: ", error_log
        log_file.write( str(error_log))
        print error_log
        pass

def pick_media_from_content(content_soup):
    '''
    Parses through the content of node and finds the media 
    files and dump it
    '''
    try:
        global log_file
        log_file.write( "\n pick_media_from_content invoked.")

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
        log_file.write( str(error_log))
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
            # import ipdb; ipdb.set_trace()                                                                                                                                                                                                                                                                                                                                                                                                                                                               
            path = historyMgr.get_file_path(node)
            path = path + ",v"

            if not os.path.exists(path):
                path = historyMgr.get_file_path(node)
                path = path + ",v"
            # log_file.write( "\n RCS Copied " + str(path)
            cp = "cp  -u " + path + " " +" --parents " + DATA_EXPORT_PATH + "/"
            subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)

        except Exception as copyRCSError:
            error_log = "\n !!! Error found while Copying RCS ."
            error_log += "\nError: " + str(copyRCSError)
            log_file.write( str(error_log))
            print error_log
            pass

def get_counter_ids(group_id=None, group_node=None, user_ids=None):
    '''
    Fetch all the Counter instances of the exporting Group
    '''
    if group_id:
        counter_collection_cur = counter_collection.find({'group_id':ObjectId(group_id)})
    elif group_node:
        counter_collection_cur = counter_collection.find({'group_id':ObjectId(group_node._id)})
    elif user_ids:
        counter_collection_cur = counter_collection.find({'user_id': {'$in': user_ids}})

    if counter_collection_cur :
        for each_obj in counter_collection_cur :
            dump_node(node=each_obj,collection_name=counter_collection, variables_dict=GLOBAL_DICT)


def write_md5_of_dump(group_dump_path, configs_file_path):
    from checksumdir import dirhash
    md5hash = dirhash(group_dump_path, 'md5')
    with open(configs_file_path, 'a+') as configs_file_out:
        configs_file_out.write("\nMD5='" + str(md5hash) + "'")


def dumping_call(node, collection_name):
    try:
        global log_file
        global GROUP_ID
        global DUMPED_NODE_IDS
        log_file.write( "\nDumping Call for : " + str(node))
        print ".",
        build_rcs(node, collection_name)

        if collection_name == node_collection:
            get_triple_data(node._id)
            if 'File' in node.member_of_names_list:
                get_file_node_details(node, exclude_node=True)
        log_file.write( "\n Dump node finished for:  " + str(node._id))

    except Exception as dumping_call_err:
        error_log = "\n !!! Error found in dumping_call_node() ."
        error_log += "\nError: " + str(dumping_call_err)
        log_file.write( str(error_log))
        print error_log
        pass

def update_globals(variables_dict):
    try:
        global GLOBAL_DICT
        global GROUP_CONTRIBUTORS
        global DUMP_PATH
        global TOP_PATH
        global GROUP_ID
        global DATA_EXPORT_PATH
        global MEDIA_EXPORT_PATH
        global RESTORE_USER_DATA
        global SCHEMA_MAP_PATH
        global log_file_path
        global DUMP_NODES_LIST
        global DUMPED_NODE_IDS
        global ROOT_DUMP_NODE_ID
        global ROOT_DUMP_NODE_NAME
        global MULTI_DUMP
        global log_file

        GLOBAL_DICT = variables_dict
        GROUP_CONTRIBUTORS = variables_dict.get("GROUP_CONTRIBUTORS", None)
        DUMP_PATH = variables_dict.get("DUMP_PATH", None)
        TOP_PATH = variables_dict.get("TOP_PATH", None)
        GROUP_ID = variables_dict.get("GROUP_ID", None)
        DATA_EXPORT_PATH = variables_dict.get("DATA_EXPORT_PATH", None)
        MEDIA_EXPORT_PATH = variables_dict.get("MEDIA_EXPORT_PATH", None)
        RESTORE_USER_DATA = variables_dict.get("RESTORE_USER_DATA", None)
        SCHEMA_MAP_PATH = variables_dict.get("SCHEMA_MAP_PATH", None)
        log_file_path = variables_dict.get("log_file_path", None)
        if log_file_path:
            log_file = open(log_file_path, 'a+')
            log_file.write("\n######### Export-Logic entered at : " + str(datetime.datetime.now()) + " #########\n\n")

        DUMP_NODES_LIST = variables_dict.get("DUMP_NODES_LIST", None)
        DUMPED_NODE_IDS = variables_dict.get("DUMPED_NODE_IDS", None)
        ROOT_DUMP_NODE_ID = variables_dict.get("ROOT_DUMP_NODE_ID", None)
        ROOT_DUMP_NODE_NAME = variables_dict.get("ROOT_DUMP_NODE_NAME", None)
        MULTI_DUMP = variables_dict.get("MULTI_DUMP", None)

    except Exception as globals_err:
        print "\n Error in update_globals() in export_logic.py: ", globals_err
        pass

def dump_node(collection_name=node_collection, node=None, node_id=None, node_id_list=None, variables_dict=None):
    '''
    Receives all nodes pertaining to exporting group belonging to all existing collections.
    Calls build_rcs.
    '''
    try:
        if variables_dict:
            update_globals(variables_dict)
        global DATA_EXPORT_PATH
        global MEDIA_EXPORT_PATH
        global log_file
        log_file.write( "\n dump_node invoked for: " + str(collection_name))
        if node:
            dumping_call(node,collection_name)
        elif node_id:
            log_file.write( "\tNode_id : " + str(node_id))
            node = collection_name.one({'_id': ObjectId(node_id), '_type': {'$nin': ['Group', 'Author']}})
            if node:
                dumping_call(node, collection_name)

        elif node_id_list:
            node_cur = collection_name.one({'_id': {'$in': node_id_list}, '_type': {'$nin': ['Group', 'Author']}})
            log_file.write( "\tNode_id_list : " + str(node_id_list))
            for each_node in nodes_cur:
                if each_node:
                    dumping_call(each_node,collection_name)
    except Exception as dump_err:
        error_log = "\n !!! Error found while taking dump in dump_node() ."
        error_log += "\nError: " + str(dump_err)
        log_file.write(str(error_log))
        print error_log
        pass

def dump_media_data(media_path):
    # Copy media file to /data/media location
    # print MEDIA_EXPORT_PATH
    global log_file
    log_file.write( "\n--- Media Copying in process --- "+ str(media_path))
    try:
        if media_path:
            fp = os.path.join(MEDIA_ROOT,media_path)
            if os.path.exists(fp):
                cp = "cp  -u " + fp + " " +" --parents " + MEDIA_EXPORT_PATH + "/"
                subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
                log_file.write( "\n Media Copied:  " + str(fp))

            else:
                log_file.write( "\n Media NOT Copied:  " + str(fp))
        else:
            log_file.write( "\n No MediaPath found:  " + str(media_path))
    except Exception as dumpMediaError:
        error_log = "\n !!! Error found while taking dump of Media.\n" +  str(media_path)
        error_log += "\nError: " + str(dumpMediaError)
        log_file.write( str(error_log))
        print error_log
        pass

def get_triple_data(node_id):
    '''
    Gets all data stored in triples for this node.
    Fetches GAttrtibutes as wells as GRelations.
    '''
    try:
        global log_file
        log_file.write( "\n get_triple_data invoked for: " + str(node_id))

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
                log_file.write( "\n fetch_value: " + str(fetch_value))
                if fetch_value == "right_subject":
                    log_file.write( "\n Picking up right-subject nodes.\n\t " + str(each_triple_node[fetch_value]))

                    if type(each_triple_node[fetch_value]) == list and all(isinstance(each_obj_value, ObjectId) for each_obj_value in each_triple_node[fetch_value]):
                        log_file.write( "\n List:  " + str(True))
                        dump_node(node_id_list=each_triple_node[fetch_value],
                            collection_name=node_collection)

                    elif isinstance(each_triple_node[fetch_value], ObjectId):
                        log_file.write( "\n ObjectId:  " + str(True))
                        dump_node(node_id=each_triple_node[fetch_value],
                                collection_name=node_collection)

        log_file.write( "\n get_triple_data finished for: " + str(node_id))

    except Exception as get_triple_data_err:
        error_log = "\n !!! Error found while taking triple data in get_triple_data() ."
        error_log += "\nError: " + str(get_triple_data_err)
        print "\n Error: ", error_log
        log_file.write( str(error_log))
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
        log_file.write( "\n get_file_node_details invoked for: " + str(node))
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
        log_file.write( str(error_log))
        print error_log
        pass

