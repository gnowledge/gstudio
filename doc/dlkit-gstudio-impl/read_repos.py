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
all_repos = repository_service_mgr.get_repositories()
print "\nTotal repositories: ", all_repos.len()
test_repo = None
for each in all_repos:
	print "\t- ", each.get_display_name().get_text()
	test_repo = each
# al = repository_service_mgr.get_asset_lookup_session()
al_repo = repository_service_mgr.get_asset_lookup_session_for_repository(test_repo.get_repository_id())


# asset_by_id = repository_service_mgr.get_asset_content(ObjectId('57926e16a6127d01f8e85946'))
# print "\nAsset found:  ", asset_by_id



# ============================================================= try outs

# repo_obj = all_repos.next()
# print repo_obj.get_display_name().get_text()
# print repo_obj.get_description().get_text()

# from dlkit_runtime.proxy_example import TestRequest
# dummy_request = TestRequest(username='administrator',
#                             authenticated=True)

# from django.contrib.auth.models import User
# u = User.objects.get(pk=1)
# from django.test import RequestFactory

# rf = RequestFactory()

# req_obj = rf.get('/home')
# req_obj.user = u
# req_obj.user.id
