try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import get_group_name_id, get_language_tuple
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_LANGUAGE

asset_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Asset'})

def create_asset(group_id, asset_name, **kwargs):
	asset_obj = node_collection.find_one({'member_of': asset_gst._id, 'group_set': group_id,
				'name': {'$regex': str(asset_name), '$options': "i"}})
	if asset_obj is None:
		asset_obj = node_collection.collection.GSystem()
		asset_obj.fill_node_values(**kwargs)
		asset_obj.group_set = [ObjectId(group_id)]
		asset_obj.member_of = [asset_gst._id]
		asset_obj.name = asset_name
		# print asset_obj
		asset_obj.save()
	return asset_obj
