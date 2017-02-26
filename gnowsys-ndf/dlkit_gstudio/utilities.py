"""GStudio utilities.py"""
import time
import datetime
from threading import Thread
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import OperationFailure as PyMongoOperationFailed
from bson import ObjectId
from bson.timestamp import Timestamp

from .osid.osid_errors import NullArgument, NotFound,\
    OperationFailed, Unimplemented, IllegalState, InvalidArgument
from dlkit.primordium.calendaring.primitives import DateTime
from dlkit.primordium.id.primitives import Id
from importlib import import_module

from . import MONGO_CLIENT

class Filler(object):
    pass


def set_mongo_client(runtime):
    try:
        mongo_host_param_id = Id('parameter:mongoHostURI@mongo')
        mongo_host = runtime.get_configuration().get_value_by_parameter(mongo_host_param_id).get_string_value()
    except (AttributeError, KeyError, NotFound):
        MONGO_CLIENT.set_mongo_client(MongoClient())
    else:
        MONGO_CLIENT.set_mongo_client(MongoClient(mongo_host))

class MongoClientValidated(object):
    """automatically validates the insert_one, find_one, and delete_one methods"""
    def __init__(self, db, collection=None, runtime=None):
        if not MONGO_CLIENT.is_mongo_client_set() and runtime is not None:
            set_mongo_client(runtime)
        db_prefix = ''
        try:
            db_prefix_param_id = Id('parameter:mongoDBNamePrefix@mongo')
            db_prefix = runtime.get_configuration().get_value_by_parameter(db_prefix_param_id).get_string_value()
        except (AttributeError, KeyError, NotFound):
            pass

        if collection is None:
            self._mc = MONGO_CLIENT.mongo_client[db_prefix + db]
        else:
            self._mc = MONGO_CLIENT.mongo_client[db_prefix + db][collection]
            # add the collection index, if available in the configs
            try:
                mongo_indexes_param_id = Id('parameter:indexes@mongo')
                mongo_indexes = runtime.get_configuration().get_value_by_parameter(mongo_indexes_param_id).get_object_value()
                namespace = '{0}.{1}'.format(db, collection)
                if namespace in mongo_indexes:
                    for field in mongo_indexes[namespace]:
                        self._mc.create_index(field)
            except (AttributeError, KeyError, NotFound):
                pass

    def _validate_write(self, result):
        try:
            if not result.acknowledged or result.inserted_id is None:
            # if (('writeErrors' in result and len(result['writeErrors']) > 0) or
            #         ('writeConcernErrors' in result and len(result['writeConcernErrors']) > 0)):
                raise OperationFailed(str(result))
        except AttributeError:
            # account for deprecated save() method
            if result is None:
                raise OperationFailed('Nothing saved to database.')

    def count(self):
        return self._mc.count()

    def delete_one(self, query):
        try:
            result = self._mc.delete_one(query)
        except TypeError:
            result = self._mc.remove(query)
            if result is not None:
                returned_object = result
                result = Filler()
                result.deleted_count = returned_object['n']
        if result is None or result.deleted_count == 0:
            raise NotFound(str(query) + ' returned None.')
        return result

    def find(self, query=None):
        if query is None:
            return self._mc.find()
        else:
            return self._mc.find(query)

    def find_one(self, query):
        result = self._mc.find_one(query)
        if result is None:
            raise NotFound(str(query) + ' returned None.')
        return result

    def insert_one(self, doc):
        try:
            result = self._mc.insert_one(doc)
        except TypeError:
            # pymongo 2.8.1
            result = self._mc.insert(doc)
            if result is not None:
                returned_object_id = result
                result = Filler()
                result.inserted_id = returned_object_id
        self._validate_write(result)
        return result

    def raw(self):
        """ return the raw mongo client object...used for GridFS
        """
        return self._mc

    def save(self, doc):
        result = self._mc.save(doc)
        self._validate_write(result)
        return result

def remove_null_proxy_kwarg(func):
    """decorator, to remove a 'proxy' keyword argument. For wrapping certain Manager methods"""
    def wrapper(*args, **kwargs):
        if 'proxy' in kwargs:
            #if kwargs['proxy'] is None:
            del kwargs['proxy']
            #else:
            #    raise InvalidArgument('Manager sessions cannot be called with Proxies. Use ProxyManager instead')
        return func(*args, **kwargs)
    return wrapper

def arguments_not_none(func):
    """decorator, to check if any arguments are None; raise exception if so"""
    def wrapper(*args, **kwargs):
        for arg in args:
            if arg is None:
                raise NullArgument()
        for arg, val in kwargs.iteritems():
            if val is None:
                raise NullArgument()
        try:
            return func(*args, **kwargs)
        except TypeError as ex:
            if 'takes exactly' in ex.args[0]:
                raise NullArgument('Wrong number of arguments provided: ' + str(ex.args[0]))
            else:
                raise
    return wrapper

def get_provider_manager(osid, runtime=None, proxy=None, local=False):
    """
    Gets the most appropriate provider manager depending on config.

    If local is True, then don't bother with the runtime/config and
    try to get the requested service manager directly from the local
    service implementations known to this mongodb implementation.

    """
    if runtime is not None:
        if local:
            parameter_id = Id('parameter:localImpl@gstudio')
        else:
            parameter_id = Id('parameter:' + osid.lower() + 'ProviderImpl@gstudio')
        try:
            # Try to get the manager from the runtime, if available:
            config = runtime.get_configuration()
            impl_name = config.get_value_by_parameter(parameter_id).get_string_value()
            if proxy is None:
                return runtime.get_manager(osid, impl_name)
            else:
                return runtime.get_proxy_manager(osid, impl_name)
        except (AttributeError, KeyError, NotFound):
            pass
    # Try to return a Manager directly from this implementation, or raise OperationFailed:
    try:
        if proxy is None:
            mgr_str = 'Manager'
        else:
            mgr_str = 'ProxyManager'
        module = import_module('dlkit.mongo.' + osid.lower() + '.managers')
        manager_name = ''.join((osid.title()).split('_')) + mgr_str
        manager = getattr(module, manager_name)()
    except (ImportError, AttributeError):
        raise OperationFailed()
    if runtime is not None:
        manager.initialize(runtime)
    return manager

