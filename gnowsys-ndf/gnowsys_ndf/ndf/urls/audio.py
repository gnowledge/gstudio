from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.audioDashboard',
			url(r'^[/]$', 'audioDashboard', name='audio'),
                        
)
