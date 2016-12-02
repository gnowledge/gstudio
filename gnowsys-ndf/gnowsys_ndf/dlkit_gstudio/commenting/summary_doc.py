# -*- coding: utf-8 -*-
"""Commenting Open Service Interface Definitions
commenting version 3.0.0

The Commenting OSID provides a means of relating user comments and
ratings to OSID Objects.

The Commenting OSID may be used as an auxiliary service orchestrated
with other OSIDs to either provide administrative comments as well as
create a social network-esque comment and rating service to various
``OsidObjects``.

Comments

``Comments`` contain text entries logged by date and ``Agent``. A
``Comment`` may also include a rating represented by a ``Grade`` defined
in a ``GradeSystem``. The ``RatingLookupSession`` may be used to query
cumulative scores across an object reference or the entire ``Book``.

``Comments`` are ``OsidRelationships`` between a commentor and a
reference Id. The relationship defines dates for which the comment
and/or rating is effective.

Commentors

An ``Agent`` comments on something. As a person is represented by a
``Resource`` in the Resource OSID, the Comments provide access to both
the commenting ``Agent`` and the related ``Resource`` to avoid the need
of an additional service orchestration for resolving the ``Agent``.

Cataloging

``Comments`` are cataloged in ``Books`` which may also be grouped
hierarchically to federate multiple collections of comments.

Sub Packages

The Commenting OSID includes a Commenting Batch OSID for managing
``Comments`` and ``Books`` in bulk.

"""
