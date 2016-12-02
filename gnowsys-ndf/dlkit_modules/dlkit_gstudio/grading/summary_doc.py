# -*- coding: utf-8 -*-
"""Grading Open Service Interface Definitions
grading version 3.0.0

The Grading OSID defines a service to apply grades or ratings.

Grade Systems

The grade system sessions provide the means to retrievs and manage
``GradeSystem`` definitions. A ``GradeSystem`` is a fixed set of
``Grades`` . ``GradeSystems`` may also take the form of a numerical
score as well as a rating based on some system. ``GradeEntries`` belong
to a single ``GradebookColumn``.

Gradebook Columns

A ``Gradebook`` is represented by a series of ``GradebookColumns``. A
``GradeBookColumn`` represents a something to be graded and is joined to
a single ``GradeSystem``. A ``GradebookColumn`` may be constrained to a
single grader.

Grade Entries

A ``GradebookColumn`` is comprised of a series of ``GradeEntry``
elements. A ``GradebookColumn`` may represent "Assignment 3" while a
``GradeEntry`` may represent the assignment turned in by a particular
student.

A ``Grade`` can be applied to a ``GradeEntry`` that relates the entry to
a grader and a key ``Resource``. In the case of a class gradebook, the
key resource represents the student. If there are multiple graders for
the same key resource, each grader gets their own ``GradebookColumn``.

Gradebooks may also be used to capture ratings about other objects. In
the case where people vote for their favorite assets, the key resource
represents the ``Asset`` .

``GradebookColumns`` may have a ``GradebookColumnSummary`` entry for
summary results and statistics across all ``GradeEntries`` in the
column.

Gradebook Cataloging

``GradebookColumns`` are organized into ``Gradebooks``.  ``Gradebooks``
also provide for a federated hierarchy of ``GradebookColumns``. Simple
reordering of ``GradebookColumns`` can be performed by moving the
``GradebookColumn`` relative to another. The relative positioning may
reference two ``GradebookColumns`` through the federation.

Sub Packages

The Grading OSID includes several subpackages. The Grading Transform
OSID provides a means of translating one ``GradeSystem`` to another. The
Grading Calculation OSID defines derived ``GradebookColumns``. The
Grading Batch OSID manages ``GradeSystems,``  ``GradeEntries,``
``Gradebooks,`` and ``GradebookColumns`` in bulk.

"""
