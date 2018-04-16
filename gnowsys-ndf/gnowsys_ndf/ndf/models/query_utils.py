from gnowsys_ndf.ndf.models import *
# from gnowsys_ndf.ndf.models.db_utils import get_collection_hierarchy
# Conventions followed for names w.r.t mongoDB:
# {"key": "value"}

def get_unique_values(collection_cls_name, field_key, db_collection_name=''):
    if not db_collection_name:
        db_collection_name = db_utils.get_db_collection_name_from_cls(collection_cls_name)
    # print collection_dict
    # print db[collection_dict[collection_cls_name]].find().distinct(field_key)
    query_type_dict = {'_type': collection_cls_name} if collection_cls_name else {}
    return db[db_collection_name].find(query_type_dict).distinct(field_key)


def get_documents(collection_cls_name, db_collection_name='', **kwargs):
    if not db_collection_name:
        db_collection_name = db_utils.get_db_collection_name_from_cls(collection_cls_name)

    # if field_value:
        # query_dict = {'_type': collection_cls_name, field_key: field_value} if collection_cls_name else {}
    query_dict = {'_type': collection_cls_name}
    query_dict.update(kwargs)
    query_dict = db_utils.cast_model_values_data_type(collection_cls_name, **query_dict)

    return db[db_collection_name].find(query_dict)
