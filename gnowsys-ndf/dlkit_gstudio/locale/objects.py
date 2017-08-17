"""Mongodb implementations of locale objects."""

# pylint: disable=no-init
#     Numerous classes don't require __init__.
# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=protected-access
#     Access to protected methods allowed in package mongo package scope
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification







from .. import utilities
from ...abstract_osid.locale import objects as abc_locale_objects
from ..osid import objects as osid_objects
from ..primitives import Type
from dlkit.abstract_osid.osid import errors
from dlkit.primordium.locale.types import calendar
from dlkit.primordium.locale.types import calendar_format
from dlkit.primordium.locale.types import coordinate_format
from dlkit.primordium.locale.types import currency
from dlkit.primordium.locale.types import currency_format
from dlkit.primordium.locale.types import language
from dlkit.primordium.locale.types import numeric_format
from dlkit.primordium.locale.types import script
from dlkit.primordium.locale.types import time
from dlkit.primordium.locale.types import time_format
from dlkit.primordium.locale.types import unit_system




class Locale(abc_locale_objects.Locale):
    """A locale is a collection of types.

    ``Locale`` defines a set of types that together define the
    formatting, language, calendaring, and currency for a locale or
    culture.

    """

    ##
    # This constructor should probably be referencing a locale settings
    # module for default values?
    def __init__(self,
                 language_type_identifier='ENG',
                 script_type_identifier='LATN',
                 calendar_type_identifier='ISO_8601',
                 time_type_identifier='UTC',
                 currency_type_identifier='USD',
                 unit_system_type_identifier='ENGLISH',
                 numeric_format_type_identifier='F8.2',
                 calendar_format_type_identifier='MMDDYYYY',
                 time_format_type_identifier='HHMMSS',
                 currency_format_type_identifier='US',
                 coordinate_format_type_identifier='DMS'):

        self._language_type_identifier = language_type_identifier
        self._script_type_identifier = script_type_identifier
        self._calendar_type_identifier = calendar_type_identifier
        self._time_type_identifier = time_type_identifier
        self._currency_type_identifier = currency_type_identifier
        self._unit_system_type_identifier = unit_system_type_identifier
        self._numeric_format_type_identifier = numeric_format_type_identifier
        self._calendar_format_type_identifier = calendar_format_type_identifier
        self._time_format_type_identifier = time_format_type_identifier
        self._currency_format_type_identifier = currency_format_type_identifier
        self._coordinate_format_type_identifier = coordinate_format_type_identifier

    def get_language_type(self):
        """Gets the language ``Type``.

        return: (osid.type.Type) - the language type
        *compliance: mandatory -- This method must be implemented.*

        """
        return Type(**language.get_type_data(self._language_type_identifier))

    language_type = property(fget=get_language_type)

    def get_script_type(self):
        """Gets the script ``Type``.

        return: (osid.type.Type) - the script type
        *compliance: mandatory -- This method must be implemented.*

        """
        return Type(**script.get_type_data(self._script_type_identifier))

    script_type = property(fget=get_script_type)

    def get_calendar_type(self):
        """Gets the calendar ``Type``.

        return: (osid.type.Type) - the calendar type
        *compliance: mandatory -- This method must be implemented.*

        """
        return Type(**calendar.get_type_data(self._calendar_type_identifier))

    calendar_type = property(fget=get_calendar_type)

    def get_time_type(self):
        """Gets the time ``Type``.

        return: (osid.type.Type) - the time type
        *compliance: mandatory -- This method must be implemented.*

        """
        return Type(**time.get_type_data(self._time_type_identifier))

    time_type = property(fget=get_time_type)

    def get_currency_type(self):
        """Gets the currency ``Type``.

        return: (osid.type.Type) - the currency type
        *compliance: mandatory -- This method must be implemented.*

        """
        return Type(**currency.get_type_data(self._currency_type_identifier))

    currency_type = property(fget=get_currency_type)

    def get_unit_system_type(self):
        """Gets the unit system ``Type``.

        return: (osid.type.Type) - the unit system type
        *compliance: mandatory -- This method must be implemented.*

        """
        return Type(**unit_system.get_type_data(self._unit_system_type_identifier))

    unit_system_type = property(fget=get_unit_system_type)

    def get_numeric_format_type(self):
        """Gets the numeric format ``Type``.

        return: (osid.type.Type) - the numeric format type
        *compliance: mandatory -- This method must be implemented.*

        """
        return Type(**numeric_format.get_type_data(self._numeric_format_type_identifier))

    numeric_format_type = property(fget=get_numeric_format_type)

    def get_calendar_format_type(self):
        """Gets the calendar format ``Type``.

        return: (osid.type.Type) - the calendar format type
        *compliance: mandatory -- This method must be implemented.*

        """
        return Type(**calendar_format.get_type_data(self._calendar_format_type_identifier))

    calendar_format_type = property(fget=get_calendar_format_type)

    def get_time_format_type(self):
        """Gets the time format ``Type``.

        return: (osid.type.Type) - the time format type
        *compliance: mandatory -- This method must be implemented.*

        """
        return Type(**time_format.get_type_data(self._time_format_type_identifier))

    time_format_type = property(fget=get_time_format_type)

    def get_currency_format_type(self):
        """Gets the currency format ``Type``.

        return: (osid.type.Type) - the currency format type
        *compliance: mandatory -- This method must be implemented.*

        """
        return Type(**currency_format.get_type_data(self._currency_format_type_identifier))

    currency_format_type = property(fget=get_currency_format_type)

    def get_coordinate_format_type(self):
        """Gets the coordinate format ``Type``.

        return: (osid.type.Type) - the coordinate format type
        *compliance: mandatory -- This method must be implemented.*

        """
        return Type(**coordinate_format.get_type_data(self._coordinate_format_type_identifier))

    coordinate_format_type = property(fget=get_coordinate_format_type)


class LocaleList(abc_locale_objects.LocaleList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``LocaleList`` provides a means for accessing ``Locale`` elements sequentially either one at a time or many at a time.

    Examples: while (ll.hasNext()) { Locale locale = ll.getNextLocale();
    }

    or
      while (ll.hasNext()) {
           Locale[] locales = ll.getNextLocales(ll.available());
      }



    """

    def get_next_locale(self):
        """Gets the next ``Locale`` in this list.

        return: (osid.locale.Locale) - the next ``Locale`` in this list.
                The ``has_next()`` method should be used to test that a
                next ``Locale`` is available before calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        try:
            next_item = self.next()
        except StopIteration:
            raise errors.IllegalState('no more elements available in this list')
        except: #Need to specify exceptions here
            raise errors.OperationFailed()
        else:
            return next_item

    def next(self):
        next_item = osid_objects.OsidList.next(self)
        return Locale(next_item)

    next_locale = property(fget=get_next_locale)

    @utilities.arguments_not_none
    def get_next_locales(self, n):
        """Gets the next set of ``Locale`` elements in this list.

        The specified amount must be less than or equal to the return
        from ``available()``.

        arg:    n (cardinal): the number of ``Locale`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.locale.Locale) - an array of ``Locale``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
    # Implemented from template for osid.resource.ResourceList.get_next_resources
        if n > self.available():
            # !!! This is not quite as specified (see method docs) !!!
            raise errors.IllegalState('not enough elements available in this list')
        else:
            next_list = []
            i = 0
            while i < n:
                try:
                    next_list.append(self.next())
                except StopIteration:
                    break
                i += 1
            return next_list


