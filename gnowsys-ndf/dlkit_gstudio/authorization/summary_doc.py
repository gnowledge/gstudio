# -*- coding: utf-8 -*-
"""Authorization Open Service Interface Definitions
authorization version 3.0.0

The Authorization OSID manages and queries authorizations.

Authorizations

An ``Authorization`` is an ``OsidRelationship`` that defines who can do
what to what. The grammar of an authorization incluides the subject or
the actor (who), the action or verb (do what), and the object or context
(to what). All three of these components must exist in an authorization
for it to have any explicit meaning. An ``Authorization`` is a mapping
among these three components.

  * ``Agent:`` the actor (eg: tom@coppeto.org)
  * ``Function:`` the action (eg: create purchase order)
  * ``Qualifier:`` the object or context within a Function (eg: on
    account 1967)


This tuple in essence defines a role. "Instructor" is not a role and is
not suitable for making an authorization decision. "Instructs Physics
101", both the function and qualifier, defines the complete role (within
the context of a particular college) that can be used for an
authorization decision.

The basic service of the Authorization OSID is to provide a means for
asking whether a given ``Agent`` is authorized to perform a ``Function``
with a ``Qualifier,`` in other words, if such a mapping exists. The
Agent will generally be obtained from an Authentication service and the
``Function`` and ``Qualifier`` generally known to the consuming
application (a server process needing to protect some resource).

Example
  Authentication auth = authNValidationSession.authenticate(creds);
  
  AuthorizationSession session = authZManager.getAuthorizationSession();
  boolean authorized = session.isAuthorized(auth.getAgentId(), functionId, qualifierId);



The rest of the Authorization OSID is concerned with managing
authorizations.

Explicit/Implicit Authorizations

Authorizations can be explcit or implcit. Explicit authorizations are
managed while implcit authorizations are derived from ``Resources,``
``Function`` and ``Qualifier`` hierrachies. Examples of implcit
authorizations:

  * The Authorization OSID can accept a ``Resource`` in lieu of an
    ``Agent`` as the actor so a Person, Group or Organization may be
    used to specify an authorization. In this case, the explicit
    authorization is the one containing the ``Resource`` and an implicit
    authorization exists for each ``Agent.``
  * ``Qualifiers`` only exist as Hierarchy Nodes since the Authorization
    OSID does not manage the objects used as qualifiers but may manage
    directly, or have access to, a Hierarchy service to obtain the
    identity and relationship among these objects. An explicit
    authorization for a given ``Qualifier`` creates an implcit
    authorization for every child of that ``Qualifier.``


The Authorization OSID manages ``Functions`` directly through its owned
defined sessions and exposes actors via the Resource OSID.
``Qualifiers`` are only exposed through the Hierarchy service as the
Authorization service doesn't have anything to say about the objects
represented by the ``Qualifiers``.

Vault Cataloging

``Authorizations, Functions`` and ``Qualifiers`` may be organized into
one or many ``Vaults``. This serves to categorize authorizatiion data
for the purpose of browsing or auditing. ``Vaults`` are hierarchical
where each node includes all the authorization data of its children. A
single root node will make available all known authorizations and is a
reasonable choice for a default ``Vault`` for a non-federated aware
consumer. A federated authorization scheme is one in which ``Vaults``
are available for selection.

Notifications

Certain consumers may wish to be notified of changes within the service.
Authorization supports notifications via
``AuthorizatioNotificationSession,``  ``FunctionNotificationSession``
and ``VaultNotificationSession``.
  if (manager.supportsAuthorizationNotification()) {
      AuthorizationNotificationSession ans = manager.getAuthorizationNotificationSession(receiver);           
      ans.registerForDeletedAuthorizations();
  }
  
  AuthorizationReceiver receiver {
      newAuthorization(Authorization a) {print("authorization created");}
      deletedAuthorization(Authorization a) {print("authorization removed");}
  }



Sub Packages

The Authorization OSID includes an Authorization Rules OSID for managing
the effectiveness of ``Authorizations``.

"""
