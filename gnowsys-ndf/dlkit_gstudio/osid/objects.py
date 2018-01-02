"""GStudio implementations of osid objects."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



import importlib
import itertools
import uuid


from decimal import Decimal
from pymongo.cursor import Cursor


from . import default_mdata
from .. import utilities
from dlkit.abstract_osid.osid import objects as abc_osid_objects
from ..osid import markers as osid_markers
from ..primitives import Id, DisplayText
from dlkit.abstract_osid.locale.primitives import DisplayText as abc_display_text
from ..utilities import OsidListList
from ..utilities import get_locale_with_proxy
from ..utilities import update_display_text_defaults
from .metadata import Metadata
from dlkit.abstract_osid.osid import errors
# from dlkit.primordium.id.primitives import Id
from dlkit.primordium.type.primitives import Type
from dlkit.primordium.locale.types import language, script
from dlkit.primordium.locale.types import format as text_format
from ..utilities import get_display_text_map
#=================
# for multi-language
from ..types import Language, Script, Format
from ..primitives import Type, DisplayText
DEFAULT_LANGUAGE_TYPE = Type(**Language().get_type_data('DEFAULT'))
DEFAULT_SCRIPT_TYPE = Type(**Script().get_type_data('DEFAULT'))
DEFAULT_FORMAT_TYPE = Type(**Format().get_type_data('DEFAULT'))
# ==============


class OsidObject(abc_osid_objects.OsidObject, osid_markers.Identifiable, osid_markers.Extensible, osid_markers.Browsable):
    """``OsidObject`` is the top level interface for all OSID Objects.

    An OSID Object is an object identified by an OSID ``Id`` and may
    implements optional interfaces. OSID Objects also contain a display
    name and a description. These fields are required but may be used
    for a variety of purposes ranging from a primary name and
    description of the object to a more user friendly display of various
    attributes.

    Creation of OSID Objects and the modification of their data is
    managed through the associated ``OsidSession`` which removes the
    dependency of updating data elements upon object retrieval.The
    ``OsidManager`` should be used to test if updates are available and
    determine what ``PropertyTypes`` are supported. The ``OsidManager``
    is also used to create the appropriate ``OsidSession`` for object
    creation, updates and deletes.

    All ``OsidObjects`` are identified by an immutable ``Id``. An ``Id``
    is assigned to an object upon creation of the object and cannot be
    changed once assigned.

    An ``OsidObject`` may support one or more supplementary records
    which are expressed in the form of interfaces. Each record interface
    is identified by a Type. A record interface may extend another
    record interface where support of the parent record interface is
    implied. In this case of interface inheritance, support of the
    parent record type may be implied through ``has_record_type()`` and
    not explicit in ``getRecordTypes()``.

    For example, if recordB extends recordA, typeB is a child of typeA.
    If a record implements typeB, than it also implements typeA. An
    application that only knows about typeA retrieves recordA. An
    application that knows about typeB, retrieves recordB which is the
    union of methods specified in typeA and typeB. If an application
    requests typeA, it may not attempt to access methods defined in
    typeB as they may not exist until explicitly requested. The
    mechanics of this polymorphism is defined by the language binder.
    One mechanism might be the use of casting.

    In addition to the record ``Types,`` OSID Objects also have a genus
    ``Type``. A genus ``Type`` indicates a classification or kind of the
    object where an "is a" relationship exists. The purpose of of the
    genus ``Type`` is to avoid the creation of unnecessary record types
    that may needlessly complicate an interface hierarchy or introduce
    interoperability issues. For example, an OSID object may have a
    record ``Type`` of ``Publication`` that defines methods pertinent to
    publications, such as an ISBN number. A provider may wish to
    distinguish between books and journals without having the need of
    new record interfaces. In this case, the genus ``Type`` may be one
    of ``Book`` or ``Journal``. While this distinction can aid a search,
    these genres should be treated in such a way that do not introduce
    interoperability problems.

    Like record Types, the genus Types may also exist in an implicit
    type hierarchy. An OSID object always has at least one genus. Genus
    types should not be confused with subject tagging, which is managed
    externally to the object. Unlike record ``Types,`` an object's genus
    may be modified. However, once an object's record is created with a
    record ``Type,`` it cannot be changed.

    Methods that return values are not permitted to return nulls. If a
    value is not set, it is indicated in the ``Metadata`` of the update
    form.

    """

    _namespace = 'osid.OsidObject'

    def __init__(self, gstudio_node, runtime=None, **kwargs):
        osid_markers.Identifiable.__init__(self, runtime=runtime)
        osid_markers.Extensible.__init__(self, runtime=runtime, **kwargs)
        self._gstudio_map = {}
        self._gstudio_map['gstudio_node'] = gstudio_node
        self._gstudio_map['recordTypeIds'] = []
        self._gstudio_node = gstudio_node
        self._my_map = {}
        self._my_map['recordTypeIds'] = []
        self._my_map['gstudio_node'] = gstudio_node
        self._load_records(self._gstudio_map['recordTypeIds'])
        self._load_records(self._my_map['recordTypeIds'])
        # print "\n gstudio_node: ", gstudio_node
        self.copyright = DisplayText(display_text_map={
                                'text':gstudio_node['legal']['copyright'],
                                'languageTypeId': str(DEFAULT_LANGUAGE_TYPE),
                                'scriptTypeId': str(DEFAULT_SCRIPT_TYPE),
                                'formatTypeId': str(DEFAULT_FORMAT_TYPE)
                            })
        self.license = DisplayText(display_text_map={
                                'text':gstudio_node['legal']['license'],
                                'languageTypeId': str(DEFAULT_LANGUAGE_TYPE),
                                'scriptTypeId': str(DEFAULT_SCRIPT_TYPE),
                                'formatTypeId': str(DEFAULT_FORMAT_TYPE)
                            })

        self._gstudio_map['displayName'] = DisplayText(display_text_map={
                                'text':gstudio_node['name'],
                                'languageTypeId': str(DEFAULT_LANGUAGE_TYPE),
                                'scriptTypeId': str(DEFAULT_SCRIPT_TYPE),
                                'formatTypeId': str(DEFAULT_FORMAT_TYPE)
                            })
        self._gstudio_map['description'] = DisplayText(display_text_map={
                                'text':gstudio_node['content'],
                                'languageTypeId': str(DEFAULT_LANGUAGE_TYPE),
                                'scriptTypeId': str(DEFAULT_SCRIPT_TYPE),
                                'formatTypeId': str(DEFAULT_FORMAT_TYPE)
                            })
        self._gstudio_map['displayNames'] = [get_display_text_map(self._gstudio_map['displayName'])]
        self._gstudio_map['descriptions'] = [get_display_text_map(self._gstudio_map['description'])]


    def get_object_map(self, obj_map):
        """Adds OsidObject elements to object map"""
        super(OsidObject, self).get_object_map(obj_map)
        obj_map['id'] = str(self.get_id())

        obj_map['displayName'] = get_display_text_map(self._gstudio_map['displayName'])
        obj_map['description'] = get_display_text_map(self._gstudio_map['description'])
        if 'gstudio_node' in self._gstudio_map:
            obj_map['license'] = get_display_text_map(self._gstudio_map['gstudio_node']['legal']['license'])
            obj_map['copyright'] = get_display_text_map(self._gstudio_map['gstudio_node']['legal']['copyright'])
        # obj_map['displayName'] = get_display_text_map(self.get_display_name())
        # obj_map['description'] = get_display_text_map(self.get_description())
        try:
            obj_map['genusType'] = str(self.get_genus_type())
            # asset-content-genus-type%3A<mimetytpe>%40ODL.MIT.EDU
        except errors.Unimplemented:
            obj_map['genusType'] = 'Default%3ADefault%40Default'
        return obj_map

    object_map = property(get_object_map)


    def get_display_name(self):
        """Gets the preferred display name associated with this instance of this OSID object appropriate for display to the user.

        return: (osid.locale.DisplayText) - the display name
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: A display name is a string used for
        identifying an object in human terms. A provider may wish to
        initialize the display name based on one or more object
        attributes. In some cases, the display name may not map to a
        specific or significant object attribute but simply be used as a
        preferred display name that can be modified. A provider may also
        wish to translate the display name into a specific locale using
        the Locale service. Some OSIDs define methods for more detailed
        naming.

        """

        # default script: 'LATN'
        # default format: 'PLAIN'
        # language : from node
        display_name_val = self._gstudio_node['altnames'] 
        if not display_name_val:
            display_name_val = self._gstudio_node['name']
        return DisplayText(
            text=display_name_val,
            language_type=Type(**language.get_type_data(self._gstudio_node['language'][0])),
            script_type=Type(**script.get_type_data('LATN')),
            format_type=Type(**text_format.get_type_data('PLAIN')),
            )

    display_name = property(fget=get_display_name)

    def get_description(self):
        """Gets the description associated with this instance of this OSID object.

        return: (osid.locale.DisplayText) - the description
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: A description is a string used for
        describing an object in human terms and may not have
        significance in the underlying system. A provider may wish to
        initialize the description based on one or more object
        attributes and/or treat it as an auxiliary piece of data that
        can be modified. A provider may also wish to translate the
        description into a specific locale using the Locale service.

        """
        # return DisplayText(self._gstudio_node['content'])

        text_val = self._gstudio_node['content'] 
        if not text_val:
            text_val = "No description available."
        # if not text_val and self._gstudio_node['altnames']:
        #     text_val = self._gstudio_node['altnames']
        # else:
        #     text_val = self._gstudio_node['name']

        return DisplayText(
            text=text_val,
            language_type=Type(**language.get_type_data(self._gstudio_node['language'][0])),
            script_type=Type(**script.get_type_data('LATN')),
            format_type=Type(**text_format.get_type_data('PLAIN')),
            )


    description = property(fget=get_description)

    def get_genus_type(self):
        """Gets the genus type of this object.

        return: (osid.type.Type) - the genus type of this object
        *compliance: mandatory -- This method must be implemented.*

        """
        try:
            # Try to stand up full Type objects if they can be found
            # (Also need to LOOK FOR THE TYPE IN types or through type lookup)
            if 'gstudio_node' in self._gstudio_map and ['if_file']['mime_type'] in self._gstudio_map['gstudio_node']['if_file']:
                mimetype_val = str(self._gstudio_map['gstudio_node']['if_file']['mime_type'].split('/')[-1])
                genusType = Id(identifier=str(mimetype_val), 
                                namespace="asset-content-genus-type",
                                authority="ODL.MIT.EDU")
                # genus_type_identifier = genusType.get_identifier()
                # return Type(**types.Genus().get_type_data(genus_type_identifier))
                return Type(idstr=str(genusType))
            return None
        except:
            return None
            # If that doesn't work, return the id only type, still useful for comparison.

        # return Type('asset-content-genus-type%3Amp4%40ODL.MIT.EDU')

    
    genus_type = property(fget=get_genus_type)

    @utilities.arguments_not_none
    def is_of_genus_type(self, genus_type):
        """Tests if this object is of the given genus ``Type``.

        The given genus type may be supported by the object through the
        type hierarchy.

        arg:    genus_type (osid.type.Type): a genus type
        return: (boolean) - ``true`` if this object is of the given
                genus ``Type,``  ``false`` otherwise
        raise:  NullArgument - ``genus_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class OsidRelationship(abc_osid_objects.OsidRelationship, OsidObject, osid_markers.Temporal):
    """A ``Relationship`` associates two OSID objects.

    Relationships are transient. They define a date range for which they
    are in effect.

    Unlike other ``OsidObjects`` that rely on the auxiliary Journaling
    OSID to track variance over time, ``OsidRelationships`` introduce a
    different concept of time independent from journaling. For example,
    in the present, a student was registered in a course and dropped it.
    The relationship between the student and the course remains
    pertinent, independent of any journaled changes that may have
    occurred to either the student or the course.

    Once the student has dropped the course, the relationship has
    expired such that ``is_effective()`` becomes false. It can be
    inferred that during the period of the effective dates, the student
    was actively registered in the course. Here is an example:

      * T1. September 1: Student registers for course for grades
      * T2. September 10: Student drops course
      * T3. September 15: Student re-registers for course pass/fail


    The relationships are:
      T1. R1 {effective,   September 1  -> end of term,  data=grades}
      T2. R1 {ineffective, September 1  -> September 10, data=grades}
      T3. R1 {ineffective, September 1  -> September 10, data=grades}
          R2 {effective,   September 10 -> end of term,  data=p/f}



    An OSID Provider may also permit dates to be set in the future in
    which case the relationship can become automatically become
    effective at a future time and later expire. More complex
    effectiveness management can be done through other rule-based
    services.

    OSID Consumer lookups and queries of relationships need to consider
    that it may be only effective relationshps are of interest.

    """

    def has_end_reason(self):
        """Tests if a reason this relationship came to an end is known.

        return: (boolean) - ``true`` if an end reason is available,
                ``false`` otherwise
        raise:  IllegalState - ``is_effective()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_end_reason_id(self):
        """Gets a state ``Id`` indicating why this relationship has ended.

        return: (osid.id.Id) - a state ``Id``
        raise:  IllegalState - ``has_end_reason()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    end_reason_id = property(fget=get_end_reason_id)

    def get_end_reason(self):
        """Gets a state indicating why this relationship has ended.

        return: (osid.process.State) - a state
        raise:  IllegalState - ``has_end_reason()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    end_reason = property(fget=get_end_reason)


class OsidCatalog(abc_osid_objects.OsidCatalog, OsidObject, osid_markers.Sourceable, osid_markers.Federateable):
    """``OsidCatalog`` is the top level interface for all OSID catalog-like objects.

    A catalog relates to other OSID objects for the purpose of
    organization and federation and almost always are hierarchical. An
    example catalog is a ``Repository`` that relates to a collection of
    ``Assets``.

    ``OsidCatalogs`` allow for the retrieval of a provider identity and
    branding.

    Collections visible through an ``OsidCatalog`` may be the output of
    a dynamic query or some other rules-based evaluation. The facts
    surrounding the evaluation are the ``OsidObjects`` visible to the
    ``OsidCatalog`` from its position in the federated hierarchy. The
    input conditions may satisifed on a service-wide basis using an
    ``OsidQuery`` or environmental conditions supplied to the services
    via a ``Proxy`` .

    Often, the selection of an ``OsidCatalog`` in instantiating an
    ``OsidSession`` provides access to a set of ``OsidObjects`` .
    Because the view inside an ``OsidCatalog`` can also be produced
    behaviorally using a rules evaluation, the ``Id`` (or well-known
    alias) of the ``OsidCatalog`` may be used as an abstract means of
    requesting a predefined set of behaviors or data constraints from an
    OSID Provider.

    The flexibility of interpretation together with its central role in
    federation to build a rich and complex service from a set of
    individual OSID Providers makes cataloging an essential pattern to
    achieve abstraction from implementations in the OSIDs without loss
    of functionality. Most OSIDs include a cataloging pattern.

    """

    _namespace = 'osid.OsidCatalog'
    
    def __init__(self, **kwargs):
        OsidObject.__init__(self, **kwargs)

        # Should we initialize Sourceable?
        # Should we initialize Federatable?

    def get_object_map(self, obj_map):
        """Adds OsidCatalog elements to object map"""
        super(OsidCatalog, self).get_object_map(obj_map)    




class OsidRule(abc_osid_objects.OsidRule, OsidObject, osid_markers.Operable):
    """An ``OsidRule`` identifies an explicit or implicit rule evaluation.

    An associated ``Rule`` may be available in cases where the behavior
    of the object can be explicitly modified using a defined rule. In
    many cases, an ``OsidObject`` may define specific methods to manage
    certain common behavioral aspects and delegate anything above and
    beyond what has been defined to a rule evaluation.

    Rules are defined to be operable. In the case of a statement
    evaluation, an enabled rule overrides any evaluation to return
    ``true`` and a disabled rule overrides any evaluation to return
    ``false``.

    ``Rules`` are never required to consume or implement. They serve as
    a mechanism to offer a level of management not attainable in the
    immediate service definition. Each Rule implies evaluating a set of
    facts known to the service to produce a resulting beavior. Rule
    evaluations may also accept input data or conditions, however,
    ``OsidRules`` as they appear in throughout the services may or may
    not provide a means of supplying ``OsidConditions`` directly. In the
    services where an explicit ``OsidCondition`` is absent they may be
    masquerading as another interface such as a ``Proxy`` or an
    ``OsidQuery`` .

    """

    def has_rule(self):
        """Tests if an explicit rule is available.

        return: (boolean) - ``true`` if an explicit rule is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False

    def get_rule_id(self):
        """Gets the explicit rule ``Id``.

        return: (osid.id.Id) - the rule ``Id``
        raise:  IllegalState - ``has_rule()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Someday I'll have a real implementation, but for now I just:
        raise errors.IllegalState()

    rule_id = property(fget=get_rule_id)

    def get_rule(self):
        """Gets the explicit rule.

        return: (osid.rules.Rule) - the rule
        raise:  IllegalState - ``has_rule()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Someday I'll have a real implementation, but for now I just:
        raise errors.IllegalState()

    rule = property(fget=get_rule)


