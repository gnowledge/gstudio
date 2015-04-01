from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.e-book',
                       url(r'^[/]$', 'ebook_listing', name='e-book'),
                       )
