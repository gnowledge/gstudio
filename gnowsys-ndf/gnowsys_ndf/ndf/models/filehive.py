from base_imports import *
from history_manager import HistoryManager

@connection.register
class Filehive(DjangoDocument):
    """
    Filehive class to hold any resource in file system.
    """

    objects = models.Manager()
    collection_name = 'Filehives'

    structure = {
        '_type': unicode,
        'md5': basestring,
        'relurl': basestring,
        'mime_type': basestring,             # Holds the type of file
        'length': float,
        'filename': unicode,
        'first_uploader': int,
        'first_parent': ObjectId,
        'uploaded_at': datetime.datetime,
        'if_image_size_name': basestring,
        'if_image_dimensions': basestring,
        }

    indexes = [
        {
            # 12: Single index
            'fields': [
                ('mime_type', INDEX_ASCENDING)
            ]
        }
    ]

    use_dot_notation = True
    required_fields = ['md5', 'mime_type']
    default_values = {
                        'uploaded_at': datetime.datetime.now
                    }


    def __unicode__(self):
        return self._id


    def identity(self):
        return self.__unicode__()


    def get_file_md5(self, file_blob):
        file_md5 = gfs.computehash(file_blob)
        return file_md5


    def get_filehive_obj_from_file_blob(self, file_blob):
        file_md5 = self.get_file_md5(file_blob)
        return filehive_collection.find_one({'md5': str(file_md5)})


    def check_if_file_exists(self, file_blob):
        file_md5 = self.get_file_md5(file_blob)
        return filehive_collection.find_one({'md5': file_md5})


    def _put_file(self, file_blob, file_extension):
        '''
        - Put's file under specified root.
        - After saving file blob or if file already exists,
            returns it's relative path.
        '''

        file_hash = gfs.computehash(file_blob)

        if gfs.exists(file_hash):
            # file with same hash already exists in file system.
            hash_addr_obj = gfs.get(file_hash)
        else:
            hash_addr_obj = gfs.put(file_blob, file_extension)

        return hash_addr_obj


    def save_file_in_filehive(self,
                              file_blob,
                              first_uploader,
                              first_parent,
                              file_name='',
                              mime_type=None,
                              file_extension='',
                              if_image_size_name='',
                              if_image_dimensions=None,
                              **kwargs):

        # file_hash = gfs.computehash(file_blob)

        # to check if file is new-fresh-file or old-existing-file
        file_exists = True

        file_metadata_dict = self.get_file_metadata(file_blob, mime_type, file_extension, file_name, if_image_dimensions)

        # file_blob.seek(0)
        addr_obj = self._put_file(file_blob, file_metadata_dict['file_extension'])
        # print "addr_obj : ", addr_obj

        md5 = str(addr_obj.id)
        filehive_obj = filehive_collection.find_one({'md5': md5})
        # print filehive_obj

        id_url_dict = {'id': None, 'relurl': ''}

        if not filehive_obj:

            # file is new and it doesn't exists
            file_exists = False

            # instantiating empty instance
            # filehive_obj = filehive_collection.collection.Filehive()
            filehive_obj = self

            filehive_obj.md5                 = str(md5)
            filehive_obj.relurl              = str(addr_obj.relpath)
            filehive_obj.mime_type           = str(file_metadata_dict['file_mime_type'])
            filehive_obj.length              = float(file_metadata_dict['file_size'])
            filehive_obj.filename            = unicode(file_metadata_dict['file_name'])
            filehive_obj.first_uploader      = int(first_uploader)
            filehive_obj.first_parent        = ObjectId(first_parent)
            filehive_obj.if_image_size_name  = str(if_image_size_name)
            filehive_obj.if_image_dimensions = str(file_metadata_dict['image_dimension'])

            filehive_obj.save()
            # print "filehive_obj : ", filehive_obj

        id_url_dict['id']     = filehive_obj._id
        id_url_dict['relurl'] = filehive_obj.relurl

        if kwargs.has_key('get_obj') and kwargs['get_obj']:
            result = filehive_obj
        else:
            result = id_url_dict

        if kwargs.has_key('get_file_exists') and kwargs['get_file_exists']:
            return (file_exists, result)

        return result


    @staticmethod
    def delete_file_from_filehive(filehive_id, filehive_relurl):

        filehive_obj    = filehive_collection.one({'_id': ObjectId(filehive_id)})
        if filehive_obj:
            file_md5        = str(filehive_obj.md5)
            filehive_obj_id = str(filehive_obj._id)

            print "\nDeleted filehive object having '_id': ", filehive_obj_id," from Filehive collection."
            filehive_obj.delete()

            if gfs.delete(file_md5):
                print "\nDeleted physical file having 'md5': ", file_md5
                return True

        if gfs.delete(filehive_relurl):
            print "\nDeleted physical file having 'relurl': ", filehive_relurl
            return True

        return False


    # -- file helper methods --
    def get_file_metadata(self,
                          file_blob,
                          mime_type=None,
                          file_extension='',
                          file_name='',
                          image_dimensions=None):

        # as file_blob is mostly uploaded file, using some of django's
        # <django.core.files.uploadedfile> class's built in properties.
        file_metadata_dict = {
            'file_name': '',
            'file_size': 0,
            'file_mime_type': '',
            'file_extension': '',
            'image_dimension': None
        }

        file_name = file_name if file_name else file_blob.name if hasattr(file_blob, 'name') else ''

        file_metadata_dict['file_name'] = file_name

        file_mime_type = mime_type if mime_type else self.get_file_mimetype(file_blob)
        file_metadata_dict['file_mime_type'] = file_mime_type

        if file_extension:
            file_metadata_dict['file_extension'] = file_extension
        else:
            file_extension = self.get_file_extension(file_name, file_mime_type)

        try:
            if hasattr(file_blob, 'size'):
                file_size = file_blob.size
            else:
                file_blob.seek(0, os.SEEK_END)
                file_size = file_blob.tell()
                file_blob.seek(0)
        except Exception, e:
            print "Exception in calculating file_size: ", e
            file_size = 0

        file_metadata_dict['file_size'] = file_size

        # get_image_dimensions: Returns the (width, height) of an image
        image_dimension_str = ''
        image_dimension_tuple = None
        if image_dimensions:
            image_dimension_tuple = image_dimensions
        else:
            try:
                image_dimension_tuple = get_image_dimensions(file_blob)
            except Exception, e:
                print "Exception in calculating file dimensions: ", e
                pass

        if image_dimension_tuple:
            image_dimension_str = str(image_dimension_tuple[0])
            image_dimension_str += ' X '
            image_dimension_str += str(image_dimension_tuple[1])
        file_metadata_dict['image_dimension'] = image_dimension_str

        # print "\nfile_metadata_dict : ", file_metadata_dict
        return file_metadata_dict


    def get_file_mimetype(self, file_blob, file_name=None):
        file_mime_type = ''

        file_content_type = file_blob.content_type if hasattr(file_blob, 'content_type') else None
        if file_name and "vtt" in file_name:
            return "text/vtt"
        if file_name and "srt" in file_name:
            return "text/srt"
        if file_content_type and file_content_type != 'application/octet-stream':
            file_mime_type = file_blob.content_type
        else:
            file_blob.seek(0)
            file_mime_type = magic.from_buffer(file_blob.read(), mime=True)
            file_blob.seek(0)

        return file_mime_type


    def get_file_name(self, file_blob):

        file_name = file_blob.name if hasattr(file_blob, 'name') else ''
        return file_name

    def get_file_extension(self, file_name, file_mime_type):
        # if uploaded file is of mimetype: 'text/plain':
        #     - use extension of original file if provided.
        #     - if extension is not provided, use '.txt' as extension.
        file_extension = ''

        poss_ext = '.'
        poss_ext += file_name.split('.')[-1]

        # possible extension from file name
        # get all possible extensions as a list
        # e.g for text/plain:
        # ['.ksh', '.pl', '.bat', '.h', '.c', '.txt', '.asc', '.text', '.pot', '.brf', '.srt']
        all_poss_ext = mimetypes.guess_all_extensions(file_mime_type)

        if poss_ext in all_poss_ext:
            file_extension = poss_ext

        elif poss_ext == '.vtt':
            file_mime_type = 'text/vtt'
            file_extension = '.vtt'

        elif poss_ext == '.srt':
            file_mime_type = 'text/srt'
            file_extension = '.srt'

        elif file_mime_type == 'text/plain':
            file_extension = '.txt'

        elif poss_ext == '.ggb':
            file_extension = '.ggb'

        else:
            file_extension = mimetypes.guess_extension(file_mime_type)

        return file_extension


    def convert_image_to_size(self, files, file_name='', file_extension='', file_size=()):
        """
        convert image into mid size image w.r.t. max width of 500
        """
        try:

            files.seek(0)
            mid_size_img = StringIO()
            size = file_size if file_size else (500, 300)
            file_name = file_name if file_name else files.name if hasattr(files, 'name') else ''

            try:
                img = Image.open(StringIO(files.read()))
            except Exception, e:
                print "Exception in opening file with PIL.Image.Open(): ", e
                return None, None

            size_to_comp = size[0]
            if (img.size > size) or (img.size[0] >= size_to_comp):
                # both width and height are more than width:500 and height:300
                # or
                # width is more than width:500
                factor = img.size[0]/size_to_comp
                img = img.resize((size_to_comp, int(img.size[1] / factor)), Image.ANTIALIAS)

            elif (img.size <= size) or (img.size[0] <= size_to_comp):
                img = img.resize(img.size, Image.ANTIALIAS)

            if 'jpg' in file_extension or 'jpeg' in file_extension:
                extension = 'JPEG'
            elif 'png' in file_extension:
                extension = 'PNG'
            elif 'gif' in file_extension:
                extension = 'GIF'
            elif 'svg' in file_extension:
                extension = 'SVG'
            else:
                extension = ''

            if extension:
                img.save(mid_size_img, extension)
            else:
                img.save(mid_size_img, "JPEG")

            img_size = img.size if img else None
            mid_size_img.name = file_name
            mid_size_img.seek(0)

            return mid_size_img, img_size

        except Exception, e:
            print "Exception in converting image to mid size: ", e
            return None

    def save(self, *args, **kwargs):

        is_new = False if ('_id' in self) else True

        if is_new:
            self.uploaded_at = datetime.datetime.now()

        super(Filehive, self).save(*args, **kwargs)

        # storing Filehive JSON in RSC system:
        history_manager = HistoryManager()
        rcs_obj = RCS()

        if is_new:

            # Create history-version-file
            if history_manager.create_or_replace_json_file(self):
                fp = history_manager.get_file_path(self)
                message = "This document (" + str(self.md5) + ") is created on " + self.uploaded_at.strftime("%d %B %Y")
                rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

        else:
            # Update history-version-file
            fp = history_manager.get_file_path(self)

            try:
                rcs_obj.checkout(fp, otherflags="-f")

            except Exception as err:
                try:
                    if history_manager.create_or_replace_json_file(self):
                        fp = history_manager.get_file_path(self)
                        message = "This document (" + str(self.md5) + ") is re-created on " + self.uploaded_at.strftime("%d %B %Y")
                        rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

                except Exception as err:
                    print "\n DocumentError: This document (", self._id, ":", str(self.md5), ") can't be re-created!!!\n"
                    node_collection.collection.remove({'_id': self._id})
                    raise RuntimeError(err)

            try:
                if history_manager.create_or_replace_json_file(self):
                    message = "This document (" + str(self.md5) + ") is lastly updated on " + datetime.datetime.now().strftime("%d %B %Y")
                    rcs_obj.checkin(fp, 1, message.encode('utf-8'))

            except Exception as err:
                print "\n DocumentError: This document (", self._id, ":", str(self.md5), ") can't be updated!!!\n"
                raise RuntimeError(err)

        # --- END of storing Filehive JSON in RSC system ---


filehive_collection = db["Filehives"].Filehive
