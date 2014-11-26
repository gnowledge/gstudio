from django.conf.urls import patterns, url

from django.views.generic import TemplateView

urlpatterns = patterns('gnowsys_ndf.ndf.views.data_review',
                       url(r'^/$', 'data_review', name='data_review'),
                       url(r'^/page-no=(?P<page_no>\d+)/$', 'data_review', name='data_review_page'),
                       url(r'^/save/$', 'data_review_save', name='data_review_save'),
                       url(r'^/search/', 'data_review', name="data_review_search"),
)