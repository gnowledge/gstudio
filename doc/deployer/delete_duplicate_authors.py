from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import delete_node

# to find duplicate Author instances:
ag = node_collection.collection.aggregate([{'$match': {'_type': 'Author'}}, {'$group': {'_id': {'created_by': '$created_by',  }, 'objs': {'$push': '$$CURRENT'}, 'count': {'$sum': 1} }}, {'$match': {'count': {'$gt': 1}}},  ])

# aggregate all Author objects in a list
j = [x for sl in (i.get('objs') for i in ag['result']) for x in sl]
auth_dec = {}

# create a dict to have a list of ids to keep and delete to make decision:
for i in j:
    try:
        if i['created_at'] < auth_dec[i['created_by']]['old'].keys()[0]:
            auth_dec[i['created_by']]['new'].extends(auth_dec[i['created_by']]['old'])
            auth_dec[i['created_by']]['old'] = {i['created_at']: i['_id']}
        else:
            auth_dec[i['created_by']]['new'][i['created_at']] = i['_id']
    except:
        auth_dec[i['created_by']] = {'old': {i['created_at']: i['_id']}, 'new': {} }

# delete new instances:
for each_node_to_del_id in ([ sl for x in (i['new'].values() for i in auth_dec.values()) for sl in x ]):
    delete_node(each_node_to_del, deletion_type=1)

# Pending:
# - check for grelation `profile_pic` and other to take decision of which object to keep