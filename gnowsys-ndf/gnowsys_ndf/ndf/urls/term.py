from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.term',
					   url(r'^$', 'term', name='term')
)