from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.dev_utils',
						url(r'^test/$', 'render_test_template', name='render_test_template')
						
                       )
