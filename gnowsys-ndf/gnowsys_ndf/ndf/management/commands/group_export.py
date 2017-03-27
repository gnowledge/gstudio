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

def create_log_file(group_name):
    log_file_name = 'group_dump_' + str(group_name)+ '.log'
    if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
        os.makedirs(GSTUDIO_LOGS_DIR_PATH)

    log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
    # print log_file_path
    global log_file
    log_file = open(log_file_path, 'w+')
    log_file.write("######### Script ran on : " + str(datetime.datetime.now()) + " #########\n\n")

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


def get_triple_data(node_id, node_triple_set, is_triple_rt):
    # node_triple_set can be node.attribute_set OR
    # node.relation_set
    if is_triple_rt:
        rt_at_query = {"_type": "RelationType"}
        triple_query = {"_type": "GRelation", "subject": node_id}
        fetch_value = 'right_subject'
    else:
        rt_at_query = {"_type": "AttributeType"}
        triple_query = {"_type": "GAttribute", "subject": node_id}
        fetch_value = 'object_value'
    for each_triple_val in node_triple_set:
        if each_triple_val:
            each_triple_val_name = each_triple_val.keys()[0]
            # print "\neach_triple_val_name: ", each_triple_val_name
            if each_triple_val_name:
                rt_at_query.update({"name": unicode(each_triple_val_name)})
                rt_at_node = node_collection.one(rt_at_query)
                if rt_at_node:
                    if is_triple_rt:
                        triple_query.update({"relation_type": rt_at_node._id})
                    else:
                        triple_query.update({"attribute_type": rt_at_node._id})

                    triple_node = triple_collection.find(triple_query)
                    if triple_node:
                        for each_triple_node in triple_node:
                            triple_collection_ids.add(each_triple_node._id)
                            # Get ObjectIds in object_value fields
                            if type(each_triple_node[fetch_value]) == list and all(isinstance(each_obj_value, ObjectId) for each_obj_value in each_triple_node[fetch_value]):
                                node_collection_ids.extend(each_triple_node[fetch_value])
                            elif isinstance(each_triple_node[fetch_value], ObjectId):
                                node_collection_ids.add(each_triple_node[fetch_value])

class Command(BaseCommand):
    def handle(self, *args, **options):
        group_id = raw_input("Please enter group id:\t")
        group_node = node_collection.one({"_type":"Group","_id":ObjectId(group_id)})
        if group_node:
            print "\n Initializing Dump of : ", group_node.name
            group_dump_path = setup_dump_path(group_node.name)
            create_factory_schema_mapper(group_dump_path)
            nodes_falling_under_grp = node_collection.find({"group_set":ObjectId(group_node._id)})
            print "\n Export will be found at: ", data_export_path
            print "\n Total GSystem objects found: ", nodes_falling_under_grp.count()
            confirm_export = raw_input("Do you want to continue? Enter y/n:\t ")
            if confirm_export == 'y' or confirm_export == 'Y':
                print "*"*70
                print "\n This will take few minutes. Please be patient.\n"
                print "*"*70
                for each_node in nodes_falling_under_grp:
                    print ".",
                    node_collection_ids.add(each_node._id)
                    if 'File' in each_node.member_of_names_list:
                        get_file_node_details(each_node)

                    if each_node.collection_set:
                        get_nested_ids(each_node,'collection_set')

                    if each_node.prior_node:
                        get_nested_ids(each_node,'prior_node')

                    if each_node.post_node:
                        get_nested_ids(each_node,'post_node')

                    if each_node.attribute_set:
                        #fetch attribute_type
                        get_triple_data(node_id=each_node._id, node_triple_set=each_node.attribute_set,is_triple_rt=False)
                    if each_node.relation_set:
                        get_triple_data(node_id=each_node._id, node_triple_set=each_node.relation_set,is_triple_rt=True)

                initiate_dump()
            create_log_file(group_node.name)
            log_file.write("\n*************************************************************")
            log_file.write("\n\nTotal Migrations Expected: "+ str(len(node_collection_ids) + len(triple_collection_ids) + len(filehives_collection_ids) + len(filehives_media_urls) + len(counter_collection_ids)))

            log_file.write("\n*************************************************************")
            log_file.write("Nodes Migrations Expected: "+ str(len(node_collection_ids)))
            log_file.write("Triple Migrations Expected: "+ str(len(triple_collection_ids)))
            log_file.write("Filehives Migrations Expected: "+ str(len(filehives_collection_ids)))
            log_file.write("File Media Migrations Expected: "+ str(len(filehives_media_urls)))
            log_file.write("Counters Migrations Expected: "+ str(len(counter_collection_ids)))

            log_file.write("\n*************************************************************")
            log_file.write("Successful Migrations: "+ str(len(rcs_paths_found)))
            log_file.write("Unsuccessful Migrations: "+ str(len(build_rcs)))

            log_file.write("\n*************************************************************")
            log_file.write("Successful Media Migrations: " + str(len(media_url_found)))
            log_file.write("Unsuccessful Media Migrations: " + str(len(media_url_not_found)))

            log_file.write("\n*************************************************************")
            log_file.write("Details of RCS Paths Not Found: " + str(build_rcs))
            log_file.write("\n*************************************************************")
            log_file.write("Details of Media Paths Not Found: " + str(media_url_not_found))
            log_file.write("######### Script Completed at : " + str(datetime.datetime.now()) + " #########\n\n")

        else:
            print "\n Please enter a Valid ObjectId."