class OsidEnabler(abc_osid_objects.OsidEnabler, OsidRule, osid_markers.Temporal):
    """``OsidEnabler`` is used to manage the effectiveness, enabledness, or operation of an ``OsidObejct``.

    The ``OsidEnabler`` itself is active or inactive When an
    ``OsidEnabler`` is active, any ``OsidObject`` mapped to it is "on."
    When all ``OsidEnablers`` mapped to an ``OsidObject`` are inactive,
    then the ``OsidObject`` is "off."

    The managed ``OsidObject`` may have varying semantics as to what its
    on/off status means and in particular, which methods are used to
    indicate the effect of an ``OsidEnabler``. Some axamples:

      * ``Operables:``  ``OsidEnablers`` effect the operational status.
      * ``Temporals:``  ``OsidEnablers`` may be used to extend or
        shorten the effectiveness of a ``Temporal`` such as an
        ``OsidRelationship.``


    In the case where an ``OsidEnabler`` may cause a discontinuity in a
    ``Temporal,`` the ``OsidEnabler`` may cause the creation of new
    ``Temporals`` to capture the gap in effectiveness.

    For example, An ``OsidRelationship`` that began in 2007 may be
    brought to an end in 2008 due to the absence of any active
    ``OsidEnablers``. When an effective ``OsidEnabler`` appears in 2009,
    a new ``OsidRelationship`` is created with a starting effective date
    of 2009 leaving the existing ``OsidRelationship`` with effective
    dates from 2007 to 2008.

    An ``OsidEnabler`` itself is both a ``Temporal`` and an ``OsidRule``
    whose activity status of the object may be controlled
    administratively, using a span of effective dates, through an
    external rule, or all three. The ``OsidEnabler`` defines a set of
    canned rules based on dates, events, and cyclic events.

    """

    def is_effective_by_schedule(self):
        """Tests if the effectiveness of the enabler is governed by a ``Schedule``.

        If a schedule exists, it is bounded by the effective dates of
        this enabler. If ``is_effective_by_schedule()`` is ``true,``
        ``is_effective_by_event()`` and
        ``is_effective_by_cyclic_event()`` must be ``false``.

        return: (boolean) - ``true`` if the enabler is governed by
                schedule, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_schedule_id(self):
        """Gets the schedule ``Id``.

        return: (osid.id.Id) - the schedule ``Id``
        raise:  IllegalState - ``is_effective_by_schedule()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    schedule_id = property(fget=get_schedule_id)

    def get_schedule(self):
        """Gets the schedule.

        return: (osid.calendaring.Schedule) - the schedule
        raise:  IllegalState - ``is_effective_by_schedule()`` is
                ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    schedule = property(fget=get_schedule)

    def is_effective_by_event(self):
        """Tests if the effectiveness of the enabler is governed by an ``Event`` such that the start and end dates of the event govern the effectiveness.

        The event may also be a ``RecurringEvent`` in which case the
        enabler is effective for start and end dates of each event in
        the series If an event exists, it is bounded by the effective
        dates of this enabler. If ``is_effective_by_event()`` is
        ``true,`` ``is_effective_by_schedule()`` and
        ``is_effective_by_cyclic_event()`` must be ``false``.

        return: (boolean) - ``true`` if the enabler is governed by an
                event, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_event_id(self):
        """Gets the event ``Id``.

        return: (osid.id.Id) - the event ``Id``
        raise:  IllegalState - ``is_effective_by_event()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    event_id = property(fget=get_event_id)

    def get_event(self):
        """Gets the event.

        return: (osid.calendaring.Event) - the event
        raise:  IllegalState - ``is_effective_by_event()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    event = property(fget=get_event)

    def is_effective_by_cyclic_event(self):
        """Tests if the effectiveness of the enabler is governed by a ``CyclicEvent``.

        If a cyclic event exists, it is evaluated by the accompanying
        cyclic time period. If ``is_effective_by_cyclic_event()`` is
        ``true,`` ``is_effective_by_schedule()`` and
        ``is_effective_by_event()`` must be ``false``.

        return: (boolean) - ``true`` if the enabler is governed by a
                cyclic event, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_cyclic_event_id(self):
        """Gets the cyclic event ``Id``.

        return: (osid.id.Id) - the cyclic event ``Id``
        raise:  IllegalState - ``is_effective_by_cyclic_event()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    cyclic_event_id = property(fget=get_cyclic_event_id)

    def get_cyclic_event(self):
        """Gets the cyclic event.

        return: (osid.calendaring.cycle.CyclicEvent) - the cyclic event
        raise:  IllegalState - ``is_effective_by_cyclic_event()`` is
                ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    cyclic_event = property(fget=get_cyclic_event)

    def is_effective_for_demographic(self):
        """Tests if the effectiveness of the enabler applies to a demographic resource.

        return: (boolean) - ``true`` if the rule apples to a
                demographic. ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_demographic_id(self):
        """Gets the demographic resource ``Id``.

        return: (osid.id.Id) - the resource ``Id``
        raise:  IllegalState - ``is_effective_for_demographic()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    demographic_id = property(fget=get_demographic_id)

    def get_demographic(self):
        """Gets the demographic resource.

        return: (osid.resource.Resource) - the resource representing the
                demographic
        raise:  IllegalState - ``is_effective_for_demographic()`` is
                ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    demographic = property(fget=get_demographic)


