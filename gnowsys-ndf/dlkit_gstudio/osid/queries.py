"""GStudio implementations of osid queries."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from dlkit.abstract_osid.osid import queries as abc_osid_queries
from ..osid import markers as osid_markers




class OsidQuery(abc_osid_queries.OsidQuery, osid_markers.Suppliable):
    """The ``OsidQuery`` is used to assemble search queries.

    An ``OsidQuery`` is available from an ``OsidQuerySession`` and
    defines methods to match objects. Once the desired parameters are
    set, the ``OsidQuery`` is given to the designated search method. The
    same ``OsidQuery`` returned from the session must be used in the
    search as the provider may utilize implementation-specific data
    wiithin the object.

    If multiple data elements are set in this interface, the results
    matching all the given data (eg: AND) are returned.

    Any match method inside an ``OsidQuery`` may be invoked multiple
    times. In the case of a match method, each invocation adds an
    element to an ``OR`` expression. Any of these terms may also be
    negated through the ``match`` flag.
      OsidQuery { OsidQuery.matchDisplayName AND (OsidQuery.matchDescription OR OsidQuery.matchDescription)}



    ``OsidObjects`` allow for the definition of an additonal records and
    the ``OsidQuery`` parallels this mechanism. An interface type of an
    ``OsidObject`` record must also define the corresponding
    ``OsidQuery`` record which is available through query interfaces.
    Multiple requests of these typed interfaces may return the same
    underlying object and thus it is only useful to request once.

    An ``OsidQuery`` may be used to query for set or unset values using
    the "match any" methods. A field that has not bee explicitly
    assigned may default to a value. If multiple language translations
    exist and the query session is placed in a non-default locale,
    fields that have not been explicitly assigned in the non-default
    locale are considered unset even if the values from the default
    locale appear in the objects.

    """

    def get_string_match_types(self):
        """Gets the string matching types supported.

        A string match type specifies the syntax of the string query,
        such as matching a word or including a wildcard or regular
        expression.

        return: (osid.type.TypeList) - a list containing the supported
                string match types
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    string_match_types = property(fget=get_string_match_types)

    @utilities.arguments_not_none
    def supports_string_match_type(self, string_match_type):
        """Tests if the given string matching type is supported.

        arg:    string_match_type (osid.type.Type): a ``Type``
                indicating a string match type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``string_match_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_keyword(self, keyword, string_match_type, match):
        """Adds a keyword to match.

        Multiple keywords can be added to perform a boolean ``OR`` among
        them. A keyword may be applied to any of the elements defined in
        this object such as the display name, description or any method
        defined in an interface implemented by this object.

        arg:    keyword (string): keyword to match
        arg:    string_match_type (osid.type.Type): the string match
                type
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``keyword`` is not of
                ``string_match_type``
        raise:  NullArgument - ``keyword`` or ``string_match_type`` is
                ``null``
        raise:  Unsupported -
                ``supports_string_match_type(string_match_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_keyword_terms(self):
        """Clears all keyword terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    keyword_terms = property(fdel=clear_keyword_terms)

    @utilities.arguments_not_none
    def match_any(self, match):
        """Matches any object.

        arg:    match (boolean): ``true`` to match any object ``,``
                ``false`` to match no objects
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_any_terms(self):
        """Clears the match any terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    any_terms = property(fdel=clear_any_terms)


class OsidIdentifiableQuery(abc_osid_queries.OsidIdentifiableQuery, OsidQuery):
    """The ``OsidIdentiableQuery`` is used to assemble search queries for ``Identifiable`` objects.

    An ``OsidIdentifiableQuery`` is available from an
    ``OsidQuerySession`` and defines methods to match objects. Once the
    desired parameters are set, the ``OsidIdentifiableQuery`` is given
    to the designated search method. The same ``OsidIdentifiableQuery``
    returned from the session must be used in the search as the provider
    may utilize implementation-specific data wiithin the object.

    If multiple data elements are set in this interface, the results
    matching all the given data (eg: AND) are returned.

    """

    @utilities.arguments_not_none
    def match_id(self, id_, match):
        """Adds an ``Id`` to match.

        Multiple ``Ids`` can be added to perform a boolean ``OR`` among
        them.

        arg:    id (osid.id.Id): ``Id`` to match
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_id_terms(self):
        """Clears all ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    id_terms = property(fdel=clear_id_terms)


class OsidExtensibleQuery(abc_osid_queries.OsidExtensibleQuery, OsidQuery, osid_markers.Extensible):
    """The ``OsidExtensibleQuery`` is used to assemble search queries for ``Extensible`` objects.

    An ``OsidExtensibleQuery`` is available from an ``OsidQuerySession``
    and defines methods to match objects. Once the desired parameters
    are set, the ``OsidExtensibleQuery`` is given to the designated
    search method. The same ``OsidExtensibleQuery`` returned from the
    session must be used in the search as the provider may utilize
    implementation-specific data wiithin the object.

    If multiple data elements are set in this interface, the results
    matching all the given data (eg: AND) are returned.

    """

    @utilities.arguments_not_none
    def match_record_type(self, record_type, match):
        """Sets a ``Type`` for querying objects having records implementing a given record type.

        arg:    record_type (osid.type.Type): a record type
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_record(self, match):
        """Matches an object that has any record.

        arg:    match (boolean): ``true`` to match any record, ``false``
                to match objects with no records
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_record_terms(self):
        """Clears all record ``Type`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    record_terms = property(fdel=clear_record_terms)


class OsidBrowsableQuery(abc_osid_queries.OsidBrowsableQuery, OsidQuery):
    """The ``OsidBrowsableQuery`` is used to assemble search queries for ``Browsable`` objects.

    An ``OsidBrowsableQuery`` is available from an ``OsidQuerySession``
    and defines methods to match objects. Once the desired parameters
    are set, the ``OsidBrowsableQuery`` is given to the designated
    search method. The same ``OsidBrowsableQuery`` returned from the
    session must be used in the search as the provider may utilize
    implementation-specific data wiithin the object.

    If multiple data elements are set in this interface, the results
    matching all the given data (eg: AND) are returned.

    """




class OsidTemporalQuery(abc_osid_queries.OsidTemporalQuery, OsidQuery):
    """This is the query interface for searching temporal objects.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """

    @utilities.arguments_not_none
    def match_effective(self, match):
        """Match effective objects where the current date falls within the start and end dates inclusive.

        arg:    match (boolean): ``true`` to match any effective,
                ``false`` to match ineffective
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_effective_terms(self):
        """Clears the effective query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    effective_terms = property(fdel=clear_effective_terms)

    @utilities.arguments_not_none
    def match_start_date(self, start, end, match):
        """Matches temporals whose start date falls in between the given dates inclusive.

        arg:    start (osid.calendaring.DateTime): start of date range
        arg:    end (osid.calendaring.DateTime): end of date range
        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        raise:  InvalidArgument - ``start`` is less than ``end``
        raise:  NullArgument - ``start`` or ``end`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_start_date(self, match):
        """Matches temporals with any start date set.

        arg:    match (boolean): ``true`` to match any start date,
                ``false`` to match no start date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_start_date_terms(self):
        """Clears the start date query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    start_date_terms = property(fdel=clear_start_date_terms)

    @utilities.arguments_not_none
    def match_end_date(self, start, end, match):
        """Matches temporals whose effective end date falls in between the given dates inclusive.

        arg:    start (osid.calendaring.DateTime): start of date range
        arg:    end (osid.calendaring.DateTime): end of date range
        arg:    match (boolean): ``true`` if a positive match, ``false``
                for negative match
        raise:  InvalidArgument - ``start`` is less than ``end``
        raise:  NullArgument - ``start`` or ``end`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_end_date(self, match):
        """Matches temporals with any end date set.

        arg:    match (boolean): ``true`` to match any end date,
                ``false`` to match no start date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_end_date_terms(self):
        """Clears the end date query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    end_date_terms = property(fdel=clear_end_date_terms)

    @utilities.arguments_not_none
    def match_date(self, from_, to, match):
        """Matches temporals where the given date range falls entirely between the start and end dates inclusive.

        arg:    from (osid.calendaring.DateTime): start date
        arg:    to (osid.calendaring.DateTime): end date
        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        raise:  InvalidArgument - ``from`` is less than ``to``
        raise:  NullArgument - ``from`` or ``to`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_date_terms(self):
        """Clears the date query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    date_terms = property(fdel=clear_date_terms)


class OsidSubjugateableQuery(abc_osid_queries.OsidSubjugateableQuery, OsidQuery):
    """The ``OsidSubjugateableQuery`` is used to assemble search queries for dependent objects."""




class OsidAggregateableQuery(abc_osid_queries.OsidAggregateableQuery, OsidQuery):
    """The ``OsidAggregateableQuery`` is used to assemble search queries for assemblages."""




class OsidContainableQuery(abc_osid_queries.OsidContainableQuery, OsidQuery):
    """This is the query interface for searching containers.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """

    @utilities.arguments_not_none
    def match_sequestered(self, match):
        """Match containables that are sequestered.

        arg:    match (boolean): ``true`` to match any sequestered
                containables, ``false`` to match non- sequestered
                containables
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_sequestered_terms(self):
        """Clears the sequestered query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    sequestered_terms = property(fdel=clear_sequestered_terms)


class OsidSourceableQuery(abc_osid_queries.OsidSourceableQuery, OsidQuery):
    """The ``OsidSourceableQuery`` is used to assemble search queries for sourceables."""

    @utilities.arguments_not_none
    def match_provider_id(self, resource_id, match):
        """Match the ``Id`` of the provider resource.

        arg:    resource_id (osid.id.Id): ``Id`` to match
        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``resource_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_provider_id_terms(self):
        """Clears all provider ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    provider_id_terms = property(fdel=clear_provider_id_terms)

    def supports_provider_query(self):
        """Tests if a ``ResourceQuery`` for the provider is available.

        return: (boolean) - ``true`` if a resource query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_provider_query(self, match):
        """Gets the query for the provider.

        Each retrieval performs a boolean ``OR``.

        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        return: (osid.resource.ResourceQuery) - the provider query
        raise:  Unimplemented - ``supports_provider_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_provider_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_provider(self, match):
        """Match sourceables with a provider value.

        arg:    match (boolean): ``true`` to match sourceables with any
                provider, ``false`` to match sourceables with no
                providers
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_provider_terms(self):
        """Clears all provider terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    provider_terms = property(fdel=clear_provider_terms)

    @utilities.arguments_not_none
    def match_branding_id(self, asset_id, match):
        """Match the ``Id`` of an asset used for branding.

        arg:    asset_id (osid.id.Id): ``Id`` to match
        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``asset_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_branding_id_terms(self):
        """Clears all asset ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    branding_id_terms = property(fdel=clear_branding_id_terms)

    def supports_branding_query(self):
        """Tests if an ``AssetQuery`` for the branding is available.

        return: (boolean) - ``true`` if a asset query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_branding_query(self, match):
        """Gets the query for an asset.

        Each retrieval performs a boolean ``OR``.

        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        return: (osid.repository.AssetQuery) - the asset query
        raise:  Unimplemented - ``supports_branding_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_branding_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_branding(self, match):
        """Match sourceables with any branding.

        arg:    match (boolean): ``true`` to match any asset, ``false``
                to match no assets
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_branding_terms(self):
        """Clears all branding terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    branding_terms = property(fdel=clear_branding_terms)

    @utilities.arguments_not_none
    def match_license(self, license_, string_match_type, match):
        """Adds a license to match.

        Multiple license matches can be added to perform a boolean
        ``OR`` among them.

        arg:    license (string): a string to match
        arg:    string_match_type (osid.type.Type): the string match
                type
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``license`` is not of
                ``string_match_type``
        raise:  NullArgument - ``license`` or ``string_match_type`` is
                ``null``
        raise:  Unsupported -
                ``supports_string_match_type(string_match_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_license(self, match):
        """Matches any object with a license.

        arg:    match (boolean): ``true`` to match any license,
                ``false`` to match objects with no license
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_license_terms(self):
        """Clears all license terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    license_terms = property(fdel=clear_license_terms)


class OsidFederateableQuery(abc_osid_queries.OsidFederateableQuery, OsidQuery):
    """The ``OsidFederateableQuery`` is used to assemble search queries for federated objects."""




class OsidOperableQuery(abc_osid_queries.OsidOperableQuery, OsidQuery):
    """This is the query interface for searching operables.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """

    @utilities.arguments_not_none
    def match_active(self, match):
        """Matches active.

        arg:    match (boolean): ``true`` to match active, ``false`` to
                match inactive
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_active_terms(self):
        """Clears the active query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    active_terms = property(fdel=clear_active_terms)

    @utilities.arguments_not_none
    def match_enabled(self, match):
        """Matches administratively enabled.

        arg:    match (boolean): ``true`` to match administratively
                enabled, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_enabled_terms(self):
        """Clears the administratively enabled query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    enabled_terms = property(fdel=clear_enabled_terms)

    @utilities.arguments_not_none
    def match_disabled(self, match):
        """Matches administratively disabled.

        arg:    match (boolean): ``true`` to match administratively
                disabled, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_disabled_terms(self):
        """Clears the administratively disabled query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    disabled_terms = property(fdel=clear_disabled_terms)

    @utilities.arguments_not_none
    def match_operational(self, match):
        """Matches operational operables.

        arg:    match (boolean): ``true`` to match operational,
                ``false`` to match not operational
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_operational_terms(self):
        """Clears the operational query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    operational_terms = property(fdel=clear_operational_terms)


class OsidObjectQuery(abc_osid_queries.OsidObjectQuery, OsidIdentifiableQuery, OsidExtensibleQuery, OsidBrowsableQuery):
    """The ``OsidObjectQuery`` is used to assemble search queries.

    An ``OsidObjectQuery`` is available from an ``OsidSession`` and
    defines methods to query for an ``OsidObject`` that includes setting
    a display name and a description. Once the desired parameters are
    set, the ``OsidQuery`` is given to the designated search method. The
    same ``OsidQuery`` returned from the session must be used in the
    search as the provider may utilize implementation-specific data
    wiithin the object.

    If multiple data elements are set in this interface, the results
    matching all the given data (eg: AND) are returned.

    Any match method inside an ``OsidObjectQuery`` may be invoked
    multiple times. In the case of a match method, each invocation adds
    an element to an ``OR`` expression. Any of these terms may also be
    negated through the ``match`` flag.
      OsidObjectQuery { OsidQuery.matchDisplayName AND (OsidQuery.matchDescription OR OsidObjectQuery.matchDescription)}



    ``OsidObjects`` allow for the definition of an additonal records and
    the ``OsidQuery`` parallels this mechanism. An interface type of an
    ``OsidObject`` record must also define the corresponding
    ``OsidQuery`` record which is available through query interfaces.
    Multiple requests of these typed interfaces may return the same
    underlying object and thus it is only useful to request once.

    String searches are described using a string search ``Type`` that
    indicates the type of regular expression or wildcarding encoding.
    Compatibility with a strings search ``Type`` can be tested within
    this interface.

    As with all aspects of OSIDs, nulls cannot be used. Separate tests
    are available for querying for unset values except for required
    fields.

    An example to find all objects whose name starts with "Fred" or
    whose name starts with "Barney", but the word "dinosaur" does not
    appear in the description and not the color is not purple.
    ``ColorQuery`` is a record of the object that defines a color.
      ObjectObjectQuery query;
      query = session.getObjectQuery();
      query.matchDisplayName("Fred*", wildcardStringMatchType, true);
      query.matchDisplayName("Barney*", wildcardStringMatchType, true);
      query.matchDescriptionMatch("dinosaur", wordStringMatchType, false);
      
      ColorQuery recordQuery;
      recordQuery = query.getObjectRecord(colorRecordType);
      recordQuery.matchColor("purple", false);
      ObjectList list = session.getObjectsByQuery(query);



    """

    @utilities.arguments_not_none
    def match_display_name(self, display_name, string_match_type, match):
        """Adds a display name to match.

        Multiple display name matches can be added to perform a boolean
        ``OR`` among them.

        arg:    display_name (string): display name to match
        arg:    string_match_type (osid.type.Type): the string match
                type
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``display_name`` is not of
                ``string_match_type``
        raise:  NullArgument - ``display_name`` or ``string_match_type``
                is ``null``
        raise:  Unsupported -
                ``supports_string_match_type(string_match_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_display_name(self, match):
        """Matches any object with a display name.

        arg:    match (boolean): ``true`` to match any display name,
                ``false`` to match objects with no display name
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_display_name_terms(self):
        """Clears all display name terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    display_name_terms = property(fdel=clear_display_name_terms)

    @utilities.arguments_not_none
    def match_description(self, description, string_match_type, match):
        """Adds a description name to match.

        Multiple description matches can be added to perform a boolean
        ``OR`` among them.

        arg:    description (string): description to match
        arg:    string_match_type (osid.type.Type): the string match
                type
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``description`` is not of
                ``string_match_type``
        raise:  NullArgument - ``description`` or ``string_match_type``
                is ``null``
        raise:  Unsupported -
                ``supports_string_match_type(string_match_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_description(self, match):
        """Matches a description that has any value.

        arg:    match (boolean): ``true`` to match any description,
                ``false`` to match descriptions with no values
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_description_terms(self):
        """Clears all description terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    description_terms = property(fdel=clear_description_terms)

    @utilities.arguments_not_none
    def match_genus_type(self, genus_type, match):
        """Sets a ``Type`` for querying objects of a given genus.

        A genus type matches if the specified type is the same genus as
        the object genus type.

        arg:    genus_type (osid.type.Type): the object genus type
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``genus_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_genus_type(self, match):
        """Matches an object that has any genus type.

        arg:    match (boolean): ``true`` to match any genus type,
                ``false`` to match objects with no genus type
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_genus_type_terms(self):
        """Clears all genus type terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    genus_type_terms = property(fdel=clear_genus_type_terms)

    @utilities.arguments_not_none
    def match_parent_genus_type(self, genus_type, match):
        """Sets a ``Type`` for querying objects of a given genus.

        A genus type matches if the specified type is the same genus as
        the object or if the specified type is an ancestor of the object
        genus in a type hierarchy.

        arg:    genus_type (osid.type.Type): the object genus type
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``genus_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_parent_genus_type_terms(self):
        """Clears all genus type terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    parent_genus_type_terms = property(fdel=clear_parent_genus_type_terms)

    @utilities.arguments_not_none
    def match_subject_id(self, subject_id, match):
        """Matches an object with a relationship to the given subject.

        arg:    subject_id (osid.id.Id): a subject ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``subject_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_subject_id_terms(self):
        """Clears all subject ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    subject_id_terms = property(fdel=clear_subject_id_terms)

    def supports_subject_query(self):
        """Tests if a ``SubjectQuery`` is available.

        return: (boolean) - ``true`` if a subject query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_subject_query(self):
        """Gets the query for a subject.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.ontology.SubjectQuery) - the subject query
        raise:  Unimplemented - ``supports_subject_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_subject_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    subject_query = property(fget=get_subject_query)

    @utilities.arguments_not_none
    def match_any_subject(self, match):
        """Matches an object that has any relationship to a ``Subject``.

        arg:    match (boolean): ``true`` to match any subject,
                ``false`` to match objects with no subjects
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_subject_terms(self):
        """Clears all subject terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    subject_terms = property(fdel=clear_subject_terms)

    def supports_subject_relevancy_query(self):
        """Tests if a ``RelevancyQuery`` is available to provide queries about the relationships to ``Subjects``.

        return: (boolean) - ``true`` if a relevancy entry query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_subject_relevancy_query(self):
        """Gets the query for a subject relevancy.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.ontology.RelevancyQuery) - the relevancy query
        raise:  Unimplemented - ``supports_subject_relevancy_query()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_subject_relevancy_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    subject_relevancy_query = property(fget=get_subject_relevancy_query)

    def clear_subject_relevancy_terms(self):
        """Clears all subject relevancy terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    subject_relevancy_terms = property(fdel=clear_subject_relevancy_terms)

    @utilities.arguments_not_none
    def match_state_id(self, state_id, match):
        """Matches an object mapped to the given state.

        arg:    state_id (osid.id.Id): a state ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``state_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_state_id_terms(self):
        """Clears all state ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    state_id_terms = property(fdel=clear_state_id_terms)

    def supports_state_query(self):
        """Tests if a ``StateQuery`` is available to provide queries of processed objects.

        return: (boolean) - ``true`` if a state query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_state_query(self):
        """Gets the query for a state.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.process.StateQuery) - the journal entry query
        raise:  Unimplemented - ``supports_state_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_state_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    state_query = property(fget=get_state_query)

    @utilities.arguments_not_none
    def match_any_state(self, match):
        """Matches an object that has any mapping to a ``State`` in the given ``Process``.

        arg:    match (boolean): ``true`` to match any state, ``false``
                to match objects with no states
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_state_terms(self):
        """Clears all state terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    state_terms = property(fdel=clear_state_terms)

    @utilities.arguments_not_none
    def match_comment_id(self, comment_id, match):
        """Matches an object that has the given comment.

        arg:    comment_id (osid.id.Id): a comment ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``comment_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_comment_id_terms(self):
        """Clears all comment ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    comment_id_terms = property(fdel=clear_comment_id_terms)

    def supports_comment_query(self):
        """Tests if a ``CommentQuery`` is available.

        return: (boolean) - ``true`` if a comment query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_comment_query(self):
        """Gets the query for a comment.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.commenting.CommentQuery) - the comment query
        raise:  Unimplemented - ``supports_comment_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    comment_query = property(fget=get_comment_query)

    @utilities.arguments_not_none
    def match_any_comment(self, match):
        """Matches an object that has any ``Comment`` in the given ``Book``.

        arg:    match (boolean): ``true`` to match any comment,
                ``false`` to match objects with no comments
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_comment_terms(self):
        """Clears all comment terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    comment_terms = property(fdel=clear_comment_terms)

    @utilities.arguments_not_none
    def match_journal_entry_id(self, journal_entry_id, match):
        """Matches an object that has the given journal entry.

        arg:    journal_entry_id (osid.id.Id): a journal entry ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``journal_entry_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_journal_entry_id_terms(self):
        """Clears all journal entry ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    journal_entry_id_terms = property(fdel=clear_journal_entry_id_terms)

    def supports_journal_entry_query(self):
        """Tests if a ``JournalEntry`` is available to provide queries of journaled ``OsidObjects``.

        return: (boolean) - ``true`` if a journal entry query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_journal_entry_query(self):
        """Gets the query for a journal entry.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.journaling.JournalEntryQuery) - the journal entry
                query
        raise:  Unimplemented - ``supports_journal_entry_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_journal_entry_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    journal_entry_query = property(fget=get_journal_entry_query)

    @utilities.arguments_not_none
    def match_any_journal_entry(self, match):
        """Matches an object that has any ``JournalEntry`` in the given ``Journal``.

        arg:    match (boolean): ``true`` to match any journal entry,
                ``false`` to match objects with no journal entries
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_journal_entry_terms(self):
        """Clears all journal entry terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    journal_entry_terms = property(fdel=clear_journal_entry_terms)

    def supports_statistic_query(self):
        """Tests if a ``StatisticQuery`` is available to provide statistical queries.

        return: (boolean) - ``true`` if a statistic query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_statistic_query(self):
        """Gets the query for a statistic.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.metering.StatisticQuery) - the statistic query
        raise:  Unimplemented - ``supports_statistic_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_statistic_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    statistic_query = property(fget=get_statistic_query)

    @utilities.arguments_not_none
    def match_any_statistic(self, match):
        """Matches an object that has any ``Statistic``.

        arg:    match (boolean): ``true`` to match any statistic,
                ``false`` to match objects with no statistics
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_statistic_terms(self):
        """Clears all statistic terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    statistic_terms = property(fdel=clear_statistic_terms)

    @utilities.arguments_not_none
    def match_credit_id(self, credit_id, match):
        """Matches an object that has the given credit.

        arg:    credit_id (osid.id.Id): a credit ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``credit_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_credit_id_terms(self):
        """Clears all credit ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    credit_id_terms = property(fdel=clear_credit_id_terms)

    def supports_credit_query(self):
        """Tests if a ``CreditQuery`` is available to provide queries of related acknowledgements.

        return: (boolean) - ``true`` if a credit query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_credit_query(self):
        """Gets the query for an ackowledgement credit.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.acknowledgement.CreditQuery) - the credit query
        raise:  Unimplemented - ``supports_credit_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_credit_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    credit_query = property(fget=get_credit_query)

    @utilities.arguments_not_none
    def match_any_credit(self, match):
        """Matches an object that has any ``Credit``.

        arg:    match (boolean): ``true`` to match any credit, ``false``
                to match objects with no credits
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_credit_terms(self):
        """Clears all credit terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    credit_terms = property(fdel=clear_credit_terms)

    @utilities.arguments_not_none
    def match_relationship_id(self, relationship_id, match):
        """Matches an object that has the given relationship.

        arg:    relationship_id (osid.id.Id): a relationship ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``relationship_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_relationship_id_terms(self):
        """Clears all relationship ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    relationship_id_terms = property(fdel=clear_relationship_id_terms)

    def supports_relationship_query(self):
        """Tests if a ``RelationshipQuery`` is available.

        return: (boolean) - ``true`` if a relationship query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_relationship_query(self):
        """Gets the query for relationship.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.relationship.RelationshipQuery) - the relationship
                query
        raise:  Unimplemented - ``supports_relationship_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_relationship_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    relationship_query = property(fget=get_relationship_query)

    @utilities.arguments_not_none
    def match_any_relationship(self, match):
        """Matches an object that has any ``Relationship``.

        arg:    match (boolean): ``true`` to match any relationship,
                ``false`` to match objects with no relationships
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_relationship_terms(self):
        """Clears all relationship terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    relationship_terms = property(fdel=clear_relationship_terms)

    @utilities.arguments_not_none
    def match_relationship_peer_id(self, peer_id, match):
        """Matches an object that has a relationship to the given peer ``Id``.

        arg:    peer_id (osid.id.Id): a relationship peer ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``peer_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_relationship_peer_id_terms(self):
        """Clears all relationship ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    relationship_peer_id_terms = property(fdel=clear_relationship_peer_id_terms)


class OsidRelationshipQuery(abc_osid_queries.OsidRelationshipQuery, OsidObjectQuery, OsidTemporalQuery):
    """This is the query interface for searching relationships.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """

    @utilities.arguments_not_none
    def match_end_reason_id(self, state_id, match):
        """Match the ``Id`` of the end reason state.

        arg:    state_id (osid.id.Id): ``Id`` to match
        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``rule_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_end_reason_id_terms(self):
        """Clears all state ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    end_reason_id_terms = property(fdel=clear_end_reason_id_terms)

    def supports_end_reason_query(self):
        """Tests if a ``StateQuery`` for the end reason is available.

        return: (boolean) - ``true`` if a end reason query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_end_reason_query(self, match):
        """Gets the query for the end reason state.

        Each retrieval performs a boolean ``OR``.

        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        return: (osid.process.StateQuery) - the state query
        raise:  Unimplemented - ``supports_end_reason_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_end_reason_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_end_reason(self, match):
        """Match any end reason state.

        arg:    match (boolean): ``true`` to match any state, ``false``
                to match no state
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_end_reason_terms(self):
        """Clears all end reason state terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    end_reason_terms = property(fdel=clear_end_reason_terms)


class OsidCatalogQuery(abc_osid_queries.OsidCatalogQuery, OsidObjectQuery, OsidSourceableQuery, OsidFederateableQuery):
    """The ``OsidCatalogQuery`` is used to assemble search queries for catalogs."""




class OsidRuleQuery(abc_osid_queries.OsidRuleQuery, OsidObjectQuery, OsidOperableQuery):
    """This is the query interface for searching rules.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """

    @utilities.arguments_not_none
    def match_rule_id(self, rule_id, match):
        """Match the ``Id`` of the rule.

        arg:    rule_id (osid.id.Id): ``Id`` to match
        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``rule_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_rule_id_terms(self):
        """Clears all rule ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rule_id_terms = property(fdel=clear_rule_id_terms)

    def supports_rule_query(self):
        """Tests if a ``RuleQuery`` for the rule is available.

        return: (boolean) - ``true`` if a rule query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_rule_query(self, match):
        """Gets the query for the rule.

        Each retrieval performs a boolean ``OR``.

        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        return: (osid.rules.RuleQuery) - the rule query
        raise:  Unimplemented - ``supports_rule_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_rule_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_rule(self, match):
        """Match any associated rule.

        arg:    match (boolean): ``true`` to match any rule, ``false``
                to match no rules
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_rule_terms(self):
        """Clears all rule terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rule_terms = property(fdel=clear_rule_terms)


class OsidEnablerQuery(abc_osid_queries.OsidEnablerQuery, OsidRuleQuery, OsidTemporalQuery):
    """This is the query interface for searching enablers.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """

    @utilities.arguments_not_none
    def match_schedule_id(self, schedule_id, match):
        """Match the ``Id`` of an associated schedule.

        arg:    schedule_id (osid.id.Id): ``Id`` to match
        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``schedule_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_schedule_id_terms(self):
        """Clears all schedule ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    schedule_id_terms = property(fdel=clear_schedule_id_terms)

    def supports_schedule_query(self):
        """Tests if a ``ScheduleQuery`` for the rule is available.

        return: (boolean) - ``true`` if a schedule query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_schedule_query(self, match):
        """Gets the query for the schedule.

        Each retrieval performs a boolean ``OR``.

        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        return: (osid.calendaring.ScheduleQuery) - the schedule query
        raise:  Unimplemented - ``supports_schedule_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_schedule_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_schedule(self, match):
        """Match any associated schedule.

        arg:    match (boolean): ``true`` to match any schedule,
                ``false`` to match no schedules
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_schedule_terms(self):
        """Clears all schedule terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    schedule_terms = property(fdel=clear_schedule_terms)

    @utilities.arguments_not_none
    def match_event_id(self, event_id, match):
        """Match the ``Id`` of an associated event.

        arg:    event_id (osid.id.Id): ``Id`` to match
        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``event_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_event_id_terms(self):
        """Clears all event ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    event_id_terms = property(fdel=clear_event_id_terms)

    def supports_event_query(self):
        """Tests if a ``EventQuery`` for the rule is available.

        return: (boolean) - ``true`` if an event query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_event_query(self, match):
        """Gets the query for the event.

        Each retrieval performs a boolean ``OR``.

        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        return: (osid.calendaring.EventQuery) - the event query
        raise:  Unimplemented - ``supports_event_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_event_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_event(self, match):
        """Match any associated event.

        arg:    match (boolean): ``true`` to match any event, ``false``
                to match no events
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_event_terms(self):
        """Clears all recurirng event terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    event_terms = property(fdel=clear_event_terms)

    @utilities.arguments_not_none
    def match_cyclic_event_id(self, cyclic_event_id, match):
        """Sets the cyclic event ``Id`` for this query.

        arg:    cyclic_event_id (osid.id.Id): the cyclic event ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``cyclic_event_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_cyclic_event_id_terms(self):
        """Clears the cyclic event ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    cyclic_event_id_terms = property(fdel=clear_cyclic_event_id_terms)

    def supports_cyclic_event_query(self):
        """Tests if a ``CyclicEventQuery`` is available.

        return: (boolean) - ``true`` if a cyclic event query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_cyclic_event_query(self):
        """Gets the query for a cyclic event.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.calendaring.cycle.CyclicEventQuery) - the cyclic
                event query
        raise:  Unimplemented - ``supports_cyclic_event_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_cyclic_event_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    cyclic_event_query = property(fget=get_cyclic_event_query)

    @utilities.arguments_not_none
    def match_any_cyclic_event(self, match):
        """Matches any enabler with a cyclic event.

        arg:    match (boolean): ``true`` to match any enablers with a
                cyclic event, ``false`` to match enablers with no cyclic
                events
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_cyclic_event_terms(self):
        """Clears the cyclic event query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    cyclic_event_terms = property(fdel=clear_cyclic_event_terms)

    @utilities.arguments_not_none
    def match_demographic_id(self, resource_id, match):
        """Match the ``Id`` of the demographic resource.

        arg:    resource_id (osid.id.Id): ``Id`` to match
        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``resource_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_demographic_id_terms(self):
        """Clears all resource ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    demographic_id_terms = property(fdel=clear_demographic_id_terms)

    def supports_demographic_query(self):
        """Tests if a ``ResourceQuery`` for the demographic is available.

        return: (boolean) - ``true`` if a resource query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_demographic_query(self, match):
        """Gets the query for the resource.

        Each retrieval performs a boolean ``OR``.

        arg:    match (boolean): ``true`` if for a positive match,
                ``false`` for a negative match
        return: (osid.resource.ResourceQuery) - the resource query
        raise:  Unimplemented - ``supports_resource_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_resource_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_demographic(self, match):
        """Match any associated resource.

        arg:    match (boolean): ``true`` to match any demographic,
                ``false`` to match no rules
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_demographic_terms(self):
        """Clears all demographic terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    demographic_terms = property(fdel=clear_demographic_terms)


class OsidConstrainerQuery(abc_osid_queries.OsidConstrainerQuery, OsidRuleQuery):
    """This is the query interface for searching constrainers.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """




class OsidProcessorQuery(abc_osid_queries.OsidProcessorQuery, OsidRuleQuery):
    """This is the query interface for searching processors.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """




class OsidGovernatorQuery(abc_osid_queries.OsidGovernatorQuery, OsidObjectQuery, OsidOperableQuery, OsidSourceableQuery):
    """This is the query interface for searching governers.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """




class OsidCompendiumQuery(abc_osid_queries.OsidCompendiumQuery, OsidObjectQuery, OsidSubjugateableQuery):
    """This is the query interface for searching reports.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """

    @utilities.arguments_not_none
    def match_start_date(self, start, end, match):
        """Matches reports whose start date falls in between the given dates inclusive.

        arg:    start (osid.calendaring.DateTime): start of date range
        arg:    end (osid.calendaring.DateTime): end of date range
        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        raise:  InvalidArgument - ``start`` is less than ``end``
        raise:  NullArgument - ``start`` or ``end`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_start_date(self, match):
        """Matches reports with any start date set.

        arg:    match (boolean): ``true`` to match any start date,
                ``false`` to match no start date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_start_date_terms(self):
        """Clears the start date query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    start_date_terms = property(fdel=clear_start_date_terms)

    @utilities.arguments_not_none
    def match_end_date(self, start, end, match):
        """Matches reports whose effective end date falls in between the given dates inclusive.

        arg:    start (osid.calendaring.DateTime): start of date range
        arg:    end (osid.calendaring.DateTime): end of date range
        arg:    match (boolean): ``true`` if a positive match, ``false``
                for negative match
        raise:  InvalidArgument - ``start`` is less than ``end``
        raise:  NullArgument - ``start`` or ``end`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_end_date(self, match):
        """Matches reports with any end date set.

        arg:    match (boolean): ``true`` to match any end date,
                ``false`` to match no start date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_end_date_terms(self):
        """Clears the end date query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    end_date_terms = property(fdel=clear_end_date_terms)

    @utilities.arguments_not_none
    def match_interpolated(self, match):
        """Match reports that are interpolated.

        arg:    match (boolean): ``true`` to match any interpolated
                reports, ``false`` to match non- interpolated reports
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_interpolated_terms(self):
        """Clears the interpolated query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    interpolated_terms = property(fdel=clear_interpolated_terms)

    @utilities.arguments_not_none
    def match_extrapolated(self, match):
        """Match reports that are extrapolated.

        arg:    match (boolean): ``true`` to match any extrapolated
                reports, ``false`` to match non- extrapolated reports
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_extrapolated_terms(self):
        """Clears the extrapolated query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    extrapolated_terms = property(fdel=clear_extrapolated_terms)


class OsidCapsuleQuery(abc_osid_queries.OsidCapsuleQuery, OsidQuery):
    """This is the query interface for searching capsulating interfaces.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """




