# -*- coding: utf-8 -*-
"""Repository Open Service Interface Definitions
repository version 3.0.0

The Repository OSID provides the service of finding and managing digital
assets.

Assets

An ``Asset`` represents a unit of content, whether it be an image, a
video, an application document or some text. The Asset defines a core
set of definitions applicable to digital content, such as copyright and
publisher, and allows for a type specification to be appended as with
other ``OsidObjects``.

Asset content, such as a document, is defined such that there may be
multiple formats contained with the same asset. A document may be
accessible in both PDF and MS Word, but is the same document, for
example. An image may have both a large size and a thumbnail version.
Generally, an asset contains more than one version of content when it is
left to the application to decide which is most appropriate.

The ``Asset``  ``Type`` may define methods in common throughout the
content variations. An example asset is one whose content ``Types`` are
"Quicktime" and "MPEG", but the ``Asset``  ``Type`` is "movie" and
defines methods that describe the move aside from the formats. This
"double" Type hierarchy stemming from the asset requires more care in
defining interfaces.

``Assets`` also have "credits" which define the authors, editors,
creators, performers, producers or any other "role", identified with a
role ``Type,`` with the production of the asset. These are managed
externally to the asset through another ``OsidSession``.

Through additional optional ``OsidSessions,`` the ``Asset`` can be
"extended" to offer temporal information. An asset may pertain to a
date, a period of time, or a series of dates and periods. This mechanism
is to offer the ability to search for assets pertaining to a desired
date range without requiring understanding of a ``Type``.

Similarly, the ``Asset`` can also map to spatial information. A
photograph may be "geotagged" with the GPS coordinates where it was
taken, a conical shape in stellar coordinates could be described for an
astronimocal image, or there may be a desire to may a historical book to
the spatial coordinates of Boston and Philadelphia. Unlike temporal
mappings, the definition of the spatial coordinate is left to a spatial
Type to define. The Repository OSID simply manages spatial mappings to
the Asset.

Asset Tagging

``Assets`` may also relate to Ontology OSID ``Subjects``. The
``Subject`` provides the ability to normalize information related to
subject matter across the ``Assets`` to simplify management and provide
a more robust searching mechanism. For example, with a photograph of the
Empire State Building, one may wish to describe that it was designed by
Shreve, Lamb and Harmon and completed in 1931. The information about the
building itself can be described using a ``Subject`` and related to the
photograph, and any other photograph that captures the building. The
``Asset``  ``Type`` for the photograph may simply be "photograph" and
doesn't attempt to describe a building, while the ``AssetContent``
``Type`` is "image/jpeg".

An application performing a search for Empire State Building can be
execute the search over the ``Subjects,`` and once the user has narrowed
the subject area, then the related Assets can be retrieved, and from
there negotiate the content.

A provider wishing to construct a simple inventory database of buildings
in New York may decide to do so using the Resource OSID. The
``Resource``  ``Type`` may describe the construction dates, height,
location, style and architects of buildings. The ``Type`` may also
include a means of getting a reference image using the ``Asset``
interface. Since there is no explicit relationship between ``Subject``
and ``Resource,`` the ``Resource`` can be adapted to the ``Subject``
interface (mapping a ``building_resource_type`` to a
``building_subject_type`` ) to use the same data for ``Subject`` to
``Asset`` mappings and searching.

Asset Compositions

Asset compositions can be created using the ``Composition`` interface. A
``Composition`` is a group of ``Assets`` and compositions may be
structured into a hierarchy for the purpose of "building" larger
content. A content management system may make use of this interface to
construct a web page. The ``Composition`` hierarchy may map into an
XHTML structure and each ``Asset`` represent an image or a link in the
document. However, the produced web page at a given URL may be
represented by another single ``Asset`` that whose content has both the
URL and the XHTML stream.

Another example is an IMS Common Cartridge. The ``Composition`` may be
used to produce the zip file cartridge, but consumers may access the zip
file via an ``Asset`` .

Repository Cataloging

Finally, ``Assets`` and ``Compositions`` may be categorized into
``Repository`` objects. A ``Repository`` is a catalog-like interface to
help organize assets and subject matter. Repositories may be organized
into hierarchies for organization or federation purposes.

This number of service aspects to this Repository OSID produce a large
number of definitions. It is recommended to use the
``RepositoryManager`` definition to select a single ``OsidSession`` of
interest, and work that definition through its dependencies before
tackling another aspect.

Sub Packages

The Repository OSID includes a rules subpackage for managing dynamic
compositions.

"""
