from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.explore',
						url(r'^$', 'explore', name='explore'),
						url(r'^courses$', 'explore_courses', name='explore_courses'),
						url(r'^groups$', 'explore_groups', name='explore_groups'),
 )