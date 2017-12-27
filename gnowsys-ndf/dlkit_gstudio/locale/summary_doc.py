# -*- coding: utf-8 -*-
# pylint: skip-file

"""
Locale Open Service Interface Definitions
locale version 3.0.0

The Locale OSID provides the service of localizing applications defining
interfaces for string translation, measurement unit conversion, calendar
conversion, spatial conversion, and currency conversion.

String Translation

The Locale OSID can access and manage string translations using the
``TranslationSession`` and ``TranslationAdminSession`` respectively.
Translations map a pair of strings with language and script Types. The
translation services provide a simple means for an OSID Consumer to
localize known display strings for an application.

Numeric Formatting

The ``NumericFormattingSession`` provides the service of converting
numbers to display strings and parsing display strings into numbers. The
format of the display string is identified by a numeric format ``Type``.
It supports the various numeric types defined among OSID Primitives such
as integers, decimals, and cardinal numbers.

Calendar Formatting

The ``CalendarFormattingSession`` converts ``DateTime`` and ``Time``
OSID Primitives to display strings and parses display strings back into
``DateTimes`` and ``Times``. The display string formats are specified by
a date format ``Type`` and time format ``Type`` respectively. The
calendaring and time systems implemented by ``DateTime`` and ``Time``
are specified by a calendar ``Type`` and time ``Type``. Conversions
among calendaring systems are performed using the
``CalendarConversionSession``.

Currency Formatting

The ``CurrencyFormattingSession`` converts currency amounts to display
strings and parses display strings into currency amounts. The format of
the display string is identified by both a currency and a numeric format
``Type``. Conversions among currencies are performed using the
``CurrencyConversionSession``.

Coordinate Formatting

The ``CoordinateFormattingSession`` converts ``Coordinate`` OSID
Primitives to display strings and parses display strings back into
``Coordinates``. The display string formats are specified by a
coordinate format ``Type``. The coordinate data is identified by the
coordinate record ``Type``. Conversions among calendaring systems are
performed using the ``CoordinateConversionSession``.

Unit Conversion

The ``UnitConversionSession`` converts units of measurement among unit
types. The unit types may represent different units within the same
system of measurement or units among different measurement systems where
a conversion exists.

Currency Conversion

The ``CurrencyConversionSession`` converts a currency amount from one
currency system to another where a means for transforming the currency
values exists.

Spatial Unit Conversion

The ``SpatialUnitConversionSession`` converts a spatial units from one
spatial system to another where a means for transforming the spatial
units exists.

Text Format Conversion

The ``FormatConversionSession`` converts text from one format to
another.



Informational Objects

The Locale OSID includes a ``CalendarInfo`` and ``TimeInfo`` interfaces
for inspecting the details of the respective ``Types`` to assist in
displaying calendars and clocks without knowledge of the specific
system.

The ``Locale`` interface defines a set of types that together define the
formatting, language, calendaring, and currency for a locale or culture.
Locale is referenced in OsidSessions to convey the localization of the
service.

"""
