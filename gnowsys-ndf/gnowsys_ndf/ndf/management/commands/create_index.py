# imports from python libraries
from os import path as OS_PATH
import time
from sys import exc_info as EXC_INFO

# imports from core django libraries
from django.core.management.base import BaseCommand


# imports from third-party app(s)
from django_mongokit.document import model_names
from mongokit.database import Database as MK_Database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

# imports from project's app(s)
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.models import AttributeType, RelationType, MetaType, ProcessType, GSystemType
from gnowsys_ndf.ndf.models import Benchmark, Analytics
from gnowsys_ndf.ndf.models import GSystem, File, Group, Author
from gnowsys_ndf.ndf.models import Triple, GAttribute, GRelation
from gnowsys_ndf.ndf.models import ReducedDocs, ToReduceDocs, IndexedWordList
from gnowsys_ndf.ndf.models import node_holder
from gnowsys_ndf.ndf.models import db, node_collection, triple_collection, filehive_collection, counter_collection, benchmark_collection, filehive_collection, buddy_collection
from gnowsys_ndf.ndf.models import Filehive, Buddy, Counter

from gnowsys_ndf.ndf.models import INDEX_ASCENDING

####################################################################################################################

SCHEMA_ROOT = OS_PATH.join(OS_PATH.dirname(__file__), "schema_files")

log_list = []  # To hold intermediate errors
log_list_append = log_list.append

info_message = "\n######### Script run on : " + time.strftime("%c") + " #########\n" \
    + "############################################################"
log_list_append("\n" + info_message)
print info_message


def get_index_name(index_fields_list):
    """Returns index name and updated index field's list."""
    if type(index_fields_list) is not list:
        index_fields_list = list(index_fields_list)

    index_name = ""
    for i, index_field_value in enumerate(index_fields_list):
        if type(index_field_value) is not tuple:
            index_fields_list[i] = index_field_value = \
                (index_field_value, INDEX_ASCENDING)
            index_field_value_updated = True
        index_name += "{0}_{1}_".format(index_field_value[0], \
            index_field_value[1])

    # Remove trailing '_'
    return index_name.rstrip('_'), index_fields_list


def ensure_collection(db_obj, collection_name):
    """Creates collection in given database, if it doesn't exists.

    Accepts parameters:
        > db_obj: Database object.
        > collection_name: Name of the collection name in string format.
    """
    if not isinstance(db_obj, MK_Database):
        raise Exception('\nDatabaseObject (ensure_index): Invalid database object found!\n')

    if collection_name not in db_obj.collection_names():
        db_obj.create_collection(collection_name)
        return "\nCollection creation: {0}... created successfully".format(collection_name)
    else:
        return "\nCollection creation: {0}... already created.".format(collection_name)