class OsidConstrainer(abc_osid_objects.OsidConstrainer, OsidRule):
    """An ``OsidConstrainer`` marks an interface as a control point to constrain another object.

    A constrainer may define specific methods to describe the
    constrainment or incorporate external logic using a rule.

    """




class OsidProcessor(abc_osid_objects.OsidProcessor, OsidRule):
    """An ``OsidProcessor`` is an interface describing the operation of another object.

    A processor may define specific methods to manage processing, or
    incorporate external logic using a rule.

    """




class OsidGovernator(abc_osid_objects.OsidGovernator, OsidObject, osid_markers.Operable, osid_markers.Sourceable):
    """An ``OsidGovernator`` is a control point to govern the behavior of a service.

    ``OsidGovernators`` generally indicate the presence of
    ``OsidEnablers`` and other rule governing interfaces to provide a
    means of managing service operations and constraints from a "behind
    the scenes" perspective. The ``OsidGovernator`` is a focal point for
    these various rules.

    ``OsidGovernators`` are ``Sourceable``. An ``OsidGovernator``
    implies a governance that often corresponds to a provider of a
    process as opposed to a catalog provider of ``OsidObjects``.

    ``OsidGovernators`` are ``Operable``. They indicate an active and
    operational status and related rules may be administratively
    overridden using this control point. Administratively setting the
    enabled or disabled flags in the operator overrides any enabling
    rule mapped to this ``OsidGovernator``.

    """




class OsidCompendium(abc_osid_objects.OsidCompendium, OsidObject, osid_markers.Subjugateable):
    """``OsidCompendium`` is the top level interface for reports based on measurements, calculations, summaries, or views of transactional activity within periods of time.

    This time dimension of this report may align with managed time
    periods, specific dates, or both. Oh my.

    Reports are often derived dynamically based on an examination of
    data managed elsewhere in an OSID. Reports may also be directly
    managed outside where it is desirable to capture summaries without
    the detail of the implied evaluated data. The behavior of a direct
    create or update of a report is not specified but is not limited to
    an override or a cascading update of underlying data.

    The start and end date represents the date range used in the
    evaluation of the transactional data on which this report is based.
    The start and end date may be the same indicating that the
    evaluation occurred at a point in time rather than across a date
    range. The start and end date requested may differ from the start
    and end date indicated in this report because of the inability to
    interpolate or extrapolate the date. These dates should be examined
    to understand what actually occurred and to what dates the
    information in this report pertains.

    These dates differ from the dates the report itself was requested,
    created, or modified. The dates refer to the context of the
    evaluation. In a managed report, the dates are simply the dates to
    which the report information pertains. The history of a single
    report may be examined in the Journaling OSID.

    For example, the Location of a Resource at 12:11pm is reported to be
    in Longwood and at 12:23pm is reported to be at Chestnut Hill. A
    request of a ``ResourceLocation``. A data correction may update the
    Longwood time to be 12:09pm. The update of the ``ResourceLocation``
    from 12:11pm to 12:09pm may be examined in the Journaling OSID while
    the 12:11pm time would not longer be visible in current versions of
    this report.

    Reports may be indexed by a managed time period such as a ``Term``
    or ``FiscalPeriod``. The evaluation dates may map to the opening and
    closing dates of the time period. Evaluation dates that differ from
    the time period may indicate that the transactional data is
    incomplete for that time period or that the report was calculated
    using a requested date range.

    ``OsidCompendiums`` are subjugates to other ``OsidObjects`` in that
    what is reported is tied to an instance of a dimension such as a
    person, account, or an ``OsidCatalog`` .

    """

    def get_start_date(self):
        """Gets the start date used in the evaluation of the transactional data on which this report is based.

        return: (osid.calendaring.DateTime) - the date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    start_date = property(fget=get_start_date)

    def get_end_date(self):
        """Gets the end date used in the evaluation of the transactional data on which this report is based.

        return: (osid.calendaring.DateTime) - the date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    end_date = property(fget=get_end_date)

    def is_interpolated(self):
        """Tests if this report is interpolated within measured data or known transactions.

        Interpolation may occur if the start or end date fall between
        two known facts or managed time period.

        return: (boolean) - ``true`` if this report is interpolated,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def is_extrapolated(self):
        """Tests if this report is extrapolated outside measured data or known transactions.

        Extrapolation may occur if the start or end date fall outside
        two known facts or managed time period. Extrapolation may occur
        within a managed time period in progress where the results of
        the entire time period are projected.

        return: (boolean) - ``true`` if this report is extrapolated,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class OsidCapsule(abc_osid_objects.OsidCapsule):
    """``OsidCapsule`` wraps other objects.

    The interface has no meaning other than to return a set of
    semantically unrelated objects from a method.

    """




