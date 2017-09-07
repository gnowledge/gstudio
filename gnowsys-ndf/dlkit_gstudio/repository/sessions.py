"""GStudio implementations of repository sessions."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification

from bson import ObjectId
from .. import utilities
from . import objects
from dlkit.abstract_osid.repository import sessions as abc_repository_sessions
from ..osid import sessions as osid_sessions
from ..osid.sessions import OsidSession
from dlkit.abstract_osid.osid import errors
from dlkit.primordium.id.primitives import Id
from .objects import Repository, RepositoryList
from gnowsys_ndf.ndf.models import Group, GSystem, GSystemType, node_collection, Node, triple_collection
from gnowsys_ndf.ndf.views.group import CreateGroup
from dlkit.abstract_osid.id.primitives import Id as ABCId
from dlkit.abstract_osid.type.primitives import Type as ABCType

CREATED = True
UPDATED = True


class AssetLookupSession(abc_repository_sessions.AssetLookupSession, osid_sessions.OsidSession):
    """This session defines methods for retrieving assets.

    An ``Asset`` represents an element of content stored in a
    Repository.

    This lookup session defines several views:

      * comparative view: elements may be silently omitted or re-ordered
      * plenary view: provides a complete result set or is an error
        condition
      * isolated repository view: All asset methods in this session
        operate, retrieve and pertain to assets defined explicitly in
        the current repository. Using an isolated view is useful for
        managing ``Assets`` with the ``AssetAdminSession.``
      * federated repository view: All asset methods in this session
        operate, retrieve and pertain to all assets defined in this
        repository and any other assets implicitly available in this
        repository through repository inheritence.


    The methods ``use_federated_repository_view()`` and
    ``use_isolated_repository_view()`` behave as a radio group and one
    should be selected before invoking any lookup methods.

    Assets may have an additional records indicated by their respective
    record types. The record may not be accessed through a cast of the
    ``Asset``.

    """
    def __init__(self, catalog_id=None, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        self._catalog_class = objects.Repository
        self._session_name = 'AssetLookupSession'
        self._catalog_name = 'Repository'
        OsidSession._init_object(
            self,
            catalog_id,
            proxy,
            runtime,
            db_name='repository',
            cat_name='Repository',
            cat_class=objects.Repository)
        self._kwargs = kwargs

    # def __init__(self, proxy=None, runtime=None, **kwargs):
    #     OsidSession.__init__(self)
    #     OsidSession._init_proxy_and_runtime(self, proxy=proxy, runtime=runtime)
    #     self._kwargs = kwargs

    def get_repository_id(self):
        """Gets the ``Repository``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Repository Id`` associated with
                this session
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._catalog_id

    repository_id = property(fget=get_repository_id)

    def get_repository(self):
        """Gets the ``Repository`` associated with this session.

        return: (osid.repository.Repository) - the ``Repository``
                associated with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._catalog
        # pass

    repository = property(fget=get_repository)

    def can_lookup_assets(self):
        """Tests if this user can perform ``Asset`` lookups.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer lookup
        operations.

        return: (boolean) - ``false`` if lookup methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_comparative_asset_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        pass

    def use_plenary_asset_view(self):
        """A complete view of the ``Asset`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        pass

    def use_federated_repository_view(self):
        """Federates the view for methods in this session.

        A federated view will include assets in repositories which are
        children of this repository in the repository hierarchy.

        *compliance: mandatory -- This method is must be implemented.*

        """
        pass

    def use_isolated_repository_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts lookups to this repository only.

        *compliance: mandatory -- This method is must be implemented.*

        """
        pass

    @utilities.arguments_not_none
    def get_asset(self, asset_id):
        """Gets the ``Asset`` specified by its ``Id``.

        In plenary mode, the exact ``Id`` is found or a ``NotFound``
        results. Otherwise, the returned ``Asset`` may have a different
        ``Id`` than requested, such as the case where a duplicate ``Id``
        was assigned to an ``Asset`` and retained for compatibility.

        arg:    asset_id (osid.id.Id): the ``Id`` of the ``Asset`` to
                retrieve
        return: (osid.repository.Asset) - the returned ``Asset``
        raise:  NotFound - no ``Asset`` found with the given ``Id``
        raise:  NullArgument - ``asset_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        if asset_id:
            result = Node.get_node_by_id(ObjectId(asset_id.identifier))

            has_assetcontent_rt = node_collection.one({'_type': 'RelationType', 'name': 'has_assetcontent'})
            asset_grels = triple_collection.find({'_type': 'GRelation', 
                 'subject': result._id, 'relation_type': has_assetcontent_rt._id,
            }, {'right_subject': 1})
            asset_content_list = []
            if asset_grels.count():
                asset_content_ids = [each_rs['right_subject'] for each_rs in asset_grels]
                result_cur = Node.get_nodes_by_ids_list(asset_content_ids)
        
                asset_content_objs = [objects.AssetContent(gstudio_node=each_assetcontent) for each_assetcontent in result_cur]
                for asset_content in asset_content_objs:
                    asset_content_list.append(asset_content.get_object_map())



            # asset_content_list = []
            # asset_contents = self.get_asset_contents()
            # for asset_content in asset_contents:
            #     asset_content_list.append(asset_content.get_object_map())
            # # self._gstudio_map['assetContents'] = asset_content_list

            return objects.Asset(gstudio_node=result, runtime=self._runtime, proxy=self._proxy, assetContents=asset_content_list)


    @utilities.arguments_not_none
    def get_assets_by_ids(self, asset_ids):
        """Gets an ``AssetList`` corresponding to the given ``IdList``.

        In plenary mode, the returned list contains all of the assets
        specified in the ``Id`` list, in the order of the list,
        including duplicates, or an error results if an ``Id`` in the
        supplied list is not found or inaccessible. Otherwise,
        inaccessible ``Assets`` may be omitted from the list and may
        present the elements in any order including returning a unique
        set.

        arg:    asset_ids (osid.id.IdList): the list of ``Ids`` to
                retrieve
        return: (osid.repository.AssetList) - the returned ``Asset
                list``
        raise:  NotFound - an ``Id`` was not found
        raise:  NullArgument - ``asset_ids`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        object_id_list = []
        for i in asset_ids:
            object_id_list.append(ObjectId(self._get_id(i, 'repository').get_identifier()))
        result_cur = Node.get_nodes_by_ids_list(object_id_list)
        sorted_result = list(result_cur)
        return objects.AssetList(sorted_result, runtime=self._runtime, proxy=self._proxy)

    @utilities.arguments_not_none
    def get_assets_by_genus_type(self, asset_genus_type):
        """Gets an ``AssetList`` corresponding to the given asset genus ``Type`` which does not include assets of types derived from the specified ``Type``.

        In plenary mode, the returned list contains all known assets or
        an error results. Otherwise, the returned list may contain only
        those assets that are accessible through this session.

        arg:    asset_genus_type (osid.type.Type): an asset genus type
        return: (osid.repository.AssetList) - the returned ``Asset
                list``
        raise:  NullArgument - ``asset_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        pass

    @utilities.arguments_not_none
    def get_assets_by_parent_genus_type(self, asset_genus_type):
        """Gets an ``AssetList`` corresponding to the given asset genus ``Type`` and include any additional assets with genus types derived from the specified ``Type``.

        In plenary mode, the returned list contains all known assets or
        an error results. Otherwise, the returned list may contain only
        those assets that are accessible through this session.

        arg:    asset_genus_type (osid.type.Type): an asset genus type
        return: (osid.repository.AssetList) - the returned ``Asset
                list``
        raise:  NullArgument - ``asset_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        pass

    @utilities.arguments_not_none
    def get_assets_by_record_type(self, asset_record_type):
        """Gets an ``AssetList`` containing the given asset record ``Type``.

        In plenary mode, the returned list contains all known assets or
        an error results. Otherwise, the returned list may contain only
        those assets that are accessible through this session.

        arg:    asset_record_type (osid.type.Type): an asset record type
        return: (osid.repository.AssetList) - the returned ``Asset
                list``
        raise:  NullArgument - ``asset_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        pass

    @utilities.arguments_not_none
    def get_assets_by_provider(self, resource_id):
        """Gets an ``AssetList`` from the given provider.

        In plenary mode, the returned list contains all known assets or
        an error results. Otherwise, the returned list may contain only
        those assets that are accessible through this session.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        return: (osid.repository.AssetList) - the returned ``Asset
                list``
        raise:  NullArgument - ``resource_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        pass

    def get_assets(self):
        """Gets all ``Assets``.

        In plenary mode, the returned list contains all known assets or
        an error results. Otherwise, the returned list may contain only
        those assets that are accessible through this session.

        return: (osid.repository.AssetList) - a list of ``Assets``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Get all Asset objects from all Groups.
        # To be implemented
        asset_list = []
        group_id = self._catalog_id.identifier
        asset_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Asset'})
        asset_cur = node_collection.find({'member_of': asset_gst._id, 'group_set': ObjectId(group_id)})
        asset_list = [objects.Asset(gstudio_node=each_asset) for each_asset in asset_cur]
        return objects.AssetList(asset_list, runtime=self._runtime, proxy=self._proxy)

    assets = property(fget=get_assets)

class AssetContentLookupSession(abc_repository_sessions.AssetContentLookupSession, osid_sessions.OsidSession):
    """This session defines methods for retrieving asset contents.

    An ``AssetContent`` represents an element of content stored associated
    with an ``Asset``.

    This lookup session defines several views:

      * comparative view: elements may be silently omitted or re-ordered
      * plenary view: provides a complete result set or is an error
        condition
      * isolated repository view: All asset content methods in this session
        operate, retrieve and pertain to asset contents defined explicitly in
        the current repository. Using an isolated view is useful for
        managing ``AssetContents`` with the ``AssetAdminSession.``
      * federated repository view: All asset content methods in this session
        operate, retrieve and pertain to all asset contents defined in this
        repository and any other asset contents implicitly available in this
        repository through repository inheritence.


    The methods ``use_federated_repository_view()`` and
    ``use_isolated_repository_view()`` behave as a radio group and one
    should be selected before invoking any lookup methods.

    AssetContents may have an additional records indicated by their respective
    record types. The record may not be accessed through a cast of the
    ``AssetContent``.

    """

    def __init__(self, catalog_id=None, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        self._catalog_class = objects.Repository
        self._session_name = 'AssetContentLookupSession'
        self._catalog_name = 'Repository'
        OsidSession._init_object(
            self,
            catalog_id,
            proxy,
            runtime,
            db_name='repository',
            cat_name='Repository',
            cat_class=objects.Repository)
        self._kwargs = kwargs

    def get_repository_id(self):
        """Gets the ``Repository``  ``Id`` associated with this session.

        :return: the ``Repository Id`` associated with this session
        :rtype: ``osid.id.Id``


        *compliance: mandatory -- This method must be implemented.*

        """
        return self._catalog_id

    repository_id = property(fget=get_repository_id)

    def get_repository(self):
        """Gets the ``Repository`` associated with this session.

        :return: the ``Repository`` associated with this session
        :rtype: ``osid.repository.Repository``
        :raise: ``OperationFailed`` -- unable to complete request
        :raise: ``PermissionDenied`` -- authorization failure

        *compliance: mandatory -- This method must be implemented.*

        """
        return self._catalog

    repository = property(fget=get_repository)

    def can_lookup_asset_contents(self):
        """Tests if this user can perform ``Asset`` lookups.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer lookup
        operations.

        :return: ``false`` if lookup methods are not authorized, ``true`` otherwise
        :rtype: ``boolean``


        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_comparative_asset_content_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.



        *compliance: mandatory -- This method is must be implemented.*

        """
        pass

    def use_plenary_asset_content_view(self):
        """A complete view of the ``Asset`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.



        *compliance: mandatory -- This method is must be implemented.*

        """
        pass

    def use_federated_repository_view(self):
        """Federates the view for methods in this session.

        A federated view will include assets in repositories which are
        children of this repository in the repository hierarchy.



        *compliance: mandatory -- This method is must be implemented.*

        """
        pass

    def use_isolated_repository_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts lookups to this repository only.



        *compliance: mandatory -- This method is must be implemented.*

        """
        pass

    @utilities.arguments_not_none
    def get_asset_content(self, asset_content_id):
        """Gets the ``AssetContent`` specified by its ``Id``.

        In plenary mode, the exact ``Id`` is found or a ``NotFound``
        results. Otherwise, the returned ``AssetContent`` may have a different
        ``Id`` than requested, such as the case where a duplicate ``Id``
        was assigned to an ``AssetContent`` and retained for compatibility.

        :param asset_content_id: the ``Id`` of the ``AssetContent`` to retrieve
        :type asset_content_id: ``osid.id.Id``
        :return: the returned ``AssetContent``
        :rtype: ``osid.repository.Asset``
        :raise: ``NotFound`` -- no ``AssetContent`` found with the given ``Id``
        :raise: ``NullArgument`` -- ``asset_content_id`` is ``null``
        :raise: ``OperationFailed`` -- unable to complete request
        :raise: ``PermissionDenied`` -- authorization failure

        *compliance: mandatory -- This method must be implemented.*

        """
        asset_content_identifier = ObjectId(self._get_id(asset_content_id, 'repository').get_identifier())
        result = Node.get_node_by_id(asset_content_identifier)
        return objects.AssetContent(gstudio_node=result, runtime=self._runtime, proxy=self._proxy)

    @utilities.arguments_not_none
    def get_asset_contents_by_ids(self, asset_content_ids):
        """Gets an ``AssetList`` corresponding to the given ``IdList``.

        In plenary mode, the returned list contains all of the asset contents
        specified in the ``Id`` list, in the order of the list,
        including duplicates, or an error results if an ``Id`` in the
        supplied list is not found or inaccessible. Otherwise,
        inaccessible ``AssetContnts`` may be omitted from the list and may
        present the elements in any order including returning a unique
        set.

        :param asset_content_ids: the list of ``Ids`` to retrieve
        :type asset_content_ids: ``osid.id.IdList``
        :return: the returned ``AssetContent list``
        :rtype: ``osid.repository.AssetContentList``
        :raise: ``NotFound`` -- an ``Id`` was not found
        :raise: ``NullArgument`` -- ``asset_ids`` is ``null``
        :raise: ``OperationFailed`` -- unable to complete request
        :raise: ``PermissionDenied`` -- authorization failure

        *compliance: mandatory -- This method must be implemented.*

        """
        object_id_list = []
        for i in asset_content_ids:
            object_id_list.append(ObjectId(self._get_id(i, 'repository').get_identifier()))
        result_cur = Node.get_nodes_by_ids_list(object_id_list)
        # sorted_result = list(result_cur)
        asset_content_objs = [AssetContent(gstudio_node=each_assetcontent) for each_assetcontent in result_cur]
        return AssetContentList(asset_content_objs)

    @utilities.arguments_not_none
    def get_asset_contents_by_genus_type(self, asset_content_genus_type):
        """Gets an ``AssetContentList`` corresponding to the given asset content genus ``Type`` which does not include asset contents of types derived from the specified ``Type``.

        In plenary mode, the returned list contains all known asset contents or
        an error results. Otherwise, the returned list may contain only
        those asset contents that are accessible through this session.

        :param asset_content_genus_type: an asset content genus type
        :type asset_content_genus_type: ``osid.type.Type``
        :return: the returned ``AssetContent list``
        :rtype: ``osid.repository.AssetContentList``
        :raise: ``NullArgument`` -- ``asset_content_genus_type`` is ``null``
        :raise: ``OperationFailed`` -- unable to complete request
        :raise: ``PermissionDenied`` -- authorization failure

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_asset_contents_by_parent_genus_type(self, asset_content_genus_type):
        """Gets an ``AssetContentList`` corresponding to the given asset content genus ``Type`` and include any additional asset contents with genus types derived from the specified ``Type``.

        In plenary mode, the returned list contains all known asset contents or
        an error results. Otherwise, the returned list may contain only
        those asset contents that are accessible through this session.

        :param asset_content_genus_type: an asset content genus type
        :type asset_content_genus_type: ``osid.type.Type``
        :return: the returned ``AssetContent list``
        :rtype: ``osid.repository.AssetContentList``
        :raise: ``NullArgument`` -- ``asset_content_genus_type`` is ``null``
        :raise: ``OperationFailed`` -- unable to complete request
        :raise: ``PermissionDenied`` -- authorization failure

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_asset_contents_by_record_type(self, asset_content_record_type):
        """Gets an ``AssetContentList`` containing the given asset record ``Type``.

        In plenary mode, the returned list contains all known asset contents or
        an error results. Otherwise, the returned list may contain only
        those asset contents that are accessible through this session.

        :param asset_content_record_type: an asset content record type
        :type asset_content_record_type: ``osid.type.Type``
        :return: the returned ``AssetContent list``
        :rtype: ``osid.repository.AssetContentList``
        :raise: ``NullArgument`` -- ``asset_content_record_type`` is ``null``
        :raise: ``OperationFailed`` -- unable to complete request
        :raise: ``PermissionDenied`` -- authorization failure

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_asset_contents_for_asset(self, asset_id):
        """Gets an ``AssetList`` from the given Asset.

        In plenary mode, the returned list contains all known asset contents or
        an error results. Otherwise, the returned list may contain only
        those asset contents that are accessible through this session.

        :param asset_id: an asset ``Id``
        :type asset_id: ``osid.id.Id``
        :return: the returned ``AssetContent list``
        :rtype: ``osid.repository.AssetContentList``
        :raise: ``NullArgument`` -- ``asset_id`` is ``null``
        :raise: ``OperationFailed`` -- unable to complete request
        :raise: ``PermissionDenied`` -- authorization failure

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_asset_contents_by_genus_type_for_asset(self, asset_content_genus_type, asset_id):
        """Gets an ``AssetContentList`` from the given GenusType and Asset Id.

        In plenary mode, the returned list contains all known asset contents or
        an error results. Otherwise, the returned list may contain only
        those asset contents that are accessible through this session.

        :param asset_content_genus_type: an an asset content genus type
        :type asset_id: ``osid.type.Type``
        :param asset_id: an asset ``Id``
        :type asset_id: ``osid.id.Id``
        :return: the returned ``AssetContent list``
        :rtype: ``osid.repository.AssetContentList``
        :raise: ``NullArgument`` -- ``asset_content_genus_type`` or ``asset_id`` is ``null``
        :raise: ``OperationFailed`` -- unable to complete request
        :raise: ``PermissionDenied`` -- authorization failure

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssetQuerySession(abc_repository_sessions.AssetQuerySession, osid_sessions.OsidSession):
    """This session provides methods for searching among ``Asset`` objects.

    The search query is constructed using the ``AssetQuery``.

    This session defines views that offer differing behaviors for
    searching.

      * federated repository view: searches include assets in
        repositories of which this repository is a ancestor in the
        repository hierarchy
      * isolated repository view: searches are restricted to assets in
        this repository


    Assets may have a query record indicated by their respective record
    types. The query record is accessed via the ``AssetQuery``.

    """

    def __init__(self, catalog_id=None, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        self._catalog_class = objects.Repository
        self._session_name = 'AssetQuerySession'
        self._catalog_name = 'Repository'
        OsidSession._init_object(
            self,
            catalog_id,
            proxy,
            runtime,
            db_name='repository',
            cat_name='Repository',
            cat_class=objects.Repository)
        self._kwargs = kwargs

    def get_repository_id(self):
        """Gets the ``Repository``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Repository Id`` associated with
                this session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository_id = property(fget=get_repository_id)

    def get_repository(self):
        """Gets the ``Repository`` associated with this session.

        return: (osid.repository.Repository) - the ``Repository``
                associated with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository = property(fget=get_repository)

    def can_search_assets(self):
        """Tests if this user can perform ``Asset`` searches.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer search
        operations to unauthorized users.

        return: (boolean) - ``false`` if search methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_federated_repository_view(self):
        """Federates the view for methods in this session.

        A federated view will include assets in repositories which are
        children of this repository in the repository hierarchy.

        *compliance: mandatory -- This method is must be implemented.*

        """
        self._use_federated_catalog_view()

    def use_isolated_repository_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts lookups to this repository only.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def get_asset_query(self):
        """Gets an asset query.

        return: (osid.repository.AssetQuery) - the asset query
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    asset_query = property(fget=get_asset_query)

    @utilities.arguments_not_none
    def get_assets_by_query(self, asset_query):
        """Gets a list of ``Assets`` matching the given asset query.

        arg:    asset_query (osid.repository.AssetQuery): the asset
                query
        return: (osid.repository.AssetList) - the returned ``AssetList``
        raise:  NullArgument - ``asset_query`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - the ``asset_query`` is not of this service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssetSearchSession(abc_repository_sessions.AssetSearchSession, AssetQuerySession):
    """This session provides methods for searching among ``Asset`` objects.

    The search query is constructed using the ``AssetQuery``.

    ``get_assets_by_query()`` is the basic search method and returns a
    list of ``Assets``. A more advanced search may be performed with
    ``getAssetsBySearch()``. It accepts an ``AssetSearch`` in addition
    to the query for the purpose of specifying additional options
    affecting the entire search, such as ordering.
    ``get_assets_by_search()`` returns an ``AssetSearchResults`` that
    can be used to access the resulting ``AssetList`` or be used to
    perform a search within the result set through ``AssetList``.

    This session defines views that offer differing behaviors for
    searching.

      * federated repository view: searches include assets in
        repositories of which this repository is a ancestor in the
        repository hierarchy
      * isolated repository view: searches are restricted to assets in
        this repository


    Assets may have a query record indicated by their respective record
    types. The query record is accessed via the ``AssetQuery``.

    """

    def get_asset_search(self):
        """Gets an asset search.

        return: (osid.repository.AssetSearch) - the asset search
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    asset_search = property(fget=get_asset_search)

    def get_asset_search_order(self):
        """Gets an asset search order.

        The ``AssetSearchOrder`` is supplied to an ``AssetSearch`` to
        specify the ordering of results.

        return: (osid.repository.AssetSearchOrder) - the asset search
                order
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    asset_search_order = property(fget=get_asset_search_order)

    @utilities.arguments_not_none
    def get_assets_by_search(self, asset_query, asset_search):
        """Gets the search results matching the given search query using the given search.

        arg:    asset_query (osid.repository.AssetQuery): the asset
                query
        arg:    asset_search (osid.repository.AssetSearch): the asset
                search
        return: (osid.repository.AssetSearchResults) - the asset search
                results
        raise:  NullArgument - ``asset_query`` or ``asset_search`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``asset_query`` or ``asset_search`` is not
                of this service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_asset_query_from_inspector(self, asset_query_inspector):
        """Gets an asset query from an inspector.

        The inspector is available from a ``AssetSearchResults``.

        arg:    asset_query_inspector
                (osid.repository.AssetQueryInspector): an asset query
                inspector
        return: (osid.repository.AssetQuery) - the asset query
        raise:  NullArgument - ``asset_query_inspector`` is ``null``
        raise:  Unsupported - ``asset_query_inspector`` is not of this
                service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssetAdminSession(abc_repository_sessions.AssetAdminSession, osid_sessions.OsidSession):
    """This session creates, updates, and deletes ``Assets``.

    The data for create and update is provided by the consumer via the
    form object. ``OsidForms`` are requested for each create or update
    and may not be reused.

    Create and update operations differ in their usage. To create an
    ``Asset,`` an ``AssetForm`` is requested using
    ``get_asset_form_for_create()`` specifying the desired record
    ``Types`` or none if no record ``Types`` are needed. The returned
    ``AssetyForm`` will indicate that it is to be used with a create
    operation and can be used to examine metdata or validate data prior
    to creation. Once the ``AssetForm`` is submiited to a create
    operation, it cannot be reused with another create operation unless
    the first operation was unsuccessful. Each ``AssetForm`` corresponds
    to an attempted transaction.

    For updates, ``AssetForms`` are requested to the ``Asset``  ``Id``
    that is to be updated using ``getAssetFormForUpdate()``. Similarly,
    the ``AssetForm`` has metadata about the data that can be updated
    and it can perform validation before submitting the update. The
    ``AssetForm`` can only be used once for a successful update and
    cannot be reused.

    The delete operations delete ``Assets``. To unmap an ``Asset`` from
    the current ``Repository,`` the ``AssetRepositoryAssignmentSession``
    should be used. These delete operations attempt to remove the
    ``Bid`` itself thus removing it from all known ``Repository``
    catalogs.

    This session includes an ``Id`` aliasing mechanism to assign an
    external ``Id`` to an internally assigned Id.

    The view of the administrative methods defined in this session is
    determined by the provider. For an instance of this session where no
    repository has been specified, it may not be parallel to the
    ``AssetLookupSession``. For example, a default
    ``AssetLookupSession`` may view the entire repository hierarchy
    while the default ``AssetAdminSession`` uses an isolated
    ``Repository`` to create new ``Assets`` ora specific repository to
    operate on a predetermined set of ``Assets``. Another scenario is a
    federated provider who does not wish to permit administrative
    operations for the federation unaware.

    Example create:
      if (!session.canCreateAssets()) {
          return "asset creation not permitted";
      }

      Type types[1];
      types[0] = assetPhotographType;
      if (!session.canCreateAssetWithRecordTypes(types)) {
          return "creating an asset with a photograph type is not supported";
      }

      AssetForm form = session.getAssetFormForCreate();
      Metadata metadata = form.getDisplayNameMetadata();
      if (metadata.isReadOnly()) {
          return "cannot set display name";
      }

      form.setDisplayName("my photo");

      PhotographRecordForm photoForm = (PhotographRecordForn) form.getRecordForm(assetPhotogaphType);
      Metadata metadata = form.getApertureMetadata();
      if (metadata.isReadOnly()) {
          return ("cannot set aperture");
      }

      photoForm.setAperture("5.6");
      if (!form.isValid()) {
          return form.getValidationMessage();
      }

      Asset newAsset = session.createAsset(form);



    """
    def __init__(self, catalog_id=None, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        self._catalog_class = objects.Repository
        self._session_name = 'AssetAdminSession'
        self._catalog_name = 'Repository'
        OsidSession._init_object(
            self,
            catalog_id,
            proxy,
            runtime,
            db_name='repository',
            cat_name='Repository',
            cat_class=objects.Repository)
        self._forms = dict()
        self._kwargs = kwargs

    def get_repository_id(self):
        """Gets the ``Repository``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Repository Id`` associated with
                this session
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._catalog_id

    repository_id = property(fget=get_repository_id)

    def get_repository(self):
        """Gets the ``Repository`` associated with this session.

        return: (osid.repository.Repository) - the ``Repository``
                associated with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._catalog

    repository = property(fget=get_repository)

    def can_create_assets(self):
        """Tests if this user can create ``Assets``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known creating an ``Asset``
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer create
        operations to an unauthorized user.

        return: (boolean) - ``false`` if ``Asset`` creation is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def can_create_asset_with_record_types(self, asset_record_types):
        """Tests if this user can create a single ``Asset`` using the desired record types.

        While ``RepositoryManager.getAssetRecordTypes()`` can be used to
        examine which records are supported, this method tests which
        record(s) are required for creating a specific ``Asset``.
        Providing an empty array tests if an ``Asset`` can be created
        with no records.

        arg:    asset_record_types (osid.type.Type[]): array of asset
                record types
        return: (boolean) - ``true`` if ``Asset`` creation using the
                specified record ``Types`` is supported, ``false``
                otherwise
        raise:  NullArgument - ``asset_record_types`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_asset_form_for_create(self, asset_record_types):
        """Gets the asset form for creating new assets.

        A new form should be requested for each create transaction.

        arg:    asset_record_types (osid.type.Type[]): array of asset
                record types
        return: (osid.repository.AssetForm) - the asset form
        raise:  NullArgument - ``asset_record_types`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - unable to get form for requested record
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceAdminSession.get_resource_form_for_create_template

        for arg in asset_record_types:
            if not isinstance(arg, ABCType):
                raise errors.InvalidArgument('one or more argument array elements is not a valid OSID Type')
        if asset_record_types == []:
            obj_form = objects.AssetForm(
                repository_id=self._catalog_id,
                runtime=self._runtime,
                effective_agent_id=self.get_effective_agent_id(),
                proxy=self._proxy)
        else:
            obj_form = objects.AssetForm(
                repository_id=self._catalog_id,
                record_types=asset_record_types,
                runtime=self._runtime,
                effective_agent_id=self.get_effective_agent_id(),
                proxy=self._proxy)
        self._forms[obj_form.get_id().get_identifier()] = not CREATED
        return obj_form


    @utilities.arguments_not_none
    def create_asset(self, asset_form):
        """Creates a new ``Asset``.

        arg:    asset_form (osid.repository.AssetForm): the form for
                this ``Asset``
        return: (osid.repository.Asset) - the new ``Asset``
        raise:  IllegalState - ``asset_form`` already used in a create
                transaction
        raise:  InvalidArgument - one or more of the form elements is
                invalid
        raise:  NullArgument - ``asset_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``asset_form`` did not originate from
                ``get_asset_form_for_create()``
        *compliance: mandatory -- This method must be implemented.*

        """

        from dlkit_gstudio.gstudio_user_proxy import GStudioRequest
        from gnowsys_ndf.ndf.views.asset import create_asset as gstudio_create_asset
        req_obj = GStudioRequest(id=1)
        try:
            if self._forms[asset_form.get_id().get_identifier()] == CREATED:
                raise errors.IllegalState('asset_form already used in a create transaction')
        except KeyError:
            raise errors.Unsupported('asset_form did not originate from this session')
        if not asset_form.is_valid():
            raise errors.InvalidArgument('one or more of the form elements is invalid')
        self._forms[asset_form.get_id().get_identifier()] = CREATED
        # This should be part of _init_gstudio_map
        asset_name = asset_form._gstudio_map['name'].strip()
        asset_obj = gstudio_create_asset(group_id=self._catalog_id.get_identifier(),\
         created_by=1, **asset_form._gstudio_map)
        # asset_obj = gstudio_create_asset(group_id=self._catalog_id.get_identifier(),\
        # created_by=req_obj.user.id, **asset_form._gstudio_map)

        # # asset_obj is gstudio node
        if asset_obj:
            result = objects.Asset(
                gstudio_node=asset_obj,
                runtime=self._runtime,
                proxy=self._proxy)

            return result
        raise errors.OperationFailed()

    def can_update_assets(self):
        """Tests if this user can update ``Assets``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known updating an ``Asset``
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer update
        operations to an unauthorized user.

        return: (boolean) - ``false`` if ``Asset`` modification is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_asset_form_for_update(self, asset_id):
        """Gets the asset form for updating an existing asset.

        A new asset form should be requested for each update
        transaction.

        arg:    asset_id (osid.id.Id): the ``Id`` of the ``Asset``
        return: (osid.repository.AssetForm) - the asset form
        raise:  NotFound - ``asset_id`` is not found
        raise:  NullArgument - ``asset_id`` is null
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        if not isinstance(asset_id, ABCId):
            raise errors.InvalidArgument('the argument is not a valid OSID Id')
        if asset_id.get_identifier_namespace() != 'repository.Asset':
            if asset_id.get_authority() != self._authority:
                raise errors.InvalidArgument()
            else:
                asset_id = self._get_asset_id_with_enclosure(asset_id)

        result = Node.get_node_by_id(ObjectId(asset_id.get_identifier()))

        obj_form = objects.AssetForm(gstudio_node=result, repository_id=self._catalog_id,
                effective_agent_id=self.get_effective_agent_id(),runtime=self._runtime, proxy=self._proxy)
        obj_form._for_update = True
        self._forms[obj_form.get_id().get_identifier()] = not UPDATED
        return obj_form

    @utilities.arguments_not_none
    def update_asset(self, asset_form):
        """Updates an existing asset.

        arg:    asset_form (osid.repository.AssetForm): the form
                containing the elements to be updated
        raise:  IllegalState - ``asset_form`` already used in anupdate
                transaction
        raise:  InvalidArgument - the form contains an invalid value
        raise:  NullArgument - ``asset_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``asset_form`` did not originate from
                ``get_asset_form_for_update()``
        *compliance: mandatory -- This method must be implemented.*

        """
        from dlkit.abstract_osid.repository.objects import AssetForm as ABCAssetForm
        # collection = MongoClientValidated('repository',
        #                                   collection='Asset',
        #                                   runtime=self._runtime)
        if not isinstance(asset_form, ABCAssetForm):
            raise errors.InvalidArgument('argument type is not an AssetForm')
        if not asset_form.is_for_update():
            raise errors.InvalidArgument('the AssetForm is for update only, not create')
        try:
            if self._forms[asset_form.get_id().get_identifier()] == UPDATED:
                raise errors.IllegalState('asset_form already used in an update transaction')
        except KeyError:
            raise errors.Unsupported('asset_form did not originate from this session')
        if not asset_form.is_valid():
            raise errors.InvalidArgument('one or more of the form elements is invalid')


        from dlkit_gstudio.gstudio_user_proxy import GStudioRequest
        from gnowsys_ndf.ndf.views.asset import create_asset as gstudio_create_asset
        req_obj = GStudioRequest(id=1)
        asset_ident = asset_form._gstudio_map['asset_id']
        asset_obj_id = ObjectId(asset_ident)
        asset_obj = gstudio_create_asset(node_id = asset_obj_id, \
         group_id=self._catalog_id.get_identifier(), created_by=1, **asset_form._gstudio_map)
        # asset_obj = gstudio_create_asset(group_id=self._catalog_id.get_identifier(),\
         # created_by=req_obj.user.id, **asset_form._gstudio_map)

        # # asset_obj is gstudio node
        self._forms[asset_ident] = UPDATED
        if asset_obj:
            result = objects.Asset(
                gstudio_node=asset_obj,
                runtime=self._runtime,
                proxy=self._proxy)

            return result
        raise errors.OperationFailed()


    def can_delete_assets(self):
        """Tests if this user can delete ``Assets``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known deleting an ``Asset``
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer delete
        operations to an unauthorized user.

        return: (boolean) - ``false`` if ``Asset`` deletion is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def delete_asset(self, asset_id):
        """Deletes an ``Asset``.

        arg:    asset_id (osid.id.Id): the ``Id`` of the ``Asset`` to
                remove
        raise:  NotFound - ``asset_id`` not found
        raise:  NullArgument - ``asset_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_manage_asset_aliases(self):
        """Tests if this user can manage ``Id`` aliases for ``Assets``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known changing an alias
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer alias
        operations to an unauthorized user.

        return: (boolean) - ``false`` if ``Asset`` aliasing is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def alias_asset(self, asset_id, alias_id):
        """Adds an ``Id`` to an ``Asset`` for the purpose of creating compatibility.

        The primary ``Id`` of the ``Asset`` is determined by the
        provider. The new ``Id`` performs as an alias to the primary
        ``Id``. If the alias is a pointer to another asset, it is
        reassigned to the given asset ``Id``.

        arg:    asset_id (osid.id.Id): the ``Id`` of an ``Asset``
        arg:    alias_id (osid.id.Id): the alias ``Id``
        raise:  AlreadyExists - ``alias_id`` is already assigned
        raise:  NotFound - ``asset_id`` not found
        raise:  NullArgument - ``asset_id`` or ``alias_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_create_asset_content(self):
        """Tests if this user can create content for ``Assets``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known creating an
        ``AssetContent`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        create operations to an unauthorized user.

        return: (boolean) - ``false`` if ``Asset`` content creation is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def can_create_asset_content_with_record_types(self, asset_content_record_types):
        """Tests if this user can create an ``AssetContent`` using the desired record types.

        While ``RepositoryManager.getAssetContentRecordTypes()`` can be
        used to test which records are supported, this method tests
        which records are required for creating a specific
        ``AssetContent``. Providing an empty array tests if an
        ``AssetContent`` can be created with no records.

        arg:    asset_content_record_types (osid.type.Type[]): array of
                asset content record types
        return: (boolean) - ``true`` if ``AssetContent`` creation using
                the specified ``Types`` is supported, ``false``
                otherwise
        raise:  NullArgument - ``asset_content_record_types`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_asset_content_form_for_create(self, asset_id, asset_content_record_types):
        """Gets an asset content form for creating new assets.

        arg:    asset_id (osid.id.Id): the ``Id`` of an ``Asset``
        arg:    asset_content_record_types (osid.type.Type[]): array of
                asset content record types
        return: (osid.repository.AssetContentForm) - the asset content
                form
        raise:  NotFound - ``asset_id`` is not found
        raise:  NullArgument - ``asset_id`` or
                ``asset_content_record_types`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - unable to get form for requested record
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        if not isinstance(asset_id, ABCId):
            raise errors.InvalidArgument('argument is not a valid OSID Id')
        for arg in asset_content_record_types:
            if not isinstance(arg, ABCType):
                raise errors.InvalidArgument('one or more argument array elements is not a valid OSID Type')
        if asset_content_record_types == []:
            obj_form = objects.AssetContentForm(
                repository_id=self._catalog_id,
                asset_id=asset_id,
                catalog_id=self._catalog_id,
                runtime=self._runtime,
                proxy=self._proxy)
        else:
            obj_form = objects.AssetContentForm(
                repository_id=self._catalog_id,
                record_types=asset_content_record_types,
                asset_id=asset_id,
                catalog_id=self._catalog_id,
                runtime=self._runtime,
                proxy=self._proxy)
        obj_form._for_update = False
        self._forms[obj_form.get_id().get_identifier()] = not CREATED
        return obj_form


    @utilities.arguments_not_none
    def create_asset_content(self, asset_content_form):
        """Creates new ``AssetContent`` for a given asset.

        arg:    asset_content_form (osid.repository.AssetContentForm):
                the form for this ``AssetContent``
        return: (osid.repository.AssetContent) - the new
                ``AssetContent``
        raise:  IllegalState - ``asset_content_form`` already used in a
                create transaction
        raise:  InvalidArgument - one or more of the form elements is
                invalid
        raise:  NullArgument - ``asset_content_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``asset_content_form`` did not originate
                from ``get_asset_content_form_for_create()``
        *compliance: mandatory -- This method must be implemented.*

        """
        from dlkit_gstudio.gstudio_user_proxy import GStudioRequest
        from gnowsys_ndf.ndf.views.asset import create_assetcontent as gstudio_create_assetcontent
        req_obj = GStudioRequest(id=1)

        try:
            if self._forms[asset_content_form.get_id().get_identifier()] == CREATED:
                raise errors.IllegalState('asset_content_form already used in a create transaction')
        except KeyError:
            raise errors.Unsupported('asset_content_form did not originate from this session')
        if not asset_content_form.is_valid():
            raise errors.InvalidArgument('one or more of the form elements is invalid')
        self._forms[asset_content_form.get_id().get_identifier()] = CREATED
        asset_id = asset_content_form._gstudio_map['assetIdent']
        file_data = [None]
        content_data = None
        res_type = 'Page'
        if 'data' in asset_content_form._gstudio_map:
            file_data = [asset_content_form._gstudio_map['data']]
            res_type = 'File'
        else:
            content_data = asset_content_form._gstudio_map['content']
        assetcontent_obj = gstudio_create_assetcontent(asset_id=asset_id,\
         group_name_or_id=ObjectId(asset_content_form._catalog_id.identifier),\
         created_by=1, files=file_data, \
         resource_type=res_type, **asset_content_form._gstudio_map)
        # assetcontent_obj = gstudio_create_assetcontent(asset_id=asset_id,\
        #   group_name_or_id=ObjectId(asset_content_form._catalog_id.identifier),\
        #  created_by=req_obj.user.id, files=file_data, \
        #  resource_type=res_type, **asset_content_form._gstudio_map)

        return objects.AssetContent(gstudio_node=assetcontent_obj,
                              runtime=self._runtime,
                              proxy=self._proxy)

    def can_update_asset_contents(self):
        """Tests if this user can update ``AssetContent``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known updating an
        ``AssetContent`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        update operations to an unauthorized user.

        return: (boolean) - ``false`` if ``AssetContent`` modification
                is not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_asset_content_form_for_update(self, asset_content_id):
        """Gets the asset content form for updating an existing asset content.

        A new asset content form should be requested for each update
        transaction.

        arg:    asset_content_id (osid.id.Id): the ``Id`` of the
                ``AssetContent``
        return: (osid.repository.AssetContentForm) - the asset content
                form
        raise:  NotFound - ``asset_content_id`` is not found
        raise:  NullArgument - ``asset_content_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        from .objects import AssetContentForm
        # collection = MongoClientValidated('repository',
        #                                   collection='Asset',
        #                                   runtime=self._runtime)
        if not isinstance(asset_content_id, ABCId):
            raise errors.InvalidArgument('the argument is not a valid OSID Id')
        document = Node.get_node_by_id(asset_content_id.get_identifier())
        asset_id = None
        has_assetcontent_rt = node_collection.one({'_type': 'RelationType', 'name': 'has_assetcontent'})
        asset_content_ident = asset_content_id.identifier
        assetcontent_grel = triple_collection.find_one({'_type': 'GRelation',
            'right_subject': ObjectId(asset_content_ident), 'relation_type': has_assetcontent_rt._id,
            'status': u'PUBLISHED'}, {'subject': 1})

        if assetcontent_grel:
            asset_id = assetcontent_grel['subject']
            # asset_node = Node.get_node_by_id(asset_id)
            # return Asset(gstudio_node=asset_node)
            asset_id = (Id(identifier=str(asset_id), 
                namespace="repository.AssetContent",
                authority="GSTUDIO"))

        obj_form = AssetContentForm(gstudio_node=document,
                                    repository_id=self._catalog_id,
                                    asset_id=asset_id,
                                    catalog_id=self._catalog_id,
                                    runtime=self._runtime,
                                    proxy=self._proxy)

        obj_form._for_update = True
        self._forms[obj_form.get_id().get_identifier()] = not UPDATED
        return obj_form


    @utilities.arguments_not_none
    def update_asset_content(self, asset_content_form):
        """Updates an existing asset content.

        arg:    asset_content_form (osid.repository.AssetContentForm):
                the form containing the elements to be updated
        raise:  IllegalState - ``asset_content_form`` already used in an
                update transaction
        raise:  InvalidArgument - the form contains an invalid value
        raise:  NullArgument - ``asset_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``asset_content_form`` did not originate
                from ``get_asset_content_form_for_update()``
        *compliance: mandatory -- This method must be implemented.*

        """
        from dlkit.abstract_osid.repository.objects import AssetContentForm as ABCAssetContentForm
        # collection = MongoClientValidated('repository',
        #                                   collection='Asset',
        #                                   runtime=self._runtime)
        if not isinstance(asset_content_form, ABCAssetContentForm):
            raise errors.InvalidArgument('argument type is not an AssetContentForm')
        if not asset_content_form.is_for_update():
            raise errors.InvalidArgument('the AssetContentForm is for update only, not create')
        try:
            if self._forms[asset_content_form.get_id().get_identifier()] == UPDATED:
                raise errors.IllegalState('asset_content_form already used in an update transaction')
        except KeyError:
            raise errors.Unsupported('asset_content_form did not originate from this session')
        if not asset_content_form.is_valid():
            raise errors.InvalidArgument('one or more of the form elements is invalid')
        asset_id = Id(asset_content_form._my_map['assetId']).get_identifier()
        asset = Node.get_node_by_id(ObjectId(asset_id))
        # asset = collection.find_one(
        #     {'$and': [{'_id': ObjectId(asset_id)},
        #                {'assigned' + self._catalog_name + 'Ids': {'$in': [str(self._catalog_id)]}}]})
        index = 0
        found = False
        from dlkit_gstudio.gstudio_user_proxy import GStudioRequest
        from gnowsys_ndf.ndf.views.asset import create_assetcontent as gstudio_create_assetcontent
        req_obj = GStudioRequest(id=1)

        asset_id = asset_content_form._gstudio_map['assetIdent']
        file_data = [None]
        content_data = None
        res_type = 'Page'
        if 'data' in asset_content_form._gstudio_map:
            file_data = [asset_content_form._gstudio_map['data']]
            res_type = 'File'
        else:
            content_data = asset_content_form._gstudio_map['content']
        asset_content_id = None

        if 'gstudio_node' in asset_content_form._gstudio_map:
            asset_content_id = asset_content_form._gstudio_map['gstudio_node']['_id']
        assetcontent_obj = gstudio_create_assetcontent(asset_id=asset_id,node_id=asset_content_id,\
         group_name_or_id=ObjectId(asset_content_form._catalog_id.identifier),\
         created_by=1, files=file_data, \
         resource_type=res_type, **asset_content_form._gstudio_map)
        # assetcontent_obj = gstudio_create_assetcontent(asset_id=asset_id,\
        #  group_name_or_id=ObjectId(asset_content_form._catalog_id.identifier),\
        #  created_by=req_obj.user.id, files=file_data, \
        #  resource_type=res_type, **asset_content_form._gstudio_map)

        self._forms[asset_content_form.get_id().get_identifier()] = UPDATED
        # Note: this is out of spec. The OSIDs don't require an object to be returned:
        from .objects import AssetContent

        return objects.AssetContent(gstudio_node=assetcontent_obj,
                              runtime=self._runtime,
                              proxy=self._proxy)


    def can_delete_asset_contents(self):
        """Tests if this user can delete ``AssetsContents``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known deleting an
        ``AssetContent`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        delete operations to an unauthorized user.

        return: (boolean) - ``false`` if ``AssetContent`` deletion is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def delete_asset_content(self, asset_content_id):
        """Deletes content from an ``Asset``.

        arg:    asset_content_id (osid.id.Id): the ``Id`` of the
                ``AssetContent``
        raise:  NotFound - ``asset_content_id`` is not found
        raise:  NullArgument - ``asset_content_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssetNotificationSession(abc_repository_sessions.AssetNotificationSession, osid_sessions.OsidSession):
    """This session defines methods to receive notifications on adds/changes to ``Asset`` objects in this ``Repository``.

    This also includes existing assets that may appear or disappear due
    to changes in the ``Repository`` hierarchy, This session is intended
    for consumers needing to synchronize their state with this service
    without the use of polling. Notifications are cancelled when this
    session is closed.

    The two views defined in this session correspond to the views in the
    ``AssetLookupSession``.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_repository_id(self):
        """Gets the ``Repository``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Repository Id`` associated with
                this session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository_id = property(fget=get_repository_id)

    def get_repository(self):
        """Gets the ``Repository`` associated with this session.

        return: (osid.repository.Repository) - the ``Repository``
                associated with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository = property(fget=get_repository)

    def can_register_for_asset_notifications(self):
        """Tests if this user can register for ``Asset`` notifications.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer
        notification operations.

        return: (boolean) - ``false`` if notification methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def use_federated_repository_view(self):
        """Federates the view for methods in this session.

        A federated view will include assets in repositories which are
        children of this repository in the repository hierarchy.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_isolated_repository_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts notifications to this repository
        only.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def register_for_new_assets(self):
        """Register for notifications of new assets.

        ``AssetReceiver.newAssets()`` is invoked when a new ``Asset``
        appears in this repository.

        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def register_for_new_assets_by_genus_type(self, asset_genus_type):
        """Registers for notification of new assets of the given asset genus type.

        ``AssetReceiver.newAssets()`` is invoked when an asset is
        appears in this repository.

        arg:    asset_genus_type (osid.type.Type): the genus type of the
                ``Asset`` to monitor
        raise:  NullArgument - ``asset_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def register_for_changed_assets(self):
        """Registers for notification of updated assets.

        ``AssetReceiver.changedAssets()`` is invoked when an asset in
        this repository is changed.

        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def register_for_changed_assets_by_genus_type(self, asset_genus_type):
        """Registers for notification of updated assets of the given asset genus type.

        ``AssetReceiver.changedAssets()`` is invoked when an asset in
        this repository is changed.

        arg:    asset_genus_type (osid.type.Type): the genus type of the
                ``Asset`` to monitor
        raise:  NullArgument - ``asset_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def register_for_changed_asset(self, asset_id):
        """Registers for notification of an updated asset.

        ``AssetReceiver.changedAssets()`` is invoked when the specified
        asset in this repository is changed.

        arg:    asset_id (osid.id.Id): the ``Id`` of the ``Asset`` to
                monitor
        raise:  NullArgument - ``asset_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def register_for_deleted_assets(self):
        """Registers for notification of deleted assets.

        ``AssetReceiver.deletedAssets()`` is invoked when an asset is
        deleted or removed from this repository.

        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def register_for_deleted_assets_by_genus_type(self, asset_genus_type):
        """Registers for notification of deleted assets of the given asset genus type.

        ``AssetReceiver.deletedAssets()`` is invoked when an asset is
        deleted or removed from this repository.

        arg:    asset_genus_type (osid.type.Type): the genus type of the
                ``Asset`` to monitor
        raise:  NullArgument - ``asset_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def register_for_deleted_asset(self, asset_id):
        """Registers for notification of a deleted asset.

        ``AssetReceiver.deletedAssets()`` is invoked when the specified
        asset is deleted or removed from this repository.

        arg:    asset_id (osid.id.Id): the ``Id`` of the ``Asset`` to
                monitor
        raise:  NullArgument - ``asset_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def reliable_asset_notifications(self):
        """Reliable notifications are desired.

        In reliable mode, notifications are to be acknowledged using
        ``acknowledge_item_notification()`` .

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def unreliable_asset_notifications(self):
        """Unreliable notifications are desired.

        In unreliable mode, notifications do not need to be
        acknowledged.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def acknowledge_asset_notification(self, notification_id):
        """Acknowledge an asset notification.

        arg:    notification_id (osid.id.Id): the ``Id`` of the
                notification
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssetRepositorySession(abc_repository_sessions.AssetRepositorySession, osid_sessions.OsidSession):
    """This session provides methods to retrieve ``Assets`` to ``Repository`` mappings.

    An ``Asset`` may appear in multiple ``Repository`` objects. Each
    Repository may have its own authorizations governing who is allowed
    to look at it.

    This lookup session defines two views:

      * comparative view: elements may be silently omitted or re-ordered
      * plenary view: provides a complete result set or is an error
        condition


    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def can_lookup_asset_repository_mappings(self):
        """Tests if this user can perform lookups of asset/repository mappings.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known lookup methods in
        this session will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        lookup operations to unauthorized users.

        return: (boolean) - ``false`` if looking up mappings is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_comparative_repository_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_plenary_repository_view(self):
        """A complete view of the ``Asset`` and ``Repository`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_asset_ids_by_repository(self, repository_id):
        """Gets the list of ``Asset``  ``Ids`` associated with a ``Repository``.

        arg:    repository_id (osid.id.Id): ``Id`` of the ``Repository``
        return: (osid.id.IdList) - list of related asset ``Ids``
        raise:  NotFound - ``repository_id`` is not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assets_by_repository(self, repository_id):
        """Gets the list of ``Assets`` associated with a ``Repository``.

        arg:    repository_id (osid.id.Id): ``Id`` of the ``Repository``
        return: (osid.repository.AssetList) - list of related assets
        raise:  NotFound - ``repository_id`` is not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_asset_ids_by_repositories(self, repository_ids):
        """Gets the list of ``Asset Ids`` corresponding to a list of ``Repository`` objects.

        arg:    repository_ids (osid.id.IdList): list of repository
                ``Ids``
        return: (osid.id.IdList) - list of asset ``Ids``
        raise:  NullArgument - ``repository_ids`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assets_by_repositories(self, repository_ids):
        """Gets the list of ``Assets`` corresponding to a list of ``Repository`` objects.

        arg:    repository_ids (osid.id.IdList): list of repository
                ``Ids``
        return: (osid.repository.AssetList) - list of assets
        raise:  NullArgument - ``repository_ids`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_repository_ids_by_asset(self, asset_id):
        """Gets the list of ``Repository``  ``Ids`` mapped to an ``Asset``.

        arg:    asset_id (osid.id.Id): ``Id`` of an ``Asset``
        return: (osid.id.IdList) - list of repository ``Ids``
        raise:  NotFound - ``asset_id`` is not found
        raise:  NullArgument - ``asset_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_repositories_by_asset(self, asset_id):
        """Gets the list of ``Repository`` objects mapped to an ``Asset``.

        arg:    asset_id (osid.id.Id): ``Id`` of an ``Asset``
        return: (osid.repository.RepositoryList) - list of repositories
        raise:  NotFound - ``asset_id`` is not found
        raise:  NullArgument - ``asset_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssetRepositoryAssignmentSession(abc_repository_sessions.AssetRepositoryAssignmentSession, osid_sessions.OsidSession):
    """This session provides methods to re-assign ``Assets`` to ``Repositories``.

    An ``Asset`` may map to multiple ``Repository`` objects and removing
    the last reference to an ``Asset`` is the equivalent of deleting it.
    Each ``Repository`` may have its own authorizations governing who is
    allowed to operate on it.

    Moving or adding a reference of an ``Asset`` to another
    ``Repository`` is not a copy operation (eg: does not change its
    ``Id`` ).

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def can_assign_assets(self):
        """Tests if this user can alter asset/repository mappings.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known mapping methods in
        this session will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        assignment operations to unauthorized users.

        return: (boolean) - ``false`` if mapping is not authorized,
                ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def can_assign_assets_to_repository(self, repository_id):
        """Tests if this user can alter asset/repository mappings.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known mapping methods in
        this session will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        assignment operations to unauthorized users.

        arg:    repository_id (osid.id.Id): the ``Id`` of the
                ``Repository``
        return: (boolean) - ``false`` if mapping is not authorized,
                ``true`` otherwise
        raise:  NullArgument - ``repository_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_assignable_repository_ids(self, repository_id):
        """Gets a list of repositories including and under the given repository node in which any asset can be assigned.

        arg:    repository_id (osid.id.Id): the ``Id`` of the
                ``Repository``
        return: (osid.id.IdList) - list of assignable repository ``Ids``
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assignable_repository_ids_for_asset(self, repository_id, asset_id):
        """Gets a list of repositories including and under the given repository node in which a specific asset can be assigned.

        arg:    repository_id (osid.id.Id): the ``Id`` of the
                ``Repository``
        arg:    asset_id (osid.id.Id): the ``Id`` of the ``Asset``
        return: (osid.id.IdList) - list of assignable repository ``Ids``
        raise:  NullArgument - ``repository_id`` or ``asset_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def assign_asset_to_repository(self, asset_id, repository_id):
        """Adds an existing ``Asset`` to a ``Repository``.

        arg:    asset_id (osid.id.Id): the ``Id`` of the ``Asset``
        arg:    repository_id (osid.id.Id): the ``Id`` of the
                ``Repository``
        raise:  AlreadyExists - ``asset_id`` already assigned to
                ``repository_id``
        raise:  NotFound - ``asset_id`` or ``repository_id`` not found
        raise:  NullArgument - ``asset_id`` or ``repository_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def unassign_asset_from_repository(self, asset_id, repository_id):
        """Removes an ``Asset`` from a ``Repository``.

        arg:    asset_id (osid.id.Id): the ``Id`` of the ``Asset``
        arg:    repository_id (osid.id.Id): the ``Id`` of the
                ``Repository``
        raise:  NotFound - ``asset_id`` or ``repository_id`` not found
                or ``asset_id`` not assigned to ``repository_id``
        raise:  NullArgument - ``asset_id`` or ``repository_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssetCompositionSession(abc_repository_sessions.AssetCompositionSession, osid_sessions.OsidSession):
    """This session defines methods for looking up ``Asset`` to ``Composition`` mappings.

    A ``Composition`` represents a collection of ``Assets``.

    This lookup session defines several views:

      * comparative view: elements may be silently omitted or re-ordered
      * plenary view: provides a complete result set or is an error
        condition
      * isolated repository view: All lookup methods in this session
        operate, retrieve and pertain to asseta and compositions defined
        explicitly in the current repository. Using an isolated view is
        useful for managing compositions with the
        CompositionAdminSession.
      * federated repository view: All lookup methods in this session
        operate, retrieve and pertain to all compositions and assets
        defined in this repository and any other compositions implicitly
        available in this repository through repository inheritence.


    The methods ``use_federated_asset_composition_view()`` and
    ``use_isolated_asset_compositiont_view()`` behave as a radio group
    and one should be selected before invoking any lookup methods.

    """

    def get_repository_id(self):
        """Gets the ``Repository``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Repository Id`` associated with
                this session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository_id = property(fget=get_repository_id)

    def get_repository(self):
        """Gets the ``Repository`` associated with this session.

        return: (osid.repository.Repository) - the ``Repository``
                associated with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository = property(fget=get_repository)

    def can_access_asset_compositions(self):
        """Tests if this user can perform composition lookups.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer lookup
        operations to unauthorized users.

        return: (boolean) - ``false`` if lookup methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def use_comparative_asset_composition_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_plenary_asset_composition_view(self):
        """A complete view of the returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_federated_repository_view(self):
        """Federates the view for methods in this session.

        A federated view will include compositions in repositories which
        are children of this repository in the repository hierarchy.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_isolated_repository_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts lookups to this repository only.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_composition_assets(self, composition_id):
        """Gets the list of assets mapped to the given ``Composition``.

        arg:    composition_id (osid.id.Id): ``Id`` of the
                ``Composition``
        return: (osid.repository.AssetList) - list of assets
        raise:  NotFound - ``composition_id`` not found
        raise:  NullArgument - ``composition_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_compositions_by_asset(self, asset_id):
        """Gets a list of compositions including the given asset.

        arg:    asset_id (osid.id.Id): ``Id`` of the ``Asset``
        return: (osid.repository.CompositionList) - the returned
                ``Composition list``
        raise:  NotFound - ``asset_id`` is not found
        raise:  NullArgument - ``asset_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssetCompositionDesignSession(abc_repository_sessions.AssetCompositionDesignSession, osid_sessions.OsidSession):
    """This session provides the means for adding assets to an asset composiiton.

    The asset is identified inside a composition using its own Id. To
    add the same asset to the composition, multiple compositions should
    be used and placed at the same level in the ``Composition``
    hierarchy.

    """

    def get_repository_id(self):
        """Gets the ``Repository``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Repository Id`` associated with
                this session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository_id = property(fget=get_repository_id)

    def get_repository(self):
        """Gets the ``Repository`` associated with this session.

        return: (osid.repository.Repository) - the ``Repository``
                associated with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository = property(fget=get_repository)

    def can_compose_assets(self):
        """Tests if this user can manage mapping of ``Assets`` to ``Compositions``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as an application hint that may opt not to offer composition
        operations.

        return: (boolean) - ``false`` if asset composiion is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def add_asset(self, asset_id, composition_id):
        """Appends an asset to a composition.

        arg:    asset_id (osid.id.Id): ``Id`` of the ``Asset``
        arg:    composition_id (osid.id.Id): ``Id`` of the
                ``Composition``
        raise:  AlreadyExists - ``asset_id`` already part
                ``composition_id``
        raise:  NotFound - ``asset_id`` or ``composition_id`` not found
        raise:  NullArgument - ``asset_id`` or ``composition_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization fauilure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def move_asset_ahead(self, asset_id, composition_id, reference_id):
        """Reorders assets in a composition by moving the specified asset in front of a reference asset.

        arg:    asset_id (osid.id.Id): ``Id`` of the ``Asset``
        arg:    composition_id (osid.id.Id): ``Id`` of the
                ``Composition``
        arg:    reference_id (osid.id.Id): ``Id`` of the reference
                ``Asset``
        raise:  NotFound - ``asset_id`` or ``reference_id``  ``not found
                in composition_id``
        raise:  NullArgument - ``asset_id, reference_id`` or
                ``composition_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization fauilure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def move_asset_behind(self, asset_id, composition_id, reference_id):
        """Reorders assets in a composition by moving the specified asset behind of a reference asset.

        arg:    asset_id (osid.id.Id): ``Id`` of the ``Asset``
        arg:    composition_id (osid.id.Id): ``Id`` of the
                ``Composition``
        arg:    reference_id (osid.id.Id): ``Id`` of the reference
                ``Asset``
        raise:  NotFound - ``asset_id`` or ``reference_id``  ``not found
                in composition_id``
        raise:  NullArgument - ``asset_id, reference_id`` or
                ``composition_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization fauilure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_assets(self, asset_ids, composition_id):
        """Reorders a set of assets in a composition.

        arg:    asset_ids (osid.id.Id[]): ``Ids`` for a set of
                ``Assets``
        arg:    composition_id (osid.id.Id): ``Id`` of the
                ``Composition``
        raise:  NotFound - ``composition_id`` not found or, an
                ``asset_id`` not related to ``composition_id``
        raise:  NullArgument - ``instruction_ids`` or ``agenda_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def remove_asset(self, asset_id, composition_id):
        """Removes an ``Asset`` from a ``Composition``.

        arg:    asset_id (osid.id.Id): ``Id`` of the ``Asset``
        arg:    composition_id (osid.id.Id): ``Id`` of the
                ``Composition``
        raise:  NotFound - ``asset_id``  ``not found in composition_id``
        raise:  NullArgument - ``asset_id`` or ``composition_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization fauilure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class CompositionLookupSession(abc_repository_sessions.CompositionLookupSession, osid_sessions.OsidSession):
    """This session provides methods for retrieving ``Composition`` objects.

    The ``Composition`` represents a collection of ``Assets``.

    This session defines views that offer differing behaviors when
    retrieving multiple objects.

      * comparative view: elements may be silently omitted or re-ordered
      * plenary view: provides a complete and ordered result set or is
        an error condition
      * isolated repository view: All lookup methods in this session
        operate, retrieve and pertain to compositions defined explicitly
        in the current repository. Using an isolated view is useful for
        managing compositions with the ``CompositionAdminSession.``
      * federated repository view: All composition methods in this
        session operate, retrieve and pertain to all compositions
        defined in this repository and any other compositions implicitly
        available in this repository through repository inheritence.
      * active composition view: All composition lookup methods return
        active compositions.
      * any status composition view: Compositions of any active or
        inactive status are returned from methods.
      * sequestered composition viiew: All composition methods suppress
        sequestered compositions.
      * unsequestered composition view: All composition methods return
        all compositions.


    Generally, the comparative view should be used for most applications
    as it permits operation even if there is data that cannot be
    accessed. For example, a browsing application may only need to
    examine the ``Composition`` it can access, without breaking
    execution. However, an administrative application may require a
    complete set of ``Composition`` objects to be returned.

    Compositions may have an additional records indicated by their
    respective record types. The record may not be accessed through a
    cast of the ``Composition``.

    """

    def get_repository_id(self):
        """Gets the ``Repository``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Repository Id`` associated with
                this session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository_id = property(fget=get_repository_id)

    def get_repository(self):
        """Gets the ``Repository`` associated with this session.

        return: (osid.repository.Repository) - the ``Repository``
                associated with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository = property(fget=get_repository)

    def can_lookup_compositions(self):
        """Tests if this user can perform ``Composition`` lookups.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer lookup
        operations to unauthorized users.

        return: (boolean) - ``false`` if lookup methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_comparative_composition_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_plenary_composition_view(self):
        """A complete view of the ``Composition`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_federated_repository_view(self):
        """Federates the view for methods in this session.

        A federated view will include compositions in repositories which
        are children of this repository in the repository hierarchy.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_isolated_repository_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts lookups to this repository only.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_active_composition_view(self):
        """Only active compositions are returned by methods in this session.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_any_status_composition_view(self):
        """All active and inactive compositions are returned by methods in this session.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_sequestered_composition_view(self):
        """The methods in this session omit sequestered compositions.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_unsequestered_composition_view(self):
        """The methods in this session return all compositions, including sequestered compositions.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_composition(self, composition_id):
        """Gets the ``Composition`` specified by its ``Id``.

        arg:    composition_id (osid.id.Id): ``Id`` of the
                ``Composiiton``
        return: (osid.repository.Composition) - the composition
        raise:  NotFound - ``composition_id`` not found
        raise:  NullArgument - ``composition_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_compositions_by_ids(self, composition_ids):
        """Gets a ``CompositionList`` corresponding to the given ``IdList``.

        arg:    composition_ids (osid.id.IdList): the list of ``Ids`` to
                retrieve
        return: (osid.repository.CompositionList) - the returned
                ``Composition list``
        raise:  NotFound - an ``Id`` was not found
        raise:  NullArgument - ``composition_ids`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_compositions_by_genus_type(self, composition_genus_type):
        """Gets a ``CompositionList`` corresponding to the given composition genus ``Type`` which does not include compositions of types derived from the specified ``Type``.

        arg:    composition_genus_type (osid.type.Type): a composition
                genus type
        return: (osid.repository.CompositionList) - the returned
                ``Composition list``
        raise:  NullArgument - ``composition_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_compositions_by_parent_genus_type(self, composition_genus_type):
        """Gets a ``CompositionList`` corresponding to the given composition genus ``Type`` and include any additional compositions with genus types derived from the specified ``Type``.

        arg:    composition_genus_type (osid.type.Type): a composition
                genus type
        return: (osid.repository.CompositionList) - the returned
                ``Composition list``
        raise:  NullArgument - ``composition_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_compositions_by_record_type(self, composition_record_type):
        """Gets a ``CompositionList`` containing the given composition record ``Type``.

        arg:    composition_record_type (osid.type.Type): a composition
                record type
        return: (osid.repository.CompositionList) - the returned
                ``Composition list``
        raise:  NullArgument - ``composition_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_compositions_by_provider(self, resource_id):
        """Gets a ``CompositionList`` from the given provider ````.

        In plenary mode, the returned list contains all known
        compositions or an error results. Otherwise, the returned list
        may contain only those compositions that are accessible through
        this session.

        In sequestered mode, no sequestered compositions are returned.
        In unsequestered mode, all compositions are returned.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        return: (osid.repository.CompositionList) - the returned
                ``Composition list``
        raise:  NullArgument - ``resource_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_compositions(self):
        """Gets all ``Compositions``.

        return: (osid.repository.CompositionList) - a list of
                ``Compositions``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    compositions = property(fget=get_compositions)


