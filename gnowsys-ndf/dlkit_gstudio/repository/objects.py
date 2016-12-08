"""GStudio implementations of repository objects."""

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
from dlkit.abstract_osid.repository import objects as abc_repository_objects
from ..osid import markers as osid_markers
from ..osid import objects as osid_objects
from ..osid.metadata import Metadata
from ..primitives import Id
from ..utilities import get_registry
from ..utilities import update_display_text_defaults
from dlkit.abstract_osid.osid import errors
from dlkit.primordium.id.primitives import Id




class Asset(abc_repository_objects.Asset, osid_objects.OsidObject, osid_markers.Aggregateable, osid_markers.Sourceable):
    """An ``Asset`` represents some digital content.

    Example assets might be a text document, an image, or a movie. The
    content data, and metadata related directly to the content format
    and quality, is accessed through ``AssetContent. Assets`` , like all
    ``OsidObjects,`` include a type a record to qualify the ``Asset``
    and include additional data. The division between the ``Asset``
    ``Type`` and ``AssetContent`` is to separate data describing the
    asset from data describing the format of the contents, allowing a
    consumer to select among multiple formats, sizes or levels of
    fidelity.

    An example is a photograph of the Bay Bridge. The content may
    deliver a JPEG in multiple resolutions where the ``AssetContent``
    may also desribe size or compression factor for each one. The
    content may also include an uncompressed TIFF version. The ``Asset``
    ``Type`` may be "photograph" indicating that the photo itself is the
    asset managed in this repository.

    Since an Asset may have multiple ``AssetContent`` structures, the
    decision of how many things to stuff inside a single asset comes
    down to if the content is actually a different format, or size, or
    quality, falling under the same creator, copyright, publisher and
    distribution rights as the original. This may, in some cases,
    provide a means to implement some accessibility, it doesn't handle
    the case where, to meet an accessibility requirement, one asset
    needs to be substituted for another. The Repository OSID manages
    this aspect outside the scope of the core ``Asset`` definition.

    ``Assets`` map to ``AssetSubjects``.  ``AssetSubjects`` are
    ``OsidObjects`` that capture a subject matter. In the above example,
    an ``AssetSubject`` may be defined for the Bay Bridge and include
    data describing the bridge. The single subject can map to multiple
    assets depicting the bridge providing a single entry for a search
    and a single place to describe a bridge. Bridges, as physical items,
    may also be described using the Resource OSID in which case the use
    of the ``AssetSubject`` acts as a cover for the underlying
    ``Resource`` to assist repository-only consumers.

    The ``Asset`` definition includes some basic copyright and related
    licensing information to assist in finding free-to-use content, or
    to convey the distribution restrictions that may be placed on the
    asset. Generally, if no data is available it is to be assumed that
    all rights are reserved.

    A publisher is applicable if the content of this ``Asset`` has been
    published. Not all ``Assets`` in this ``Repository`` may have a
    published status and such a status may effect the applicability of
    copyright law. To trace the source of an ``Asset,`` both a provider
    and source are defined. The provider indicates where this repository
    acquired the asset and the source indicates the original provider or
    copyright owner. In the case of a published asset, the source is the
    publisher.

    ``Assets`` also define methods to facilitate searches over time and
    space as it relates to the subject matter. This may at times be
    redundant with the ``AssetSubject``. In the case of the Bay Bridge
    photograph, the temporal coverage may include 1936, when it opened,
    and/or indicate when the photo was taken to capture a current event
    of the bridge. The decision largeley depends on what desired effect
    is from a search. The spatial coverage may describe the gps
    coordinates of the bridge or describe the spatial area encompassed
    in the view. In either case, a "photograph" type may unambiguously
    defined methods to describe the exact time the photograph was taken
    and the location of the photographer.

    The core Asset defines methods to perform general searches and
    construct bibliographic entries without knowledge of a particular
    ``Asset`` or ``AssetContent`` record ``Type``.

    """

    _namespace = 'repository.Asset'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='ASSET', **kwargs)
        # Can remove object_name param
        self._catalog_name = 'repository'


    def get_title(self):
        """Gets the proper title of this asset.

        This may be the same as the display name or the display name may
        be used for a less formal label.

        return: (osid.locale.DisplayText) - the title of this asset
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    title = property(fget=get_title)

    def is_copyright_status_known(self):
        """Tests if the copyright status is known.

        return: (boolean) - ``true`` if the copyright status of this
                asset is known, ``false`` otherwise. If ``false,
                is_public_domain(),`` ``can_distribute_verbatim(),
                can_distribute_alterations() and
                can_distribute_compositions()`` may also be ``false``.
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def is_public_domain(self):
        """Tests if this asset is in the public domain.

        An asset is in the public domain if copyright is not applicable,
        the copyright has expired, or the copyright owner has expressly
        relinquished the copyright.

        return: (boolean) - ``true`` if this asset is in the public
                domain, ``false`` otherwise. If ``true,``
                ``can_distribute_verbatim(),
                can_distribute_alterations() and
                can_distribute_compositions()`` must also be ``true``.
        raise:  IllegalState - ``is_copyright_status_known()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_copyright(self):
        """Gets the copyright statement and of this asset which identifies the current copyright holder.

        For an asset in the public domain, this method may return the
        original copyright statement although it may be no longer valid.

        return: (osid.locale.DisplayText) - the copyright statement or
                an empty string if none available. An empty string does
                not imply the asset is not protected by copyright.
        raise:  IllegalState - ``is_copyright_status_known()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    copyright_ = property(fget=get_copyright)

    def get_copyright_registration(self):
        """Gets the copyright registration information for this asset.

        return: (string) - the copyright registration. An empty string
                means the registration status isn't known.
        raise:  IllegalState - ``is_copyright_status_known()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    copyright_registration = property(fget=get_copyright_registration)

    def can_distribute_verbatim(self):
        """Tests if there are any license restrictions on this asset that restrict the distribution, re-publication or public display of this asset, commercial or otherwise, without modification, alteration, or inclusion in other works.

        This method is intended to offer consumers a means of filtering
        out search results that restrict distribution for any purpose.
        The scope of this method does not include licensing that
        describes warranty disclaimers or attribution requirements. This
        method is intended for informational purposes only and does not
        replace or override the terms specified in a license agreement
        which may specify exceptions or additional restrictions.

        return: (boolean) - ``true`` if the asset can be distributed
                verbatim, ``false`` otherwise.
        raise:  IllegalState - ``is_copyright_status_known()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_distribute_alterations(self):
        """Tests if there are any license restrictions on this asset that restrict the distribution, re-publication or public display of any alterations or modifications to this asset, commercial or otherwise, for any purpose.

        This method is intended to offer consumers a means of filtering
        out search results that restrict the distribution or public
        display of any modification or alteration of the content or its
        metadata of any kind, including editing, translation,
        resampling, resizing and cropping. The scope of this method does
        not include licensing that describes warranty disclaimers or
        attribution requirements. This method is intended for
        informational purposes only and does not replace or override the
        terms specified in a license agreement which may specify
        exceptions or additional restrictions.

        return: (boolean) - ``true`` if the asset can be modified,
                ``false`` otherwise. If ``true,``
                ``can_distribute_verbatim()`` must also be ``true``.
        raise:  IllegalState - ``is_copyright_status_known()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_distribute_compositions(self):
        """Tests if there are any license restrictions on this asset that restrict the distribution, re-publication or public display of this asset as an inclusion within other content or composition, commercial or otherwise, for any purpose, including restrictions upon the distribution or license of the resulting composition.

        This method is intended to offer consumers a means of filtering
        out search results that restrict the use of this asset within
        compositions. The scope of this method does not include
        licensing that describes warranty disclaimers or attribution
        requirements. This method is intended for informational purposes
        only and does not replace or override the terms specified in a
        license agreement which may specify exceptions or additional
        restrictions.

        return: (boolean) - ``true`` if the asset can be part of a
                larger composition ``false`` otherwise. If ``true,``
                ``can_distribute_verbatim()`` must also be ``true``.
        raise:  IllegalState - ``is_copyright_status_known()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_source_id(self):
        """Gets the ``Resource Id`` of the source of this asset.

        The source is the original owner of the copyright of this asset
        and may differ from the creator of this asset. The source for a
        published book written by Margaret Mitchell would be Macmillan.
        The source for an unpublished painting by Arthur Goodwin would
        be Arthur Goodwin.

        An ``Asset`` is ``Sourceable`` and also contains a provider
        identity. The provider is the entity that makes this digital
        asset available in this repository but may or may not be the
        publisher of the contents depicted in the asset. For example, a
        map published by Ticknor and Fields in 1848 may have a provider
        of Library of Congress and a source of Ticknor and Fields. If
        copied from a repository at Middlebury College, the provider
        would be Middlebury College and a source of Ticknor and Fields.

        return: (osid.id.Id) - the source ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    source_id = property(fget=get_source_id)

    def get_source(self):
        """Gets the ``Resource`` of the source of this asset.

        The source is the original owner of the copyright of this asset
        and may differ from the creator of this asset. The source for a
        published book written by Margaret Mitchell would be Macmillan.
        The source for an unpublished painting by Arthur Goodwin would
        be Arthur Goodwin.

        return: (osid.resource.Resource) - the source
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    source = property(fget=get_source)

    def get_provider_link_ids(self):
        """Gets the resource ``Ids`` representing the source of this asset in order from the most recent provider to the originating source.

        return: (osid.id.IdList) - the provider ``Ids``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    provider_link_ids = property(fget=get_provider_link_ids)

    def get_provider_links(self):
        """Gets the ``Resources`` representing the source of this asset in order from the most recent provider to the originating source.

        return: (osid.resource.ResourceList) - the provider chain
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    provider_links = property(fget=get_provider_links)

    def get_created_date(self):
        """Gets the created date of this asset, which is generally not related to when the object representing the asset was created.

        The date returned may indicate that not much is known.

        return: (osid.calendaring.DateTime) - the created date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    created_date = property(fget=get_created_date)

    def is_published(self):
        """Tests if this asset has been published.

        Not all assets viewable in this repository may have been
        published. The source of a published asset indicates the
        publisher.

        return: (boolean) - true if this asset has been published,
                ``false`` if unpublished or its published status is not
                known
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_published_date(self):
        """Gets the published date of this asset.

        Unpublished assets have no published date. A published asset has
        a date available, however the date returned may indicate that
        not much is known.

        return: (osid.calendaring.DateTime) - the published date
        raise:  IllegalState - ``is_published()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    published_date = property(fget=get_published_date)

    def get_principal_credit_string(self):
        """Gets the credits of the principal people involved in the production of this asset as a display string.

        return: (osid.locale.DisplayText) - the principal credits
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    principal_credit_string = property(fget=get_principal_credit_string)

    def get_asset_content_ids(self):
        """Gets the content ``Ids`` of this asset.

        return: (osid.id.IdList) - the asset content ``Ids``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    asset_content_ids = property(fget=get_asset_content_ids)

    def get_asset_contents(self):
        """Gets the content of this asset.

        return: (osid.repository.AssetContentList) - the asset contents
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    asset_contents = property(fget=get_asset_contents)

    def is_composition(self):
        """Tetss if this asset is a representation of a composition of assets.

        return: (boolean) - true if this asset is a composition,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_composition_id(self):
        """Gets the ``Composition``  ``Id`` corresponding to this asset.

        return: (osid.id.Id) - the composiiton ``Id``
        raise:  IllegalState - ``is_composition()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    composition_id = property(fget=get_composition_id)

    def get_composition(self):
        """Gets the Composition corresponding to this asset.

        return: (osid.repository.Composition) - the composiiton
        raise:  IllegalState - ``is_composition()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    composition = property(fget=get_composition)

    @utilities.arguments_not_none
    def get_asset_record(self, asset_record_type):
        """Gets the asset record corresponding to the given ``Asset`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``asset_record_type`` may be the ``Type``
        returned in ``get_record_types()`` or any of its parents in a
        ``Type`` hierarchy where ``has_record_type(asset_record_type)``
        is ``true`` .

        arg:    asset_record_type (osid.type.Type): an asset record type
        return: (osid.repository.records.AssetRecord) - the asset record
        raise:  NullArgument - ``asset_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(asset_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssetForm(abc_repository_objects.AssetForm, osid_objects.OsidObjectForm, osid_objects.OsidAggregateableForm, osid_objects.OsidSourceableForm):
    """This is the form for creating and updating ``Assets``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``AssetAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'repository.Asset'

    def __init__(self, **kwargs):
        osid_objects.OsidObjectForm.__init__(self, object_name='ASSET', **kwargs)
        self._mdata = default_mdata.get_asset_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""

        osid_objects.OsidSourceableForm._init_metadata(self)
        osid_objects.OsidObjectForm._init_metadata(self, **kwargs)
        self._copyright_registration_default = self._mdata['copyright_registration']['default_string_values'][0]
        update_display_text_defaults(self._mdata['copyright'], self._locale_map)
        self._copyright_default = dict(self._mdata['copyright']['default_string_values'][0])
        update_display_text_defaults(self._mdata['title'], self._locale_map)
        self._title_default = dict(self._mdata['title']['default_string_values'][0])
        self._distribute_verbatim_default = self._mdata['distribute_verbatim']['default_boolean_values'][0]
        self._created_date_default = self._mdata['created_date']['default_date_time_values'][0]
        self._distribute_alterations_default = self._mdata['distribute_alterations']['default_boolean_values'][0]
        update_display_text_defaults(self._mdata['principal_credit_string'], self._locale_map)
        self._principal_credit_string_default = dict(self._mdata['principal_credit_string']['default_string_values'][0])
        self._published_date_default = self._mdata['published_date']['default_date_time_values'][0]
        self._source_default = self._mdata['source']['default_id_values'][0]
        self._provider_links_default = self._mdata['provider_links']['default_id_values']
        self._public_domain_default = self._mdata['public_domain']['default_boolean_values'][0]
        self._distribute_compositions_default = self._mdata['distribute_compositions']['default_boolean_values'][0]
        self._composition_default = self._mdata['composition']['default_id_values'][0]
        self._published_default = self._mdata['published']['default_boolean_values'][0]

    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""

        osid_objects.OsidSourceableForm._init_map(self)
        osid_objects.OsidObjectForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    def get_title_metadata(self):
        """Gets the metadata for an asset title.

        return: (osid.Metadata) - metadata for the title
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['title'])
        # metadata.update({'existing_title_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    title_metadata = property(fget=get_title_metadata)

    @utilities.arguments_not_none
    def set_title(self, title):
        """Sets the title.

        arg:    title (string): the new title
        raise:  InvalidArgument - ``title`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``title`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_title(self):
        """Removes the title.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    title = property(fset=set_title, fdel=clear_title)

    def get_public_domain_metadata(self):
        """Gets the metadata for the public domain flag.

        return: (osid.Metadata) - metadata for the public domain
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['public_domain'])
        # metadata.update({'existing_public_domain_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    public_domain_metadata = property(fget=get_public_domain_metadata)

    @utilities.arguments_not_none
    def set_public_domain(self, public_domain):
        """Sets the public domain flag.

        arg:    public_domain (boolean): the public domain status
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_public_domain(self):
        """Removes the public domain status.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    public_domain = property(fset=set_public_domain, fdel=clear_public_domain)

    def get_copyright_metadata(self):
        """Gets the metadata for the copyright.

        return: (osid.Metadata) - metadata for the copyright
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['copyright'])
        # metadata.update({'existing_copyright_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    copyright_metadata = property(fget=get_copyright_metadata)

    @utilities.arguments_not_none
    def set_copyright(self, copyright_):
        """Sets the copyright.

        arg:    copyright (string): the new copyright
        raise:  InvalidArgument - ``copyright`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``copyright`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_copyright(self):
        """Removes the copyright.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    copyright_ = property(fset=set_copyright, fdel=clear_copyright)

    def get_copyright_registration_metadata(self):
        """Gets the metadata for the copyright registration.

        return: (osid.Metadata) - metadata for the copyright
                registration
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['copyright_registration'])
        # metadata.update({'existing_copyright_registration_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    copyright_registration_metadata = property(fget=get_copyright_registration_metadata)

    @utilities.arguments_not_none
    def set_copyright_registration(self, registration):
        """Sets the copyright registration.

        arg:    registration (string): the new copyright registration
        raise:  InvalidArgument - ``copyright`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``copyright`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_copyright_registration(self):
        """Removes the copyright registration.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    copyright_registration = property(fset=set_copyright_registration, fdel=clear_copyright_registration)

    def get_distribute_verbatim_metadata(self):
        """Gets the metadata for the distribute verbatim rights flag.

        return: (osid.Metadata) - metadata for the distribution rights
                fields
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['distribute_verbatim'])
        # metadata.update({'existing_distribute_verbatim_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    distribute_verbatim_metadata = property(fget=get_distribute_verbatim_metadata)

    @utilities.arguments_not_none
    def set_distribute_verbatim(self, distribute_verbatim):
        """Sets the distribution rights.

        arg:    distribute_verbatim (boolean): right to distribute
                verbatim copies
        raise:  InvalidArgument - ``distribute_verbatim`` is invalid
        raise:  NoAccess - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_distribute_verbatim(self):
        """Removes the distribution rights.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    distribute_verbatim = property(fset=set_distribute_verbatim, fdel=clear_distribute_verbatim)

    def get_distribute_alterations_metadata(self):
        """Gets the metadata for the distribute alterations rights flag.

        return: (osid.Metadata) - metadata for the distribution rights
                fields
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['distribute_alterations'])
        # metadata.update({'existing_distribute_alterations_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    distribute_alterations_metadata = property(fget=get_distribute_alterations_metadata)

    @utilities.arguments_not_none
    def set_distribute_alterations(self, distribute_mods):
        """Sets the distribute alterations flag.

        This also sets distribute verbatim to ``true``.

        arg:    distribute_mods (boolean): right to distribute
                modifications
        raise:  InvalidArgument - ``distribute_mods`` is invalid
        raise:  NoAccess - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_distribute_alterations(self):
        """Removes the distribution rights.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    distribute_alterations = property(fset=set_distribute_alterations, fdel=clear_distribute_alterations)

    def get_distribute_compositions_metadata(self):
        """Gets the metadata for the distribute compositions rights flag.

        return: (osid.Metadata) - metadata for the distribution rights
                fields
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['distribute_compositions'])
        # metadata.update({'existing_distribute_compositions_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    distribute_compositions_metadata = property(fget=get_distribute_compositions_metadata)

    @utilities.arguments_not_none
    def set_distribute_compositions(self, distribute_comps):
        """Sets the distribution rights.

        This sets distribute verbatim to ``true``.

        arg:    distribute_comps (boolean): right to distribute
                modifications
        raise:  InvalidArgument - ``distribute_comps`` is invalid
        raise:  NoAccess - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_distribute_compositions(self):
        """Removes the distribution rights.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    distribute_compositions = property(fset=set_distribute_compositions, fdel=clear_distribute_compositions)

    def get_source_metadata(self):
        """Gets the metadata for the source.

        return: (osid.Metadata) - metadata for the source
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['source'])
        # metadata.update({'existing_source_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    source_metadata = property(fget=get_source_metadata)

    @utilities.arguments_not_none
    def set_source(self, source_id):
        """Sets the source.

        arg:    source_id (osid.id.Id): the new publisher
        raise:  InvalidArgument - ``source_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``source_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_source(self):
        """Removes the source.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    source = property(fset=set_source, fdel=clear_source)

    def get_provider_links_metadata(self):
        """Gets the metadata for the provider chain.

        return: (osid.Metadata) - metadata for the provider chain
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    provider_links_metadata = property(fget=get_provider_links_metadata)

    @utilities.arguments_not_none
    def set_provider_links(self, resource_ids):
        """Sets a provider chain in order from the most recent source to the originating source.

        arg:    resource_ids (osid.id.Id[]): the new source
        raise:  InvalidArgument - ``resource_ids`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``resource_ids`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_provider_links(self):
        """Removes the provider chain.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    provider_links = property(fset=set_provider_links, fdel=clear_provider_links)

    def get_created_date_metadata(self):
        """Gets the metadata for the asset creation date.

        return: (osid.Metadata) - metadata for the created date
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['created_date'])
        # metadata.update({'existing_created_date_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    created_date_metadata = property(fget=get_created_date_metadata)

    @utilities.arguments_not_none
    def set_created_date(self, created_date):
        """Sets the created date.

        arg:    created_date (osid.calendaring.DateTime): the new
                created date
        raise:  InvalidArgument - ``created_date`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``created_date`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_created_date(self):
        """Removes the created date.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    created_date = property(fset=set_created_date, fdel=clear_created_date)

    def get_published_metadata(self):
        """Gets the metadata for the published status.

        return: (osid.Metadata) - metadata for the published field
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['published'])
        # metadata.update({'existing_published_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    published_metadata = property(fget=get_published_metadata)

    @utilities.arguments_not_none
    def set_published(self, published):
        """Sets the published status.

        arg:    published (boolean): the published status
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_published(self):
        """Removes the published status.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    published = property(fset=set_published, fdel=clear_published)

    def get_published_date_metadata(self):
        """Gets the metadata for the published date.

        return: (osid.Metadata) - metadata for the published date
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['published_date'])
        # metadata.update({'existing_published_date_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    published_date_metadata = property(fget=get_published_date_metadata)

    @utilities.arguments_not_none
    def set_published_date(self, published_date):
        """Sets the published date.

        arg:    published_date (osid.calendaring.DateTime): the new
                published date
        raise:  InvalidArgument - ``published_date`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``published_date`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_published_date(self):
        """Removes the puiblished date.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    published_date = property(fset=set_published_date, fdel=clear_published_date)

    def get_principal_credit_string_metadata(self):
        """Gets the metadata for the principal credit string.

        return: (osid.Metadata) - metadata for the credit string
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['principal_credit_string'])
        # metadata.update({'existing_principal_credit_string_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    principal_credit_string_metadata = property(fget=get_principal_credit_string_metadata)

    @utilities.arguments_not_none
    def set_principal_credit_string(self, credit_string):
        """Sets the principal credit string.

        arg:    credit_string (string): the new credit string
        raise:  InvalidArgument - ``credit_string`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``credit_string`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_principal_credit_string(self):
        """Removes the principal credit string.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    principal_credit_string = property(fset=set_principal_credit_string, fdel=clear_principal_credit_string)

    def get_composition_metadata(self):
        """Gets the metadata for linking this asset to a composition.

        return: (osid.Metadata) - metadata for the composition
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['composition'])
        # metadata.update({'existing_composition_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    composition_metadata = property(fget=get_composition_metadata)

    @utilities.arguments_not_none
    def set_composition(self, composition_id):
        """Sets the composition.

        arg:    composition_id (osid.id.Id): a composition
        raise:  InvalidArgument - ``composition_id`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``composition_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_composition(self):
        """Removes the composition link.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    composition = property(fset=set_composition, fdel=clear_composition)

    @utilities.arguments_not_none
    def get_asset_form_record(self, asset_record_type):
        """Gets the ``AssetFormRecord`` corresponding to the given ``Asset`` record ``Type``.

        arg:    asset_record_type (osid.type.Type): an asset record type
        return: (osid.repository.records.AssetFormRecord) - the asset
                form record
        raise:  NullArgument - ``asset_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(asset_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssetList(abc_repository_objects.AssetList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``AssetList`` provides a means for accessing ``Asset`` elements sequentially either one at a time or many at a time.

    Examples: while (al.hasNext()) { Asset asset = al.getNextAsset(); }

    or
      while (al.hasNext()) {
           Asset[] assets = al.getNextAssets(al.available());
      }



    """

    def get_next_asset(self):
        """Gets the next ``Asset`` in this list.

        return: (osid.repository.Asset) - the next ``Asset`` in this
                list. The ``has_next()`` method should be used to test
                that a next ``Asset`` is available before calling this
                method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Asset)

    next_asset = property(fget=get_next_asset)

    @utilities.arguments_not_none
    def get_next_assets(self, n):
        """Gets the next set of ``Assets`` in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``Asset`` elements requested
                which must be less than or equal to ``available()``
        return: (osid.repository.Asset) - an array of ``Asset``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class AssetContent(abc_repository_objects.AssetContent, osid_objects.OsidObject, osid_markers.Subjugateable):
    """``AssetContent`` represents a version of content represented by an ``Asset``.

    Although ``AssetContent`` is a separate ``OsidObject`` with its own
    ``Id`` to distuinguish it from other content inside an ``Asset,
    AssetContent`` can only be accessed through an ``Asset``.

    Once an ``Asset`` is selected, multiple contents should be
    negotiated using the size, fidelity, accessibility requirements or
    application evnironment.

    """

    _namespace = 'repository.AssetContent'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='ASSET_CONTENT', **kwargs)
        self._catalog_name = 'repository'


    def get_asset_id(self):
        """Gets the ``Asset Id`` corresponding to this content.

        return: (osid.id.Id) - the asset ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    asset_id = property(fget=get_asset_id)

    def get_asset(self):
        """Gets the ``Asset`` corresponding to this content.

        return: (osid.repository.Asset) - the asset
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    asset = property(fget=get_asset)

    def get_accessibility_types(self):
        """Gets the accessibility types associated with this content.

        return: (osid.type.TypeList) - list of content accessibility
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    accessibility_types = property(fget=get_accessibility_types)

    def has_data_length(self):
        """Tests if a data length is available.

        return: (boolean) - ``true`` if a length is available for this
                content, ``false`` otherwise.
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_data_length(self):
        """Gets the length of the data represented by this content in bytes.

        return: (cardinal) - the length of the data stream
        raise:  IllegalState - ``has_data_length()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    data_length = property(fget=get_data_length)

    def get_data(self):
        """Gets the asset content data.

        return: (osid.transport.DataInputStream) - the length of the
                content data
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    data = property(fget=get_data)

    def has_url(self):
        """Tests if a URL is associated with this content.

        return: (boolean) - ``true`` if a URL is available, ``false``
                otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_url(self):
        """Gets the URL associated with this content for web-based retrieval.

        return: (string) - the url for this data
        raise:  IllegalState - ``has_url()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    url = property(fget=get_url)

    @utilities.arguments_not_none
    def get_asset_content_record(self, asset_content_content_record_type):
        """Gets the asset content record corresponding to the given ``AssetContent`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``asset_record_type`` may be the ``Type``
        returned in ``get_record_types()`` or any of its parents in a
        ``Type`` hierarchy where ``has_record_type(asset_record_type)``
        is ``true`` .

        arg:    asset_content_content_record_type (osid.type.Type): the
                type of the record to retrieve
        return: (osid.repository.records.AssetContentRecord) - the asset
                content record
        raise:  NullArgument - ``asset_content_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(asset_content_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssetContentForm(abc_repository_objects.AssetContentForm, osid_objects.OsidObjectForm, osid_objects.OsidSubjugateableForm):
    """This is the form for creating and updating content for ``AssetContent``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``AssetAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'repository.AssetContent'

    def __init__(self, **kwargs):
        osid_objects.OsidObjectForm.__init__(self, object_name='ASSET_CONTENT', **kwargs)
        self._mdata = default_mdata.get_asset_content_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""
        osid_objects.OsidObjectForm._init_metadata(self, **kwargs)
        self._url_default = self._mdata['url']['default_string_values'][0]
        self._data_default = self._mdata['data']['default_object_values'][0]
        self._accessibility_type_default = self._mdata['accessibility_type']['default_type_values'][0]

    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""
        osid_objects.OsidObjectForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    def get_accessibility_type_metadata(self):
        """Gets the metadata for an accessibility type.

        return: (osid.Metadata) - metadata for the accessibility types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['accessibility_type'])
        # metadata.update({'existing_accessibility_type_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    accessibility_type_metadata = property(fget=get_accessibility_type_metadata)

    @utilities.arguments_not_none
    def add_accessibility_type(self, accessibility_type):
        """Adds an accessibility type.

        Multiple types can be added.

        arg:    accessibility_type (osid.type.Type): a new accessibility
                type
        raise:  InvalidArgument - ``accessibility_type`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``accessibility_t_ype`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def remove_accessibility_type(self, accessibility_type):
        """Removes an accessibility type.

        arg:    accessibility_type (osid.type.Type): accessibility type
                to remove
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NotFound - acessibility type not found
        raise:  NullArgument - ``accessibility_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_accessibility_types(self):
        """Removes all accessibility types.

        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    accessibility_types = property(fdel=clear_accessibility_types)

    def get_data_metadata(self):
        """Gets the metadata for the content data.

        return: (osid.Metadata) - metadata for the content data
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['data'])
        # metadata.update({'existing_data_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    data_metadata = property(fget=get_data_metadata)

    @utilities.arguments_not_none
    def set_data(self, data):
        """Sets the content data.

        arg:    data (osid.transport.DataInputStream): the content data
        raise:  InvalidArgument - ``data`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``data`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_data(self):
        """Removes the content data.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    data = property(fset=set_data, fdel=clear_data)

    def get_url_metadata(self):
        """Gets the metadata for the url.

        return: (osid.Metadata) - metadata for the url
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceForm.get_group_metadata_template
        metadata = dict(self._mdata['url'])
        # metadata.update({'existing_url_values': [THE EXISTING VALUE OR VALUES IN A LIST]})
        return Metadata(**metadata)

    url_metadata = property(fget=get_url_metadata)

    @utilities.arguments_not_none
    def set_url(self, url):
        """Sets the url.

        arg:    url (string): the new copyright
        raise:  InvalidArgument - ``url`` is invalid
        raise:  NoAccess - ``Metadata.isReadOnly()`` is ``true``
        raise:  NullArgument - ``url`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_url(self):
        """Removes the url.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    url = property(fset=set_url, fdel=clear_url)

    @utilities.arguments_not_none
    def get_asset_content_form_record(self, asset_content_record_type):
        """Gets the ``AssetContentFormRecord`` corresponding to the given asset content record ``Type``.

        arg:    asset_content_record_type (osid.type.Type): an asset
                content record type
        return: (osid.repository.records.AssetContentFormRecord) - the
                asset content form record
        raise:  NullArgument - ``asset_content_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(asset_content_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssetContentList(abc_repository_objects.AssetContentList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``AssetContentList`` provides a means for accessing ``AssetContent`` elements sequentially either one at a time or many at a time.

    Examples: while (acl.hasNext()) { AssetContent content =
    acl.getNextAssetContent(); }

    or
      while (acl.hasNext()) {
           AssetContent[] contents = acl.getNextAssetContents(acl.available());
      }



    """

    def get_next_asset_content(self):
        """Gets the next ``AssetContent`` in this list.

        return: (osid.repository.AssetContent) - the next
                ``AssetContent`` in this list. The ``has_next()`` method
                should be used to test that a next ``AssetContent`` is
                available before calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(AssetContent)

    next_asset_content = property(fget=get_next_asset_content)

    @utilities.arguments_not_none
    def get_next_asset_contents(self, n):
        """Gets the next set of ``AssetContents`` in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``AssetContent`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.repository.AssetContent) - an array of
                ``AssetContent`` elements.The length of the array is
                less than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class Composition(abc_repository_objects.Composition, osid_objects.OsidObject, osid_markers.Containable, osid_markers.Operable, osid_markers.Sourceable):
    """A ``Composition`` represents an authenticatable identity.

    Like all OSID objects, a ``Composition`` is identified by its Id and
    any persisted references should use the Id.

    """

    _namespace = 'repository.Composition'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='COMPOSITION', **kwargs)
        self._catalog_name = 'repository'


    def get_children_ids(self):
        """Gets the child ``Ids`` of this composition.

        return: (osid.id.IdList) - the composition child ``Ids``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    children_ids = property(fget=get_children_ids)

    def get_children(self):
        """Gets the children of this composition.

        return: (osid.repository.CompositionList) - the composition
                children
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    children = property(fget=get_children)

    @utilities.arguments_not_none
    def get_composition_record(self, composition_record_type):
        """Gets the composition record corresponding to the given ``Composition`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``composition_record_type`` may be the
        ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(composition_record_type)`` is ``true`` .

        arg:    composition_record_type (osid.type.Type): a composition
                record type
        return: (osid.repository.records.CompositionRecord) - the
                composition record
        raise:  NullArgument - ``composition_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(composition_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class CompositionForm(abc_repository_objects.CompositionForm, osid_objects.OsidObjectForm, osid_objects.OsidContainableForm, osid_objects.OsidOperableForm, osid_objects.OsidSourceableForm):
    """This is the form for creating and updating ``Compositions``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``CompositionAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'repository.Composition'

    def __init__(self, **kwargs):
        osid_objects.OsidObjectForm.__init__(self, object_name='COMPOSITION', **kwargs)
        self._mdata = default_mdata.get_composition_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""

        osid_objects.OsidContainableForm._init_metadata(self)
        osid_objects.OsidSourceableForm._init_metadata(self)
        osid_objects.OsidObjectForm._init_metadata(self, **kwargs)
        self._children_default = self._mdata['children']['default_id_values']

    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""

        osid_objects.OsidContainableForm._init_map(self)
        osid_objects.OsidSourceableForm._init_map(self)
        osid_objects.OsidObjectForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    @utilities.arguments_not_none
    def get_composition_form_record(self, composition_record_type):
        """Gets the ``CompositionFormRecord`` corresponding to the given repository record ``Type``.

        arg:    composition_record_type (osid.type.Type): a composition
                record type
        return: (osid.repository.records.CompositionFormRecord) - the
                composition form record
        raise:  NullArgument - ``composition_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(composition_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class CompositionList(abc_repository_objects.CompositionList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``CompositionList`` provides a means for accessing ``Composition`` elements sequentially either one at a time or many at a time.

    Examples: while (cl.hasNext()) { Composition composition =
    cl.getNextComposition(); }

    or
      while (cl.hasNext()) {
           Composition[] compositions = cl.getNextCompositions(cl.available());
      }



    """

    def get_next_composition(self):
        """Gets the next ``Composition`` in this list.

        return: (osid.repository.Composition) - the next ``Composition``
                in this list. The ``has_next()`` method should be used
                to test that a next ``Composition`` is available before
                calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Composition)

    next_composition = property(fget=get_next_composition)

    @utilities.arguments_not_none
    def get_next_compositions(self, n):
        """Gets the next set of ``Composition`` elements in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``Composition`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.repository.Composition) - an array of
                ``Composition`` elements.The length of the array is less
                than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class Repository(abc_repository_objects.Repository, osid_objects.OsidCatalog):
    """A repository defines a collection of assets."""

    _namespace = 'repository.Repository'

    def __init__(self, **kwargs):
        # self._record_type_data_sets = get_registry('REPOSITORY_RECORD_TYPES', runtime)
        osid_objects.OsidCatalog.__init__(self, **kwargs)

    @utilities.arguments_not_none
    def get_repository_record(self, repository_record_type):
        """Gets the record corresponding to the given ``Repository`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``repository_record_type`` may be the
        ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(repository_record_type)`` is ``true`` .

        arg:    repository_record_type (osid.type.Type): a repository
                record type
        return: (osid.repository.records.RepositoryRecord) - the
                repository record
        raise:  NullArgument - ``repository_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(repository_record_type)`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class RepositoryForm(abc_repository_objects.RepositoryForm, osid_objects.OsidCatalogForm):
    """This is the form for creating and updating repositories.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``RepositoryAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'repository.Repository'

    def __init__(self, **kwargs):
        osid_objects.OsidCatalogForm.__init__(self, **kwargs)
        self._mdata = default_mdata.get_repository_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_form(self, record_types=None, **kwargs):
        """Initialize form map"""
        osid_objects.OsidCatalogForm.__init__(self, **kwargs)


    @utilities.arguments_not_none
    def get_repository_form_record(self, repository_record_type):
        """Gets the ``RepositoryFormRecord`` corresponding to the given repository record ``Type``.

        arg:    repository_record_type (osid.type.Type): a repository
                record type
        return: (osid.repository.records.RepositoryFormRecord) - the
                repository form record
        raise:  NullArgument - ``repository_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(repository_record_type)`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class RepositoryList(abc_repository_objects.RepositoryList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``RepositoryList`` provides a means for accessing ``Repository`` elements sequentially either one at a time or many at a time.

    Examples: while (rl.hasNext()) { Repository repository =
    rl.getNextRepository(); }

    or
      while (rl.hasNext()) {
           Repository[] repositories = rl.getNextRepositories(rl.available());
      }



    """

    def get_next_repository(self):
        """Gets the next ``Repository`` in this list.

        return: (osid.repository.Repository) - the next ``Repository``
                in this list. The ``has_next()`` method should be used
                to test that a next ``Repository`` is available before
                calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Repository)

    next_repository = property(fget=get_next_repository)

    @utilities.arguments_not_none
    def get_next_repositories(self, n):
        """Gets the next set of ``Repository`` elements in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``Repository`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.repository.Repository) - an array of
                ``Repository`` elements.The length of the array is less
                than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class RepositoryNode(abc_repository_objects.RepositoryNode, osid_objects.OsidNode):
    """This interface is a container for a partial hierarchy retrieval.

    The number of hierarchy levels traversable through this interface
    depend on the number of levels requested in the
    ``RepositoryHierarchySession``.

    """

    def get_repository(self):
        """Gets the ``Repository`` at this node.

        return: (osid.repository.Repository) - the repository
                represented by this node
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    repository = property(fget=get_repository)

    def get_parent_repository_nodes(self):
        """Gets the parents of this repository.

        return: (osid.repository.RepositoryNodeList) - the parents of
                the ``id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    parent_repository_nodes = property(fget=get_parent_repository_nodes)

    def get_child_repository_nodes(self):
        """Gets the children of this repository.

        return: (osid.repository.RepositoryNodeList) - the children of
                this repository
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    child_repository_nodes = property(fget=get_child_repository_nodes)


class RepositoryNodeList(abc_repository_objects.RepositoryNodeList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``RepositoryNodeList`` provides a means for accessing ``RepositoryNode`` elements sequentially either one at a time or many at a time.

    Examples: while (rnl.hasNext()) { RepositoryNode node =
    rnl.getNextRepositoryNode(); }

    or
      while (rnl.hasNext()) {
           RepositoryNode[] nodes = rnl.getNextRepositoryNodes(rnl.available());
      }



    """

    def get_next_repository_node(self):
        """Gets the next ``RepositoryNode`` in this list.

        return: (osid.repository.RepositoryNode) - the next
                ``RepositoryNode`` in this list. The ``has_next()``
                method should be used to test that a next
                ``RepositoryNode`` is available before calling this
                method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(RepositoryNode)

    next_repository_node = property(fget=get_next_repository_node)

    @utilities.arguments_not_none
    def get_next_repository_nodes(self, n):
        """Gets the next set of ``RepositoryNode`` elements in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``RepositoryNode`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.repository.RepositoryNode) - an array of
                ``RepositoryNode`` elements.The length of the array is
                less than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


