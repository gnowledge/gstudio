"""GStudio implementations of assessment objects."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification

#from ..id.objects import IdList
#import importlib
#from ..osid.objects import OsidForm
#from ..osid.objects import OsidObjectForm
#from ..utilities import get_registry


import importlib


from . import default_mdata
from .. import utilities
from ...abstract_osid.assessment import objects as abc_assessment_objects
from ..osid import markers as osid_markers
from ..osid import objects as osid_objects
from ..osid.metadata import Metadata
from ..primitives import Id
from ..utilities import get_registry
from ..utilities import update_display_text_defaults
from dlkit.abstract_osid.osid import errors
from dlkit.primordium.id.primitives import Id




class Question(abc_assessment_objects.Question, osid_objects.OsidObject):
    """A ``Question`` represents the question portion of an assessment item.

    Like all OSID objects, a ``Question`` is identified by its ``Id``
    and any persisted references should use the ``Id``.

    """

    _namespace = 'assessment.Question'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='QUESTION', **kwargs)
        self._catalog_name = 'bank'


    @utilities.arguments_not_none
    def get_question_record(self, question_record_type):
        """Gets the item record corresponding to the given ``Question`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``question_record_type`` may be the
        ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(question_record_type)`` is ``true`` .

        arg:    question_record_type (osid.type.Type): the type of the
                record to retrieve
        return: (osid.assessment.records.QuestionRecord) - the question
                record
        raise:  NullArgument - ``question_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(question_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class QuestionForm(abc_assessment_objects.QuestionForm, osid_objects.OsidObjectForm):
    """This is the form for creating and updating ``Questions``."""

    _namespace = 'assessment.Question'

    def __init__(self, **kwargs):
        osid_objects.OsidObjectForm.__init__(self, object_name='QUESTION', **kwargs)
        self._mdata = default_mdata.get_question_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""
        osid_objects.OsidObjectForm._init_metadata(self, **kwargs)
    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""
        osid_objects.OsidObjectForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    @utilities.arguments_not_none
    def get_question_form_record(self, question_record_type):
        """Gets the ``QuestionFormRecord`` corresponding to the given question record ``Type``.

        arg:    question_record_type (osid.type.Type): the question
                record type
        return: (osid.assessment.records.QuestionFormRecord) - the
                question record
        raise:  NullArgument - ``question_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(question_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class QuestionList(abc_assessment_objects.QuestionList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``QuestionList`` provides a means for accessing ``Question`` elements sequentially either one at a time or many at a time.

    Examples: while (ql.hasNext()) { Question question =
    ql.getNextQuestion(); }

    or
      while (ql.hasNext()) {
           Question[] question = al.getNextQuestions(ql.available());
      }



    """

    def get_next_question(self):
        """Gets the next ``Question`` in this list.

        return: (osid.assessment.Question) - the next ``Question`` in
                this list. The ``has_next()`` method should be used to
                test that a next ``Question`` is available before
                calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Question)

    next_question = property(fget=get_next_question)

    @utilities.arguments_not_none
    def get_next_questions(self, n):
        """Gets the next set of ``Question`` elements in this list which must be less than or equal to the number returned from ``available()``.

        arg:    n (cardinal): the number of ``Question`` elements
                requested which should be less than or equal to
                ``available()``
        return: (osid.assessment.Question) - an array of ``Question``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class Answer(abc_assessment_objects.Answer, osid_objects.OsidObject):
    """An ``Answer`` represents the question portion of an assessment item.

    Like all OSID objects, an ``Answer`` is identified by its ``Id`` and
    any persisted references should use the ``Id``.

    """

    _namespace = 'assessment.Answer'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='ANSWER', **kwargs)
        self._catalog_name = 'bank'


    @utilities.arguments_not_none
    def get_answer_record(self, answer_record_type):
        """Gets the answer record corresponding to the given ``Answer`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested records. The ``answer_record_type`` may be the
        ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(answer_record_type)`` is ``true`` .

        arg:    answer_record_type (osid.type.Type): the type of the
                record to retrieve
        return: (osid.assessment.records.AnswerRecord) - the answer
                record
        raise:  NullArgument - ``answer_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(answer_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AnswerForm(abc_assessment_objects.AnswerForm, osid_objects.OsidObjectForm):
    """This is the form for creating and updating ``Answers``."""

    _namespace = 'assessment.Answer'

    def __init__(self, **kwargs):
        osid_objects.OsidObjectForm.__init__(self, object_name='ANSWER', **kwargs)
        self._mdata = default_mdata.get_answer_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""
        osid_objects.OsidObjectForm._init_metadata(self, **kwargs)
    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""
        osid_objects.OsidObjectForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    @utilities.arguments_not_none
    def get_answer_form_record(self, answer_record_type):
        """Gets the ``AnswerFormRecord`` corresponding to the given answer record ``Type``.

        arg:    answer_record_type (osid.type.Type): the answer record
                type
        return: (osid.assessment.records.AnswerFormRecord) - the answer
                record
        raise:  NullArgument - ``answer_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(answer_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AnswerList(abc_assessment_objects.AnswerList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``AnswerList`` provides a means for accessing ``Answer`` elements sequentially either one at a time or many at a time.

    Examples: while (al.hasNext()) { Answer answer = al.getNextAnswer();
    }

    or
      while (al.hasNext()) {
           Answer[] answer = al.getNextAnswers(al.available());
      }



    """

    def get_next_answer(self):
        """Gets the next ``Answer`` in this list.

        return: (osid.assessment.Answer) - the next ``Answer`` in this
                list. The ``has_next()`` method should be used to test
                that a next ``Answer`` is available before calling this
                method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Answer)

    next_answer = property(fget=get_next_answer)

    @utilities.arguments_not_none
    def get_next_answers(self, n):
        """Gets the next set of ``Answer`` elements in this list which must be less than or equal to the number returned from ``available()``.

        arg:    n (cardinal): the number of ``Answer`` elements
                requested which should be less than or equal to
                ``available()``
        return: (osid.assessment.Answer) - an array of ``Answer``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class Item(abc_assessment_objects.Item, osid_objects.OsidObject, osid_markers.Aggregateable):
    """An ``Item`` represents an individual assessment item such as a question.

    Like all OSID objects, a ``Item`` is identified by its ``Id`` and
    any persisted references should use the ``Id``.

    An ``Item`` is composed of a ``Question`` and an ``Answer``.

    """

    _namespace = 'assessment.Item'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='ITEM', **kwargs)
        self._catalog_name = 'bank'


    def get_learning_objective_ids(self):
        """Gets the ``Ids`` of any ``Objectives`` corresponding to this item.

        return: (osid.id.IdList) - the learning objective ``Ids``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    learning_objective_ids = property(fget=get_learning_objective_ids)

    def get_learning_objectives(self):
        """Gets the any ``Objectives`` corresponding to this item.

        return: (osid.learning.ObjectiveList) - the learning objectives
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    learning_objectives = property(fget=get_learning_objectives)

    def get_question_id(self):
        """Gets the ``Id`` of the ``Question``.

        return: (osid.id.Id) - the question ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    question_id = property(fget=get_question_id)

    def get_question(self):
        """Gets the question.

        return: (osid.assessment.Question) - the question
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    question = property(fget=get_question)

    def get_answer_ids(self):
        """Gets the ``Ids`` of the answers.

        Questions may have more than one acceptable answer.

        return: (osid.id.IdList) - the answer ``Ids``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    answer_ids = property(fget=get_answer_ids)

    def get_answers(self):
        """Gets the answers.

        return: (osid.assessment.AnswerList) - the answers
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    answers = property(fget=get_answers)

    @utilities.arguments_not_none
    def get_item_record(self, item_record_type):
        """Gets the item record corresponding to the given ``Item`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested records. The ``item_record_type`` may be the ``Type``
        returned in ``get_record_types()`` or any of its parents in a
        ``Type`` hierarchy where ``has_record_type(item_record_type)``
        is ``true`` .

        arg:    item_record_type (osid.type.Type): the type of the
                record to retrieve
        return: (osid.assessment.records.ItemRecord) - the item record
        raise:  NullArgument - ``item_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(item_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ItemForm(abc_assessment_objects.ItemForm, osid_objects.OsidObjectForm, osid_objects.OsidAggregateableForm):
    """This is the form for creating and updating ``Items``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``ItemAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'assessment.Item'

    def __init__(self, **kwargs):
        osid_objects.OsidObjectForm.__init__(self, object_name='ITEM', **kwargs)
        self._mdata = default_mdata.get_item_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""
        osid_objects.OsidObjectForm._init_metadata(self, **kwargs)
        self._learning_objectives_default = self._mdata['learning_objectives']['default_id_values']

    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""
        osid_objects.OsidObjectForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    def get_learning_objectives_metadata(self):
        """Gets the metadata for learning objectives.

        return: (osid.Metadata) - metadata for the learning objectives
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    learning_objectives_metadata = property(fget=get_learning_objectives_metadata)

    @utilities.arguments_not_none
    def set_learning_objectives(self, objective_ids):
        """Sets the learning objectives.

        arg:    objective_ids (osid.id.Id[]): the learning objective
                ``Ids``
        raise:  InvalidArgument - ``objective_ids`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_learning_objectives(self):
        """Clears the learning objectives.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    learning_objectives = property(fset=set_learning_objectives, fdel=clear_learning_objectives)

    @utilities.arguments_not_none
    def get_item_form_record(self, item_record_type):
        """Gets the ``ItemnFormRecord`` corresponding to the given item record ``Type``.

        arg:    item_record_type (osid.type.Type): the item record type
        return: (osid.assessment.records.ItemFormRecord) - the item
                record
        raise:  NullArgument - ``item_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(item_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ItemList(abc_assessment_objects.ItemList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``ItemList`` provides a means for accessing ``Item`` elements sequentially either one at a time or many at a time.

    Examples: while (il.hasNext()) { Item item = il.getNextItem(); }

    or
      while (il.hasNext()) {
           Item[] items = il.getNextItems(il.available());
      }



    """

    def get_next_item(self):
        """Gets the next ``Item`` in this list.

        return: (osid.assessment.Item) - the next ``Item`` in this list.
                The ``has_next()`` method should be used to test that a
                next ``Item`` is available before calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Item)

    next_item = property(fget=get_next_item)

    @utilities.arguments_not_none
    def get_next_items(self, n):
        """Gets the next set of ``Item`` elements in this list which must be less than or equal to the number returned from ``available()``.

        arg:    n (cardinal): the number of ``Item`` elements requested
                which should be less than or equal to ``available()``
        return: (osid.assessment.Item) - an array of ``Item``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class Assessment(abc_assessment_objects.Assessment, osid_objects.OsidObject):
    """An ``Assessment`` represents a sequence of assessment items.

    Like all OSID objects, an ``Assessment`` is identified by its ``Id``
    and any persisted references should use the ``Id``.

    An ``Assessment`` may have an accompanying rubric used for assessing
    performance. The rubric assessment is established canonically in
    this ``Assessment``.

    """

    _namespace = 'assessment.Assessment'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='ASSESSMENT', **kwargs)
        self._catalog_name = 'bank'


    def get_level_id(self):
        """Gets the ``Id`` of a ``Grade`` corresponding to the assessment difficulty.

        return: (osid.id.Id) - a grade ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    level_id = property(fget=get_level_id)

    def get_level(self):
        """Gets the ``Grade`` corresponding to the assessment difficulty.

        return: (osid.grading.Grade) - the level
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    level = property(fget=get_level)

    def has_rubric(self):
        """Tests if a rubric assessment is associated with this assessment.

        return: (boolean) - ``true`` if a rubric is available, ``false``
                otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_rubric_id(self):
        """Gets the ``Id`` of the rubric.

        return: (osid.id.Id) - an assessment ``Id``
        raise:  IllegalState - ``has_rubric()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rubric_id = property(fget=get_rubric_id)

    def get_rubric(self):
        """Gets the rubric.

        return: (osid.assessment.Assessment) - the assessment
        raise:  IllegalState - ``has_rubric()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rubric = property(fget=get_rubric)

    @utilities.arguments_not_none
    def get_assessment_record(self, assessment_record_type):
        """Gets the assessment record corresponding to the given ``Assessment`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``assessment_record_type`` may be the
        ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(assessment_record_type)`` is ``true`` .

        arg:    assessment_record_type (osid.type.Type): the type of the
                record to retrieve
        return: (osid.assessment.records.AssessmentRecord) - the
                assessment record
        raise:  NullArgument - ``assessment_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_record_type)`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentForm(abc_assessment_objects.AssessmentForm, osid_objects.OsidObjectForm):
    """This is the form for creating and updating ``Assessments``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``AssessmentAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'assessment.Assessment'

    def __init__(self, **kwargs):
        osid_objects.OsidObjectForm.__init__(self, object_name='ASSESSMENT', **kwargs)
        self._mdata = default_mdata.get_assessment_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""
        osid_objects.OsidObjectForm._init_metadata(self, **kwargs)
        self._rubric_default = self._mdata['rubric']['default_id_values'][0]
        self._level_default = self._mdata['level']['default_id_values'][0]

    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""
        osid_objects.OsidObjectForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    def get_level_metadata(self):
        """Gets the metadata for a grade level.

        return: (osid.Metadata) - metadata for the grade level
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['level'])
        # metadata.update({'existing_level_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    level_metadata = property(fget=get_level_metadata)

    @utilities.arguments_not_none
    def set_level(self, grade_id):
        """Sets the level of difficulty expressed as a ``Grade``.

        arg:    grade_id (osid.id.Id): the grade level
        raise:  InvalidArgument - ``grade_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``grade_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_level(self):
        """Clears the grade level.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    level = property(fset=set_level, fdel=clear_level)

    def get_rubric_metadata(self):
        """Gets the metadata for a rubric assessment.

        return: (osid.Metadata) - metadata for the assesment
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['rubric'])
        # metadata.update({'existing_rubric_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    rubric_metadata = property(fget=get_rubric_metadata)

    @utilities.arguments_not_none
    def set_rubric(self, assessment_id):
        """Sets the rubric expressed as another assessment.

        arg:    assessment_id (osid.id.Id): the assessment ``Id``
        raise:  InvalidArgument - ``assessment_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``assessment_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_rubric(self):
        """Clears the rubric.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rubric = property(fset=set_rubric, fdel=clear_rubric)

    @utilities.arguments_not_none
    def get_assessment_form_record(self, assessment_record_type):
        """Gets the ``AssessmentFormRecord`` corresponding to the given assessment record ``Type``.

        arg:    assessment_record_type (osid.type.Type): the assessment
                record type
        return: (osid.assessment.records.AssessmentFormRecord) - the
                assessment record
        raise:  NullArgument - ``assessment_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_record_type)`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentList(abc_assessment_objects.AssessmentList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``AssessmentList`` provides a means for accessing ``Assessment`` elements sequentially either one at a time or many at a time.

    Examples: while (al.hasNext()) { Assessment assessment =
    al.getNextAssessment(); }

    or
      while (al.hasNext()) {
           Assessment[] assessments = al.hetNextAssessments(al.available());
      }



    """

    def get_next_assessment(self):
        """Gets the next ``Assessment`` in this list.

        return: (osid.assessment.Assessment) - the next ``Assessment``
                in this list. The ``has_next()`` method should be used
                to test that a next ``Assessment`` is available before
                calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Assessment)

    next_assessment = property(fget=get_next_assessment)

    @utilities.arguments_not_none
    def get_next_assessments(self, n):
        """Gets the next set of ``Assessment`` elements in this list which must be less than or equal to the number returned from ``available()``.

        arg:    n (cardinal): the number of ``Assessment`` elements
                requested which should be less than or equal to
                ``available()``
        return: (osid.assessment.Assessment) - an array of
                ``Assessment`` elements.The length of the array is less
                than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class AssessmentOffered(abc_assessment_objects.AssessmentOffered, osid_objects.OsidObject, osid_markers.Subjugateable):
    """An ``AssessmentOffered`` represents a sequence of assessment items.

    Like all OSID objects, an ``AssessmentOffered`` is identified by its
    ``Id`` and any persisted references should use the ``Id``.

    """

    _namespace = 'assessment.AssessmentOffered'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='ASSESSMENT_OFFERED', **kwargs)
        self._catalog_name = 'bank'


    def get_assessment_id(self):
        """Gets the assessment ``Id`` corresponding to this assessment offering.

        return: (osid.id.Id) - the assessment id
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_id = property(fget=get_assessment_id)

    def get_assessment(self):
        """Gets the assessment corresponding to this assessment offereng.

        return: (osid.assessment.Assessment) - the assessment
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment = property(fget=get_assessment)

    def get_level_id(self):
        """Gets the ``Id`` of a ``Grade`` corresponding to the assessment difficulty.

        return: (osid.id.Id) - a grade id
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    level_id = property(fget=get_level_id)

    def get_level(self):
        """Gets the ``Grade`` corresponding to the assessment difficulty.

        return: (osid.grading.Grade) - the level
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    level = property(fget=get_level)

    def are_items_sequential(self):
        """Tests if the items or parts in this assessment are taken sequentially.

        return: (boolean) - ``true`` if the items are taken
                sequentially, ``false`` if the items can be skipped and
                revisited
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def are_items_shuffled(self):
        """Tests if the items or parts appear in a random order.

        return: (boolean) - ``true`` if the items appear in a random
                order, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def has_start_time(self):
        """Tests if there is a fixed start time for this assessment.

        return: (boolean) - ``true`` if there is a fixed start time,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_start_time(self):
        """Gets the start time for this assessment.

        return: (osid.calendaring.DateTime) - the designated start time
        raise:  IllegalState - ``has_start_time()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    start_time = property(fget=get_start_time)

    def has_deadline(self):
        """Tests if there is a fixed end time for this assessment.

        return: (boolean) - ``true`` if there is a fixed end time,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_deadline(self):
        """Gets the end time for this assessment.

        return: (osid.calendaring.DateTime) - the designated end time
        raise:  IllegalState - ``has_deadline()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    deadline = property(fget=get_deadline)

    def has_duration(self):
        """Tests if there is a fixed duration for this assessment.

        return: (boolean) - ``true`` if there is a fixed duration,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_duration(self):
        """Gets the duration for this assessment.

        return: (osid.calendaring.Duration) - the duration
        raise:  IllegalState - ``has_duration()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    duration = property(fget=get_duration)

    def is_scored(self):
        """Tests if this assessment will be scored.

        return: (boolean) - ``true`` if this assessment will be scored
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_score_system_id(self):
        """Gets the grade system ``Id`` for the score.

        return: (osid.id.Id) - the grade system ``Id``
        raise:  IllegalState - ``is_scored()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    score_system_id = property(fget=get_score_system_id)

    def get_score_system(self):
        """Gets the grade system for the score.

        return: (osid.grading.GradeSystem) - the grade system
        raise:  IllegalState - ``is_scored()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    score_system = property(fget=get_score_system)

    def is_graded(self):
        """Tests if this assessment will be graded.

        return: (boolean) - ``true`` if this assessment will be graded,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_grade_system_id(self):
        """Gets the grade system ``Id`` for the grade.

        return: (osid.id.Id) - the grade system ``Id``
        raise:  IllegalState - ``is_graded()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system_id = property(fget=get_grade_system_id)

    def get_grade_system(self):
        """Gets the grade system for the grade.

        return: (osid.grading.GradeSystem) - the grade system
        raise:  IllegalState - ``is_graded()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system = property(fget=get_grade_system)

    def has_rubric(self):
        """Tests if a rubric assessment is associated with this assessment.

        return: (boolean) - ``true`` if a rubric is available, ``false``
                otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_rubric_id(self):
        """Gets the ``Id`` of the rubric.

        return: (osid.id.Id) - an assessment offered ``Id``
        raise:  IllegalState - ``has_rubric()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rubric_id = property(fget=get_rubric_id)

    def get_rubric(self):
        """Gets the rubric.

        return: (osid.assessment.AssessmentOffered) - the assessment
                offered
        raise:  IllegalState - ``has_rubric()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rubric = property(fget=get_rubric)

    @utilities.arguments_not_none
    def get_assessment_offered_record(self, assessment_taken_record_type):
        """Gets the assessment offered record corresponding to the given ``AssessmentOffered`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``assessment_offered_record_type`` may be
        the ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(assessment_offered_record_type)`` is ``true``
        .

        arg:    assessment_taken_record_type (osid.type.Type): an
                assessment offered record type
        return: (osid.assessment.records.AssessmentOfferedRecord) - the
                assessment offered record
        raise:  NullArgument - ``assessment_offered_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_offered_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentOfferedForm(abc_assessment_objects.AssessmentOfferedForm, osid_objects.OsidObjectForm, osid_objects.OsidSubjugateableForm):
    """This is the form for creating and updating an ``AssessmentOffered``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``AssessmentOfferedAdminSession``. For each data element that may be
    set, metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'assessment.AssessmentOffered'

    def __init__(self, **kwargs):
        osid_objects.OsidObjectForm.__init__(self, object_name='ASSESSMENT_OFFERED', **kwargs)
        self._mdata = default_mdata.get_assessment_offered_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""
        osid_objects.OsidObjectForm._init_metadata(self, **kwargs)
        self._level_default = self._mdata['level']['default_id_values'][0]
        self._start_time_default = self._mdata['start_time']['default_date_time_values'][0]
        self._grade_system_default = self._mdata['grade_system']['default_id_values'][0]
        self._items_shuffled_default = self._mdata['items_shuffled']['default_boolean_values'][0]
        self._score_system_default = self._mdata['score_system']['default_id_values'][0]
        self._deadline_default = self._mdata['deadline']['default_date_time_values'][0]
        self._duration_default = self._mdata['duration']['default_duration_values'][0]
        self._items_sequential_default = self._mdata['items_sequential']['default_boolean_values'][0]

    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""
        osid_objects.OsidObjectForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    def get_level_metadata(self):
        """Gets the metadata for a grade level.

        return: (osid.Metadata) - metadata for the grade level
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['level'])
        # metadata.update({'existing_level_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    level_metadata = property(fget=get_level_metadata)

    @utilities.arguments_not_none
    def set_level(self, grade_id):
        """Sets the level of difficulty expressed as a ``Grade``.

        arg:    grade_id (osid.id.Id): the grade level
        raise:  InvalidArgument - ``grade_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_level(self):
        """Clears the level.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    level = property(fset=set_level, fdel=clear_level)

    def get_items_sequential_metadata(self):
        """Gets the metadata for sequential operation.

        return: (osid.Metadata) - metadata for the sequential flag
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['items_sequential'])
        # metadata.update({'existing_items_sequential_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    items_sequential_metadata = property(fget=get_items_sequential_metadata)

    @utilities.arguments_not_none
    def set_items_sequential(self, sequential):
        """Sets the items sequential flag.

        arg:    sequential (boolean): ``true`` if the items are taken
                sequentially, ``false`` if the items can be skipped and
                revisited
        raise:  InvalidArgument - ``sequential`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_items_sequential(self):
        """Clears the items sequential flag.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    items_sequential = property(fset=set_items_sequential, fdel=clear_items_sequential)

    def get_items_shuffled_metadata(self):
        """Gets the metadata for shuffling items.

        return: (osid.Metadata) - metadata for the shuffled flag
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['items_shuffled'])
        # metadata.update({'existing_items_shuffled_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    items_shuffled_metadata = property(fget=get_items_shuffled_metadata)

    @utilities.arguments_not_none
    def set_items_shuffled(self, shuffle):
        """Sets the shuffle flag.

        The shuffle flag may be overidden by other assessment sequencing
        rules.

        arg:    shuffle (boolean): ``true`` if the items are shuffled,
                ``false`` if the items appear in the designated order
        raise:  InvalidArgument - ``shuffle`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_items_shuffled(self):
        """Clears the shuffle flag.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    items_shuffled = property(fset=set_items_shuffled, fdel=clear_items_shuffled)

    def get_start_time_metadata(self):
        """Gets the metadata for the assessment start time.

        return: (osid.Metadata) - metadata for the start time
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['start_time'])
        # metadata.update({'existing_start_time_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    start_time_metadata = property(fget=get_start_time_metadata)

    @utilities.arguments_not_none
    def set_start_time(self, start):
        """Sets the assessment start time.

        arg:    start (osid.calendaring.DateTime): assessment start time
        raise:  InvalidArgument - ``start`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_start_time(self):
        """Clears the start time.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    start_time = property(fset=set_start_time, fdel=clear_start_time)

    def get_deadline_metadata(self):
        """Gets the metadata for the assessment deadline.

        return: (osid.Metadata) - metadata for the end time
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['deadline'])
        # metadata.update({'existing_deadline_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    deadline_metadata = property(fget=get_deadline_metadata)

    @utilities.arguments_not_none
    def set_deadline(self, end):
        """Sets the assessment end time.

        arg:    end (timestamp): assessment end time
        raise:  InvalidArgument - ``end`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_deadline(self):
        """Clears the deadline.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    deadline = property(fset=set_deadline, fdel=clear_deadline)

    def get_duration_metadata(self):
        """Gets the metadata for the assessment duration.

        return: (osid.Metadata) - metadata for the duration
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['duration'])
        # metadata.update({'existing_duration_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    duration_metadata = property(fget=get_duration_metadata)

    @utilities.arguments_not_none
    def set_duration(self, duration):
        """Sets the assessment duration.

        arg:    duration (osid.calendaring.Duration): assessment
                duration
        raise:  InvalidArgument - ``duration`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_duration(self):
        """Clears the duration.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    duration = property(fset=set_duration, fdel=clear_duration)

    def get_score_system_metadata(self):
        """Gets the metadata for a score system.

        return: (osid.Metadata) - metadata for the grade system
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['score_system'])
        # metadata.update({'existing_score_system_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    score_system_metadata = property(fget=get_score_system_metadata)

    @utilities.arguments_not_none
    def set_score_system(self, grade_system_id):
        """Sets the scoring system.

        arg:    grade_system_id (osid.id.Id): the grade system
        raise:  InvalidArgument - ``grade_system_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_score_system(self):
        """Clears the score system.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    score_system = property(fset=set_score_system, fdel=clear_score_system)

    def get_grade_system_metadata(self):
        """Gets the metadata for a grading system.

        return: (osid.Metadata) - metadata for the grade system
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['grade_system'])
        # metadata.update({'existing_grade_system_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    grade_system_metadata = property(fget=get_grade_system_metadata)

    @utilities.arguments_not_none
    def set_grade_system(self, grade_system_id):
        """Sets the grading system.

        arg:    grade_system_id (osid.id.Id): the grade system
        raise:  InvalidArgument - ``grade_system_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_system(self):
        """Clears the grading system.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system = property(fset=set_grade_system, fdel=clear_grade_system)

    @utilities.arguments_not_none
    def get_assessment_offered_form_record(self, assessment_offered_record_type):
        """Gets the ``AssessmentOfferedFormRecord`` corresponding to the given assessment record ``Type``.

        arg:    assessment_offered_record_type (osid.type.Type): the
                assessment offered record type
        return: (osid.assessment.records.AssessmentOfferedFormRecord) -
                the assessment offered record
        raise:  NullArgument - ``assessment_offered_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_offered_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentOfferedList(abc_assessment_objects.AssessmentOfferedList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``AssessmentOfferedList`` provides a means for accessing ``AssessmentTaken`` elements sequentially either one at a time or many at a time.

    Examples: while (aol.hasNext()) { AssessmentOffered assessment =
    aol.getNextAssessmentOffered();

    or
      while (aol.hasNext()) {
           AssessmentOffered[] assessments = aol.hetNextAssessmentsOffered(aol.available());
      }



    """

    def get_next_assessment_offered(self):
        """Gets the next ``AssessmentOffered`` in this list.

        return: (osid.assessment.AssessmentOffered) - the next
                ``AssessmentOffered`` in this list. The ``has_next()``
                method should be used to test that a next
                ``AssessmentOffered`` is available before calling this
                method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(AssessmentOffered)

    next_assessment_offered = property(fget=get_next_assessment_offered)

    @utilities.arguments_not_none
    def get_next_assessments_offered(self, n):
        """Gets the next set of ``AssessmentOffered`` elements in this list which must be less than or equal to the number returned from ``available()``.

        arg:    n (cardinal): the number of ``AssessmentOffered``
                elements requested which should be less than or equal to
                ``available()``
        return: (osid.assessment.AssessmentOffered) - an array of
                ``AssessmentOffered`` elements.The length of the array
                is less than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class AssessmentTaken(abc_assessment_objects.AssessmentTaken, osid_objects.OsidObject):
    """Represents a taken assessment or an assessment in progress."""

    _namespace = 'assessment.AssessmentTaken'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='ASSESSMENT_TAKEN', **kwargs)
        self._catalog_name = 'bank'


    def get_assessment_offered_id(self):
        """Gets the ``Id`` of the ``AssessmentOffered``.

        return: (osid.id.Id) - the assessment offered ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_offered_id = property(fget=get_assessment_offered_id)

    def get_assessment_offered(self):
        """Gets the ``AssessmentOffered``.

        return: (osid.assessment.AssessmentOffered) - the assessment
                offered
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_offered = property(fget=get_assessment_offered)

    def get_taker_id(self):
        """Gets the ``Id`` of the resource who took or is taking this assessment.

        return: (osid.id.Id) - the resource ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    taker_id = property(fget=get_taker_id)

    def get_taker(self):
        """Gets the ``Resource`` taking this assessment.

        return: (osid.resource.Resource) - the resource
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    taker = property(fget=get_taker)

    def get_taking_agent_id(self):
        """Gets the ``Id`` of the ``Agent`` who took or is taking the assessment.

        return: (osid.id.Id) - the agent ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    taking_agent_id = property(fget=get_taking_agent_id)

    def get_taking_agent(self):
        """Gets the ``Agent``.

        return: (osid.authentication.Agent) - the agent
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    taking_agent = property(fget=get_taking_agent)

    def has_started(self):
        """Tests if this assessment has begun.

        return: (boolean) - ``true`` if the assessment has begun,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_actual_start_time(self):
        """Gets the time this assessment was started.

        return: (osid.calendaring.DateTime) - the start time
        raise:  IllegalState - ``has_started()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    actual_start_time = property(fget=get_actual_start_time)

    def has_ended(self):
        """Tests if this assessment has ended.

        return: (boolean) - ``true`` if the assessment has ended,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_completion_time(self):
        """Gets the time of this assessment was completed.

        return: (osid.calendaring.DateTime) - the end time
        raise:  IllegalState - ``has_ended()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    completion_time = property(fget=get_completion_time)

    def get_time_spent(self):
        """Gets the total time spent taking this assessment.

        return: (osid.calendaring.Duration) - the total time spent
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    time_spent = property(fget=get_time_spent)

    def get_completion(self):
        """Gets a completion percentage of the assessment.

        return: (cardinal) - the percent complete (0-100)
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    completion = property(fget=get_completion)

    def is_scored(self):
        """Tests if a score is available for this assessment.

        return: (boolean) - ``true`` if a score is available, ``false``
                otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_score_system_id(self):
        """Gets a score system ``Id`` for the assessment.

        return: (osid.id.Id) - the grade system
        raise:  IllegalState - ``is_score()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    score_system_id = property(fget=get_score_system_id)

    def get_score_system(self):
        """Gets a grade system for the score.

        return: (osid.grading.GradeSystem) - the grade system
        raise:  IllegalState - ``is_scored()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    score_system = property(fget=get_score_system)

    def get_score(self):
        """Gets a score for the assessment.

        return: (decimal) - the score
        raise:  IllegalState - ``is_scored()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    score = property(fget=get_score)

    def is_graded(self):
        """Tests if a grade is available for this assessment.

        return: (boolean) - ``true`` if a grade is available, ``false``
                otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_grade_id(self):
        """Gets a grade ``Id`` for the assessment.

        return: (osid.id.Id) - the grade
        raise:  IllegalState - ``is_graded()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_id = property(fget=get_grade_id)

    def get_grade(self):
        """Gets a grade for the assessment.

        return: (osid.grading.Grade) - the grade
        raise:  IllegalState - ``is_graded()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade = property(fget=get_grade)

    def get_feedback(self):
        """Gets any overall comments available for this assessment by the grader.

        return: (osid.locale.DisplayText) - comments
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    feedback = property(fget=get_feedback)

    def has_rubric(self):
        """Tests if a rubric assessment is associated with this assessment.

        return: (boolean) - ``true`` if a rubric is available, ``false``
                otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_rubric_id(self):
        """Gets the ``Id`` of the rubric.

        return: (osid.id.Id) - an assessment taken ``Id``
        raise:  IllegalState - ``has_rubric()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rubric_id = property(fget=get_rubric_id)

    def get_rubric(self):
        """Gets the rubric.

        return: (osid.assessment.AssessmentTaken) - the assessment taken
        raise:  IllegalState - ``has_rubric()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rubric = property(fget=get_rubric)

    @utilities.arguments_not_none
    def get_assessment_taken_record(self, assessment_taken_record_type):
        """Gets the assessment taken record corresponding to the given ``AssessmentTaken`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``assessment_taken_record_type`` may be
        the ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(assessment_taken_record_type)`` is ``true`` .

        arg:    assessment_taken_record_type (osid.type.Type): an
                assessment taken record type
        return: (osid.assessment.records.AssessmentTakenRecord) - the
                assessment taken record
        raise:  NullArgument - ``assessment_taken_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_taken_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentTakenForm(abc_assessment_objects.AssessmentTakenForm, osid_objects.OsidObjectForm):
    """This is the form for creating and updating an ``AssessmentTaken``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``AssessmentTakenAdminSession``. For each data element that may be
    set, metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'assessment.AssessmentTaken'

    def __init__(self, **kwargs):
        osid_objects.OsidObjectForm.__init__(self, object_name='ASSESSMENT_TAKEN', **kwargs)
        self._mdata = default_mdata.get_assessment_taken_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""
        osid_objects.OsidObjectForm._init_metadata(self, **kwargs)
        self._taker_default = self._mdata['taker']['default_id_values'][0]

    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""
        osid_objects.OsidObjectForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    def get_taker_metadata(self):
        """Gets the metadata for a resource to manually set which resource will be taking the assessment.

        return: (osid.Metadata) - metadata for the resource
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['taker'])
        # metadata.update({'existing_taker_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    taker_metadata = property(fget=get_taker_metadata)

    @utilities.arguments_not_none
    def set_taker(self, resource_id):
        """Sets the resource who will be taking this assessment.

        arg:    resource_id (osid.id.Id): the resource Id
        raise:  InvalidArgument - ``resource_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_taker(self):
        """Clears the resource.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    taker = property(fset=set_taker, fdel=clear_taker)

    @utilities.arguments_not_none
    def get_assessment_taken_form_record(self, assessment_taken_record_type):
        """Gets the ``AssessmentTakenFormRecord`` corresponding to the given assessment taken record ``Type``.

        arg:    assessment_taken_record_type (osid.type.Type): the
                assessment taken record type
        return: (osid.assessment.records.AssessmentTakenFormRecord) -
                the assessment taken record
        raise:  NullArgument - ``assessment_taken_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_taken_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentTakenList(abc_assessment_objects.AssessmentTakenList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``AssessmentTakenList`` provides a means for accessing ``AssessmentTaken`` elements sequentially either one at a time or many at a time.

    Examples: while (atl.hasNext()) { AssessmentTaken assessment =
    atl.getNextAssessmentTaken();

    or
      while (atl.hasNext()) {
           AssessmentTaken[] assessments = atl.hetNextAssessmentsTaken(atl.available());
      }



    """

    def get_next_assessment_taken(self):
        """Gets the next ``AssessmentTaken`` in this list.

        return: (osid.assessment.AssessmentTaken) - the next
                ``AssessmentTaken`` in this list. The ``has_next()``
                method should be used to test that a next
                ``AssessmentTaken`` is available before calling this
                method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(AssessmentTaken)

    next_assessment_taken = property(fget=get_next_assessment_taken)

    @utilities.arguments_not_none
    def get_next_assessments_taken(self, n):
        """Gets the next set of ``AssessmentTaken`` elements in this list which must be less than or equal to the number returned from ``available()``.

        arg:    n (cardinal): the number of ``AssessmentTaken`` elements
                requested which should be less than or equal to
                ``available()``
        return: (osid.assessment.AssessmentTaken) - an array of
                ``AssessmentTaken`` elements.The length of the array is
                less than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class AssessmentSection(abc_assessment_objects.AssessmentSection, osid_objects.OsidObject):
    """Represents an assessment section.

    An assessment section represents a cluster of questions used to
    organize the execution of an assessment. The section is the student
    aspect of an assessment part.

    """

    _namespace = 'assessment.AssessmentSection'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='ASSESSMENT_SECTION', **kwargs)
        self._catalog_name = 'bank'


    def get_assessment_taken_id(self):
        """Gets the ``Id`` of the ``AssessmentTaken``.

        return: (osid.id.Id) - the assessment taken ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_taken_id = property(fget=get_assessment_taken_id)

    def get_assessment_taken(self):
        """Gets the ``AssessmentTakeb``.

        return: (osid.assessment.AssessmentTaken) - the assessment taken
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_taken = property(fget=get_assessment_taken)

    def has_allocated_time(self):
        """Tests if this section must be completed within an allocated time.

        return: (boolean) - ``true`` if this section has an allocated
                time, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_allocated_time(self):
        """Gets the allocated time for this section.

        return: (osid.calendaring.Duration) - allocated time
        raise:  IllegalState - ``has_allocated_time()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    allocated_time = property(fget=get_allocated_time)

    def are_items_sequential(self):
        """Tests if the items or parts in this section are taken sequentially.

        return: (boolean) - ``true`` if the items are taken
                sequentially, ``false`` if the items can be skipped and
                revisited
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def are_items_shuffled(self):
        """Tests if the items or parts appear in a random order.

        return: (boolean) - ``true`` if the items appear in a random
                order, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assessment_section_record(self, assessment_section_record_type):
        """Gets the assessment section record corresponding to the given ``AssessmentSection`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``assessment_section_record_type`` may be
        the ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(assessment_section_record_type)`` is ``true``
        .

        arg:    assessment_section_record_type (osid.type.Type): an
                assessment section record type
        return: (osid.assessment.records.AssessmentSectionRecord) - the
                assessment section record
        raise:  NullArgument - ``assessment_section_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_section_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentSectionList(abc_assessment_objects.AssessmentSectionList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``AssessmentSectionList`` provides a means for accessing ``AssessmentSection`` elements sequentially either one at a time or many at a time.

    Examples: while (asl.hasNext()) { AssessmentSection section =
    asl.getNextAssessmentSection();

    or
      while (asl.hasNext()) {
           AssessmentSection[] sections = asl.hetNextAssessmentSections(asl.available());
      }



    """

    def get_next_assessment_section(self):
        """Gets the next ``AssessmentSection`` in this list.

        return: (osid.assessment.AssessmentSection) - the next
                ``AssessmentSection`` in this list. The ``has_next()``
                method should be used to test that a next
                ``AssessmentSection`` is available before calling this
                method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(AssessmentSection)

    next_assessment_section = property(fget=get_next_assessment_section)

    @utilities.arguments_not_none
    def get_next_assessment_sections(self, n):
        """Gets the next set of ``AssessmentSection`` elements in this list which must be less than or equal to the number returned from ``available()``.

        arg:    n (cardinal): the number of ``AssessmentSection``
                elements requested which should be less than or equal to
                ``available()``
        return: (osid.assessment.AssessmentSection) - an array of
                ``AssessmentSection`` elements.The length of the array
                is less than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class Bank(abc_assessment_objects.Bank, osid_objects.OsidCatalog):
    """A bank defines a collection of assessments and items."""

    _namespace = 'assessment.Bank'

    def __init__(self, **kwargs):
        # self._record_type_data_sets = get_registry('BANK_RECORD_TYPES', runtime)
        osid_objects.OsidCatalog.__init__(self, object_name='BANK', **kwargs)

    @utilities.arguments_not_none
    def get_bank_record(self, bank_record_type):
        """Gets the bank record corresponding to the given ``Bank`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``bank_record_type`` may be the ``Type``
        returned in ``get_record_types()`` or any of its parents in a
        ``Type`` hierarchy where ``has_record_type(bank_record_type)``
        is ``true`` .

        arg:    bank_record_type (osid.type.Type): a bank record type
        return: (osid.assessment.records.BankRecord) - the bank record
        raise:  NullArgument - ``bank_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(bank_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class BankForm(abc_assessment_objects.BankForm, osid_objects.OsidCatalogForm):
    """This is the form for creating and updating banks.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``BankAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'assessment.Bank'

    def __init__(self, **kwargs):
        osid_objects.OsidCatalogForm.__init__(self, object_name='BANK', **kwargs)
        self._mdata = default_mdata.get_bank_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    @utilities.arguments_not_none
    def get_bank_form_record(self, bank_record_type):
        """Gets the ``BankFormRecord`` corresponding to the given bank record ``Type``.

        arg:    bank_record_type (osid.type.Type): a bank record type
        return: (osid.assessment.records.BankFormRecord) - the bank
                record
        raise:  NullArgument - ``bank_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(bank_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class BankList(abc_assessment_objects.BankList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``BankList`` provides a means for accessing ``Bank`` elements sequentially either one at a time or many at a time.

    Examples: while (bl.hasNext()) { Bank bank = bl.getNextBank(); }

    or
      while (bl.hasNext()) {
           Bank[] banks = bl.getNextBanks(bl.available());
      }



    """

    def get_next_bank(self):
        """Gets the next ``Bank`` in this list.

        return: (osid.assessment.Bank) - the next ``Bank`` in this list.
                The ``has_next()`` method should be used to test that a
                next ``Bank`` is available before calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Bank)

    next_bank = property(fget=get_next_bank)

    @utilities.arguments_not_none
    def get_next_banks(self, n):
        """Gets the next set of ``Bank`` elements in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``Bank`` elements requested
                which must be less than or equal to ``available()``
        return: (osid.assessment.Bank) - an array of ``Bank``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class BankNode(abc_assessment_objects.BankNode, osid_objects.OsidNode):
    """This interface is a container for a partial hierarchy retrieval.

    The number of hierarchy levels traversable through this interface
    depend on the number of levels requested in the
    ``BankHierarchySession``.

    """

    def get_bank(self):
        """Gets the ``Bank`` at this node.

        return: (osid.assessment.Bank) - the bank represented by this
                node
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank = property(fget=get_bank)

    def get_parent_bank_nodes(self):
        """Gets the parents of this bank.

        return: (osid.assessment.BankNodeList) - the parents of this
                node
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    parent_bank_nodes = property(fget=get_parent_bank_nodes)

    def get_child_bank_nodes(self):
        """Gets the children of this bank.

        return: (osid.assessment.BankNodeList) - the children of this
                node
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    child_bank_nodes = property(fget=get_child_bank_nodes)


class BankNodeList(abc_assessment_objects.BankNodeList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``BankNodeList`` provides a means for accessing ``BankNode`` elements sequentially either one at a time or many at a time.

    Examples: while (bnl.hasNext()) { BankNode node =
    bnl.getNextBankNode(); }

    or
      while (bnl.hasNext()) {
           BankNode[] nodes = bnl.getNextBankNodes(bnl.available());
      }



    """

    def get_next_bank_node(self):
        """Gets the next ``BankNode`` in this list.

        return: (osid.assessment.BankNode) - the next ``BankNode`` in
                this list. The ``has_next()`` method should be used to
                test that a next ``BankNode`` is available before
                calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(BankNode)

    next_bank_node = property(fget=get_next_bank_node)

    @utilities.arguments_not_none
    def get_next_bank_nodes(self, n):
        """Gets the next set of ``BankNode`` elements in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``BankNode`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.assessment.BankNode) - an array of ``BanklNode``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class ResponseList(abc_assessment_objects.ResponseList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``ResponseList`` provides a means for accessing ``Response`` elements sequentially either one at a time or many at a time.

    Examples: while (rl.hasNext()) { Response response =
    rl.getNextResponse(); }

    or
      while (rl.hasNext()) {
           Response[] responses = rl.getNextResponses(rl.available());
      }



    """

    def get_next_response(self):
        """Gets the next ``Response`` in this list.

        return: (osid.assessment.Response) - the next ``Response`` in
                this list. The ``has_next()`` method should be used to
                test that a next ``Response`` is available before
                calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Response)

    next_response = property(fget=get_next_response)

    @utilities.arguments_not_none
    def get_next_responses(self, n):
        """Gets the next set of ``Response`` elements in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``Response`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.assessment.Response) - an array of ``Response``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


