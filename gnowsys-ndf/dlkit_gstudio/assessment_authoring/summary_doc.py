# -*- coding: utf-8 -*-
"""Assessment Authoring Open Service Interface Definitions
assessment.authoring version 3.0.0

The Assessment OSID provides the means to create, access, and take
assessments. An ``Assessment`` may represent a quiz, survey, or other
evaluation that includes assessment ``Items``. The OSID defines methods
to describe the flow of control and the relationships among the objects.
Assessment ``Items`` are extensible objects to capture various types of
questions, such as a multiple choice or asset submission.

The Assessment service can br broken down into several distinct
services:

  * Assessment Taking
  * Assessment and Item authoring
  * Accessing and managing banks of assessments and items


Each of these service areas are covered by different session and object
interfaces. The object interfaces describe both the structure of the
assessment and follow an assessment management workflow. They are:

  * ``Item`` : a question and answer pair
  * ``Response:`` a response to an ``Item`` question
  * ``Assessment`` : a set of ``Items``
  * ``AssessmentPart:`` A grouped set of ``Items`` for fancier
    assessment sequencing
  * ``AssessmentOffering:`` An ``Assessment`` available for taking
  * ``AssessmentTaken:`` An ``AssessmentOffering`` that has been
    completed or in progress


The ``AssessmentSession`` is used to take an assessment and review the
results. It captures various ways an assessment can be taken which may
include time constraints, the ability to suspend and resume,
availability of an answer key, or access to a score or other evaluation.
Care should be taken to understand the various interoperability issues
in using this interface.

An ``AssessmentSession`` may be created using an ``AssessmentOffered``
or ``AssessmentTaken``  ``Id``. If instantiated with an
``AssessmentOffered``  ``Id,`` an ``AssessmentTaken`` is implicitly
created and further references to its state should be performed using
the ``AssessmentTaken``  ``Id``.

An ``AssessmentSession`` is a mapping of an ``AssessmentOffered`` to an
``Agent`` at a point in time. The resulting ``AssessmentTaken`` is an
identifier representing this relationship.

On the authoring side, Items map to ``Assessments``. An ``Item`` may
appear in more than one ``Assessment``. Item banks may be used to
catalog sets of Items and/or sets of ``Assessments``.

"""
