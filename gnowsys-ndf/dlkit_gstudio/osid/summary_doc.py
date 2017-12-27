# -*- coding: utf-8 -*-
"""Core Service Interface Definitions
osid version 3.0.0

The Open Service Interface Definitions (OSIDs) is a service-based
architecture to promote software interoperability. The OSIDs are a large
suite of interface contract specifications that describe the integration
points among services and system components for the purpose of creating
choice among a variety of different and independently developed
applications and systems, allowing independent evolution of software
components within a complex system, and federated service providers.

The OSIDs were initially developed in 2001 as part of the MIT Open
Knowledge Initiative Project funded by the Andrew W. Mellon Foundation
to provide an architecture for higher education learning systems. OSID
3K development began in 2006 to redesign the capabilities of the
specifications to apply to a much broader range of service domains and
integration challenges among both small and large-scale enterprise
systems.

The ``osid`` package defines the building blocks for the OSIDs which are
defined in packages for their respective services. This package defines
the top-level interfaces used by all the OSIDs as well as specification
metadata and the OSID Runtime interface.

Meta Interfaces and Enumerations

  * ``OSID:`` an enumeration listing the OSIDs defined in the
    specification.
  * ``Syntax:`` an enumeration listing primitive types
  * ``Metadata:`` an interface for describing data constraints on a data
    element


Interface Behavioral Markers

Interface behavioral markers are used to tag a behavioral pattern of the
interface used to construct other object interfaces.

  * ``OsidPrimitive:`` marks an OSID interface used as a primitive. OSID
    primitives may take the form interfaces if not bound to a language
    primitive. Interfaces used as primitives are marked to indicate that
    the underlying objects may be constructed by an OSID Consumer and an
    OSID Provider must honor any OSID primitive regardless of its
    origin.
  * ``Identifiable:`` Marks an interface identifiable by an OSID ``Id.``
  * ``Extensible:`` Marks an interface as extensible through
    ``OsidRecords.``
  * ``Browsable:`` Marks an interface as providing ``Property``
    inspection for its ``OsidRecords.``
  * ``Suppliable:`` Marks an interface as accepting data from an OSID
    Consumer.
  * ``Temporal:`` Marks an interface that has a lifetime with begin an
    end dates.
  * ``Subjugateable:`` Mars an interface that is dependent on another
    object.
  * ``Aggregateable:`` Marks an interface that contains other objects
    normally related through other services.
  * ``Containable:`` Marks an interface that contains a recursive
    reference to itself.
  * ``Sourceable:`` Marks an interface as having a provider.
  * ``Federateable:`` Marks an interface that can be federated using the
    OSID Hierarchy pattern.
  * ``Operable:`` Marks an interface as responsible for performing
    operatons or tasks. ``Operables`` may be enabled or disabled.


Abstract service Interfaces

  * ``OsidProfile:`` Defines interoperability methods used by
    OsidManagers.
  * ``OsidManager:`` The entry point into an OSID and provides access to
    ``OsidSessions.``
  * ``OsidProxyManager:`` Another entry point into an OSID providing a
    means for proxying data from a middle tier application server to an
    underlying OSID Provider.
  * ``OsidSession`` : A service interface accessible from an
    ``OsidManager`` that defines a set of methods for an aspect of a
    service.


Object-like interfaces are generally defined along lines of
interoperability separating issues of data access from data management
and searching. These interfaces may also implement any of the abstract
behavioral interfaces listed above. The OSIDs do not adhere to a DAO/DTO
model in its service definitions in that there are service methods
defined on the objects (although they can be implemented using DTOs if
desired). For the sake of an outline, we'll pretend they are data
objects.

  * ``OsidObject:`` Defines object data. ``OsidObjects`` are accessed
    from ``OsidSessions.``  ``OsidObjects`` are part of an interface
    hierarchy whose interfaces include the behavioral markers and a
    variety of common ``OsidObjects.`` All ``OsidObjects`` are
    ``Identifiable,``  ``Extensible,`` and have a ``Type.`` There are
    several variants of ``OsidObjects`` that indicate a more precise
    behavior.
  * ``OsidObjectQuery:`` Defines a set of methods to query an OSID for
    its ``OsidObjects`` . An ``OsidQuery`` is accessed from an
    ``OsidSession.``
  * ``OsidObjectQueryInspector:`` Defines a set of methods to examine an
    ``OsidQuery.``
  * ``OsidObjectForm:`` Defines a set of methods to create and update
    data. ``OsidForms`` are accessed from ``OsidSessions.``
  * ``OsidObjectSearchOrder:`` Defines a set of methods to order search
    results. ``OsidSearchOrders`` are accessed from ``OsidSessions.``


Most objects are or are derived from ``OsidObjects``. Some object
interfaces may not implement ``OsidObejct`` but instead derive directly
from interface behavioral markers. Other ``OsidObjects`` may include
interface behavioral markers to indicate functionality beyond a plain
object. Several categories of ``OsidObjects`` have been defined to
cluster behaviors to semantically distinguish their function in the
OSIDs.

  * ``OsidCatalog:`` At the basic level, a catalog represents a
    collection of other ``OsidObjects.`` The collection may be physical
    or virtual and may be federated to build larger ``OsidCatalogs``
    using hierarchy services. ``OsidCatalogs`` may serve as a control
    point to filter or constrain the ``OsidObjects`` that may be visible
    or created. Each ``OsidCatalog`` may have its own provider identifty
    apart from the service provider.
  * ``OsidRelationship:`` Relates two ``OsidObjects.`` The
    ``OsidRelationship`` represents the edge in a graph that may have
    its own relationship type and data. ``OsidRelationships`` are
    ``Temporal`` in that they have a time in which the relationship came
    into being and a time when the relationship ends.
  * ``OsidRule:`` Defines an injection point for logic. An ``OsidRule``
    may represent some constraint, evaluation, or execution. While
    authoring of ``OsidRules`` is outside the scope of the OSIDs, an
    ``OsidRule`` provides the mean to identify the rule and map it to
    certain ``OsidObjects`` to effect behavior of a service.


The most basic operations of an OSID center on retrieval, search, create
& update, and notifications on changes to an ``OsidObject``. The more
advanced OSIDs model a system behavior where a variety of implicit
relationships, constraints and rules come into play.

  * ``OsidGovernator:`` Implies an activity or operation exists in the
    OSID Provider acting as an ``Operable`` point for a set of rules
    governing related ``OsidObjects.`` The ``OsidGovernator`` represents
    an engine of sorts in an OSID Provider and may have its own provider
    identity.
  * ``OsidCompendium`` : ``OsidObjects`` which are reports or summaries
    based on transactional data managed elsewhere.


Managing data governing rules occurs in a separate set of interfaces
from the effected ``OsidObjects`` (and often in a separate package).
This allows for a normalized set of rules managing a small set of
control points in a potentially large service.

  * ``OsidEnabler:`` A managed control point to enable or disable the
    operation or effectiveness of another ``OsidObject`` . Enablers
    create a dynamic environment where behaviors and relationships can
    come and go based on rule evauations.
  * ``OsidConstrainer:`` A managed control point to configure the
    constraints on the behavior of another ``OsidObject.``
  * ``OsidProcessor:`` A managed control point to configure the behavior
    of another ``OsidObject`` where some kins of processing is implied.


Other Abstract Interfaces

  * ``OsidSearch:`` Defines set of methods to manage search options for
    performing searches.
  * ``OsidSearchResults:`` Defines a set of methods to examine search
    results.

  * ``OsidReceiver:`` Defines a set of methods invoked for asynchronous
    notification.
  * ``OsidList:`` Defines a set of methods to sequentially access a set
    of objects.
  * ``OsidNode:`` An interface used by hierarchy nodes.
  * ``OsidCondition:`` An input or "statement of fact" into an
    ``OsidRule`` evaluation.
  * ``OsidInput:`` An input of source data into an ``OsidRule``
    processor.
  * ``OsidResult:`` The output from processing an ``OsidRule.``
  * ``OsidRecord:`` An interface marker for an extension to another
    interface. ``OsidRecord`` are negotiated using OSID ``Types.``

  * ``Property:`` Maps a name to a value. Properties are available in
    OSID objects to provide a simplified view of data that may exist
    within a typed interface.
  * ``PropertyList:`` A list of properties.


Runtime

  * ``OsidRuntimeProfile:`` The ``OsidProfile`` for the runtime
    ``OsidManager.``
  * ``OsidRuntimeManager:`` The OSID Runtime service.


Abstract Flow

Generally, these definitions are abstract and not accesed directly. They
are used as building blocks to define interfaces in the OSIDs
themselves. OSIDs derive most of their definitions from a definition in
the osid package. The methods that are defined at this abstract level
versus the methods defined directly in a specific OSID is determined by
the typing in the method signatures. The osid package interfaces are a
means of ensuring consistency of common methods and not designed to
facilitate object polymorphism among different OSIDs. A language binder
may elect to alter the interface hierarchy presented in this
specification and a provider need not parallel these interfaces in their
implementations.

The flow of control through any OSID can be described in terms of these
definitions. An ``OsidManager`` or ``OsidProxyManager`` is retrieved
from the ``OsidRuntimeManager`` for a given service. Both types of
managers share an interface for describing what they support in the
``OsidProfile``.

``OsidSessions`` are created from the ``OsidManager``.  ``OsidSessions``
tend to be organized along clusters of like-functionality. Lookup-
oriented sessions retrieve ``OsidObjects``. Return of multiple
``OsidObjects`` is done via the ``OsidList``. Search-oriented sessions
retrieve ``OsidObjects`` through searches provided through the
``OsidQuery`` and ``OsidSearch`` interfaces.

Administrative-oriented sessions create and update ``OsidObjects`` using
the ``OsidForm`` interface. The ``OsidForm`` makes available
``Metadata`` to help define its rules for setting and changing various
data elements.

``OsidObjects`` can be organized within ``OsidCatalogs``. An
``OsidCatalog`` is hierarchical and can be traversed through an
``OsidNode``. An ``OsidQuery`` or an ``OsidSearchOrder`` may be mapped
to a dynamic ``OsidCatalog``. Such a query may be examined using an
``OsidQueryInspector``.

A notification session provides a means for subscribing to events, "a
new object has been created", for example, and these events are received
from an ``OsidReceiver``.

Meta OSID Specification

The OSID Specification framework defines the interace and method
structures as well as the language primitives and errors used throughout
the OSIDs. The OSID Specifications are defined completely in terms of
interfaces and the elements specified in the meta specification.

Language Primitives

Ths meta OSID Specification enumerates the allowable language primitives
that can be used in OSID method signatures. Parameters and returns in
OSID methods may be specified in terms of other OSID interfaces or using
one of these primitives. An OSID Binder translates these language
primitives into an appropriate language primitive counterpart.

An OSID Primitive differs from a language primitive. An OSID Primitive
is an interface used to describe a more complex structure than a simple
language primitive can support. Both OSID Primitives and language
primitives have the same behavior in the OSIDs in that an there is no
service encapsulation present allowing OSID Primitives to be consructed
by an OSID Consumer.

Errors

OSID methods are required to return a value, if specified, or return one
of the errors specified in the method signature. The meta package
defines the set of errors that a method signtaure may use.

Errors should result when the contract of the interface as been violated
or cannot be fulfilled and it is necessary to disrupt the flow of
control for a consumer. Different errors are specified where it is
forseen that a consumer may wish to execute a different action without
violating the encapsulation of internal provider operations. Such
actions do not include debugging or other detailed information which is
the responsibility of the provider to manage. As such, the number of
errors defined across all the interfaces is kept to a minimum and the
context of the error may vary from method to method in accordance with
the spceification.

Errors are categorized to convey the audience to which the error
pertains.

  * User Errors: Errors which may be the result of a user operation
    intended for the user.
  * Operational Errors: Errors which may be the result of a system or
    some other problem intended for the user.
  * Consumer Contract Errors: Software errors resulting in the use of
    the OSIDs by an OSID Consumer intended for the application
    programmer. These also include integration problems where the OSID
    Consumer bypassed a method to test for support of a service or type.
  * Provider Contract Errors: Software errors in the use of an OSID by
    an OSID Provider intended for an implementation programmer.


Compliance

OSID methods include a compliance statement indicating whether a method
is required or optional to implement. An optional OSID method is one
that defines an UNIMPLEMENTED error and there is a corresponding method
to test for the existence of an implementation.

OSID 3K Acknowledgements

  * Tom Coppeto (Editor & Architect)
  * Scott Thorne (Architect)


The authors gratefully acknowledge the following individuals for their
time, wisdom, and contributions in shaping these specifications.

  * Adam Franco, Middlebury College
  * Jeffrey Merriman, Massachusetts Institute of Technology
  * Charles Shubert, Massachusetts Insitute of Technology

  * Prof. Marc Alier, Universitat Politècnica de Catalyuna
  * Joshua Aresty, Massachusetts Institute of Technology
  * Fabrizio Cardinali, Giunti Labs
  * Pablo Casado, Universitat Politècnica de Catalyuna
  * Alex Chapin, Middlebury College
  * Craig Counterman, Massachusetts Institute of Technology
  * Francesc Santanach Delisau, Universitat Oberta de Catalyuna
  * Prof. Llorenç Valverde Garcia, Universitat Oberta de Catalyuna
  * Catherine Iannuzzo, Massachusetts Institute of Technology
  * Jeffrey Kahn, Verbena Consulting
  * Michael Korcynski, Tufts University
  * Anoop Kumar, Tufts University
  * Eva de Lera, Universitat Oberta de Catalyuna
  * Roberto García Marrodán, Universitat Oberta de Catalyuna
  * Andrew McKinney, Massachusetts Institute of Technology
  * Scott Morris, Apple
  * Mark Norton, Nolaria Consulting
  * Mark O'Neill, Dartmouth College
  * Prof. Charles Severance, University of Michigan
  * Stuart Sim, Sun Microsystems/Common Need
  * Colin Smythe, IMS Global Learning Consortium
  * George Ward, California State University
  * Peter Wilkins, Massachusetts Institute of Technology
  * Norman Wright, Massachusetts Institute of Technology


O.K.I. Acknowledgements

OSID 3K is based on the O.K.I. OSIDs developed as part of the MIT Open
Knowledge Initiative (O.K.I) project 2001-2004.

  * Vijay Kumar, O.K.I. Principal Investigator, Massachusetts Insitute
    of Technology
  * Jeffrey Merriman, O.K.I. Project Director, Massachusetts Insitute of
    Technology
  * Scott Thorne, O.K.I. Chief Architect, Massachusetts Institute of
    Technology
  * Charles Shubert, O.K.I. Architect, Massachusetts Institute of
    Technology
  * Lois Brooks, Project Coordinator, Stanford University
  * Mark Brown, O.K.I. Project Manager, Massachusetts Institute of
    Technology
  * Bill Fitzgerald, O.K.I. Finance Manager, Massachusetts Institute of
    Technology
  * Judson Harward, Educational Systems Architect, Massachusetts
    Institute of Technology
  * Charles Kerns, Educational Systems Architect, Stanford University
  * Jeffrey Kahn, O.K.I. Partner, Verbena Consulting
  * Judith Leonard, O.K.I. Project Administrator, Massachusetts
    Institute of Technology
  * Phil Long, O.K.I. Outreach Coordinator, Massachusetts Institute of
    Technology

  * Cambridge University, O.K.I. Core Collaborator
  * Dartmouth College, O.K.I. Core Collaborator
  * Massachusetts Institute of Technology, O.K.I. Core Collaborator
  * North Carolina State University, O.K.I. Core Collaborator
  * Stanford University, O.K.I. Core Collaborator
  * University of Michigan, O.K.I. Core Collaborator
  * University of Pennsylvania, O.K.I. Core Collaborator
  * University of Wisconsin, Madison, O.K.I. Core Collaborator


"""
