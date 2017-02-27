"""GStudio implementations of grading objects."""

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
import numpy as np


from decimal import Decimal


from . import default_mdata
from .. import utilities
from ...abstract_osid.grading import objects as abc_grading_objects
from ..osid import markers as osid_markers
from ..osid import objects as osid_objects
from ..osid.metadata import Metadata
from ..primitives import Id
from ..resource.simple_agent import Agent
from ..utilities import get_registry
from ..utilities import now_map
from ..utilities import update_display_text_defaults
from dlkit.abstract_osid.osid import errors
from dlkit.primordium.calendaring.primitives import DateTime
from dlkit.primordium.id.primitives import Id




class Grade(abc_grading_objects.Grade, osid_objects.OsidObject, osid_markers.Subjugateable):
    """A ``Grade``.

    Grades represent qualified performance levels defined within some
    grading system.

    """

    _namespace = 'grading.Grade'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='GRADE', **kwargs)
        self._catalog_name = 'gradebook'


    def get_grade_system_id(self):
        """Gets the ``GradeSystem Id`` in which this grade belongs.

        return: (osid.id.Id) - the grade system ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system_id = property(fget=get_grade_system_id)

    def get_grade_system(self):
        """Gets the ``GradeSystem`` in which this grade belongs.

        return: (osid.grading.GradeSystem) - the grade system
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system = property(fget=get_grade_system)

    def get_input_score_start_range(self):
        """Gets the low end of the input score range equivalent to this grade.

        return: (decimal) - the start range
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystem.get_lowest_numeric_score_template
        if self._my_map['inputScoreStartRange'] is None:
            return None
        else:
            return Decimal(str(self._my_map['inputScoreStartRange']))

    input_score_start_range = property(fget=get_input_score_start_range)

    def get_input_score_end_range(self):
        """Gets the high end of the input score range equivalent to this grade.

        return: (decimal) - the end range
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystem.get_lowest_numeric_score_template
        if self._my_map['inputScoreEndRange'] is None:
            return None
        else:
            return Decimal(str(self._my_map['inputScoreEndRange']))

    input_score_end_range = property(fget=get_input_score_end_range)

    def get_output_score(self):
        """Gets the output score for this grade used for calculating cumultives or performing articulation.

        return: (decimal) - the output score
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystem.get_lowest_numeric_score_template
        if self._my_map['outputScore'] is None:
            return None
        else:
            return Decimal(str(self._my_map['outputScore']))

    output_score = property(fget=get_output_score)

    @utilities.arguments_not_none
    def get_grade_record(self, grade_record_type):
        """Gets the grade record corresponding to the given ``Grade`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``grade_record_type`` may be the ``Type``
        returned in ``get_record_types()`` or any of its parents in a
        ``Type`` hierarchy where ``has_record_type(grade_record_type)``
        is ``true`` .

        arg:    grade_record_type (osid.type.Type): the type of the
                record to retrieve
        return: (osid.grading.records.GradeRecord) - the grade record
        raise:  NullArgument - ``grade_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(grade_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradeForm(abc_grading_objects.GradeForm, osid_objects.OsidObjectForm, osid_objects.OsidSubjugateableForm):
    """This is the form for creating and updating ``Grades``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``GradeAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'grading.Grade'

    def __init__(self, **kwargs):
        osid_objects.OsidObjectForm.__init__(self, object_name='GRADE', **kwargs)
        self._mdata = default_mdata.get_grade_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""
        osid_objects.OsidObjectForm._init_metadata(self, **kwargs)
        self._output_score_default = self._mdata['output_score']['default_decimal_values'][0]
        self._input_score_end_range_default = self._mdata['input_score_end_range']['default_decimal_values'][0]
        self._input_score_start_range_default = self._mdata['input_score_start_range']['default_decimal_values'][0]

    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""
        osid_objects.OsidObjectForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    def get_input_score_start_range_metadata(self):
        """Gets the metadata for the input score start range.

        return: (osid.Metadata) - metadata for the input score start
                range
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['input_score_start_range'])
        # metadata.update({'existing_input_score_start_range_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    input_score_start_range_metadata = property(fget=get_input_score_start_range_metadata)

    @utilities.arguments_not_none
    def set_input_score_start_range(self, score):
        """Sets the input score start range.

        arg:    score (decimal): the new start range
        raise:  InvalidArgument - ``score`` is invalid
        raise:  NoAccess - ``range`` cannot be modified
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystemForm.set_lowest_numeric_score
        if self.get_input_score_start_range_metadata().is_read_only():
            raise errors.NoAccess()
        try:
            score = float(score)
        except ValueError:
            raise errors.InvalidArgument()
        if not self._is_valid_decimal(score, self.get_input_score_start_range_metadata()):
            raise errors.InvalidArgument()
        self._my_map['inputScoreStartRange'] = score

    def clear_input_score_start_range(self):
        """Clears the input score start.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystemForm.clear_lowest_numeric_score
        if (self.get_input_score_start_range_metadata().is_read_only() or
                self.get_input_score_start_range_metadata().is_required()):
            raise errors.NoAccess()
        self._my_map['inputScoreStartRange'] = self._input_score_start_range_default

    input_score_start_range = property(fset=set_input_score_start_range, fdel=clear_input_score_start_range)

    def get_input_score_end_range_metadata(self):
        """Gets the metadata for the input score start range.

        return: (osid.Metadata) - metadata for the input score start
                range
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['input_score_end_range'])
        # metadata.update({'existing_input_score_end_range_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    input_score_end_range_metadata = property(fget=get_input_score_end_range_metadata)

    @utilities.arguments_not_none
    def set_input_score_end_range(self, score):
        """Sets the input score start range.

        arg:    score (decimal): the new start range
        raise:  InvalidArgument - ``score`` is invalid
        raise:  NoAccess - ``range`` cannot be modified
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystemForm.set_lowest_numeric_score
        if self.get_input_score_end_range_metadata().is_read_only():
            raise errors.NoAccess()
        try:
            score = float(score)
        except ValueError:
            raise errors.InvalidArgument()
        if not self._is_valid_decimal(score, self.get_input_score_end_range_metadata()):
            raise errors.InvalidArgument()
        self._my_map['inputScoreEndRange'] = score

    def clear_input_score_end_range(self):
        """Clears the input score start.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystemForm.clear_lowest_numeric_score
        if (self.get_input_score_end_range_metadata().is_read_only() or
                self.get_input_score_end_range_metadata().is_required()):
            raise errors.NoAccess()
        self._my_map['inputScoreEndRange'] = self._input_score_end_range_default

    input_score_end_range = property(fset=set_input_score_end_range, fdel=clear_input_score_end_range)

    def get_output_score_metadata(self):
        """Gets the metadata for the output score start range.

        return: (osid.Metadata) - metadata for the output score start
                range
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['output_score'])
        # metadata.update({'existing_output_score_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    output_score_metadata = property(fget=get_output_score_metadata)

    @utilities.arguments_not_none
    def set_output_score(self, score):
        """Sets the output score.

        arg:    score (decimal): the new output score
        raise:  InvalidArgument - ``score`` is invalid
        raise:  NoAccess - ``score`` cannot be modified
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystemForm.set_lowest_numeric_score
        if self.get_output_score_metadata().is_read_only():
            raise errors.NoAccess()
        try:
            score = float(score)
        except ValueError:
            raise errors.InvalidArgument()
        if not self._is_valid_decimal(score, self.get_output_score_metadata()):
            raise errors.InvalidArgument()
        self._my_map['outputScore'] = score

    def clear_output_score(self):
        """Clears the output score.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystemForm.clear_lowest_numeric_score
        if (self.get_output_score_metadata().is_read_only() or
                self.get_output_score_metadata().is_required()):
            raise errors.NoAccess()
        self._my_map['outputScore'] = self._output_score_default

    output_score = property(fset=set_output_score, fdel=clear_output_score)

    @utilities.arguments_not_none
    def get_grade_form_record(self, grade_record_type):
        """Gets the ``GradeFormRecord`` corresponding to the given grade record ``Type``.

        arg:    grade_record_type (osid.type.Type): the grade record
                type
        return: (osid.grading.records.GradeFormRecord) - the grade form
                record
        raise:  NullArgument - ``grade_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(grade_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradeList(abc_grading_objects.GradeList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``GradeList`` provides a means for accessing ``Grade`` elements sequentially either one at a time or many at a time.

    Examples: while (gl.hasNext()) { Grade grade = gl.getNextGrade(); }

    or
      while (gl.hasNext()) {
           Grade[] grades = gl.getNextGrades(gl.available());
      }



    """

    def get_next_grade(self):
        """Gets the next ``Grade`` in this list.

        return: (osid.grading.Grade) - the next ``Grade`` in this list.
                The ``has_next()`` method should be used to test that a
                next ``Grade`` is available before calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Grade)

    next_grade = property(fget=get_next_grade)

    @utilities.arguments_not_none
    def get_next_grades(self, n):
        """Gets the next set of ``Grade`` elements in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``Grade`` elements requested
                which must be less than or equal to ``available()``
        return: (osid.grading.Grade) - an array of ``Grade``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class GradeSystem(abc_grading_objects.GradeSystem, osid_objects.OsidObject, osid_markers.Aggregateable):
    """A ``GradeSystem`` represents a grading system.

    The system can be based on assigned Grades or based on a numeric
    scale.

    """

    _namespace = 'grading.GradeSystem'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='GRADE_SYSTEM', **kwargs)
        self._catalog_name = 'gradebook'


    def is_based_on_grades(self):
        """Tests if the grading system is based on grades.

        return: (boolean) - true if the grading system is based on
                grades, ``false`` if the system is a numeric score
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_grade_ids(self):
        """Gets the grade ``Ids`` in this system ranked from highest to lowest.

        return: (osid.id.IdList) - the list of grades ``Ids``
        raise:  IllegalState - ``is_based_on_grades()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_ids = property(fget=get_grade_ids)

    def get_grades(self):
        """Gets the grades in this system ranked from highest to lowest.

        return: (osid.grading.GradeList) - the list of grades
        raise:  IllegalState - ``is_based_on_grades()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grades = property(fget=get_grades)

    def get_lowest_numeric_score(self):
        """Gets the lowest number in a numeric grading system.

        return: (decimal) - the lowest number
        raise:  IllegalState - ``is_based_on_grades()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self.is_based_on_grades():
            raise errors.IllegalState('This GradeSystem is based on grades')
        if self._my_map['lowestNumericScore'] is None:
            return None
        else:
            return Decimal(str(self._my_map['lowestNumericScore']))

    lowest_numeric_score = property(fget=get_lowest_numeric_score)

    def get_numeric_score_increment(self):
        """Gets the incremental step.

        return: (decimal) - the increment
        raise:  IllegalState - ``is_based_on_grades()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self.is_based_on_grades():
            raise errors.IllegalState('This GradeSystem is based on grades')
        if self._my_map['numericScoreIncrement'] is None:
            return None
        else:
            return Decimal(str(self._my_map['numericScoreIncrement']))

    numeric_score_increment = property(fget=get_numeric_score_increment)

    def get_highest_numeric_score(self):
        """Gets the highest number in a numeric grading system.

        return: (decimal) - the highest number
        raise:  IllegalState - ``is_based_on_grades()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self.is_based_on_grades():
            raise errors.IllegalState('This GradeSystem is based on grades')
        if self._my_map['highestNumericScore'] is None:
            return None
        else:
            return Decimal(str(self._my_map['highestNumericScore']))

    highest_numeric_score = property(fget=get_highest_numeric_score)

    @utilities.arguments_not_none
    def get_grade_system_record(self, grade_system_record_type):
        """Gets the grade system record corresponding to the given ``GradeSystem`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``grade_system_record_type`` may be the
        ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(grade_system_record_type)`` is ``true`` .

        arg:    grade_system_record_type (osid.type.Type): the type of
                the record to retrieve
        return: (osid.grading.records.GradeSystemRecord) - the grade
                system record
        raise:  NullArgument - ``grade_system_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(grade_system_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_object_map(self):
        obj_map = dict(self._my_map)
        obj_map['grades'] = []
        for grade in self.get_grades():
            obj_map['grades'].append(grade.get_object_map())
        return osid_objects.OsidObject.get_object_map(self, obj_map)

    object_map = property(fget=get_object_map)


class GradeSystemForm(abc_grading_objects.GradeSystemForm, osid_objects.OsidObjectForm, osid_objects.OsidAggregateableForm):
    """This is the form for creating and updating ``GradeSystems``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``GradeSystemAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'grading.GradeSystem'

    def __init__(self, **kwargs):
        osid_objects.OsidObjectForm.__init__(self, object_name='GRADE_SYSTEM', **kwargs)
        self._mdata = default_mdata.get_grade_system_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""
        osid_objects.OsidObjectForm._init_metadata(self, **kwargs)
        self._numeric_score_increment_default = self._mdata['numeric_score_increment']['default_decimal_values'][0]
        self._lowest_numeric_score_default = self._mdata['lowest_numeric_score']['default_decimal_values'][0]
        self._based_on_grades_default = self._mdata['based_on_grades']['default_boolean_values'][0]
        self._highest_numeric_score_default = self._mdata['highest_numeric_score']['default_decimal_values'][0]

    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""
        osid_objects.OsidObjectForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    def get_based_on_grades_metadata(self):
        """Gets the metadata for a grade-based designation.

        return: (osid.Metadata) - metadata for the grade-based
                designation
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['based_on_grades'])
        # metadata.update({'existing_based_on_grades_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    based_on_grades_metadata = property(fget=get_based_on_grades_metadata)

    @utilities.arguments_not_none
    def set_based_on_grades(self, grades):
        """Sets the grade-based designation.

        arg:    grades (boolean): the grade-based designation
        raise:  InvalidArgument - ``grades`` is invalid
        raise:  NoAccess - ``grades`` cannot be modified
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_based_on_grades(self):
        """Clears the based on grades designation.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    based_on_grades = property(fset=set_based_on_grades, fdel=clear_based_on_grades)

    def get_lowest_numeric_score_metadata(self):
        """Gets the metadata for the lowest numeric score.

        return: (osid.Metadata) - metadata for the lowest numeric score
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['lowest_numeric_score'])
        # metadata.update({'existing_lowest_numeric_score_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    lowest_numeric_score_metadata = property(fget=get_lowest_numeric_score_metadata)

    @utilities.arguments_not_none
    def set_lowest_numeric_score(self, score):
        """Sets the lowest numeric score.

        arg:    score (decimal): the lowest numeric score
        raise:  InvalidArgument - ``score`` is invalid
        raise:  NoAccess - ``score`` cannot be modified
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystemForm.set_lowest_numeric_score
        if self.get_lowest_numeric_score_metadata().is_read_only():
            raise errors.NoAccess()
        try:
            score = float(score)
        except ValueError:
            raise errors.InvalidArgument()
        if not self._is_valid_decimal(score, self.get_lowest_numeric_score_metadata()):
            raise errors.InvalidArgument()
        self._my_map['lowestNumericScore'] = score

    def clear_lowest_numeric_score(self):
        """Clears the lowest score.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystemForm.clear_lowest_numeric_score
        if (self.get_lowest_numeric_score_metadata().is_read_only() or
                self.get_lowest_numeric_score_metadata().is_required()):
            raise errors.NoAccess()
        self._my_map['lowestNumericScore'] = self._lowest_numeric_score_default

    lowest_numeric_score = property(fset=set_lowest_numeric_score, fdel=clear_lowest_numeric_score)

    def get_numeric_score_increment_metadata(self):
        """Gets the metadata for the lowest numeric score.

        return: (osid.Metadata) - metadata for the lowest numeric score
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['numeric_score_increment'])
        # metadata.update({'existing_numeric_score_increment_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    numeric_score_increment_metadata = property(fget=get_numeric_score_increment_metadata)

    @utilities.arguments_not_none
    def set_numeric_score_increment(self, increment):
        """Sets the numeric score increment.

        arg:    increment (decimal): the numeric score increment
        raise:  InvalidArgument - ``increment`` is invalid
        raise:  NoAccess - ``increment`` cannot be modified
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystemForm.set_lowest_numeric_score
        if self.get_numeric_score_increment_metadata().is_read_only():
            raise errors.NoAccess()
        try:
            increment = float(increment)
        except ValueError:
            raise errors.InvalidArgument()
        if not self._is_valid_decimal(increment, self.get_numeric_score_increment_metadata()):
            raise errors.InvalidArgument()
        self._my_map['numericScoreIncrement'] = increment

    def clear_numeric_score_increment(self):
        """Clears the numeric score increment.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystemForm.clear_lowest_numeric_score
        if (self.get_numeric_score_increment_metadata().is_read_only() or
                self.get_numeric_score_increment_metadata().is_required()):
            raise errors.NoAccess()
        self._my_map['numericScoreIncrement'] = self._numeric_score_increment_default

    numeric_score_increment = property(fset=set_numeric_score_increment, fdel=clear_numeric_score_increment)

    def get_highest_numeric_score_metadata(self):
        """Gets the metadata for the highest numeric score.

        return: (osid.Metadata) - metadata for the highest numeric score
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['highest_numeric_score'])
        # metadata.update({'existing_highest_numeric_score_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    highest_numeric_score_metadata = property(fget=get_highest_numeric_score_metadata)

    @utilities.arguments_not_none
    def set_highest_numeric_score(self, score):
        """Sets the highest numeric score.

        arg:    score (decimal): the highest numeric score
        raise:  InvalidArgument - ``score`` is invalid
        raise:  NoAccess - ``score`` cannot be modified
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystemForm.set_lowest_numeric_score
        if self.get_highest_numeric_score_metadata().is_read_only():
            raise errors.NoAccess()
        try:
            score = float(score)
        except ValueError:
            raise errors.InvalidArgument()
        if not self._is_valid_decimal(score, self.get_highest_numeric_score_metadata()):
            raise errors.InvalidArgument()
        self._my_map['highestNumericScore'] = score

    def clear_highest_numeric_score(self):
        """Clears the highest numeric score.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystemForm.clear_lowest_numeric_score
        if (self.get_highest_numeric_score_metadata().is_read_only() or
                self.get_highest_numeric_score_metadata().is_required()):
            raise errors.NoAccess()
        self._my_map['highestNumericScore'] = self._highest_numeric_score_default

    highest_numeric_score = property(fset=set_highest_numeric_score, fdel=clear_highest_numeric_score)

    @utilities.arguments_not_none
    def get_grade_system_form_record(self, grade_system_record_type):
        """Gets the ``GradeSystemFormRecord`` corresponding to the given grade system record ``Type``.

        arg:    grade_system_record_type (osid.type.Type): the grade
                system record type
        return: (osid.grading.records.GradeSystemFormRecord) - the grade
                system form record
        raise:  NullArgument - ``grade_system_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(grade_system_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradeSystemList(abc_grading_objects.GradeSystemList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``GradeSystemList`` provides a means for accessing ``GradeSystem`` elements sequentially either one at a time or many at a time.

    Examples: while (gsl.hasNext()) { GradeSystem system =
    gsl.getNextGradeSystem(); }

    or
      while (gsl.hasNext()) {
           GradeSystem[] systems = gsl.getNextGradeSystems(gsl.available());
      }



    """

    def get_next_grade_system(self):
        """Gets the next ``GradeSystem`` in this list.

        return: (osid.grading.GradeSystem) - the next ``GradeSystem`` in
                this list. The ``has_next()`` method should be used to
                test that a next ``GradeSystem`` is available before
                calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(GradeSystem)

    next_grade_system = property(fget=get_next_grade_system)

    @utilities.arguments_not_none
    def get_next_grade_systems(self, n):
        """Gets the next set of ``GradeSystem`` elements in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``GradeSystem`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.grading.GradeSystem) - an array of ``GradeSystem``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class GradeEntry(abc_grading_objects.GradeEntry, osid_objects.OsidRelationship):
    """A ``GradeEntry`` represents an entry in a ``Gradebook``."""

    _namespace = 'grading.GradeEntry'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='GRADE_ENTRY', **kwargs)
        self._catalog_name = 'gradebook'


    def get_gradebook_column_id(self):
        """Gets the ``Id`` of the ``GradebookColumn``.

        return: (osid.id.Id) - the ``Id`` of the ``GradebookColumn``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_column_id = property(fget=get_gradebook_column_id)

    def get_gradebook_column(self):
        """Gets the ``GradebookColumn``.

        return: (osid.grading.GradebookColumn) - the ``GradebookColumn``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_column = property(fget=get_gradebook_column)

    def get_key_resource_id(self):
        """Gets the ``Id`` of the key resource of this entry.

        The key resource may be a student or other applicable key to
        identify a row of grading entries.

        return: (osid.id.Id) - ``Id`` of the key resource
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._my_map['resourceId']

    key_resource_id = property(fget=get_key_resource_id)

    def get_key_resource(self):
        """Gets the key resource of this entry.

        The key resource may be a student or other applicable key to
        identify a row of grading entries.

        return: (osid.resource.Resource) - the key resource
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    key_resource = property(fget=get_key_resource)

    def is_derived(self):
        """Tests if this is a calculated entry.

        return: (boolean) - ``true`` if this entry is a calculated
                entry, ``false`` otherwise. If ``true,`` then
                ``overrides_calculated_entry()`` must be ``false``.
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def overrides_calculated_entry(self):
        """Tests if this is a manual entry that overrides a calculated entry.

        return: (boolean) - ``true`` if this entry overrides a
                calculated entry, ``false`` otherwise. If ``true,`` then
                ``is_derived()`` must be ``false``.
        *compliance: mandatory -- This method must be implemented.*

        """
        return bool(self._my_map('overriddenCalculatedEntryId'))

    def get_overridden_calculated_entry_id(self):
        """Gets the calculated entry ``Id`` this entry overrides.

        return: (osid.id.Id) - the calculated entry ``Id``
        raise:  IllegalState - ``overrides_derived_entry()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        if not self.overrides_calculated_entry():
            raise errors.IllegalState()
        return self._my_map['overriddenCalculatedEntryId']

    overridden_calculated_entry_id = property(fget=get_overridden_calculated_entry_id)

    def get_overridden_calculated_entry(self):
        """Gets the calculated entry this entry overrides.

        return: (osid.grading.GradeEntry) - the calculated entry
        raise:  IllegalState - ``overrides_calculated_entry()`` is
                ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    overridden_calculated_entry = property(fget=get_overridden_calculated_entry)

    def is_ignored_for_calculations(self):
        """Tests if this is entry should be ignored in any averaging, scaling or curve calculation.

        return: (boolean) - ``true`` if this entry is ignored, ``false``
                otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def is_graded(self):
        """Tests if a grade or score has been assigned to this entry.

        Generally, an entry is created with a grade or score.

        return: (boolean) - ``true`` if a grade has been assigned,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return bool(self._my_map['gradeId'] is not None or self._my_map['score'] is not None)

    def get_grade_id(self):
        """Gets the grade ``Id`` in this entry if the grading system is based on grades.

        return: (osid.id.Id) - the grade ``Id``
        raise:  IllegalState - ``is_graded()`` is ``false`` or
                ``GradeSystem.isBasedOnGrades()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_id = property(fget=get_grade_id)

    def get_grade(self):
        """Gets the grade in this entry if the grading system is based on grades.

        return: (osid.grading.Grade) - the grade
        raise:  IllegalState - ``is_graded()`` is ``false`` or
                ``GradeSystem.isBasedOnGrades()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade = property(fget=get_grade)

    def get_score(self):
        """Gets the score in this entry if the grading system is not based on grades.

        return: (decimal) - the score
        raise:  IllegalState - ``is_graded()`` is ``false`` or
                ``GradeSystem.isBasedOnGrades()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.grading.GradeSystem.get_lowest_numeric_score_template
        if self._my_map['score'] is None:
            return None
        else:
            return Decimal(str(self._my_map['score']))

    score = property(fget=get_score)

    def get_time_graded(self):
        """Gets the time the gradeable object was graded.

        return: (osid.calendaring.DateTime) - the timestamp of the
                grading entry
        raise:  IllegalState - ``is_graded()`` is ``false`` or
                ``is_derived()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        if not self.is_graded or self.is_derived():
            raise errors.IllegalState()
        time_graded = self._my_map['timeGraded']
        return DateTime(
            time_graded['year'],
            time_graded['month'],
            time_graded['day'],
            time_graded['hour'],
            time_graded['minute'],
            time_graded['second'],
            time_graded['microsecond'])

    time_graded = property(fget=get_time_graded)

    def get_grader_id(self):
        """Gets the ``Id`` of the ``Resource`` that created this entry.

        return: (osid.id.Id) - the ``Id`` of the ``Resource``
        raise:  IllegalState - ``is_graded()`` is ``false`` or
                ``is_derived()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grader_id = property(fget=get_grader_id)

    def get_grader(self):
        """Gets the ``Resource`` that created this entry.

        return: (osid.resource.Resource) - the ``Resource``
        raise:  IllegalState - ``is_graded() is false or is_derived() is
                true``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grader = property(fget=get_grader)

    def get_grading_agent_id(self):
        """Gets the ``Id`` of the ``Agent`` that created this entry.

        return: (osid.id.Id) - the ``Id`` of the ``Agent``
        raise:  IllegalState - ``is_graded()`` is ``false`` or
                ``is_derived()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        if not self.is_graded or self.is_derived():
            raise errors.IllegalState()
        return Id(self._my_map['gradingAgentId'])

    grading_agent_id = property(fget=get_grading_agent_id)

    def get_grading_agent(self):
        """Gets the ``Agent`` that created this entry.

        return: (osid.authentication.Agent) - the ``Agent``
        raise:  IllegalState - ``is_graded() is false or is_derived() is
                true``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        return Agent(self.get_grading_agent_id())

    grading_agent = property(fget=get_grading_agent)

    @utilities.arguments_not_none
    def get_grade_entry_record(self, grade_entry_record_type):
        """Gets the grade entry record corresponding to the given ``GradeEntry`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``grade_entry_record_type`` may be the
        ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(grade_entry_record_type)`` is ``true`` .

        arg:    grade_entry_record_type (osid.type.Type): the type of
                the record to retrieve
        return: (osid.grading.records.GradeEntryRecord) - the grade
                entry record
        raise:  NullArgument - ``grade_entry_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(grade_entry_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradeEntryForm(abc_grading_objects.GradeEntryForm, osid_objects.OsidRelationshipForm):
    """This is the form for creating and updating ``GradeEntries``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``GradeEntryAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'grading.GradeEntry'

    def __init__(self, **kwargs):
        osid_objects.OsidRelationshipForm.__init__(self, object_name='GRADE_ENTRY', **kwargs)
        self._mdata = default_mdata.get_grade_entry_mdata()
        self._effective_agent_id = kwargs['effective_agent_id']

        mgr = self._get_provider_manager('GRADING') # What about the Proxy?
        lookup_session = mgr.get_gradebook_column_lookup_session(proxy=getattr(self, "_proxy", None))
        lookup_session.use_federated_gradebook_view()
        if 'gradebook_column_id' in kwargs:
            gradebook_column = lookup_session.get_gradebook_column(kwargs['gradebook_column_id'])
        elif 'osid_object_map' in kwargs and kwargs['osid_object_map'] is not None:
            gradebook_column = lookup_session.get_gradebook_column(Id(kwargs['osid_object_map']['gradebookColumnId']))
        else:
            raise errors.NullArgument('gradebook_column_id required for create forms.')
        self._grade_system = gradebook_column.get_grade_system()
        self._init_metadata(**kwargs)

        if not self.is_for_update():
            self._init_map(**kwargs)

    def _init_metadata(self, **kwargs):
        osid_objects.OsidRelationshipForm._init_metadata(self, **kwargs)
        if self._grade_system.is_based_on_grades():
            self._mdata['score'].update(
                {'minimum_decimal': None,
                 'maximum_decimal': None})
            allowable_grades = self._grade_system.get_grades()
            allowable_grade_ids = [g.ident for g in allowable_grades]
            self._mdata['grade']['id_set'] = allowable_grade_ids
        else:
            self._mdata['score'].update(
                {'minimum_decimal': self._grade_system.get_lowest_numeric_score(),
                 'maximum_decimal': self._grade_system.get_highest_numeric_score()})
        self._grade_default = self._mdata['grade']['default_id_values'][0]
        self._ignored_for_calculations_default = self._mdata['ignored_for_calculations']['default_boolean_values'][0]
        self._score_default = self._mdata['score']['default_decimal_values'][0]


    def _init_map(self, record_types=None, **kwargs):
        osid_objects.OsidRelationshipForm._init_map(self, record_types=record_types)
        self._my_map['resourceId'] = str(kwargs['resource_id'])
        self._my_map['gradeId'] = self._grade_default
        self._my_map['agentId'] = str(kwargs['effective_agent_id'])
        self._my_map['ignoredForCalculations'] = self._ignored_for_calculations_default
        self._my_map['score'] = self._score_default
        self._my_map['gradingAgentId'] = ''
        self._my_map['gradebookColumnId'] = str(kwargs['gradebook_column_id'])
        self._my_map['assignedGradebookIds'] = [str(kwargs['gradebook_id'])]
        self._my_map['derived'] = False # This is probably not persisted data
        self._my_map['timeGraded'] = None 
        self._my_map['overriddenCalculatedEntryId'] = '' # This will soon do something different


    def get_ignored_for_calculations_metadata(self):
        """Gets the metadata for the ignore flag.

        return: (osid.Metadata) - metadata for the ignore flag
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['ignored_for_calculations'])
        # metadata.update({'existing_ignored_for_calculations_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    ignored_for_calculations_metadata = property(fget=get_ignored_for_calculations_metadata)

    @utilities.arguments_not_none
    def set_ignored_for_calculations(self, ignore):
        """Sets the ignore for calculations flag.

        arg:    ignore (boolean): the new ignore flag
        raise:  InvalidArgument - ``ignore`` is invalid
        raise:  NoAccess - ``ignore`` cannot be modified
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_ignored_for_calculations(self):
        """Clears the ignore for calculations flag.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    ignored_for_calculations = property(fset=set_ignored_for_calculations, fdel=clear_ignored_for_calculations)

    def get_grade_metadata(self):
        """Gets the metadata for a grade.

        return: (osid.Metadata) - metadata for the grade
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['grade'])
        # metadata.update({'existing_grade_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    grade_metadata = property(fget=get_grade_metadata)

    @utilities.arguments_not_none
    def set_grade(self, grade_id):
        """Sets the grade.

        arg:    grade_id (osid.id.Id): the new grade
        raise:  InvalidArgument - ``grade_id`` is invalid or
                ``GradebookColumn.getGradeSystem().isBasedOnGrades()``
                is ``false``
        raise:  NoAccess - ``grade_id`` cannot be modified
        raise:  NullArgument - ``grade_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        if not self._grade_system.is_based_on_grades():
            raise errors.InvalidArgument()
        if self.get_grade_metadata().is_read_only():
            raise errors.NoAccess()
        if not self._is_valid_id(grade_id):
            raise errors.InvalidArgument()
        if not self._is_in_set(grade_id, self.get_grade_metadata()):
            raise errors.InvalidArgument('Grade ID not in the acceptable set.')
        self._my_map['gradeId'] = str(grade_id)
        self._my_map['gradingAgentId'] = str(self._effective_agent_id)
        self._my_map['timeGraded'] = now_map()

    def clear_grade(self):
        """Clears the grade.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        if not self._grade_system.is_based_on_grades():
            return # do nothing, spec does not raise error
        if (self.get_grade_metadata().is_read_only() or
                self.get_grade_metadata().is_required()):
            raise errors.NoAccess()
        self._my_map['gradeId'] = self._grade_default
        self._my_map['gradingAgentId'] = ''
        self._my_map['timeGraded'] = None

    grade = property(fset=set_grade, fdel=clear_grade)

    def get_score_metadata(self):
        """Gets the metadata for a score.

        return: (osid.Metadata) - metadata for the score
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['score'])
        # metadata.update({'existing_score_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    score_metadata = property(fget=get_score_metadata)

    @utilities.arguments_not_none
    def set_score(self, score):
        """Sets the score.

        arg:    score (decimal): the new score
        raise:  InvalidArgument - ``score`` is invalid or
                ``GradebookColumn.getGradeSystem().isBasedOnGrades()``
                is ``true``
        raise:  NoAccess - ``score`` cannot be modified
        *compliance: mandatory -- This method must be implemented.*

        """
        if self._grade_system.is_based_on_grades():
            raise errors.InvalidArgument()
        if self.get_score_metadata().is_read_only():
            raise errors.NoAccess()
        if not self._is_valid_decimal(score, self.get_score_metadata()):
            raise errors.InvalidArgument()
        if not isinstance(score, Decimal):
            score = Decimal(str(score))
        if (self._grade_system.get_numeric_score_increment() and 
                score % self._grade_system.get_numeric_score_increment() != 0):
            raise errors.InvalidArgument('score must be in increments of ' + str(self._score_increment))
        self._my_map['score'] = float(score)
        self._my_map['gradingAgentId'] = str(self._effective_agent_id)
        self._my_map['timeGraded'] = now_map()

    def clear_score(self):
        """Clears the score.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self._grade_system.is_based_on_grades():
            return # do nothing, spec does not raise error
        if (self.get_score_metadata().is_read_only() or
                self.get_score_metadata().is_required()):
            raise errors.NoAccess()
        self._my_map['score'] = self._score_default
        self._my_map['gradingAgentId'] = ''
        self._my_map['timeGraded'] = None

    score = property(fset=set_score, fdel=clear_score)

    @utilities.arguments_not_none
    def get_grade_entry_form_record(self, grade_entry_record_type):
        """Gets the ``GradeEntryFormRecord`` corresponding to the given grade entry record ``Type``.

        arg:    grade_entry_record_type (osid.type.Type): the grade
                entry record type
        return: (osid.grading.records.GradeEntryFormRecord) - the grade
                entry form record
        raise:  NullArgument - ``grade_entry_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(grade_entry_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradeEntryList(abc_grading_objects.GradeEntryList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``GradeEntryList`` provides a means for accessing ``GradeEntry`` elements sequentially either one at a time or many at a time.

    Examples: while (gel.hasNext()) { GradeEntry entry =
    gel.getNextGradeEntry(); }

    or
      while (gel.hasNext()) {
           GradeEntry[] entries = gel.getNextGradeEntries(gel.available());
      }



    """

    def get_next_grade_entry(self):
        """Gets the next ``GradeEntry`` in this list.

        return: (osid.grading.GradeEntry) - the next ``GradeEntry`` in
                this list. The ``has_next()`` method should be used to
                test that a next ``GradeEntry`` is available before
                calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(GradeEntry)

    next_grade_entry = property(fget=get_next_grade_entry)

    @utilities.arguments_not_none
    def get_next_grade_entries(self, n):
        """Gets the next set of ``GradeEntry`` elements in this list which must be less than or equal to the number returned from ``available()``.

        arg:    n (cardinal): the number of ``GradeEntry`` elements
                requested which should be less than or equal to
                ``available()``
        return: (osid.grading.GradeEntry) - an array of ``GradeEntry``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class GradebookColumn(abc_grading_objects.GradebookColumn, osid_objects.OsidObject):
    """A ``GradebookColumn`` represents a series of grade entries in a gradebook.

    Each GradeEntry in a column share the same ``GradeSystem``.

    """

    _namespace = 'grading.GradebookColumn'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='GRADEBOOK_COLUMN', **kwargs)
        self._catalog_name = 'gradebook'


    def get_grade_system_id(self):
        """Gets the ``GradeSystem Id`` in which this grade belongs.

        return: (osid.id.Id) - the grade system ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system_id = property(fget=get_grade_system_id)

    def get_grade_system(self):
        """Gets the ``GradeSystem`` in which this grade belongs.

        return: (osid.grading.GradeSystem) - the package grade system
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system = property(fget=get_grade_system)

    @utilities.arguments_not_none
    def get_gradebook_column_record(self, gradebook_column_record_type):
        """Gets the gradebook column record corresponding to the given ``GradeBookColumn`` record ``Type``.

        This method ie used to retrieve an object implementing the
        requested record. The ``gradebook_column_record_type`` may be
        the ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(gradebook_column_record_type)`` is ``true`` .

        arg:    gradebook_column_record_type (osid.type.Type): the type
                of the record to retrieve
        return: (osid.grading.records.GradebookColumnRecord) - the
                gradebook column record
        raise:  NullArgument - ``gradebook_column_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(gradebook_column_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradebookColumnForm(abc_grading_objects.GradebookColumnForm, osid_objects.OsidObjectForm):
    """This is the form for creating and updating ``GradebookColumns``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``GradebookAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'grading.GradebookColumn'

    def __init__(self, **kwargs):
        osid_objects.OsidObjectForm.__init__(self, object_name='GRADEBOOK_COLUMN', **kwargs)
        self._mdata = default_mdata.get_gradebook_column_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""
        osid_objects.OsidObjectForm._init_metadata(self, **kwargs)
        self._grade_system_default = self._mdata['grade_system']['default_id_values'][0]

    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""
        osid_objects.OsidObjectForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    def get_grade_system_metadata(self):
        """Gets the metadata for a grade system.

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
        """Sets the grade system.

        arg:    grade_system_id (osid.id.Id): the new grade system
        raise:  InvalidArgument - ``grade_system_id`` is invalid
        raise:  NoAccess - ``grade_system_id`` cannot be modified
        raise:  NullArgument - ``grade_system_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_system(self):
        """Clears the grade system.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system = property(fset=set_grade_system, fdel=clear_grade_system)

    @utilities.arguments_not_none
    def get_gradebook_column_form_record(self, gradebook_column_record_type):
        """Gets the ``GradebookColumnFormRecord`` corresponding to the given gradebook column record ``Type``.

        arg:    gradebook_column_record_type (osid.type.Type): a
                gradebook column record type
        return: (osid.grading.records.GradebookColumnFormRecord) - the
                gradebook column form record
        raise:  NullArgument - ``gradebook_column_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(gradebook_column_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradebookColumnList(abc_grading_objects.GradebookColumnList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``GradebookColumnList`` provides a means for accessing ``GradebookColumn`` elements sequentially either one at a time or many at a time.

    Examples: while (gcl.hasNext()) { GradebookColumn column =
    gcl.getNextGradebookColumn(); }

    or
      while (gcl.hasNext()) {
           GradebookColumn[] columns = gcl.getNextGradebookColumns(gcl.available());
      }



    """

    def get_next_gradebook_column(self):
        """Gets the next ``GradebookColumn`` in this list.

        return: (osid.grading.GradebookColumn) - the next
                ``GradebookColumn`` in this list. The ``has_next()``
                method should be used to test that a next
                ``GradebookColumn`` is available before calling this
                method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(GradebookColumn)

    next_gradebook_column = property(fget=get_next_gradebook_column)

    @utilities.arguments_not_none
    def get_next_gradebook_columns(self, n):
        """Gets the next set of ``GradebookColumn`` elements in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``GradebookColumn`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.grading.GradebookColumn) - an array of
                ``GradebookColumn`` elements.The length of the array is
                less than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class GradebookColumnSummary(abc_grading_objects.GradebookColumnSummary, osid_objects.OsidObject):
    """A ``GradebookColumnSummary`` is a summary of all entries within a gradebook column."""

    _record_type_data_sets = {}
    _namespace = 'grading.GradebookColumnSummary'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='GRADEBOOK_COLUMN_SUMMARY', **kwargs)
        self._catalog_name = 'gradebook'

        # Not set the entries to be included in the calculation
        self._entries = self._get_entries_for_calculation()
        self._entry_scores = self._get_entry_scores()

    def _get_entries_for_calculation(self):
        """Ignores entries flagged with ignoreForCalculation"""
        mgr = self._get_provider_manager('Grading') # what about the Proxy?
        if not mgr.supports_gradebook_column_lookup():
            raise errors.OperationFailed('Grading does not support GradebookColumn lookup')
        gradebook_id = Id(self._my_map['assignedGradebookIds'][0])
        lookup_session = mgr.get_grade_entry_lookup_session_for_gradebook(gradebook_id,
                                                                          proxy=getattr(self, "_proxy", None))
        entries = lookup_session.get_grade_entries_for_gradebook_column(self.get_gradebook_column_id())
        return [e for e in entries if not e.is_ignored_for_calculations()]

    def _get_entry_scores(self):
        """Takes entries from self._entries and returns a list of scores (or
        output scores, if based on grades)"""
        if self.get_gradebook_column().get_grade_system().is_based_on_grades():
            return [e.get_grade().get_output_score() for e in self._entries if e.is_graded()]
        else:
            return [e.get_score() for e in self._entries if e.is_graded()]

    def get_gradebook_column_id(self):
        """Gets the ``Id`` of the ``GradebookColumn``.

        return: (osid.id.Id) - the ``Id`` of the ``GradebookColumn``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_column_id = property(fget=get_gradebook_column_id)

    def get_gradebook_column(self):
        """Gets the ``GradebookColumn``.

        return: (osid.grading.GradebookColumn) - the ``GradebookColumn``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_column = property(fget=get_gradebook_column)

    def get_mean(self):
        """Gets the mean score.

        If this system is based on grades, the mean output score is
        returned.

        return: (decimal) - the mean score
        *compliance: mandatory -- This method must be implemented.*

        """
        return np.mean(self._entry_scores)

    mean = property(fget=get_mean)

    def get_median(self):
        """Gets the median score.

        If this system is based on grades, the mean output score is
        returned.

        return: (decimal) - the median score
        *compliance: mandatory -- This method must be implemented.*

        """
        return np.median(self._entry_scores)

    median = property(fget=get_median)

    def get_mode(self):
        """Gets the mode of the score.

        If this system is based on grades, the mode of the output score
        is returned.

        return: (decimal) - the median score
        *compliance: mandatory -- This method must be implemented.*

        """
        # http://stackoverflow.com/questions/10797819/finding-the-mode-of-a-list-in-python
        return max(set(self._entry_scores), key=self._entry_scores.count)

    mode = property(fget=get_mode)

    def get_rms(self):
        """Gets the root mean square of the score.

        If this system is based on grades, the RMS of the output score
        is returned.

        return: (decimal) - the median score
        *compliance: mandatory -- This method must be implemented.*

        """
        return np.sqrt(np.mean(np.square(self._entry_scores)))

    rms = property(fget=get_rms)

    def get_standard_deviation(self):
        """Gets the standard deviation.

        If this system is based on grades, the spread of the output
        scores is returned.

        return: (decimal) - the standard deviation
        *compliance: mandatory -- This method must be implemented.*

        """
        return np.std(self._entry_scores)

    standard_deviation = property(fget=get_standard_deviation)

    def get_sum(self):
        """Gets the sum of the scores.

        If this system is based on grades, the sum of the output scores
        is returned.

        return: (decimal) - the median score
        *compliance: mandatory -- This method must be implemented.*

        """
        return sum(self._entry_scores)

    sum = property(fget=get_sum)

    @utilities.arguments_not_none
    def get_gradebook_column_summary_record(self, gradebook_column_summary_record_type):
        """Gets the gradebook column summary record corresponding to the given ``GradebookColumnSummary`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``gradebook_column_summary_record_type``
        may be the ``Type`` returned in ``get_record_types()`` or any of
        its parents in a ``Type`` hierarchy where
        ``has_record_type(gradebook_column_summary_record_type)`` is
        ``true`` .

        arg:    gradebook_column_summary_record_type (osid.type.Type):
                the type of the record to retrieve
        return: (osid.grading.records.GradebookColumnSummaryRecord) -
                the gradebook column summary record
        raise:  NullArgument - ``gradebook_column_summary_record_type``
                is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(gradebook_column_summary_record_type)`
                ` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class Gradebook(abc_grading_objects.Gradebook, osid_objects.OsidCatalog):
    """A gradebook defines a collection of grade entries."""

    _namespace = 'grading.Gradebook'

    def __init__(self, **kwargs):
        # self._record_type_data_sets = get_registry('GRADEBOOK_RECORD_TYPES', runtime)
        osid_objects.OsidCatalog.__init__(self, object_name='GRADEBOOK', **kwargs)

    @utilities.arguments_not_none
    def get_gradebook_record(self, gradebook_record_type):
        """Gets the gradebook record corresponding to the given ``Gradebook`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``gradebook_record_type`` may be the
        ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(gradebook_record_type)`` is ``true`` .

        arg:    gradebook_record_type (osid.type.Type): a gradebook
                record type
        return: (osid.grading.records.GradebookRecord) - the gradebook
                record
        raise:  NullArgument - ``gradebook_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(gradebook_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradebookForm(abc_grading_objects.GradebookForm, osid_objects.OsidCatalogForm):
    """This is the form for creating and updating ``Gradebooks``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``GradebookAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'grading.Gradebook'

    def __init__(self, **kwargs):
        osid_objects.OsidCatalogForm.__init__(self, object_name='GRADEBOOK', **kwargs)
        self._mdata = default_mdata.get_gradebook_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    @utilities.arguments_not_none
    def get_gradebook_form_record(self, gradebook_record_type):
        """Gets the ``GradebookFormRecord`` corresponding to the given gradebook record ``Type``.

        arg:    gradebook_record_type (osid.type.Type): a gradebook
                record type
        return: (osid.grading.records.GradebookFormRecord) - the
                gradebook form record
        raise:  NullArgument - ``gradebook_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(gradebook_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradebookList(abc_grading_objects.GradebookList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``GradebookList`` provides a means for accessing ``Gradebook`` elements sequentially either one at a time or many at a time.

    Examples: while (gl.hasNext()) { Gradebook gradebook =
    gl.getNextGradebook(); }

    or
      while (gl.hasNext()) {
           Gradebook[] gradebooks = gl.getNextGradebooks(gl.available());
      }



    """

    def get_next_gradebook(self):
        """Gets the next ``Gradebook`` in this list.

        return: (osid.grading.Gradebook) - the next ``Gradebook`` in
                this list. The ``has_next()`` method should be used to
                test that a next ``Gradebook`` is available before
                calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Gradebook)

    next_gradebook = property(fget=get_next_gradebook)

    @utilities.arguments_not_none
    def get_next_gradebooks(self, n):
        """Gets the next set of ``Gradebook`` elements in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``Gradebook`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.grading.Gradebook) - an array of ``Gradebook``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class GradebookNode(abc_grading_objects.GradebookNode, osid_objects.OsidNode):
    """This interface is a container for a partial hierarchy retrieval.

    The number of hierarchy levels traversable through this interface
    depend on the number of levels requested in the
    ``GradebookHierarchySession``.

    """

    def get_gradebook(self):
        """Gets the ``Gradebook`` at this node.

        return: (osid.grading.Gradebook) - the gradebook represented by
                this node
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook = property(fget=get_gradebook)

    def get_parent_gradebook_nodes(self):
        """Gets the parents of this gradebook.

        return: (osid.grading.GradebookNodeList) - the parents of the
                ``id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    parent_gradebook_nodes = property(fget=get_parent_gradebook_nodes)

    def get_child_gradebook_nodes(self):
        """Gets the children of this gradebook.

        return: (osid.grading.GradebookNodeList) - the children of this
                gradebook
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    child_gradebook_nodes = property(fget=get_child_gradebook_nodes)


class GradebookNodeList(abc_grading_objects.GradebookNodeList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``GradebookNodeList`` provides a means for accessing ``GradebookNode`` elements sequentially either one at a time or many at a time.

    Examples: while (gnl.hasNext()) { GradebookNode node =
    gnl.getNextGradebookNode(); }

    or
      while (gnl.hasNext()) {
           GradebookNode[] nodes = gnl.getNextGradebookNodes(gnl.available());
      }



    """

    def get_next_gradebook_node(self):
        """Gets the next ``GradebookNode`` in this list.

        return: (osid.grading.GradebookNode) - the next
                ``GradebookNode`` in this list. The ``has_next()``
                method should be used to test that a next
                ``GradebookNode`` is available before calling this
                method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(GradebookNode)

    next_gradebook_node = property(fget=get_next_gradebook_node)

    @utilities.arguments_not_none
    def get_next_gradebook_nodes(self, n):
        """Gets the next set of ``GradebookNode`` elements in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``GradebookNode`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.grading.GradebookNode) - an array of
                ``GradebookNode`` elements.The length of the array is
                less than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


