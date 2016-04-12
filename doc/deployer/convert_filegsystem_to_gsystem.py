import time
import StringIO

from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GSTUDIO_LOGS_DIR_PATH


# all File class instances
all_gridfile = node_collection.find({ '_type': u'File'})

gst_file = node_collection.one({'_type': 'GSystemType', 'name': 'File'})

# all GSystem instances which are file
all_fhgs = node_collection.find({'_type': 'GSystem', 'member_of': {'$in': [gst_file._id]}})

# static lists
fs_file_ids_size_names = ['original', 'thumbnail', 'mid']
file_fields_tobe_remove_list = ['mime_type', 'fs_file_ids', 'file_size']
log_list = []

# all_gridfile.limit(5)
# print [gf._id for gf in all_gridfile]
# all_gridfile.rewind()

def log_print(log_string):
    try:
        log_list.append('\n')
        log_list.append(log_string)
        print "\n", log_string

    except:
        error_message = '\n !! Error while doing log and print.\n\n'
        print error_message
        log_list.append(error_message)


script_start_str = "######### Script ran on : " + time.strftime("%c") + " #########\n------------------------------------------------------------\n"
log_print(script_start_str)

for each_gridfile in all_gridfile:

    try:
        info = u'\nProcessing file having _id: "' + unicode(each_gridfile._id) + u'" | name: "' + each_gridfile.name + u'"\n'
        log_print(info)
    except Exception, e:
        print '\nProcessing file having _id: "', each_gridfile._id.__str__() + '"\n'

    # logging/showing object before processing
    log_print('\nPrevious to processing, OLD object: ')
    log_print(each_gridfile.to_json())

    # getting file's '_id', 'fs_file_ids', 'created_by' and 'if_file'
    each_gridfile_id = each_gridfile._id
    fs_file_ids_list = each_gridfile.fs_file_ids if hasattr(each_gridfile, 'fs_file_ids') else []
    user_id = each_gridfile.created_by
    if_file = each_gridfile.if_file

    # start populating "if_file"
    if hasattr(each_gridfile, 'mime_type'):
        if_file['mime_type'] = each_gridfile.mime_type

    log_print("\nfs_file_ids : " + fs_file_ids_list.__str__())

    # looping over each fs_file_ids
    for index, each_fs_file_ids in enumerate(fs_file_ids_list):

        info = '\n- ' + fs_file_ids_size_names[index] + '  : "' + fs_file_ids_list[index].__str__() + '"'
        log_print(info)

        # retriving file from gridfs
        # returns gridout object
        gridoutfile = each_gridfile.fs.files.get(fs_file_ids_list[index])

        # initializing filehive obj to hold current file
        filehive_obj = filehive_collection.collection.Filehive()

        file_name   = gridoutfile.filename
        mime_type   = gridoutfile.content_type
        file_extension = filehive_obj.get_file_extension(file_name, mime_type)

        # needs to convert gridoutfile into StringIO, so casting:
        stringiofile = StringIO(gridoutfile.read())

        filehive_id_url_dict = filehive_obj.save_file_in_filehive(
            file_blob=stringiofile,
            file_name=file_name,
            first_uploader=user_id,
            first_parent=each_gridfile_id,
            mime_type=mime_type,
            file_extension=file_extension,
            if_image_size_name=fs_file_ids_size_names[index],
            )

        log_print('\t-- filehive_id_url_dict: ' + str(filehive_id_url_dict))

        # updating if_file to that file_size:
        if_file[fs_file_ids_size_names[index]] = filehive_id_url_dict

        # --- END of looping ---

    # updating / overwritting each_gridfile object:
    # "_type"
    each_gridfile._type = u'GSystem'

    # "member_of" for gst File
    if gst_file._id not in each_gridfile.member_of:
        each_gridfile.member_of.append(gst_file._id)

    # "if_file"
    each_gridfile.if_file = if_file

    # removing file fields: 'mime_type', 'fs_file_ids', 'file_size'
    for each_field in file_fields_tobe_remove_list:
        try:
            each_gridfile.pop(each_field)
        except Exception, e:
            print 'Exception in removing field : "' + each_field + '". ' + str(e)
            pass

    each_gridfile.save()

    # # removing File class fields:
    # print node_collection.collection.update(
    #                 {'_id': ObjectId(each_gridfile_id)},
    #                 {
    #                     '$unset': {
    #                         'mime_type': False,
    #                         'fs_file_ids': False,
    #                         'file_size': False 
    #                         }
    #                 },upsert=False, multi=False)

    each_gridfile.reload()
    log_print('\nAfter processing, UPDATED object:')
    log_print(each_gridfile.to_json())

    log_print('\n\n=============================================================================================================\n')


log_list.append("\n :::::::::::::::::::::::::::::::::::::::::::::: End of Iteration ::::::::::::::::::::::::::::::::::::::::::::::\n\n\n")
log_file_name = 'convert_filegsystem_to_gsystem.log'

if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
    os.makedirs(GSTUDIO_LOGS_DIR_PATH)

log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
# print log_file_path
with open(log_file_path, 'a') as log_file:
    log_file.writelines(log_list)