class CompositionQuerySession(abc_repository_sessions.CompositionQuerySession, osid_sessions.OsidSession):
    """This session provides methods for searching among ``Composition`` objects.

    The search query is constructed using the ``CompositionQuery``.

    This session defines views that offer differing behaviors when
    searching.

      * federated repository view: searches include compositions in
        repositories of which this repository is an ancestor in the
        repository hierarchy
      * isolated repository view: searches are restricted to subjects in
        this repository
      * sequestered composition viiew: All composition methods suppress
        sequestered compositions.
      * unsequestered composition view: All composition methods return
        all compositions.


    Compositions may have a query record indicated by their respective
    record types. The query record is accessed via the
    ``CompositionQuery``.

    """

    def get_repository_id(self):
        """Gets the ``Repository``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Repository Id`` associated with
                this session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository_id = property(fget=get_repository_id)

    def get_repository(self):
        """Gets the ``Repository`` associated with this session.

        return: (osid.repository.Repository) - the ``Repository``
                associated with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository = property(fget=get_repository)

    def can_search_compositions(self):
        """Tests if this user can perform ``Composition`` searches.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer search
        operations to unauthorized users.

        return: (boolean) - ``false`` if search methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_federated_repository_view(self):
        """Federates the view for methods in this session.

        A federated view will include compositions in repositories which
        are children of this repository in the repository hierarchy.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_isolated_repository_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts lookups to this repository only.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_sequestered_composition_view(self):
        """The methods in this session omit sequestered compositions.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_unsequestered_composition_view(self):
        """The methods in this session return all compositions, including sequestered compositions.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def get_composition_query(self):
        """Gets a composition query.

        return: (osid.repository.CompositionQuery) - the composition
                query
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    composition_query = property(fget=get_composition_query)

    @utilities.arguments_not_none
    def get_compositions_by_query(self, composition_query):
        """Gets a list of ``Compositions`` matching the given composition query.

        arg:    composition_query (osid.repository.CompositionQuery):
                the composition query
        return: (osid.repository.CompositionList) - the returned
                ``CompositionList``
        raise:  NullArgument - ``composition_query`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``composition_query`` is not of this
                service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class CompositionSearchSession(abc_repository_sessions.CompositionSearchSession, CompositionQuerySession):
    """This session provides methods for searching among ``Composition`` objects.

    The search query is constructed using the ``CompositionQuery``.

    ``get_compositions_by_query()`` is the basic search method and
    returns a list of ``Compositions``. A more advanced search may be
    performed with ``getCompositionsBySearch()``. It accepts an
    ``Composition`` in addition to the query for the purpose of
    specifying additional options affecting the entire search, such as
    ordering. ``get_compositions_by_search()`` returns an
    ``CompositionSearchResults`` that can be used to access the
    resulting ``Composition`` or be used to perform a search within the
    result set through ``CompositionSearch``.

    This session defines views that offer differing behaviors when
    searching.

      * federated repository view: searches include compositions in
        repositories of which this repository is an ancestor in the
        repository hierarchy
      * isolated repository view: searches are restricted to subjects in
        this repository


    Compositions may have a query record indicated by their respective
    record types. The query record is accessed via the
    ``CompositionQuery``.

    """

    def get_composition_search(self):
        """Gets a composition search.

        return: (osid.repository.CompositionSearch) - the composition
                search
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    composition_search = property(fget=get_composition_search)

    def get_composition_search_order(self):
        """Gets a composition search order.

        The ``CompositionSearchOrder`` is supplied to an
        ``CompositionSearch`` to specify the ordering of results.

        return: (osid.repository.CompositionSearchOrder) - the
                composition search order
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    composition_search_order = property(fget=get_composition_search_order)

    @utilities.arguments_not_none
    def get_compositions_by_search(self, composition_query, composition_search):
        """Gets the search results matching the given search query using the given search.

        arg:    composition_query (osid.repository.CompositionQuery):
                the composition query
        arg:    composition_search (osid.repository.CompositionSearch):
                the composition search
        return: (osid.repository.CompositionSearchResults) - the
                composition search results
        raise:  NullArgument - ``composition_query`` or
                ``composition_search`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``composition_query`` or
                ``composition_search`` is not of this service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_composition_query_from_inspector(self, composition_query_inspector):
        """Gets a composition query from an inspector.

        The inspector is available from a ``CompositionSearchResults``.

        arg:    composition_query_inspector
                (osid.repository.CompositionQueryInspector): a
                composition query inspector
        return: (osid.repository.CompositionQuery) - the composition
                query
        raise:  NullArgument - ``composition_query_inspector`` is
                ``null``
        raise:  Unsupported - ``composition_query_inspector`` is not of
                this service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class CompositionAdminSession(abc_repository_sessions.CompositionAdminSession, osid_sessions.OsidSession):
    """This session creates, updates, and deletes ``Compositions``.

    The data for create and update is provided by the consumer via the
    form object. ``OsidForms`` are requested for each create or update
    and may not be reused.

    Create and update operations differ in their usage. To create a
    ``Composition,`` a ``CompositionForm`` is requested using
    ``get_composition_form_for_create()`` specifying the desired record
    ``Types`` or none if no record ``Types`` are needed. The returned
    ``CompositionForm`` will indicate that it is to be used with a
    create operation and can be used to examine metdata or validate data
    prior to creation. Once the ``CompositionForm`` is submiited to a
    create operation, it cannot be reused with another create operation
    unless the first operation was unsuccessful. Each
    ``CompositionForm`` corresponds to an attempted transaction.

    For updates, ``CompositionForms`` are requested to the
    ``Composition``  ``Id`` that is to be updated using
    ``getCompositionFormForUpdate()``. Similarly, the
    ``CompositionForm`` has metadata about the data that can be updated
    and it can perform validation before submitting the update. The
    ``CompositionForm`` can only be used once for a successful update
    and cannot be reused.

    The delete operations delete ``Compositions``. To unmap a
    ``Composition`` from the current ``Repository,`` the
    ``CompositionRepositoryAssignmentSession`` should be used. These
    delete operations attempt to remove the ``Bid`` itself thus removing
    it from all known ``Repository`` catalogs.

    This session includes an ``Id`` aliasing mechanism to assign an
    external ``Id`` to an internally assigned Id.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_repository_id(self):
        """Gets the ``Repository``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Repository Id`` associated with
                this session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository_id = property(fget=get_repository_id)

    def get_repository(self):
        """Gets the ``Repository`` associated with this session.

        return: (osid.repository.Repository) - the ``Repository``
                associated with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository = property(fget=get_repository)

    def can_create_compositions(self):
        """Tests if this user can create ``Compositions``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known creating a
        ``Composition`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may not wish to offer
        create operations to unauthorized users.

        return: (boolean) - ``false`` if ``Composition`` creation is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def can_create_composition_with_record_types(self, composition_record_types):
        """Tests if this user can create a single ``Composition`` using the desired record types.

        While ``RepositoryManager.getCompositionRecordTypes()`` can be
        used to examine which records are supported, this method tests
        which record(s) are required for creating a specific
        ``Composition``. Providing an empty array tests if a
        ``Composition`` can be created with no records.

        arg:    composition_record_types (osid.type.Type[]): array of
                composition record types
        return: (boolean) - ``true`` if ``Composition`` creation using
                the specified ``Types`` is supported, ``false``
                otherwise
        raise:  NullArgument - ``composition_record_types`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_composition_form_for_create(self, composition_record_types):
        """Gets the composition form for creating new compositions.

        A new form should be requested for each create transaction.

        arg:    composition_record_types (osid.type.Type[]): array of
                composition record types
        return: (osid.repository.CompositionForm) - the composition form
        raise:  NullArgument - ``composition_record_types`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - unable to get form for requested record
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def create_composition(self, composiiton_form):
        """Creates a new ``Composition``.

        arg:    composiiton_form (osid.repository.CompositionForm): the
                form for this ``Composition``
        return: (osid.repository.Composition) - the new ``Composition``
        raise:  IllegalState - ``composition_form`` already used in a
                create transaction
        raise:  InvalidArgument - one or more of the form elements is
                invalid
        raise:  NullArgument - ``composition_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``composition_form`` did not originate
                from ``get_composition_form_for_create()``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_update_compositions(self):
        """Tests if this user can update ``Compositions``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known updating a
        ``Composition`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may not wish to offer
        update operations to unauthorized users.

        return: (boolean) - ``false`` if ``Composition`` modification is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_composition_form_for_update(self, composition_id):
        """Gets the composition form for updating an existing composition.

        A new composition form should be requested for each update
        transaction.

        arg:    composition_id (osid.id.Id): the ``Id`` of the
                ``Composition``
        return: (osid.repository.CompositionForm) - the composition form
        raise:  NotFound - ``composition_id`` is not found
        raise:  NullArgument - ``composition_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def update_composition(self, composiiton_form):
        """Updates an existing composition.

        arg:    composiiton_form (osid.repository.CompositionForm): the
                form containing the elements to be updated
        raise:  IllegalState - ``composition_form`` already used in an
                update transaction
        raise:  InvalidArgument - the form contains an invalid value
        raise:  NullArgument - ``composition_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``composition_form`` did not originate
                from ``get_composition_form_for_update()``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_delete_compositions(self):
        """Tests if this user can delete ``Compositions``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known deleting a
        ``Composition`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may not wish to offer
        delete operations to unauthorized users.

        return: (boolean) - ``false`` if ``Composition`` deletion is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def delete_composition(self, composition_id):
        """Deletes a ``Composition``.

        arg:    composition_id (osid.id.Id): the ``Id`` of the
                ``Composition`` to remove
        raise:  NotFound - ``composition_id`` not found
        raise:  NullArgument - ``composition_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def delete_composition_node(self, composition_id):
        """Deletes a ``Composition`` and all contained children.

        arg:    composition_id (osid.id.Id): the ``Id`` of the
                ``Composition`` to remove
        raise:  NotFound - ``composition_id`` not found
        raise:  NullArgument - ``composition_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def add_composition_child(self, composition_id, child_composition_id):
        """Adds a composition to a parent composition.

        arg:    composition_id (osid.id.Id): the ``Id`` of a parent
                ``Composition``
        arg:    child_composition_id (osid.id.Id): the ``Id`` of a child
                ``Composition``
        raise:  AlreadyExists - ``child_composition_id`` is already a
                child of ``composition_id``
        raise:  NotFound - ``composition_id`` or
                ``child_composition_id`` is not found
        raise:  NullArgument - ``composition_id`` or
                ``child_composition_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def remove_composition_child(self, composition_id, child_composition_id):
        """Removes a composition from a parent composition.

        arg:    composition_id (osid.id.Id): the ``Id`` of a parent
                ``Composition``
        arg:    child_composition_id (osid.id.Id): the ``Id`` of a child
                ``Composition``
        raise:  NotFound - ``composition_id`` or
                ``child_composition_id`` is not found or not related
        raise:  NullArgument - ``composition_id`` or
                ``child_composition_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_manage_composition_aliases(self):
        """Tests if this user can manage ``Id`` aliases for ``Compositions``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known changing an alias
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer alias
        operations to an unauthorized user.

        return: (boolean) - ``false`` if ``Composition`` aliasing is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def alias_composition(self, composition_id, alias_id):
        """Adds an ``Id`` to a ``Composition`` for the purpose of creating compatibility.

        The primary ``Id`` of the ``Composition`` is determined by the
        provider. The new ``Id`` is an alias to the primary ``Id``. If
        the alias is a pointer to another composition, it is reassigned
        to the given composition ``Id``.

        arg:    composition_id (osid.id.Id): the ``Id`` of a
                ``Composition``
        arg:    alias_id (osid.id.Id): the alias ``Id``
        raise:  AlreadyExists - ``alias_id`` is in use as a primary
                ``Id``
        raise:  NotFound - ``composition_id`` not found
        raise:  NullArgument - ``composition_id`` or ``alias_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class CompositionRepositorySession(abc_repository_sessions.CompositionRepositorySession, osid_sessions.OsidSession):
    """This session provides methods to retrieve ``Composition`` to ``Repository`` mappings.

    A ``Composition`` may appear in multiple ``Repository`` objects.
    Each ``Repository`` may have its own authorizations governing who is
    allowed to look at it.

    This lookup session defines several views:

      * comparative view: elements may be silently omitted or re-ordered
      * plenary view: provides a complete result set or is an error
        condition


    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def use_comparative_composition_repository_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_plenary_composition_repository_view(self):
        """A complete view of the ``Composition`` and ``Repository`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def can_lookup_composition_repository_mappings(self):
        """Tests if this user can perform lookups of composition/repository mappings.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known lookup methods in
        this session will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        lookup operations to unauthorized users.

        return: (boolean) - ``false`` if looking up mappings is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_composition_ids_by_repository(self, repository_id):
        """Gets the list of ``Composition``  ``Ids`` associated with a ``Repository``.

        arg:    repository_id (osid.id.Id): ``Id`` of the ``Repository``
        return: (osid.id.IdList) - list of related composition ``Ids``
        raise:  NotFound - ``repository_id`` is not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_compositions_by_repository(self, repository_id):
        """Gets the list of ``Compositions`` associated with a ``Repository``.

        arg:    repository_id (osid.id.Id): ``Id`` of the ``Repository``
        return: (osid.repository.CompositionList) - list of related
                compositions
        raise:  NotFound - ``repository_id`` is not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_composition_ids_by_repositories(self, repository_ids):
        """Gets the list of ``Composition``  ``Ids`` corresponding to a list of ``Repository`` objects.

        arg:    repository_ids (osid.id.IdList): list of repository
                ``Ids``
        return: (osid.id.IdList) - list of composition ``Ids``
        raise:  NullArgument - ``repository_ids`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_compoitions_by_repositories(self, repository_ids):
        """Gets the list of ``Compositions`` corresponding to a list of ``Repository`` objects.

        arg:    repository_ids (osid.id.IdList): list of repository
                ``Ids``
        return: (osid.repository.CompositionList) - list of Compositions
        raise:  NullArgument - ``repository_ids`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_repository_ids_by_composition(self, composition_id):
        """Gets the ``Repository``  ``Ids`` mapped to a ``Composition``.

        arg:    composition_id (osid.id.Id): ``Id`` of a ``Composition``
        return: (osid.id.IdList) - list of repository ``Ids``
        raise:  NotFound - ``composition_id`` is not found
        raise:  NullArgument - ``composition_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_repositories_by_composition(self, composition_id):
        """Gets the ``Repository`` objects mapped to a ``Composition``.

        arg:    composition_id (osid.id.Id): ``Id`` of a ``Composition``
        return: (osid.repository.RepositoryList) - list of repositories
        raise:  NotFound - ``composition_id`` is not found
        raise:  NullArgument - ``composition_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class CompositionRepositoryAssignmentSession(abc_repository_sessions.CompositionRepositoryAssignmentSession, osid_sessions.OsidSession):
    """This session provides methods to re-assign ``Compositions`` to ``Repository`` objects.

    A ``Composition`` may be associated with multiple ``Repository``
    objects. Removing the last reference to a ``Composition`` is the
    equivalent of deleting it. Each ``Repository`` may have its own
    authorizations governing who is allowed to operate on it.

    Moving or adding a reference of a ``Composition`` to another
    ``Repository`` is not a copy operation (eg: does not change its
    ``Id`` ).

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def can_assign_compositions(self):
        """Tests if this user can alter composition/repository mappings.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known mapping methods in
        this session will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        assignment operations to unauthorized users.

        return: (boolean) - ``false`` if mapping is not authorized,
                ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def can_assign_compositions_to_repository(self, repository_id):
        """Tests if this user can alter composition/repository mappings.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known mapping methods in
        this session will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        assignment operations to unauthorized users.

        arg:    repository_id (osid.id.Id): the ``Id`` of the
                ``Repository``
        return: (boolean) - ``false`` if mapping is not authorized,
                ``true`` otherwise
        raise:  NullArgument - ``repository_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_assignable_repository_ids(self, repository_id):
        """Gets a list of repositories including and under the given repository node in which any composition can be assigned.

        arg:    repository_id (osid.id.Id): the ``Id`` of the
                ``Repository``
        return: (osid.id.IdList) - list of assignable repository ``Ids``
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assignable_repository_ids_for_composition(self, repository_id, composition_id):
        """Gets a list of repositories including and under the given repository node in which a specific composition can be assigned.

        arg:    repository_id (osid.id.Id): the ``Id`` of the
                ``Repository``
        arg:    composition_id (osid.id.Id): the ``Id`` of the
                ``Composition``
        return: (osid.id.IdList) - list of assignable repository ``Ids``
        raise:  NullArgument - ``repository_id`` or ``composition_id``
                is ``null``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def assign_composition_to_repository(self, composition_id, repository_id):
        """Adds an existing ``Composition`` to a ``Repository``.

        arg:    composition_id (osid.id.Id): the ``Id`` of the
                ``Composition``
        arg:    repository_id (osid.id.Id): the ``Id`` of the
                ``Repository``
        raise:  AlreadyExists - ``composition_id`` already assigned to
                ``repository_id``
        raise:  NotFound - ``composition_id`` or ``repository_id`` not
                found
        raise:  NullArgument - ``composition_id`` or ``repository_id``
                is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def unassign_composition_from_repository(self, composition_id, repository_id):
        """Removes ``Composition`` from a ``Repository``.

        arg:    composition_id (osid.id.Id): the ``Id`` of the
                ``Composition``
        arg:    repository_id (osid.id.Id): the ``Id`` of the
                ``Repository``
        raise:  NotFound - ``composition_id`` or ``repository_id`` not
                found or ``composition_id`` not assigned to
                ``repository_id``
        raise:  NullArgument - ``composition_id`` or ``repository_id``
                is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class RepositoryLookupSession(abc_repository_sessions.RepositoryLookupSession, osid_sessions.OsidSession):
    """This session provides methods for retrieving ``Repository`` objects.

    The ``Repository`` represents a collection of ``Assets`` and
    ``Compositions``.

    This session defines views that offer differing behaviors when
    retrieving multiple objects.

      * comparative view: elements may be silently omitted or re-ordered
      * plenary view: provides a complete set or is an error condition


    Generally, the comparative view should be used for most applications
    as it permits operation even if there is data that cannot be
    accessed. For example, a browsing application may only need to
    examine the ``Repositories`` it can access, without breaking
    execution. However, an administrative application may require all
    ``Repository`` elements to be available.

    Repositories may have an additional records indicated by their
    respective record types. The record may not be accessed through a
    cast of the ``Repository``.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(self, proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def can_lookup_repositories(self):
        """Tests if this user can perform ``Repository`` lookups.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer lookup
        operations to unauthorized users.

        return: (boolean) - ``false`` if lookup methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_comparative_repository_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        # raise errors.Unimplemented()
        pass

    def use_plenary_repository_view(self):
        """A complete view of the ``Repository`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        pass
        # raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_repository(self, repository_id):
        """Gets the ``Repository`` specified by its ``Id``.

        In plenary mode, the exact ``Id`` is found or a ``NotFound``
        results. Otherwise, the returned ``Repository`` may have a
        different ``Id`` than requested, such as the case where a
        duplicate ``Id`` was assigned to a ``Repository`` and retained
        for compatibility.

        arg:    repository_id (osid.id.Id): ``Id`` of the ``Repository``
        return: (osid.repository.Repository) - the repository
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method is must be implemented.*

        """
        # repository_id will be of type  dlkit.primordium.id.primitives.Id
        #return objects.Repository(gstudio_node=node_collection.one({'_id': ObjectId(repository_id.identifier)}))
        # =======
        # updated for aliasing
        return objects.Repository(gstudio_node=node_collection.one({'_id': ObjectId(self._get_id(repository_id, 'repository').identifier)}))

    @utilities.arguments_not_none
    def get_repositories_by_ids(self, repository_ids):
        """Gets a ``RepositoryList`` corresponding to the given ``IdList``.

        In plenary mode, the returned list contains all of the
        repositories specified in the ``Id`` list, in the order of the
        list, including duplicates, or an error results if an ``Id`` in
        the supplied list is not found or inaccessible. Otherwise,
        inaccessible ``Repositories`` may be omitted from the list and
        may present the elements in any order including returning a
        unique set.

        arg:    repository_ids (osid.id.IdList): the list of ``Ids`` to
                retrieve
        return: (osid.repository.RepositoryList) - the returned
                ``Repository list``
        raise:  NotFound - an ``Id`` was not found
        raise:  NullArgument - ``repository_ids`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        repository_list = []
        repository_ids = [ObjectId(repository_id.identifier) for repository_id in repository_ids]
        group_cur = node_collection.find({'_id': {'$in': repository_ids}})
        repository_list = [objects.Repository(gstudio_node=each_grp) for each_grp in group_cur]
        return objects.RepositoryList(repository_list)

    @utilities.arguments_not_none
    def get_repositories_by_genus_type(self, repository_genus_type):
        """Gets a ``RepositoryList`` corresponding to the given repository genus ``Type`` which does not include repositories of types derived from the specified ``Type``.

        In plenary mode, the returned list contains all known
        repositories or an error results. Otherwise, the returned list
        may contain only those repositories that are accessible through
        this session.

        arg:    repository_genus_type (osid.type.Type): a repository
                genus type
        return: (osid.repository.RepositoryList) - the returned
                ``Repository list``
        raise:  NullArgument - ``repository_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_repositories_by_parent_genus_type(self, repository_genus_type):
        """Gets a ``RepositoryList`` corresponding to the given repository genus ``Type`` and include any additional repositories with genus types derived from the specified ``Type``.

        In plenary mode, the returned list contains all known
        repositories or an error results. Otherwise, the returned list
        may contain only those repositories that are accessible through
        this session.

        arg:    repository_genus_type (osid.type.Type): a repository
                genus type
        return: (osid.repository.RepositoryList) - the returned
                ``Repository list``
        raise:  NullArgument - ``repository_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_repositories_by_record_type(self, repository_record_type):
        """Gets a ``RepositoryList`` containing the given repository record ``Type``.

        In plenary mode, the returned list contains all known
        repositories or an error results. Otherwise, the returned list
        may contain only those repositories that are accessible through
        this session.

        arg:    repository_record_type (osid.type.Type): a repository
                record type
        return: (osid.repository.RepositoryList) - the returned
                ``Repository list``
        raise:  NullArgument - ``repository_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_repositories_by_provider(self, resource_id):
        """Gets a ``RepositoryList`` from the given provider ````.

        In plenary mode, the returned list contains all known
        repositories or an error results. Otherwise, the returned list
        may contain only those repositories that are accessible through
        this session.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        return: (osid.repository.RepositoryList) - the returned
                ``Repository list``
        raise:  NullArgument - ``resource_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_repositories(self):
        """Gets all ``Repositories``.

        In plenary mode, the returned list contains all known
        repositories or an error results. Otherwise, the returned list
        may contain only those repositories that are accessible through
        this session.

        return: (osid.repository.RepositoryList) - a list of
                ``Repositories``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        repository_list = []
        group_cur = node_collection.find({'_type': 'Group'})
        repository_list = [objects.Repository(gstudio_node=each_grp) for each_grp in group_cur]
        return objects.RepositoryList(repository_list)

    repositories = property(fget=get_repositories)


class RepositoryQuerySession(abc_repository_sessions.RepositoryQuerySession, osid_sessions.OsidSession):
    """This session provides methods for searching among ``Repository`` objects.

    The search query is constructed using the ``RepositoryQuery``.

    Repositories may have a query record indicated by their respective
    record types. The query record is accessed via the
    ``RepositoryQuery``.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def can_search_repositories(self):
        """Tests if this user can perform ``Repository`` searches.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer search
        operations to unauthorized users.

        return: (boolean) - ``false`` if search methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def get_repository_query(self):
        """Gets a repository query.

        return: (osid.repository.RepositoryQuery) - the repository query
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository_query = property(fget=get_repository_query)

    @utilities.arguments_not_none
    def get_repositories_by_query(self, repository_query):
        """Gets a list of ``Repositories`` matching the given repository query.

        arg:    repository_query (osid.repository.RepositoryQuery): the
                repository query
        return: (osid.repository.RepositoryList) - the returned
                ``RepositoryList``
        raise:  NullArgument - ``repository_query`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``repository_query`` is not of this
                service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class RepositoryAdminSession(abc_repository_sessions.RepositoryAdminSession, osid_sessions.OsidSession):
    """This session creates, updates, and deletes ``Repositories``.

    The data for create and update is provided by the consumer via the
    form object. ``OsidForms`` are requested for each create or update
    and may not be reused.

    Create and update operations differ in their usage. To create a
    ``Repository,`` a ``RepositoryForm`` is requested using
    ``get_repository_form_for_create()`` specifying the desired record
    ``Types`` or none if no record ``Types`` are needed. The returned
    ``RepositoryForm`` will indicate that it is to be used with a create
    operation and can be used to examine metdata or validate data prior
    to creation. Once the ``RepositoryForm`` is submiited to a create
    operation, it cannot be reused with another create operation unless
    the first operation was unsuccessful. Each ``RepositoryForm``
    corresponds to an attempted transaction.

    For updates, ``RepositoryForms`` are requested to the ``Repository``
    ``Id`` that is to be updated using ``getRepositoryFormForUpdate()``.
    Similarly, the ``RepositoryForm`` has metadata about the data that
    can be updated and it can perform validation before submitting the
    update. The ``RepositoryForm`` can only be used once for a
    successful update and cannot be reused.

    The delete operations delete ``Repositories``. This session includes
    an ``Id`` aliasing mechanism to assign an external ``Id`` to an
    internally assigned Id.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(self, proxy=proxy, runtime=runtime)
        self._kwargs = kwargs
        self._forms = dict()

    def can_create_repositories(self):
        """Tests if this user can create ``Repositories``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known creating a
        ``Repository`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may not wish to offer
        create operations to unauthorized users.

        return: (boolean) - ``false`` if ``Repository`` creation is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def can_create_repository_with_record_types(self, repository_record_types):
        """Tests if this user can create a single ``Repository`` using the desired record types.

        While ``RepositoryManager.getRepositoryRecordTypes()`` can be
        used to examine which records are supported, this method tests
        which record(s) are required for creating a specific
        ``Repository``. Providing an empty array tests if a
        ``Repository`` can be created with no records.

        arg:    repository_record_types (osid.type.Type[]): array of
                repository record types
        return: (boolean) - ``true`` if ``Repository`` creation using
                the specified ``Types`` is supported, ``false``
                otherwise
        raise:  NullArgument - ``repository_record_types`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_repository_form_for_create(self, repository_record_types):
        """Gets the repository form for creating new repositories.

        A new form should be requested for each create transaction.

        arg:    repository_record_types (osid.type.Type[]): array of
                repository record types
        return: (osid.repository.RepositoryForm) - the repository form
        raise:  NullArgument - ``repository_record_types`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - unable to get form for requested record
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        if repository_record_types == []:
            result = objects.RepositoryForm(
                runtime=self._runtime,
                effective_agent_id=self.get_effective_agent_id(),
                proxy=self._proxy) ## Probably don't need effective agent id now that we have proxy in form.
            self._forms[result.get_id().get_identifier()] = not CREATED

            return result
        # pass
        # raise errors.Unimplemented()

    @utilities.arguments_not_none
    def create_repository(self, repository_form):
        """Creates a new ``Repository``.

        arg:    repository_form (osid.repository.RepositoryForm): the
                form for this ``Repository``
        return: (osid.repository.Repository) - the new ``Repository``
        raise:  IllegalState - ``repository_form`` already used in a
                create transaction
        raise:  InvalidArgument - one or more of the form elements is
                invalid
        raise:  NullArgument - ``repository_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``repository_form`` did not originate from
                ``get_repository_form_for_create()``
        *compliance: mandatory -- This method must be implemented.*

        """
        try:
            if self._forms[repository_form.get_id().get_identifier()] == CREATED:
                raise errors.IllegalState('repository_form already used in a create transaction')
        except KeyError:
            raise errors.Unsupported('repository_form did not originate from this session')

        if not repository_form.is_valid():
            raise errors.InvalidArgument('one or more of the form elements is invalid')

        from dlkit_gstudio.gstudio_user_proxy import GStudioRequest
        req_obj = GStudioRequest(id=1)

        self._forms[repository_form.get_id().get_identifier()] = CREATED

        group_ins = CreateGroup(req_obj)
        group_name = repository_form._gstudio_map['name']
        status_obj_tuple = group_ins.create_group(group_name,**repository_form._gstudio_map)
        if status_obj_tuple[0]:
            result = objects.Repository(
                gstudio_node=status_obj_tuple[1],
                runtime=self._runtime,
                proxy=self._proxy)

            return result
        raise errors.OperationFailed(status_obj_tuple[1])


    def can_update_repositories(self):
        """Tests if this user can update ``Repositories``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known updating a
        ``Repository`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may not wish to offer
        update operations to unauthorized users.

        return: (boolean) - ``false`` if ``Repository`` modification is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_repository_form_for_update(self, repository_id):
        """Gets the repository form for updating an existing repository.

        A new repository form should be requested for each update
        transaction.

        arg:    repository_id (osid.id.Id): the ``Id`` of the
                ``Repository``
        return: (osid.repository.RepositoryForm) - the repository form
        raise:  NotFound - ``repository_id`` is not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        if not isinstance(repository_id, ABCId):
            raise errors.InvalidArgument('the argument is not a valid OSID Id')


        self._forms[repository_form.get_id().get_identifier()] = CREATED

        group_obj = Node.get_node_by_id(ObjectId(repository_form.get_id().get_identifier()))

        cat_form = objects.RepositoryForm(gstudio_node=group_obj, runtime=self._runtime, proxy=self._proxy)
        self._forms[cat_form.get_id().get_identifier()] = not UPDATED
        return cat_form

    @utilities.arguments_not_none
    def update_repository(self, repository_form):
        """Updates an existing repository.

        arg:    repository_form (osid.repository.RepositoryForm): the
                form containing the elements to be updated
        raise:  IllegalState - ``repository_form`` already used in an
                update transaction
        raise:  InvalidArgument - the form contains an invalid value
        raise:  NullArgument - ``repository_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``repository_form`` did not originate from
                ``get_repository_form_for_update()``
        *compliance: mandatory -- This method must be implemented.*

        """
        if not isinstance(repository_form, ABCRepositoryForm):
            raise errors.InvalidArgument('argument type is not an RepositoryForm')
        if not repository_form.is_for_update():
            raise errors.InvalidArgument('the RepositoryForm is for update only, not create')
        try:
            if self._forms[repository_form.get_id().get_identifier()] == UPDATED:
                raise errors.IllegalState('repository_form already used in an update transaction')
        except KeyError:
            raise errors.Unsupported('repository_form did not originate from this session')
        if not repository_form.is_valid():
            raise errors.InvalidArgument('one or more of the form elements is invalid')
        from dlkit_gstudio.gstudio_user_proxy import GStudioRequest
        req_obj = GStudioRequest(id=1)
        group_ins = CreateGroup(req_obj)
        group_obj = Node.get_node_by_id(ObjectId(repository_form.get_id().get_identifier()))
        group_obj = group_ins.get_group_fields(group_name, **repository_form._gstudio_map)
        group_obj.save()

        if group_obj:
            result = objects.Repository(
                gstudio_node=group_obj,
                runtime=self._runtime,
                proxy=self._proxy)

            return result
        raise errors.OperationFailed("Error")


    def can_delete_repositories(self):
        """Tests if this user can delete ``Repositories``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known deleting a
        ``Repository`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may not wish to offer
        delete operations to unauthorized users.

        return: (boolean) - ``false`` if ``Repository`` deletion is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def delete_repository(self, repository_id):
        """Deletes a ``Repository``.

        arg:    repository_id (osid.id.Id): the ``Id`` of the
                ``Repository`` to remove
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_manage_repository_aliases(self):
        """Tests if this user can manage ``Id`` aliases for repositories.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known changing an alias
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer alias
        operations to an unauthorized user.

        return: (boolean) - ``false`` if ``Repository`` aliasing is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()
