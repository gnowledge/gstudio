import os
import csv
from bson import ObjectId
# import time

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from gnowsys_ndf.ndf.models import Author, node_collection
# from gnowsys_ndf.settings import GSTUDIO_LOGS_DIR_PATH

# if not os.path.isdir(GSTUDIO_LOGS_DIR_PATH):
# 	os.makedirs(GSTUDIO_LOGS_DIR_PATH)

auth_gst = node_collection.one({'_type': u'GSystemType', 'name': u'Author'})
auth_gst_id = auth_gst._id

# csv_log_file_name = 'user_details-' + str(time.strftime("%d-%b-%Y-%Hh-%Mm-%Ss")) + '.csv'
# csv_log_file = os.path.join(GSTUDIO_LOGS_DIR_PATH, csv_log_file_name)
# # To hold intermediate logs/errors
# csv_log_list = []


class Command(BaseCommand):
    help = "\n\tFor saving data in gstudio DB from NROER schema files. This will create 'File' type GSystem instances.\n\tCSV file condition: The first row should contain DB names.\n"

    def handle(self, *args, **options):

        file_input = args[0] if args else ''

        if not file_input or not os.path.exists(file_input):
            file_input = raw_input("\nEnter below file path to be used:\n")

        if os.path.exists(file_input):

            msg = '\nFound file: "' + str(file_input) + '"\n\n'
            print msg

            cntr = 0
            with open(file_input, 'rb') as csvfile:
                # csv schema:
                # user_id, school_code, username, password, oid
                users = csv.reader(csvfile, delimiter=',')


                for user_id, school_code, username, password, oid in users:

                    # temp_csv_log_list = [school_code, username, password]
                    # temp_csv_log_list = [user_id, school_code, username, password, oid]
                    # print temp_csv_log_list

                    user_id = int(user_id)

                    if User.objects.filter(id=user_id):
                        print "\nUser with id: '",user_id,"' and username: '",username,"' already exists."

                    else:
                        print "\nCreating User object for user: ", username
                        user_obj = User.objects.create_user(username=username, password=password, id=user_id)
                        user_id = user_obj.id

                    # temp_csv_log_list.append(str(user_id))

                    if not node_collection.one({'_type': 'Author', 'created_by': user_id}):
                        print "\nCreating Author object for user: ", username
                        auth = node_collection.collection.Author()
                        auth['name'] = unicode(username)
                        auth['member_of'] = [auth_gst_id]
                        auth['group_type'] = u"PUBLIC"
                        auth['edit_policy'] = u"NON_EDITABLE"
                        auth['created_by'] = user_id
                        auth['modified_by'] = user_id
                        auth['contributors'] = [user_id]
                        auth['group_admin'] = [user_id]
                        auth['agency_type'] = "Student"
                        oid = ObjectId(oid)
                        auth['_id'] = oid
                        auth.save(groupid=oid)
                    # temp_csv_log_list.append(str(oid))
                    # csv_log_list.append(temp_csv_log_list)
                    cntr += 1

            print "\n\nDone with creating user's."
            print "\nTotal users processed: ", cntr

        else:
            msg = "\nPlease Enter correct file path. File does not exists at specified location !!\n\n\n"
            print msg

        # with open(csv_log_file, 'wb') as csvfile:
        #     logwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        #     for each in csv_log_list:
        #         logwriter.writerow(each)
        #     print "\nDone with creating CSV: ", csv_log_file

