"""GStudio implementations of osid search_orders."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from dlkit.abstract_osid.osid import search_orders as abc_osid_search_orders
from ..osid import markers as osid_markers
from dlkit.abstract_osid.osid import errors




class OsidSearchOrder(abc_osid_search_orders.OsidSearchOrder, osid_markers.Suppliable):
    """``OsidSearchOrder`` specifies preferred ordering of search results.

    An ``OsidSearchOrder`` is available from an search session and
    supplied to an ``OsidSearch`` interface. OsidSearch os =
    session.getObjectSearch(); os.limitResultSet(1, 25); OsidSearchOrder
    order = session.getObjectSearchOrder(); order.orderByDisplayName();
    os.orderResults(order); OsidQuery queru; query =
    session.getObjectQuery(); query.addDescriptionMatch("*food*",
    wildcardStringMatchType, true); ObjectSearchResults results =
    session.getObjectsBySearch(query, os); ObjectList list =
    results.getObjectList();

    """




class OsidIdentifiableSearchOrder(abc_osid_search_orders.OsidIdentifiableSearchOrder, OsidSearchOrder):
    """``OsidIdentifiableSearchOrder`` specifies preferred ordering of search results.

    An ``OsidSearchOrder`` is available from an search session and
    supplied to an ``OsidSearch``.

    """

    @utilities.arguments_not_none
    def order_by_id(self, style):
        """Specifies a preference for ordering the result set by the ``Id``.

        arg:    style (osid.SearchOrderStyle): the search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class OsidExtensibleSearchOrder(abc_osid_search_orders.OsidExtensibleSearchOrder, OsidSearchOrder, osid_markers.Extensible):
    """``OsidExtensibleSearchOrder`` specifies preferred ordering of search results.

    An ``OsidSearchOrder`` is available from an search session and
    supplied to an ``OsidSearch``.

    """




class OsidBrowsableSearchOrder(abc_osid_search_orders.OsidBrowsableSearchOrder, OsidSearchOrder):
    """``OsidBrowsableSearchOrder`` specifies preferred ordering of search results.

    An ``OsidSearchOrder`` is available from an search session and
    supplied to an ``OsidSearch``.

    """




class OsidTemporalSearchOrder(abc_osid_search_orders.OsidTemporalSearchOrder, OsidSearchOrder):
    """An interface for specifying the ordering of search results."""

    @utilities.arguments_not_none
    def order_by_effective(self, style):
        """Specifies a preference for ordering the result set by the effective status.

        arg:    style (osid.SearchOrderStyle): the search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_start_date(self, style):
        """Specifies a preference for ordering the result set by the start date.

        arg:    style (osid.SearchOrderStyle): the search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_end_date(self, style):
        """Specifies a preference for ordering the result set by the end date.

        arg:    style (osid.SearchOrderStyle): the search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class OsidSubjugateableSearchOrder(abc_osid_search_orders.OsidSubjugateableSearchOrder, OsidSearchOrder):
    """An interface for specifying the ordering of dependent object search results."""




class OsidAggregateableSearchOrder(abc_osid_search_orders.OsidAggregateableSearchOrder, OsidSearchOrder):
    """An interface for specifying the ordering of assemblage search results."""




class OsidContainableSearchOrder(abc_osid_search_orders.OsidContainableSearchOrder, OsidSearchOrder):
    """An interface for specifying the ordering of search results."""

    @utilities.arguments_not_none
    def order_by_sequestered(self, style):
        """Specifies a preference for ordering the result set by the sequestered flag.

        arg:    style (osid.SearchOrderStyle): the search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class OsidSourceableSearchOrder(abc_osid_search_orders.OsidSourceableSearchOrder, OsidSearchOrder):
    """An interface for specifying the ordering of search results."""

    @utilities.arguments_not_none
    def order_by_provider(self, style):
        """Specifies a preference for ordering the results by provider.

        The element of the provider to order is not specified but may be
        managed through the provider ordering interface.

        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def supports_provider_search_order(self):
        """Tests if a ``ProviderSearchOrder`` interface is available.

        return: (boolean) - ``true`` if a provider search order
                interface is available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_provider_search_order(self):
        """Gets the search order interface for a provider.

        return: (osid.resource.ResourceSearchOrder) - the provider
                search order interface
        raise:  Unimplemented - ``supports_provider_search_order()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_provider_search_order()`` is ``true``.*

        """
        raise errors.Unimplemented()

    provider_search_order = property(fget=get_provider_search_order)


class OsidFederateableSearchOrder(abc_osid_search_orders.OsidFederateableSearchOrder, OsidSearchOrder):
    """An interface for specifying the ordering of search results."""




