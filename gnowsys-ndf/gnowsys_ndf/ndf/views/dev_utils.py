''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json

''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
from django.http import Http404

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import node_collection, triple_collection, gridfs_collection, NodeJSONEncoder

def query_doc(request, doc_id_or_name=None):

	result = ''

	try:
		oid = ObjectId(doc_id_or_name)
		document = node_collection.one({'_id': oid})
		result = json.dumps(document, cls=NodeJSONEncoder, sort_keys=True)
		result = [result]

	except:
		name = doc_id_or_name
		documents = node_collection.find({'name': unicode(name)})
		result = []
		for each_doc in documents:
			result.append(json.dumps(each_doc, cls=NodeJSONEncoder, sort_keys=True))

	return render_to_response(
        'ndf/dev_query_doc.html',
        {'result': result},
        context_instance=RequestContext(request)
    )
