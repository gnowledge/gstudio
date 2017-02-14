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
# is equivalent to:
all_repos = repository_service_mgr.get_repositories()
# The latter is supported by the "services" implementation as a developer convenience
# The service manager keeps track of the sessions on behalf of the consumer
# In each case the "lookup_session" is invoked without a repository, which is the convention
# for such sessions.  So the authz_adapter will report the ROOT repository.
# The GStudio Authorization implentation must deal with this.


# print "\nTotal repositories: ", all_repos.len()
# the above code should use available() instead. .len() mostly works but will not always guarantee 
# a correct answer for complex or very large iterators. Instead use:
print "\nTotal repositories: ", all_repos.available()
test_repo = None
for each in all_repos:
	print "\t- ", each.get_display_name()
	test_repo = each
# So now test_repo holds the last repository found in the all_repos iterator.

# Calling repository_service_mgr.get_asset_lookup_session() will default to the ROOT repo Id. 
# This must be supported by your implementation.  same for get_asset_admin_session(), etc.  The
# question to ask yoruself is what does it mean in GStudio. I would bet that GStudio doesn't allow
# Assets to exist at the system/root level. In other words, Assets must always exist in 
# Repositories/Groups. So perhaps your Authorization implementation might always return False
# for is_authorized() calls where the qualifier_id.identifier == "ROOT"
al = repository_service_mgr.get_asset_lookup_session()
al.get_assets() # might raise PermissionDenied because is_authorized() returned False
# However, if the session is set to use_federated_repository_view(), then the underlying
# implementation would be expected to return all Assets from Repositories/Groups where
# the logged-in user is authorized to lookup Assets. We need to talk about this.

# As with the Repository example above, the following two calls are equivalent:
al_repo = repository_service_mgr.get_asset_lookup_session_for_repository(test_repo.get_repository_id())
assets = al_repo.get_assets() # Returns all the Assets
# is equivalent to:
test_repo.get_assets() # Returns all the Assets
# Again, the latter is supported by the "services" implementation as a developer convenience
# In this case the Repository itself keeps track of the sessions for you.
# Since both of these calls are using Repository-bound sessions the authz_adapter will send 
# along a Qualifier Id where qualifier_id.identifier == a gstudio group ObjectId string

