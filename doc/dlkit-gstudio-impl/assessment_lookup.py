from dlkit_runtime import PROXY_SESSION, RUNTIME
from dlkit_gstudio.gstudio_user_proxy import GStudioRequest
req_obj = GStudioRequest(id=1)
condition = PROXY_SESSION.get_proxy_condition()
condition.set_http_request(req_obj)
proxy = PROXY_SESSION.get_proxy(condition)
assessment_service_mgr = RUNTIME.get_service_manager('ASSESSMENT', proxy=proxy)
all_banks = assessment_service_mgr.get_banks()
all_banks.available()


# ======

# from dlkit_runtime import PROXY_SESSION, RUNTIME
# from dlkit_gstudio.gstudio_user_proxy import GStudioRequest
# condition = PROXY_SESSION.get_proxy_condition()
# proxy = PROXY_SESSION.get_proxy(condition)
# assessment_service_mgr = RUNTIME.get_service_manager('ASSESSMENT', proxy=proxy)
# all_banks = assessment_service_mgr.get_banks()
# all_banks.available()
# from dlkit.primordium.id.primitives import Id
# bank = assessment_service_mgr.get_bank(Id('assessment.Bank%3A57c00fbded849b11f52fc8ec%40ODL.MIT.EDU'))
# bank.get_display_name().text
# # bank = all_banks.next()
# assessment_items = bank.get_assessments()
# assessment_items.available()
# a = assessment_items.next()
# offerings = bank.get_assessments_offered_for_assessment(a.get_id())


# Error:
# /home/docker/code/gstudio/gnowsys-ndf/qbank_lite/dlkit/mongo/assessment/objects.pyc in next(self)
#    1190
#    1191     def next(self):
# -> 1192         return self._get_next_object(Assessment)
#    1193
#    1194     next_assessment = property(fget=get_next_assessment)

# /home/docker/code/gstudio/gnowsys-ndf/qbank_lite/dlkit/mongo/osid/objects.pyc in _get_next_object(self, object_class)
#    2454             raise
#    2455         if isinstance(next_object, dict):
# -> 2456             next_object = object_class(osid_object_map=next_object, runtime=self._runtime, proxy=self._proxy)
#    2457         elif isinstance(next_object, basestring) and object_class == Id:
#    2458             next_object = Id(next_object)

# /home/docker/code/gstudio/gnowsys-ndf/qbank_lite/dlkit/mongo/assessment/objects.pyc in __init__(self, **kwargs)
#     827
#     828     def __init__(self, **kwargs):
# --> 829         osid_objects.OsidObject.__init__(self, object_name='ASSESSMENT', **kwargs)
#     830         self._catalog_name = 'bank'
#     831

# /home/docker/code/gstudio/gnowsys-ndf/qbank_lite/dlkit/mongo/osid/objects.pyc in __init__(self, osid_object_map, runtime, **kwargs)
#     114         osid_markers.Extensible.__init__(self, runtime=runtime, **kwargs)
#     115         self._my_map = osid_object_map
# --> 116         self._load_records(osid_object_map['recordTypeIds'])
#     117
#     118     def get_object_map(self, obj_map=None):

# /home/docker/code/gstudio/gnowsys-ndf/qbank_lite/dlkit/mongo/osid/markers.pyc in _load_records(self, record_type_idstrs)
#     174         """Load all records from given record_type_idstrs."""
#     175         for record_type_idstr in record_type_idstrs:
# --> 176             self._init_record(record_type_idstr)
#     177
#     178     def _init_records(self, record_types):

# /home/docker/code/gstudio/gnowsys-ndf/qbank_lite/dlkit/mongo/osid/markers.pyc in _init_record(self, record_type_idstr)
#     189         import importlib
#     190         record_type_data = self._record_type_data_sets[Id(record_type_idstr).get_identifier()]
# --> 191         module = importlib.import_module(record_type_data['module_path'])
#     192         record = getattr(module, record_type_data['object_record_class_name'], None)
#     193         # only add recognized records ... so apps don't break

# /usr/lib/python2.7/importlib/__init__.pyc in import_module(name, package)
#      35             level += 1
#      36         name = _resolve_name(name[level:], package, level)
# ---> 37     __import__(name)
#      38     return sys.modules[name]

# ImportError: No module named records.osid.object_records


