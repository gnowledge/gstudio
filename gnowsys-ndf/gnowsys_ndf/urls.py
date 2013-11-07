from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', include('gnowsys_ndf.ndf.urls')),
    (r'^ndf/', include('gnowsys_ndf.ndf.urls')),
    (r'^benchmarker/', include('gnowsys_ndf.benchmarker.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('gnowsys_ndf.registration.backends.default.urls')),
)
