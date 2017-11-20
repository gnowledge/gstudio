from django_mongokit import get_database

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


def get_model_name(collection_obj):
	return collection_obj._meta.model_name