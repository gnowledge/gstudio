# -*- coding: utf-8 -*-
"""Learning Open Service Interface Definitions
learning version 3.0.0

The Learning OSID manages learning objectives. A learning ``Objective``
describes measurable learning goals.

Objectives

``Objectives`` describe measurable learning goals. A learning objective
may be measured by a related ``Assesment``.  ``Objectives`` may be
mapped to levels, A level is represented by a ``Grade`` which is used to
indicate a grade level or level of difficulty.

``Objectives`` are hierarchical. An ``Objective`` with children
represents an objective that is inclusive of all its children. For
example, an ``Objective`` that represents learning in arithmetic may be
composed of objectives that represent learning in both addition and
subtraction.

``Objectives`` may also have requisites. A requisite objective is one
that should be achieved before an objective is attempted.

Activities

An ``Activity`` describes actions that one can do to meet a learning
objective. An ``Activity`` includes a list of ``Assets`` to read or
watch, or a list of ``Courses`` to take, or a list of learning
``Assessments`` to practice. An ``Activity`` may also represent other
learning activities such as taking a course or practicing an instrument.
An ``Activity`` is specific to an ``Objective`` where the reusability is
achieved based on what the ``Activity`` relates.

Proficiencies

A ``Proficiency`` is an ``OsidRelationship`` measuring the competence of
a ``Resource`` with respect to an Objective.

Objective Bank Cataloging

``Objectives, Activities,`` and ``Proficiencies`` can be organized into
hierarchical ``ObjectiveBanks`` for the purposes of categorization and
federation.

Concept Mapping

A concept can be modeled as a learning ``Objective`` without any related
``Assessment`` or ``Activities``. In this scenario, an ``Objective``
looks much like the simpler ``Subject`` in the Ontology OSID. The
Ontology OSID is constrained to qualifying concepts while the relations
found in an ``Objective`` allow for the quantification of the learning
concept and providing paths to self-learning.

The Topology OSID may also be used to construct and view a concept map.
While a Topology OSID Provider may be adapted from a Learning OSID or an
Ontology OSID, the topology for either would be interpreted from a
multi-parented hierarchy of the ``Objectives`` and ``Subjects``
respectively.

Courses

The Learning OSID may be used in conjunction with the Course OSID to
identify dsired learning oitcomes from a course or to align the course
activities and syllabus with stated learning objectives. The Course OSID
describes learning from a structured curriculum management point of view
where the Learning OSID and allows for various objectives to be combined
and related without any regard to a prescribed curriculum.

Sub Packages

The Learning OSID contains a Learning Batch OSID for bulk management of
``Objectives,``  ``Activities,`` and ``Proficiencies`` .

"""
