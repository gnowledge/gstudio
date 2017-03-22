'''
Include all core python code/methods to process set/batch of data.
Possibly avoid (direct) queries.
'''

def get_dict_from_list_of_dicts(list_of_dicts,convert_objid_to_str=False):
    req_dict = {}
    [req_dict.update(d) for d in list_of_dicts]
    if convert_objid_to_str:
        str_val_dict = {key: map(str,val) for key, val in req_dict.items()}
        return str_val_dict
    return req_dict


def get_query_dict(**kwargs):
    '''
    Example:
    get_query_dict(created_by=1,
                   _type='GSystem',
                   member_of=[ObjectId('5752ad552e01310a05dca4a1'), ObjectId('5752ad552e01310a05dca4a3')])

    output:
    {
        '_type': {'$in': ['GSystem']},
        'created_by': {'$in': [1]},
        'member_of': {'$in': [ObjectId('5752ad552e01310a05dca4a1'), ObjectId('5752ad552e01310a05dca4a3')]}
    }
    '''
    temp_dict = {}
    for k, v in kwargs.items():
        temp_dict.update({k: {'$in':v if isinstance(v, list) else [v]}})
    # print temp_dict

    # just for testing, for time being. no query will be in this method/file.
    q = node_collection.find(temp_dict)
    # print q.count()

    return q


def add_to_list(list_to_update, value_to_append):
    '''
    adding <value_to_append> after checking it's presence in list_to_update
    '''
    if value_to_append not in list_to_update:
        list_to_update.append(value_to_append)
    return list_to_update