class OsidForm(abc_osid_objects.OsidForm, osid_markers.Identifiable, osid_markers.Suppliable):
    """The ``OsidForm`` is the vehicle used to create and update objects.

    The form is a container for data to be sent to an update or create
    method of a session. Applications should persist their own data
    until a form is successfully submitted in an update or create
    transaction.

    The form may provide some feedback as to the validity of certain
    data updates before the update transaction is issued to the
    correspodning session but a successful modification of the form is
    not a guarantee of success for the update transaction. A consumer
    may elect to perform all updates within a single update transaction
    or break up a large update intio smaller units. The tradeoff is the
    granularity of error feedback vs. the performance gain of a single
    transaction.

    ``OsidForms`` are ``Identifiable``. The ``Id`` of the ``OsidForm``
    is used to uniquely identify the update or create transaction and
    not that of the object being updated. Currently, it is not necessary
    to have these ``Ids`` persisted.

    As with all aspects of the OSIDs, nulls cannot be used. Methods to
    clear values are also defined in the form.

    A new ``OsidForm`` should be acquired for each transaction upon an
    ``OsidObject``. Forms should not be reused from one object to
    another even if the supplied data is the same as the forms may
    encapsulate data specific to the object requested. Example of
    changing a display name and a color defined in a color interface
    extension:
      ObjectForm form = session.getObjectFormForUpdate(objectId);
      form.setDisplayName("new name");
      ColorForm recordForm = form.getFormRecord(colorRecordType);
      recordForm.setColor("green");
      session.updateObject(objectId, form);



    """

    # pylint: disable=no-self-use
    # MUCH OF THIS SHOULD BE MOVED TO A UTILITY MODULE

    _namespace = 'osid.OsidForm'

    def __init__(self, runtime=None, proxy=None, **kwargs):
        self._identifier = str(uuid.uuid4())
        self._mdata = None
        self._for_update = None
        # self._runtime = None # This is now being set in Extensible by higher order objects
        # self._proxy = None # This is now being set in Extensible by higher order objects
        self._kwargs = kwargs
        self._locale_map = dict()
        locale = get_locale_with_proxy(proxy)
        self._locale_map['languageTypeId'] = str(locale.get_language_type())
        self._locale_map['scriptTypeId'] = str(locale.get_script_type())
        if runtime is not None:
            self._set_authority(runtime=runtime)
        if 'catalog_id' in kwargs:
            self._catalog_id = kwargs['catalog_id']

    def _init_metadata(self):
        """Initialize OsidObjectForm metadata."""

        # pylint: disable=attribute-defined-outside-init
        # this method is called from descendent __init__
        self._mdata.update(default_mdata.get_osid_form_mdata())
        update_display_text_defaults(self._mdata['journal_comment'], self._locale_map)
        for element_name in self._mdata:
            self._mdata[element_name].update(
                {'element_id': Id(self._authority,
                                  self._namespace,
                                  element_name)})
        self._journal_comment_default = self._mdata['journal_comment']['default_string_values'][0]
        self._validation_messages = {}

    def _init_map(self):
        self._journal_comment = self._journal_comment_default

    def _init_gstudio_map(self, record_types=None):
        """Initialize gstudio form elements"""

    def _init_form(self):
        """Initialize form elements"""

    def get_id(self):
        """ Override get_id as implemented in Identifiable.

        for the purpose of returning an Id unique to this form for
        submission purposed as recommended in the osid specification.
        This implementation substitutes the intialized Python uuid4
        identifier, and the form namespace from the calling Osid Form.

         """
        return Id(identifier=self._identifier,
                  namespace=self._namespace,
                  authority=self._authority)

    def _is_valid_input(self, inpt, metadata, array):
        """The _is_valid_input method takes three arguments:

        the user input to be checked, the associated  osid.Metadata object
        containing validation requirements and a boolean value indicating
        whether this is an array value.

        """
        # pylint: disable=too-many-branches,no-self-use
        # Please redesign, and move to utility module
        syntax = metadata.get_syntax

        ##
        # First check if this is a required data element
        if metadata.is_required == True and not inpt:
            return False

        valid = True # Innocent until proven guilty
        ##
        # Recursively run through all the elements of an array
        if array == True:
            if len(inpt) < metadata['minimum_elements']:
                valid = False
            elif len(inpt) > metadata['maximum_elements']:
                valid = False
            else:
                for element in array:
                    valid = (valid and self._is_valid_input(element, metadata, False))
        ##
        # Run through all the possible syntax types
        elif syntax == 'ID':
            valid = self._is_valid_id(inpt)
        elif syntax == 'TYPE':
            valid = self._is_valid_type(inpt)
        elif syntax == 'BOOLEAN':
            valid = self._is_valid_boolean(inpt)
        elif syntax == 'STRING':
            valid = self._is_valid_string(inpt, metadata)
        elif syntax == 'INTEGER':
            valid = self._is_valid_integer(inpt, metadata)
        elif syntax == 'DECIMAL':
            valid = self._is_valid_decimal(inpt, metadata)
        elif syntax == 'DATETIME':
            valid = self._is_valid_date_time(inpt, metadata)
        elif syntax == 'DURATION':
            valid = self._is_valid_duration(inpt, metadata)
        elif syntax == 'CARDINAL':
            valid = self._is_valid_cardinal(inpt, metadata)
        elif syntax == 'INTEGER':
            valid = self._is_valid_integer(inpt, metadata)
        elif syntax == 'DECIMAL':
            valid = self._is_valid_decimal(inpt, metadata)
        else:
            raise errors.OperationFailed('no validation function available for ' + syntax)

        return valid

    def _is_valid_id(self, inpt):
        """Checks if input is a valid Id"""
        from dlkit.abstract_osid.id.primitives import Id as abc_id
        if isinstance(inpt, abc_id):
            return True
        else:
            return False

    def _is_valid_type(self, inpt):
        """Checks if input is a valid Type"""
        from dlkit.abstract_osid.type.primitives import Type as abc_type
        if isinstance(inpt, abc_type):
            return True
        else:
            return False

    def _is_valid_boolean(self, inpt):
        """Checks if input is a valid boolean"""
        if isinstance(inpt, bool):
            return True
        else:
            return False

    def _is_valid_string(self, inpt, metadata):
        """Checks if input is a valid string"""
        if not isinstance(inpt, basestring):
            return False
        if metadata.get_minimum_string_length() and len(inpt) < metadata.get_minimum_string_length():
            return False
        elif metadata.get_maximum_string_length() and len(inpt) > metadata.get_maximum_string_length():
            return False
        if metadata.get_string_set() and inpt not in metadata.get_string_set():
            return False
        else:
            return True

    def _get_display_text(self, inpt, metadata):
        if metadata.is_read_only():
            raise errors.NoAccess()
        if isinstance(inpt, abc_display_text):
            display_text = inpt
        elif self._is_valid_string(inpt, metadata):
            display_text = dict(metadata.get_default_string_values()[0])
            display_text.update({'text': inpt})
        else:
            raise errors.InvalidArgument()
        return display_text

    def _is_valid_cardinal(self, inpt, metadata):
        """Checks if input is a valid cardinal value"""
        if not isinstance(inpt, int):
            return False
        if metadata.get_minimum_cardinal() and inpt < metadata.get_maximum_cardinal():
            return False
        if metadata.get_maximum_cardinal() and inpt > metadata.get_minimum_cardinal():
            return False
        if metadata.get_cardinal_set() and inpt not in metadata.get_cardinal_set():
            return False
        else:
            return True

    def _is_valid_integer(self, inpt, metadata):
        """Checks if input is a valid integer value"""
        if not isinstance(inpt, int):
            return False
        if metadata.get_minimum_integer() and inpt < metadata.get_maximum_integer():
            return False
        if metadata.get_maximum_integer() and inpt > metadata.get_minimum_integer():
            return False
        if metadata.get_integer_set() and inpt not in metadata.get_integer_set():
            return False
        else:
            return True

    def _is_valid_decimal(self, inpt, metadata):
        """Checks if input is a valid decimal value"""
        if not (isinstance(inpt, float) or isinstance(inpt, Decimal)):
            return False
        if not isinstance(inpt, Decimal):
            inpt = Decimal(str(inpt))
        if metadata.get_minimum_decimal() and inpt < metadata.get_minimum_decimal():
            return False
        if metadata.get_maximum_decimal() and inpt > metadata.get_maximum_decimal():
            return False
        if metadata.get_decimal_set() and inpt not in metadata.get_decimal_set():
            return False
        if metadata.get_decimal_scale() and len(str(inpt).split('.')[-1]) != metadata.get_decimal_scale():
            return False
        else:
            return True

    def _is_valid_date_time(self, inpt, metadata):
        """Checks if input is a valid DateTime object"""
        # NEED TO ADD CHECKS FOR OTHER METADATA, LIKE MINIMUM, MAXIMUM, ETC.
        from dlkit.abstract_osid.calendaring.primitives import DateTime as abc_datetime
        if isinstance(inpt, abc_datetime):
            return True
        else:
            return False

    def _is_valid_timestamp(self, *args, **kwargs):
        """Checks if input is a valid timestamp"""
        # This should be temporary to deal with a bug in the OSID RC3 spec
        # Check assessment.AssessmentOffered.set_deadline to see if this
        # is still required.
        return self._is_valid_date_time(*args, **kwargs)

    def _is_valid_duration(self, inpt, metadata):
        """Checks if input is a valid Duration"""
        # NEED TO ADD CHECKS FOR OTHER METADATA, LIKE MINIMUM, MAXIMUM, ETC.
        from dlkit.abstract_osid.calendaring.primitives import Duration as abc_duration
        if isinstance(inpt, abc_duration):
            return True
        else:
            return False

    def _is_in_set(self, inpt, metadata):
        """checks if the input is in the metadata's *_set list"""
        # makes an assumption there is only one _set in the metadata dict
        get_set_methods = [m for m in dir(metadata) if 'get_' in m and '_set' in m]
        set_results = None
        for m in get_set_methods:
            try:
                set_results = getattr(metadata, m)()
                break
            except errors.IllegalState:
                pass
        if set_results is not None and inpt in set_results:
            return True
        return False

    def is_for_update(self):
        """Tests if this form is for an update operation.

        return: (boolean) - ``true`` if this form is for an update
                operation, ``false`` if for a create operation
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._for_update

    def get_default_locale(self):
        """Gets a default locale for ``DisplayTexts`` when a locale is not specified.

        return: (osid.locale.Locale) - the default locale
        *compliance: mandatory -- This method must be implemented.*

        """
        # from ..locale.objects import Locale

        # If no constructor arguments are given it is expected that the
        # locale service will return the default Locale.
        return get_locale_with_proxy(self._proxy)

    default_locale = property(fget=get_default_locale)

    def get_locales(self):
        """Gets a list of locales for available ``DisplayText`` translations that can be performed using this form.

        return: (osid.locale.LocaleList) - a list of available locales
                or an empty list if no translation operations are
                available
        *compliance: mandatory -- This method must be implemented.*

        """
        # Someday I might have a real implementation
        # For now only default Locale is supported
        from ..locale.objects import LocaleList
        return LocaleList([])

    locales = property(fget=get_locales)

    @utilities.arguments_not_none
    def set_locale(self, language_type, script_type):
        """Specifies a language and script type for ``DisplayText`` fields in this form.

        Setting a locale to something other than the default locale may
        affect the ``Metadata`` in this form.

        If multiple locales are available for managing translations, the
        ``Metadata`` indicates the fields are unset as they may be
        returning a defeult value based on the default locale.

        arg:    language_type (osid.type.Type): the language type
        arg:    script_type (osid.type.Type): the script type
        raise:  NullArgument - ``language_type`` or ``script_type`` is
                null
        raise:  Unsupported - ``language_type`` and ``script_type`` not
                available from ``get_locales()``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Someday I might have a real implementation
        # For now only default Locale is supported
        self._locale_map['languageType'] = language_type
        self._locale_map['scriptType'] = script_type

    def get_journal_comment_metadata(self):
        """Gets the metadata for the comment corresponding to this form submission.

        The comment is used for describing the nature of the change to
        the corresponding object for the purposes of logging and
        auditing.

        return: (osid.Metadata) - metadata for the comment
        *compliance: mandatory -- This method must be implemented.*

        """
        return Metadata(**self._mdata['journal_comment'])

    journal_comment_metadata = property(fget=get_journal_comment_metadata)

    @utilities.arguments_not_none
    def set_journal_comment(self, comment):
        """Sets a comment.

        arg:    comment (string): the new comment
        raise:  InvalidArgument - ``comment`` is invalid
        raise:  NoAccess - ``Metadata.isReadonly()`` is ``true``
        raise:  NullArgument - ``comment`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._my_map['journal_comment'] = self._get_display_text(comment, self.get_journal_comment_metadata())

    journal_comment = property(fset=set_journal_comment)

    def is_valid(self):
        """Tests if ths form is in a valid state for submission.

        A form is valid if all required data has been supplied compliant
        with any constraints.

        return: (boolean) - ``false`` if there is a known error in this
                form, ``true`` otherwise
        raise:  OperationFailed - attempt to perform validation failed
        *compliance: mandatory -- This method must be implemented.*

        """
        # It is assumed that all setter methods check validity so there
        # should never be a state where invalid data exists in the form.
        # And if you believe that...
        return True

    def get_validation_messages(self):
        """Gets text messages corresponding to additional instructions to pass form validation.

        return: (osid.locale.DisplayText) - a list of messages
        *compliance: mandatory -- This method must be implemented.*

        """
        # See note above
        return []

    validation_messages = property(fget=get_validation_messages)

    def get_invalid_metadata(self):
        """Gets a list of metadata for the elements in this form which are not valid.

        return: (osid.Metadata) - invalid metadata
        *compliance: mandatory -- This method must be implemented.*

        """
        # See notes above
        return []

    invalid_metadata = property(fget=get_invalid_metadata)


class OsidIdentifiableForm(abc_osid_objects.OsidIdentifiableForm, OsidForm):
    """The ``OsidIdentifiableForm`` is used to create and update identifiable objects.

    The form is a container for data to be sent to an update or create
    method of a session.

    """




class OsidExtensibleForm(abc_osid_objects.OsidExtensibleForm, OsidForm, osid_markers.Extensible):
    """The ``OsidExtensibleForm`` is used to create and update extensible objects.

    The form is a container for data to be sent to an update or create
    method of a session.

    """
    def __init__(self, **kwargs):
        osid_markers.Extensible.__init__(self, **kwargs)
        # sets runtime and proxy to the current object
    def _init_map(self, record_types):
        self._gstudio_map['recordTypeIds'] = []
        self._my_map['recordTypeIds'] = []
        if record_types is not None:
            self._init_records(record_types)
        self._supported_record_type_ids = self._gstudio_map['recordTypeIds']
        self._supported_record_type_ids = self._my_map['recordTypeIds']

    def _init_gstudio_map(self, record_types=None):
        """Initialize gstudio map for form"""

    def _get_record(self, record_type):
        """This overrides _get_record in osid.Extensible.

        Perhaps we should leverage it somehow?

        """
        if (not self.has_record_type(record_type) and
                record_type.get_identifier() not in self._record_type_data_sets):
            raise errors.Unsupported()
        if str(record_type) not in self._records:
            record_initialized = self._init_record(str(record_type))
            if record_initialized and str(record_type) not in self._gstudio_map['recordTypeIds']:
                self._gstudio_map['recordTypeIds'].append(str(record_type))
        return self._records[str(record_type)]

    def _init_record(self, record_type_idstr):
        """Override this from osid.Extensible because Forms use a different
        attribute in record_type_data."""
        record_type_data = self._record_type_data_sets[Id(record_type_idstr).get_identifier()]
        module = importlib.import_module(record_type_data['module_path'])
        record = getattr(module, record_type_data['form_record_class_name'])
        if record is not None:
            self._records[record_type_idstr] = record(self)
            return True
        else:
            return False

    def get_required_record_types(self):
        """Gets the required record types for this form.

        The required records may change as a result of other data in
        this form and should be checked before submission.

        return: (osid.type.TypeList) - a list of required record types
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    required_record_types = property(fget=get_required_record_types)


