from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    (r'^$', include('gnowsys_ndf.ndf.urls')),
    (r'^ndf/', include('gnowsys_ndf.ndf.urls')),
    (r'^benchmarker/', include('gnowsys_ndf.benchmarker.urls')),
)
