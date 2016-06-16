import csv
import os
import string
from random import choice
from bson import ObjectId

all_small_letters = string.letters.lower()

# folder structure
data_path = '/data'
csvs_folder_name = 'user-csvs'
csvs_folder_path = os.path.join(data_path, csvs_folder_name)

if not os.path.exists(csvs_folder_path):
	os.makedirs(csvs_folder_path)

# generate random characters:
# print (''.join(choice(all_small_letters) for i in xrange(6)))

# statecode_cum_range_dict = {'mz': (1, 200), 'rj': (201, 500), 'ct': (501, 800), 'tg': (801, 1100), 'sp': (1100, 1300)}

statecode_range_dict = {'mz': (1, 200), 'rj': (1, 300), 'ct': (1, 300), 'tg': (1, 300), 'sp': (1, 300)}

state_startwith_dict = {'mz': 0, 'rj': 200, 'ct': 500, 'tg': 800, 'sp': 1100}


# ------ for generating school codes ------
statecode_schoolcodes_dict = {}

for state, school_range in statecode_range_dict.iteritems():

    state_codes_list = []
    last = school_range[1] + 1

    append = state_codes_list.append
    for school_no in xrange(school_range[0], last):
        append(state + str(school_no))

	statecode_schoolcodes_dict[state] = state_codes_list

	state_csv_file_path = os.path.join(csvs_folder_path, state)
	if not os.path.exists(state_csv_file_path):
		os.makedirs(state_csv_file_path)
	state_csv_file_name = os.path.join(state_csv_file_path, state + '_school_codes.csv' )

    # writting to file
    with open(state_csv_file_name, 'w') as csvfile:
        statewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for each_sc in state_codes_list:
            statewriter.writerow([each_sc])
    # print state_codes_list

# print statecode_schoolcodes_dict

# ------ for generating school codes ------
# -----------------------------------------


st_usernames = '/data/user-csvs/student-usernames.csv'
tc_usernames = '/data/user-csvs/teacher-usernames.csv'

def create_users_csv(csv_file_name_path, code, start_user_id, last_user_id, user_type='users'):
    with open(csv_file_name_path, 'rb') as csvfile:
        all_rows = csv.reader(csvfile, delimiter=';')
        current_user_id = start_user_id
        complete_data_list = []
        append = complete_data_list.append
        for each_row in all_rows:

            # csv schema:
            # user_id, school_code, username, password, oid

            # user-id
            temp_row_list = [current_user_id]
            current_user_id += 1

            # school code
            temp_row_list.append(code)

            # username = each_row[0] + '-' + code
            temp_row_list.append(each_row[0] + '-' + code)

            # password
            temp_row_list.append(''.join(choice(all_small_letters) for i in xrange(6)))

            # author ObjectId
            temp_row_list.append(ObjectId())

            # print temp_row_list
            append(temp_row_list)

            if current_user_id > last_user_id:
                break
            else:
                continue

        state_code = code[:2]
        state_csv_file_path = os.path.join(csvs_folder_path, state_code)
        if not os.path.exists(state_csv_file_path):
            os.makedirs(state_csv_file_path)

        # writting to file
        mode = 'a' if (user_type == 'student') else 'w'

        user_type = 'users'
        state_csv_file_name = os.path.join(state_csv_file_path, code + '_' + user_type + '.csv' )

        with open(state_csv_file_name, mode) as csvfile:
            statewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for each_user in complete_data_list:
                statewriter.writerow(each_user)
        # print complete_data_list

user_id_creation_order = ['cc', 'mz', 'rj', 'ct', 'tg', 'sp']
# user_id_creation_order = ['cc', 'mz']

create_users_csv(st_usernames, 'cc', start_user_id=2, last_user_id=1000, user_type='users')
print "\n\nCreating csv's for : cc"
user_id_creation_order.remove('cc')
print "\tcreated csv for : cc"

user_type_list = ['teacher', 'student']
usertype_csvfile_dict = {'teacher': tc_usernames, 'student': st_usernames}
teacher_student_start_perschool = {'teacher': 1, 'student': 51}
teacher_student_user_splitup = {'teacher': 50, 'student': 1000}

for code in user_id_creation_order:
    print "\n\nCreating csv's for : ", code

    school_codes_list = statecode_schoolcodes_dict[code]

    for each_sc in school_codes_list:

        for user_type, csvfile in usertype_csvfile_dict.iteritems():

            # print "each_sc: ", each_sc, each_sc[2:], state_startwith_dict[each_sc[:2]]
            # print int(each_sc[2:]) + state_startwith_dict[each_sc[:2]]
            last_user_id = 1000 + (( int(each_sc[2:]) + state_startwith_dict[each_sc[:2]] ) * 1050 )
            start_user_id = last_user_id - 1050
            start_user_id += teacher_student_start_perschool[user_type]
            if user_type == "teacher":
                last_user_id = start_user_id + teacher_student_user_splitup[user_type] - 1

            # print "each_sc : ", each_sc
            # print "start_user_id : ", start_user_id
            # print "last_user_id : ", last_user_id
            # print "user_type : ", user_type
            # print "csvfile : ", csvfile
            # print "\n"
            create_users_csv(csvfile, each_sc, start_user_id, last_user_id, user_type)
            print "\tcreated csv for :", each_sc
