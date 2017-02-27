"""GStudio implementations of osid metadata."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from dlkit.abstract_osid.osid import metadata as abc_osid_metadata
from dlkit.abstract_osid.osid import errors




class Metadata(abc_osid_metadata.Metadata):
    """The ``Metadata`` interface defines a set of methods describing a the syntax and rules for creating and updating a data element inside an ``OsidForm``.

    This interface provides a means to retrieve special restrictions
    placed upon data elements such as sizes and ranges that may vary
    from provider to provider or from object to object.

    """

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def get_element_id(self):
        """Gets a unique ``Id`` for the data element.

        return: (osid.id.Id) - an ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_element_id_template
        return self._kwargs['element_id']

    element_id = property(fget=get_element_id)

    def get_element_label(self):
        """Gets a display label for the data element.

        return: (osid.locale.DisplayText) - a display label
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_element_id_template
        return self._kwargs['element_label']

    element_label = property(fget=get_element_label)

    def get_instructions(self):
        """Gets instructions for updating this element value.

        This is a human readable description of the data element or
        property that may include special instructions or caveats to the
        end-user above and beyond what this interface provides.

        return: (osid.locale.DisplayText) - instructions
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_element_id_template
        return self._kwargs['instructions']

    instructions = property(fget=get_instructions)

    def get_syntax(self):
        """Gets the syntax of this data.

        return: (osid.Syntax) - an enumeration indicating thetype of
                value
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_element_id_template
        return self._kwargs['syntax']

    syntax = property(fget=get_syntax)

    def is_array(self):
        """Tests if this data element is an array.

        return: (boolean) - ``true`` if this data is an array, ``false``
                if a single element
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_element_id_template
        return self._kwargs['array']

    def is_required(self):
        """Tests if this data element is required for creating new objects.

        return: (boolean) - ``true`` if this element value is required,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_element_id_template
        return self._kwargs['required']

    def is_read_only(self):
        """Tests if this data can be updated.

        This may indicate the result of a pre-authorization but is not a
        guarantee that an authorization failure will not occur when the
        create or update transaction is issued.

        return: (boolean) - ``true`` if this data is not updatable,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_element_id_template
        return self._kwargs['read_only']

    def is_linked(self):
        """Tests if this data element is linked to other data in the object.

        Updating linked data elements should refresh all metadata and
        revalidate object elements.

        return: (boolean) - true if this element is linked, false if
                updates have no side effect
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_element_id_template
        return self._kwargs['linked']

    def is_value_known(self):
        """Tests if an existing value is known for this data element.

        If it is known that a value does not exist, then this method
        returns ``true``.

        return: (boolean) - ``true`` if the element value is known,
                ``false`` if the element value is not known
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_element_id_template
        return self._kwargs['value_known']

    def has_value(self):
        """Tests if this data element has a set non-default value.

        return: (boolean) - ``true`` if this element value has been set,
                ``false`` otherwise
        raise:  IllegalState - ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['']:
            raise errors.IllegalState()
        return self._kwargs['value']

    def get_units(self):
        """Gets the units of this data for display purposes ('lbs', 'gills', 'furlongs').

        return: (osid.locale.DisplayText) - the display units of this
                data or an empty string if not applicable
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_element_id_template
        return self._kwargs['units']

    units = property(fget=get_units)

    def get_minimum_elements(self):
        """In the case where an array or list of elements is specified in an ``OsidForm,`` this specifies the minimum number of elements that must be included.

        return: (cardinal) - the minimum elements or ``1`` if
                ``is_array()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_element_id_template
        return self._kwargs['minimum_elements']

    minimum_elements = property(fget=get_minimum_elements)

    def get_maximum_elements(self):
        """In the case where an array or list of elements is specified in an ``OsidForm,`` this specifies the maximum number of elements that can be specified.

        return: (cardinal) - the maximum elements or ``1`` if
                ``is_array()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_element_id_template
        return self._kwargs['maximum_elements']

    maximum_elements = property(fget=get_maximum_elements)

    def get_minimum_cardinal(self):
        """Gets the minimum cardinal value.

        return: (cardinal) - the minimum cardinal
        raise:  IllegalState - syntax is not a ``CARDINAL``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['CARDINAL']:
            raise errors.IllegalState()
        return self._kwargs['minimum_cardinal']

    minimum_cardinal = property(fget=get_minimum_cardinal)

    def get_maximum_cardinal(self):
        """Gets the maximum cardinal value.

        return: (cardinal) - the maximum cardinal
        raise:  IllegalState - syntax is not a ``CARDINAL``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['CARDINAL']:
            raise errors.IllegalState()
        return self._kwargs['maximum_cardinal']

    maximum_cardinal = property(fget=get_maximum_cardinal)

    def get_cardinal_set(self):
        """Gets the set of acceptable cardinal values.

        return: (cardinal) - a set of cardinals or an empty array if not
                restricted
        raise:  IllegalState - syntax is not a ``CARDINAL``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['CARDINAL']:
            raise errors.IllegalState()
        return self._kwargs['cardinal_set']

    cardinal_set = property(fget=get_cardinal_set)

    def get_default_cardinal_values(self):
        """Gets the default cardinal values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (cardinal) - the default cardinal values
        raise:  IllegalState - syntax is not a ``CARDINAL`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['CARDINAL']:
            raise errors.IllegalState()
        return self._kwargs['default_cardinal_values']

    default_cardinal_values = property(fget=get_default_cardinal_values)

    def get_existing_cardinal_values(self):
        """Gets the existing cardinal values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (cardinal) - the existing cardinal values
        raise:  IllegalState - syntax is not a ``CARDINAL`` or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['CARDINAL']:
            raise errors.IllegalState()
        return self._kwargs['existing_cardinal_values']

    existing_cardinal_values = property(fget=get_existing_cardinal_values)

    def get_coordinate_types(self):
        """Gets the set of acceptable coordinate types.

        return: (osid.type.Type) - the set of coordinate types
        raise:  IllegalState - syntax is not a ``COORDINATE or
                SPATIALUNIT``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['COORDINATE', 'SPATIALUNIT']:
            raise errors.IllegalState()
        return self._kwargs['coordinate_types']

    coordinate_types = property(fget=get_coordinate_types)

    @utilities.arguments_not_none
    def supports_coordinate_type(self, coordinate_type):
        """Tests if the given coordinate type is supported.

        arg:    coordinate_type (osid.type.Type): a coordinate Type
        return: (boolean) - ``true`` if the type is supported, ``false``
                otherwise
        raise:  IllegalState - syntax is not a ``COORDINATE``
        raise:  NullArgument - ``coordinate_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.supports_coordinate_type
        if self._kwargs['syntax'] not in ['``COORDINATE``']:
            raise errors.IllegalState()
        return coordinate_type in self.get_coordinate_types

    @utilities.arguments_not_none
    def get_axes_for_coordinate_type(self, coordinate_type):
        """Gets the number of axes for a given supported coordinate type.

        arg:    coordinate_type (osid.type.Type): a coordinate Type
        return: (cardinal) - the number of axes
        raise:  IllegalState - syntax is not a ``COORDINATE``
        raise:  NullArgument - ``coordinate_type`` is ``null``
        raise:  Unsupported -
                ``supports_coordinate_type(coordinate_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_minimum_coordinate_values(self, coordinate_type):
        """Gets the minimum coordinate values given supported coordinate type.

        arg:    coordinate_type (osid.type.Type): a coordinate Type
        return: (decimal) - the minimum coordinate values
        raise:  IllegalState - syntax is not a ``COORDINATE``
        raise:  NullArgument - ``coordinate_type`` is ``null``
        raise:  Unsupported -
                ``supports_coordinate_type(coordinate_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_maximum_coordinate_values(self, coordinate_type):
        """Gets the maximum coordinate values given supported coordinate type.

        arg:    coordinate_type (osid.type.Type): a coordinate Type
        return: (decimal) - the maximum coordinate values
        raise:  IllegalState - syntax is not a ``COORDINATE``
        raise:  NullArgument - ``coordinate_type`` is ``null``
        raise:  Unsupported -
                ``supports_coordinate_type(coordinate_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_coordinate_set(self):
        """Gets the set of acceptable coordinate values.

        return: (osid.mapping.Coordinate) - a set of coordinates or an
                empty array if not restricted
        raise:  IllegalState - syntax is not a ``COORDINATE``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['COORDINATE']:
            raise errors.IllegalState()
        return self._kwargs['coordinate_set']

    coordinate_set = property(fget=get_coordinate_set)

    def get_default_coordinate_values(self):
        """Gets the default coordinate values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (osid.mapping.Coordinate) - the default coordinate
                values
        raise:  IllegalState - syntax is not a ``COORDINATE`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['COORDINATE']:
            raise errors.IllegalState()
        return self._kwargs['default_coordinate_values']

    default_coordinate_values = property(fget=get_default_coordinate_values)

    def get_existing_coordinate_values(self):
        """Gets the existing coordinate values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (osid.mapping.Coordinate) - the existing coordinate
                values
        raise:  IllegalState - syntax is not a ``COORDINATE`` or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['COORDINATE']:
            raise errors.IllegalState()
        return self._kwargs['existing_coordinate_values']

    existing_coordinate_values = property(fget=get_existing_coordinate_values)

    def get_currency_types(self):
        """Gets the set of acceptable currency types.

        return: (osid.type.Type) - the set of currency types
        raise:  IllegalState - syntax is not a ``CURRENCY``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['CURRENCY']:
            raise errors.IllegalState()
        return self._kwargs['currency_types']

    currency_types = property(fget=get_currency_types)

    @utilities.arguments_not_none
    def supports_currency_type(self, currency_type):
        """Tests if the given currency type is supported.

        arg:    currency_type (osid.type.Type): a currency Type
        return: (boolean) - ``true`` if the type is supported, ``false``
                otherwise
        raise:  IllegalState - syntax is not a ``CURRENCY``
        raise:  NullArgument - ``currency_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.supports_coordinate_type
        if self._kwargs['syntax'] not in ['``CURRENCY``']:
            raise errors.IllegalState()
        return currency_type in self.get_currency_types

    def get_minimum_currency(self):
        """Gets the minimum currency value.

        return: (osid.financials.Currency) - the minimum currency
        raise:  IllegalState - syntax is not a ``CURRENCY``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['CURRENCY']:
            raise errors.IllegalState()
        return self._kwargs['minimum_currency']

    minimum_currency = property(fget=get_minimum_currency)

    def get_maximum_currency(self):
        """Gets the maximum currency value.

        return: (osid.financials.Currency) - the maximum currency
        raise:  IllegalState - syntax is not a ``CURRENCY``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['CURRENCY']:
            raise errors.IllegalState()
        return self._kwargs['maximum_currency']

    maximum_currency = property(fget=get_maximum_currency)

    def get_currency_set(self):
        """Gets the set of acceptable currency values.

        return: (osid.financials.Currency) - a set of currencies or an
                empty array if not restricted
        raise:  IllegalState - syntax is not a ``CURRENCY``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['CURRENCY']:
            raise errors.IllegalState()
        return self._kwargs['currency_set']

    currency_set = property(fget=get_currency_set)

    def get_default_currency_values(self):
        """Gets the default currency values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (osid.financials.Currency) - the default currency values
        raise:  IllegalState - syntax is not a ``CURRENCY`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['CURRENCY']:
            raise errors.IllegalState()
        return self._kwargs['default_currency_values']

    default_currency_values = property(fget=get_default_currency_values)

    def get_existing_currency_values(self):
        """Gets the existing currency values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (osid.financials.Currency) - the existing currency
                values
        raise:  IllegalState - syntax is not a ``CURRENCY`` or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['CURRENCY']:
            raise errors.IllegalState()
        return self._kwargs['existing_currency_values']

    existing_currency_values = property(fget=get_existing_currency_values)

    def get_date_time_resolution(self):
        """Gets the smallest resolution of the date time value.

        return: (osid.calendaring.DateTimeResolution) - the resolution
        raise:  IllegalState - syntax is not a ``DATETIME, DURATION`` ,
                or ``TIME``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DATETIME,', 'DURATION', 'TIME']:
            raise errors.IllegalState()
        return self._kwargs['date_time_resolution']

    date_time_resolution = property(fget=get_date_time_resolution)

    def get_calendar_types(self):
        """Gets the set of acceptable calendar types.

        return: (osid.type.Type) - the set of calendar types
        raise:  IllegalState - syntax is not a ``DATETIME`` or
                ``DURATION``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DATETIME', 'DURATION']:
            raise errors.IllegalState()
        return self._kwargs['calendar_types']

    calendar_types = property(fget=get_calendar_types)

    @utilities.arguments_not_none
    def supports_calendar_type(self, calendar_type):
        """Tests if the given calendar type is supported.

        arg:    calendar_type (osid.type.Type): a calendar Type
        return: (boolean) - ``true`` if the type is supported, ``false``
                otherwise
        raise:  IllegalState - syntax is not a ``DATETIME`` or
                ``DURATION``
        raise:  NullArgument - ``calendar_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.supports_coordinate_type
        if self._kwargs['syntax'] not in ['``DATETIME``', '``DURATION``']:
            raise errors.IllegalState()
        return calendar_type in self.get_calendar_types

    def get_time_types(self):
        """Gets the set of acceptable time types.

        return: (osid.type.Type) - a set of time types or an empty array
                if not restricted
        raise:  IllegalState - syntax is not a ``DATETIME, DURATION,``
                or ``TIME``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DATETIME,', 'DURATION,', 'TIME']:
            raise errors.IllegalState()
        return self._kwargs['time_types']

    time_types = property(fget=get_time_types)

    @utilities.arguments_not_none
    def supports_time_type(self, time_type):
        """Tests if the given time type is supported.

        arg:    time_type (osid.type.Type): a time Type
        return: (boolean) - ``true`` if the type is supported, ``false``
                otherwise
        raise:  IllegalState - syntax is not a ``DATETIME, DURATION,``
                or ``TIME``
        raise:  NullArgument - ``time_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.supports_coordinate_type
        if self._kwargs['syntax'] not in ['``DATETIME,', 'DURATION,``', '``TIME``']:
            raise errors.IllegalState()
        return time_type in self.get_time_types

    def get_minimum_date_time(self):
        """Gets the minimum date time value.

        return: (osid.calendaring.DateTime) - the minimum value
        raise:  IllegalState - syntax is not a ``DATETIME``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DATETIME']:
            raise errors.IllegalState()
        return self._kwargs['minimum_date_time']

    minimum_date_time = property(fget=get_minimum_date_time)

    def get_maximum_date_time(self):
        """Gets the maximum date time value.

        return: (osid.calendaring.DateTime) - the maximum value
        raise:  IllegalState - syntax is not a ``DATETIME``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DATETIME']:
            raise errors.IllegalState()
        return self._kwargs['maximum_date_time']

    maximum_date_time = property(fget=get_maximum_date_time)

    def get_date_time_set(self):
        """Gets the set of acceptable date time values.

        return: (osid.calendaring.DateTime) - a set of values or an
                empty array if not restricted
        raise:  IllegalState - syntax is not a ``DATETIME``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DATETIME']:
            raise errors.IllegalState()
        return self._kwargs['date_time_set']

    date_time_set = property(fget=get_date_time_set)

    def get_default_date_time_values(self):
        """Gets the default date time values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (osid.calendaring.DateTime) - the default date time
                values
        raise:  IllegalState - syntax is not a ``DATETIME`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DATETIME']:
            raise errors.IllegalState()
        return self._kwargs['default_date_time_values']

    default_date_time_values = property(fget=get_default_date_time_values)

    def get_existing_date_time_values(self):
        """Gets the existing date time values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (osid.calendaring.DateTime) - the existing date time
                values
        raise:  IllegalState - syntax is not a ``DATETIME`` or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DATETIME']:
            raise errors.IllegalState()
        return self._kwargs['existing_date_time_values']

    existing_date_time_values = property(fget=get_existing_date_time_values)

    def get_decimal_scale(self):
        """Gets the number of digits to the right of the decimal point.

        return: (cardinal) - the scale
        raise:  IllegalState - syntax is not a ``DECIMAL``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DECIMAL']:
            raise errors.IllegalState()
        return self._kwargs['decimal_scale']

    decimal_scale = property(fget=get_decimal_scale)

    def get_minimum_decimal(self):
        """Gets the minimum decimal value.

        return: (decimal) - the minimum decimal
        raise:  IllegalState - syntax is not a ``DECIMAL``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DECIMAL']:
            raise errors.IllegalState()
        return self._kwargs['minimum_decimal']

    minimum_decimal = property(fget=get_minimum_decimal)

    def get_maximum_decimal(self):
        """Gets the maximum decimal value.

        return: (decimal) - the maximum decimal
        raise:  IllegalState - syntax is not a ``DECIMAL``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DECIMAL']:
            raise errors.IllegalState()
        return self._kwargs['maximum_decimal']

    maximum_decimal = property(fget=get_maximum_decimal)

    def get_decimal_set(self):
        """Gets the set of acceptable decimal values.

        return: (decimal) - a set of decimals or an empty array if not
                restricted
        raise:  IllegalState - syntax is not a ``DECIMAL``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DECIMAL']:
            raise errors.IllegalState()
        return self._kwargs['decimal_set']

    decimal_set = property(fget=get_decimal_set)

    def get_default_decimal_values(self):
        """Gets the default decimal values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (decimal) - the default decimal values
        raise:  IllegalState - syntax is not a ``DECIMAL`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DECIMAL']:
            raise errors.IllegalState()
        return self._kwargs['default_decimal_values']

    default_decimal_values = property(fget=get_default_decimal_values)

    def get_existing_decimal_values(self):
        """Gets the existing decimal values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (decimal) - the existing decimal values
        raise:  IllegalState - syntax is not a ``DECIMAL`` or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DECIMAL']:
            raise errors.IllegalState()
        return self._kwargs['existing_decimal_values']

    existing_decimal_values = property(fget=get_existing_decimal_values)

    def get_distance_resolution(self):
        """Gets the smallest resolution of the distance value.

        return: (osid.mapping.DistanceResolution) - the resolution
        raise:  IllegalState - syntax is not a ``DISTANCE``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DISTANCE']:
            raise errors.IllegalState()
        return self._kwargs['distance_resolution']

    distance_resolution = property(fget=get_distance_resolution)

    def get_minimum_distance(self):
        """Gets the minimum distance value.

        return: (osid.mapping.Distance) - the minimum value
        raise:  IllegalState - syntax is not a ``DISTANCE``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DISTANCE']:
            raise errors.IllegalState()
        return self._kwargs['minimum_distance']

    minimum_distance = property(fget=get_minimum_distance)

    def get_maximum_distance(self):
        """Gets the maximum distance value.

        return: (osid.mapping.Distance) - the maximum value
        raise:  IllegalState - syntax is not a ``DISTANCE``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DISTANCE']:
            raise errors.IllegalState()
        return self._kwargs['maximum_distance']

    maximum_distance = property(fget=get_maximum_distance)

    def get_distance_set(self):
        """Gets the set of acceptable distance values.

        return: (osid.mapping.Distance) - a set of values or an empty
                array if not restricted
        raise:  IllegalState - syntax is not a ``DISTANCE``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DISTANCE']:
            raise errors.IllegalState()
        return self._kwargs['distance_set']

    distance_set = property(fget=get_distance_set)

    def get_default_distance_values(self):
        """Gets the default distance values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (osid.mapping.Distance) - the default distance values
        raise:  IllegalState - syntax is not a ``DISTANCE`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DISTANCE']:
            raise errors.IllegalState()
        return self._kwargs['default_distance_values']

    default_distance_values = property(fget=get_default_distance_values)

    def get_existing_distance_values(self):
        """Gets the existing distance values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (osid.mapping.Distance) - the existing distance values
        raise:  IllegalState - syntax is not a ``DISTANCE`` or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DISTANCE']:
            raise errors.IllegalState()
        return self._kwargs['existing_distance_values']

    existing_distance_values = property(fget=get_existing_distance_values)

    def get_minimum_duration(self):
        """Gets the minimum duration.

        return: (osid.calendaring.Duration) - the minimum duration
        raise:  IllegalState - syntax is not a ``DURATION``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DURATION']:
            raise errors.IllegalState()
        return self._kwargs['minimum_duration']

    minimum_duration = property(fget=get_minimum_duration)

    def get_maximum_duration(self):
        """Gets the maximum duration.

        return: (osid.calendaring.Duration) - the maximum duration
        raise:  IllegalState - syntax is not a ``DURATION``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DURATION']:
            raise errors.IllegalState()
        return self._kwargs['maximum_duration']

    maximum_duration = property(fget=get_maximum_duration)

    def get_duration_set(self):
        """Gets the set of acceptable duration values.

        return: (osid.calendaring.Duration) - a set of durations or an
                empty array if not restricted
        raise:  IllegalState - syntax is not a ``DURATION``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DURATION']:
            raise errors.IllegalState()
        return self._kwargs['duration_set']

    duration_set = property(fget=get_duration_set)

    def get_default_duration_values(self):
        """Gets the default duration values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most at most a single value.

        return: (osid.calendaring.Duration) - the default duration
                values
        raise:  IllegalState - syntax is not a DURATION or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DURATION']:
            raise errors.IllegalState()
        return self._kwargs['default_duration_values']

    default_duration_values = property(fget=get_default_duration_values)

    def get_existing_duration_values(self):
        """Gets the existing duration values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (osid.calendaring.Duration) - the existing duration
                values
        raise:  IllegalState - syntax is not a ``DURATION`` or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['DURATION']:
            raise errors.IllegalState()
        return self._kwargs['existing_duration_values']

    existing_duration_values = property(fget=get_existing_duration_values)

    def get_heading_types(self):
        """Gets the set of acceptable heading types.

        return: (osid.type.Type) - a set of heading types or an empty
                array if not restricted
        raise:  IllegalState - syntax is not a ``HEADING``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['HEADING']:
            raise errors.IllegalState()
        return self._kwargs['heading_types']

    heading_types = property(fget=get_heading_types)

    @utilities.arguments_not_none
    def supports_heading_type(self, heading_type):
        """Tests if the given heading type is supported.

        arg:    heading_type (osid.type.Type): a heading Type
        return: (boolean) - ``true`` if the type is supported, ``false``
                otherwise
        raise:  IllegalState - syntax is not a ``HEADING``
        raise:  NullArgument - ``heading_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.supports_coordinate_type
        if self._kwargs['syntax'] not in ['``HEADING``']:
            raise errors.IllegalState()
        return heading_type in self.get_heading_types

    @utilities.arguments_not_none
    def get_axes_for_heading_type(self, heading_type):
        """Gets the number of axes for a given supported heading type.

        arg:    heading_type (osid.type.Type): a heading Type
        return: (cardinal) - the number of axes
        raise:  IllegalState - syntax is not a ``HEADING``
        raise:  NullArgument - ``heading_type`` is ``null``
        raise:  Unsupported - ``supports_heading_type(heading_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_minimum_heading_values(self, heading_type):
        """Gets the minimum heading values given supported heading type.

        arg:    heading_type (osid.type.Type): a heading Type
        return: (decimal) - the minimum heading values
        raise:  IllegalState - syntax is not a ``HEADING``
        raise:  NullArgument - ``heading_type`` is ``null``
        raise:  Unsupported - ``supports_heading_type(heading_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_maximum_heading_values(self, heading_type):
        """Gets the maximum heading values given supported heading type.

        arg:    heading_type (osid.type.Type): a heading Type
        return: (decimal) - the maximum heading values
        raise:  IllegalState - syntax is not a ``HEADING``
        raise:  NullArgument - ``heading_type`` is ``null``
        raise:  Unsupported - ``supports_heading_type(heading_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_heading_set(self):
        """Gets the set of acceptable heading values.

        return: (osid.mapping.Heading) - the set of heading
        raise:  IllegalState - syntax is not a ``HEADING``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['HEADING']:
            raise errors.IllegalState()
        return self._kwargs['heading_set']

    heading_set = property(fget=get_heading_set)

    def get_default_heading_values(self):
        """Gets the default heading values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (osid.mapping.Heading) - the default heading values
        raise:  IllegalState - syntax is not a ``HEADING`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['HEADING']:
            raise errors.IllegalState()
        return self._kwargs['default_heading_values']

    default_heading_values = property(fget=get_default_heading_values)

    def get_existing_heading_values(self):
        """Gets the existing heading values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (osid.mapping.Heading) - the existing heading values
        raise:  IllegalState - syntax is not a ``HEADING`` or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['HEADING']:
            raise errors.IllegalState()
        return self._kwargs['existing_heading_values']

    existing_heading_values = property(fget=get_existing_heading_values)

    def get_id_set(self):
        """Gets the set of acceptable ``Ids``.

        return: (osid.id.Id) - a set of ``Ids`` or an empty array if not
                restricted
        raise:  IllegalState - syntax is not an ``ID``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['ID']:
            raise errors.IllegalState()
        return self._kwargs['id_set']

    id_set = property(fget=get_id_set)

    def get_default_id_values(self):
        """Gets the default ``Id`` values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (osid.id.Id) - the default ``Id`` values
        raise:  IllegalState - syntax is not an ``ID`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['ID']:
            raise errors.IllegalState()
        return self._kwargs['default_id_values']

    default_id_values = property(fget=get_default_id_values)

    def get_existing_id_values(self):
        """Gets the existing ``Id`` values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (osid.id.Id) - the existing ``Id`` values
        raise:  IllegalState - syntax is not an ``ID``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['ID']:
            raise errors.IllegalState()
        return self._kwargs['existing_id_values']

    existing_id_values = property(fget=get_existing_id_values)

    def get_minimum_integer(self):
        """Gets the minimum integer value.

        return: (integer) - the minimum value
        raise:  IllegalState - syntax is not an ``INTEGER``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['INTEGER']:
            raise errors.IllegalState()
        return self._kwargs['minimum_integer']

    minimum_integer = property(fget=get_minimum_integer)

    def get_maximum_integer(self):
        """Gets the maximum integer value.

        return: (integer) - the maximum value
        raise:  IllegalState - syntax is not an ``INTEGER``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['INTEGER']:
            raise errors.IllegalState()
        return self._kwargs['maximum_integer']

    maximum_integer = property(fget=get_maximum_integer)

    def get_integer_set(self):
        """Gets the set of acceptable integer values.

        return: (integer) - a set of values or an empty array if not
                restricted
        raise:  IllegalState - syntax is not an ``INTEGER``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['INTEGER']:
            raise errors.IllegalState()
        return self._kwargs['integer_set']

    integer_set = property(fget=get_integer_set)

    def get_default_integer_values(self):
        """Gets the default integer values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (integer) - the default integer values
        raise:  IllegalState - syntax is not an ``INTEGER`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['INTEGER']:
            raise errors.IllegalState()
        return self._kwargs['default_integer_values']

    default_integer_values = property(fget=get_default_integer_values)

    def get_existing_integer_values(self):
        """Gets the existing integer values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (integer) - the existing integer values
        raise:  IllegalState - syntax is not a ``INTEGER`` or
                isValueKnown() is false
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['INTEGER']:
            raise errors.IllegalState()
        return self._kwargs['existing_integer_values']

    existing_integer_values = property(fget=get_existing_integer_values)

    def get_object_types(self):
        """Gets the set of acceptable ``Types`` for an arbitrary object.

        return: (osid.type.Type) - a set of ``Types`` or an empty array
                if not restricted
        raise:  IllegalState - syntax is not an ``OBJECT``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['OBJECT']:
            raise errors.IllegalState()
        return self._kwargs['object_types']

    object_types = property(fget=get_object_types)

    @utilities.arguments_not_none
    def supports_object_type(self, object_type):
        """Tests if the given object type is supported.

        arg:    object_type (osid.type.Type): an object Type
        return: (boolean) - ``true`` if the type is supported, ``false``
                otherwise
        raise:  IllegalState - syntax is not an ``OBJECT``
        raise:  NullArgument - ``object_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.supports_coordinate_type
        if self._kwargs['syntax'] not in ['``OBJECT``']:
            raise errors.IllegalState()
        return object_type in self.get_object_types

    def get_object_set(self):
        """Gets the set of acceptable object values.

        return: (object) - a set of values or an empty array if not
                restricted
        raise:  IllegalState - syntax is not an ``OBJECT``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['OBJECT']:
            raise errors.IllegalState()
        return self._kwargs['object_set']

    object_set = property(fget=get_object_set)

    def get_default_object_values(self):
        """Gets the default object values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (object) - the default object values
        raise:  IllegalState - syntax is not an ``OBJECT`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['OBJECT']:
            raise errors.IllegalState()
        return self._kwargs['default_object_values']

    default_object_values = property(fget=get_default_object_values)

    def get_existing_object_values(self):
        """Gets the existing object values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (object) - the existing object values
        raise:  IllegalState - syntax is not an OBJECT or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['OBJECT']:
            raise errors.IllegalState()
        return self._kwargs['existing_object_values']

    existing_object_values = property(fget=get_existing_object_values)

    def get_spatial_unit_record_types(self):
        """Gets the set of acceptable spatial unit record types.

        return: (osid.type.Type) - the set of spatial unit types
        raise:  IllegalState - syntax is not ``SPATIALUNIT``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['SPATIALUNIT']:
            raise errors.IllegalState()
        return self._kwargs['spatial_unit_record_types']

    spatial_unit_record_types = property(fget=get_spatial_unit_record_types)

    @utilities.arguments_not_none
    def supports_spatial_unit_record_type(self, spatial_unit_record_type):
        """Tests if the given spatial unit record type is supported.

        arg:    spatial_unit_record_type (osid.type.Type): a spatial
                unit record Type
        return: (boolean) - ``true`` if the type is supported, ``false``
                otherwise
        raise:  IllegalState - syntax is not an ``SPATIALUNIT``
        raise:  NullArgument - ``spatial_unit_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.supports_coordinate_type
        if self._kwargs['syntax'] not in ['``SPATIALUNIT``']:
            raise errors.IllegalState()
        return spatial_unit_record_type in self.get_spatial_unit_record_types

    def get_spatial_unit_set(self):
        """Gets the set of acceptable spatial unit values.

        return: (osid.mapping.SpatialUnit) - a set of spatial units or
                an empty array if not restricted
        raise:  IllegalState - syntax is not a ``SPATIALUNIT``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['SPATIALUNIT']:
            raise errors.IllegalState()
        return self._kwargs['spatial_unit_set']

    spatial_unit_set = property(fget=get_spatial_unit_set)

    def get_default_spatial_unit_values(self):
        """Gets the default spatial unit values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (osid.mapping.SpatialUnit) - the default spatial unit
                values
        raise:  IllegalState - syntax is not a ``SPATIALUNIT`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['SPATIALUNIT']:
            raise errors.IllegalState()
        return self._kwargs['default_spatial_unit_values']

    default_spatial_unit_values = property(fget=get_default_spatial_unit_values)

    def get_existing_spatial_unit_values(self):
        """Gets the existing spatial unit values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (osid.mapping.SpatialUnit) - the existing spatial unit
                values
        raise:  IllegalState - syntax is not a SPATIALUNIT or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['SPATIALUNIT']:
            raise errors.IllegalState()
        return self._kwargs['existing_spatial_unit_values']

    existing_spatial_unit_values = property(fget=get_existing_spatial_unit_values)

    def get_minimum_speed(self):
        """Gets the minimum speed value.

        return: (osid.mapping.Speed) - the minimum speed
        raise:  IllegalState - syntax is not a ``SPEED``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['SPEED']:
            raise errors.IllegalState()
        return self._kwargs['minimum_speed']

    minimum_speed = property(fget=get_minimum_speed)

    def get_maximum_speed(self):
        """Gets the maximum speed value.

        return: (osid.mapping.Speed) - the maximum speed
        raise:  IllegalState - syntax is not a ``SPEED``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['SPEED']:
            raise errors.IllegalState()
        return self._kwargs['maximum_speed']

    maximum_speed = property(fget=get_maximum_speed)

    def get_speed_set(self):
        """Gets the set of acceptable speed values.

        return: (osid.mapping.Speed) - a set of speeds or an empty array
                if not restricted
        raise:  IllegalState - syntax is not a ``SPEED``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['SPEED']:
            raise errors.IllegalState()
        return self._kwargs['speed_set']

    speed_set = property(fget=get_speed_set)

    def get_default_speed_values(self):
        """Gets the default speed values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (osid.mapping.Speed) - the default speed values
        raise:  IllegalState - syntax is not a ``SPEED`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['SPEED']:
            raise errors.IllegalState()
        return self._kwargs['default_speed_values']

    default_speed_values = property(fget=get_default_speed_values)

    def get_existing_speed_values(self):
        """Gets the existing speed values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (osid.mapping.Speed) - the existing speed values
        raise:  IllegalState - syntax is not a ``SPEED`` or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['SPEED']:
            raise errors.IllegalState()
        return self._kwargs['existing_speed_values']

    existing_speed_values = property(fget=get_existing_speed_values)

    def get_minimum_string_length(self):
        """Gets the minimum string length.

        return: (cardinal) - the minimum string length
        raise:  IllegalState - syntax is not a ``STRING``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['STRING']:
            raise errors.IllegalState()
        return self._kwargs['minimum_string_length']

    minimum_string_length = property(fget=get_minimum_string_length)

    def get_maximum_string_length(self):
        """Gets the maximum string length.

        return: (cardinal) - the maximum string length
        raise:  IllegalState - syntax is not a ``STRING``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['STRING']:
            raise errors.IllegalState()
        return self._kwargs['maximum_string_length']

    maximum_string_length = property(fget=get_maximum_string_length)

    def get_string_match_types(self):
        """Gets the set of valid string match types for use in validating a string.

        If the string match type indicates a regular expression then
        ``get_string_expression()`` returns a regular expression.

        return: (osid.type.Type) - the set of string match types
        raise:  IllegalState - syntax is not a ``STRING``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['STRING']:
            raise errors.IllegalState()
        return self._kwargs['string_match_types']

    string_match_types = property(fget=get_string_match_types)

    @utilities.arguments_not_none
    def supports_string_match_type(self, string_match_type):
        """Tests if the given string match type is supported.

        arg:    string_match_type (osid.type.Type): a string match type
        return: (boolean) - ``true`` if the given string match type Is
                supported, ``false`` otherwise
        raise:  IllegalState - syntax is not a ``STRING``
        raise:  NullArgument - ``string_match_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.supports_coordinate_type
        if self._kwargs['syntax'] not in ['``STRING``']:
            raise errors.IllegalState()
        return string_match_type in self.get_string_match_types

    @utilities.arguments_not_none
    def get_string_expression(self, string_match_type):
        """Gets the regular expression of an acceptable string for the given string match type.

        arg:    string_match_type (osid.type.Type): a string match type
        return: (string) - the regular expression
        raise:  NullArgument - ``string_match_type`` is ``null``
        raise:  IllegalState - syntax is not a ``STRING``
        raise:  Unsupported -
                ``supports_string_match_type(string_match_type`` ) is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_string_format_types(self):
        """Gets the set of valid string formats.

        return: (osid.type.Type) - the set of valid text format types
        raise:  IllegalState - syntax is not a ``STRING``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['STRING']:
            raise errors.IllegalState()
        return self._kwargs['string_format_types']

    string_format_types = property(fget=get_string_format_types)

    def get_string_set(self):
        """Gets the set of acceptable string values.

        return: (string) - a set of strings or an empty array if not
                restricted
        raise:  IllegalState - syntax is not a ``STRING``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['STRING']:
            raise errors.IllegalState()
        return self._kwargs['string_set']

    string_set = property(fget=get_string_set)

    def get_default_string_values(self):
        """Gets the default string values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (string) - the default string values
        raise:  IllegalState - syntax is not a ``STRING`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['STRING']:
            raise errors.IllegalState()
        return self._kwargs['default_string_values']

    default_string_values = property(fget=get_default_string_values)

    def get_existing_string_values(self):
        """Gets the existing string values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (string) - the existing string values
        raise:  IllegalState - syntax is not a ``STRING`` or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['STRING']:
            raise errors.IllegalState()
        return self._kwargs['existing_string_values']

    existing_string_values = property(fget=get_existing_string_values)

    def get_minimum_time(self):
        """Gets the minimum time value.

        return: (osid.calendaring.Time) - the minimum time
        raise:  IllegalState - syntax is not a ``TIME``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['TIME']:
            raise errors.IllegalState()
        return self._kwargs['minimum_time']

    minimum_time = property(fget=get_minimum_time)

    def get_maximum_time(self):
        """Gets the maximum time value.

        return: (osid.calendaring.Time) - the maximum time
        raise:  IllegalState - syntax is not a ``TIME``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['TIME']:
            raise errors.IllegalState()
        return self._kwargs['maximum_time']

    maximum_time = property(fget=get_maximum_time)

    def get_time_set(self):
        """Gets the set of acceptable time values.

        return: (osid.calendaring.Time) - a set of times or an empty
                array if not restricted
        raise:  IllegalState - syntax is not a ``TIME``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['TIME']:
            raise errors.IllegalState()
        return self._kwargs['time_set']

    time_set = property(fget=get_time_set)

    def get_default_time_values(self):
        """Gets the default time values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (osid.calendaring.Time) - the default time values
        raise:  IllegalState - syntax is not a ``TIME`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['TIME']:
            raise errors.IllegalState()
        return self._kwargs['default_time_values']

    default_time_values = property(fget=get_default_time_values)

    def get_existing_time_values(self):
        """Gets the existing time values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (osid.calendaring.Time) - the existing time values
        raise:  IllegalState - syntax is not a ``TIME`` or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['TIME']:
            raise errors.IllegalState()
        return self._kwargs['existing_time_values']

    existing_time_values = property(fget=get_existing_time_values)

    def get_type_set(self):
        """Gets the set of acceptable ``Types``.

        return: (osid.type.Type) - a set of ``Types`` or an empty array
                if not restricted
        raise:  IllegalState - syntax is not a ``TYPE``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['TYPE']:
            raise errors.IllegalState()
        return self._kwargs['type_set']

    type_set = property(fget=get_type_set)

    def get_default_type_values(self):
        """Gets the default type values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (osid.type.Type) - the default type values
        raise:  IllegalState - syntax is not a ``TYPE`` or
                ``is_required()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['TYPE']:
            raise errors.IllegalState()
        return self._kwargs['default_type_values']

    default_type_values = property(fget=get_default_type_values)

    def get_existing_type_values(self):
        """Gets the existing type values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (osid.type.Type) - the existing type values
        raise:  IllegalState - syntax is not a ``TYPE`` or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['TYPE']:
            raise errors.IllegalState()
        return self._kwargs['existing_type_values']

    existing_type_values = property(fget=get_existing_type_values)

    def get_version_types(self):
        """Gets the set of acceptable version types.

        return: (osid.type.Type) - the set of version types
        raise:  IllegalState - syntax is not a ``VERSION``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['VERSION']:
            raise errors.IllegalState()
        return self._kwargs['version_types']

    version_types = property(fget=get_version_types)

    @utilities.arguments_not_none
    def supports_version_type(self, version_type):
        """Tests if the given version type is supported.

        arg:    version_type (osid.type.Type): a version Type
        return: (boolean) - ``true`` if the type is supported, ``false``
                otherwise
        raise:  IllegalState - syntax is not a ``VERSION``
        raise:  NullArgument - ``version_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.supports_coordinate_type
        if self._kwargs['syntax'] not in ['``VERSION``']:
            raise errors.IllegalState()
        return version_type in self.get_version_types

    def get_minimum_version(self):
        """Gets the minumim acceptable ``Version``.

        return: (osid.installation.Version) - the minumim ``Version``
        raise:  IllegalState - syntax is not a ``VERSION``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['VERSION']:
            raise errors.IllegalState()
        return self._kwargs['minimum_version']

    minimum_version = property(fget=get_minimum_version)

    def get_maximum_version(self):
        """Gets the maximum acceptable ``Version``.

        return: (osid.installation.Version) - the maximum ``Version``
        raise:  IllegalState - syntax is not a ``VERSION``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['VERSION']:
            raise errors.IllegalState()
        return self._kwargs['maximum_version']

    maximum_version = property(fget=get_maximum_version)

    def get_version_set(self):
        """Gets the set of acceptable ``Versions``.

        return: (osid.installation.Version) - a set of ``Versions`` or
                an empty array if not restricted
        raise:  IllegalState - syntax is not a ``VERSION``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['VERSION']:
            raise errors.IllegalState()
        return self._kwargs['version_set']

    version_set = property(fget=get_version_set)

    def get_default_version_values(self):
        """Gets the default version values.

        These are the values used if the element value is not provided
        or is cleared. If ``is_array()`` is false, then this method
        returns at most a single value.

        return: (osid.installation.Version) - the default version values
        raise:  IllegalState - syntax is not a TIME or isValueKnown() is
                false
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['TIME']:
            raise errors.IllegalState()
        return self._kwargs['default_version_values']

    default_version_values = property(fget=get_default_version_values)

    def get_existing_version_values(self):
        """Gets the existing version values.

        If ``has_value()`` and ``is_required()`` are ``false,`` then
        these values are the default values ````. If ``is_array()`` is
        false, then this method returns at most a single value.

        return: (osid.installation.Version) - the existing version
                values
        raise:  IllegalState - syntax is not a ``VERSION`` or
                ``is_value_known()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.Metadata.get_minimum_cardinal
        if self._kwargs['syntax'] not in ['VERSION']:
            raise errors.IllegalState()
        return self._kwargs['existing_version_values']

    existing_version_values = property(fget=get_existing_version_values)


