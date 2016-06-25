import os
import subprocess

from django.core.management.base import BaseCommand

from gnowsys_ndf.ndf.models import *

nodelist = []
user_list = []
group_set = []
member_of = []
prior_node_list = []
post_node_list = []
fs_file_ids = []
Gattribute_ids = []
Grelations_ids = []
collection_set_ids = []
Gattribute_value = []
Grelations_value = []
class Command(BaseCommand):


        def handle(self, *args, **options):

            print "Enter Group Name whose data backup is to be taken"
            Group_name = raw_input()
            #db = get_database()
            #files = db['fs.files']
            #chunks = db['fs.chunks']
            #follow the recursive stretagy go till the depth of the snode take their induvidual dumps and then finally of the main groups
            Group_node = node_collection.find_one({"_type":"Group","name":unicode(Group_name)})
            if Group_node:
                #all the nodes having Group id
                print "Enter name of the database"
                db_name=raw_input()
                nodes = node_collection.find({"group_set":ObjectId(Group_node._id)})

                user_list.extend(Group_node.author_set)
                user_list.extend(Group_node.group_admin)

                for i in nodes:

                    nodelist.append(i._id)
                    get_page_node_details(i)
                    # get_file_node_details(i)
                    if i.collection_set:
                        get_collection(i.collection_set)
                    if i.prior_node:
                        get_p_node(i.prior_node)
                    if i.post_node:
                        get_pst_node(i.post_node)
                    if i.attribute_set:
                        #fetch attribute_type
                        for j in i.attribute_set:
                            at_type = node_collection.find_one({"_type":"AttributeType","name":unicode(j.keys()[0])})
                            attr = triple_collection.find_one({"_type": "GAttribute", "subject": i._id, "attribute_type.$id": at_type._id})
                            if attr:
                                Gattribute_ids.append(attr._id)
                                if type(attr.object_value) not in  [datetime.datetime,unicode,int] :
                                    try:
                                        Gattribute_value.extend(attr.object_value)
                                    except:
                                        Gattribute_value.append(attr.object_value)

                    if i.relation_set:
                        for j in i.relation_set:
                            if unicode(j.keys()[0]):
                                rel_node = node_collection.find_one({"$or":
                                                      [ {"name":unicode(j.keys()[0])},  {"inverse_name":unicode(j.keys()[0])}],"_type":"RelationType"})

                                value_node = triple_collection.find_one({"_type": "GRelation", "subject": i._id, "relation_type.$id": rel_node._id})
                                if value_node:
                                    Grelations_ids.append(value_node._id)
                                    if type(attr.object_value) not in  [datetime.datetime,unicode,int] :
                                        try:
                                            Grelations_value.extend(value_node.right_subject)
                                        except:
                                            Grelations_value.append(value_node.right_subject)
                query_list = []
                commandlist=[]
                query ={}




                #the final list
                # take rcs of every thing
                node_list = []
                triple_list = []
                # final_list.extend(Gattribute_value)
                node_list.extend(collection_set_ids)
                node_list.extend(nodelist)
                #final_list.extend(fs_file_ids)
                triple_list.extend(Grelations_value)
                triple_list.extend(Grelations_ids)
                triple_list.extend(Gattribute_ids)
                #check if rcs dir exists if not create it
                PROJECT_ROOT = os.path.abspath(os.path.dirname(os.pardir))
                rcs_path = os.path.join(PROJECT_ROOT, 'gnowsys_ndf/copy_rcs')
                path_val = os.path.exists(rcs_path)
                if path_val == False:
                    os.makedirs(rcs_path)

                node_data = node_collection.find({"_id":{"$in":node_list}})

                for i in node_data:
                    #get rcs files path and copy them to the current dir:
                    hr = HistoryManager()
                    try:
                        path = hr.get_file_path(i)
                        path = path + ",v"
                        cp = "cp  -u " + path + " " +" --parents " + rcs_path + "/"
                        subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
                    except:
                        pass

                triple_node = triple_collection.find({"_id":{"$in":triple_list}})
                for i in triple_node:
                    #get rcs files path and copy them to the current dir:
                    hr = HistoryManager()
                    try:
                        path = hr.get_file_path(i)
                        path = path + ",v"
                        cp = "cp  -u " + path + " " +" --parents " + rcs_path + "/"
                        subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
                    except:
                        pass


def get_file_node_details(node):
    for i in node:
        if 'fs_file_ids' == i:
            fs_file_ids.extend(node['fs_file_ids'])
        if 'group_set' == i:
            for j in node.group_set:
                group_node = node_collection.find_one({"_id":ObjectId(j)})
                if group_node:
                    if group_node._type != unicode('Author'):
                        group_set.extend(group_node.group_set)
        if 'author_set' == i:
                user_list.extend(node.author_set)
    return node

def get_page_node_details(node):
    for i in node:
        if 'group_set' == i:
            for j in node.group_set:
                group_node = node_collection.find_one({"_id":ObjectId(j)})
                if group_node:
                    if group_node._type != unicode('Author'):
                        group_set.extend(group_node.group_set)
        if 'author_set' == i:
                user_list.extend(node.author_set)
    return node


def get_collection_node_ids(collection_list):
    # loop and call
    subset_collection_set   = []
    for i in collection_list:
        collection_set_ids.append(i)
        subset_collection_set.extend(get_new_collection_set(i))
    if subset_collection_set:
        get_collection(subset_collection_set)

def get_collection(collection_list):
    get_collection_node_ids(collection_list)


def get_new_collection_set(i):
    new_node = node_collection.find_one({"_id":ObjectId(i)})
    subset_collection_set = []
    if new_node:
            if new_node.collection_set:
                subset_collection_set.extend(new_node.collection_set)
    return subset_collection_set

def get_prior_node(p_node):
    subset_p_node = []
    for i in p_node:
        prior_node_list.append(i)
        new_node = node_collection.find_one({"_id":ObjectId(i)})
        if new_node:
            if new_node.prior_node:
                subset_p_node.extend(new_node.prior_node)
    if subset_p_node:
        get_p_node(subset_p_node)

def get_p_node(p_node):
    get_prior_node(p_node)


def get_post_node(post_node):
    subset_post_node = []
    for i in post_node:
        post_node_list.append(i)
        new_node = node_collection.find_one({"_id":ObjectId(i)})
        if new_node:
            if new_node.post_node:
                subset_post_node.extend(new_node.prior_node)
    if subset_post_node:
        get_p_node(subset_p_node)

def get_pst_node(post_node):
    get_post_node(post_node)


