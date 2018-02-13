from base_imports import *
from node import Node, node_collection
from filehive import filehive_collection


@connection.register
class GSystem(Node):
    """GSystemType instance
    """

    # static vars:
    image_sizes_name = ['original', 'mid', 'thumbnail']
    image_sizes = {'mid': (500, 300), 'thumbnail': (128, 128)}
    sys_gen_image_prefix = 'gstudio-'

    structure = {
        'attribute_set': [dict],    # ObjectIds of GAttributes
        'relation_set': [dict],     # ObjectIds of GRelations
        'module_set': [dict],       # Holds the ObjectId & SnapshotID (version_number)
                                        # of collection elements
                                        # along with their sub-collection elemnts too
        'if_file': {
                        'mime_type': basestring,
                        'original': {'id': ObjectId, 'relurl': basestring},
                        'mid': {'id': ObjectId, 'relurl': basestring},
                        'thumbnail': {'id': ObjectId, 'relurl': basestring}
                    },
        'author_set': [int],        # List of Authors
        'annotations': [dict],      # List of json files for annotations on the page
        'origin': [],                # e.g:
                                        # [
                                        #   {"csv-import": <fn name>},
                                        #   {"sync_source": "<system-pub-key>"}
                                        # ]
        # Replace field 'license': basestring with
        # legal: dict
        'legal': {
                    'copyright': basestring,
                    'license': basestring
                    }
    }

    use_dot_notation = True

    # default_values = "CC-BY-SA 4.0 unported"
    default_values = {
                        'legal': {
                            'copyright': GSTUDIO_DEFAULT_COPYRIGHT,
                            'license': GSTUDIO_DEFAULT_LICENSE
                        }
                    }

    def fill_gstystem_values(self,
                            request=None,
                            attribute_set=[],
                            relation_set=[],
                            author_set=[],
                            origin=[],
                            uploaded_file=None,
                            **kwargs):
        '''
        all node fields will be passed from **kwargs and rest GSystem's fields as args.
        '''

        existing_file_gs = None
        existing_file_gs_if_file = None

        if "_id" not in self and uploaded_file:

            fh_obj = filehive_collection.collection.Filehive()
            existing_fh_obj = fh_obj.check_if_file_exists(uploaded_file)

            if existing_fh_obj:
                existing_file_gs = node_collection.find_one({
                                    '_type': 'GSystem',
                                    'if_file.original.id': existing_fh_obj._id
                                })

            if kwargs.has_key('unique_gs_per_file') and kwargs['unique_gs_per_file']:

                if existing_file_gs:
                    print "Returning:: "
                    return existing_file_gs

        self.fill_node_values(request, **kwargs)

        # fill gsystem's field values:
        self.author_set = author_set

        user_id = self.created_by

        # generating '_id':
        if not self.has_key('_id'):
            self['_id'] = ObjectId()

        # origin:
        if origin:
            self['origin'].append(origin)
        # else:  # rarely/no origin field value will be sent via form/request.
        #     self['origin'] = request.POST.get('origin', '').strip()

        if existing_file_gs:

            existing_file_gs_if_file = existing_file_gs.if_file

            def __check_if_file(d):
                for k, v in d.iteritems():
                    if isinstance(v, dict):
                        __check_if_file(v)
                    else:
                        # print "{0} : {1}".format(k, v)
                        if not v:
                            existing_file_gs_if_file = None

        if uploaded_file and existing_file_gs_if_file:
            self['if_file'] = existing_file_gs_if_file

        elif uploaded_file and not existing_file_gs:
            original_filehive_obj   = filehive_collection.collection.Filehive()
            original_file           = uploaded_file

            file_name = original_filehive_obj.get_file_name(original_file)
            if not file_name:
                file_name = self.name
            mime_type = original_filehive_obj.get_file_mimetype(original_file, file_name)
            original_file_extension = original_filehive_obj.get_file_extension(file_name, mime_type)

            file_exists, original_filehive_obj = original_filehive_obj.save_file_in_filehive(
                file_blob=original_file,
                file_name=file_name,
                first_uploader=user_id,
                first_parent=self._id,
                mime_type=mime_type,
                file_extension=original_file_extension,
                if_image_size_name='original',
                get_obj=True,
                get_file_exists=True
                )

            mime_type = original_filehive_obj.mime_type

            # print "original_filehive_obj: ", original_filehive_obj
            if original_filehive_obj:

                self.if_file.mime_type       = mime_type
                self.if_file.original.id    = original_filehive_obj._id
                self.if_file.original.relurl = original_filehive_obj.relurl

                if 'image' in original_filehive_obj.mime_type.lower():

                    for each_image_size in self.image_sizes_name[1:]:

                        parent_id = self.if_file[self.image_sizes_name[self.image_sizes_name.index(each_image_size) - 1]]['id']

                        each_image_size_filename =  self.sys_gen_image_prefix \
                                                    + each_image_size \
                                                    + '-' \
                                                    + original_filehive_obj.filename

                        each_image_size_filehive_obj = filehive_collection.collection.Filehive()
                        each_image_size_file, dimension = each_image_size_filehive_obj.convert_image_to_size(files=original_file,
                                                  file_name=each_image_size_filename,
                                                  file_extension=original_file_extension,
                                                  file_size=self.image_sizes[each_image_size])

                        if each_image_size_file:
                            each_image_size_id_url = each_image_size_filehive_obj.save_file_in_filehive(
                                file_blob=each_image_size_file,
                                file_name=each_image_size_filename,
                                first_uploader=user_id,
                                first_parent=parent_id,
                                mime_type=mime_type,
                                file_extension=original_file_extension,
                                if_image_size_name=each_image_size,
                                if_image_dimensions=dimension)

                            # print "each_image_size_id_url : ",each_image_size_id_url
                            self.if_file[each_image_size]['id']    = each_image_size_id_url['id']
                            self.if_file[each_image_size]['relurl'] = each_image_size_id_url['relurl']

        # Add legal information[copyright and license] to GSystem node
        license = kwargs.get('license', None)
        copyright = kwargs.get('copyright', None)

        if license:
            if self.legal['license'] is not license:
                self.legal['license'] = license
        else:
            self.legal['license'] = GSTUDIO_DEFAULT_LICENSE

        if copyright:
            if self.legal['copyright'] is not copyright:
                self.legal['copyright'] = copyright
        else:
            self.legal['copyright'] = GSTUDIO_DEFAULT_COPYRIGHT

        return self


    def get_gsystem_mime_type(self):

        if hasattr(self, 'mime_type') and self.mime_type:
            mime_type = self.mime_type
        elif self.if_file.mime_type:
            mime_type = self.if_file.mime_type
        else:
            mime_type = ''

        return mime_type


    def get_file(self, md5_or_relurl=None):

        file_blob = None

        try:
            if md5_or_relurl:
                file_blob = gfs.open(md5_or_relurl)
        except Exception, e:
                print "File '", md5_or_relurl, "' not found: ", e

        return file_blob


    # static query methods
    @staticmethod
    def query_list(group_id, member_of_name, user_id=None, if_gstaff=False, **kwargs):
        from group import Group
        from gsystem_type import GSystemType

        group_name, group_id = Group.get_group_name_id(group_id)
        gst_name, gst_id = GSystemType.get_gst_name_id(member_of_name)
        if if_gstaff:
            query = {
                    '_type': 'GSystem',
                    'status': 'PUBLISHED',
                    'group_set': {'$in': [group_id]},
                    'member_of': {'$in': [gst_id]},
                    'access_policy': {'$in': [u'Public', u'PUBLIC', u'PRIVATE']}
                    }
        else:
            query = {
                    '_type': 'GSystem',
                    'status': 'PUBLISHED',
                    'group_set': {'$in': [group_id]},
                    'member_of': {'$in': [gst_id]},
                    '$or':[
                            {'access_policy': {'$in': [u'Public', u'PUBLIC']}},
                            {'$and': [
                                {'access_policy': u"PRIVATE"},
                                {'created_by': user_id}
                                ]
                            },
                            {'created_by': user_id}
                        ]
                    }
        for each in kwargs:
            query.update({each : kwargs[each]})
        return node_collection.find(query).sort('last_update', -1)

    @staticmethod
    def child_class_names():
        '''
        Currently, this is hardcoded but it should be dynamic.
        Try following:
        import inspect
        inspect.getmro(GSystem)
        '''
        return ['Group', 'Author', 'File']
    # --- END of static query methods
