# -*- coding: utf-8 -*-
"""Proxy Open Service Interface Definitions
proxy version 3.0.0

The Proxy OSID helps a consumer map external data, such as that received
via a server request, into a Proxy that can be used with OSID proxy
managers. Then purpose of this OSID is to modularize assumptions made
about the input data into another OSID Provider, such as the
authentication or localization information.

The ``Proxy`` represents the ``OsidResult`` of an evaluation of the
input ``OsidCondition`` performed by the Proxy OSID Provider. The
resulting Proxy is meant to be passed to ``OsidProxyManagers``. The
Proxy OSID is the glue between the application server environment and
the OSID services.

The input data may be anything acceptable to a ``ProxyCondition`` record
Type. The ``ProxyCondition`` record ``Types`` are aligned with the
application server environment while the ``Proxy`` record ``Types`` are
aligned with OSID Providers. This alignment poses various
interoperability issues and as such it might be helpful to be very broad
in what may be specified in a ``ProxyCondition`` so that this service
may produce the variety of ``Proxy`` records needed by the services in
the OSID environment.

Some data is defined in the ``ProxyCondition``. This in no way implies
support of this input by an OSID Provider. The resulting ``OsidSession``
indicates what actually happened.

Example

An example using a specifier record for an http request:
  ProxyCondition condition = proxySession.getProxyCondition();
  HttpRequestRecord record = condition.getProxyConditionRecord(httpRequestRecordType);
  record.setHttpRequest(servletRequest);
  
  Proxy proxy = proxySession.getProxy(condition);



"""
