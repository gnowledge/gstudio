# -*- coding: utf-8 -*-
"""Authentication Open Service Interface Definitions
authentication version 3.0.0

The Authentication OSID manages authenticated entities.

Agent

The Authentication OSID defines an ``Agent`` to represent the identity
of the authenticated entity. An Agent may map to a specific
authentication principal while some providers may elect to hide multiple
authentication principals behind a single ``Agent``. Because principal
identities tend not to be durable and persistent, consumers should
always persist the ``Id``.

Resource Mapping

An ``Agent`` may be mapped to a ``Resource`` in the Resource OSID. A
``Resource`` may map to multiple ``Agents`` but an ``Agent`` may only
map to a single Resource. In the case of a person, a person may be
utilize a number of authentication technologies each with a different
authentication identity. Decoupling the authentication identity from
that of ther person is to provide a means of integrating multiple
services where different authentication identities exist for a person
that impact the handling of authorization.

Authorization

Authorization is a separate service. The Authorization OSID manages what
functions the ``Agent`` is authorized to perform and references the
``Agent``  ``Id``. The Authentication OSID is only responsible for
identity management of the ``Agent``.

Each ``Agent`` of a ``Resource`` may be used to define distinct security
levels of assurance (although the paranoid may opt for defining a
pseudo-resource for each ``Agent`` ). These security levels of assurance
can be linked to the ``Agent``  ``Type`` and managed in the
Authorization OSID. The ``Agent``  ``Type`` would be an indicator of the
authentication strength and although it may correlate to a specific
authentication technology, coupling it too tightly to a particular
technology may limit flexibility.

Certain consumers may wish to be notified of changes within the service.
Authentication supports notifications via an
``AgentNotificationSession``.
  if (manager.supportsAgentNotification()) {
      AgentNotificationSession ans = manager.getAgentNotificationSession(receiver);
      ans.registerForNewAgents();
      hangAround();
  }
  
  AgentReceiver receiver {
      newAgent(Id agentId) { print("new agent"); }
      changedAgent(Id agentId) { print("updated agent"); }
      deletedAgent(Id agentId) { print("deleted agent"); }
  }



Agency Cataloging

``Agents`` are organized into federateable ``Agency``  ``OsidCatalogs``.

Sub Packages

The Authentication OSID includes an Authentication Key OSID for managing
private keys associated with an ``Agent`` and an Authentication Process
OSID for acquiring and validating authentication credentials. It slaos
includes an Authentication Batch OSID for managing ``Agents`` and
``Agencies`` in bulk.

"""