class OsidBrowsableForm(abc_osid_objects.OsidBrowsableForm, OsidForm):
    """The ``OsidBrowsableForm`` is used to create and update browsable objects.

    The form is a container for data to be sent to an update or create
    method of a session.

    """




class OsidTemporalForm(abc_osid_objects.OsidTemporalForm, OsidForm):
    """This form is used to create and update temporals."""

    _namespace = "osid.OsidTemporalForm"

    def __init__(self):
        self._mdata = None

    def _init_metadata(self, **kwargs):
        # pylint: disable=attribute-defined-outside-init
        # this method is called from descendent __init__
        self._mdata.update(default_mdata.get_osid_temporal_mdata())
        self._mdata['start_date'].update({'default_date_time_values': [datetime.datetime.utcnow()]})
        self._mdata['end_date'].update({
            'default_date_time_values': [datetime.datetime.utcnow() + datetime.timedelta(weeks=9999)]
        })

    def _init_form(self):
        """Initialize form elements"""

    def _init_map(self):
        # pylint: disable=attribute-defined-outside-init
        # this method is called from descendent __init__
        self._my_map['startDate'] = self._mdata['start_date']['default_date_time_values'][0]
        self._my_map['endDate'] = self._mdata['end_date']['default_date_time_values'][0]

    def get_start_date_metadata(self):
        """Gets the metadata for a start date.

        return: (osid.Metadata) - metadata for the date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    start_date_metadata = property(fget=get_start_date_metadata)

    @utilities.arguments_not_none
    def set_start_date(self, date):
        """Sets the start date.

        arg:    date (osid.calendaring.DateTime): the new date
        raise:  InvalidArgument - ``date`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``date`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_start_date(self):
        """Clears the start date.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    start_date = property(fset=set_start_date, fdel=clear_start_date)

    def get_end_date_metadata(self):
        """Gets the metadata for an end date.

        return: (osid.Metadata) - metadata for the date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    end_date_metadata = property(fget=get_end_date_metadata)

    @utilities.arguments_not_none
    def set_end_date(self, date):
        """Sets the end date.

        arg:    date (osid.calendaring.DateTime): the new date
        raise:  InvalidArgument - ``date`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``date`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_end_date(self):
        """Clears the end date.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    end_date = property(fset=set_end_date, fdel=clear_end_date)


class OsidSubjugateableForm(abc_osid_objects.OsidSubjugateableForm, OsidForm):
    """This form is used to create and update dependent objects."""




class OsidAggregateableForm(abc_osid_objects.OsidAggregateableForm, OsidForm):
    """This form is used to create and update assemblages."""




