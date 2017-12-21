from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.explore',
						url(r'^$', 'explore', name='explore'),
						url(r'^courses$', 'explore_courses', name='explore_courses'),

						url(r'^basecourses$', 'explore_basecourses', name='explore_basecourses'),
						url(r'^workspaces$', 'explore_groups', name='explore_groups'),
						url(r'^courses/page-no=(?P<page_no>\d+)/$', 'explore_courses', name='courses_paged'),
						url(r'^basecourses/page-no=(?P<page_no>\d+)/$', 'explore_basecourses', name='basecourses_paged'),
						url(r'^groups/page-no=(?P<page_no>\d+)/$', 'explore_groups', name='groups_paged'),
						url(r'^drafts$', 'explore_drafts', name='explore_drafts'),
                        url(r'^reorder$', 'module_order_list', name='module_order_list'),
 )


urlpatterns += patterns('',
						url(r'^(?P<group_id>[\w-]+)/modules$', 'gnowsys_ndf.ndf.views.module.list_modules', name='explore_modules'),
						# url(r'^modules$', 'gnowsys_ndf.ndf.views.module.list_modules', {'group_id': None}, name='explore_modules'),
)
