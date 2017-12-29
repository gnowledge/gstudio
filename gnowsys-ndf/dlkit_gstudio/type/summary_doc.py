# -*- coding: utf-8 -*-
"""Type Open Service Interface Definitions
type version 3.0.0

The Type OSID defines a set of interfaces for managing ``Type``
definitions. ``Types`` are used as an identifier primarily for
identification of interface extensions throughout the OSIDs and
occasionally used as an extensible enumeration. An agreement between an
OSID Consumer and an OSID Provider means they support the same ``Type``.

Types

A ``Type`` is similar to an Id but includes other data for display and
organization. The identification portion of the Type is globally unique
and contains:

  * authority: the name of the entity or organization responsible for
    the type. Using a domain name is a reasonable convention.
  * identifier: a string serving as an id. The identifier may be a urn,
    guid, oid or some other means of identification. Since all of the
    identification elements including the domain and authority create an
    overall unique Type, the identifier may even be a sequence number
    defined within a particular domain.
  * namespace: a string identifying the namespace of the identifier,
    such as "urn" or "oid".


Example
  Type type = lookupSession.getType("asset", "uri",         
                                    "http://harvestroad.com/osidTypes/image",
                                    "harvestroad.com");
  print type.getDisplayName();



The sessions in this OSID offer the capabilities of a ``Type`` registry
to centrally manage definitions and localized display strings and
descriptions. Applications may opt to construct their own ``Types``
directly and bypass this service.

Type Hierarchies

Types are part of an internal hierarchy. A ``Type`` in a hierarchy
includes the ``Types`` of its children. For example, an ``Asset`` may
have a "photograph" ``Type`` included as part of an "image" base
``Type``.

Unless an application will display a type, it can simply construct a
type based on the identification components. OSID Providers may benefit
by using this service to manage the type hierarchy, to provide a place
to perform mappings across different type definitions, and to provide
displayable metadata to its consumers.

Type Type Relations

``Types`` may relate to other ``Types`` to describe constraints or
compositions. The relationship is expressed as another Type. For
example, a ``Position`` of type "researcher" may be appropriately
associated with an ``Organization`` of type "laboratory" using a
relation Type of "allowed." Or, a root ``Event`` type depends on a root
``TimePeriod`` type using a relationship type of "depends on."

Types for Constraints and Side Effects

An OSID Provider may link a ``Type,`` such as a genus, to a set of
constraints that are made known to the application as ``Metadata``
through an ``OsidForm``. Types of an ``OsidObject`` may also be used by
an OSID Provider to constrain the possible relationship ``Types`` that
may be possible to that ``OsidObject``. In these uses of ``Types,``
there is a semantic accompanying the ``Type`` definition managed within
an OSID Provider. The Type OSID manages the metadata of the ``Type``
itself. Logic implementing the meaning of the ``Type`` is managed
completely within an OSID Provider.

OSIDs emphasize relationships over data typing since type agreements are
often an impediment to interoperability. Generally, the rule of thumb
for record ``Types`` is to first explore other ``OsidObjects,`` even
those in other OSIDs for a place for extra data. Often, what is hiding
behind a list of data elements is a separate service that can be
provided as a separate module and serves to keep the principal
``OsidObject`` lighter and more flexible.

Genus ``Types`` primarily serve as a quick and dirty way to unclutter
the record ``Types`` with "is kind of like" tags. ``OsidCatalogs`` can
be used for a richer solution. For example, a genus ``Type`` may be used
to identify all ``Events`` on a ``Calendar`` which are classes at a
school and is accompanied by constraint logic such that the ``Events``
occur at a ``Location`` on campus.

Another pathway to explore is to create a smart ``Calendar`` from an
``EventQuery`` that specifies constrraints on the ``Event`` sponsor,
``Location,`` or other data required for classes. Creates and updates
for Events in that smart ``Calendar`` will be similarly constrained and
surfaced to the OSID Consumer through the ``Metadata`` in the
EventForms. While this path is certainly more difficult than simply
nailing up some logic indexed by a genus Type, it can be considered if
there is a need to expose the logic and authoring capabilities.

OsidPrimitives

Most OSID interfaces are used to encapsulate implementation-specific
objects from provider to consumer. ``Type`` is an ``OsidPrimitive`` and
as such cannot be used to encapsulate implementation-specific data other
than what is defined explicitly in the ``Type``. An OSID Provider must
respect any ``Type`` constructed by an OSID Consumer.

"""
