"""GStudio implementations of osid sessions."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification


from bson.objectid import ObjectId
from .. import types
from .. import utilities

from dlkit.abstract_osid.osid import sessions as abc_osid_sessions
from ..utilities import get_effective_agent_id_with_proxy

from dlkit.abstract_osid.osid import errors
from dlkit.primordium.id.primitives import Id
from dlkit.primordium.type.primitives import Type
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_GROUP

# =================
# for aliasing ... there is probably a better way
from pymongo import MongoClient
# =================

FEDERATED = 0


class OsidSession(abc_osid_sessions.OsidSession):
    """The ``OsidSession`` is the top level interface for all OSID sessions.

    An ``OsidSession`` is created through its corresponding
    ``OsidManager``. A new ``OsidSession`` should be created for each
    user of a service and for each processing thread. A session
    maintains a single authenticated user and is not required to ensure
    thread-protection. A typical OSID session defines a set of service
    methods corresponding to some compliance level as defined by the
    service and is generally responsible for the management and
    retrieval of ``OsidObjects``.

    ``OsidSession`` defines a set of common methods used throughout all
    OSID sessions. An OSID session may optionally support transactions
    through the transaction interface.

    """

    def __init__(self):
        self._proxy = None
        self._runtime = None

    def _init_proxy_and_runtime(self, proxy, runtime):
        self._proxy = proxy
        self._runtime = runtime
        if runtime is not None:
            try:
                authority_param_id = Id('parameter:authority@mongo')
                self._authority = runtime.get_configuration().get_value_by_parameter(
                    authority_param_id).get_string_value()
            except (KeyError, errors.NotFound):
                self._authority = 'GSTUDIO'

    def _init_object(self, catalog_id, proxy, runtime, db_name, cat_name, cat_class):
        """Initialize this object as an OsidObject."""
        self._catalog_identifier = None
        self._init_proxy_and_runtime(proxy, runtime)
        if catalog_id is not None and catalog_id.get_identifier() != '000000000000000000000000':
            self._catalog_identifier = catalog_id.get_identifier()
            try:
                # self._my_catalog_map = collection.find_one({'_id': ObjectId(self._catalog_identifier)})
                self._my_catalog_map = node_collection.one({'_id': ObjectId(self._catalog_identifier)})
            except errors.NotFound:
                if catalog_id.get_identifier_namespace() != db_name + '.' + cat_name:
                    self._my_catalog_map = self._create_orchestrated_cat(catalog_id, db_name, cat_name)
                else:
                    raise errors.NotFound('could not find catalog identifier ' + catalog_id.get_identifier() + cat_name)
        else:
            # Use GSTUDIO_DEFAULT_GROUP

            self._my_catalog_map = node_collection.one({'_type': 'Group', 'name': GSTUDIO_DEFAULT_GROUP})
            self._catalog_identifier = self._my_catalog_map._id
            '''
            self._catalog_identifier = '000000000000000000000000'
            self._my_catalog_map = {
                '_id': ObjectId(self._catalog_identifier),
                'displayName': {'text': 'Default ' + cat_name,
                                'languageTypeId': str(Type(**types.Language().get_type_data('DEFAULT'))),
                                'scriptTypeId': str(Type(**types.Script().get_type_data('DEFAULT'))),
                                'formatTypeId': str(Type(**types.Format().get_type_data('DEFAULT'))),},
                'description': {'text': 'The Default ' + cat_name,
                                'languageTypeId': str(Type(**types.Language().get_type_data('DEFAULT'))),
                                'scriptTypeId': str(Type(**types.Script().get_type_data('DEFAULT'))),
                                'formatTypeId': str(Type(**types.Format().get_type_data('DEFAULT'))),},
                'genusType': str(Type(**types.Genus().get_type_data('DEFAULT'))),
                'recordTypeIds': [] # Could this somehow inherit source catalog records?
            }
            '''
        # return Repository(gstudio_node=node_collection.one({'_id': ObjectId(repository_id)}))
        self._catalog = cat_class(gstudio_node=self._my_catalog_map, runtime=self._runtime, proxy=self._proxy)
        self._catalog._authority = self._authority  # there should be a better way...
        self._catalog_id = self._catalog.get_id()
        self._forms = dict()


    def get_locale(self):
        """Gets the locale indicating the localization preferences in effect for this session.

        return: (osid.locale.Locale) - the locale
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    locale = property(fget=get_locale)

    def is_authenticated(self):
        """Tests if an agent is authenticated to this session.

        return: (boolean) - ``true`` if valid authentication credentials
                exist, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_authenticated_agent_id(self):
        """Gets the ``Id`` of the agent authenticated to this session.

        This is the agent for which credentials are used either acquired
        natively or via an ``OsidProxyManager``.

        return: (osid.id.Id) - the authenticated agent ``Id``
        raise:  IllegalState - ``is_authenticated()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    authenticated_agent_id = property(fget=get_authenticated_agent_id)

    def get_authenticated_agent(self):
        """Gets the agent authenticated to this session.

        This is the agent for which credentials are used either acquired
        natively or via an ``OsidProxyManager``.

        return: (osid.authentication.Agent) - the authenticated agent
        raise:  IllegalState - ``is_authenticated()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    authenticated_agent = property(fget=get_authenticated_agent)

    def get_effective_agent_id(self):
        """Gets the ``Id`` of the effective agent in use by this session.

        If ``is_authenticated()`` is true, then the effective agent may
        be the same as the agent returned by
        ``getAuthenticatedAgent()``. If ``is_authenticated()`` is
        ``false,`` then the effective agent may be a default agent used
        for authorization by an unknwon or anonymous user.

        return: (osid.id.Id) - the effective agent
        *compliance: mandatory -- This method must be implemented.*

        """
        return get_effective_agent_id_with_proxy(self._proxy)

    effective_agent_id = property(fget=get_effective_agent_id)

    def get_effective_agent(self):
        """Gets the effective agent in use by this session.

        If ``is_authenticated()`` is true, then the effective agent may
        be the same as the agent returned by
        ``getAuthenticatedAgent()``. If ``is_authenticated()`` is
        ``false,`` then the effective agent may be a default agent used
        for authorization by an unknwon or anonymous user.

        return: (osid.authentication.Agent) - the effective agent
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    effective_agent = property(fget=get_effective_agent)

    def get_date(self):
        """Gets the service date which may be the current date or the effective date in which this session exists.

        return: (timestamp) - the service date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    date = property(fget=get_date)

    def get_clock_rate(self):
        """Gets the rate of the service clock.

        return: (decimal) - the clock rate
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    clock_rate = property(fget=get_clock_rate)

    def get_format_type(self):
        """Gets the ``DisplayText`` format ``Type`` preference in effect for this session.

        return: (osid.type.Type) - the effective ``DisplayText`` format
                ``Type``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    format_type = property(fget=get_format_type)

    def supports_transactions(self):
        """Tests for the availability of transactions.

        return: (boolean) - ``true`` if transaction methods are
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def start_transaction(self):
        """Starts a new transaction for this sesson.

        Transactions are a means for an OSID to provide an all-or-
        nothing set of operations within a session and may be used to
        coordinate this service from an external transaction manager. A
        session supports one transaction at a time. Starting a second
        transaction before the previous has been committed or aborted
        results in an ``IllegalState`` error.

        return: (osid.transaction.Transaction) - a new transaction
        raise:  IllegalState - a transaction is already open
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - transactions not supported
        *compliance: optional -- This method must be implemented if
        ``supports_transactions()`` is true.*
        *implementation notes*: Ideally, a provider that supports
        transactions should guarantee atomicity, consistency, isolation
        and durability in a 2 phase commit process. This is not always
        possible in distributed systems and a transaction provider may
        simply allow for a means of processing bulk updates.  To
        maximize interoperability, providers should honor the one-
        transaction-at-a-time rule.

        """
        raise errors.Unimplemented()


    def _use_federated_catalog_view(self):
        self._catalog_view = FEDERATED

    def _init_catalog(self, proxy=None, runtime=None):
        """Initialize this object as an OsidCatalog."""
        self._init_proxy_and_runtime(proxy, runtime)


    def _get_provider_manager(self, osid, local=False):
        """Gets the most appropriate provider manager depending on config."""
        return utilities.get_provider_manager(osid, runtime=self._runtime, proxy=self._proxy, local=local)