class OsidOperableSearchOrder(abc_osid_search_orders.OsidOperableSearchOrder, OsidSearchOrder):
    """An interface for specifying the ordering of search results."""

    @utilities.arguments_not_none
    def order_by_active(self, style):
        """Specifies a preference for ordering the result set by the active status.

        arg:    style (osid.SearchOrderStyle): the search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_enabled(self, style):
        """Specifies a preference for ordering the result set by the administratively enabled status.

        arg:    style (osid.SearchOrderStyle): the search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_disabled(self, style):
        """Specifies a preference for ordering the result set by the administratively disabled status.

        arg:    style (osid.SearchOrderStyle): the search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_operational(self, style):
        """Specifies a preference for ordering the results by the operational status.

        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class OsidObjectSearchOrder(abc_osid_search_orders.OsidObjectSearchOrder, OsidIdentifiableSearchOrder, OsidExtensibleSearchOrder, OsidBrowsableSearchOrder):
    """``OsidObjectSearchOrder`` specifies preferred ordering of search results.

    An ``OsidSearchOrder`` is available from an search session and
    supplied to an ``OsidSearch``. OsidObjectSearch os =
    session.getObjectSearch(); os.limitResultSet(1, 25);
    OsidObjectSearchOrder order = session.getObjectSearchOrder();
    order.orderByDisplayName(); os.orderResults(order); OsidObjectQuery
    query; query = session.getObjectQuery();
    query.addDescriptionMatch("*food*", wildcardStringMatchType, true);
    ObjectSearchResults results = session.getObjectsBySearch(query, os);
    ObjectList list = results.getObjectList();

    """

    @utilities.arguments_not_none
    def order_by_display_name(self, style):
        """Specifies a preference for ordering the result set by the display name.

        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_description(self, style):
        """Specifies a preference for ordering the result set by the description.

        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_genus_type(self, style):
        """Specifies a preference for ordering the result set by the genus type.

        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_state(self, process_id, style):
        """Orders by the state in a given ``Process``.

        arg:    process_id (osid.id.Id): a process ``Id``
        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``process_id`` or ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_cumulative_rating(self, book_id, style):
        """Orders by the cumulative rating in a given ``Book``.

        arg:    book_id (osid.id.Id): a book ``Id``
        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``book_id`` or ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_statistic(self, meter_id, style):
        """Orders by a statistic for a given ``Meter``.

        arg:    meter_id (osid.id.Id): a meter ``Id``
        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``meter_id`` or ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_create_time(self, style):
        """Orders by the timestamp of the first journal entry.

        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_last_modified_time(self, style):
        """Orders by the timestamp of the last journal entry.

        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class OsidRelationshipSearchOrder(abc_osid_search_orders.OsidRelationshipSearchOrder, OsidObjectSearchOrder, OsidTemporalSearchOrder):
    """An interface for specifying the ordering of search results."""

    @utilities.arguments_not_none
    def order_by_end_reason(self, style):
        """Specifies a preference for ordering the results by the end reason state.

        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def supports_end_reason_search_order(self):
        """Tests if a ``StateSearchOrder`` is available.

        return: (boolean) - ``true`` if a state search order is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_end_reason_search_order(self):
        """Gets the search order for a state.

        return: (osid.process.StateSearchOrder) - the state search order
        raise:  Unimplemented - ``supports_end_reason_search_order()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_end_reason_search_order()`` is ``true``.*

        """
        raise errors.Unimplemented()

    end_reason_search_order = property(fget=get_end_reason_search_order)


class OsidCatalogSearchOrder(abc_osid_search_orders.OsidCatalogSearchOrder, OsidObjectSearchOrder, OsidSourceableSearchOrder, OsidFederateableSearchOrder):
    """An interface for specifying the ordering of catalog search results."""




class OsidRuleSearchOrder(abc_osid_search_orders.OsidRuleSearchOrder, OsidObjectSearchOrder, OsidOperableSearchOrder):
    """An interface for specifying the ordering of search results."""

    @utilities.arguments_not_none
    def order_by_rule(self, style):
        """Specifies a preference for ordering the results by the associated rule.

        The element of the rule to order is not specified but may be
        managed through a ``RuleSearchOrder``.

        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def supports_rule_search_order(self):
        """Tests if a ``RuleSearchOrder`` is available.

        return: (boolean) - ``true`` if a rule search order is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_rule_search_order(self):
        """Gets the search order for a rule.

        return: (osid.rules.RuleSearchOrder) - the rule search order
        raise:  Unimplemented - ``supports_rule_search_order()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_rule_search_order()`` is ``true``.*

        """
        raise errors.Unimplemented()

    rule_search_order = property(fget=get_rule_search_order)


