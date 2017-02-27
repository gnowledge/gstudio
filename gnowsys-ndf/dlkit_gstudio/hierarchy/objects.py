"""GStudio implementations of hierarchy objects."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification

#from ..osid.objects import OsidForm
#from ..osid.objects import OsidObjectForm
#from ..utilities import get_registry


from . import default_mdata
from .. import utilities
from ...abstract_osid.hierarchy import objects as abc_hierarchy_objects
from ..osid import objects as osid_objects
from ..primitives import Id
from dlkit.abstract_osid.osid import errors
from dlkit.primordium.id.primitives import Id




class Hierarchy(abc_hierarchy_objects.Hierarchy, osid_objects.OsidCatalog):
    """A ``Hierarchy`` represents an authenticatable identity.

    Like all OSID objects, a ``Hierarchy`` is identified by its Id and
    any persisted references should use the Id.

    """

    _namespace = 'hierarchy.Hierarchy'

    def __init__(self, **kwargs):
        # self._record_type_data_sets = get_registry('HIERARCHY_RECORD_TYPES', runtime)
        osid_objects.OsidCatalog.__init__(self, object_name='HIERARCHY', **kwargs)

    @utilities.arguments_not_none
    def get_hierarchy_record(self, hierarchy_record_type):
        """Gets the hierarchy record corresponding to the given ``Hierarchy`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``hierarchy_record_type`` may be the
        ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(hierarchy_record_type)`` is ``true`` .

        arg:    hierarchy_record_type (osid.type.Type): the type of the
                record to retrieve
        return: (osid.hierarchy.records.HierarchyRecord) - the hierarchy
                record
        raise:  NullArgument - ``hierarchy_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(hierarchyrecord_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class HierarchyForm(abc_hierarchy_objects.HierarchyForm, osid_objects.OsidCatalogForm):
    """This is the form for creating and updating ``Hierarchy`` objects.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``HierarchyAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'hierarchy.Hierarchy'

    def __init__(self, **kwargs):
        osid_objects.OsidCatalogForm.__init__(self, object_name='HIERARCHY', **kwargs)
        self._mdata = default_mdata.get_hierarchy_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    @utilities.arguments_not_none
    def get_hierarchy_form_record(self, hierarchy_record_type):
        """Gets the ``HierarchyFormRecord`` corresponding to the given hierarchy record ``Type``.

        arg:    hierarchy_record_type (osid.type.Type): the hierarchy
                record type
        return: (osid.hierarchy.records.HierarchyFormRecord) - the
                hierarchy form record
        raise:  NullArgument - ``hierarchy_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(hierarchy_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class HierarchyList(abc_hierarchy_objects.HierarchyList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``HierarchyList`` provides a means for accessing ``Id`` elements sequentially either one at a time or many at a time.

    Examples: while (hl.hasNext()) { Hierarchy hierarchy =
    hl.getNextHierarchy(); }

    or
      while (hl.hasNext()) {
           Hierarchy[] hierarchies = hl.getNextHierarchies(hl.available());
      }



    """

    def get_next_hierarchy(self):
        """Gets the next ``Hierarchy`` in this list.

        return: (osid.hierarchy.Hierarchy) - the next ``Hierarchy`` in
                this list. The ``has_next()`` method should be used to
                test that a next ``Hierarchy`` is available before
                calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Hierarchy)

    next_hierarchy = property(fget=get_next_hierarchy)

    @utilities.arguments_not_none
    def get_next_hierarchies(self, n):
        """Gets the next set of ``Hierarchy`` objects in this list.

        The specified amount must be less than or equal to the return
        from ``available()``.

        arg:    n (cardinal): the number of ``Hierarchy`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.hierarchy.Hierarchy) - an array of ``Hierarchy``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class Node(abc_hierarchy_objects.Node, osid_objects.OsidNode):
    """This interface is a container for a partial hierarchy retrieval.

    The number of hierarchy levels traversable through this interface
    depend on the number of levels requested in the hierarchy traversal
    session.

    """

    def get_parents(self):
        """Gets the parents of this node.

        return: (osid.hierarchy.NodeList) - the parents of this node
        *compliance: mandatory -- This method must be implemented.*

        """
        return NodeList(self._my_map['parentNodes'])

    parents = property(fget=get_parents)

    def get_children(self):
        """Gets the children of this node.

        return: (osid.hierarchy.NodeList) - the children of this node
        *compliance: mandatory -- This method must be implemented.*

        """
        return NodeList(self._my_map['childNodes'])

    children = property(fget=get_children)


class NodeList(abc_hierarchy_objects.NodeList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``NodeList`` provides a means for accessing ``Id`` elements sequentially either one at a time or many at a time.

    Examples: while (nl.hasNext()) { Node node = nl.getNextNode(); }

    or
      while (nl.hasNext()) {
           Node[] nodes = nl.getNextNodes(nl.available());
      }



    """

    def get_next_node(self):
        """Gets the next ``Node`` in this list.

        return: (osid.hierarchy.Node) - the next ``Node`` in this list.
                The ``has_next()`` method should be used to test that a
                next ``Node`` is available before calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Node)

    next_node = property(fget=get_next_node)

    @utilities.arguments_not_none
    def get_next_nodes(self, n):
        """Gets the next set of ``Node`` objects in this list.

        The specified amount must be less than or equal to the return
        from ``available()``.

        arg:    n (cardinal): the number of ``Node`` elements requested
                which must be less than or equal to ``available()``
        return: (osid.hierarchy.Node) - an array of ``Node``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


