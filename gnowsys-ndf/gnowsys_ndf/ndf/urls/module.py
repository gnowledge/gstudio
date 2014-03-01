from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.module',
                        url(r'^(?P<module_id>[\w-]+)$', 'module', name='module'),

                       )
