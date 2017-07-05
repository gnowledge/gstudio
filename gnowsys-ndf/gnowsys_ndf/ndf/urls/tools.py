from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.tools',
						url(r'^logging/$','tools_logging', name='tools_logging')
						
                       )
