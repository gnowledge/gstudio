from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.explore',
						url(r'^$', 'explore', name='explore'),
						url(r'^courses$', 'explore_courses', name='explore_courses'),
						url(r'^basecourses$', 'explore_basecourses', name='explore_basecourses'),
						url(r'^groups$', 'explore_groups', name='explore_groups'),
						url(r'^courses/page-no=(?P<page_no>\d+)/$', 'explore_courses', name='courses_paged'),
						url(r'^basecourses/page-no=(?P<page_no>\d+)/$', 'explore_basecourses', name='basecourses_paged'),
						url(r'^groups/page-no=(?P<page_no>\d+)/$', 'explore_groups', name='groups_paged'),

 )