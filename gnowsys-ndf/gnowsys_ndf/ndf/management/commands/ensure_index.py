# imports from python libraries
from os import path as OS_PATH
import time
from sys import exc_info as EXC_INFO

# imports from installed packages
from django.core.management.base import BaseCommand
from django_mongokit.document import model_names

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

# imports from application folders/files
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.models import AttributeType, RelationType, MetaType, ProcessType, GSystemType
from gnowsys_ndf.ndf.models import Benchmark, Analytics
from gnowsys_ndf.ndf.models import GSystem, File, Group, Author
from gnowsys_ndf.ndf.models import Triple, GAttribute, GRelation
from gnowsys_ndf.ndf.models import ReducedDocs, ToReduceDocs, IndexedWordList
from gnowsys_ndf.ndf.models import node_holder
from gnowsys_ndf.ndf.models import node_collection, triple_collection

from gnowsys_ndf.ndf.models import INDEX_ASCENDING

####################################################################################################################

SCHEMA_ROOT = OS_PATH.join(OS_PATH.dirname(__file__), "schema_files")

log_list = []  # To hold intermediate errors
log_list_append = log_list.append

info_message = "\n######### Script run on : " + time.strftime("%c") + " #########\n" \
    + "############################################################"
log_list_append(info_message)
print info_message


class Command(BaseCommand):
    help = "This script helps in creating/updating index(es) for a collection."

    def handle(self, *args, **options):
        try:
            # Iterate through all class(es) defined in models file
            # And create index(es) defined in "indexes" field
            # defined within each class definition
            print "\nFollowing are the model(s) defined: {0}".format(model_names)
            collection_object_wrapper = {
                'Nodes': node_collection.collection,
                'Triples': triple_collection.collection
            }

            for each_class_tuple in model_names:
                indexes_defined_for_collection = []
                gstudio_collection_name = None

                class_variable = eval(each_class_tuple[0])
                try:
                    time.sleep(1)
                    info_message = "\nCreating index(es) for {0}".format(class_variable)
                    log_list_append(info_message)
                    print info_message
                    time.sleep(1)
                    gstudio_collection_name = class_variable.collection_name
                    info_message = "Collection name: {0}".format(gstudio_collection_name)
                    log_list_append(info_message)
                    print info_message
                    time.sleep(2)

                    indexes_defined_for_collection = class_variable.indexes

                    if not indexes_defined_for_collection:
                        info_message = "There is NO index defined for this collection."
                        log_list_append(info_message)
                        print info_message
                except Exception as e:
                    error_message = "Error in line #{0} ({1}) : {2} !!!" \
                        .format(EXC_INFO()[-1].tb_lineno, each_class_tuple[1], str(e))
                    print error_message
                    log_list_append(error_message)
                    continue

                # Iterate through various index field-name(s) defined or
                # field-tuple(s) [i.e. (field-name, indexing-order)] defined as 
                # part of index-field-list in a given collection
                for i, index_dict in enumerate(iter(indexes_defined_for_collection)):
                    time.sleep(1)
                    index_fields_list = index_dict["fields"]
                    index_type = "Single index"
                    index_val = ""  # Value returned after index is created/updated

                    if len(index_fields_list) > 1:
                        index_type = "Compound index"

                    info_message = "#{0} >>> Creating {1} on following field(s): {2}" \
                        .format((i+1), index_type, index_fields_list)
                    print info_message
                    log_list_append(info_message)

                    time.sleep(4)
                    # If only field-name is provided in the list
                    # Then reformat it in format as (field-name, index-order)
                    index_field_value_updated = False
                    for i, index_field_value in enumerate(index_fields_list):
                        if type(index_field_value) is not tuple:
                            index_fields_list[i] = index_field_value = \
                                (index_field_value, INDEX_ASCENDING)
                            index_field_value_updated = True
                        index_val += "_{0}_{1}".format(index_field_value[0].strip('_'), \
                            index_field_value[1])

                    if index_field_value_updated:
                        time.sleep(1)
                        info_message = "Index field(s) list updated... {0}" \
                            .format(index_fields_list)
                        print info_message
                        log_list_append(info_message)

                    time.sleep(1)
                    # Set collection-object based on collection_name defined for
                    # given collection in models before creating/updating index
                    # e.g. gstudio_collection = node_collection.collection
                    try:
                        gstudio_collection = collection_object_wrapper[gstudio_collection_name]
                    except Exception as e:
                        error_message = "Error in line #{0} (DoesNotExist): Collection-object wrapper for " \
                            + "collection {1} not found!".format(EXC_INFO()[-1].tb_lineno, gstudio_collection_name)
                        log_list_append(error_message)
                        error_message = "IndexError: {0}... not created/updated!!!" \
                            .format(index_val)
                        log_list_append(error_message)
                        continue

                    time.sleep(3)
                    # Create/Update index
                    if index_val in gstudio_collection.index_information().keys():
                        info_message = "{0}... index has already been created!" \
                            .format(index_val)
                    else:
                        index_val = gstudio_collection.ensure_index(index_fields_list)
                        if index_val:
                            info_message = "{0}... index created successfully." \
                                .format(index_val)
                    log_list.append(info_message)
                    print info_message

        except Exception as e:
            error_message = "Error in line #{0}: {1}!!!" \
                .format(EXC_INFO()[-1].tb_lineno, str(e))
            log_list_append(error_message)
            print error_message

        finally:
            if log_list:
                time.sleep(3)
                info_message = "\n================ End of Iteration ================\n"
                log_list_append(info_message)
                print info_message

                log_file_name = "ensure_index" + ".log"
                log_file_path = OS_PATH.join(SCHEMA_ROOT, log_file_name)
                with open(log_file_path, 'a') as log_file:
                    log_file.writelines(log_list)
        # --- End of handle() ---
