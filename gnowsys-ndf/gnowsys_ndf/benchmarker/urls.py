#from django.conf.urls.defaults import *
from django.conf.urls import patterns, url, include
from django.conf.urls import *
import views

urlpatterns = patterns('',
    url(r'^$', views.run, name='run'),
    url(r'^BenchmarkReport/',include('gnowsys_ndf.benchmarker.report')),
)