class OsidEnablerSearchOrder(abc_osid_search_orders.OsidEnablerSearchOrder, OsidRuleSearchOrder, OsidTemporalSearchOrder):
    """An interface for specifying the ordering of search results."""

    @utilities.arguments_not_none
    def order_by_schedule(self, style):
        """Specifies a preference for ordering the results by the associated schedule.

        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def supports_schedule_search_order(self):
        """Tests if a ``ScheduleSearchOrder`` is available.

        return: (boolean) - ``true`` if a schedule search order is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_schedule_search_order(self):
        """Gets the search order for a schedule.

        return: (osid.calendaring.ScheduleSearchOrder) - the schedule
                search order
        raise:  Unimplemented - ``supports_schedule_search_order() is
                false``
        *compliance: optional -- This method must be implemented if
        ``supports_schedule_search_order()`` is true.*

        """
        raise errors.Unimplemented()

    schedule_search_order = property(fget=get_schedule_search_order)

    @utilities.arguments_not_none
    def order_by_event(self, style):
        """Specifies a preference for ordering the results by the associated event.

        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def supports_event_search_order(self):
        """Tests if an ``EventSearchOrder`` is available.

        return: (boolean) - ``true`` if an event search order is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_event_search_order(self):
        """Gets the search order for an event.

        return: (osid.calendaring.EventSearchOrder) - the event search
                order
        raise:  Unimplemented - ``supports_event_search_order() is
                false``
        *compliance: optional -- This method must be implemented if
        ``supports_event_search_order()`` is true.*

        """
        raise errors.Unimplemented()

    event_search_order = property(fget=get_event_search_order)

    @utilities.arguments_not_none
    def order_by_cyclic_event(self, style):
        """Orders the results by cyclic event.

        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def supports_cyclic_event_search_order(self):
        """Tests if a cyclic event search order is available.

        return: (boolean) - ``true`` if a cyclic event search order is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_cyclic_event_search_order(self):
        """Gets the cyclic event search order.

        return: (osid.calendaring.cycle.CyclicEventSearchOrder) - the
                cyclic event search order
        raise:  IllegalState - ``supports_cyclic_event_search_order()``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    cyclic_event_search_order = property(fget=get_cyclic_event_search_order)

    @utilities.arguments_not_none
    def order_by_demographic(self, style):
        """Specifies a preference for ordering the results by the associated demographic resource.

        arg:    style (osid.SearchOrderStyle): search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def supports_demographic_search_order(self):
        """Tests if a ``ResourceSearchOrder`` is available.

        return: (boolean) - ``true`` if a resource search order is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_demographic_search_order(self):
        """Gets the search order for a demographic resource.

        return: (osid.resource.ResourceSearchOrder) - the resource
                search order
        raise:  Unimplemented - ``supports_demographic_search_order()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_demographic_search_order()`` is ``true``.*

        """
        raise errors.Unimplemented()

    demographic_search_order = property(fget=get_demographic_search_order)


class OsidConstrainerSearchOrder(abc_osid_search_orders.OsidConstrainerSearchOrder, OsidRuleSearchOrder):
    """An interface for specifying the ordering of search results."""




class OsidProcessorSearchOrder(abc_osid_search_orders.OsidProcessorSearchOrder, OsidRuleSearchOrder):
    """An interface for specifying the ordering of search results."""




class OsidGovernatorSearchOrder(abc_osid_search_orders.OsidGovernatorSearchOrder, OsidObjectSearchOrder, OsidOperableSearchOrder, OsidSourceableSearchOrder):
    """An interface for specifying the ordering of search results."""




class OsidCompendiumSearchOrder(abc_osid_search_orders.OsidCompendiumSearchOrder, OsidObjectSearchOrder, OsidSubjugateableSearchOrder):
    """An interface for specifying the ordering of search results."""

    @utilities.arguments_not_none
    def order_by_start_date(self, style):
        """Specifies a preference for ordering the result set by the start date.

        arg:    style (osid.SearchOrderStyle): the search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_end_date(self, style):
        """Specifies a preference for ordering the result set by the end date.

        arg:    style (osid.SearchOrderStyle): the search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_interpolated(self, style):
        """Specifies a preference for ordering the result set by interpolated results.

        arg:    style (osid.SearchOrderStyle): the search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_by_extrapolated(self, style):
        """Specifies a preference for ordering the result set by extrapolated results.

        arg:    style (osid.SearchOrderStyle): the search order style
        raise:  NullArgument - ``style`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class OsidCapsuleSearchOrder(abc_osid_search_orders.OsidCapsuleSearchOrder, OsidSearchOrder):
    """An interface for specifying the ordering of search results."""




