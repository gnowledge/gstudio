from django.conf.urls import patterns, url

from django.views.generic import TemplateView

urlpatterns = patterns('gnowsys_ndf.ndf.views.sitemap',
                        url(r'^', 'sitemap', name='sitemap')


)