# ===========
# for aliasing
    @staticmethod
    def _set_mongo_client(runtime):
        """set the host / port....could be somewhere else"""
        try:
            mongo_host_param_id = Id('parameter:mongoHostURI@mongo')
            mongo_host = runtime.get_configuration().get_value_by_parameter(mongo_host_param_id).get_string_value()
        except (AttributeError, KeyError, errors.NotFound):
            return MongoClient()
        else:
            return MongoClient(mongo_host)

    def _alias_id(self, primary_id, equivalent_id):
        """Adds the given equivalent_id as an alias for primary_id if possible"""
        pkg_name = primary_id.get_identifier_namespace().split('.')[0]
        obj_name = primary_id.get_identifier_namespace().split('.')[1]
        mongo = self._set_mongo_client(self._runtime)
        # We should do a check here -- but would have to be
        # with gstudio node_collection?
        #collection.find_one({'_id': ObjectId(primary_id.get_identifier())}) # to raise NotFound
        node_collection.one({'_id': ObjectId(primary_id.identifier)})
        collection = mongo['id'][pkg_name + 'Ids']
        result = collection.find_one({'aliasIds': {'$in': [str(equivalent_id)]}})
        if result is not None:
            result['aliasIds'].remove(str(equivalent_id))
            collection.save(result)
        id_map = collection.find_one({'_id': str(primary_id)})
        if id_map is None:
            try:
                collection.insert_one({'_id': str(primary_id), 'aliasIds': [str(equivalent_id)]})
            except TypeError:
                collection.insert({'_id': str(primary_id), 'aliasIds': [str(equivalent_id)]})
    
        else:
            id_map['aliasIds'].append(str(equivalent_id))
            collection.save(id_map)

    def _get_id(self, id_, pkg_name):
        """
        Returns the primary id given an alias.

        If the id provided is not in the alias table, it will simply be
        returned as is.

        Only looks within the Id Alias namespace for the session package

        """
        mongo = self._set_mongo_client(self._runtime)
        collection = mongo['id'][pkg_name + 'Ids']
        result = collection.find_one({'aliasIds': {'$in': [str(id_)]}})
        if result is None:
            return id_
        return Id(result['_id'])
