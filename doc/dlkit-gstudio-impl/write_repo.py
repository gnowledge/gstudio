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

repo_create_form = repository_service_mgr.get_repository_form_for_create([])

repo_create_form.set_display_name('TestGrou1')
repo_create_form.set_description('TestGroup1 description')

repo_obj = repository_service_mgr.create_repository(repo_create_form)


