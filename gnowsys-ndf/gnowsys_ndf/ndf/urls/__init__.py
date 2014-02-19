from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from registration.backends.default.views import RegistrationView

from gnowsys_ndf.ndf.forms import *
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/class/', include('gnowsys_ndf.ndf.urls.adminDashboard')),
    (r'^admin/', include(admin.site.urls)),
    (r'^$', RedirectView.as_view(url= '/home/')),    
    (r'^(?P<group_name>[^/]+)/file/', include('gnowsys_ndf.ndf.urls.file')),
    (r'^(?P<group_name>[^/]+)/image/', include('gnowsys_ndf.ndf.urls.image')),
    (r'^(?P<group_name>[^/]+)/video/', include('gnowsys_ndf.ndf.urls.video')),
    (r'^(?P<group_name>[^/]+)/page/', include('gnowsys_ndf.ndf.urls.page')),
    (r'^(?P<group_name>[^/]+)/group/', include('gnowsys_ndf.ndf.urls.group')),
    (r'^(?P<group_name>[^/]+)/forum/', include('gnowsys_ndf.ndf.urls.forum')),
    (r'^(?P<group_name>[^/]+)/quiz/', include('gnowsys_ndf.ndf.urls.quiz')),
    (r'^(?P<group_name>[^/]+)/course/', include('gnowsys_ndf.ndf.urls.course')),
    (r'^(?P<group_name>[^/]+)/module/', include('gnowsys_ndf.ndf.urls.module')),
    (r'^(?P<group_name>[^/]+)/ajax/', include('gnowsys_ndf.ndf.urls.ajax-urls')),
    (r'^(?P<group_name>[^/]+)/',include('gnowsys_ndf.ndf.urls.group')),
    (r'^(?P<group_name>[^/]+)/', include('gnowsys_ndf.ndf.urls.user')),
   # (r'^home/', 'gnowsys_ndf.ndf.views.home.homepage'),
    (r'^benchmarker/', include('gnowsys_ndf.benchmarker.urls')),
    url(r'^accounts/password/change/done/', auth_views.password_change_done, name='password_change_done'),
    url(r'^accounts/password/change/', auth_views.password_change, {'password_change_form': UserChangeform}),
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, {'set_password_form': UserResetform},name='password_reset_confirm'),
    url(r'^accounts/password/reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^accounts/password/reset/done/$',auth_views.password_reset_done,name="password_reset_done"),
    url(r'^accounts/password/reset/$',
        auth_views.password_reset,
        {
            'template_name': 'registration/password_reset_form.html',
            'email_template_name': 'registration/password_reset_email.html',
            'subject_template_name':'registration/password_reset_email_subject.txt'
        },
        name='password_reset'
    ),
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=UserRegistrationForm)),
     (r'^accounts/', include('registration.backends.default.urls')),
    url(r'^Beta/', TemplateView.as_view(template_name= 'gstudio/beta.html'), name="beta"),
)
