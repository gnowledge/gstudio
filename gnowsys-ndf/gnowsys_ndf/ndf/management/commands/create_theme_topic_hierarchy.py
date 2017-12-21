''' -- imports from python libraries -- '''
import os
import csv
import json
import ast
import datetime
import time

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

# from django_mongokit import get_database
from django.template.defaultfilters import slugify
# from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.views.methods import create_gattribute
# from mongokit import IS

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import *

###################################################################

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files")

# collection = get_database()[Node.collection_name]
theme_gst       = node_collection.one({'_type': 'GSystemType', 'name': 'Theme' })
theme_item_gst  = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item' })
topic_gst       = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})
home_group      = node_collection.one({'_type': 'Group', 'name': 'home'})
home_group_id   = home_group._id
curricular_at   = node_collection.one({'_type': 'AttributeType', 'name': u'curricular'})
alignment_at    = node_collection.one({'_type': 'AttributeType', 'name': u'educationalalignment'})

nroer_team_id = 1

log_list = []  # To hold intermediate errors and logs
log_list.append("\n######### Script run on : " + time.strftime("%c") + " #########\n############################################################\n")


# utility function
def create_user_nroer_team():
    '''
    Check for the user: "nroer_team". If it doesn't exists, create one.
    '''
    global nroer_team_id

    if User.objects.filter(username="nroer_team"):
        nroer_team_id = get_user_id("nroer_team")

    else:
        info_message = "\n- Creating super user: 'nroer_team': "
        user = User.objects.create_superuser(username='nroer_team', password='nroer_team', email='nroer_team@example.com')

        nroer_team_id = user.id

        info_message += "\n- Created super user with following creadentials: "
        info_message += "\n\n\tusername = 'nroer_team', \n\tpassword = 'nroer_team', \n\temail = 'nroer_team@example.com', \n\tid = '" + str(nroer_team_id) + "'"
        print info_message
        log_list.append(info_message)


def get_user_id(user_name):
    '''
    Takes the "user name" as an argument and returns:
    - django "use id" as a response.
    else
    - returns False.
    '''
    try:
        user_obj = User.objects.get(username=user_name)
        return int(user_obj.id)
    except Exception as e:
        error_message = e + "\n!! for username: " + user_name
        print error_message
        log_list.append(str(error_message))
        return False


class Command(BaseCommand):
    help = "\
            Creating themes topic hierarchy\
            Schema for CSV has to be as follows:\
            column 1: CR/XCR\
            column 2: featured\
            column 3: alignment\
            column 4: content_org for topic\
            column 5: Theme/Collection\
            column 6: Theme-item (sub-theme)\
            column ... : ... (sub-theme)\
            column n-1: Theme-item (sub-theme)\
            column n: Topic\
            "

    def handle(self, *args, **options):
        try:
            for file_name in args:
                file_path = os.path.join(SCHEMA_ROOT, file_name)

                if os.path.exists(file_path):
                    info_message = "\n- CSV File (" + file_path + ") found!!!"
                    print info_message
                    log_list.append(str(info_message))

                else:
                    info_message = "\n- CSV File (" + file_path + ") not found!!!"
                    print info_message
                    log_list.append(str(info_message))
                    raise Exception(info_message)

                with open(file_path, 'rb') as f:

                    # calling methid to get nroer_team_id
                    create_user_nroer_team()

                    reader = csv.reader(f)

                    try:
                        i = 1
                        for index, each_row in enumerate(reader):

                            each_row = [cell.strip() for cell in each_row]

                            # print "\n each_row: ", each_row
                            # print "\n descrp: ",descrp,"\n"
                            create_theme_topic_hierarchy(each_row)

                            i = i + 1

                            print "\n", i ," rows successfully compiled"
                            print " ======================================================="

                            # if (i == 3):
                                # break
                    except csv.Error as e:
                        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

        except Exception as e:
            print str(e)
            log_list.append(str(e))

        finally:
            if log_list:

                log_list.append("\n ============================================================ End of Iteration ============================================================\n")
                # print log_list

                log_file_name = args[0].rstrip("csv") + "log"
                log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)
                # print log_file_path
                with open(log_file_path, 'a') as log_file:
                    log_file.writelines(log_list)


