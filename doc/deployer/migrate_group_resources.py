import sys
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *
copy_files = False
move_files = False
clone_files = False
hard_clone_files = False

source_group_id = raw_input("Enter source group _id: ")
destination_group_id = raw_input("Enter destination group _id: ")

resource_type_input = raw_input("\nChoose Resource type:\n  1. File\n  2. Page\n  3. Asset\n 4. Cancel\nEnter option no. (1 or 2 or 3): ")
if resource_type_input == '1':
	resource_type_name = 'File'
elif resource_type_input == '2':
	resource_type_name = 'Page'
elif resource_type_input == '3':
	resource_type_name = 'Asset'
elif resource_type_input == '4':
	sys.exit()
else:
	print '\nYou have choosen wrong option. "File" will be default option selected in this case.'
	resource_type_name = 'File'

print '\nYou have choosen resource type: ', resource_type_name, '\n'

operation_choice = raw_input("\nChoose Operation type:\n  1. Copy\n  2. Move\n  3. Clone (Does NOT Clone GAttribute and GRelations)\n  4. Hard Clone (Clones GAttribute and GRelations)\n  5. Cancel\nEnter option no. (1 or 2 or 3 or 4 or 5): ")

if operation_choice == '1':
	copy_files = True
elif operation_choice == '2':
	move_files = True
elif operation_choice == '3':
	clone_files = True
elif operation_choice == '4':
	hard_clone_files = True
elif operation_choice == '5':
	sys.exit()
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
											})

		if source_grp_files.count():

			copy_move_confirmation = raw_input("Total files to be processed: "+ str(source_grp_files.count())+". Enter y/Y to continue: ")

			if copy_move_confirmation == 'y' or copy_move_confirmation == 'Y':
				for each_source_file in source_grp_files:

					if copy_files:
						if destination_group_obj._id not in each_source_file.group_set:
							each_source_file.group_set.append(destination_group_obj._id)
						each_source_file.save()

					elif move_files:
						# Remove source_group_id and add destination_group_id
						# This is to prevent file that are cross-published
						# to multiple groups other than source_group
						each_source_file.group_set.remove(source_group_obj._id)

						if destination_group_obj._id not in each_source_file.group_set:
							each_source_file.group_set.append(destination_group_obj._id)
						each_source_file.save()

					elif clone_files:
						print "\n Preparing to Clone object. Please wait."
						each_new_file = create_clone(1, each_source_file, destination_group_obj._id)

					elif hard_clone_files:
						print "\n Preparing to Hard Clone object. Please wait."
						each_new_file = replicate_resource(None, each_source_file, destination_group_obj._id)
					# after doing copy/move/object (update of group_set), save object:
		else:
			print "\n No files found in source group."
	else:
		print "\n Either source or destination group does not exist."

except Exception as copy_move_files_err:
	print "\n Error occurred!!!! ", copy_move_files_err
