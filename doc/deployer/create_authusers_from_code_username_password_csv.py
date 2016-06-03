import os
import csv
import time
from bson import ObjectId
from django.contrib.auth.models import User
from gnowsys_ndf.settings import GSTUDIO_LOGS_DIR_PATH
from gnowsys_ndf.ndf.models import Author, node_collection

if not os.path.isdir(GSTUDIO_LOGS_DIR_PATH):
	os.makedirs(GSTUDIO_LOGS_DIR_PATH)

auth_gst = node_collection.one({'_type': u'GSystemType', 'name': u'Author'})
auth_gst_id = auth_gst._id
csv_log_file_name = 'user_details-' + str(time.strftime("%d-%b-%Y-%Hh-%Mm-%Ss")) + '.csv'
csv_log_file = os.path.join(GSTUDIO_LOGS_DIR_PATH, csv_log_file_name)
file_input = raw_input("\nEnter below file path to be used:\n")
# To hold intermediate logs/errors
csv_log_list = []

if os.path.exists(file_input):
    msg = '\nFound file: "' + str(file_input) + '"\n\n'
    print msg
    with open(file_input, 'rb') as csvfile:
        users = csv.reader(csvfile, delimiter=';')
        for school_code, username, password in users:
            temp_csv_log_list = [school_code, username, password]
            user_obj = User.objects.create_user(username=username, password=password)
            user_id = user_obj.id
            temp_csv_log_list.append(str(user_id))
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
            auth['_id'] = ObjectId()
            auth.save(groupid=auth['_id'])
            temp_csv_log_list.append(str(auth['_id']))
            csv_log_list.append(temp_csv_log_list)

    print "\n\nDone with creating user's.\nNow creating CSV..."

else:
    msg = "\nPlease Enter correct file path. File does not exists at specified location !!\n\n\n"
    print msg

with open(csv_log_file, 'wb') as csvfile:
    logwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    for each in csv_log_list:
        logwriter.writerow(each)

print "calculating count..."
print "Total users created: ", len(csv_log_list)