def create_theme_topic_hierarchy(row):
    """

    Args:
        row (list): each row of CSV
        e.g: ["CR/XCR", "featured", "alignment", "content_org", "Theme name", "theme item name", .., .., .... , "topic"]

    Returns:
        TYPE: Description
    """

    # print row
    language = row[0]   # language field will get populated in this case.
    curricular = row[1] # CR or XCR
    featured = int(row[2])   # 0 or 1
    alignment = row[3]  # like NCF
    content_org = row[4]
    theme_name = row[5] # theme-name like National Curriculum
    # topic_name = row[-1:]

    # --- Theme processing ---

    # fetching a theme node
    theme_node = node_collection.one({
                                    'name': {'$regex': "^" + unicode(theme_name) + "$", '$options': 'i'},
                                    'group_set': {'$in': [home_group_id]},
                                    'member_of': theme_gst._id
                                })

    # creating a new theme node:
    if not theme_node:
        theme_node = create_object(name=theme_name, member_of_id=theme_gst._id, featured=bool(featured), language=language)

        info_message = "- Created New Object : "+ str(theme_node.name) + "\n"
        print info_message
        log_list.append(str(info_message))


    # casting curricular field to bool:
    if curricular == "CR":
        curricular = True
    elif curricular == "XCR":
        curricular = False
    else:  # needs to be confirm
        curricular = False

    # if theme_node already has curricular as attribute, it will update it's value
    # otherwise it will create a new attribute:
    ga_node = create_gattribute(theme_node._id, curricular_at, curricular)

    info_message = "- Created ga_node : "+ str(ga_node.name) + "\n"
    print info_message
    log_list.append(str(info_message))

    ga_node = create_gattribute(theme_node._id, alignment_at, unicode(alignment))

    info_message = "- Created ga_node : "+ str(ga_node.name) + "\n"
    print info_message
    log_list.append(str(info_message))

    # --- END of Theme processing ---

    # --- theme-item and topic processing ---
    # from 5th item or 4rd index of row there will be start of theme-item and topic(at last)
    theme_item_topic_list = row[6:]

    # do not entertain any blank values here:
    theme_item_topic_list = [i for i in theme_item_topic_list if i]
    # print theme_item_topic_list

    topic_name = theme_item_topic_list.pop()  # Only 1 topic name, last item of row/list
    theme_item_list = theme_item_topic_list  # list of only theme-item name's, after pop

    # to initiate with parent node:
    parent_node = theme_node

    # theme-item procesing ---
    for each_theme_item in theme_item_list:
        # print each_theme_item

        # fetching a theme-item node
        theme_item_node = node_collection.one({
                                'name': {'$regex': "^" + unicode(each_theme_item) + "$", '$options': 'i'},
                                'group_set': {'$in': [home_group_id]},
                                'member_of': {'$in': [theme_item_gst._id]},
                                'prior_node': {'$in': [parent_node._id]}
                            })

        if not theme_item_node:

            theme_item_node = create_object(name=each_theme_item, member_of_id=theme_item_gst._id, prior_node_id=parent_node._id, language=language)

            info_message = "\n- Created theme-item : "+ str(theme_item_node.name) + "\n"
            print info_message
            log_list.append(str(info_message))

        else:
            info_message = "\n!! Theme Item : "+ str(theme_item_node.name) + " already exists!\n"
            print info_message
            log_list.append(str(info_message))

        # cheking for current theme-item's _id in collection_set of parent_node
        if not theme_item_node._id in parent_node.collection_set:
            add_to_collection_set(node_object=parent_node, id_to_be_added=theme_item_node._id)

        parent_node = theme_item_node

    # END of theme-item processing ---

    # topic processing ---

    # fetching a theme-item node
    topic_node = node_collection.one({
                        'name': {'$regex': "^" + unicode(topic_name) + "$", '$options': 'i'},
                        'group_set': {'$in': [home_group_id]},
                        'member_of': {'$in': [topic_gst._id]},
                        'prior_node': {'$in': [parent_node._id]}
                    })

    if not topic_node:
        topic_node = create_object(name=topic_name, \
                                 member_of_id=topic_gst._id, \
                                 prior_node_id=parent_node._id, \
                                 content_org=content_org,\
                                 language=language)

        info_message = "\n--- Created topic : "+ str(topic_node.name) + "\n"
        print info_message
        log_list.append(str(info_message))

    else:

        info_message = "\n!! Topic : "+ str(topic_node.name) + " already exists!\n"
        print info_message
        log_list.append(str(info_message))

    # cheking for current theme-item's _id in collection_set of parent_node
    if not topic_node._id in parent_node.collection_set:
        add_to_collection_set(node_object=parent_node, id_to_be_added=topic_node._id)


def create_object(name, member_of_id, prior_node_id=None, content_org=None, group_set_id=home_group_id, featured=None, language=('en', 'English')):

    node                = node_collection.collection.GSystem()
    node.name           = unicode(name)
    node.featured       = featured
    node.language       = eval(language)
    node.access_policy  = u"PUBLIC"
    node.status         = u"PUBLISHED"
    node.modified_by    = nroer_team_id
    node.created_by     = nroer_team_id
    node.contributors.append(nroer_team_id)
    node.group_set.append(group_set_id)
    node.member_of.append(member_of_id)

    if prior_node_id:
        node.prior_node.append(ObjectId(prior_node_id))

    if content_org:
        node.content_org = unicode(content_org)
        # node.content = org2html(content_org, file_prefix=ObjectId().__str__())
        node.content = unicode(content_org)

    node.save()

    return node


def add_to_collection_set(node_object, id_to_be_added):
    """Adds/updates a collection_set of object with provided object and id.

    Args:
        node_object (mongodb object)
        id_to_be_added (mongodb _id)

    Returns:
        updates an object but returns nothing
    """
    if not ObjectId(id_to_be_added) in node_object.collection_set and \
    node_object._id != id_to_be_added:

        node_collection.collection.update({
                '_id': node_object._id},
                {'$push': {'collection_set': ObjectId(id_to_be_added)} },
                upsert=False,
                multi=False
            )