def get_provider_session(provider_manager, session_method, proxy=None, *args, **kwargs):
    if proxy is None:
        return getattr(provider_manager, session_method)(*args, **kwargs)
    else:
        return getattr(provider_manager, session_method)(proxy, *args, **kwargs)

def format_catalog(catalog_name):
    return catalog_name.replace('_', '').title()

def now_map():
    now = DateTime.utcnow()
    return {
        'year': now.year,
        'month': now.month,
        'day': now.day,
        'hour': now.hour,
        'minute': now.minute,
        'second': now.second,
        'microsecond': now.microsecond,
    }

def overlap(start1, end1, start2, end2):
    """
    Does the range (start1, end1) overlap with (start2, end2)?

    From Ned Batchelder
    http://nedbatchelder.com/blog/201310/range_overlap_in_two_compares.html

    """
    return not (end1 < start2 or end2 < start1)


class OsidListList(list):
    """
    A morker class for initializing OsidLists with a list of other OsidLists

    To use, load up this list with OsidLists of the same object type, and pass
    it as the argument to an OsidList of that same object type. The OsidList
    should exhaust all the contained OsidLists in order on iteration to return
    all the underlying objects as if they are part of one list.

    """
    pass


def get_registry(entry, runtime):
    """Returns a record registry given an entry and runtime"""
    try:
        records_location_param_id = Id('parameter:recordsRegistry@mongo')
        registry = runtime.get_configuration().get_value_by_parameter(
            records_location_param_id).get_string_value()
        return import_module(registry).__dict__.get(entry, {})
    except (ImportError, AttributeError, KeyError, NotFound):
        return {}

def is_authenticated_with_proxy(proxy):
    """Given a Proxy, checks whether a user is authenticated"""
    if proxy is None:
        return False
    elif proxy.has_authentication():
        return proxy.get_authentication().is_valid()
    else:
        return False

def get_authenticated_agent_id_with_proxy(proxy):
    """Given a Proxy, returns the Id of the authenticated Agent"""
    if is_authenticated_with_proxy(proxy):
        return proxy.get_authentication().get_agent_id()
    else:
        raise IllegalState()

def get_authenticated_agent_with_proxy(proxy):
    """Given a Proxy, returns the authenticated Agent"""
    if is_authenticated_with_proxy(proxy):
        return proxy.get_authentication().get_agent()
    else:
        raise IllegalState()

def get_effective_agent_id_with_proxy(proxy):
    """Given a Proxy, returns the Id of the effective Agent"""
    if is_authenticated_with_proxy(proxy):
        if proxy.has_effective_agent():
            return proxy.get_effective_agent_id()
        else:
            return proxy.get_authentication().get_agent_id()
    else:
        return Id(
            identifier='MC3GUE$T@MIT.EDU',
            namespace='authentication.Agent',
            authority='MIT-ODL')

def get_effective_agent_with_proxy(proxy):
    """Given a Proxy, returns the effective Agent"""
    #effective_agent_id = self.get_effective_agent_id()
    # This may want to be extended to get the Agent directly from the Authentication
    # if available and if not effective agent is available in the proxy
    #return Agent(
    #    identifier=effective_agent_id.get_identifier(),
    #    namespace=effective_agent_id.get_namespace(),
    #    authority=effective_agent_id.get_authority())
    raise Unimplemented()

def get_locale_with_proxy(proxy):
    """Given a Proxy, returns the Locale

    This assumes that instantiating a dlkit.gst.locale.objects.Locale
    without constructor arguments wlll return the default Locale.

    """
    from dlkit.mongo.locale.objects import Locale
    if proxy is not None:
            locale = proxy.get_locale()
            if locale is not None:
                return locale
    return Locale()

def update_display_text_defaults(mdata, locale_map):
    for default_display_text in mdata['default_string_values']:
        default_display_text.update(locale_map)


def split_osid_id(osid_id):
    # e.g: osid.agent.Agent%3Aadministrator%40MIT-ODL
    #      <namespace> <identifier> <authority>
    osid_id_dict = {
        'namespace': '',
        'identifier': '',
        'authority': ''
    }
    osid_id = str(osid_id)
    try:
        temp_list = osid_id.split('%3A')
        osid_id_dict['namespace'] = temp_list.pop(0)
        temp_list = temp_list.pop().split('%40')
        osid_id_dict['identifier'] = temp_list[0]
        osid_id_dict['authority'] = temp_list[1]
    except Exception, e:
        pass

    return osid_id_dict


def get_display_text_map(display_text=None):
    """Returns display text elements for map"""
    if display_text:
        try:
            display_text = display_text.get_text()
        except Exception as e:
            display_text = str(display_text)
        return {'formatTypeId': 'TextFormats%3APLAIN%40okapia.net',
        'languageTypeId': '639-2%3AENG%40ISO',
        'scriptTypeId': u'15924%3ALATN%40ISO',
        'text': display_text}
    else:
        # defualt blank_display_text
        return {'formatTypeId': 'TextFormats%3APLAIN%40okapia.net',
        'languageTypeId': '639-2%3AENG%40ISO',
        'scriptTypeId': u'15924%3ALATN%40ISO',
        'text': ''}

