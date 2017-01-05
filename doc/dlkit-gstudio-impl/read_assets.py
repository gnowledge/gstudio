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
import ipdb; ipdb.set_trace()
rl = repository_service_mgr.get_asset_lookup_session_for_repository(d)
