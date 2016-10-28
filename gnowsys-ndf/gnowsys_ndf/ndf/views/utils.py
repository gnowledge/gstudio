def get_dict_from_list_of_dicts(list_of_dicts,convert_objid_to_str=False):
    req_dict = {}
    [req_dict.update(d) for d in list_of_dicts]
    if convert_objid_to_str:
        str_val_dict = {key: map(str,val) for key, val in req_dict.items()}
        return str_val_dict
    return req_dict
