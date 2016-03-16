from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.jhapp',
			url(r'^[/]$', 'get_jhapp_apps', name='get_jhapp_apps'),
                        
)
