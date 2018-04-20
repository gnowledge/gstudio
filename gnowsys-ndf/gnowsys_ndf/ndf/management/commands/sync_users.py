import os
import io
import csv
from bson import ObjectId
# import time

from django.http import HttpRequest
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

# from gnowsys_ndf.settings import GSTUDIO_LOGS_DIR_PATH
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.filehive import *
from gnowsys_ndf.ndf.views.methods import create_grelation

# if not os.path.isdir(GSTUDIO_LOGS_DIR_PATH):
#   os.makedirs(GSTUDIO_LOGS_DIR_PATH)

warehouse_grp = node_collection.one({'_type': "Group", 'name': "warehouse"})
file_gst = node_collection.one({'_type': "GSystemType", 'name': "File"})
has_profile_pic_rt = node_collection.one({'_type': 'RelationType', 'name': unicode('has_profile_pic') })
auth_gst = node_collection.one({'_type': u'GSystemType', 'name': u'Author'})
auth_gst_id = auth_gst._id

# csv_log_file_name = 'user_details-' + str(time.strftime("%d-%b-%Y-%Hh-%Mm-%Ss")) + '.csv'
# csv_log_file = os.path.join(GSTUDIO_LOGS_DIR_PATH, csv_log_file_name)
# # To hold intermediate logs/errors
# csv_log_list = []

user_icons_dir_path = '/home/docker/code/display-pics/'


class Command(BaseCommand):
    help = "Creating user, author and attaching profile pics from CSV's.\n\t- CSV file schema: user_id, school_code, username, password, oid\n\t- CSV file-name-path needs to be passed either as argument or can be passed on demand/asked by script.\n\t- Please keep user-display-pics folder at following location:\n\t\t/home/docker/code/display-pics/"

    def handle(self, *args, **options):

        file_input = args[0] if args else ''

        if not file_input or not os.path.exists(file_input):
            file_input = raw_input("\nEnter below file path to be used:\n")

        techer_element_set = {'carbon', 'chlorine', 'copper', 'helium', 'iron', 'nitrogen', 'oxygen', 'silver', 'sodium', 'zinc'}

        if os.path.exists(file_input):

            msg = '\nFound file: "' + str(file_input) + '"\n\n'
            print msg

            cntr = 0
            with open(file_input, 'rb') as csvfile:
                # csv schema:
                # user_id, school_code, username, password, oid
                users = csv.reader(csvfile, delimiter=',')

                for index, (user_id, school_code, username, password, oid) in enumerate(users, 1):

                    print "\n\n[", index, "]. User: ",username
                    user_id = int(user_id)
                    set_icon = True
                    if User.objects.filter(id=user_id):
                        print '- Exists user with id: "%s" and username: "%s".'%(user_id, username)

                    else:
                        print "+ Creating User object for user [", user_id, "]: ", username
                        user_obj = User.objects.create_user(username=username, password=password, id=user_id)
                        user_id = user_obj.id

                    # temp_csv_log_list.append(str(user_id))

                    auth = node_collection.one({'_type': 'Author', 'created_by': user_id})
                    if auth:
                        print "- Exists Author object having '_id': ", auth._id

                    if not auth:
                        print "+ Creating Author object for user: ", username
                        auth = node_collection.collection.Author()
                        auth['name'] = unicode(username)
                        auth['member_of'] = [auth_gst_id]
                        auth['group_type'] = u"PUBLIC"
                        auth['edit_policy'] = u"NON_EDITABLE"
                        auth['created_by'] = user_id
                        auth['modified_by'] = user_id
                        auth['contributors'] = [user_id]
                        auth['group_admin'] = [user_id]
                        auth['agency_type'] = 'Student'
                        auth['origin'] = [{"script": "sync_users.py"}]
                        try:
                            auth['agency_type'] = 'Teacher' if (username.split('-')[1] in techer_element_set) else 'Student'
                        except Exception, e:
                            auth['agency_type'] = 'Student'
                        oid = ObjectId(oid)
                        auth['_id'] = oid
                        auth.save(groupid=oid)

                    try:
                        # if auth.relation_set:
                        #     for each_rel in auth.relation_set:
                        #         if each_rel and 'has_profile_pic' in each_rel:
                        #             set_icon = False
                        #             break
                        auth_grel = auth.get_relation(u'has_profile_pic', status=u'PUBLISHED')
                        if auth_grel.count():
                            print "- Exists GRelation 'has_profile_pic' object having '_id': ", auth_grel[0]._id
                        else:
                            attach_user_icon(username, auth)

                    except Exception, e:
                        print "!!! Error occurred: ", e
                        pass
                    # temp_csv_log_list.append(str(oid))
                    # csv_log_list.append(temp_csv_log_list)
                    cntr += 1

            print "\n\nDone with creating user's."
            print "\nTotal users processed: ", cntr

        else:
            msg = "\n!!! Please Enter correct file path. File does not exists at specified location.\n\n\n"
            print msg

        # with open(csv_log_file, 'wb') as csvfile:
        #     logwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        #     for each in csv_log_list:
        #         logwriter.writerow(each)
        #     print "\nDone with creating CSV: ", csv_log_file


def attach_user_icon(username, auth_node):
    if username and auth_node:

        icon_file_name = username[:username.rfind('-')] + '.png'
        file_obj_in_str = open(user_icons_dir_path + icon_file_name)

        img_file = io.BytesIO(file_obj_in_str.read())
        img_file.seek(0)
        fh_obj = filehive_collection.collection.Filehive()
        filehive_obj_exists = fh_obj.check_if_file_exists(img_file)
        file_gs_obj = None
        if not filehive_obj_exists:
            file_gs_obj = node_collection.collection.GSystem()

            file_gs_obj.fill_gstystem_values(
                                            request=HttpRequest(),
                                            name=unicode(icon_file_name),
                                            group_set=[warehouse_grp._id],
                                            # language=language,
                                            uploaded_file=img_file,
                                            created_by=1,
                                            member_of=file_gst._id,
                                            origin={'script': 'sync_users.py'},
                                            unique_gs_per_file=True
                                    )

            file_gs_obj.save(groupid=warehouse_grp._id)

        else:
            file_gs_obj = node_collection.one({'_type':"GSystem", '$or': [
                        {'if_file.original.id':filehive_obj_exists._id},
                        {'if_file.mid.id':filehive_obj_exists._id},
                        {'if_file.thumbnail.id':filehive_obj_exists._id}
                    ]})


        # create GRelation 'has_profile_pic' with respective Author nodes
        if file_gs_obj:
            gr_node = create_grelation(auth_node._id, has_profile_pic_rt, file_gs_obj._id)
            print '+ Created new GRelation "has_profile_pic" with file "%s"'%file_gs_obj.name
            # log_filewrite("\n File : " + str(file_gs_obj.name) + " -- linked -- "+ str(each_auth.name))

    else:
        print "!!! Either User or Author does NOT exist."