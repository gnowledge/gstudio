from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

urlpatterns = patterns('gnowsys_ndf.ndf.views.languagepref',
        url(r'^[/]$','lang_pref', name='language_pref'),
)
