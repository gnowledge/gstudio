from dlkit_runtime import RUNTIME, PROXY_SESSION
from dlkit_gstudio.gstudio_user_proxy import GStudioRequest
from dlkit.primordium.id.primitives import Id
from gnowsys_ndf.ndf.models import node_collection
from dlkit.primordium.transport.objects import DataInputStream
import os
condition = PROXY_SESSION.get_proxy_condition()

# getting req object
req_obj = GStudioRequest(id=1)

condition.set_http_request(req_obj)
proxy = PROXY_SESSION.get_proxy(condition)

repository_service_mgr = RUNTIME.get_service_manager('REPOSITORY', proxy=proxy)
repo_lookup_session = repository_service_mgr.get_repository_lookup_session()

# Find Group 
grp_as_node_name = raw_input("Enter name of Group to add Assets*: ")
grp_as_node = node_collection.one({"_type": "Group", "name": unicode(grp_as_node_name.strip())})
# print "grp_as_repo: ",grp_as_repo
# print "grp_as_repo_id: ", grp_as_repo_id
grp_as_repo_id = Id(identifier=str(grp_as_node._id),
		namespace="repository.Repository",
		authority="GSTUDIO")
grp_as_repo = repo_lookup_session.get_repository(grp_as_repo_id)
print "\n Group: ", grp_as_node.name

# Create Asset 
assets_count = int(raw_input("Enter No. of Assets to be added*: "))
for i in xrange(0, assets_count):
	print "Adding Asset %d" % (i+1)
	asset_name = raw_input("Enter Asset Name*: ")
	asset_desc = raw_input("Enter Asset Description: ")
	if asset_name:
		asset_form = grp_as_repo.get_asset_form_for_create([])
		asset_form.display_name = asset_name
		asset_form.description = asset_desc
		asset_obj = grp_as_repo.create_asset(asset_form)
		print "\n Asset created successfully."

		# Create AssetContent 
		assetcontents_count = int(raw_input("Enter No. of AssetContents to be added*: "))
		for i in xrange(0, assetcontents_count):
			print "Adding AssetContent %d" % (i+1)
			asset_content_type_list = []
			assetcontent_form = grp_as_repo.get_asset_content_form_for_create(
				asset_obj.ident, asset_content_type_list)
			assetcontent_name = raw_input("Enter AssetContent Name*: ")
			assetcontent_desc = raw_input("Enter AssetContent Description: ")
			if assetcontent_name:
				assetcontent_form.display_name = assetcontent_name
				assetcontent_form.description = assetcontent_desc
				# To upload file
				filepath = raw_input("Enter path of file to be uploaded*: ")
				if os.path.exists(filepath):
					file_obj = open(filepath, 'r')
					assetcontent_form.set_data(DataInputStream(file_obj))
				assetcontent_obj = grp_as_repo.create_asset_content(assetcontent_form)
				print "\n AssetContent created successfully."
