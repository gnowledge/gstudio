# -*- coding: utf-8 -*-
"""Assessment Open Service Interface Definitions
assessment version 3.0.0

The Assessment OSID provides the means to create, access, and take
assessments. An ``Assessment`` may represent a quiz, survey, or other
evaluation that includes assessment ``Items``. The OSID defines methods
to describe the flow of control and the relationships among the objects.
Assessment ``Items`` are extensible objects to capture various types of
questions, such as a multiple choice or an asset submission.

The Assessment service can br broken down into several distinct
services:

  * Assessment Taking
  * Assessment and Item authoring
  * Accessing and managing banks of assessments and items


Each of these service areas are covered by different session and object
interfaces. The object interfaces describe both the structure of the
assessment and follow an assessment management workflow of first
defining assessment items and then authoring assessments based on those
items. They are:

  * ``Item`` : a question and answer pair
  * ``Response:`` a response to an ``Item`` question
  * ``Assessment`` : a set of ``Items``
  * ``AssessmentSection:`` A grouped set of ``Items``
  * ``AssessmentOffering:`` An ``Assessment`` available for taking
  * ``AssessmentTaken:`` An ``AssessmentOffering`` that has been
    completed or in progress


Taking Assessments

The ``AssessmentSession`` is used to take an assessment. It captures
various ways an assessment can be taken which may include time
constraints, the ability to suspend and resume, and the availability of
an answer.

Taking an ``Assessment`` involves first navigating through
``AssessmentSections``. An ``AssessmentSection`` is an advanced
authoring construct used to both visually divide an ``Assessment`` and
impose additional constraints. Basic assessments are assumed to always
have one ``AssessmentSection`` even if not explicitly created.

Authoring

A basic authoring session is available in this package to map ``Items``
to ``Assessments``. More sophisticated authoring using
``AssessmentParts`` and sequencing is available in the Assessment
Authoring OSID.

Bank Cataloging

``Assessments,``  ``AssessmentsOffered,``  ``AssessmentsTaken,`` and
``Items`` may be organized into federateable catalogs called ``Banks`` .

Sub Packages

The Assessment OSID includes an Assessment Authoring OSID for more
advanced authoring and sequencing options.

"""
