# -*- coding: utf-8 -*-
"""Relationship Open Service Interface Definitions
relationship version 3.0.0

The Relationship OSID provides the ability to relate and manage data
between ``OsidObjects``.

Relationships

The Relationship OSID defines a ``Relationship`` that can be used to
explicitly identify a relationship between two OSID ``Ids`` and manage
information specific to the relationship.

The Relationship OSID is a building block on which relationships defined
in the context of other OSIDs can be built. Examples of relationships
include the enrollment record of a student in a ``Course`` or the
commitment or a person to an ``Event``.

The Relationship OSID depends on the relationship Type to indicate the
nature of the relationship including its natural ordering between the
source and destination ``Ids``. A relationship of type "friend" may
place the peers in either order and be queryable in either order. A
relationship of type "parent" is between a father peer and a son peer,
but not the other way around. Queries of the son peer based on the
"parent" type is not equiavelent to queries of the father peer based on
the "parent" type.

Such directional relationships may be accompanied by two types. An
additional relationship type of "child" can be used with the son peer to
determine the father peer. The directionality and the inverse among the
types are part of the type definition.

Family Cataloging

``Relationships`` may be cataloged using the ``Family`` interface.

Sub Packages

The Relationship OSID includes a Relationship Rules OSID for controlling
the enable status of ``Relationships``.

"""
