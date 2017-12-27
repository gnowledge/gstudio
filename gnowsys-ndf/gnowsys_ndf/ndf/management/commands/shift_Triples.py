''' -- imports from python libraries -- '''
import os
import shutil
import json
import bson
import time
import datetime
from pymongo import ASCENDING

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import db, Node, Triple, HistoryManager, RCS, AttributeType, RelationType

####################################################################################################################

SCHEMA_ROOT = os.path.join(os.path.dirname(__file__), "schema_files")

log_list = []  # To hold intermediate errors
info_message = "\n######### Script run on : " + time.strftime("%c") + " #########\n############################################################"
log_list.append(info_message)
print info_message


class Command(BaseCommand):
    help = "Based on "

    def handle(self, *args, **options):
        try:
            triple_collection_name = Triple.collection_name
            node_collection_name = Node.collection_name
            
            if triple_collection_name not in db.collection_names():
                try:
                    # [A] Create Triples collection
                    info_message = "\n\n  Creating new collection named as \"" + triple_collection_name + "\"..."
                    print info_message
                    log_list.append(info_message)

                    db.create_collection(triple_collection_name)

                    info_message = "\n\tCollection (" + triple_collection_name + ") created successfully."
                    print info_message
                    log_list.append(info_message)

                    info_message = "\n==================================================================================================="
                    print info_message
                    log_list.append(info_message)
                except Exception as e:
                    error_message = "\n  Collection (" + triple_collection_name + ") NOT created as following error occurred: " + str(e)
                    print error_message
                    log_list.append(error_message)
                    return

            # Fetch "Nodes" collection
            node_collection = db[node_collection_name].Node

            # Fetch newly created "Triples" collection
            triple_collection = db[triple_collection_name].Triple

            info_message = "\n\n  Before shifting document(s) from " + node_collection_name + " collection into " + triple_collection_name + " collection: "
            print info_message

            gattribute_cur = node_collection.find({"_type": "GAttribute"})
            gattribute_cur_count = gattribute_cur.count()
            info_message = "\n\n\tNo. of GAttribute node(s) found in " + node_collection_name + " collection: " + str(gattribute_cur_count)
            print info_message
            log_list.append(info_message)

            grelation_cur = node_collection.find({"_type": "GRelation"})
            grelation_cur_count = grelation_cur.count()
            info_message = "\n\tNo. of GRelation node(s) found in " + node_collection_name + " collection: " + str(grelation_cur_count)
            print info_message
            log_list.append(info_message)

            if gattribute_cur.count() == 0 and grelation_cur.count() == 0:
                info_message = "\n\n  No records found in " + node_collection_name + " collection to be shifted into " + triple_collection_name + " collection."
                print info_message
                log_list.append(info_message)
                # info_message = "\n\n  Triples collection already created and indexes, too, set on it."
                # print info_message
                # log_list.append(info_message)

                # info_message = "\n\tExisting index information on \"" + triple_collection_name + "\" collection is as follows:" + \
                #     "\n" + json.dumps(triple_collection.index_information(), indent=2, sort_keys=False)
                # print info_message
                # log_list.append(info_message)

            else:
                gtattribute_cur = triple_collection.find({"_type": "GAttribute"})
                gtattribute_cur_count = gtattribute_cur.count()
                info_message = "\n\n\tNo. of GAttribute node(s) found in " + triple_collection_name + " collection: " + str(gtattribute_cur_count)
                print info_message
                log_list.append(info_message)

                gtrelation_cur = triple_collection.find({"_type": "GRelation"})
                gtrelation_cur_count = gtrelation_cur.count()
                info_message = "\n\tNo. of GRelation node(s) found in " + triple_collection_name + " collection: " + str(gtrelation_cur_count)
                print info_message

                info_message = "\n==================================================================================================="
                print info_message
                log_list.append(info_message)

                info_message = "\n\n  Existing index information on \"" + triple_collection_name + "\" collection are as follows:" + \
                    "\n" + json.dumps(triple_collection.collection.index_information(), indent=4, sort_keys=False)
                print info_message
                log_list.append(info_message)

                # [B] Creating following indexes for "Triples" collection
                info_message = "\n\n\tCreating following indexes for \"" + triple_collection_name + "\" collection..." + \
                    "\n\t\t1. _type(1) >> subject(1) >> attribute_type.$id(1) >> status(1)" + \
                    "\n\t\t2. _type(1) >> subject(1) >> relation_type.$id(1) >> status(1) >> right_subject(1)" + \
                    "\n\t\t3. _type(1) >> right_subject(1) >> relation_type.$id(1) >> status(1)"
                print info_message
                log_list.append(info_message)

                # 1. _type(1) >> subject(1) >> attribute_type.$id(1) >> status(1)
                index_val = triple_collection.collection.ensure_index([("_type", ASCENDING), ("subject", ASCENDING), ("attribute_type.$id", ASCENDING), ("status", ASCENDING)])
                if index_val:
                    info_message = "\n\n\t" + str(index_val) + " index created for " + str(triple_collection_name) + " collection successfully."
                else:
                    info_message = "\n\n\t_type_1_subject_1_attribute_type.$id_1_status_1 index already created for " + str(triple_collection_name) + " collection."
                print info_message
                log_list.append(info_message)

                # 2. _type(1) >> subject(1) >> relation_type.$id(1) >> status(1) >> right_subject(1)
                index_val = triple_collection.collection.ensure_index([("_type", ASCENDING), ("subject", ASCENDING), ("relation_type.$id", ASCENDING), ("status", ASCENDING), ("right_subject", ASCENDING)])
                if index_val:
                    info_message = "\n\t" + str(index_val) + " index created for " + str(triple_collection_name) + " collection successfully."
                else:
                    info_message = "\n\t_type_1_subject_1_relation_type.$id_1_status_1_right_subject_1 index already created for " + str(triple_collection_name) + " collection."
                print info_message
                log_list.append(info_message)

                # 3. _type(1) >> right_subject(1) >> relation_type.$id(1) >> status(1)
                index_val = triple_collection.collection.ensure_index([("_type", ASCENDING), ("right_subject", ASCENDING), ("relation_type.$id", ASCENDING), ("status", ASCENDING)])
                if index_val:
                    info_message = "\n\t" + str(index_val) + " index created for " + str(triple_collection_name) + " collection successfully."
                else:
                    info_message = "\n\t_type_1_subject_1_relation_type.$id_1_status_1_right_subject_1 index already created for " + str(triple_collection_name) + " collection."
                print info_message
                log_list.append(info_message)

                info_message = "\n\n  Modified index information on \"" + triple_collection_name + "\" collection are as follows:" + \
                    "\n" + json.dumps(triple_collection.collection.index_information(), indent=4, sort_keys=False)
                print info_message
                log_list.append(info_message)

                info_message = "\n==================================================================================================="
                print info_message
                log_list.append(info_message)

                # [C] Move GAttribute & GRelation nodes from Nodes collection to Triples collection
                info_message = "\n\n  Moving GAttribute (" + str(gattribute_cur_count) + ") & GRelation (" + str(grelation_cur_count) + ") node(s) from Nodes collection to Triples collection..." + \
                    "\n  THIS MAY TAKE MORE TIME DEPENDING UPON HOW MUCH DATA YOU HAVE.. SO PLEASE HAVE PATIENCE !"
                print info_message
                log_list.append(info_message)

                bulk_insert = triple_collection.collection.initialize_unordered_bulk_op()
                bulk_remove = node_collection.collection.initialize_unordered_bulk_op()

                triple_cur = node_collection.find({"_type": {"$in": ["GAttribute", "GRelation"]}}, timeout=False)
                delete_nodes = []
                hm = HistoryManager()
                rcs_obj = RCS()
                existing_rcs_file = []
                newly_created_rcs_file = []
                at_rt_updated_node_list = []

                tf1 = time.time()
                for i, doc in enumerate(triple_cur):
                    info_message = "\n\n\tChecking attribute_type & relation_type fields of # " + str((i+1)) + " record :-"
                    print info_message
                    log_list.append(info_message)

                    if doc["_type"] == "GAttribute":
                        if (type(doc["attribute_type"]) != bson.dbref.DBRef) and ( (type(doc["attribute_type"]) == dict) or (type(doc["attribute_type"]) == AttributeType) ):
                            doc["attribute_type"] = node_collection.collection.AttributeType(doc["attribute_type"]).get_dbref()
                            at_rt_updated_node_list.append(str(doc._id))
                            info_message = "\n\tattribute_type field updated for # " + str((i+1)) + " record."
                            print info_message
                            log_list.append(info_message)

                    elif doc["_type"] == "GRelation":
                        if (type(doc["relation_type"]) != bson.dbref.DBRef) and ( (type(doc["relation_type"]) == dict) or (type(doc["relation_type"]) == RelationType) ):
                            doc["relation_type"] = node_collection.collection.RelationType(doc["relation_type"]).get_dbref()
                            at_rt_updated_node_list.append(str(doc._id))
                            info_message = "\n\trelation_type field updated for # " + str((i+1)) + " record."
                            print info_message
                            log_list.append(info_message)

                    delete_nodes.append(doc._id)

                    bulk_insert.insert(doc)

                    try:
                        node_rcs_file = hm.get_file_path(doc)

                        # As we have changed collection-name for Triple from Nodes to Triples
                        # Hence, we need to first replace Triples with Nodes
                        # In order to move rcs-files from Nodes into Triples directory
                        node_rcs_file = node_rcs_file.replace(triple_collection_name, node_collection_name)
                        info_message = "\n\n\tMoving # " + str((i+1)) + " Node rcs-file (" + node_rcs_file + ")..."
                        print info_message
                        log_list.append(info_message)

                        if os.path.exists(node_rcs_file + ",v"):
                            node_rcs_file = node_rcs_file + ",v"
                        elif os.path.exists(node_rcs_file):
                            node_rcs_file = node_rcs_file

                        info_message = "\n\t  node_rcs_file (json/,v) : " + node_rcs_file
                        print info_message
                        log_list.append(info_message)

                        # If exists copy to Triples directory
                        # Then delete it
                        if node_rcs_file[-2:] == ",v" and os.path.isfile(node_rcs_file):
                            info_message = "\n\t  File FOUND : " + node_rcs_file
                            print info_message
                            log_list.append(info_message)

                            # Replacing Node collection-name (Nodes) with Triple collection-name (Triples)
                            triple_rcs_file = node_rcs_file.replace(node_collection_name, triple_collection_name)
                            info_message = "\n\t  triple_rcs_file : " + triple_rcs_file
                            print info_message
                            log_list.append(info_message)

                            triple_dir_path = os.path.dirname(triple_rcs_file)
                            info_message = "\n\t  triple_dir_path : " + triple_dir_path
                            print info_message
                            log_list.append(info_message)

                            if not os.path.isdir(triple_dir_path):
                                # Creates required directory path for Triples collection in rcs-repo
                                os.makedirs(triple_dir_path)

                                info_message = "\n\t  CREATED PATH : " + triple_dir_path
                                print info_message
                                log_list.append(info_message)

                            # Copy files keeping metadata intact
                            shutil.copy2(node_rcs_file, triple_rcs_file)
                            info_message = "\n\t  COPIED TO : " + triple_rcs_file
                            print info_message
                            log_list.append(info_message)

                            # Deleting file from Nodes directory
                            os.remove(node_rcs_file)
                            info_message = "\n\t  DELETED : " + node_rcs_file
                            print info_message
                            log_list.append(info_message)

                            # Append to list to keep track of those Triple nodes
                            # for which corresponding rcs-file exists
                            existing_rcs_file.append(str(doc._id))

                        else:
                            error_message = "\n\t  Version-File (.json,v) NOT FOUND : " + node_rcs_file + " !!!"
                            print error_message
                            log_list.append(error_message)

                            if hm.create_or_replace_json_file(doc):
                                fp = hm.get_file_path(doc)
                                message = "This document (" + doc.name + ") is shifted (newly created) from Nodes collection to Triples collection on " + datetime.datetime.now().strftime("%d %B %Y")
                                rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

                                if os.path.isdir(os.path.dirname(fp)):
                                    # Append to list to keep track of those Triple nodes
                                    # for which corresponding rcs-file doesn't exists
                                    newly_created_rcs_file.append(str(doc._id))

                                    info_message = "\n\t  CREATED rcs-file : " + fp
                                    print info_message
                                    log_list.append(info_message)

                    except OSError as ose:
                        error_message = "\n\t  OSError (" + node_rcs_file + ") : " + str(ose) + " !!!"
                        print error_message
                        log_list.append(error_message)
                        continue

                    except Exception as e:
                        error_message = "\n\t  Exception (" + node_rcs_file + ") : " + str(e) + " !!!"
                        print error_message
                        log_list.append(error_message)
                        continue

                tf2 = time.time()
                info_message = "\n\n\tTime taken by for loop (list) : " + str(tf2 - tf1) + " secs"
                print info_message
                log_list.append(info_message)

                t1 = time.time()
                bulk_insert.execute()
                t2 = time.time()
                info_message = "\n\tTime taken to copy given no. of Triple's docmuents : " + str(t2 - t1) + " secs"
                print info_message
                log_list.append(info_message)

                t3 = time.time()
                bulk_remove.find({"_id": {"$in": delete_nodes}}).remove()
                bulk_remove.execute()
                t4 = time.time()
                info_message = "\n\tTime taken to delete given no. of Triple's docmuents () : " + str(t4 - t3) + " secs"
                print info_message
                log_list.append(info_message)

                info_message = "\n==================================================================================================="
                print info_message
                log_list.append(info_message)

                info_message = "\n\n  After shifting document(s) from " + node_collection_name + " collection into " + triple_collection_name + " collection: "
                print info_message
                log_list.append(info_message)

                # Entries in Nodes collection
                gattribute_cur = node_collection.find({"_type": "GAttribute"})
                gattribute_cur_count = gattribute_cur.count()
                info_message = "\n\n\tNo. of GAttribute node(s) found in " + node_collection_name + " collection: " + str(gattribute_cur_count)
                print info_message
                log_list.append(info_message)

                grelation_cur = node_collection.find({"_type": "GRelation"})
                grelation_cur_count = grelation_cur.count()
                info_message = "\n\tNo. of GRelation node(s) found in " + node_collection_name + " collection: " + str(grelation_cur_count)
                print info_message
                log_list.append(info_message)

                # Entries in Triples collection
                gtattribute_cur = triple_collection.find({"_type": "GAttribute"})
                gtattribute_cur_count = gtattribute_cur.count()
                info_message = "\n\n\tNo. of GAttribute node(s) found in " + triple_collection_name + " collection: " + str(gtattribute_cur_count)
                print info_message
                log_list.append(info_message)

                gtrelation_cur = triple_collection.find({"_type": "GRelation"})
                gtrelation_cur_count = gtrelation_cur.count()
                info_message = "\n\tNo. of GRelation node(s) found in " + triple_collection_name + " collection: " + str(gtrelation_cur_count)
                print info_message
                log_list.append(info_message)

                # Information about attribute_type & relation_type fields updated
                info_message = "\n\n\tNo. of node(s) (# " + str(len(at_rt_updated_node_list)) + ") whose attribute_type & relation_type fields are updated: \n" + str(at_rt_updated_node_list)
                print info_message
                log_list.append(info_message)

                # Information about RCS files
                info_message = "\n\n\tRCS file(s) moved for follwoing node(s) (# " + str(len(existing_rcs_file)) + ") :-  \n" + str(existing_rcs_file)
                print info_message
                log_list.append(info_message)

                info_message = "\n\tRCS file(s) re-created for follwoing node(s) (# " + str(len(newly_created_rcs_file)) + ") :-  \n" + str(newly_created_rcs_file)
                print info_message
                log_list.append(info_message)

                if triple_cur.alive:
                    triple_cur.close()
                    info_message = "\n\n\tTriple's cursor closed."
                    print info_message
                    log_list.append(info_message)

                info_message = "\n\n==================================================================================================="
                print info_message
                log_list.append(info_message)

            """
            info_message = "\n\n  Looking for dict type value(s) in attribute_type" + \
                " and relation_type fields of respective GAttribute and GRelation" + \
                "\n\tIf found code will replace corresponding value(s) with respective AttributeType/RelationType instances" + \
                "\n\tTHIS MAY TAKE MORE TIME DEPENDING UPON HOW MUCH DATA YOU HAVE.. SO PLEASE HAVE PATIENCE !\n"
            print info_message
            log_list.append(info_message)

            triple_cur = triple_collection.collection.find({"_type": {"$in": ["GAttribute", "GRelation"]}}, timeout=False)
            import bson
            hm = HistoryManager()
            sc = []
            ec = []
            tc = triple_cur.count()
            for i, each in enumerate(triple_cur):
                try:
                    n = None
                    info_message = "\n\n\tChecking # " + str((i+1)) + " record :-"
                    print info_message
                    log_list.append(info_message)

                    if each["_type"] == "GAttribute":
                        if (type(each["attribute_type"]) != bson.dbref.DBRef) and (type(each["attribute_type"]) == dict):
                            each["attribute_type"] = node_collection.collection.AttributeType(each["attribute_type"])
                            n = triple_collection.collection.GAttribute(each)
                            n.save()
                            sc.append(str(n._id))
                    elif each["_type"] == "GRelation":
                        if (type(each["relation_type"]) != bson.dbref.DBRef) and (type(each["relation_type"]) == dict):
                            each["relation_type"] = node_collection.collection.RelationType(each["relation_type"])
                            n = triple_collection.collection.GRelation(each)
                            n.save()
                            sc.append(str(n._id))
                except Exception as e:
                    error_message = "\n Error (" + str(each["_id"]) + ") : ", str(e) + " !!!"
                    print error_message
                    log_list.append(error_message)
                    ec.append(str(each["_id"]))
                    continue

            info_message = "\n\n\tTotal node(s) found: " + str(tc)
            print info_message
            log_list.append(info_message)

            info_message = "\n\n\tTotal node(s) updated (" + str(len(sc)) + ") : \n" + str(sc)
            print info_message
            log_list.append(info_message)

            info_message = "\n\n\tTotal node(s) where error encountered (" + str(len(ec)) + ") : \n" + str(ec)
            print info_message
            log_list.append(info_message)

            if triple_cur.alive:
                triple_cur.close()
                info_message = "\n\n\tTriple's cursor closed."
                print info_message
                log_list.append(info_message)

            info_message = "\n\n==================================================================================================="
            print info_message
            log_list.append(info_message)
            """
        except Exception as e:
            error_message = str(e)
            print error_message
            log_list.append("\n  Error: " + error_message + " !!!\n")

        finally:
            if log_list:
                info_message = "\n\n================ End of Iteration ================\n"
                print info_message
                log_list.append(info_message)

                log_file_name = "shift_Triples" + ".log"
                log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)
                with open(log_file_path, 'a') as log_file:
                    log_file.writelines(log_list)
        # --- End of handle() ---
