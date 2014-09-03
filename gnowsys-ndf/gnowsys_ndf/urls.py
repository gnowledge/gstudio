from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from registration.backends.default.views import RegistrationView

from gnowsys_ndf.ndf.forms import * 
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', include('gnowsys_ndf.ndf.urls')),
    (r'^ndf/', include('gnowsys_ndf.ndf.urls')),
    (r'^benchmarker/', include('gnowsys_ndf.benchmarker.urls')),
    (r'^admin/', include(admin.site.urls)),
)
