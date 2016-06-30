from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import delete_node

ce_gst = node_collection.one({'_type':"GSystemType", 'name': "CourseEventGroup"})
group_cur = node_collection.find({'_type': u'Group', 'member_of': ce_gst._id})

print "Total CE found --- ",group_cur.count()
def delete_res(del_cur):

    for each in del_cur:
        # print "\n=== deleted: ===\n", each.name , "---", each.member_of_names_list
        del_status, del_status_msg = delete_node(
            node_id=each._id,
            deletion_type=1
        )
        # print "\n---------\n",del_status, "--", del_status_msg
        if not del_status:
            print "*"*80
            print "\n Error node: _id: ", each._id, " , name: ", each.name, " type: ", each.member_of_names_list
            print "*"*80


for group_obj in group_cur:
    confirmation = raw_input("Delete group: "+ str(group_obj.name)+ ". Enter (y/Y) to continue or (n) to skip this group: ")
    if confirmation == 'Y' or confirmation == 'y':
        # Fetch all nodes that have ONLY group_obj _id in its group_set.

        # grp_res = node_collection.find({'group_set':{'$size':1}, 'group_set': group_obj._id})
        grp_res = node_collection.find({ '$and': [ {'group_set':{'$size':1}}, {'group_set': {'$all': [ObjectId(group_obj._id)]}} ] })

        print "\n Total resources to be deleted", grp_res.count()
        # Delete all objects of the cursor grp_res

        delete_res(grp_res)
        print "\n Deleting group: "
        del_status, del_status_msg = delete_node(
            node_id=group_obj._id,
            deletion_type=1
        )
    else:
        continue