class Command(BaseCommand):
    help = "This script helps in creating/updating index(es) for a collection."

    def handle(self, *args, **options):
        try:
            # Iterate through all class(es) defined in models file
            # And create index(es) defined in "indexes" field
            # defined within each class definition
            print "\nFollowing are the model(s) defined: \n{0}".format(', '.join(map(lambda name_tuple: name_tuple[0], model_names)))
            collection_object_wrapper = {
                'Nodes': node_collection.collection,
                'Triples': triple_collection.collection,
                'Benchmark': benchmark_collection,
                'Filehive': filehive_collection,
                'Buddy': buddy_collection,
                'Counter': counter_collection
            }

            collection_index_dict = {}

            for each_class_tuple in model_names:
                time.sleep(0.2)
                indexes_defined_for_collection = []
                gstudio_collection_name = None

                class_variable = eval(each_class_tuple[0])
                try:
                    gstudio_collection_name = class_variable.collection_name
                    info_message = ensure_collection(db, gstudio_collection_name)
                    log_list_append("\n" + info_message)
                    print info_message

                    info_message = "\nCreating index(es) for {0}".format(class_variable)
                    time.sleep(0.2)
                    log_list_append("\n" + info_message)
                    print info_message

                    info_message = "Collection name: {0}".format(gstudio_collection_name)
                    time.sleep(0.2)
                    log_list_append("\n" + info_message)
                    print info_message

                    indexes_defined_for_collection = \
                        map(lambda indexes_dict: tuple(indexes_dict['fields']), \
                            class_variable.indexes)

                    indexes_to_create = indexes_defined_for_collection
                    if gstudio_collection_name in collection_index_dict:
                        # Filter already created indexes
                        indexes_to_create = set(indexes_defined_for_collection) \
                            .difference(map(lambda indexes_list: tuple(indexes_list), \
                                collection_index_dict[gstudio_collection_name]))

                    # Override latest list of indexes
                    collection_index_dict[gstudio_collection_name] = \
                        indexes_defined_for_collection

                    if not indexes_defined_for_collection:
                        info_message = "There is NO index defined for this collection."
                        print info_message
                        time.sleep(0.2)
                        log_list_append("\n" + info_message)

                    elif not indexes_to_create:
                        info_message = "Following indexes are already been created..."
                        print info_message
                        time.sleep(0.2)
                        log_list_append("\n" + info_message)
                        for index_fields_list in indexes_defined_for_collection:
                            # If only field-name is provided in the list
                            # Then reformat it in format as (field-name, index-order)
                            index_val = ""  # Value returned after index is created/updated

                            index_val, index_fields_list = get_index_name(index_fields_list)

                            info_message = "  {0}".format(index_val)
                            print info_message
                            log_list_append("\n" + info_message)

                        # As there are no indexes to create for given collection
                        # Continue processing with next collection
                        continue

                except Exception as e:
                    error_message = "Error in line #{0} ({1}) : {2} !!!" \
                        .format(EXC_INFO()[-1].tb_lineno, each_class_tuple[1], str(e))
                    print error_message
                    log_list_append("\n" + error_message)
                    continue

                # Iterate through various index field-name(s) defined or
                # field-tuple(s) [i.e. (field-name, indexing-order)] defined as
                # part of index-field-list in a given collection
                """
                for i, index_dict in enumerate(iter(indexes_defined_for_collection)):
                    index_fields_list = index_dict["fields"]
                """
                for i, index_fields_list in enumerate(indexes_to_create):
                    time.sleep(0.2)
                    index_type = "Single index"
                    index_val = ""  # Value returned after index is created/updated

                    if len(index_fields_list) > 1:
                        index_type = "Compound index"

                    info_message = "#{0} >>> Creating {1} on following field(s): {2}" \
                        .format((i+1), index_type, index_fields_list)
                    print info_message
                    time.sleep(0.4)
                    log_list_append("\n" + info_message)
                    info_message = ""

                    # If only field-name is provided in the list
                    # Then reformat it in format as (field-name, index-order)
                    index_field_value_updated = False

                    index_val, index_fields_list = get_index_name(index_fields_list)

                    if index_field_value_updated:
                        info_message = "Index field(s) list updated... {0}" \
                            .format(index_fields_list)
                        print info_message
                        time.sleep(0.2)
                        log_list_append("\n" + info_message)

                    # Set collection-object based on collection_name defined for
                    # given collection in models before creating/updating index
                    # e.g. gstudio_collection = node_collection.collection
                    try:
                        time.sleep(0.2)
                        gstudio_collection = collection_object_wrapper[gstudio_collection_name]
                    except Exception as e:
                        error_message = "Error in line #{0} (DoesNotExist): Collection-object wrapper for " \
                            + "collection {1} not found!".format(EXC_INFO()[-1].tb_lineno, gstudio_collection_name)
                        log_list_append("\n" + error_message)
                        print error_message
                        error_message = "IndexError: {0}... not created/updated!!!" \
                            .format(index_val)
                        log_list_append("\n" + error_message)
                        print "\n", error_message
                        continue

                    # Create/Update index
                    if index_val in gstudio_collection.index_information().keys():
                        info_message = "{0}... index has already been created!" \
                            .format(index_val)
                        log_list_append("\n" + info_message)
                        print info_message
                    else:
                        try:
                            index_val = gstudio_collection.ensure_index(index_fields_list)
                            if index_val:
                                info_message = "{0}... index created successfully." \
                                    .format(index_val)
                            else:
                                info_message = "Index NOT created!"
                            print info_message
                            log_list_append("\n" + info_message)
                        except Exception as e:
                            error_message = "Error in line #{0}: {1}!!!" \
                                .format(EXC_INFO()[-1].tb_lineno, str(e))
                            log_list_append("\n" + error_message)
                            print error_message

        except Exception as e:
            error_message = "Error in line #{0}: {1}!!!" \
                .format(EXC_INFO()[-1].tb_lineno, str(e))
            log_list_append("\n" + error_message)
            print error_message

        finally:
            if log_list:
                time.sleep(0.6)

                log_file_name = "ensure_index" + ".log"
                log_file_path = OS_PATH.join(SCHEMA_ROOT, log_file_name)
                with open(log_file_path, 'a') as log_file:
                    log_file.writelines(log_list)

                info_message = "\nIndex Creation Completed ########################\n"
                log_list_append("\n" + info_message)
                print info_message
        # --- End of handle() ---
