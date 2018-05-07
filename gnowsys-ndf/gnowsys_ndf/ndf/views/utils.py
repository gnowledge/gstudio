'''
Include all core python code/methods to process set/batch of data.
Possibly avoid (direct) queries.
'''
import bson
import datetime

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


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
    # just for testing, for time being. no query will be in this method/file.
    q = node_collection.find(temp_dict)

    return q

def add_to_list(list_to_update, value_to_append):
    '''
    adding <value_to_append> after checking it's presence in list_to_update
    '''
    if isinstance(value_to_append, list):
        list_to_update_copy = []
        [list_to_update_copy.append(each_val) for each_val in value_to_append if each_val not in list_to_update]
        list_to_update.extend(list_to_update_copy)
        return list_to_update
    if value_to_append not in list_to_update:
        list_to_update.append(value_to_append)
    return list_to_update


def cast_to_data_type(value, data_type):
    '''
    This method will cast first argument: "value" to second argument: "data_type" and returns casted value.
    '''

    if (data_type in ["basestring", "unicode"]) and isinstance(value, (str, unicode)):
        value = value.strip()
    casted_value = value

    if data_type in [unicode, "unicode"]:
        casted_value = unicode(value)

    elif data_type in [basestring, "basestring"]:
        casted_value = unicode(value)

    elif (data_type in [int, "int"]) and str(value):
        casted_value = int(value) if (str.isdigit(str(value))) else value

    elif (data_type in [float, "float"]) and str(value):
        casted_value = float(value) if (str.isdigit(str(value))) else value

    elif (data_type in [long, "long"]) and str(value):
        casted_value = long(value) if (str.isdigit(str(value))) else value

    # converting unicode to int and then to bool
    elif data_type in [bool, "bool"] and str(value):
        if (str.isdigit(str(value))):
            casted_value = bool(int(value))
        elif unicode(value) in [u"True", u"False"]:
            if (unicode(value) == u"True"):
                casted_value = True
            elif (unicode(value) == u"False"):
                casted_value = False

    elif (data_type in [list, "list"] or isinstance(data_type, list)):

        if isinstance(value, str):
            value = value.replace("\n", "").split(",")

        if not isinstance(value, list):
            value = [value]
        # check for complex list type like: [int] or [unicode] or [ObjectId]
        if isinstance(value, list) and len(value) and isinstance(data_type[0], type):
            casted_value = [data_type[0](i) for i in value if i]
            casted_value = list(set(casted_value))
        # else:  # otherwise normal list
        #     casted_value = [i.strip() for i in value if i]

    elif data_type in [datetime.datetime, "datetime.datetime"]:
        # "value" should be in following example format
        # In [10]: datetime.strptime( "11/12/2014", "%d/%m/%Y")
        # Out[10]: datetime(2014, 12, 11, 0, 0)
        casted_value = datetime.strptime(value, "%d/%m/%Y")

    elif data_type in [bson.objectid.ObjectId, 'bson.objectid.ObjectId']:
        casted_value = ObjectId(value)

    return casted_value


def replace_in_list(list_to_update, old_val, new_val, append_if_not=False):
    '''
    Replace <old_value> with <new_value> in list_to_update, if exists.
    Else if append_if_not flag is passed True,
    add the <new_val> in list_to_update
    '''
    try:
        list_to_update[list_to_update.index(old_val)] = new_val
    except ValueError:
        if append_if_not:
            add_to_list(list_to_update, new_val)
    # finally:
    #     return list_to_update

def merge_lists_and_maintain_unique_ele(list_a, list_b, advanced_merge=False):
    '''
    Merge 2 lists list_a and list_b and remove
    duplicate elements and return the result list.
    '''
    if advanced_merge:
        concat_list = list_a + list_b
        merged_list = []
        flat_dict = {}
        for each_dict in concat_list:
            for key,val in each_dict.iteritems():
                if isinstance(val, ObjectId):
                    if key in flat_dict:
                        flat_dict[key].extend(val)
                    else:
                        flat_dict.update({key:val})
        for key,val in flat_dict.iteritems():
            merged_list.append({key:val})
    else:
        merged_list = list(set(list_a) | set(list_b))
    return merged_list


def reverse_dict_having_listvalues(dict_listvalues):
    '''
    >>> reverse_dict_having_listvalues({ 'a': ['b', 'c'], 'd': ['e', 'f'] })
    >>> {'c': 'a', 'f': 'd', 'b': 'a', 'e': 'd'}
    '''
    return {value: key for key in dict_listvalues for value in dict_listvalues[key]}
