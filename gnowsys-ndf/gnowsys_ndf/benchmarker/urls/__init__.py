from django.conf.urls import patterns, url
from gnowsys_ndf.benchmarker import views
from django.views.generic import TemplateView

urlpatterns = patterns('gnowsys_ndf.benchmarker.benchmarkreport',
                       url(r'^report/', 'report', name='report'),
                       url(r'^month/','month_view',name='month_view'),
                       )
                       
#urlpatterns = patterns('',
#                      url(r'^run/', views.run, name='run'),
#                       )                                              
