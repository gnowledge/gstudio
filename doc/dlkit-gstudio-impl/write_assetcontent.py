from dlkit_runtime import RUNTIME, PROXY_SESSION
condition = PROXY_SESSION.get_proxy_condition()

# getting req object
from dlkit_gstudio.gstudio_user_proxy import GStudioRequest
req_obj = GStudioRequest(id=1)

condition.set_http_request(req_obj)
proxy = PROXY_SESSION.get_proxy(condition)


#================================================== GROUP as REPOSITORY ==================
repository_service_mgr = RUNTIME.get_service_manager('REPOSITORY', proxy=proxy)

# import ipdb; ipdb.set_trace()

# The following two calls are equivalent:
rl = repository_service_mgr.get_repository_lookup_session()
all_repos = rl.get_repositories()
all_repos = repository_service_mgr.get_repositories()
print "\nTotal repositories: ", all_repos.available()
test_repo = None
for each in all_repos:
	test_repo = each
d =  test_repo.get_id()
# import ipdb; ipdb.set_trace()
grp_assets = test_repo.get_assets()
print "\n Total Assets: ", grp_assets.available()
asset_obj = grp_assets.next()
print "\n Asset name: ", asset_obj.get_display_name().get_text()

# rl = repository_service_mgr.get_asset_lookup_session_for_repository(d)


# ================================================== ASSET CONTENT ========================

from dlkit.primordium.id.primitives import Id
from dlkit.primordium.transport.objects import DataInputStream

##### WRITE OPERATIONS

asset_content_type_list = []
'''
# Need to figure out this:
try:
    config = repo_obj._catalog._runtime.get_configuration()
    parameter_id = Id('parameter:assetContentRecordTypeForFiles@filesystem')
    asset_content_type_list.append(
        config.get_value_by_parameter(parameter_id).get_type_value())
except (AttributeError, KeyError):
    pass
'''
assetcontent_form = test_repo.get_asset_content_form_for_create(asset_obj.ident, asset_content_type_list)
assetcontent_form.description = 'AssetC description'
assetcontent_form.display_name = 'AssetC3 name'



# To upload file
# f = open('../../display-pics/black-ant.png', 'r')
# assetcontent_form.set_data(DataInputStream(f))

t = test_repo.create_asset_content(assetcontent_form)
