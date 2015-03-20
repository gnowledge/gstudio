from PIL import Image
from StringIO import StringIO
import magic

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.file import convert_mid_size_image

########################################################################


class Command(BaseCommand):

    help = " This script will remove existing mid size images and update with new size as 500*300 pixels "

    def handle(self, *args, **options):

		img_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Image'})
		img_objs = node_collection.find({'member_of': ObjectId(img_GST._id) })

		for each in img_objs:
			img = node_collection.one({'_id':ObjectId(each._id)})
			if img:

				# taking original size image in f
				f = img.fs.files.get(ObjectId(img.fs_file_ids[0]))

				filetype = magic.from_buffer(f.read(100000), mime = 'true')
				filename= f.name
				image_files = ["gif","jpeg","png","tif","thm","bmp"] 
				ext = ""
				for e in image_files:
					if e in filetype:
						ext = e
				if not ext:
					ext = "JPEG"

				# -- deleting already existing gridfs --
				# removing first positioned thumbnail size image (thumbnai-size image)
				if len(img.fs_file_ids) > 1:
					rm_id = img.fs_file_ids[1]
					img.fs.files.delete(rm_id)
					node_collection.collection.update({'_id':img._id},{'$pull':{'fs_file_ids': rm_id}})

				# removing second positioned mid size image (mid-size image)
				if len(img.fs_file_ids) > 2:
					rm_id = img.fs_file_ids[2]
					img.fs.files.delete(rm_id)
					node_collection.collection.update({'_id':img._id},{'$pull':{'fs_file_ids': rm_id}})

				node_collection.collection.update({'_id':img._id}, {"$set": {'fs_file_ids': [ img.fs_file_ids[0] ] } }, upsert=False, multi=False )
				# -- END of deleting already existing gridfs --

				# creating thumbnail images
				f.seek(0)
				img_thumb = StringIO()
				size = 128, 128
				obj = Image.open(StringIO(f.read()))
				obj.thumbnail(size, Image.ANTIALIAS)
				obj.save(img_thumb, ext)
				img_thumb.seek(0)

				if img_thumb:
					img_thumb_id = img.fs.files.put(img_thumb, filename=filename+"-thumbnail", content_type=filetype)
					node_collection.collection.update({'_id':img._id},{'$push':{'fs_file_ids':img_thumb_id}})

					print "\n thumbnail image created for image: ", img.name

				# creating mid-size images
				f.seek(0)
				mid_size_img = convert_mid_size_image(f, extension=ext)

				if mid_size_img:
					mid_img_id = img.fs.files.put(mid_size_img, filename=filename+"-mid_size_img", content_type=filetype)
					node_collection.collection.update({'_id':img._id},{'$push':{'fs_file_ids':mid_img_id}})

					print "\n mid size image created for image: ",img.name,"\n"

				# elif len(img.fs_file_ids) < 2:

				# 	f.seek(0)
				# 	img_thumb = StringIO()
				# 	# img_size = obj.size 
				# 	size = 128, 128
				# 	obj = Image.open(StringIO(f.read()))
				# 	obj.thumbnail(size, Image.ANTIALIAS)
				# 	obj.save(img_thumb, ext)
				# 	img_thumb.seek(0)

				# 	if img_thumb:
				# 		img_thumb_id = img.fs.files.put(img_thumb, filename=filename+"-thumbnail", content_type=filetype)
				# 		node_collection.collection.update({'_id':img._id},{'$push':{'fs_file_ids':img_thumb_id}})

				# 		print "\n thumbnail image created for image: ",img.name,"\n"

				# 	f.seek(0)
				# 	mid_size_img = convert_mid_size_image(f)

				# 	if mid_size_img:
				# 		mid_img_id = img.fs.files.put(mid_size_img, filename=filename+"-mid_size_img", content_type=filetype)
				# 		node_collection.collection.update({'_id':img._id},{'$push':{'fs_file_ids':mid_img_id}})

				# 		print "\n mid size image created for image: ",img.name,"\n"

				
				# # to update existing images
				# if len(img.fs_file_ids) >= 2:

				# 	img.fs.files.delete(img.fs_file_ids[1])
				# 	rm_id = img.fs_file_ids[1]
				# 	node_collection.collection.update({'_id':img._id},{'$pull':{'fs_file_ids': rm_id}})

				# 	f.seek(0)
				# 	mid_size_img = convert_mid_size_image(f)

				# 	if mid_size_img:
				# 		mid_img_id = img.fs.files.put(mid_size_img, filename=filename+"-mid_size_img", content_type=filetype)
				# 		node_collection.collection.update({'_id':img._id},{'$push':{'fs_file_ids':mid_img_id}})

				# 		# print "\n mid size image created for image: ",img.name,"\n"