def initiate_dump():
    try:
        # rcs of Nodes collection
        print "*"*90
        print "\n--- Dump Inititated for Nodes --- "
        print "*"*90
        dump_node_ids(node_collection_ids,'node_collection', num_of_processes=multiprocessing.cpu_count())

        # rcs of Triples collection
        print "*"*90
        print "\n--- Dump Inititated for Triples --- "
        print "*"*90
        dump_node_ids(triple_collection_ids,'triple_collection', num_of_processes=multiprocessing.cpu_count())

        # rcs of Filehives collection
        print "*"*90
        print "\n--- Dump Inititated for Filehives --- "
        print "*"*90
        dump_node_ids(filehives_collection_ids,'filehive_collection', num_of_processes=multiprocessing.cpu_count())

        # rcs of Counter collection
        print "*"*90
        print "\n--- Dump Inititated for Counters --- "
        print "*"*90
        get_counter_ids(group_node._id)
        dump_node_ids(counter_collection_ids,'counter_collection', num_of_processes=multiprocessing.cpu_count())


        dump_media_data()
    except Exception as dump_err:
        error_log = "\n !!! Error found while taking dump in initiate_dump() ."
        error_log =+ "\nError: " + str(dump_err)
        log_file.write(error_log)
        print error_log
        pass

def dump_media_data():
    # Copy media file to /data/media location
    print "*"*90
    print "\n--- Dump Inititated for Filehives Media --- "
    print "*"*90

    print media_export_path

    try:
        for each_file_media_url in filehives_media_urls:
            # import ipdb;ipdb.set_trace()
            fp = os.path.join(MEDIA_ROOT,each_file_media_url)
            if os.path.exists(fp):
                cp = "cp  -u " + fp + " " +" --parents " + media_export_path + "/"
                subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
                media_url_found.add(fp)
            else:
                media_url_not_found.add(fp)
    except Exception as dumpMediaError:
        error_log = "\n !!! Error found while taking dump of Media.\n" +  str(each_file_media_url)
        error_log =+ "\nError: " + str(dumpMediaError)
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
    for each_field,each_value in node.items():
        if each_field =='if_file':
            filehives_collection_ids.add(each_value['original']['id'])
            filehives_collection_ids.add(each_value['mid']['id'])
            filehives_collection_ids.add(each_value['thumbnail']['id'])
            filehives_media_urls.add(each_value['original']['relurl'])
            filehives_media_urls.add(each_value['mid']['relurl'])
            filehives_media_urls.add(each_value['thumbnail']['relurl'])

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
            node_collection_ids.add(each_id)
            each_node = node_collection.one({"_id":ObjectId(each_id)})
            if each_node and each_node[field_name]:
                get_nested_ids(each_node, field_name)

def get_counter_ids(group_id) :
    counter_collection_cur = counter_collection.find({'group_id':ObjectId(group_id)})
    if counter_collection_cur :
        for each_obj in counter_collection_cur :
            counter_collection_ids.add(each_obj._id)

def dump_node_ids(list_of_ids,collection_name, num_of_processes=4):
    def worker(list_of_ids, out_q):
        for each_id_of_list in list_of_ids:
            try:
                if isinstance(each_id_of_list, ObjectId):
                    each_node_by_id = None
                    if collection_name == "node_collection":
                        each_node_by_id = node_collection.find_one({"_id":ObjectId(each_id_of_list)})
                        each_node_by_id.save()
                    elif collection_name == "triple_collection":
                        each_node_by_id = triple_collection.find_one({"_id":ObjectId(each_id_of_list)})
                        if 'attribute_type' in each_node_by_id:
                            triple_node_RT_AT = node_collection.one({'_id': each_node_by_id.attribute_type})
                        else:
                            triple_node_RT_AT = node_collection.one({'_id': each_node_by_id.relation_type})
                        # import ipdb; ipdb.set_trace()
                        each_node_by_id.save(triple_node=triple_node_RT_AT, triple_id=triple_node_RT_AT._id)
                    elif collection_name == "filehive_collection":
                        each_node_by_id = filehive_collection.find_one({"_id":ObjectId(each_id_of_list)})
                        each_node_by_id.save()
                    elif collection_name == "counter_collection":
                        each_node_by_id = counter_collection.find_one({"_id":ObjectId(each_id_of_list)})
                        each_node_by_id.save()
                    if each_node_by_id:
                        # To update RCS
                        path = historyMgr.get_file_path(each_node_by_id)
                        path = path + ",v"

                        if not os.path.exists(path):
                            path = historyMgr.get_file_path(each_node_by_id)
                            path = path + ",v"
                            build_rcs.add(path)
                        cp = "cp  -vu " + path + " " +" --parents " + data_export_path + "/"
                        subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
                        rcs_paths_found.add(path)
            except Exception as dumpError:
                error_log = "\n !!! Error while taking dump !!! " + str(each_id_of_list)
                error_log =+ "\nError: " + str(error_log)
                log_file.write(error_log)
                print error_log
                pass
        # out_q.put(list_of_ids)

    # Each process will get 'chunksize' student_cur and a queue to put his out
    # dict into
    out_q = multiprocessing.Queue()
    chunksize = int(math.ceil(len(list_of_ids) / float(num_of_processes)))
    procs = []

    for i in range(num_of_processes):
        p = multiprocessing.Process(
            target=worker,
            args=(list_of_ids[chunksize * i:chunksize * (i + 1)], out_q)
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
