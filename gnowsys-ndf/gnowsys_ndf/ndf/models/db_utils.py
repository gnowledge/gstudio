import bson

from django_mongokit import get_database
from gnowsys_ndf.ndf.views.utils import reverse_dict_having_listvalues, cast_to_data_type

db = get_database()


def get_collection_names():
	# [u'Filehives', u'Benchmarks', u'Buddies', u'Counters', u'Triples', u'Nodes']
	return db.collection_names()


def get_collection_child_names(collection_name='Nodes'):
	# get_collection_child_names('Nodes')
	# [u'MetaType', u'GSystemType', u'RelationType', u'AttributeType', u'GSystem', u'Group', u'ToReduceDocs', u'Author']
	return db[collection_name].find().distinct('_type')


def get_all_collection_child_names():
	# [u'Filehive', u'Benchmark', u'Buddy', u'Counter', u'GAttribute', u'GRelation', u'MetaType', u'GSystemType', u'RelationType', u'AttributeType', u'GSystem', u'Group', u'ToReduceDocs', u'Author']
	return sum([get_collection_child_names(i) for i in get_collection_names()], [])


def get_collection_hierarchy():
	# returns following JSON:
	# {"Filehives": ["Filehive"], "Triples": ["GAttribute", "GRelation"], "Buddies": ["Buddy"], "Benchmarks": ["Benchmark"], "Nodes": ["MetaType", "GSystemType", "RelationType", "AttributeType", "GSystem", "Group", "ToReduceDocs", "Author"], "Counters": ["Counter"]}
	return {k: get_collection_child_names(k) for k in get_collection_names()}


def get_model_name(collection_obj):
	return collection_obj._meta.model_name


def get_model_structure(collection_name):
	# collection_name: str
	from gnowsys_ndf.ndf.models import *
	collection_str = getattr(eval(collection_name), 'structure')
	collection_str.update({'_id': bson.objectid.ObjectId})
	return collection_str

def cast_model_values_data_type(collection_cls_name, **kwargs):
	return { k: cast_to_data_type(v, get_model_structure(collection_cls_name)[k]) for k, v in kwargs.iteritems() }


def get_db_collection_name_from_cls(collection_cls_name):
	return reverse_dict_having_listvalues(get_collection_hierarchy())[collection_cls_name]
