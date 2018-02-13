"""GStudio implementations of id primitives."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.id import primitives as abc_id_primitives
from ..osid import markers as osid_markers




class Id(abc_id_primitives.Id, osid_markers.OsidPrimitive):
    """``Id`` represents an identifier object.

    Ids are designated by the following elements:

      * ``identifier:`` a unique key or guid
      * ``namespace:`` the namespace of the identifier
      * ``authority:`` the issuer of the identifier


    Two Ids are equal if their namespace, identifier and authority
    strings are equal. Only the identifier is case-sensitive. Persisting
    an ``Id`` means persisting the above components.

    """

    def __init__(self, authority, namespace, identifier):
        self._authority = authority
        self._namespace = namespace
        self._identifier = identifier

    def get_authority(self):
        """Gets the authority of this ``Id``.

        The authority is a string used to ensure the uniqueness of this
        ``Id`` when using a non- federated identifier space. Generally,
        it is a service name identifying the provider of this ``Id``.
        This method is used to compare one ``Id`` to another.

        return: (string) - the authority of this ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._authority

    authority = property(fget=get_authority)

    def get_identifier_namespace(self):
        """Gets the namespace of the identifier.

        The namespace reflects the domain in which the identifier is
        unique. When using a global identifier schema, the namespace may
        indicate the name of the scheme. When using a local
        identification scheme, the namespace may be more specific, such
        as the name of a database or file in which the identifiers
        exist. Federating adapters may use a custom namespace to include
        information for routing. This method is used to compare one
        ``Id`` to another.

        return: (string) - the authority of this ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._namespace

    identifier_namespace = property(fget=get_identifier_namespace)

    namespace = property(fget=get_identifier_namespace)

    def get_identifier(self):
        """Gets the identifier of this ``Id``.

        This method is used to compare one ``Id`` to another.

        return: (string) - the identifier of this ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._identifier

    identifier = property(fget=get_identifier)


