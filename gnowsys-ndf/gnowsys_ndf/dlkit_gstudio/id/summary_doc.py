# -*- coding: utf-8 -*-
"""Id Open Service Interface Definitions
id version 3.0.0

The Id OSID provides the means for creating and mapping identifiers. All
OSID objects are identified by a unique and immutable ``Id``. The ``Id``
OSID can be used to generate new ``Ids`` when creating new objects.

Consumers wishing to persist an OSID object should instead persist the
reference to the object by serializing the ``Id``.

Most OSID interfaces are used to encapsulate implementation-specific
objects from provider to consumer. ``Id`` is an ``OsidPrimitive`` and as
such cannot be used to encapsulate implementation-specific data other
than what is defined explicitly in the ``Id``. An OSID Provider must
respect any ``Id`` based on its interface alone.

The Id service can be used to assign Ids for an OSID Provider or be used
to manage Id translations for system to system compatibility.

The ``Id`` service can also be used as a means to map one identifier to
another when an object is known by multiple identifiers. Mapping
identifier spaces is often a critical part of interoperability and the
Id service can be used as a shim to bridge different systems.

Id Mapping Example
  public Asset getAsset(assetId) {
      Id id = idSession.getId(assetId);
      return (other_impl.getAsset(assetId));
  }



"""
