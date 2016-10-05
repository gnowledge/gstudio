from gnowsys_ndf.ndf.models import *
copy_files = False
move_files = False

source_group_id = raw_input("Enter source group _id: ")
destination_group_id = raw_input("Enter destination group _id: ")

resource_type_input = raw_input("\nChoose Resource type:\n  1. File\n  2. Page\nEnter option no. (1 or 2): ")
if resource_type_input == '1':
	resource_type_name = 'File'
elif resource_type_input == '2':
	resource_type_name = 'Page'
else:
	print '\nYou have choosen wrong option. "File" will be default option selected in this case.'
	resource_type_name = 'File'

print '\nYou have choosen resource type: ', resource_type_name, '\n'

copy_or_move = raw_input("Enter c/C to copy the files OR m/M to move the files :")

if copy_or_move == 'c' or copy_or_move == 'C':
	copy_files = True
elif copy_or_move == 'm' or copy_or_move == 'M':
	move_files = True
else:
	print "\nInvalid option."

try:

	source_group_obj = node_collection.one({'_id': ObjectId(source_group_id)})
	destination_group_obj = node_collection.one({'_id': ObjectId(destination_group_id)})

	if source_group_obj and destination_group_obj:

		member_of_gst = node_collection.one({'_type': u'GSystemType', 'name': unicode(resource_type_name)})

		# Find all files that are having source_group_id in its group_set
		source_grp_files = node_collection.find({
												'_type': 'GSystem',
												'group_set': source_group_obj._id,
												'member_of': {'$in': [member_of_gst._id]}
												# 'if_file.mime_type': {
												# 	'$exists': True, '$ne': None
												# }
											})

		if source_grp_files.count():

			copy_move_confirmation = raw_input("Total files to be processed: "+ str(source_grp_files.count())+". Enter y/Y to continue: ")

			if copy_move_confirmation == 'y' or copy_move_confirmation == 'Y':
				for each_source_file in source_grp_files:

					if copy_files and not move_files:
						if destination_group_obj._id not in each_source_file.group_set:
							each_source_file.group_set.append(destination_group_obj._id)

					elif move_files and not copy_files:
						# Remove source_group_id and add destination_group_id
						# This is to prevent file that are cross-published
						# to multiple groups other than source_group

						each_source_file.group_set.remove(source_group_obj._id)

						if destination_group_obj._id not in each_source_file.group_set:
							each_source_file.group_set.append(destination_group_obj._id)

					# after doing copy/move (update of group_set), save object:
					each_source_file.save()

		else:
			print "\n No files found in source group."

	else:
		print "\n Either source/destination group does not exist."

except Exception as copy_move_files_err:
	print "\n Error occurred!!!! ", copy_move_files_err
