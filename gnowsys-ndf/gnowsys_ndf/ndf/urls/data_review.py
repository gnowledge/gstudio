from django.conf.urls import patterns, url

from django.views.generic import TemplateView

urlpatterns = patterns('gnowsys_ndf.ndf.views.data_review',
						# simple data-review with/withou page no.
						url(r'^[/]$', 'data_review', name='data_review'),
						url(r'^/page-no=(?P<page_no>\d+)/$', 'data_review', name='data_review_page'),

						# to save edited data-review row
						url(r'^/save/$', 'data_review_save', name='data_review_save'),

						# to render search result with and without page no.
						url(r'^/search$', 'get_dr_search_result_dict', name="data_review_search"),
						url(r'^/search/search_text=(?P<search_text>[^/]+)/page-no=(?P<page_no>\d+)/$', 'get_dr_search_result_dict', name="data_review_search_page"),
 )