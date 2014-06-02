from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.batch',
                       url(r'^$', 'batch', name='batch'),
                       url(r'^/create$', 'create', name='create'),
                       url(r'^/save$', 'save', name='save'),
                       )
