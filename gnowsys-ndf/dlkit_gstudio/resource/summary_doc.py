# -*- coding: utf-8 -*-
"""Resource Open Service Interface Definitions
resource version 3.0.0

The Resource OSID defines a service to access and manage a directory of
objects.

Resources

``Resources`` may represent people, places or a set or arbitrary
entities that are used throughout the OSIDs as references to indirect
objects. In core OSID, ``Resources`` have no other meaning other than to
provide an identifier and a relation to an authentication principal.
``Resource``  ``Types`` may define extra data to define an employee,
organizational unit or an inventory item.

``Resources`` are referenced throughout the OSIDs to and the abstraction
level of this service provides a consistent interface with which to
access and manage object references not directly pertinent to the
service in play. For example, a Repository OSID may reference
``Resources`` as authors or a Course OSID may reference ``Resources``
for students and instructors. Each of these OSIDs may orchestrate a
Resource OSID to provide management of the set of referenced resources.

A ``Resource`` genus Type may be used to provide a label the kind of
resource. This service offers the flexibility that the producer of a
film may be a person, a production company, or a fire hydrant. While
genus ``Types`` may be used to constrain the kinds of ``Resources`` that
may be related to various ``OsidObjects`` if necessary ``,`` OSID
Consumers are expected to simply use the Resource as a reference. If an
OSID Consumer wishes to provide a mechanism for updating a ``Resource``
referenced, the OSID Consumer should use an orchestrated Resource OSID.

Agents

A ``Resource`` also provides the mapping between an authentication
``Agent`` and the entity on whose behalf the agent is acting. An
``Agent`` can only map to a single ``Resource`` while a ``Resource`` can
have multiple ``Agents``. An agent that represents the unix login of
"vijay" on server due.mit.edu can map to a ``Resource`` representing
Vijay Kumar, who may also have a campus agent of "vkumar@mit.edu."

Group

When a ``Resource`` is referenced in another OSID, it is a singular
entity. To provide groupings of multiple people or things, a
``Resource`` can also be defined as a hierarchical group of other
resources. Whether a resource is a single entity or a group is an
attribute of the ``Resource`` itself. If a ``Resource`` is a group, then
its membership can be queried or managed in one of the group sessions.
This overloading of the object definition serves to keep the nature of
the resource separate from the other OSIDs such that a message to a
"group", for example, is referenced as a single resource receipient.
Other OSIDs are blind to whether or not a referenced ``Resource`` is a
group or a singular entity..

Resource Relationships

For kicks, ``Resources`` may have arbitrrary relationships to other
``Resources`` using the ``ResourceRelationship`` interface. Resource
relationships may also be used to provide a place to describe in more
detail, or hang data, on a member to group relationship.

Bin Cataloging

``Resources`` may be mapped into hierarchial ``Bins`` for the purpose of
cataloging or federation.

Sub Packages

The Resource OSID includes a Resource Demographic OSID for managing
dynamically generated populations of ``Resources`` and a Resource Batch
OSID for managing ``Resources`` in bulk.

"""
