"""GStudio implementations of authentication.process objects."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification

#from ..id.objects import IdList
#import importlib


from .. import utilities
from ...abstract_osid.authentication_process import objects as abc_authentication_process_objects
from ..authentication.objects import Agent
from ..osid import objects as osid_objects
from ..primitives import Id
from ..utilities import get_registry
from dlkit.abstract_osid.osid import errors




class Authentication(abc_authentication_process_objects.Authentication, osid_objects.OsidObject):
    """``Authentication`` represents an authentication credential which contains set of ``bytes`` and a format Type.

    Once an ``Authentication`` is created from the
    ``AuthenticationValidationSession,`` the credential data can be
    extracted and sent to the remote peer for validation. The remote
    peer gets another ``Authentication`` object as a result of
    validating the serialized credential data.

    An ``Authentication`` may or may not be valid. ``is_valid()`` should
    be checked before acting upon the ``Agent`` identity to which the
    credential is mapped.

    """

    def __init__(self):
        self._django_user = None
        self._credential = None


    def get_agent_id(self):
        """Gets the ``Id`` of the ``Agent`` identified in this authentication credential.

        return: (osid.id.Id) - the ``Agent Id``
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: The Agent should be determined at the
        time this credential is created.

        """
        if self._django_user is not None:
            return Id(identifier=self._django_user.get_username(),
                      namespace='osid.agent.Agent',
                      authority='MIT-OEIT')
        else:
            return Id(identifier='MC3GUE$T@MIT.EDU',
                      namespace='osid.agent.Agent',
                      authority='MIT-OEIT')

    agent_id = property(fget=get_agent_id)

    def get_agent(self):
        """Gets the ``Agent`` identified in this authentication credential.

        return: (osid.authentication.Agent) - the ``Agent``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented

    agent = property(fget=get_agent)

    def is_valid(self):
        """Tests whether or not the credential represented by this ``Authentication`` is currently valid.

        A credential may be invalid because it has been destroyed,
        expired, or is somehow no longer able to be used.

        return: (boolean) - ``true`` if this authentication credential
                is valid, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: Any problem in determining the validity
        of this credential should result in ``false``.

        """
        if self._django_user is not None:
            return self._django_user.is_authenticated()
        else:
            return False

    def has_expiration(self):
        """Tests if this authentication has an expiration.

        return: (boolean) - ``true`` if this authentication has an
                expiration, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False

    def get_expiration(self):
        """Gets the expiration date associated with this authentication credential.

        Consumers should check for the existence of a an expiration
        mechanism via ``hasExpiration()``.

        return: (timestamp) - the expiration date of this authentication
                credential
        raise:  IllegalState - ``has_expiration()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        if not self.has_expiration():
            raise errors.IllegalState()
        else:
            raise errors.Unimplemented()

    expiration = property(fget=get_expiration)

    def has_credential(self):
        """Tests if this authentication has a credential for export.

        return: (boolean) - ``true`` if this authentication has a
                credential, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        if self._credential is None:
            return False
        else:
            return True

    @utilities.arguments_not_none
    def get_credential(self, credential_type):
        """Gets the credential represented by the given ``Type`` for transport to a remote service.

        arg:    credential_type (osid.type.Type): the credential format
                ``Type``
        return: (object) - the credential
        raise:  IllegalState - ``has_credential()`` is ``false``
        raise:  NullArgument - ``credential_type`` is ``null``
        raise:  Unsupported - the given ``credential_type`` is not
                supported
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: A provider may support multiple
        credential formats for a variety of applications.

        """
        if self.has_credential():
            return self._credential
        else:
            raise errors.IllegalState()

    @utilities.arguments_not_none
    def get_authentication_record(self, authentication_record_type):
        """Gets the authentication record corresponding to the given authentication record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``authentication_record_type`` may be the
        ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(authentication_record_type)`` is ``true`` .

        arg:    authentication_record_type (osid.type.Type): the type of
                authentication record to retrieve
        return:
                (osid.authentication.process.records.AuthenticationRecor
                d) - the authentication record
        raise:  NullArgument - ``authentication_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        raise:  Unsupported -
                ``has_record_type(authenticaton_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unsupported()

    def set_django_user(self, django_user):
        """Special method that excepts a django user. Should be a record."""
        self._django_user = django_user