class OsidContainableForm(abc_osid_objects.OsidContainableForm, OsidForm):
    """This form is used to create and update containers."""

    def __init__(self):
        self._mdata = None
        self._sequestered_default = None
        self._sequestered = None

    def _init_metadata(self):
        self._mdata.update(default_mdata.get_osid_containable_mdata())
        self._sequestered_default = self._mdata['sequestered']['default_boolean_values'][0]
        self._sequestered = self._sequestered_default

    def _init_form(self):
        """Initialize form elements"""

    def _init_map(self):
        self._my_map['sequestered'] = self._sequestered_default

    def get_sequestered_metadata(self):
        """Gets the metadata for the sequestered flag.

        return: (osid.Metadata) - metadata for the sequestered flag
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    sequestered_metadata = property(fget=get_sequestered_metadata)

    @utilities.arguments_not_none
    def set_sequestered(self, sequestered):
        """Sets the sequestered flag.

        arg:    sequestered (boolean): the new sequestered flag
        raise:  InvalidArgument - ``sequestered`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_sequestered(self):
        """Clears the sequestered flag.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    sequestered = property(fset=set_sequestered, fdel=clear_sequestered)


class OsidSourceableForm(abc_osid_objects.OsidSourceableForm, OsidForm):
    """This form is used to create and update sourceables."""

    def __init__(self):
        self._mdata = None
        self._provider_default = None
        self._branding_default = None
        self._license_default = None

    def _init_metadata(self):
        self._mdata.update(default_mdata.get_osid_sourceable_mdata())
        update_display_text_defaults(self._mdata['license'], self._locale_map)
        self._provider_default = self._mdata['provider']['default_id_values'][0]
        self._branding_default = self._mdata['branding']['default_id_values']
        self._license_default = self._mdata['license']['default_string_values'][0]

    def _init_form(self, effective_agent_id=None):
        """Initialize form elements"""
        self._provider_id = effective_agent_id
        self._branding_ids = self._branding_default
        self._license_id = self._license_default


    def _init_gstudio_map(self, effective_agent_id=None, **kwargs):
        """Initialize map for form"""
        self._gstudio_map['license'] = self._license_default.get_text()

    def _init_map(self, effective_agent_id=None, **kwargs):
        if 'effective_agent_id' in kwargs:
            try:
                mgr = self._get_provider_manager('RESOURCE', local=True)
                agent_session = mgr.get_resource_agent_session(proxy=self._proxy)
                agent_session.use_federated_bin_view()
                resource_idstr = str(agent_session.get_resource_id_by_agent(kwargs['effective_agent_id']))
            except (errors.OperationFailed,
                    errors.Unsupported,
                    errors.Unimplemented,
                    errors.NotFound):
                resource_idstr = self._provider_default
            self._my_map['providerId'] = resource_idstr
        else:
            self._my_map['providerId'] = self._provider_default
        self._my_map['brandingIds'] = self._branding_default
        self._my_map['license'] = self._license_default
        # self._my_map['license'] = dict(self._license_default)

    def get_provider_metadata(self):
        """Gets the metadata for a provider.

        return: (osid.Metadata) - metadata for the provider
        *compliance: mandatory -- This method must be implemented.*

        """
        metadata = dict(self._mdata['provider'])
        metadata.update({'existing_id_values': self._provider_id})
        return Metadata(**metadata)

    provider_metadata = property(fget=get_provider_metadata)

    @utilities.arguments_not_none
    def set_provider(self, provider_id):
        """Sets a provider.

        arg:    provider_id (osid.id.Id): the new provider
        raise:  InvalidArgument - ``provider_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``provider_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._provider_id = provider_id

    def clear_provider(self):
        """Removes the provider.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._provider_id = self._provider_default


    provider = property(fset=set_provider, fdel=clear_provider)

    def get_branding_metadata(self):
        """Gets the metadata for the asset branding.

        return: (osid.Metadata) - metadata for the asset branding.
        *compliance: mandatory -- This method must be implemented.*

        """
        metadata = dict(self._mdata['branding'])
        metadata.update({'existing_id_values': self._branding_ids})
        return Metadata(**metadata)


    branding_metadata = property(fget=get_branding_metadata)

    @utilities.arguments_not_none
    def set_branding(self, asset_ids):
        """Sets the branding.

        arg:    asset_ids (osid.id.Id[]): the new assets
        raise:  InvalidArgument - ``asset_ids`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``asset_ids`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._branding_ids = asset_ids

    def clear_branding(self):
        """Removes the branding.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._branding_ids = self._branding_default

    branding = property(fset=set_branding, fdel=clear_branding)

    def get_license_metadata(self):
        """Gets the metadata for the license.

        return: (osid.Metadata) - metadata for the license
        *compliance: mandatory -- This method must be implemented.*

        """
        metadata = dict(self._mdata['license'])
        metadata.update({'existing_string_values': self._license_id})
        return Metadata(**metadata)


    license_metadata = property(fget=get_license_metadata)

    @utilities.arguments_not_none
    def set_license(self, license_):
        """Sets the license.

        arg:    license (string): the new license
        raise:  InvalidArgument - ``license`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``license`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._license_id = license_
        self._my_map['license'] = self._get_display_text(license_, self.get_license_metadata())
        self._gstudio_map['license'] = self._get_display_text(license_, self.get_license_metadata())['text']

    def clear_license(self):
        """Removes the license.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._license_id = self._license_default
        self._my_map['copyright'] = dict(self._license_default)
        self._gstudio_map['copyright'] = dict(self._license_default)['text']

    license_ = property(fset=set_license, fdel=clear_license)


class OsidFederateableForm(abc_osid_objects.OsidFederateableForm, OsidForm):
    """This form is used to create and update federateables."""

    def __init__(self):
        pass




class OsidOperableForm(abc_osid_objects.OsidOperableForm, OsidForm):
    """This form is used to create and update operables."""

    def __init__(self):
        # Need to implement someday
        pass

    def _init_metadata(self):
        # Need to implement someday
        pass

    def _init_form(self):
        """Initialize form elements"""

    def get_enabled_metadata(self):
        """Gets the metadata for the enabled flag.

        return: (osid.Metadata) - metadata for the enabled flag
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    enabled_metadata = property(fget=get_enabled_metadata)

    @utilities.arguments_not_none
    def set_enabled(self, enabled):
        """Sets the administratively enabled flag.

        arg:    enabled (boolean): the new enabled flag
        raise:  InvalidArgument - ``enabled`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_enabled(self):
        """Removes the administratively enabled flag.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    enabled = property(fset=set_enabled, fdel=clear_enabled)

    def get_disabled_metadata(self):
        """Gets the metadata for the disabled flag.

        return: (osid.Metadata) - metadata for the disabled flag
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    disabled_metadata = property(fget=get_disabled_metadata)

    @utilities.arguments_not_none
    def set_disabled(self, disabled):
        """Sets the administratively disabled flag.

        arg:    disabled (boolean): the new disabled flag
        raise:  InvalidArgument - ``disabled`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_disabled(self):
        """Removes the administratively disabled flag.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    disabled = property(fset=set_disabled, fdel=clear_disabled)


