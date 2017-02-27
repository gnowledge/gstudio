# -*- coding: utf-8 -*-
"""Hierarchy Open Service Interface Definitions
hierarchy version 3.0.0

The Hierarchy OSID is an auxiliary service providing a means for
accessing and managing hierarchical relationships among OSID ``Ids``.

An OSID ``Id`` may have onr or more parents or children and the
hierarchy itself represents a directed acyclic graph. The hierarchy
service defines a set of interfaces used among other OSIDs that utilize
hierarchies and can also be used to abstract hierarchical data into a
standalone service.

Hierarchical queries may be performed using the
``HierarchyTraversalSession``. A set of methods exist to query parents,
children, ancestors, and decendants. A Node structure may be retrieved
to access a portion of a hierarchy in bulk. The ``Node`` provides
methods to get parents and children of the node directly.

Hierarchies are federateable by combining nodes. There is no hierarchy
service for the hierarchy catalog.

"""
