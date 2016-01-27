from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.userDashboard',                       
						url(r'^userpreference/', 'userpref',name='userpreference'),
						url(r'^dashboard/group', 'group_dashboard', name='group_dashboard'),
						url(r'^dashboard', 'uDashboard', name='dashboard'),
						# url(r'^(?P<usrid>[\w-]+)/userDashboard$', 'dashboard', name='userDashboard'),                                            
						url(r'^useractivity', 'user_activity', name='user_activity'),
						url(r'userprofiledata','user_data_profile',name='user_data_profile'),	
						url(r'^userprofile', 'user_profile', name='user_profile'),
						url(r'^upload_prof_pic', 'upload_prof_pic', name='upload_prof_pic'),
						url(r'^user_preference/(?P<auth_id>[\w-]+)$','user_preferences',name='user_preferences'),
						
						url(r'^my-courses/$', 'my_courses', name='my_courses'),
						url(r'^my-groups/$', 'my_groups', name='my_groups'),
			)
