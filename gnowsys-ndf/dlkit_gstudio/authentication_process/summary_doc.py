# -*- coding: utf-8 -*-
"""Authentication Process Open Service Interface Definitions
authentication.process version 3.0.0

The Authentication Process OSID conducts an authentication process.

Authentication Process

The Authentication OSID helps an OSID Consumer acquire and validate
authentication credentials without having to manage the details of a
particular authentication environment. Authentication is generally a two
step process. A user wishing to authenticate acquires a set of
credentials and transports those credentials to a remote peer. The
remote peer then validates those credentials and determines the identity
of the user represented. This process is reflected in the Authentication
OSID with the definition of two OSID sessions:

  * ``AuthenticationAcquisitionSession:`` A session to acquire
    credentials from a user and serialize them for transport to a remote
    peer for authentication.
  * ``AuthenticationValidationSession:`` A session to receive and
    validate authentication credentials from a remote peer wishing to
    authenticate.


The transport of authentication credentials is the responsibility of the
consumer of the Authentication OSID as authentication generally supports
an existing application protocol enviornment. Methods exist to extract
and supply credentials at each end. An Authentication OSID Provider may
support either or both sessions, and one or more credential formats.
Methods also exist to support a challenge-response mechanism.

Circle of Trust

In the Authorization OSID, Authorizations may be managed for a set of
Agents related to a Resource. The set of ``Agents`` may be filtered
based on the level of confidence upon the authentication mechanism. A
``Trust`` is a category of ``Agents`` produced from an authentication
mechanism that represent a level of confidence on which to specify an
Authorization.

``Trusts`` are not explicitly managed in the Authentication Process
OSID. They serve to facilitate the orchestration between an
Authentication OSID Provider and an Authorization OSID Provider. An
Authorization OSID Provider may query the ``CircleOfTrustSession`` to
determine if an ``Agent`` it has received belongs to a ``Trust``
specified in one of its Authorizations.

For example, an ``Authorization`` may be created by specifying a
``Resource``. The ``Resource`` may be an individual person or a group of
employees. While employees might be authorized to read their company
email using their GMail account, requisitions in the ERP system must be
made using the company authentication system and even perhaps a specific
specific type of credential. An ``Authorization`` can be created for a
set of employees based but restricted to a ``Trust`` where the Trust
represents any ``Agent`` related to the set of employees that have
authenticated in the desired fashion.

The multiplicity of ``Agents`` per Resource as aell as the alignment
with an Authorization OSID Provider is a consideration in the design of
an Authentication OSID Provider. It does only identify the
authentication principal as a singular entity, but may also represent
something about the authentication style that is used to perform an
authorization.

Examples

Client side authentication:
  if (manager.supportsAuthenticationAcquisition() &amp;&amp;
      manager.supportsAcquisitionInputType(krb5ServiceType) &amp;&amp;
      manager.supportsCredentialType(serialKRB5Type)) {
      AuthenticationAcquisitionSession aas = manager.getAuthenticationAcquisitionSession();
  
      // specify input parameters (interface extension)
      KRB5Service kService = new KRB5Service();
      kService.setName("host");
      kService.setInstance("server.osid.org");
      kService.setRealm("OSID.ORG");
  
      // get Credential (interface type) 
      Authentication auth = aas.getAuthentication(kService, krb5ServiceType);
      SerializedKRB5Ticket ticket = (SerializedKRB5Ticket)        auth.getCredential(serialKRB5Type);
      send_data_to_peer(ticket); // app specific protocol
  }





Server side authentication:
  if (manager.supportsAuthenticationValidation() &amp;&amp;
      manager.supportsCredentialType(serialSAML2Type)) {
      AuthenticationValidationSession avs = manager.getAuthenticationValidationSession();
  
      Authentication auth = authenticate(SAML2Token, serialSAML2Type);
  
      if (auth.isValid()) {
          Agent agent = auth.getAgent(); // identity established
      }
  }



"""