class OsidObjectForm(abc_osid_objects.OsidObjectForm, OsidIdentifiableForm, OsidExtensibleForm, OsidBrowsableForm):
    """The ``OsidObjectForm`` is used to create and update ``OsidObjects``.

    The form is not an ``OsidObject`` but merely a container for data to
    be sent to an update or create method of a session. A provider may
    or may not combine the ``OsidObject`` and ``OsidObjectForm``
    interfaces into a single object.

    Generally, a set method parallels each get method of an
    ``OsidObject``. Additionally, ``Metadata`` may be examined for each
    data element to assist in understanding particular rules concerning
    acceptable data.

    The form may provide some feedback as to the validity of certain
    data updates before the update transaction is issued to the
    correspodning session but a successful modification of the form is
    not a guarantee of success for the update transaction. A consumer
    may elect to perform all updates within a single update transaction
    or break up a large update intio smaller units. The tradeoff is the
    granularity of error feedback vs. the performance gain of a single
    transaction.

    As with all aspects of the OSIDs, nulls cannot be used. Methods to
    clear values are also defined in the form.

    A new ``OsidForm`` should be acquired for each transaction upon an
    ``OsidObject``. Forms should not be reused from one object to
    another even if the supplied data is the same as the forms may
    encapsulate data specific to the object requested. Example of
    changing a display name and a color defined in a color interface
    extension:
      ObjectForm form = session.getObjectFormForUpdate(objectId);
      form.setDisplayName("new name");
      ColorForm recordForm = form.getFormRecord(colorRecordType);
      recordForm.setColor("green");
      session.updateObject(objectId, form);



    """

    _namespace = "osid.OsidObjectForm"

    def __init__(self, osid_object_map=None, **kwargs): # removed record_types=None, runtime=None, 
        self._display_name_default = None
        self._description_default = None
        self._genus_type_default = None
        OsidForm.__init__(self, **kwargs)
        OsidExtensibleForm.__init__(self, **kwargs)
        # Req for update
        if osid_object_map is not None:
            self._for_update = True
            self._my_map = osid_object_map
            self._load_records(osid_object_map['recordTypeIds'])
        else:
            self._for_update = False
            self._my_map = {}
            self._gstudio_map = {}

    def _init_metadata(self, **kwargs):
        """Initialize metadata for form"""
        self._mdata.update(default_mdata.get_osid_object_mdata())
        OsidForm._init_metadata(self)
        if 'default_display_name' in kwargs:
            self._mdata['display_name']['default_string_values'][0]['text'] = kwargs['default_display_name']
        update_display_text_defaults(self._mdata['display_name'], self._locale_map)
        if 'default_description' in kwargs:
            self._mdata['description']['default_string_values'][0]['text'] = kwargs['default_description']
        update_display_text_defaults(self._mdata['description'], self._locale_map)
        self._display_name_default = dict(self._mdata['display_name']['default_string_values'][0])
        self._description_default = dict(self._mdata['description']['default_string_values'][0])
        # self._display_name_default = self._mdata['display_name']
        # self._description_default = self._mdata['description']
        # self._display_name_default = unicode(self._mdata['display_name']['default_string_values'][0]['text'])
        # self._description_default = unicode(self._mdata['description']['default_string_values'][0]['text'])
        self._genus_type_default = self._mdata['genus_type']['default_type_values'][0]

        if 'mdata' in kwargs:
            self._mdata.update(kwargs['mdata'])


    def _init_map(self, record_types=None):
        """Initialize map for form"""
        OsidForm._init_map(self)
        self._my_map['displayName'] = dict(self._display_name_default)
        self._my_map['description'] = dict(self._description_default)
        self._my_map['genusTypeId'] = self._genus_type_default
        OsidExtensibleForm._init_map(self, record_types)

    def _init_gstudio_map(self, record_types=None, **kwargs):
        """Initialize map for form"""
        OsidForm._init_gstudio_map(self)
        """
        Useful to fill map in 'edit' action 
        by passing gstudio_node like 
        repository.AssetForm.get_asset_content_form_for_update
        """
        if "gstudio_node" in kwargs:
            self._gstudio_map['name'] = kwargs['gstudio_node']['name']
            self._gstudio_map['altnames'] = kwargs['gstudio_node']['altnames']
            self._gstudio_map['content'] = kwargs['gstudio_node']['content']
            self._gstudio_map['content_org'] = kwargs['gstudio_node']['content']
            self.license = DisplayText(display_text_map={
                                    'text':kwargs['gstudio_node']['legal']['license'],
                                    'languageTypeId': str(DEFAULT_LANGUAGE_TYPE),
                                    'scriptTypeId': str(DEFAULT_SCRIPT_TYPE),
                                    'formatTypeId': str(DEFAULT_FORMAT_TYPE)
                                })
            # self._gstudio_map['license'] = get_display_text_map(self.license)
            self._gstudio_map['license'] = self.license.get_text()
            self.copyright = DisplayText(display_text_map={
                                    'text':kwargs['gstudio_node']['legal']['copyright'],
                                    'languageTypeId': str(DEFAULT_LANGUAGE_TYPE),
                                    'scriptTypeId': str(DEFAULT_SCRIPT_TYPE),
                                    'formatTypeId': str(DEFAULT_FORMAT_TYPE)
                                })
            # self._gstudio_map['copyright'] = get_display_text_map(self.copyright)
            self._gstudio_map['copyright'] = self.copyright.get_text()
        else:
            self._gstudio_map['name'] = self._display_name_default['text']
            self._gstudio_map['altnames'] = self._display_name_default['text']
            self._gstudio_map['content'] = self._description_default['text']
            self._gstudio_map['content_org'] = self._description_default['text']
        
        self._my_map['genusTypeId'] = self._genus_type_default
        self._gstudio_map['genusTypeId'] = self._genus_type_default
        OsidExtensibleForm._init_gstudio_map(self, record_types)

    def get_display_name_metadata(self):
        """Gets the metadata for a display name.

        return: (osid.Metadata) - metadata for the display name
        *compliance: mandatory -- This method must be implemented.*

        """
        metadata = dict(self._mdata['display_name'])
        metadata.update({'existing_string_values': self._my_map['displayName']['text']})
        # metadata.update({'existing_string_values': self._display_name})
        return Metadata(**metadata)

    display_name_metadata = property(fget=get_display_name_metadata)

    @utilities.arguments_not_none
    def set_display_name(self, display_name):
        """Sets a display name.

        A display name is required and if not set, will be set by the
        provider.

        arg:    display_name (string): the new display name
        raise:  InvalidArgument - ``display_name`` is invalid
        raise:  NoAccess - ``Metadata.isReadonly()`` is ``true``
        raise:  NullArgument - ``display_name`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._gstudio_map['name'] = unicode(display_name)
        self._gstudio_map['altnames'] = unicode(display_name)
        self._display_name = display_name
        self._my_map['displayName'] = self._get_display_text(display_name, self.get_display_name_metadata())

    def clear_display_name(self):
        """Clears the display name.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        if (self.get_display_name_metadata().is_read_only() or
                self.get_display_name_metadata().is_required()):
            raise errors.NoAccess()
        self._gstudio_map['name'] = self._display_name_default['text']
        self._my_map['displayName'] = dict(self._display_name_default)

        # self._display_name = self._display_name_default

    display_name = property(fset=set_display_name, fdel=clear_display_name)

    def get_description_metadata(self):
        """Gets the metadata for a description.

        return: (osid.Metadata) - metadata for the description
        *compliance: mandatory -- This method must be implemented.*

        """
        metadata = dict(self._mdata['description'])
        metadata.update({'existing_string_values': self._my_map['description']['text']})
        # metadata.update({'existing_string_values': self._description})
        return Metadata(**metadata)


    description_metadata = property(fget=get_description_metadata)

    @utilities.arguments_not_none
    def set_description(self, description):
        """Sets a description.

        arg:    description (string): the new description
        raise:  InvalidArgument - ``description`` is invalid
        raise:  NoAccess - ``Metadata.isReadonly()`` is ``true``
        raise:  NullArgument - ``description`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._gstudio_map['content'] = unicode(description)
        self._gstudio_map['content_org'] = unicode(description)
        self._description = description
        self._my_map['description'] = self._get_display_text(description, self.get_description_metadata())

    def clear_description(self):
        """Clears the description.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        if (self.get_description_metadata().is_read_only() or
                self.get_description_metadata().is_required()):
            raise errors.NoAccess()
        self._gstudio_map['content'] = self._description_default['text']
        # self._description = self._description_default
        self._my_map['description'] = dict(self._description_default)

    description = property(fset=set_description, fdel=clear_description)

    def get_genus_type_metadata(self):
        """Gets the metadata for a genus type.

        return: (osid.Metadata) - metadata for the genus
        *compliance: mandatory -- This method must be implemented.*

        """
        metadata = dict(self._mdata['genus_type'])
        metadata.update({'existing_string_values': self._my_map['genusTypeId']})
        # metadata.update({'existing_string_values': self._genus_type})
        return Metadata(**metadata)

    genus_type_metadata = property(fget=get_genus_type_metadata)

    @utilities.arguments_not_none
    def set_genus_type(self, genus_type):
        """Sets a genus.

        A genus cannot be cleared because all objects have at minimum a
        root genus.

        arg:    genus_type (osid.type.Type): the new genus
        raise:  InvalidArgument - ``genus_type`` is invalid
        raise:  NoAccess - ``Metadata.isReadonly()`` is ``true``
        raise:  NullArgument - ``genus_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        print "Genus value: ", genus_type, ' and : ', str(genus_type)
        if self.get_genus_type_metadata().is_read_only():
            raise errors.NoAccess()
        if not self._is_valid_type(genus_type):
            raise errors.InvalidArgument()
        self._my_map['genusTypeId'] = str(genus_type)
        self._gstudio_map['genusTypeId'] = str(genus_type)
        # self._genus_type = genus_type

    def clear_genus_type(self):
        """Clears the genus type.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        if (self.get_genus_type_metadata().is_read_only() or
                self.get_genus_type_metadata().is_required()):
            raise errors.NoAccess()
        self._my_map['genusTypeId'] = self._genus_type_default
        self._gstudio_map['genusTypeId'] = self._genus_type_default
        self._genus_type = self._genus_type_default

    genus_type = property(fset=set_genus_type, fdel=clear_genus_type)


class OsidRelationshipForm(abc_osid_objects.OsidRelationshipForm, OsidObjectForm, OsidTemporalForm):
    """This form is used to create and update relationshps."""

    def __init__(self, **kwargs):
        OsidTemporalForm.__init__(self)
        OsidObjectForm.__init__(self, **kwargs)

    def _init_map(self, record_types=None, **kwargs):
        OsidTemporalForm._init_map(self)
        OsidObjectForm._init_map(self, record_types=record_types, **kwargs)



class OsidCatalogForm(abc_osid_objects.OsidCatalogForm, OsidObjectForm, OsidSourceableForm, OsidFederateableForm):
    """This form is used to create and update catalogs."""

    def __init__(self, **kwargs):
        OsidSourceableForm.__init__(self)
        OsidFederateableForm.__init__(self)
        OsidObjectForm.__init__(self, **kwargs)


    def _init_map(self, record_types=None, **kwargs):
        OsidSourceableForm._init_map(self, **kwargs)
        OsidFederateableForm._init_map(self)
        OsidObjectForm._init_map(self, record_types)

    def _init_gstudio_map(self, record_types=None, **kwargs):
        OsidSourceableForm._init_gstudio_map(self, **kwargs)
        OsidFederateableForm._init_gstudio_map(self)
        OsidObjectForm._init_gstudio_map(self, record_types)
        self._gstudio_map.update(default_mdata.get_gstudio_catalog_mdata())


