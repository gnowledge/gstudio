from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from registration.backends.default.views import RegistrationView

from gnowsys_ndf.ndf.forms import *
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', RedirectView.as_view(url= '/home/')),
    (r'^(?P<group_name>[\w-]+)/file/', include('gnowsys_ndf.ndf.urls.file')),
    (r'^(?P<group_name>[\w-]+)/image/', include('gnowsys_ndf.ndf.urls.image')),
    (r'^(?P<group_name>[\w-]+)/video/', include('gnowsys_ndf.ndf.urls.video')),
    (r'^(?P<group_name>[\w-]+)/page/', include('gnowsys_ndf.ndf.urls.page')),
    (r'^(?P<group_name>[\w-]+)/group/', include('gnowsys_ndf.ndf.urls.group')),
    (r'^(?P<group_name>[\w-]+)/forum/', include('gnowsys_ndf.ndf.urls.forum')),
    (r'^(?P<group_name>[\w-]+)/quiz/', include('gnowsys_ndf.ndf.urls.quiz')),
    (r'^(?P<group_name>[\w-]+)/ajax/', include('gnowsys_ndf.ndf.urls.ajax-urls')),
    (r'^(?P<group_name>[\w-]+)/',include('gnowsys_ndf.ndf.urls.group')),
    (r'^home/', 'gnowsys_ndf.ndf.views.home.homepage'),
    (r'^benchmarker/', include('gnowsys_ndf.benchmarker.urls')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^accounts/password/change/done/', auth_views.password_change_done),
    url(r'^accounts/password/change/', auth_views.password_change, {'password_change_form': UserChangeform}),
    url(r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, {'set_password_form':UserResetform}),
    url(r'^accounts/password/reset/$',
        auth_views.password_reset,
        {
            'template_name': 'registration/password_reset_form.html',
            'email_template_name': 'registration/password_reset_email.html',
            'subject_template_name':'registration/password_reset_email_subject.txt'
        },
        name='auth_password_reset'
    ),
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=UserRegistrationForm)),
    (r'^accounts/', include('registration.backends.default.urls')),
)