# ===============
# Updated for aliasing
    @utilities.arguments_not_none
    def alias_repository(self, repository_id, alias_id):
        """Adds an ``Id`` to a ``Repository`` for the purpose of creating compatibility.

        The primary ``Id`` of the ``Repository`` is determined by the
        provider. The new ``Id`` is an alias to the primary ``Id``. If
        the alias is a pointer to another repository, it is reassigned
        to the given repository ``Id``.

        arg:    repository_id (osid.id.Id): the ``Id`` of a
                ``Repository``
        arg:    alias_id (osid.id.Id): the alias ``Id``
        raise:  AlreadyExists - ``alias_id`` is in use as a primary
                ``Id``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``alias_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        #raise errors.Unimplemented()
        self._alias_id(primary_id=repository_id, equivalent_id=alias_id)
# ===============


class RepositoryHierarchySession(abc_repository_sessions.RepositoryHierarchySession, osid_sessions.OsidSession):
    """This session defines methods for traversing a hierarchy of ``Repository`` objects.

    Each node in the hierarchy is a unique ``Repository``. The hierarchy
    may be traversed recursively to establish the tree structure through
    ``get_parents()`` and ``getChildren()``. To relate these ``Ids`` to
    another OSID, ``get_ancestors()`` and ``get_descendants()`` can be
    used for retrievals that can be used for bulk lookups in other
    OSIDs. Any ``Repository`` available in the Repository OSID is known
    to this hierarchy but does not appear in the hierarchy traversal
    until added as a root node or a child of another node.

    A user may not be authorized to traverse the entire hierarchy. Parts
    of the hierarchy may be made invisible through omission from the
    returns of ``get_parents()`` or ``get_children()`` in lieu of a
    ``PermissionDenied`` error that may disrupt the traversal through
    authorized pathways.

    This session defines views that offer differing behaviors when
    retrieving multiple objects.

      * comparative view: repository elements may be silently omitted or
        re-ordered
      * plenary view: provides a complete set or is an error condition


    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_catalog(self, proxy, runtime)
        self._forms = dict()
        self._kwargs = kwargs
        hierarchy_mgr = self._get_provider_manager('HIERARCHY')
        self._hierarchy_session = hierarchy_mgr.get_hierarchy_traversal_session_for_hierarchy(
            Id(authority='REPOSITORY',
               namespace='CATALOG',
               identifier='REPOSITORY'),
             proxy=self._proxy
        )


    def get_repository_hierarchy_id(self):
        """Gets the hierarchy ``Id`` associated with this session.

        return: (osid.id.Id) - the hierarchy ``Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_bin_hierarchy_id
        return self._hierarchy_session.get_hierarchy_id()

    repository_hierarchy_id = property(fget=get_repository_hierarchy_id)

    def get_repository_hierarchy(self):
        """Gets the hierarchy associated with this session.

        return: (osid.hierarchy.Hierarchy) - the hierarchy associated
                with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_bin_hierarchy
        return self._hierarchy_session.get_hierarchy()

    repository_hierarchy = property(fget=get_repository_hierarchy)

    def can_access_repository_hierarchy(self):
        """Tests if this user can perform hierarchy queries.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer lookup
        operations.

        return: (boolean) - ``false`` if hierarchy traversal methods are
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.can_access_bin_hierarchy
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_comparative_repository_view(self):
        """The returns from the repository methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_plenary_repository_view(self):
        """A complete view of the ``Repository`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def get_root_repository_ids(self):
        """Gets the root repository ``Ids`` in this hierarchy.

        return: (osid.id.IdList) - the root repository ``Ids``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_root_bin_ids
        return self._hierarchy_session.get_roots()

    root_repository_ids = property(fget=get_root_repository_ids)

    def get_root_repositories(self):
        """Gets the root repositories in the repository hierarchy.

        A node with no parents is an orphan. While all repository
        ``Ids`` are known to the hierarchy, an orphan does not appear in
        the hierarchy unless explicitly added as a root node or child of
        another node.

        return: (osid.repository.RepositoryList) - the root repositories
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method is must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_root_bins
        return RepositoryLookupSession(
            self._proxy,
            self._runtime).get_repositories_by_ids(list(self.get_root_repository_ids()))

    root_repositories = property(fget=get_root_repositories)

    @utilities.arguments_not_none
    def has_parent_repositories(self, repository_id):
        """Tests if the ``Repository`` has any parents.

        arg:    repository_id (osid.id.Id): a repository ``Id``
        return: (boolean) - ``true`` if the repository has parents,
                ``false`` otherwise
        raise:  NotFound - ``repository_id`` is not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.has_parent_bins
        return self._hierarchy_session.has_parents(id_=repository_id)

    @utilities.arguments_not_none
    def is_parent_of_repository(self, id_, repository_id):
        """Tests if an ``Id`` is a direct parent of a repository.

        arg:    id (osid.id.Id): an ``Id``
        arg:    repository_id (osid.id.Id): the ``Id`` of a repository
        return: (boolean) - ``true`` if this ``id`` is a parent of
                ``repository_id,``  ``false`` otherwise
        raise:  NotFound - ``repository_id`` is not found
        raise:  NullArgument - ``id`` or ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: If ``id`` not found return ``false``.

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.is_parent_of_bin
        return self._hierarchy_session.is_parent(id_=repository_id, parent_id=id_)

    @utilities.arguments_not_none
    def get_parent_repository_ids(self, repository_id):
        """Gets the parent ``Ids`` of the given repository.

        arg:    repository_id (osid.id.Id): a repository ``Id``
        return: (osid.id.IdList) - the parent ``Ids`` of the repository
        raise:  NotFound - ``repository_id`` is not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_parent_bin_ids
        return self._hierarchy_session.get_parents(id_=repository_id)

    @utilities.arguments_not_none
    def get_parent_repositories(self, repository_id):
        """Gets the parents of the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` to query
        return: (osid.repository.RepositoryList) - the parents of the
                repository
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_parent_bins
        return RepositoryLookupSession(
            self._proxy,
            self._runtime).get_repositories_by_ids(
                list(self.get_parent_repository_ids(repository_id)))

    @utilities.arguments_not_none
    def is_ancestor_of_repository(self, id_, repository_id):
        """Tests if an ``Id`` is an ancestor of a repository.

        arg:    id (osid.id.Id): an ``Id``
        arg:    repository_id (osid.id.Id): the Id of a repository
        return: (boolean) - ``true`` if this ``id`` is an ancestor of
                ``repository_id,``  ``false`` otherwise
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: If ``id`` not found return ``false``.

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.is_ancestor_of_bin
        return self._hierarchy_session.is_ancestor(id_=id_, ancestor_id=repository_id)

    @utilities.arguments_not_none
    def has_child_repositories(self, repository_id):
        """Tests if a repository has any children.

        arg:    repository_id (osid.id.Id): a repository ``Id``
        return: (boolean) - ``true`` if the ``repository_id`` has
                children, ``false`` otherwise
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.has_child_bins
        return self._hierarchy_session.has_children(id_=repository_id)

    @utilities.arguments_not_none
    def is_child_of_repository(self, id_, repository_id):
        """Tests if a node is a direct child of another.

        arg:    id (osid.id.Id): an ``Id``
        arg:    repository_id (osid.id.Id): the ``Id`` of a repository
        return: (boolean) - ``true`` if the ``id`` is a child of
                ``repository_id,``  ``false`` otherwise
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: If ``id`` not found return ``false``.

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.is_child_of_bin
        return self._hierarchy_session.is_child(id_=repository_id, child_id=id_)

    @utilities.arguments_not_none
    def get_child_repository_ids(self, repository_id):
        """Gets the ``Ids`` of the children of the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` to query
        return: (osid.id.IdList) - the children of the repository
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_child_bin_ids
        return self._hierarchy_session.get_children(id_=repository_id)

    @utilities.arguments_not_none
    def get_child_repositories(self, repository_id):
        """Gets the children of the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` to query
        return: (osid.repository.RepositoryList) - the children of the
                repository
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_child_bins
        return RepositoryLookupSession(
            self._proxy,
            self._runtime).get_repositories_by_ids(
                list(self.get_child_repository_ids(repository_id)))

    @utilities.arguments_not_none
    def is_descendant_of_repository(self, id_, repository_id):
        """Tests if an ``Id`` is a descendant of a repository.

        arg:    id (osid.id.Id): an ``Id``
        arg:    repository_id (osid.id.Id): the ``Id`` of a repository
        return: (boolean) - ``true`` if the ``id`` is a descendant of
                the ``repository_id,`` ``false`` otherwise
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: If ``id`` is not found return ``false``.

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.is_descendant_of_bin
        return self._hierarchy_session.is_descendant(id_=id_, descendant_id=repository_id)

    @utilities.arguments_not_none
    def get_repository_node_ids(self, repository_id, ancestor_levels, descendant_levels, include_siblings):
        """Gets a portion of the hierarchy for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` to query
        arg:    ancestor_levels (cardinal): the maximum number of
                ancestor levels to include. A value of 0 returns no
                parents in the node.
        arg:    descendant_levels (cardinal): the maximum number of
                descendant levels to include. A value of 0 returns no
                children in the node.
        arg:    include_siblings (boolean): ``true`` to include the
                siblings of the given node, ``false`` to omit the
                siblings
        return: (osid.hierarchy.Node) - the specified repository node
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_bin_node_ids
        return self._hierarchy_session.get_nodes(
            id_=repository_id,
            ancestor_levels=ancestor_levels,
            descendant_levels=descendant_levels,
            include_siblings=include_siblings)

    @utilities.arguments_not_none
    def get_repository_nodes(self, repository_id, ancestor_levels, descendant_levels, include_siblings):
        """Gets a portion of the hierarchy for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` to query
        arg:    ancestor_levels (cardinal): the maximum number of
                ancestor levels to include. A value of 0 returns no
                parents in the node.
        arg:    descendant_levels (cardinal): the maximum number of
                descendant levels to include. A value of 0 returns no
                children in the node.
        arg:    include_siblings (boolean): ``true`` to include the
                siblings of the given node, ``false`` to omit the
                siblings
        return: (osid.repository.RepositoryNode) - the specified
                repository node
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_bin_nodes
        return objects.RepositoryNode(self.get_repository_node_ids(
            repository_id=repository_id,
            ancestor_levels=ancestor_levels,
            descendant_levels=descendant_levels,
            include_siblings=include_siblings)._my_map, runtime=self._runtime, proxy=self._proxy)


class RepositoryHierarchyDesignSession(abc_repository_sessions.RepositoryHierarchyDesignSession, osid_sessions.OsidSession):
    """This session defines methods for managing a hierarchy of ``Repository`` objects.

    Each node in the hierarchy is a unique ``Repository``.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_repository_hierarchy_id(self):
        """Gets the hierarchy ``Id`` associated with this session.

        return: (osid.id.Id) - the hierarchy ``Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_bin_hierarchy_id
        return self._hierarchy_session.get_hierarchy_id()

    repository_hierarchy_id = property(fget=get_repository_hierarchy_id)

    def get_repository_hierarchy(self):
        """Gets the hierarchy associated with this session.

        return: (osid.hierarchy.Hierarchy) - the hierarchy associated
                with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_bin_hierarchy
        return self._hierarchy_session.get_hierarchy()

    repository_hierarchy = property(fget=get_repository_hierarchy)

    def can_modify_repository_hierarchy(self):
        """Tests if this user can change the hierarchy.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known performing any update
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer these
        operations to an unauthorized user.

        return: (boolean) - ``false`` if changing this hierarchy is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def add_root_repository(self, repository_id):
        """Adds a root repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of a repository
        raise:  AlreadyExists - ``repository_id`` is already in
                hierarchy
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchyDesignSession.add_root_bin_template
        return self._hierarchy_session.add_root(id_=repository_id)

    @utilities.arguments_not_none
    def remove_root_repository(self, repository_id):
        """Removes a root repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of a repository
        raise:  NotFound - ``repository_id`` not a root
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchyDesignSession.remove_root_bin_template
        return self._hierarchy_session.remove_root(id_=repository_id)

    @utilities.arguments_not_none
    def add_child_repository(self, repository_id, child_id):
        """Adds a child to a repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of a repository
        arg:    child_id (osid.id.Id): the ``Id`` of the new child
        raise:  AlreadyExists - ``repository_id`` is already a parent of
                ``child_id``
        raise:  NotFound - ``repository_id`` or ``child_id`` not found
        raise:  NullArgument - ``repository_id`` or ``child_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchyDesignSession.add_child_bin_template
        return self._hierarchy_session.add_child(id_=repository_id, child_id=child_id)

    @utilities.arguments_not_none
    def remove_child_repository(self, repository_id, child_id):
        """Removes a child from a repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of a repository
        arg:    child_id (osid.id.Id): the ``Id`` of the new child
        raise:  NotFound - ``repository_id`` not a parent of
                ``child_id``
        raise:  NullArgument - ``repository_id`` or ``child_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchyDesignSession.remove_child_bin_template
        return self._hierarchy_session.remove_child(id_=repository_id, child_id=child_id)

    @utilities.arguments_not_none
    def remove_child_repositories(self, repository_id):
        """Removes all children from a repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of a repository
        raise:  NotFound - ``repository_id`` not in hierarchy
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchyDesignSession.remove_child_bin_template
        return self._hierarchy_session.remove_children(id_=repository_id)


