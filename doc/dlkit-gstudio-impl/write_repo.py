from dlkit_runtime import RUNTIME, PROXY_SESSION
condition = PROXY_SESSION.get_proxy_condition()

# getting req object
from dlkit_gstudio.gstudio_user_proxy import GStudioRequest
req_obj = GStudioRequest(id=1)

condition.set_http_request(req_obj)
proxy = PROXY_SESSION.get_proxy(condition)

#================================================== GROUP as REPOSITORY ==================

repository_service_mgr = RUNTIME.get_service_manager('REPOSITORY', proxy=proxy)


'''
NOTE:
Since each Group represents a Catalog, it is a Service Catalog
 (http://dlkit-doc.readthedocs.io/en/latest/basic.html#service-catalogs)
A Catalog can hold another catalogs.
'''

##### WRITE OPERATIONS

# repo_create_form = repository_service_mgr.get_repository_form_for_create([])

# repo_create_form.set_display_name('TestGrou1')
# repo_create_form.set_description('TestGroup1 description')

# repo_obj = repository_service_mgr.create_repository(repo_create_form)



# ================================================== ASSET ================================

##### WRITE OPERATIONS


rl = repository_service_mgr.get_repository_lookup_session()
all_repos = repository_service_mgr.get_repositories()
print "\nTotal repositories: ", all_repos.available()
test_repo = None
for each in all_repos:
	print "\t- ", each.get_display_name().get_text()
	test_repo = each
print "catalog_name ", test_repo.get_display_name().get_text()
print "catalog_id ",test_repo.get_id()
print "catalog ",test_repo


asset_form = test_repo.get_asset_form_for_create([])
asset_form.description = 'Asset description'
asset_form.display_name = 'Asset name'
asset_obj = test_repo.create_asset(asset_form)

##### READ OPERATIONS
# all_assets = repo_obj.get_assets()
# asset_obj = all_assets.next()
# asset_obj.get_display_name().get_text()
# asset_obj.get_description().get_text()
