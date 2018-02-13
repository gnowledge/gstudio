from dlkit_runtime import RUNTIME, PROXY_SESSION
from dlkit_runtime.proxy_example import TestRequest
condition = PROXY_SESSION.get_proxy_condition()


# dummy_request = TestRequest(username='administrator',
#                             authenticated=True)

from django.contrib.auth.models import User
u = User.objects.get(pk=1)
from django.test import RequestFactory

rf = RequestFactory()

req_obj = rf.get('/home')
req_obj.user = u
req_obj.user.id


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
repo_create_form.display_name = 'Repo98'
repo_create_form.description = 'Repo98 description'
repo_obj = repository_service_mgr.create_repository(repo_create_form)
