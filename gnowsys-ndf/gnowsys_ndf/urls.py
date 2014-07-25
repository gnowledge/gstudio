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
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^admin/', include(admin.site.urls)),
   # (r'^online/', include('online_status.urls')),                     # for online_users

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
