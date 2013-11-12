from django.conf.urls import patterns, include, url
from django.contrib import admin

from django.contrib.auth import views as auth_views

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', include('gnowsys_ndf.ndf.urls')),
    (r'^ndf/', include('gnowsys_ndf.ndf.urls')),
    (r'^benchmarker/', include('gnowsys_ndf.benchmarker.urls')),

    (r'^admin/', include(admin.site.urls)),

    url(r'^accounts/password/reset/$', 
        auth_views.password_reset,
	{
            'template_name': 'registration/password_reset_form.html',
            'email_template_name': 'registration/password_reset_email.html',
            'subject_template_name':'registration/password_reset_email_subject.txt'
        },
	name='auth_password_reset'
    ),
    
    (r'^accounts/', include('registration.backends.default.urls')),
)
