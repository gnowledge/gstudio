from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.benchmarker.BenchMark_report',
                       url(r'^$', 'report', name='report'),
                       )