class OsidRuleForm(abc_osid_objects.OsidRuleForm, OsidObjectForm, OsidOperableForm):
    """This form is used to create and update rules."""

    def get_rule_metadata(self):
        """Gets the metadata for an associated rule.

        return: (osid.Metadata) - metadata for the rule
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rule_metadata = property(fget=get_rule_metadata)

    @utilities.arguments_not_none
    def set_rule(self, rule_id):
        """Sets a rule.

        arg:    rule_id (osid.id.Id): the new rule
        raise:  InvalidArgument - ``rule_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``rule_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_rule(self):
        """Removes the rule.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rule = property(fset=set_rule, fdel=clear_rule)


class OsidEnablerForm(abc_osid_objects.OsidEnablerForm, OsidRuleForm, OsidTemporalForm):
    """This form is used to create and update enablers."""

    def get_schedule_metadata(self):
        """Gets the metadata for an associated schedule.

        return: (osid.Metadata) - metadata for the schedule
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    schedule_metadata = property(fget=get_schedule_metadata)

    @utilities.arguments_not_none
    def set_schedule(self, schedule_id):
        """Sets a schedule.

        arg:    schedule_id (osid.id.Id): the new schedule
        raise:  InvalidArgument - ``schedule_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``schedule_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_schedule(self):
        """Removes the schedule.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    schedule = property(fset=set_schedule, fdel=clear_schedule)

    def get_event_metadata(self):
        """Gets the metadata for an associated event.

        return: (osid.Metadata) - metadata for the event
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    event_metadata = property(fget=get_event_metadata)

    @utilities.arguments_not_none
    def set_event(self, event_id):
        """Sets an event.

        arg:    event_id (osid.id.Id): the new event
        raise:  InvalidArgument - ``event_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``event_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_event(self):
        """Removes the event.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    event = property(fset=set_event, fdel=clear_event)

    def get_cyclic_event_metadata(self):
        """Gets the metadata for the cyclic event.

        return: (osid.Metadata) - metadata for the cyclic event
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    cyclic_event_metadata = property(fget=get_cyclic_event_metadata)

    @utilities.arguments_not_none
    def set_cyclic_event(self, cyclic_event_id):
        """Sets the cyclic event.

        arg:    cyclic_event_id (osid.id.Id): the new cyclic event
        raise:  InvalidArgument - ``cyclic_event_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``cyclic_event_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_cyclic_event(self):
        """Removes the cyclic event.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    cyclic_event = property(fset=set_cyclic_event, fdel=clear_cyclic_event)

    def get_demographic_metadata(self):
        """Gets the metadata for an associated demographic.

        return: (osid.Metadata) - metadata for the resource.
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    demographic_metadata = property(fget=get_demographic_metadata)

    @utilities.arguments_not_none
    def set_demographic(self, resource_id):
        """Sets a resource demographic.

        arg:    resource_id (osid.id.Id): the new resource
        raise:  InvalidArgument - ``resource_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``resource_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_demographic(self):
        """Removes the resource demographic.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    demographic = property(fset=set_demographic, fdel=clear_demographic)


class OsidConstrainerForm(abc_osid_objects.OsidConstrainerForm, OsidRuleForm):
    """This form is used to create and update constrainers."""




class OsidProcessorForm(abc_osid_objects.OsidProcessorForm, OsidRuleForm):
    """This form is used to create and update processors."""




class OsidGovernatorForm(abc_osid_objects.OsidGovernatorForm, OsidObjectForm, OsidOperableForm, OsidSourceableForm):
    """This form is used to create and update governators."""




class OsidCompendiumForm(abc_osid_objects.OsidCompendiumForm, OsidObjectForm, OsidSubjugateableForm):
    """This form is used to create and update governators."""

    def get_start_date_metadata(self):
        """Gets the metadata for a start date.

        return: (osid.Metadata) - metadata for the date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    start_date_metadata = property(fget=get_start_date_metadata)

    @utilities.arguments_not_none
    def set_start_date(self, date):
        """Sets the start date.

        arg:    date (osid.calendaring.DateTime): the new date
        raise:  InvalidArgument - ``date`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``date`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_start_date(self):
        """Clears the start date.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    start_date = property(fset=set_start_date, fdel=clear_start_date)

    def get_end_date_metadata(self):
        """Gets the metadata for an end date.

        return: (osid.Metadata) - metadata for the date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    end_date_metadata = property(fget=get_end_date_metadata)

    @utilities.arguments_not_none
    def set_end_date(self, date):
        """Sets the end date.

        arg:    date (osid.calendaring.DateTime): the new date
        raise:  InvalidArgument - ``date`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``date`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_end_date(self):
        """Clears the end date.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    end_date = property(fset=set_end_date, fdel=clear_end_date)

    def get_interpolated_metadata(self):
        """Gets the metadata for the interpolated flag.

        return: (osid.Metadata) - metadata for the interpolated flag
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    interpolated_metadata = property(fget=get_interpolated_metadata)

    @utilities.arguments_not_none
    def set_interpolated(self, interpolated):
        """Sets the interpolated flag.

        arg:    interpolated (boolean): the new interpolated flag
        raise:  InvalidArgument - ``interpolated`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_interpolated(self):
        """Clears the interpolated flag.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    interpolated = property(fset=set_interpolated, fdel=clear_interpolated)

    def get_extrapolated_metadata(self):
        """Gets the metadata for the extrapolated flag.

        return: (osid.Metadata) - metadata for the extrapolated flag
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    extrapolated_metadata = property(fget=get_extrapolated_metadata)

    @utilities.arguments_not_none
    def set_extrapolated(self, extrapolated):
        """Sets the extrapolated flag.

        arg:    extrapolated (boolean): the new extrapolated flag
        raise:  InvalidArgument - ``extrapolated`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_extrapolated(self):
        """Clears the extrapolated flag.

        raise:  NoAccess - ``Metadata.isRequired()`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    extrapolated = property(fset=set_extrapolated, fdel=clear_extrapolated)


class OsidCapsuleForm(abc_osid_objects.OsidCapsuleForm, OsidForm):
    """This form is used to create and update capsules."""




class OsidList(abc_osid_objects.OsidList):
    """``OsidList`` is the top-level interface for all OSID lists.

    An OSID list provides sequential access, one at a time or many at a
    time, access to a set of elements. These elements are not required
    to be OsidObjects but generally are. The element retrieval methods
    are defined in the sub-interface of ``OsidList`` where the
    appropriate return type is defined.

    Osid lists are a once pass through iteration of elements. The size
    of the object set and the means in which the element set is
    generated or stored is not known. Assumptions based on the length of
    the element set by copying the entire contents of the list into a
    fixed buffer should be done with caution a awareness that an
    implementation may return a number of elements ranging from zero to
    infinity.

    Lists are returned by methods when multiple return values are
    possible. There is no guarantee that successive calls to the same
    method will return the same set of elements in a list. Unless an
    order is specified in an interface definition, the order of the
    elements is not known.

    """

    def __init__(self, iter_object=None, runtime=None, proxy=None):
        if iter_object is None:
            iter_object = []
        if isinstance(iter_object, OsidListList):
            self._count = 0
            for osid_list in iter_object:
                self._count += osid_list.available()
            iter_object = itertools.chain(*iter_object)
        elif isinstance(iter_object, dict) or isinstance(iter_object, list):
            self._count = len(iter_object)
        elif isinstance(iter_object, Cursor):
            self._count = iter_object.count(True)
        else:
            self._count = None
        self._runtime = runtime
        self._proxy = proxy
        self._iter_object = iter(iter_object)

    def __iter__(self):
        return self

    def _get_next_n(self, number=None):
        """Gets the next set of "n" elements in this list.

        The specified amount must be less than or equal to the return
        from ``available()``.

        arg:    n (cardinal): the number of ``Relationship`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.relationship.Relationship) - an array of
                ``Relationship`` elements.The length of the array is
                less than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        if number > self.available():
            # !!! This is not quite as specified (see method docs) !!!
            raise errors.IllegalState('not enough elements available in this list')
        else:
            next_list = []
            counter = 0
            while counter < number:
                try:
                    next_list.append(self.next())
                except Exception:  # Need to specify exceptions here!
                    raise errors.OperationFailed()
                counter += 1
            return next_list

    def _get_next_object(self, object_class):
        """stub"""
        try:
            next_object = OsidList.next(self)
        except StopIteration:
            raise
        except Exception:  # Need to specify exceptions here!
            raise
        if isinstance(next_object, dict):
            next_object = object_class(osid_object_map=next_object, runtime=self._runtime, proxy=self._proxy)
        elif isinstance(next_object, basestring) and object_class == Id:
            next_object = Id(next_object)
        return next_object

    def next(self):
        """next method for iterator."""
        next_object = self._iter_object.next()
        if self._count != None:
            self._count -= 1
        return next_object

    def len(self):
        """Returns number of available elements"""
        return self.available()

    def has_next(self):
        """Tests if there are more elements in this list.

        return: (boolean) - ``true`` if more elements are available in
                this list, ``false`` if the end of the list has been
                reached
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: Any errors that may result from accesing
        the underlying set of elements are to be deferred until the
        consumer attempts retrieval in which case the provider must
        return ``true`` for this method.

        """
        if self._count != None:
            # If count is available, use it
            return bool(self._count)
        else:
            # otherwise we have no idea
            return True

    def available(self):
        """Gets the number of elements available for retrieval.

        The number returned by this method may be less than or equal to
        the total number of elements in this list. To determine if the
        end of the list has been reached, the method ``has_next()``
        should be used. This method conveys what is known about the
        number of remaining elements at a point in time and can be used
        to determine a minimum size of the remaining elements, if known.
        A valid return is zero even if ``has_next()`` is true.

        This method does not imply asynchronous usage. All OSID methods
        may block.

        return: (cardinal) - the number of elements available for
                retrieval
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: Any errors that may result from accesing
        the underlying set of elements are to be deferred until the
        consumer attempts retrieval in which case the provider must
        return a positive integer for this method so the consumer can
        continue execution to receive the error. In all other
        circumstances, the provider must not return a number greater
        than the number of elements known since this number will be fed
        as a parameter to the bulk retrieval method.

        """
        if self._count != None:
            # If count is available, use it
            return self._count
        else:
            # We have no idea.
            return 0  # Don't know what to do here

    @utilities.arguments_not_none
    def skip(self, n):
        """Skip the specified number of elements in the list.

        If the number skipped is greater than the number of elements in
        the list, hasNext() becomes false and available() returns zero
        as there are no more elements to retrieve.

        arg:    n (cardinal): the number of elements to skip
        *compliance: mandatory -- This method must be implemented.*

        """
        try:
            self._iter_object.skip(n)
        except AttributeError:
            for i in range(0, n):
                self.next()


class OsidNode(abc_osid_objects.OsidNode, osid_markers.Identifiable, osid_markers.Containable):
    """A node interface for hierarchical objects.

    The ``Id`` of the node is the ``Id`` of the object represented at
    this node.

    """

    def is_root(self):
        """Tests if this node is a root in the hierarchy (has no parents).

        A node may have no more parents available in this node structure
        but is not a root in the hierarchy. If both ``is_root()`` and
        ``has_parents()`` is false, the parents of this node may be
        accessed thorugh another node structure retrieval.

        return: (boolean) - ``true`` if this node is a root in the
                hierarchy, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def has_parents(self):
        """Tests if any parents are available in this node structure.

        There may be no more parents in this node structure however
        there may be parents that exist in the hierarchy.

        return: (boolean) - ``true`` if this node has parents, ``false``
                otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_parent_ids(self):
        """Gets the parents of this node.

        return: (osid.id.IdList) - the parents of this node
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    parent_ids = property(fget=get_parent_ids)

    def is_leaf(self):
        """Tests if this node is a leaf in the hierarchy (has no children).

        A node may have no more children available in this node
        structure but is not a leaf in the hierarchy. If both
        ``is_leaf()`` and ``has_children()`` is false, the children of
        this node may be accessed thorugh another node structure
        retrieval.

        return: (boolean) - ``true`` if this node is a leaf in the
                hierarchy, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def has_children(self):
        """Tests if any children are available in this node structure.

        There may be no more children available in this node structure
        but this node may have children in the hierarchy.

        return: (boolean) - ``true`` if this node has children,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_child_ids(self):
        """Gets the children of this node.

        return: (osid.id.IdList) - the children of this node
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    child_ids = property(fget=get_child_ids)


