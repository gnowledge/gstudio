"""GStudio implementations of type primitives."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.type import primitives as abc_type_primitives
from ..osid import markers as osid_markers




class Type(abc_type_primitives.Type, osid_markers.OsidPrimitive):
    """The Type is a form of identifier that is primarily used to identify interface specifications.

    The ``Type`` differs from ``Id`` in that it offers display
    information and ``Types`` may be arranged in hierarchies to indicate
    an extended interface. Semantically, an ``Id`` identifies any OSID
    object while the ``Type`` identifies a specification.

    The components of the Type that make up its identification are:

      * identifier: a unique key or guid
      * namespace: the namespace of the identifier
      * authority: the isuer of the identifier


    Persisting a type reference means to persist the above
    identification elements. In addition to these identifier components,
    A ``Type`` mai also provide some additional metadata such as a name,
    description and domain.

    """

    def __init__(self, type_map=None,
                       identifier=None,
                       authority=None,
                       namespace=None,
                       display_name=None,
                       display_label=None,
                       description=None,
                       domain=None):
        if type_map is not None:
            self._my_map = type_map
        elif (authority is not None and namespace is not None and identifier is not None and
            display_name is not None and description is not None and domain is not None):
            self._my_map = {}
            self._my_map['authority'] = authority
            self._my_map['namespace'] = namespace
            self._my_map['identifier'] = identifier
            self._my_map['displayName'] = self.display_text_map(display_name)
            self._my_map['displayLabel'] = self.display_text_map(display_label)
            self._my_map['description'] = self.display_text_map(description)
            self._my_map['domain'] = self.display_text_map(domain)
        else:
            raise errors.NullArgument()
    
    def display_text_map(self, string):
        from .profile import LANGUAGETYPE, SCRIPTTYPE, FORMATTYPE
        from ..primitives import Id
        language_type_str = str(Id(**LANGUAGETYPE))
        script_type_str = str(Id(**SCRIPTTYPE))
        format_type_str = str(Id(**FORMATTYPE))
        return {'text': string,
                'languageTypeId': language_type_str,
                'scriptTypeId': script_type_str,
                'formatTypeId': format_type_str}

    def get_display_name(self):
        """Gets the full display name of this ``Type``.

        return: (osid.locale.DisplayText) - the display name of this
                ``Type``
        *compliance: mandatory -- This method must be implemented.*

        """
        from ..primitives import DisplayText
        return DisplayText(self._my_map['displayName'])

    display_name = property(fget=get_display_name)

    def get_display_label(self):
        """Gets the shorter display label for this ``Type``.

        Where a display name of a ``Type`` might be ``"`` Critical
        Logging Priority Type", the display label could be "critical".

        return: (osid.locale.DisplayText) - the display label for this
                ``Type``
        *compliance: mandatory -- This method must be implemented.*

        """
        from ..primitives import DisplayText
        return DisplayText(self._my_map['displayLabel'])

    display_label = property(fget=get_display_label)

    def get_description(self):
        """Gets a description of this ``Type``.

        return: (osid.locale.DisplayText) - the description of this
                ``Type``
        *compliance: mandatory -- This method must be implemented.*

        """
        from ..primitives import DisplayText
        return DisplayText(self._my_map['description'])

    description = property(fget=get_description)

    def get_domain(self):
        """Gets the domain.

        The domain can provide an information label about ths
        application space of this Type.

        return: (osid.locale.DisplayText) - the domain of this ``Type``
        *compliance: mandatory -- This method must be implemented.*

        """
        from ..primitives import DisplayText
        return DisplayText(self._my_map['domain'])

    domain = property(fget=get_domain)

    def get_authority(self):
        """Gets the authority of this ``Type``.

        The authority is a string used to ensure the uniqueness of this
        ``Type`` when using a non- federated identifier space.
        Generally, it is a domain name identifying the party responsible
        for this ``Type``. This method is used to compare one ``Type``
        to another.

        return: (string) - the authority of this ``Type``
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._my_map['authority']

    authority = property(fget=get_authority)

    def get_identifier_namespace(self):
        """Gets the namespace of the identifier.

        This method is used to compare one ``Type`` to another.

        return: (string) - the authority of this ``Type``
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._my_map['namespace']

    identifier_namespace = property(fget=get_identifier_namespace)

    namespace = property(fget=get_identifier_namespace)

    def get_identifier(self):
        """Gets the identifier of this ``Type``.

        This method is used to compare one ``Type`` to another.

        return: (string) - the identifier of this ``Type``
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._my_map['identifier']

    identifier = property(fget=get_identifier)


