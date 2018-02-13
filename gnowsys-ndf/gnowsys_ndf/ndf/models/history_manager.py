from base_imports import *
from models_utils import NodeJSONEncoder
from db_utils import get_all_collection_child_names


class HistoryManager():
    """Handles history management for documents of a collection
    using Revision Control System (RCS).
    """

    objects = models.Manager()

    __RCS_REPO_DIR = RCS_REPO_DIR

    def __init__(self):
        pass

    def check_dir_path(self, dir_path):
        """Checks whether path exists; and if not it creates that path.

        Arguments:
        (1) dir_path -- a string value representing an absolute path

        Returns: Nothing
        """
        dir_exists = os.path.isdir(dir_path)

        if not dir_exists:
            os.makedirs(dir_path)

    def get_current_version(self, document_object):
        """Returns the current version/revision number of the given document instance.
        """
        fp = self.get_file_path(document_object)
        rcs = RCS()
        return rcs.head(fp)

    def get_version_dict(self, document_object):
        """Returns a dictionary containing list of revision numbers.

        Example:
        {
         "1": "1.1",
         "2": "1.2",
         "3": "1.3",
        }
        """
        fp = self.get_file_path(document_object)

        rcs = RCS()
        # current_rev = rcs.head(fp)          # Say, 1.4
        total_no_of_rev = int(rcs.info(fp)["total revisions"])         # Say, 4

        version_dict = {}
        for i, j in zip(range(total_no_of_rev), reversed(range(total_no_of_rev))):
            version_dict[(j + 1)] = rcs.calculateVersionNumber(fp, (i))

        return version_dict

    def get_file_path(self, document_object):
        """Returns absolute filesystem path for a json-file.

        This path is combination of :-
        (a) collection_directory_path: path to the collection-directory
        to which the given instance belongs
        (b) hashed_directory_structure: path built from object id based
        on the set hashed-directory-level
        (c) file_name: '.json' extension concatenated with object id of
        the given instance

        Arguments:
        (1) document_object -- an instance of a collection

        Returns: a string representing json-file's path
        """
        file_name = (document_object._id.__str__() + '.json')

        collection_dir = \
            (os.path.join(self.__RCS_REPO_DIR, \
                              document_object.collection_name))

        # Example:
        # if -- file_name := "523f59685a409213818e3ec6.json"
        # then -- collection_hash_dirs := "6/c/3/8/
        # -- from last (2^0)pos/(2^1)pos/(2^2)pos/(2^3)pos/../(2^n)pos"
        # here n := hash_level_num
        collection_hash_dirs = ""
        for pos in range(0, RCS_REPO_DIR_HASH_LEVEL):
            collection_hash_dirs += \
                (document_object._id.__str__()[-2**pos] + "/")

        file_path = \
            os.path.join(collection_dir, \
                             (collection_hash_dirs + file_name))

        return file_path

    def create_rcs_repo_collections(self, *versioning_collections):
        """Creates Revision Control System (RCS) repository.

        After creating rcs-repo, it also creates sub-directories
        for each collection inside it.

        Arguments:
        (1) versioning_collections -- a list representing collection-names

        Returns: Nothing
        """
        try:
            self.check_dir_path(self.__RCS_REPO_DIR)
        except OSError as ose:
            print("\n\n RCS repository not created!!!\n {0}: {1}\n"\
                      .format(ose.errno, ose.strerror))
        else:
            print("\n\n RCS repository created @ following path:\n {0}\n"\
                      .format(self.__RCS_REPO_DIR))

        # for collection in versioning_collections:
        #     rcs_repo_collection = os.path.join(self.__RCS_REPO_DIR, \
        #                                            collection)
        #     try:
        #         os.makedirs(rcs_repo_collection)
        #     except OSError as ose:
        #         print(" {0} collection-directory under RCS repository "\
        #                   "not created!!!\n Error #{1}: {2}\n"\
        #                   .format(collection, ose.errno, ose.strerror))
        #     else:
        #         print(" {0} collection-directory under RCS repository "\
        #                   "created @ following path:\n {1}\n"\
        #                   .format(collection, rcs_repo_collection))

    def create_or_replace_json_file(self, document_object=None):
        """Creates/Overwrites a json-file for passed document object in
        its respective hashed-directory structure.

        Arguments:
        (1) document_object -- an instance of document of a collection

        Returns: A boolean value indicating whether created successfully
        (a) True - if created
        (b) False - Otherwise
        # """
        # from MetaType import MetaType
        # from GSystemType import GSystemType
        # from GSystem import GSystem
        # from AttributeType import AttributeType
        # from GAttribute import GAttribute
        # from RelationType import RelationType
        # from GRelation import GRelation
        # from Filehive import Filehive
        # from Buddy import Buddy
        # Counter

        # collection_list = ('MetaType', 'GSystemType', 'GSystem', 'AttributeType', 'GAttribute', 'RelationType', 'GRelation', 'Filehive', 'Buddy', 'Counter')
        collection_list = get_all_collection_child_names() 
        file_res = False    # True, if no error/exception occurred
        if document_object is not None and \
                (document_object._meta.model_name in collection_list):
                # isinstance(document_object, collection_list):

            file_path = self.get_file_path(document_object)

            json_data = document_object.to_json_type()
            #------------------------------------------------------------------
            # Creating/Overwriting data into json-file and rcs-file
            #------------------------------------------------------------------

            # file_mode as w:-
            #    Opens a file for writing only.
            #    Overwrites the file if the file exists.
            #    If the file does not exist, creates a new file for writing.
            file_mode = 'w'
            rcs_file = None

            try:
                self.check_dir_path(os.path.dirname(file_path))

                rcs_file = open(file_path, file_mode)
            except OSError as ose:
                print("\n\n Json-File not created: Hashed directory "\
                          "structure doesn't exists!!!")
                print("\n {0}: {1}\n".format(ose.errno, ose.strerror))
            except IOError as ioe:
                print(" " + str(ioe))
                print("\n\n Please refer following command from "\
                          "\"Get Started\" file:\n"\
                          "\tpython manage.py initrcsrepo\n")
            except Exception as e:
                print(" Unexpected error : " + str(e))
            else:
                rcs_file.write(json.dumps(json_data,
                                          sort_keys=True,
                                          indent=4,
                                          separators=(',', ': '),
                                          cls=NodeJSONEncoder
                                          )
                               )

                # TODO: Commit modifications done to the file into
                # it's rcs-version-file

                file_res = True
            finally:
                if rcs_file is not None:
                    rcs_file.close()

        else:
            # TODO: Throw/raise error having following message!
            # if document_object is None or
            # !isinstance(document_object, collection_list)

            msg = " Following instance is either invalid or " \
            + "not matching given instances-type list " + str(collection_list) + ":-" \
            + "\n\tObjectId: " + document_object._id.__str__() \
            + "\n\t    Type: " + document_object._type \
            + "\n\t    Name: " + document_object.get('name', '')
            raise RuntimeError(msg)

        return file_res

    def get_version_document(self, document_object, version_no=""):
        """Returns an object representing mongodb document instance of a given version number.
        """
        if version_no == "":
            version_no = self.get_current_version(document_object)

        fp = self.get_file_path(document_object)
        rcs = RCS()
        rcs.checkout((fp, version_no), otherflags="-f")

        json_data = ""
        with open(fp, 'r') as version_file:
            json_data = version_file.read()

	# assigning None value to key, which is not present in json_data compare to Node class keys
	null = 0
	import json
	json_dict = json.loads(json_data)
	json_node_keys = document_object.keys()
	json_dict_keys = json_dict.keys()
	diff_keys = list(set(json_node_keys)-set(json_dict_keys))
	if diff_keys:
		for each in diff_keys:
			json_dict[each]=None
	json_data = json.dumps(json_dict)

        # Converts the json-formatted data into python-specific format
        doc_obj = node_collection.from_json(json_data)

        rcs.checkin(fp)

        # Below Code temporary resolves the problem of '$oid' This
        # problem occurs when we convert mongodb's document into
        # json-format using mongokit's to_json_type() function - It
        # converts ObjectId() type into corresponding format
        # "{u'$oid': u'24-digit-hexstring'}" But actual problem comes
        # into picture when we have a field whose data-type is "list
        # of ObjectIds" In case of '_id' field (automatically created
        # by mongodb), mongokit handles this conversion and does so
        # But not in case of "list of ObjectIds", it still remains in
        # above given format and causes problem

        for k, v in doc_obj.iteritems():
            oid_list_str = ""
            oid_ObjectId_list = []
            if v and type(v) == list:
                oid_list_str = v.__str__()
                try:
                    if '$oid' in oid_list_str: #v.__str__():

                        for oid_dict in v:
                            oid_ObjectId = ObjectId(oid_dict['$oid'])
                            oid_ObjectId_list.append(oid_ObjectId)

                        doc_obj[k] = oid_ObjectId_list

                except Exception as e:
                    print "\n Exception for document's ("+str(doc_obj._id)+") key ("+k+") -- ", str(e), "\n"

        return doc_obj


    @staticmethod
    def delete_json_file(node_id_or_obj, expected_type):
        from node import Node
        node_obj = Node.get_node_obj_from_id_or_obj(node_id_or_obj, expected_type)
        history_manager = HistoryManager()
        json_file_path = history_manager.get_file_path(node_obj)
        version_file_path = json_file_path + ',v'
        try:
            os.remove(version_file_path)
            print "\nDeleted RCS json version file : ", version_file_path
            os.remove(json_file_path)
            print "\nDeleted RCS json file : ", json_file_path
        except Exception, e:
            print "\nException occured while deleting RCS file for node '", node_obj._id.__str__(), "' : ", e
