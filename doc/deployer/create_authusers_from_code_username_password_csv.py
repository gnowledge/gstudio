import os
import csv
import time

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
User = get_user_model()

from gnowsys_ndf.settings import GSTUDIO_LOGS_DIR_PATH
from gnowsys_ndf.ndf.models import Author, node_collection

if not os.path.isdir(GSTUDIO_LOGS_DIR_PATH):
	os.makedirs(GSTUDIO_LOGS_DIR_PATH)

log_file_name = 'create_authusers_from_code_username_password_csv.log'
log_file = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)

csv_log_file_name = 'user_details-' + str(time.strftime("%d-%b-%Y-%Hh-%Mm-%Ss")) + '.csv'
csv_log_file = os.path.join(GSTUDIO_LOGS_DIR_PATH, csv_log_file_name)

file_input = raw_input("\nEnter below file to be used:\n")

script_start_str = "######### Script ran on : " + time.strftime("%c") + " #########\n------------------------------------------------------------\n"

# To hold intermediate logs/errors
csv_log_list = []
log_list = []

log_list.append(script_start_str)

def log_print(log_string):
    try:
        log_list.append(log_string)
        print log_string

    except:
        error_message = '\n !! Error while doing log and print.\n\n'
        print error_message
        log_list.append(error_message)


if os.path.exists(file_input):

    msg = '\nFound file: "' + str(file_input) + '"\n\n'
    log_print(msg)

    with open('/home/docker/code/user-details/test.csv', 'rb') as csvfile:
            users = csv.reader(csvfile, delimiter=';')

            for code, username, password in users:
                temp_csv_log_list = []
                temp_csv_log_list.append(code)
                temp_csv_log_list.append(username)
                temp_csv_log_list.append(password)

                try:
                    msg = '\nCreating user: ' + str(username)
                    log_print(msg)
                    user_obj = User.objects.create_user(username=username, password=password)

                    assert authenticate(username=username, password=password)

                    user_id = user_obj.id

                    msg = '\n\t-- User ' + str(username) + ' successfully created.'
                    log_print(msg)
                    temp_csv_log_list.append(str(user_id))
                    temp_csv_log_list.append('success')

                    msg = '\n\tCreating author with username: ' + str(username) + ' and created_by (django user id): ' + str(user_id)
                    log_print(msg)

                    auth_obj = Author.create_author(user_id)

                    msg = '\n\t-- author _id: ' + str(auth_obj._id)
                    log_print(msg)
                    temp_csv_log_list.append(str(auth_obj._id))


                except Exception, e:
                    msg = '\n\t!! There was a problem creating the user: ' + str(username)
                    log_print(msg)
                    temp_csv_log_list.append('-')
                    temp_csv_log_list.append(str(e).strip())
                    temp_csv_log_list.append('-')

                    msg = '\n\t!! Error : ' + str(e) + '\n'
                    log_print(msg)

                csv_log_list.append(temp_csv_log_list)

else:
	msg = "\nPlease Enter correct file path. File does not exists at specified location !!\n\n\n"
	log_print(msg)


log_list.append("\n========================= End of Iteration =========================\n\n\n")


with open(log_file, 'a') as lf:
    lf.writelines(log_list)


with open(csv_log_file, 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    for each in csv_log_list:
        spamwriter.writerow(each)

