from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.tools',
                        # url(r'^[/]$', 'tools_temp', name='tools_temp'),
						url(r'^logging/?$','tools_logging', name='tools_logging'),
						url(r'^tool-page/?$','tools_temp', name='tools_temp'),
						
                       )
