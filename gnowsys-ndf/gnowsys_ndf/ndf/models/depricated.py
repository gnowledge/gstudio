# @connection.register
# class File(GSystem):
#     """File class to hold any resource
#     """

#     structure = {
#         'mime_type': basestring,             # Holds the type of file
#         'fs_file_ids': [ObjectId],           # Holds the List of  ids of file stored in gridfs
#                                              # order is [original, thumbnail, mid]
#         'file_size': {
#             'size': float,
#             'unit': unicode
#         }  # dict used to hold file size in int and unit palace in term of KB,MB,GB
#     }

#     indexes = [
#         {
#             # 12: Single index
#             'fields': [
#                 ('mime_type', INDEX_ASCENDING)
#             ]
#         }
#     ]

#     gridfs = {
#         'containers': ['files']
#     }

#     use_dot_notation = True
