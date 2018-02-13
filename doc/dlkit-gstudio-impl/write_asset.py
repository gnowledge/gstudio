from dlkit_runtime import RUNTIME, PROXY_SESSION
condition = PROXY_SESSION.get_proxy_condition()

# getting req object
from dlkit_gstudio.gstudio_user_proxy import GStudioRequest
req_obj = GStudioRequest(id=1)

condition.set_http_request(req_obj)
proxy = PROXY_SESSION.get_proxy(condition)

# ================================================== ASSET ================================

##### WRITE OPERATIONS

repository_service_mgr = RUNTIME.get_service_manager('REPOSITORY', proxy=proxy)

rl = repository_service_mgr.get_repository_lookup_session()
all_repos = repository_service_mgr.get_repositories()
print "\nTotal repositories: ", all_repos.available()
test_repo = None
for each in all_repos:
	# print "\t- ", each.get_display_name().get_text()
	test_repo = each
print "\n Asset creating for Group: ", test_repo.get_display_name().get_text()
asset_form = test_repo.get_asset_form_for_create([])
asset_form.description = 'Asset description'
asset_form.display_name = 'Asset2 name'
asset_obj = test_repo.create_asset(asset_form)

