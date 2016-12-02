"""GStudio implementations of assessment.authoring objects."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification

#from ..id.objects import IdList
#import importlib


import importlib


from . import default_mdata
from .. import utilities
from ...abstract_osid.assessment_authoring import objects as abc_assessment_authoring_objects
from ..osid import markers as osid_markers
from ..osid import objects as osid_objects
from ..osid.metadata import Metadata
from ..primitives import Id
from ..utilities import get_registry
from ..utilities import update_display_text_defaults
from dlkit.abstract_osid.osid import errors
from dlkit.primordium.id.primitives import Id




class AssessmentPart(abc_assessment_authoring_objects.AssessmentPart, osid_objects.OsidObject, osid_markers.Containable, osid_markers.Operable):
    """An ``AssessmentPart`` represents a section of an assessment.

    ``AssessmentParts`` may be visible as sections of an assessment or
    just used to clump together a set of items on which to hang sequence
    rules.

    """

    _namespace = 'assessment_authoring.AssessmentPart'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='ASSESSMENT_PART', **kwargs)
        self._catalog_name = 'bank'


    def get_assessment_id(self):
        """Gets the assessment ``Id`` to which this rule belongs.

        return: (osid.id.Id) - ``Id`` of an assessment
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_id = property(fget=get_assessment_id)

    def get_assessment(self):
        """Gets the assessment to which this rule belongs.

        return: (osid.assessment.Assessment) - an assessment
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment = property(fget=get_assessment)

    def has_parent_part(self):
        """Tests if this assessment part belongs to a parent assessment part.

        return: (boolean) - ``true`` if this part has a parent,
                ``false`` if a root
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_assessment_part_id(self):
        """Gets the parent assessment ``Id``.

        return: (osid.id.Id) - ``Id`` of an assessment
        raise:  IllegalState - ``has_parent_part()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_part_id = property(fget=get_assessment_part_id)

    def get_assessment_part(self):
        """Gets the parent assessment.

        return: (osid.assessment.authoring.AssessmentPart) - the parent
                assessment part
        raise:  IllegalState - ``has_parent_part()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_part = property(fget=get_assessment_part)

    def is_section(self):
        """Tests if this part should be visible as a section in an assessment.

        If visible, this part will appear to the user as a separate
        section of the assessment. Typically, a section may not be under
        a non-sectioned part.

        return: (boolean) - ``true`` if this part is a section,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_weight(self):
        """Gets an integral weight factor for this assessment part used for scoring.

        The percentage weight for this part is this weight divided by
        the sum total of all the weights in the assessment.

        return: (cardinal) - the weight
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    weight = property(fget=get_weight)

    def get_allocated_time(self):
        """Gets the allocated time for this part.

        The allocated time may be used to assign fixed time limits to
        each item or can be used to estimate the total assessment time.

        return: (osid.calendaring.Duration) - allocated time
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    allocated_time = property(fget=get_allocated_time)

    def get_child_assessment_part_ids(self):
        """Gets any child assessment part ``Ids``.

        return: (osid.id.IdList) - ``Ids`` of the child assessment parts
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    child_assessment_part_ids = property(fget=get_child_assessment_part_ids)

    def get_child_assessment_parts(self):
        """Gets any child assessment parts.

        return: (osid.assessment.authoring.AssessmentPartList) - the
                child assessment parts
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    child_assessment_parts = property(fget=get_child_assessment_parts)

    @utilities.arguments_not_none
    def get_assessment_part_record(self, assessment_part_record_type):
        """Gets the assessment part record corresponding to the given ``AssessmentPart`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``assessment_part_record_type`` may be the
        ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(assessment_part_record_type)`` is ``true`` .

        arg:    assessment_part_record_type (osid.type.Type): the type
                of the record to retrieve
        return: (osid.assessment.authoring.records.AssessmentPartRecord)
                - the assessment part record
        raise:  NullArgument - ``assessment_part_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_part_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentPartForm(abc_assessment_authoring_objects.AssessmentPartForm, osid_objects.OsidObjectForm, osid_objects.OsidContainableForm, osid_objects.OsidOperableForm):
    """This is the form for creating and updating ``AssessmentParts``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``AssessmentAuthoringSession``. For each data element that may be
    set, metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'assessment_authoring.AssessmentPart'

    def __init__(self, **kwargs):
        osid_objects.OsidObjectForm.__init__(self, object_name='ASSESSMENT_PART', **kwargs)
        self._mdata = default_mdata.get_assessment_part_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""

        osid_objects.OsidContainableForm._init_metadata(self)
        osid_objects.OsidObjectForm._init_metadata(self, **kwargs)
        self._allocated_time_default = self._mdata['allocated_time']['default_duration_values'][0]

    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""

        osid_objects.OsidContainableForm._init_map(self)
        osid_objects.OsidObjectForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    def get_weight_metadata(self):
        """Gets the metadata for the weight.

        return: (osid.Metadata) - metadata for the weight
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['weight'])
        # metadata.update({'existing_weight_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    weight_metadata = property(fget=get_weight_metadata)

    @utilities.arguments_not_none
    def set_weight(self, weight):
        """Sets the weight on a scale from 0-100.

        arg:    weight (cardinal): the new weight
        raise:  InvalidArgument - ``weight`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_weight(self):
        """Clears the weight.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    weight = property(fset=set_weight, fdel=clear_weight)

    def get_allocated_time_metadata(self):
        """Gets the metadata for the allocated time.

        return: (osid.Metadata) - metadata for the allocated time
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['allocated_time'])
        # metadata.update({'existing_allocated_time_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    allocated_time_metadata = property(fget=get_allocated_time_metadata)

    @utilities.arguments_not_none
    def set_allocated_time(self, time):
        """Sets the allocated time.

        arg:    time (osid.calendaring.Duration): the allocated time
        raise:  InvalidArgument - ``time`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_allocated_time(self):
        """Clears the allocated time.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    allocated_time = property(fset=set_allocated_time, fdel=clear_allocated_time)

    @utilities.arguments_not_none
    def get_assessment_part_form_record(self, assessment_part_record_type):
        """Gets the ``AssessmentPartFormRecord`` corresponding to the given assessment record ``Type``.

        arg:    assessment_part_record_type (osid.type.Type): the
                assessment part record type
        return:
                (osid.assessment.authoring.records.AssessmentPartFormRec
                ord) - the assessment part record
        raise:  NullArgument - ``assessment_part_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_part_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentPartList(abc_assessment_authoring_objects.AssessmentPartList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``AssessmentPartList`` provides a means for accessing ``AssessmentPart`` elements sequentially either one at a time or many at a time.

    Examples: while (apl.hasNext()) { AssessmentPart assessmentPart =
    apl.getNextAssessmentPart(); }

    or
      while (apl.hasNext()) {
           AssessmentPart[] assessmentParts = apl.hetNextAssessmentParts(apl.available());
      }



    """

    def get_next_assessment_part(self):
        """Gets the next ``AssessmentPart`` in this list.

        return: (osid.assessment.authoring.AssessmentPart) - the next
                ``AssessmentPart`` in this list. The ``has_next()``
                method should be used to test that a next
                ``AssessmentPart`` is available before calling this
                method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(AssessmentPart)

    next_assessment_part = property(fget=get_next_assessment_part)

    @utilities.arguments_not_none
    def get_next_assessment_parts(self, n):
        """Gets the next set of ``AssessmentPart`` elements in this list which must be less than or equal to the number returned from ``available()``.

        arg:    n (cardinal): the number of ``AssessmentPart`` elements
                requested which should be less than or equal to
                ``available()``
        return: (osid.assessment.authoring.AssessmentPart) - an array of
                ``AssessmentPart`` elements.The length of the array is
                less than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class SequenceRule(abc_assessment_authoring_objects.SequenceRule, osid_objects.OsidRule):
    """A ``SequenceRule`` defines the ordering of ``AssessmentParts``."""

    _namespace = 'assessment_authoring.SequenceRule'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='SEQUENCE_RULE', **kwargs)
        self._catalog_name = 'bank'


    def get_assessment_part_id(self):
        """Gets the assessment part ``Id`` to which this rule belongs.

        return: (osid.id.Id) - ``Id`` of an assessment part
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_part_id = property(fget=get_assessment_part_id)

    def get_assessment_part(self):
        """Gets the assessment part to which this rule belongs.

        return: (osid.assessment.authoring.AssessmentPart) - an
                assessment part
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_part = property(fget=get_assessment_part)

    def get_next_assessment_part_id(self):
        """Gets the next assessment part ``Id`` for success of this rule.

        return: (osid.id.Id) - ``Id`` of an assessment part
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    next_assessment_part_id = property(fget=get_next_assessment_part_id)

    def get_next_assessment_part(self):
        """Gets the next assessment part for success of this rule.

        return: (osid.assessment.authoring.AssessmentPart) - an
                assessment part
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    next_assessment_part = property(fget=get_next_assessment_part)

    def get_minimum_score(self):
        """Gets the minimum score expressed as an integer (0-100) for this rule.

        return: (cardinal) - minimum score
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    minimum_score = property(fget=get_minimum_score)

    def get_maximum_score(self):
        """Gets the maximum score expressed as an integer (0-100) for this rule.

        return: (cardinal) - maximum score
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    maximum_score = property(fget=get_maximum_score)

    def is_cumulative(self):
        """Tests if the score is applied to all previous assessment parts.

        return: (boolean) - ``true`` if the score is applied to all
                previous assessment parts, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_applied_assessment_part_ids(self):
        """Qualifies ``is_cumulative()`` to apply to a specific list of assessment parts.

        If ``is_cumulative()`` is ``true,`` this method may return an
        empty list to mean all previous assessment parts.

        return: (osid.id.IdList) - list of assessment parts
        raise:  IllegalState - ``is_cumulative()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    applied_assessment_part_ids = property(fget=get_applied_assessment_part_ids)

    def get_applied_assessment_parts(self):
        """Qualifies ``is_cumulative()`` to apply to a specific list of assessment parts.

        If ``is_cumulative()`` is ``true,`` this method may return an
        empty list to mean all previous assessment parts.

        return: (osid.assessment.authoring.AssessmentPartList) - list of
                assessment parts
        raise:  IllegalState - ``is_cumulative()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    applied_assessment_parts = property(fget=get_applied_assessment_parts)

    @utilities.arguments_not_none
    def get_sequence_rule_record(self, sequence_rule_record_type):
        """Gets the assessment sequence rule record corresponding to the given ``SequenceRule`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``sequence_rule_record_type`` may be the
        ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(sequence_rule_record_type)`` is ``true`` .

        arg:    sequence_rule_record_type (osid.type.Type): the type of
                the record to retrieve
        return: (osid.assessment.authoring.records.SequenceRuleRecord) -
                the assessment sequence rule record
        raise:  NullArgument - ``sequence_rule_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(sequence_rule_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class SequenceRuleForm(abc_assessment_authoring_objects.SequenceRuleForm, osid_objects.OsidRuleForm):
    """This is the form for creating and updating sequence rules.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the ``SequenceSession``
    For each data element that may be set, metadata may be examined to
    provide display hints or data constraints.

    """

    def get_minimum_score_metadata(self):
        """Gets the metadata for the minimum score.

        return: (osid.Metadata) - metadata for the minimum score
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    minimum_score_metadata = property(fget=get_minimum_score_metadata)

    @utilities.arguments_not_none
    def set_minimum_score(self, score):
        """Sets the minimum score for this rule.

        arg:    score (cardinal): minimum score
        raise:  InvalidArgument - ``score`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    minimum_score = property(fset=set_minimum_score)

    def get_maximum_score_metadata(self):
        """Gets the metadata for the maximum score.

        return: (osid.Metadata) - metadata for the maximum score
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    maximum_score_metadata = property(fget=get_maximum_score_metadata)

    @utilities.arguments_not_none
    def set_maximum_score(self, score):
        """Sets the maximum score for this rule.

        arg:    score (cardinal): maximum score
        raise:  InvalidArgument - ``score`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    maximum_score = property(fset=set_maximum_score)

    def get_cumulative_metadata(self):
        """Gets the metadata for the cumulative flag.

        return: (osid.Metadata) - metadata for the cumulative flag
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    cumulative_metadata = property(fget=get_cumulative_metadata)

    @utilities.arguments_not_none
    def set_cumulative(self, cumulative):
        """Applies this rule to all previous assessment parts.

        arg:    cumulative (boolean): ``true`` to apply to all previous
                assessment parts. ``false`` to apply to the immediate
                previous assessment part
        raise:  InvalidArgument - ``cumulative`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    cumulative = property(fset=set_cumulative)

    def get_applied_assessment_parts_metadata(self):
        """Gets the metadata for the applied assessment parts.

        return: (osid.Metadata) - metadata for the applied assessment
                parts
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    applied_assessment_parts_metadata = property(fget=get_applied_assessment_parts_metadata)

    @utilities.arguments_not_none
    def apply_assessment_parts(self, assessment_part_ids):
        """Designates assessment parts to which the rule applies.

        arg:    assessment_part_ids (osid.id.Id[]): the parts to which
                this rule should apply
        raise:  InvalidArgument - ``assessment_part_ids`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``assessment_part_ids`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_sequence_rule_form_record(self, sequence_rule_record):
        """Gets the ``SequenceRuleFormRecord`` corresponding to the given sequence rule record ``Type``.

        arg:    sequence_rule_record (osid.type.Type): a sequence rule
                record type
        return:
                (osid.assessment.authoring.records.SequenceRuleFormRecor
                d) - the sequence rule record
        raise:  NullArgument - ``sequence_rule_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(asequence_rule_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class SequenceRuleList(abc_assessment_authoring_objects.SequenceRuleList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``SequenceRuleList`` provides a means for accessing ``SequenceRule`` elements sequentially either one at a time or many at a time.

    Examples: while (srl.hasNext()) { AssessmentSequenceRule rule =
    srl.getNextAssessmentSequenceRule(); }

    or
      while (srl.hasNext()) {
           AssessmentSequenceRule[] rules = srl.getNextAssessmentSequenceRules(srl.available());
      }



    """

    def get_next_sequence_rule(self):
        """Gets the next ``SequenceRule`` in this list.

        return: (osid.assessment.authoring.SequenceRule) - the next
                ``SequenceRule`` in this list. The ``has_next()`` method
                should be used to test that a next ``SequenceRule`` is
                available before calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(SequenceRule)

    next_sequence_rule = property(fget=get_next_sequence_rule)

    @utilities.arguments_not_none
    def get_next_sequence_rules(self, n):
        """Gets the next set of ``SequenceRule`` elements in this list which must be less than or equal to the number returned from ``available()``.

        arg:    n (cardinal): the number of ``SequenceRule`` elements
                requested which should be less than or equal to
                ``available()``
        return: (osid.assessment.authoring.SequenceRule) - an array of
                ``SequenceRule`` elements.The length of the array is
                less than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


