"""Utilities for manipulating lists of ids"""
from dlkit.abstract_osid.osid.errors import NotFound
import collections

def move_id_ahead(element_id, reference_id, idstr_list):
    """Moves element_id ahead of referece_id in the list"""
    if element_id == reference_id:
        return idstr_list
    idstr_list.remove(str(element_id))
    reference_index = idstr_list.index(str(reference_id))
    print reference_index
    idstr_list.insert(reference_index, str(element_id))
    return idstr_list

def move_id_behind(element_id, reference_id, idstr_list):
    """Moves element_id behind referece_id in the list"""
    if element_id == reference_id:
        return idstr_list
    idstr_list.remove(str(element_id))
    reference_index = idstr_list.index(str(reference_id))
    idstr_list.insert(reference_index + 1, str(element_id))
    return idstr_list

def order_ids(new_id_list, old_idstr_list):
    compare = (
        lambda new_id_list, old_idstr_list: collections.Counter(new_id_list) == 
        collections.Counter(old_idstr_list))
    new_idstr_list = []
    for id_ in new_id_list:
        new_idstr_list.append(str(id_))
    if compare(new_idstr_list, old_idstr_list):
        return new_idstr_list
    else:
        raise NotFound()