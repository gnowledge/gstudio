from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.program',
                        url(r'^[/]$', 'program_event_list', name='program'),
                        # url(r'^[/]$', 'program_event_list', name='programeventgroup'),
                        # url(r'^[/]$', 'program_event_list', name='program_event_list'),
						# url(r'^programs/$', 'program_event_list', name='program_event_list'),
                       
                       )
