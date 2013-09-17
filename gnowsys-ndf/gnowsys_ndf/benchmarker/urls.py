#from django.conf.urls.defaults import *
from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^$', views.run, name='run'),
)
