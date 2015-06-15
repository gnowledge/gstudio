from django.conf.urls import patterns, url

from django.views.generic import TemplateView

urlpatterns = patterns('gnowsys_ndf.ndf.views.moderation',

						# simple moderation having data-review view with/without page no.
						url(r'^[/]$', 'moderation', name='moderation'),

						# showing the status of all objects under moderation
						url(r'^/status/all-under-moderation/$', 'all_under_moderation', name='all_under_moderation'),
						
						# showing the status of under moderation object
						url(r'^/status/(?P<node_id>[\w-]+)$', 'moderation_status', name='moderation_status'),
	
						# dr: data_review
						url(r'^/page-no=(?P<page_no>\d+)/$', 'moderation', name='moderation_dr_page'),

						# to publish resource to next/parent(if last group) moderated group
						url(r'^/approve/$', 'approve_resource', name='approve_resource'),
						
						# # to save edited data-review row
						# url(r'^/save/$', 'data_review_save', name='data_review_save'),

						# # to render search result with and without page no.
						# url(r'^/search$', 'get_dr_search_result_dict', name="data_review_search"),
						# url(r'^/search/search_text=(?P<search_text>[^/]+)/page-no=(?P<page_no>\d+)/$', 'get_dr_search_result_dict', name="data_review_search_page"),
 )